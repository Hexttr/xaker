#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix docker-compose syntax"""

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

print("Reading docker-compose.yml...")
sftp = ssh.open_sftp()
with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'r') as f:
    compose = f.read().decode('utf-8')

print("\nFixing syntax...")
# Fix environment variables - they should be in list format with dashes
compose_lines = compose.split('\n')
new_lines = []
in_worker_env = False

for i, line in enumerate(compose_lines):
    if 'worker:' in line:
        new_lines.append(line)
        continue
    
    if 'environment:' in line and 'worker:' in '\n'.join(new_lines[-5:]):
        in_worker_env = True
        new_lines.append(line)
        continue
    
    if in_worker_env:
        # Fix environment variables format
        if 'NODE=' in line and not line.strip().startswith('-'):
            new_lines.append('      - NODE=/usr/bin/node')
            continue
        elif 'PATH=' in line and not line.strip().startswith('-'):
            new_lines.append('      - PATH=/usr/bin:/usr/local/bin:/bin:/usr/sbin:/sbin')
            continue
        elif line.strip() and not line.startswith(' ') and not line.startswith('-'):
            in_worker_env = False
            new_lines.append(line)
            continue
    
    new_lines.append(line)

compose = '\n'.join(new_lines)

# Ensure NODE and PATH are in correct format
if '- NODE=/usr/bin/node' not in compose:
    # Find environment: section and add NODE
    compose_lines = compose.split('\n')
    for i, line in enumerate(compose_lines):
        if 'environment:' in line and 'worker:' in '\n'.join(compose_lines[max(0,i-10):i]):
            # Add NODE after environment:
            if '- NODE=' not in '\n'.join(compose_lines[i:i+10]):
                compose_lines.insert(i+1, '      - NODE=/usr/bin/node')
            break
    compose = '\n'.join(compose_lines)

print("\nWriting fixed docker-compose.yml...")
with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'w') as f:
    f.write(compose.encode('utf-8'))

sftp.close()

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
    
    # Verify NODE
    stdin, stdout, stderr = ssh.exec_command('docker exec shannon_worker_1 sh -c "echo NODE=$NODE"')
    print("NODE env:", stdout.read().decode('utf-8', errors='replace'))
else:
    print("\n⚠️ Worker not running")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose logs worker --tail=20')
    print(stdout.read().decode('utf-8', errors='replace'))

ssh.close()

