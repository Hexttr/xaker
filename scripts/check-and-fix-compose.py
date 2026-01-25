#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check and fix docker-compose"""

import paramiko
import sys

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

print("Checking docker-compose.yml...")
sftp = ssh.open_sftp()
with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'r') as f:
    compose = f.read().decode('utf-8')

print("\nCurrent docker-compose.yml:")
print(compose[:1000])

# Check if worker service exists
if 'worker:' in compose:
    print("\n✅ Worker service found")
    
    # Try to start worker
    print("\nStarting worker...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose up -d worker 2>&1')
    output = stdout.read().decode('utf-8', errors='replace')
    error = stderr.read().decode('utf-8', errors='replace')
    print(output)
    if error:
        print(f"Errors: {error}")
    
    import time
    time.sleep(3)
    
    stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon_worker')
    worker = stdout.read().decode('utf-8', errors='replace')
    if worker:
        print("\n✅ Worker is running!")
    else:
        print("\n⚠️ Worker not running")
        stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose logs worker --tail=20')
        print(stdout.read().decode('utf-8', errors='replace'))
else:
    print("\n⚠️ Worker service not found in docker-compose.yml")

sftp.close()
ssh.close()

