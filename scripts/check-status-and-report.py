#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check status and report"""

import paramiko
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def check_status():
    """Check status"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("CURRENT STATUS CHECK")
    print("=" * 80)
    
    # Check docker-compose.yml
    print("\n1. Checking docker-compose.yml...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose config 2>&1 | head -5')
    config_check = stdout.read().decode('utf-8', errors='replace')
    if 'error' in config_check.lower():
        print(f"   ⚠️ Error: {config_check}")
        print("\n   Need to fix duplicate NODE env var")
    else:
        print("   ✅ docker-compose.yml is valid")
    
    # Check worker
    print("\n2. Checking worker...")
    stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon | grep worker')
    worker = stdout.read().decode('utf-8', errors='replace')
    if worker:
        container_id = worker.split()[0]
        print(f"   ✅ Worker running: {container_id}")
        
        # Check node
        stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "su pentest -c \'which node && node --version 2>&1\'"')
        node_check = stdout.read().decode('utf-8', errors='replace')
        if 'v22' in node_check:
            print(f"   ✅ Node accessible: {node_check.strip()}")
        else:
            print(f"   ⚠️ Node not accessible: {node_check}")
            print("   Need to rebuild Docker image")
    else:
        print("   ⚠️ Worker not running")
    
    # Check backend
    print("\n3. Checking backend...")
    stdin, stdout, stderr = ssh.exec_command('pm2 list | grep xaker-backend')
    backend = stdout.read().decode('utf-8', errors='replace')
    if backend and 'online' in backend:
        print("   ✅ Backend running")
    else:
        print("   ⚠️ Backend not running")
    
    ssh.close()
    
    print("\n" + "=" * 80)
    print("STATUS CHECK COMPLETE")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Fix duplicate NODE in docker-compose.yml (if needed)")
    print("2. Rebuild Docker image (if node not accessible)")
    print("3. Restart services")
    print("\nRun: python scripts/final-complete-rebuild.py")

if __name__ == "__main__":
    check_status()

