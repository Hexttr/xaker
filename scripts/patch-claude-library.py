#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Patch claude library directly in node_modules"""

import paramiko
import sys
import re

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def patch_library():
    """Patch library directly"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("PATCHING CLAUDE LIBRARY DIRECTLY")
    print("=" * 80)
    
    # Find the library file
    print("\n1. Finding library files...")
    stdin, stdout, stderr = ssh.exec_command('docker exec shannon_worker_1 find /app/node_modules/@anthropic-ai -name "*.js" -type f | grep -E "(claude|agent)" | head -10')
    files = stdout.read().decode('utf-8', errors='replace').strip().split('\n')
    files = [f for f in files if f]
    print(f"Found {len(files)} files")
    
    # Find files with spawn
    target_files = []
    for file_path in files[:5]:
        stdin, stdout, stderr = ssh.exec_command(f'docker exec shannon_worker_1 grep -l "spawn.*node\|spawnSync.*node" {file_path} 2>&1')
        if stdout.read().decode('utf-8', errors='replace').strip():
            target_files.append(file_path)
    
    print(f"Files with spawn node: {len(target_files)}")
    
    # Patch first file
    if target_files:
        file_path = target_files[0]
        print(f"\n2. Patching {file_path}...")
        
        # Read file
        stdin, stdout, stderr = ssh.exec_command(f'docker exec shannon_worker_1 cat {file_path}')
        content = stdout.read().decode('utf-8', errors='replace')
        
        # Replace 'node' with '/usr/bin/node' in spawn calls
        # Need to be careful with minified code
        original_content = content
        
        # Try to replace common patterns
        patterns = [
            (r"spawn\(['\"]node['\"]", r"spawn('/usr/bin/node'"),
            (r'spawn\(["\']node["\']', r'spawn("/usr/bin/node"'),
            (r"spawnSync\(['\"]node['\"]", r"spawnSync('/usr/bin/node'"),
            (r'spawnSync\(["\']node["\']', r'spawnSync("/usr/bin/node"'),
        ]
        
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)
        
        if content != original_content:
            print("   Found patterns to replace")
            # Write back through base64
            import base64
            content_b64 = base64.b64encode(content.encode('utf-8')).decode('ascii')
            
            # Write via echo and base64 decode
            cmd = f'docker exec shannon_worker_1 sh -c "echo {content_b64} | base64 -d > {file_path}"'
            stdin, stdout, stderr = ssh.exec_command(cmd)
            result = stdout.read().decode('utf-8', errors='replace')
            errors = stderr.read().decode('utf-8', errors='replace')
            
            if not errors or 'base64' not in errors:
                print("   File patched!")
            else:
                print(f"   Error: {errors}")
        else:
            print("   No patterns found to replace")
    
    # Alternative: Create wrapper and patch PATH in running container
    print("\n3. Creating wrapper in running container...")
    wrapper_cmd = '''docker exec shannon_worker_1 sh -c "mkdir -p /app/bin && echo '#!/bin/sh' > /app/bin/node && echo 'exec /usr/bin/node \"$@\"' >> /app/bin/node && chmod +x /app/bin/node"'''
    stdin, stdout, stderr = ssh.exec_command(wrapper_cmd)
    wrapper_result = stdout.read().decode('utf-8', errors='replace')
    wrapper_errors = stderr.read().decode('utf-8', errors='replace')
    
    if not wrapper_errors:
        print("   Wrapper created in running container")
        
        # Verify
        stdin, stdout, stderr = ssh.exec_command('docker exec shannon_worker_1 ls -la /app/bin/node')
        verify = stdout.read().decode('utf-8', errors='replace')
        print(f"   {verify}")
        
        # Restart worker to pick up changes
        print("\n4. Restarting worker...")
        ssh.exec_command('cd /opt/xaker/shannon && docker-compose restart worker')
        time.sleep(3)
        
        print("   Worker restarted")
        print("   Note: This is temporary - wrapper will be lost on container rebuild")
        print("   For permanent fix, rebuild image with Dockerfile changes")
    else:
        print(f"   Error creating wrapper: {wrapper_errors}")
    
    ssh.close()
    
    print("\n" + "=" * 80)
    print("PATCH COMPLETE")
    print("=" * 80)
    print("Try a new pentest now")
    print("If it works, rebuild image properly for permanent fix")

if __name__ == "__main__":
    import time
    patch_library()

