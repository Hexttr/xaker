#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rebuild Docker image with wrappers"""

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

print("=" * 80)
print("REBUILD DOCKER IMAGE WITH NODE WRAPPERS")
print("=" * 80)
print("\n⚠️  This will rebuild the Docker image")
print("This may take several minutes")
print("Proceeding with rebuild...")

print("\n1. Stopping worker...")
stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose stop worker && docker-compose rm -f worker')
print(stdout.read().decode('utf-8', errors='replace'))

print("\n2. Rebuilding image (this may take 5-10 minutes)...")
print("   Building with --no-cache to ensure wrappers are included...")
stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && timeout 600 docker-compose build --no-cache worker 2>&1')

# Monitor build progress
print("   Building... (this will take a while)")
import threading

def monitor_build():
    while True:
        output = stdout.read(1000).decode('utf-8', errors='replace')
        if output:
            print(output[-500:], end='', flush=True)
        time.sleep(2)
        if 'Successfully' in output or 'ERROR' in output:
            break

# Wait for build (with timeout)
time.sleep(60)  # Wait a bit for build to start

build_output = ""
for _ in range(60):  # Check every 10 seconds for 10 minutes
    chunk = stdout.read(10000).decode('utf-8', errors='replace')
    if chunk:
        build_output += chunk
        if 'Successfully' in chunk or 'Successfully tagged' in chunk:
            print("\n   ✅ Build successful!")
            break
        if 'ERROR' in chunk:
            print("\n   ⚠️ Build error detected")
            break
    time.sleep(10)
    print(".", end='', flush=True)

print("\n\n3. Build output (last 1000 chars):")
print(build_output[-1000:])

if 'Successfully' in build_output or 'Successfully tagged' in build_output:
    print("\n4. Starting worker with new image...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose up -d worker')
    output = stdout.read().decode('utf-8', errors='replace')
    print(output)
    
    time.sleep(5)
    
    print("\n5. Verifying worker...")
    stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon_worker')
    worker = stdout.read().decode('utf-8', errors='replace')
    if worker:
        print("   ✅ Worker is running!")
        
        # Check wrappers
        container_id = worker.split()[0]
        stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "which node && ls -la /usr/local/bin/node /bin/node"')
        verify = stdout.read().decode('utf-8', errors='replace')
        print(verify)
        
        # Restart backend
        print("\n6. Restarting backend...")
        stdin, stdout, stderr = ssh.exec_command('pm2 restart xaker-backend')
        print(stdout.read().decode('utf-8', errors='replace'))
        
        print("\n" + "=" * 80)
        print("✅ SUCCESS!")
        print("=" * 80)
        print("\nDocker image rebuilt with node wrappers")
        print("Worker is running")
        print("\n⚠️  Try a new pentest now!")
    else:
        print("   ⚠️ Worker not running")
else:
    print("\n   ⚠️ Build may have failed or timed out")
    print("   Check logs manually")

ssh.close()

