#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix Shannon spawn to use full node path"""

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
    """Fix spawn in Shannon source"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("FIXING SHANNON SPAWN")
    print("=" * 80)
    
    # Find source files
    print("\n1. Finding source files...")
    stdin, stdout, stderr = ssh.exec_command('find /opt/xaker/shannon/src -name "claude-executor.ts" -o -name "claude-executor.js" 2>/dev/null')
    source_files = stdout.read().decode('utf-8', errors='replace').strip().split('\n')
    source_files = [f for f in source_files if f]
    
    if not source_files:
        print("   ⚠️  Source files not found, checking dist...")
        stdin, stdout, stderr = ssh.exec_command('find /opt/xaker/shannon/dist -name "*claude*executor*" -type f 2>/dev/null')
        dist_files = stdout.read().decode('utf-8', errors='replace').strip().split('\n')
        dist_files = [f for f in dist_files if f]
        print(f"   Found dist files: {dist_files}")
        source_files = dist_files
    
    # Check for spawn calls
    for file_path in source_files[:1]:  # Check first file
        print(f"\n2. Checking {file_path}...")
        stdin, stdout, stderr = ssh.exec_command(f'grep -n "spawn.*node\|spawnSync.*node" {file_path} | head -10')
        spawn_lines = stdout.read().decode('utf-8', errors='replace')
        if spawn_lines.strip():
            print(spawn_lines)
        else:
            print("   No spawn found, checking for child_process...")
            stdin, stdout, stderr = ssh.exec_command(f'grep -n "child_process\|spawn" {file_path} | head -20')
            cp_lines = stdout.read().decode('utf-8', errors='replace')
            print(cp_lines[:1000])
    
    # Alternative: Create a wrapper script
    print("\n3. Creating wrapper script approach...")
    wrapper_script = """#!/bin/sh
exec /usr/bin/node "$@"
"""
    
    sftp = ssh.open_sftp()
    try:
        with sftp.open('/app/node-wrapper.sh', 'w') as f:
            f.write(wrapper_script.encode('utf-8'))
        print("   ✅ Wrapper script created")
    except Exception as e:
        print(f"   ⚠️  Could not create wrapper: {e}")
    
    # Make it executable
    stdin, stdout, stderr = ssh.exec_command('docker exec shannon_worker_1 chmod +x /app/node-wrapper.sh 2>&1')
    print(stdout.read().decode('utf-8', errors='replace'))
    
    # Alternative solution: Set PATH in entrypoint or use symlink
    print("\n4. Creating symlink approach...")
    stdin, stdout, stderr = ssh.exec_command('docker exec shannon_worker_1 sh -c "ln -sf /usr/bin/node /usr/local/bin/node 2>&1 || echo already exists"')
    symlink_result = stdout.read().decode('utf-8', errors='replace')
    print(symlink_result)
    
    # Check if node is in /usr/local/bin now
    stdin, stdout, stderr = ssh.exec_command('docker exec shannon_worker_1 sh -c "which node && ls -la /usr/local/bin/node 2>&1"')
    node_check = stdout.read().decode('utf-8', errors='replace')
    print(f"\n5. Node check:\n{node_check}")
    
    sftp.close()
    ssh.close()
    
    print("\n" + "=" * 80)
    print("SOLUTION APPLIED")
    print("=" * 80)
    print("Created symlink /usr/local/bin/node -> /usr/bin/node")
    print("This should help if code looks for node in /usr/local/bin")
    print("\nIf this doesn't work, need to patch source code to use full path")

if __name__ == "__main__":
    fix_spawn()

