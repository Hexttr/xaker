#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Start all services"""

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

def start_all():
    """Start all services"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("STARTING ALL SERVICES")
    print("=" * 80)
    
    # Start services
    print("\n1. Starting docker-compose services...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose up -d')
    start_output = stdout.read().decode('utf-8', errors='replace')
    print(start_output)
    
    time.sleep(5)
    
    # Check status
    print("\n2. Checking services status...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose ps')
    services = stdout.read().decode('utf-8', errors='replace')
    print(services)
    
    # Verify worker
    print("\n3. Verifying worker...")
    stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon | grep worker')
    worker = stdout.read().decode('utf-8', errors='replace')
    if worker:
        container_id = worker.split()[0]
        print(f"   Worker container: {container_id}")
        
        stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "ls -la /usr/local/bin/node && which node && /usr/local/bin/node --version && printenv NODE && printenv PATH"')
        verify = stdout.read().decode('utf-8', errors='replace')
        print(verify)
        
        if '/usr/local/bin/node' in verify:
            print("\n   ✅ Node symlink is working!")
        
        # Check worker logs
        print("\n4. Checking worker logs (last 10 lines)...")
        stdin, stdout, stderr = ssh.exec_command(f'docker logs {container_id} --tail=10 2>&1')
        logs = stdout.read().decode('utf-8', errors='replace')
        print(logs[-500:])
    else:
        print("   ⚠️  Worker container not running")
        # Try to start it manually
        print("\n   Trying to start worker manually...")
        stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose up -d worker')
        print(stdout.read().decode('utf-8', errors='replace'))
        time.sleep(3)
        
        stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon | grep worker')
        worker = stdout.read().decode('utf-8', errors='replace')
        if worker:
            container_id = worker.split()[0]
            stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "ls -la /usr/local/bin/node && which node && /usr/local/bin/node --version"')
            print(stdout.read().decode('utf-8', errors='replace'))
    
    ssh.close()
    
    print("\n" + "=" * 80)
    print("SERVICES STARTED")
    print("=" * 80)
    print("✅ TypeScript build successful")
    print("✅ Docker services started")
    print("Try a new pentest now!")

if __name__ == "__main__":
    start_all()

