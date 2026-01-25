#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verify worker fix"""

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

def verify():
    """Verify worker fix"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("VERIFYING WORKER FIX")
    print("=" * 80)
    
    # Restart worker
    print("\n1. Restarting worker...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose restart worker')
    output = stdout.read().decode('utf-8', errors='replace')
    errors = stderr.read().decode('utf-8', errors='replace')
    print(output)
    if errors:
        print(f"Errors: {errors}")
    
    time.sleep(3)
    
    # Check status
    print("\n2. Checking worker status...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose ps worker')
    status = stdout.read().decode('utf-8', errors='replace')
    print(status)
    
    # Check symlink
    print("\n3. Checking symlink...")
    stdin, stdout, stderr = ssh.exec_command('docker exec shannon_worker_1 ls -la /usr/local/bin/node 2>&1')
    symlink = stdout.read().decode('utf-8', errors='replace')
    print(symlink)
    
    # Check node availability
    print("\n4. Checking node availability...")
    stdin, stdout, stderr = ssh.exec_command('docker exec shannon_worker_1 sh -c "which node && /usr/local/bin/node --version 2>&1"')
    node_check = stdout.read().decode('utf-8', errors='replace')
    print(node_check)
    
    # Check logs
    print("\n5. Recent worker logs...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker logs shannon_worker_1 --tail=15 2>&1')
    logs = stdout.read().decode('utf-8', errors='replace')
    print(logs[-1000:])
    
    ssh.close()
    
    print("\n" + "=" * 80)
    print("VERIFICATION COMPLETE")
    print("=" * 80)
    print("If symlink exists and worker is running, try a new pentest")

if __name__ == "__main__":
    verify()

