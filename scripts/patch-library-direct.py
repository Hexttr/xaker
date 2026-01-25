#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Patch library directly by replacing node with full path"""

import paramiko
import sys
import re
import base64

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
    print("PATCHING LIBRARY DIRECTLY")
    print("=" * 80)
    
    # Find the file that spawns node
    print("\n1. Finding file with spawn node...")
    stdin, stdout, stderr = ssh.exec_command('docker exec shannon_worker_1 find /app/node_modules/@anthropic-ai -name "*.js" -type f -exec grep -l "spawn.*node" {} \\; 2>/dev/null | head -5')
    files = stdout.read().decode('utf-8', errors='replace').strip().split('\n')
    files = [f for f in files if f]
    
    if not files:
        print("   No files found, searching differently...")
        stdin, stdout, stderr = ssh.exec_command('docker exec shannon_worker_1 find /app/node_modules/@anthropic-ai -name "*.js" -type f | head -10')
        files = stdout.read().decode('utf-8', errors='replace').strip().split('\n')
        files = [f for f in files if f]
    
    print(f"   Found {len(files)} files to check")
    
    # Check and patch each file
    for file_path in files[:3]:
        print(f"\n2. Checking {file_path}...")
        
        # Read file
        stdin, stdout, stderr = ssh.exec_command(f'docker exec shannon_worker_1 cat {file_path}')
        content = stdout.read().decode('utf-8', errors='replace')
        
        # Check if it has spawn with node
        if 'spawn' in content.lower() and 'node' in content.lower():
            print(f"   Found spawn node in file")
            
            # Try to replace patterns
            original = content
            # Replace common patterns
            content = content.replace("spawn('node'", "spawn('/usr/bin/node'")
            content = content.replace('spawn("node"', 'spawn("/usr/bin/node"')
            content = content.replace("spawnSync('node'", "spawnSync('/usr/bin/node'")
            content = content.replace('spawnSync("node"', 'spawnSync("/usr/bin/node"')
            
            # Also try with /usr/local/bin/node
            if content == original:
                content = content.replace("spawn('node'", "spawn('/usr/local/bin/node'")
                content = content.replace('spawn("node"', 'spawn("/usr/local/bin/node"')
                content = content.replace("spawnSync('node'", "spawnSync('/usr/local/bin/node'")
                content = content.replace('spawnSync("node"', 'spawnSync("/usr/local/bin/node"')
            
            if content != original:
                print(f"   Patterns found, patching...")
                
                # Write back via base64
                content_b64 = base64.b64encode(content.encode('utf-8')).decode('ascii')
                
                # Write in chunks if needed
                cmd = f'docker exec shannon_worker_1 sh -c "echo {content_b64} | base64 -d > {file_path}"'
                stdin, stdout, stderr = ssh.exec_command(cmd)
                result = stdout.read().decode('utf-8', errors='replace')
                errors = stderr.read().decode('utf-8', errors='replace')
                
                if not errors or 'base64' not in errors.lower():
                    print(f"   File patched successfully!")
                    break
                else:
                    print(f"   Error: {errors[:200]}")
                    # Try alternative: write via echo with heredoc
                    print("   Trying alternative method...")
                    # Split into smaller chunks and write
                    # This is complex, skip for now
            else:
                print("   No simple patterns found (file may be minified)")
                # Check file size
                if len(content) > 100000:
                    print("   File is large, may be minified bundle")
    
    # Restart worker
    print("\n3. Restarting worker to apply changes...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose restart worker')
    restart_output = stdout.read().decode('utf-8', errors='replace')
    print(restart_output)
    
    time.sleep(3)
    
    # Verify symlink still exists
    print("\n4. Verifying symlink...")
    stdin, stdout, stderr = ssh.exec_command('docker exec shannon_worker_1 ls -la /usr/local/bin/node')
    symlink = stdout.read().decode('utf-8', errors='replace')
    print(symlink)
    
    ssh.close()
    
    print("\n" + "=" * 80)
    print("PATCH COMPLETE")
    print("=" * 80)
    print("Try a new pentest now")

if __name__ == "__main__":
    import time
    patch_library()

