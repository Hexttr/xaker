#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Force rebuild worker image"""

import paramiko
import sys
import time

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def force_rebuild():
    """Force rebuild"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("FORCING REBUILD")
    print("=" * 80)
    
    # Stop and remove
    print("\n1. Stopping worker...")
    ssh.exec_command('cd /opt/xaker/shannon && docker-compose stop worker')
    time.sleep(2)
    
    print("2. Removing container and image...")
    ssh.exec_command('cd /opt/xaker/shannon && docker-compose rm -f worker')
    ssh.exec_command('docker rmi shannon_worker shannon_worker:latest 2>&1 || true')
    time.sleep(2)
    
    # Rebuild with output
    print("\n3. Rebuilding worker (this will take 2-3 minutes)...")
    print("   Starting build...")
    
    chan = ssh.get_transport().open_session()
    chan.exec_command('cd /opt/xaker/shannon && docker-compose build --no-cache --progress=plain worker 2>&1')
    
    output = ""
    while True:
        if chan.recv_ready():
            chunk = chan.recv(1024).decode('utf-8', errors='replace')
            output += chunk
            # Print last 200 chars
            if len(output) > 200:
                print(output[-200:], end='', flush=True)
                output = output[-200:]
        elif chan.exit_status_ready():
            break
        time.sleep(0.1)
    
    remaining = chan.recv(10000).decode('utf-8', errors='replace')
    print(remaining[-500:])
    
    # Start
    print("\n4. Starting worker...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose up -d worker')
    print(stdout.read().decode('utf-8', errors='replace'))
    
    time.sleep(5)
    
    # Verify
    print("\n5. Verifying...")
    stdin, stdout, stderr = ssh.exec_command('docker exec shannon_worker_1 sh -c "ls -la /app/bin/node 2>&1 && echo --- && printenv PATH"')
    verify = stdout.read().decode('utf-8', errors='replace')
    print(verify)
    
    ssh.close()
    
    print("\n" + "=" * 80)
    if '/app/bin/node' in verify:
        print("✅ SUCCESS! Wrapper created")
    else:
        print("⚠️  Wrapper not found - check Dockerfile")

if __name__ == "__main__":
    force_rebuild()

