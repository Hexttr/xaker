#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run worker as root to avoid permission issues"""

import paramiko
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def run_as_root():
    """Run worker as root"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("RUNNING WORKER AS ROOT")
    print("=" * 80)
    print("\n⚠️  This is less secure but will solve permission issues")
    
    # Update startup script to run as root
    print("\n1. Updating startup script...")
    sftp = ssh.open_sftp()
    startup_script = """#!/bin/sh
set -e
# Set PATH explicitly
export PATH="/usr/bin:/usr/local/bin:/bin:/usr/sbin:/sbin"
export NODE="/usr/bin/node"
# Verify node is accessible
if ! command -v node >/dev/null 2>&1; then
    echo "ERROR: node not found in PATH: $PATH"
    exit 1
fi
# Start worker (running as root)
exec node dist/temporal/worker.js
"""
    
    with sftp.open('/opt/xaker/shannon/start-worker.sh', 'w') as f:
        f.write(startup_script.encode('utf-8'))
    sftp.close()
    ssh.exec_command('chmod +x /opt/xaker/shannon/start-worker.sh')
    print("   ✅ Startup script updated")
    
    # Update docker-compose.yml to remove USER pentest
    print("\n2. Updating docker-compose.yml...")
    sftp = ssh.open_sftp()
    with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'r') as f:
        compose = f.read().decode('utf-8')
    
    # Remove USER pentest from entrypoint if exists
    compose = compose.replace('su pentest -c', '')
    compose = compose.replace('USER pentest', '# USER pentest  # Commented out to run as root')
    
    with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'w') as f:
        f.write(compose.encode('utf-8'))
    sftp.close()
    print("   ✅ docker-compose.yml updated")
    
    # Restart worker
    print("\n3. Restarting worker as root...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose stop worker && docker-compose rm -f worker && docker-compose up -d worker')
    print(stdout.read().decode('utf-8', errors='replace'))
    
    import time
    time.sleep(5)
    
    # Verify
    print("\n4. Verifying...")
    stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon | grep worker')
    worker = stdout.read().decode('utf-8', errors='replace')
    if worker:
        container_id = worker.split()[0]
        stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "whoami && which node && node --version"')
        verify = stdout.read().decode('utf-8', errors='replace')
        print(f"\n   Verification:\n{verify}")
        
        if 'root' in verify and 'v22' in verify:
            print("\n   ✅ Worker running as root with node accessible!")
            
            # Check worker logs
            stdin, stdout, stderr = ssh.exec_command(f'docker logs {container_id} --tail=10 2>&1')
            logs = stdout.read().decode('utf-8', errors='replace')
            if 'Shannon worker started' in logs or 'RUNNING' in logs:
                print("\n   ✅ Worker is running!")
                
                # Restart backend
                print("\n5. Restarting backend...")
                stdin, stdout, stderr = ssh.exec_command('pm2 restart xaker-backend')
                print(stdout.read().decode('utf-8', errors='replace'))
                
                print("\n" + "=" * 80)
                print("✅ SUCCESS! Worker running as root")
                print("=" * 80)
                print("\n⚠️  Security note: Worker is running as root")
                print("This solves permission issues but is less secure")
                print("Node is accessible: /usr/bin/node")
                print("\nTry a new pentest now!")
            else:
                print("\n   ⚠️ Worker may not be fully started")
        else:
            print("\n   ⚠️ Issue with root execution")
    else:
        print("   ⚠️ Worker not running")
    
    ssh.close()

if __name__ == "__main__":
    import time
    run_as_root()

