#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix Shannon worker issue"""

import paramiko
import sys
import os

# Fix encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def fix_worker():
    """Fix Shannon worker"""
    print("=" * 80)
    print("FIXING SHANNON WORKER")
    print("=" * 80)
    
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
        
        # Check Docker containers
        print("\n1. Checking Docker containers...")
        stdin, stdout, stderr = ssh.exec_command("cd /opt/xaker/shannon && docker-compose ps 2>&1 || docker compose ps 2>&1")
        compose_status = stdout.read().decode('utf-8', errors='replace')
        print(compose_status)
        
        # Check worker logs
        print("\n2. Checking worker logs (last 50 lines)...")
        stdin, stdout, stderr = ssh.exec_command("cd /opt/xaker/shannon && docker-compose logs --tail=50 worker 2>&1 || docker compose logs --tail=50 worker 2>&1")
        worker_logs = stdout.read().decode('utf-8', errors='replace')
        print(worker_logs[-3000:])
        
        # Try to restart worker
        print("\n3. Restarting worker...")
        stdin, stdout, stderr = ssh.exec_command("cd /opt/xaker/shannon && docker-compose restart worker 2>&1 || docker compose restart worker 2>&1")
        restart_output = stdout.read().decode('utf-8', errors='replace')
        restart_errors = stderr.read().decode('utf-8', errors='replace')
        print(restart_output)
        if restart_errors:
            print(f"Errors: {restart_errors}")
        
        # Check status after restart
        print("\n4. Checking status after restart...")
        stdin, stdout, stderr = ssh.exec_command("cd /opt/xaker/shannon && docker-compose ps 2>&1 || docker compose ps 2>&1")
        final_status = stdout.read().decode('utf-8', errors='replace')
        print(final_status)
        
        # Alternative: start worker directly
        if "Exited" in final_status or "exited" in final_status:
            print("\n5. Trying to start worker directly...")
            stdin, stdout, stderr = ssh.exec_command("cd /opt/xaker/shannon && docker-compose up -d worker 2>&1 || docker compose up -d worker 2>&1")
            start_output = stdout.read().decode('utf-8', errors='replace')
            print(start_output)
        
        ssh.close()
        
        print("\n" + "=" * 80)
        print("FIX COMPLETE")
        print("=" * 80)
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_worker()

