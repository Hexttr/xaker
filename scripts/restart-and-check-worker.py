#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Restart and check worker"""

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

print("Restarting worker...")
stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose stop worker && docker-compose rm -f worker && docker-compose up -d worker')
print(stdout.read().decode('utf-8', errors='replace'))

time.sleep(5)

print("\nChecking environment...")
stdin, stdout, stderr = ssh.exec_command('docker exec shannon_worker_1 sh -c "echo NODE=$NODE && echo PATH=$PATH && which node"')
env_output = stdout.read().decode('utf-8', errors='replace')
print(env_output)

if 'NODE=' in env_output and '/usr/bin/node' in env_output.split('NODE=')[1].split('\n')[0]:
    print("\n✅ NODE is set correctly!")
else:
    print("\n⚠️ NODE is not set. Checking docker-compose.yml...")
    sftp = ssh.open_sftp()
    with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'r') as f:
        compose = f.read().decode('utf-8')
    sftp.close()
    
    if '- NODE=/usr/bin/node' in compose:
        print("   NODE is in docker-compose.yml but not in container")
        print("   This might be a Docker caching issue")
        print("   Try: docker-compose down && docker-compose up -d")
    else:
        print("   NODE is missing from docker-compose.yml")

print("\nWorker status:")
stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon_worker')
print(stdout.read().decode('utf-8', errors='replace'))

ssh.close()

