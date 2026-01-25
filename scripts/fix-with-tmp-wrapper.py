#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix by creating wrapper in /tmp"""

import paramiko
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def fix_with_tmp():
    """Fix by creating wrapper in /tmp"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("FIX: CREATE WRAPPER IN /tmp")
    print("=" * 80)
    
    # Update startup script to create wrapper in /tmp (writable by pentest)
    print("\n1. Updating startup script...")
    sftp = ssh.open_sftp()
    startup_script = """#!/bin/sh
set -e
# Set PATH explicitly - /tmp first so wrapper is found
export PATH="/tmp:/app/bin:/usr/bin:/usr/local/bin:/bin:/usr/sbin:/sbin"
export NODE="/usr/bin/node"
# Create node wrapper in /tmp (writable by pentest user)
mkdir -p /tmp
echo '#!/bin/sh' > /tmp/node
echo 'exec /usr/bin/node "$@"' >> /tmp/node
chmod +x /tmp/node
# Verify node is accessible
if ! command -v node >/dev/null 2>&1; then
    echo "ERROR: node not found in PATH: $PATH"
    ls -la /usr/bin/node /tmp/node 2>&1 || true
    exit 1
fi
# Start worker
exec node dist/temporal/worker.js
"""
    
    with sftp.open('/opt/xaker/shannon/start-worker.sh', 'w') as f:
        f.write(startup_script.encode('utf-8'))
    sftp.close()
    ssh.exec_command('chmod +x /opt/xaker/shannon/start-worker.sh')
    print("   ✅ Startup script updated")
    
    # Restart worker
    print("\n2. Restarting worker...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose stop worker && docker-compose rm -f worker && docker-compose up -d worker')
    restart_output = stdout.read().decode('utf-8', errors='replace')
    print(restart_output)
    
    import time
    time.sleep(5)
    
    # Verify
    print("\n3. Verifying...")
    stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon | grep worker')
    worker = stdout.read().decode('utf-8', errors='replace')
    if worker:
        container_id = worker.split()[0]
        print(f"   Worker container: {container_id}")
        
        stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "su pentest -c \'echo PATH=$PATH && which node && node --version && ls -la /tmp/node\'"')
        verify = stdout.read().decode('utf-8', errors='replace')
        print(f"\n   Verification:\n{verify}")
        
        if 'v22' in verify:
            print("\n   ✅ Node wrapper is working!")
            
            # Check worker logs
            stdin, stdout, stderr = ssh.exec_command(f'docker logs {container_id} --tail=10 2>&1')
            logs = stdout.read().decode('utf-8', errors='replace')
            print(f"\n   Worker logs:\n{logs[-300:]}")
            
            if 'Shannon worker started' in logs or 'RUNNING' in logs:
                print("\n   ✅ Worker is running!")
                
                # Restart backend
                print("\n4. Restarting backend...")
                stdin, stdout, stderr = ssh.exec_command('pm2 restart xaker-backend')
                print(stdout.read().decode('utf-8', errors='replace'))
                
                print("\n" + "=" * 80)
                print("✅ SUCCESS! FINAL FIX APPLIED")
                print("=" * 80)
                print("\nNode wrapper is created in /tmp on each container start")
                print("/tmp is first in PATH, so spawn('node') will find it")
                print("\nTry a new pentest now!")
            else:
                print("\n   ⚠️ Worker may not be fully started")
        else:
            print("\n   ⚠️ Node still not accessible")
    else:
        print("   ⚠️ Worker not running")
        stdin, stdout, stderr = ssh.exec_command('docker ps -a | grep shannon | grep worker | head -1')
        worker_line = stdout.read().decode('utf-8', errors='replace')
        if worker_line:
            container_id = worker_line.split()[0]
            stdin, stdout, stderr = ssh.exec_command(f'docker logs {container_id} --tail=20 2>&1')
            print(stdout.read().decode('utf-8', errors='replace'))
    
    ssh.close()

if __name__ == "__main__":
    import time
    fix_with_tmp()

