#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rebuild worker now"""

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

def rebuild_now():
    """Rebuild now"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("Stopping worker...")
    ssh.exec_command('cd /opt/xaker/shannon && docker-compose stop worker')
    time.sleep(2)
    
    print("Removing container...")
    ssh.exec_command('cd /opt/xaker/shannon && docker-compose rm -f worker')
    time.sleep(2)
    
    print("Rebuilding (this takes 2-3 minutes)...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose build --no-cache worker')
    
    # Wait and check
    time.sleep(120)
    build_output = stdout.read(100000).decode('utf-8', errors='replace')
    if 'Successfully' in build_output:
        print("Build successful!")
    print(f"Last 300 chars: {build_output[-300:]}")
    
    print("Starting worker...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose up -d worker')
    print(stdout.read().decode('utf-8', errors='replace'))
    
    time.sleep(5)
    
    print("Checking wrapper...")
    stdin, stdout, stderr = ssh.exec_command('docker exec shannon_worker_1 ls -la /app/bin/node 2>&1 && docker exec shannon_worker_1 printenv PATH')
    verify = stdout.read().decode('utf-8', errors='replace')
    print(verify)
    
    if '/app/bin/node' in verify:
        print("SUCCESS! Wrapper created. Try a new pentest.")
    else:
        print("Wrapper not found. Check Dockerfile.")
    
    ssh.close()

if __name__ == "__main__":
    rebuild_now()

