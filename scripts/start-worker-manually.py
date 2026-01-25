#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Start worker manually and verify"""

import paramiko
import sys
import time

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def start_worker():
    """Start worker manually"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("STARTING WORKER MANUALLY")
    print("=" * 80)
    
    # Check if image exists
    print("\n1. Checking if image exists...")
    stdin, stdout, stderr = ssh.exec_command('docker images | grep shannon')
    images = stdout.read().decode('utf-8', errors='replace')
    print(images)
    
    # Check docker-compose.yml
    print("\n2. Checking docker-compose.yml...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose config 2>&1 | head -30')
    config = stdout.read().decode('utf-8', errors='replace')
    print(config)
    
    # Try to start worker
    print("\n3. Starting worker...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose up -d worker 2>&1')
    start_output = stdout.read().decode('utf-8', errors='replace')
    errors = stderr.read().decode('utf-8', errors='replace')
    print(f"Output: {start_output}")
    if errors:
        print(f"Errors: {errors}")
    
    time.sleep(5)
    
    # Check status
    print("\n4. Checking status...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose ps')
    status = stdout.read().decode('utf-8', errors='replace')
    print(status)
    
    # Get container name
    stdin, stdout, stderr = ssh.exec_command('docker ps -a | grep shannon | grep worker | awk "{print $1}" | head -1')
    container_id = stdout.read().decode('utf-8', errors='replace').strip()
    
    if container_id:
        print(f"\n5. Container ID: {container_id}")
        
        # Check logs
        print("\n6. Checking container logs...")
        stdin, stdout, stderr = ssh.exec_command(f'docker logs {container_id} --tail=20 2>&1')
        logs = stdout.read().decode('utf-8', errors='replace')
        print(logs[-1000:])
        
        # Verify symlink
        print("\n7. Verifying symlink...")
        stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "ls -la /usr/local/bin/node 2>&1 || echo NOT_FOUND"')
        symlink = stdout.read().decode('utf-8', errors='replace')
        print(symlink)
        
        # Create symlink if needed
        if 'NOT_FOUND' in symlink or 'No such file' in symlink:
            print("\n8. Creating symlink...")
            stdin, stdout, stderr = ssh.exec_command(f'docker exec -u root {container_id} sh -c "mkdir -p /usr/local/bin && ln -sf /usr/bin/node /usr/local/bin/node && ls -la /usr/local/bin/node"')
            create_output = stdout.read().decode('utf-8', errors='replace')
            print(create_output)
        
        # Verify node
        print("\n9. Verifying node...")
        stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "which node && /usr/local/bin/node --version && printenv PATH"')
        verify = stdout.read().decode('utf-8', errors='replace')
        print(verify)
    else:
        print("\n5. No container found")
    
    ssh.close()
    
    print("\n" + "=" * 80)
    print("START COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    start_worker()

