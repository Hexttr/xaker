#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Final rebuild and check"""

import paramiko
import sys
import time

# Fix encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def rebuild_and_check():
    """Rebuild and check"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("FINAL REBUILD AND CHECK")
    print("=" * 80)
    
    # Check Dockerfile
    print("\n1. Checking Dockerfile...")
    stdin, stdout, stderr = ssh.exec_command('grep -A 2 "USER pentest" /opt/xaker/shannon/Dockerfile | head -5')
    dockerfile_check = stdout.read().decode('utf-8', errors='replace')
    print(dockerfile_check)
    
    # Stop and remove
    print("\n2. Stopping and removing old container...")
    ssh.exec_command('cd /opt/xaker/shannon && docker-compose stop worker')
    ssh.exec_command('cd /opt/xaker/shannon && docker-compose rm -f worker')
    time.sleep(2)
    
    # Rebuild
    print("\n3. Rebuilding worker image...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose build worker 2>&1')
    # Wait for build
    time.sleep(30)
    build_output = stdout.read().decode('utf-8', errors='replace')
    if 'Successfully built' in build_output or 'Successfully tagged' in build_output:
        print("   ✅ Build successful")
    else:
        print(f"   Build output (last 500 chars):\n{build_output[-500:]}")
    
    # Start
    print("\n4. Starting worker...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose up -d worker')
    start_output = stdout.read().decode('utf-8', errors='replace')
    print(start_output)
    
    time.sleep(5)
    
    # Check wrapper
    print("\n5. Checking wrapper...")
    stdin, stdout, stderr = ssh.exec_command('docker exec shannon_worker_1 ls -la /app/bin/node 2>&1')
    wrapper = stdout.read().decode('utf-8', errors='replace')
    print(wrapper)
    
    # Check PATH
    print("\n6. Checking PATH...")
    stdin, stdout, stderr = ssh.exec_command('docker exec shannon_worker_1 printenv PATH')
    path = stdout.read().decode('utf-8', errors='replace')
    print(f"   PATH: {path}")
    
    # Check which node
    print("\n7. Checking which node...")
    stdin, stdout, stderr = ssh.exec_command('docker exec shannon_worker_1 sh -c "which node"')
    which_node = stdout.read().decode('utf-8', errors='replace')
    print(f"   which node: {which_node}")
    
    # Check node version via wrapper
    print("\n8. Testing node wrapper...")
    stdin, stdout, stderr = ssh.exec_command('docker exec shannon_worker_1 sh -c "/app/bin/node --version 2>&1"')
    node_version = stdout.read().decode('utf-8', errors='replace')
    print(f"   /app/bin/node --version: {node_version}")
    
    ssh.close()
    
    print("\n" + "=" * 80)
    print("CHECK COMPLETE")
    print("=" * 80)
    if "/app/bin/node" in wrapper or "/app/bin" in path:
        print("✅ Wrapper should be available")
        print("Try a new pentest")
    else:
        print("⚠️  Wrapper may not be working")
        print("Check Dockerfile and rebuild")

if __name__ == "__main__":
    rebuild_and_check()

