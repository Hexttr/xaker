#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Find where spawn node is called"""

import paramiko
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def find_spawn():
    """Find spawn location"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("FINDING SPAWN LOCATION")
    print("=" * 80)
    
    # Check worker container
    stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon | grep worker')
    worker = stdout.read().decode('utf-8', errors='replace')
    if not worker:
        print("Worker not running")
        ssh.close()
        return
    
    container_id = worker.split()[0]
    
    # Find spawn calls in node_modules
    print("\n1. Searching for spawn('node') in node_modules...")
    stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} find /app/node_modules/@anthropic-ai -name "*.js" -type f -exec grep -l "spawn.*node\|spawnSync.*node" {{}} \\; 2>/dev/null | head -5')
    files = stdout.read().decode('utf-8', errors='replace').strip().split('\n')
    files = [f for f in files if f]
    
    if files:
        print(f"   Found {len(files)} files:")
        for f in files:
            print(f"   - {f}")
        
        # Check first file
        file_path = files[0]
        print(f"\n2. Checking {file_path}...")
        stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} grep -n "spawn.*node\|spawnSync.*node" {file_path} | head -10')
        spawn_lines = stdout.read().decode('utf-8', errors='replace')
        print(spawn_lines)
        
        # Read context around spawn
        if spawn_lines:
            line_num = spawn_lines.split(':')[0] if ':' in spawn_lines else None
            if line_num:
                start = max(1, int(line_num) - 5)
                end = int(line_num) + 5
                print(f"\n3. Code around line {line_num}:")
                stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sed -n "{start},{end}p" {file_path}')
                code = stdout.read().decode('utf-8', errors='replace')
                print(code)
    else:
        print("   No files found, searching differently...")
        # Search in dist
        stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} find /app/dist -name "*.js" -type f -exec grep -l "spawn.*node" {{}} \\; 2>/dev/null | head -5')
        dist_files = stdout.read().decode('utf-8', errors='replace').strip().split('\n')
        if dist_files:
            print(f"   Found in dist: {dist_files}")
    
    # Check if we can patch it
    print("\n4. Solution: Patch spawn to use full path")
    print("   We need to replace spawn('node' with spawn(process.env.NODE || '/usr/bin/node'")
    print("   Or patch the library code directly")
    
    ssh.close()

if __name__ == "__main__":
    find_spawn()

