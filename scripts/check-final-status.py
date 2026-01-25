#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check final status"""

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

def check_status():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("Checking final status...")
    
    stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon | grep worker')
    worker = stdout.read().decode('utf-8', errors='replace')
    print(f"Worker: {worker if worker else 'Not running'}")
    
    if worker:
        container_id = worker.split()[0]
        stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "su pentest -c \'which node && node --version && ls -la /app/bin/node\'"')
        verify = stdout.read().decode('utf-8', errors='replace')
        print(f"\nVerification:\n{verify}")
        
        stdin, stdout, stderr = ssh.exec_command(f'docker logs {container_id} --tail=10 2>&1')
        logs = stdout.read().decode('utf-8', errors='replace')
        print(f"\nWorker logs:\n{logs[-300:]}")
        
        if 'v22' in verify and 'Shannon worker started' in logs:
            print("\n✅ SUCCESS! Worker is running and node is accessible!")
            print("Try a new pentest now!")
        else:
            print("\n⚠️ May need more time or there's still an issue")
    else:
        print("Worker not running - checking logs...")
        stdin, stdout, stderr = ssh.exec_command('docker ps -a | grep shannon | grep worker | head -1')
        worker_line = stdout.read().decode('utf-8', errors='replace')
        if worker_line:
            container_id = worker_line.split()[0]
            stdin, stdout, stderr = ssh.exec_command(f'docker logs {container_id} --tail=20 2>&1')
            print(stdout.read().decode('utf-8', errors='replace'))
    
    ssh.close()

if __name__ == "__main__":
    check_status()

