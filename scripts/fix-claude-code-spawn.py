#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix spawn in @anthropic-ai/claude-code library"""

import paramiko
import sys
import re

# Fix encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def fix_spawn():
    """Fix spawn calls in node_modules"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("FIXING CLAUDE-CODE SPAWN")
    print("=" * 80)
    
    # Find files with spawn node
    print("\n1. Finding files with 'spawn.*node'...")
    stdin, stdout, stderr = ssh.exec_command('docker exec shannon_worker_1 find /app/node_modules/@anthropic-ai -name "*.js" -type f -exec grep -l "spawn.*node\|spawnSync.*node" {} \\; 2>/dev/null | head -10')
    files = stdout.read().decode('utf-8', errors='replace').strip().split('\n')
    files = [f for f in files if f]
    
    if not files:
        print("   ⚠️  No files found, searching differently...")
        stdin, stdout, stderr = ssh.exec_command('docker exec shannon_worker_1 find /app/node_modules/@anthropic-ai -name "*.js" -type f | head -20')
        all_files = stdout.read().decode('utf-8', errors='replace').strip().split('\n')
        print(f"   Found {len(all_files)} files in @anthropic-ai")
        files = all_files[:5]
    
    print(f"   Found {len(files)} files to check")
    
    # Check first file
    if files:
        file_path = files[0]
        print(f"\n2. Checking {file_path}...")
        stdin, stdout, stderr = ssh.exec_command(f'docker exec shannon_worker_1 grep -n "spawn.*node\|spawnSync.*node\|child_process" {file_path} | head -20')
        spawn_lines = stdout.read().decode('utf-8', errors='replace')
        print(spawn_lines[:2000])
        
        # Read file content around spawn
        if spawn_lines:
            print(f"\n3. Reading file content...")
            stdin, stdout, stderr = ssh.exec_command(f'docker exec shannon_worker_1 cat {file_path} | head -500')
            file_content = stdout.read().decode('utf-8', errors='replace')
            print(file_content[:3000])
    
    # Alternative: Patch through environment variable
    print("\n4. Trying environment variable approach...")
    print("   Setting NODE_PATH or patching through wrapper...")
    
    # Create wrapper script in container
    wrapper_script = """#!/bin/sh
# Node wrapper that ensures PATH
export PATH=/usr/bin:/usr/local/bin:$PATH
exec /usr/bin/node "$@"
"""
    
    sftp = ssh.open_sftp()
    try:
        # Write wrapper to temp location
        stdin, stdout, stderr = ssh.exec_command('docker exec shannon_worker_1 sh -c "echo \'#!/bin/sh\nexport PATH=/usr/bin:/usr/local/bin:$PATH\nexec /usr/bin/node \"$@\"\' > /tmp/node-wrapper.sh && chmod +x /tmp/node-wrapper.sh"')
        print(stdout.read().decode('utf-8', errors='replace'))
        
        # Try to use wrapper by setting PATH to include /tmp
        print("\n5. Updating PATH in docker-compose.yml...")
        stdin, stdout, stderr = ssh.exec_command('grep -A 2 "PATH=" /opt/xaker/shannon/docker-compose.yml | head -5')
        current_path = stdout.read().decode('utf-8', errors='replace')
        print(f"   Current PATH: {current_path}")
        
    except Exception as e:
        print(f"   ERROR: {e}")
    
    sftp.close()
    
    # Final solution: Patch the library code directly
    print("\n6. Attempting direct code patch...")
    if files:
        file_to_patch = files[0]
        print(f"   Patching {file_to_patch}...")
        
        # Read file
        stdin, stdout, stderr = ssh.exec_command(f'docker exec shannon_worker_1 cat {file_to_patch}')
        file_content = stdout.read().decode('utf-8', errors='replace')
        
        # Replace 'node' with '/usr/bin/node' in spawn calls
        if "'node'" in file_content or '"node"' in file_content:
            # This is risky - need to be careful
            new_content = file_content.replace("spawn('node'", "spawn('/usr/bin/node'").replace('spawn("node"', 'spawn("/usr/bin/node"')
            new_content = new_content.replace("spawnSync('node'", "spawnSync('/usr/bin/node'").replace('spawnSync("node"', 'spawnSync("/usr/bin/node"')
            
            if new_content != file_content:
                print("   ✅ Found node spawn calls, patching...")
                # Write back through docker exec
                # This is complex, need to use base64 or other method
                print("   ⚠️  Direct patch requires file write access")
            else:
                print("   ⚠️  No simple spawn('node') patterns found")
    
    ssh.close()
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print("Need to either:")
    print("1. Rebuild image with symlink in Dockerfile")
    print("2. Patch library code to use /usr/bin/node")
    print("3. Set NODE environment variable")

if __name__ == "__main__":
    fix_spawn()

