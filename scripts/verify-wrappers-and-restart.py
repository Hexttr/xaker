#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verify wrappers and restart"""

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

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)

print("Checking wrappers and restarting worker...")

stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon_worker')
worker = stdout.read().decode('utf-8', errors='replace')

if worker:
    container_id = worker.split()[0]
    print(f"Worker container: {container_id}")
    
    print("\n1. Checking wrappers...")
    stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "which node && /usr/local/bin/node --version && /bin/node --version && echo PATH=$PATH"')
    check = stdout.read().decode('utf-8', errors='replace')
    print(check)
    
    print("\n2. Restarting worker...")
    stdin, stdout, stderr = ssh.exec_command(f'docker restart {container_id}')
    print(stdout.read().decode('utf-8', errors='replace'))
    
    time.sleep(5)
    
    print("\n3. Checking worker status...")
    stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon_worker')
    status = stdout.read().decode('utf-8', errors='replace')
    print(status)
    
    if status:
        print("\n✅ Worker is running!")
        print("\n⚠️  Wrappers are created in the running container")
        print("They will be lost if container is recreated")
        print("\nTry a new pentest now!")
        print("If it still fails, we need to:")
        print("1. Free up disk space")
        print("2. Rebuild Docker image with wrappers")
    else:
        print("\n⚠️ Worker not running")
else:
    print("⚠️ Worker not running")
    print("Starting worker...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose up -d worker')
    print(stdout.read().decode('utf-8', errors='replace'))

ssh.close()

