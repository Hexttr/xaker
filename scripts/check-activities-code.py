#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check activities.js code for node spawn"""

import paramiko
import sys

# Fix encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def check_code():
    """Check activities.js code"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("CHECKING ACTIVITIES.JS CODE")
    print("=" * 80)
    
    # Read around line 213 where error occurs
    print("\n1. Code around line 213 (error location)...")
    stdin, stdout, stderr = ssh.exec_command('docker exec shannon_worker_1 sed -n "200,230p" /app/dist/temporal/activities.js')
    code_213 = stdout.read().decode('utf-8', errors='replace')
    print(code_213)
    
    # Search for spawn calls
    print("\n2. Searching for spawn calls...")
    stdin, stdout, stderr = ssh.exec_command('docker exec shannon_worker_1 grep -n "spawn" /app/dist/temporal/activities.js')
    spawn_lines = stdout.read().decode('utf-8', errors='replace')
    print(spawn_lines[:1000])
    
    # Check claude-executor.js which is imported
    print("\n3. Checking claude-executor.js...")
    stdin, stdout, stderr = ssh.exec_command('docker exec shannon_worker_1 grep -n "spawn.*node\|exec.*node" /app/dist/ai/claude-executor.js | head -20')
    executor_code = stdout.read().decode('utf-8', errors='replace')
    if executor_code.strip():
        print(executor_code)
    else:
        print("   Could not find spawn in claude-executor.js")
    
    # Check if we can patch it
    print("\n4. Checking if we can use full path to node...")
    stdin, stdout, stderr = ssh.exec_command('docker exec shannon_worker_1 sh -c "which node"')
    node_path = stdout.read().decode('utf-8', errors='replace').strip()
    print(f"   Node path: {node_path}")
    
    ssh.close()
    
    print("\n" + "=" * 80)
    print("SOLUTION")
    print("=" * 80)
    print("Need to patch activities.js or claude-executor.js to use full path to node")
    print(f"or ensure PATH is passed to spawn() call")

if __name__ == "__main__":
    check_code()

