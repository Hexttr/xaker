#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check Node.js in worker container"""

import paramiko
import sys
import os

# Fix encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def check_node():
    """Check Node.js in worker container"""
    print("=" * 80)
    print("CHECKING NODE.JS IN WORKER CONTAINER")
    print("=" * 80)
    
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
        
        # Check Node.js in container
        print("\n1. Checking Node.js in worker container...")
        stdin, stdout, stderr = ssh.exec_command("cd /opt/xaker/shannon && docker-compose exec worker node --version 2>&1 || docker compose exec worker node --version 2>&1")
        node_version = stdout.read().decode('utf-8', errors='replace')
        print(f"   Node version: {node_version.strip()}")
        
        # Check PATH in container
        print("\n2. Checking PATH in container...")
        stdin, stdout, stderr = ssh.exec_command("cd /opt/xaker/shannon && docker-compose exec worker echo $PATH 2>&1 || docker compose exec worker echo $PATH 2>&1")
        path_info = stdout.read().decode('utf-8', errors='replace')
        print(f"   PATH: {path_info.strip()}")
        
        # Check where node is
        print("\n3. Finding node executable...")
        stdin, stdout, stderr = ssh.exec_command("cd /opt/xaker/shannon && docker-compose exec worker which node 2>&1 || docker compose exec worker which node 2>&1")
        node_path = stdout.read().decode('utf-8', errors='replace')
        print(f"   Node path: {node_path.strip()}")
        
        # Check Dockerfile
        print("\n4. Checking Dockerfile...")
        stdin, stdout, stderr = ssh.exec_command("cd /opt/xaker/shannon && cat Dockerfile 2>&1 | head -30")
        dockerfile = stdout.read().decode('utf-8', errors='replace')
        print(dockerfile)
        
        # Check docker-compose.yml
        print("\n5. Checking docker-compose.yml worker service...")
        stdin, stdout, stderr = ssh.exec_command("cd /opt/xaker/shannon && grep -A 20 'worker:' docker-compose.yml 2>&1 | head -25")
        compose_config = stdout.read().decode('utf-8', errors='replace')
        print(compose_config)
        
        ssh.close()
        
        print("\n" + "=" * 80)
        print("ANALYSIS")
        print("=" * 80)
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_node()

