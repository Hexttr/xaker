#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix docker-compose final"""

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

print("Reading and fixing docker-compose.yml...")
sftp = ssh.open_sftp()
with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'r') as f:
    compose = f.read().decode('utf-8')

# Remove incorrect NODE from security_opt and end of file
compose_lines = compose.split('\n')
new_lines = []
in_security_opt = False

for i, line in enumerate(compose_lines):
    if 'security_opt:' in line:
        in_security_opt = True
        new_lines.append(line)
        continue
    
    if in_security_opt:
        if 'NODE=' in line:
            # Skip this line - it's in wrong place
            continue
        elif line.strip() and not line.startswith(' ') and not line.startswith('-'):
            in_security_opt = False
            new_lines.append(line)
            continue
    
    # Skip duplicate NODE at end of file
    if i == len(compose_lines) - 2 and 'NODE=' in line:
        continue
    
    new_lines.append(line)

compose = '\n'.join(new_lines)

# Ensure NODE is in environment section
if '- NODE=/usr/bin/node' not in compose.split('environment:')[1].split('depends_on:')[0]:
    # Add NODE to environment
    compose_lines = compose.split('\n')
    for i, line in enumerate(compose_lines):
        if 'environment:' in line and 'worker:' in '\n'.join(compose_lines[max(0,i-10):i]):
            # Check if NODE already exists
            if '- NODE=' not in '\n'.join(compose_lines[i:i+15]):
                compose_lines.insert(i+1, '      - NODE=/usr/bin/node')
            break
    compose = '\n'.join(compose_lines)

print("\nWriting fixed docker-compose.yml...")
with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'w') as f:
    f.write(compose.encode('utf-8'))

sftp.close()

print("\nStarting worker...")
stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose stop worker && docker-compose rm -f worker && docker-compose up -d worker 2>&1')
output = stdout.read().decode('utf-8', errors='replace')
error = stderr.read().decode('utf-8', errors='replace')
print(output)
if error:
    print(f"Errors: {error}")

import time
time.sleep(5)

stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon_worker')
worker = stdout.read().decode('utf-8', errors='replace')
if worker:
    print("\n✅ Worker is running!")
    
    # Verify NODE
    stdin, stdout, stderr = ssh.exec_command('docker exec shannon_worker_1 sh -c "echo NODE=$NODE && echo PATH=$PATH"')
    print("Environment:", stdout.read().decode('utf-8', errors='replace'))
    
    # Restart backend
    print("\nRestarting backend...")
    stdin, stdout, stderr = ssh.exec_command('pm2 restart xaker-backend')
    print(stdout.read().decode('utf-8', errors='replace'))
    
    print("\n" + "=" * 80)
    print("✅ SUCCESS!")
    print("=" * 80)
    print("\nNODE=/usr/bin/node is now correctly set in environment")
    print("Worker is running")
    print("\n⚠️  Try a new pentest now!")
    print("If it still fails with spawn node ENOENT, the library")
    print("needs to be patched to use NODE env variable or process.execPath")
else:
    print("\n⚠️ Worker not running")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose logs worker --tail=20')
    print(stdout.read().decode('utf-8', errors='replace'))

ssh.close()

