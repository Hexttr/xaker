#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rebuild worker properly with symlink"""

import paramiko
import sys
import time

# Fix encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def rebuild():
    """Rebuild worker"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("REBUILDING WORKER PROPERLY")
    print("=" * 80)
    
    # Stop worker
    print("\n1. Stopping worker...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose stop worker')
    print(stdout.read().decode('utf-8', errors='replace'))
    
    # Remove old container
    print("\n2. Removing old container...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose rm -f worker')
    print(stdout.read().decode('utf-8', errors='replace'))
    
    # Verify Dockerfile has symlink
    print("\n3. Verifying Dockerfile...")
    stdin, stdout, stderr = ssh.exec_command('grep -n "ln.*node" /opt/xaker/shannon/Dockerfile')
    dockerfile_check = stdout.read().decode('utf-8', errors='replace')
    print(dockerfile_check)
    
    # Rebuild with no cache
    print("\n4. Rebuilding worker image (this may take a while)...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose build --no-cache worker 2>&1')
    # Read output in chunks
    output = ""
    while True:
        chunk = stdout.read(1024).decode('utf-8', errors='replace')
        if not chunk:
            break
        output += chunk
        # Print last 500 chars
        if len(output) > 500:
            print(output[-500:], end='', flush=True)
            output = output[-500:]
    
    print("\n" + output[-1000:])
    
    # Start worker
    print("\n5. Starting worker...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose up -d worker')
    start_output = stdout.read().decode('utf-8', errors='replace')
    print(start_output)
    
    time.sleep(5)
    
    # Verify symlink exists
    print("\n6. Verifying symlink in new container...")
    stdin, stdout, stderr = ssh.exec_command('docker exec shannon_worker_1 ls -la /usr/local/bin/node 2>&1')
    symlink = stdout.read().decode('utf-8', errors='replace')
    print(symlink)
    
    # Check node availability
    print("\n7. Checking node availability...")
    stdin, stdout, stderr = ssh.exec_command('docker exec shannon_worker_1 sh -c "which node && /usr/local/bin/node --version 2>&1"')
    node_check = stdout.read().decode('utf-8', errors='replace')
    print(node_check)
    
    # Check logs
    print("\n8. Checking worker logs...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker logs shannon_worker_1 --tail=10 2>&1')
    logs = stdout.read().decode('utf-8', errors='replace')
    print(logs)
    
    ssh.close()
    
    print("\n" + "=" * 80)
    print("REBUILD COMPLETE")
    print("=" * 80)
    if "node" in symlink.lower() or "node" in node_check.lower():
        print("✅ Symlink created successfully!")
        print("Try a new pentest now")
    else:
        print("⚠️  Symlink may not be created")
        print("Need to check Dockerfile or use alternative approach")

if __name__ == "__main__":
    rebuild()

