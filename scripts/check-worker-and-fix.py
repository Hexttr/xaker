#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check worker and fix if needed"""

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

def check_and_fix():
    """Check worker and fix"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("CHECKING WORKER AND FIXING")
    print("=" * 80)
    
    # Check docker-compose status
    print("\n1. Checking docker-compose status...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose ps')
    status = stdout.read().decode('utf-8', errors='replace')
    print(status)
    
    # Start worker if not running
    if 'worker' not in status or 'Up' not in status:
        print("\n2. Starting worker...")
        stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose up -d worker')
        start_output = stdout.read().decode('utf-8', errors='replace')
        print(start_output)
        time.sleep(5)
    
    # Get container name
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose ps worker | tail -1 | awk "{print $1}"')
    container_name = stdout.read().decode('utf-8', errors='replace').strip()
    if not container_name:
        container_name = 'shannon_worker_1'
    
    print(f"\n3. Container name: {container_name}")
    
    # Verify symlink
    print("\n4. Verifying symlink...")
    stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_name} sh -c "ls -la /usr/local/bin/node 2>&1"')
    symlink = stdout.read().decode('utf-8', errors='replace')
    print(symlink)
    
    # If symlink doesn't exist, create it
    if 'No such file' in symlink or not symlink.strip():
        print("\n5. Symlink not found, creating it...")
        stdin, stdout, stderr = ssh.exec_command(f'docker exec -u root {container_name} sh -c "mkdir -p /usr/local/bin && ln -sf /usr/bin/node /usr/local/bin/node && ls -la /usr/local/bin/node"')
        create_output = stdout.read().decode('utf-8', errors='replace')
        print(create_output)
    
    # Verify node availability
    print("\n6. Verifying node availability...")
    stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_name} sh -c "which node && /usr/local/bin/node --version && printenv PATH"')
    verify = stdout.read().decode('utf-8', errors='replace')
    print(verify)
    
    # Check worker logs
    print("\n7. Checking worker logs (last 10 lines)...")
    stdin, stdout, stderr = ssh.exec_command(f'docker logs {container_name} --tail=10 2>&1')
    logs = stdout.read().decode('utf-8', errors='replace')
    print(logs[-500:])
    
    ssh.close()
    
    print("\n" + "=" * 80)
    print("CHECK COMPLETE")
    print("=" * 80)
    if 'node' in verify.lower() and ('->' in symlink or '/usr/local/bin/node' in verify):
        print("✅ SUCCESS! Worker is running and node is available")
        print("Try a new pentest now")
    else:
        print("⚠️  Some checks failed")

if __name__ == "__main__":
    check_and_fix()

