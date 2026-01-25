#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Patch all library files"""

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

def patch_all():
    """Patch all library files"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("PATCHING ALL LIBRARY FILES")
    print("=" * 80)
    
    # Find all JS files in the library
    print("\n1. Finding all JS files in library...")
    stdin, stdout, stderr = ssh.exec_command('docker exec shannon_worker_1 find /app/node_modules/@anthropic-ai/claude-agent-sdk -name "*.js" -type f')
    files = stdout.read().decode('utf-8', errors='replace').strip().split('\n')
    files = [f for f in files if f]
    print(f"   Found {len(files)} files")
    
    # Patch each file
    total_replacements = 0
    for file_path in files:
        print(f"\n2. Patching {file_path}...")
        
        # Read file
        stdin, stdout, stderr = ssh.exec_command(f'docker exec shannon_worker_1 cat {file_path}')
        content = stdout.read().decode('utf-8', errors='replace')
        
        original_content = content
        
        # Try different patterns
        replacements = [
            (r"spawn\(['\"]node['\"]", r"spawn('/usr/bin/node'"),
            (r'spawn\(["\']node["\']', r'spawn("/usr/bin/node"'),
            (r"spawnSync\(['\"]node['\"]", r"spawnSync('/usr/bin/node'"),
            (r'spawnSync\(["\']node["\']', r'spawnSync("/usr/bin/node"'),
            # Also try without quotes
            (r"spawn\(node", r"spawn('/usr/bin/node'"),
            (r'spawnSync\(node', r'spawnSync("/usr/bin/node"'),
        ]
        
        file_replacements = 0
        for pattern, replacement in replacements:
            new_content = re.sub(pattern, replacement, content)
            if new_content != content:
                content = new_content
                file_replacements += 1
        
        if content != original_content:
            # Write back via base64
            import base64
            content_b64 = base64.b64encode(content.encode('utf-8')).decode('ascii')
            
            # Write in one command
            cmd = f'docker exec shannon_worker_1 sh -c "echo {content_b64} | base64 -d > {file_path}"'
            stdin, stdout, stderr = ssh.exec_command(cmd)
            result = stdout.read().decode('utf-8', errors='replace')
            errors = stderr.read().decode('utf-8', errors='replace')
            
            if not errors or 'base64' not in errors.lower():
                print(f"   Patched! Made {file_replacements} replacements")
                total_replacements += file_replacements
            else:
                print(f"   Error: {errors[:200]}")
        else:
            print("   No patterns found")
    
    print(f"\n3. Total replacements: {total_replacements}")
    
    # Restart worker
    print("\n4. Restarting worker...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose restart worker')
    print(stdout.read().decode('utf-8', errors='replace'))
    
    import time
    time.sleep(5)
    
    # Verify
    print("\n5. Verifying...")
    stdin, stdout, stderr = ssh.exec_command('docker exec shannon_worker_1 grep -r "/usr/bin/node" /app/node_modules/@anthropic-ai/claude-agent-sdk --include="*.js" | wc -l')
    verify_count = stdout.read().decode('utf-8', errors='replace').strip()
    print(f"   Found {verify_count} occurrences of /usr/bin/node in library")
    
    ssh.close()
    
    print("\n" + "=" * 80)
    print("PATCH COMPLETE")
    print("=" * 80)
    if total_replacements > 0:
        print(f"SUCCESS! Made {total_replacements} replacements")
        print("Try a new pentest now")
    else:
        print("No replacements made - library may use different pattern")

if __name__ == "__main__":
    import time
    patch_all()

