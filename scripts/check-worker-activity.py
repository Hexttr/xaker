#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check worker activity logs and node availability"""

import paramiko
import sys

# Fix encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def check_activity():
    """Check worker activity"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("CHECKING WORKER ACTIVITY")
    print("=" * 80)
    
    # Check PATH
    print("\n1. Checking PATH in container...")
    stdin, stdout, stderr = ssh.exec_command('docker exec shannon_worker_1 printenv PATH')
    path = stdout.read().decode('utf-8', errors='replace').strip()
    print(f"   PATH: {path}")
    
    # Check node availability
    print("\n2. Checking node availability...")
    stdin, stdout, stderr = ssh.exec_command('docker exec shannon_worker_1 sh -c "which node && node --version"')
    node_info = stdout.read().decode('utf-8', errors='replace')
    print(f"   {node_info.strip()}")
    
    # Check recent worker logs
    print("\n3. Recent worker logs (last 30 lines)...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker logs shannon_worker_1 --tail=30 2>&1')
    logs = stdout.read().decode('utf-8', errors='replace')
    print(logs[-2000:])
    
    # Check activities.js to see how node is spawned
    print("\n4. Checking activities.js for node spawn...")
    stdin, stdout, stderr = ssh.exec_command('docker exec shannon_worker_1 grep -n "spawn.*node\|child_process\|exec" /app/dist/temporal/activities.js 2>&1 | head -20')
    activities_code = stdout.read().decode('utf-8', errors='replace')
    if activities_code.strip():
        print(activities_code)
    else:
        print("   Could not find activities.js or spawn code")
    
    ssh.close()
    
    print("\n" + "=" * 80)
    print("ANALYSIS")
    print("=" * 80)

if __name__ == "__main__":
    check_activity()

