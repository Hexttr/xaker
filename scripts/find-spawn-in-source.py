#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Find spawn in source code"""

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
    """Find spawn in source"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("Finding spawn calls...")
    
    # Check source code
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && grep -rn "spawn.*node\|spawnSync.*node" src/ 2>/dev/null | head -10')
    source_matches = stdout.read().decode('utf-8', errors='replace')
    print(f"Source code:\n{source_matches}")
    
    # Check compiled code
    stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon | grep worker')
    worker = stdout.read().decode('utf-8', errors='replace')
    if worker:
        container_id = worker.split()[0]
        stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} grep -n "spawn" /app/dist/temporal/activities.js | head -10')
        compiled_matches = stdout.read().decode('utf-8', errors='replace')
        print(f"\nCompiled code:\n{compiled_matches}")
        
        # Read around line 213 where error occurs
        stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sed -n "200,230p" /app/dist/temporal/activities.js')
        code_around_error = stdout.read().decode('utf-8', errors='replace')
        print(f"\nCode around line 213:\n{code_around_error}")
    
    ssh.close()

if __name__ == "__main__":
    find_spawn()

