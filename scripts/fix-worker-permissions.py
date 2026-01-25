#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix Shannon worker permissions"""

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

def fix_permissions():
    """Fix permissions for Shannon worker"""
    print("=" * 80)
    print("FIXING SHANNON WORKER PERMISSIONS")
    print("=" * 80)
    
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
        
        # Fix audit-logs directory permissions
        print("\n1. Fixing audit-logs directory permissions...")
        commands = [
            "cd /opt/xaker/shannon",
            "chmod -R 777 audit-logs 2>&1 || true",
            "chown -R 1000:1000 audit-logs 2>&1 || true",  # Docker user ID
            "ls -la audit-logs | head -10"
        ]
        stdin, stdout, stderr = ssh.exec_command(" && ".join(commands))
        output = stdout.read().decode('utf-8', errors='replace')
        errors = stderr.read().decode('utf-8', errors='replace')
        print(output)
        if errors:
            print(f"Errors: {errors}")
        
        # Check Docker user
        print("\n2. Checking Docker container user...")
        stdin, stdout, stderr = ssh.exec_command("cd /opt/xaker/shannon && docker-compose exec -T worker id 2>&1 || docker compose exec -T worker id 2>&1")
        user_info = stdout.read().decode('utf-8', errors='replace')
        print(user_info)
        
        # Fix permissions inside container
        print("\n3. Fixing permissions inside container...")
        stdin, stdout, stderr = ssh.exec_command("cd /opt/xaker/shannon && docker-compose exec -T worker chmod -R 777 /app/audit-logs 2>&1 || docker compose exec -T worker chmod -R 777 /app/audit-logs 2>&1")
        container_fix = stdout.read().decode('utf-8', errors='replace')
        print(container_fix)
        
        # Restart worker
        print("\n4. Restarting worker...")
        stdin, stdout, stderr = ssh.exec_command("cd /opt/xaker/shannon && docker-compose restart worker 2>&1 || docker compose restart worker 2>&1")
        restart_output = stdout.read().decode('utf-8', errors='replace')
        print(restart_output)
        
        # Check status
        print("\n5. Checking worker status...")
        stdin, stdout, stderr = ssh.exec_command("cd /opt/xaker/shannon && docker-compose ps worker 2>&1 || docker compose ps worker 2>&1")
        status = stdout.read().decode('utf-8', errors='replace')
        print(status)
        
        ssh.close()
        
        print("\n" + "=" * 80)
        print("PERMISSIONS FIXED")
        print("=" * 80)
        print("Worker should now be able to write logs.")
        print("Check logs in a few seconds to see if it's working.")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_permissions()

