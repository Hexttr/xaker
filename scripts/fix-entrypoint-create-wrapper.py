#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix entrypoint to create wrapper as root"""

import paramiko
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def fix_entrypoint():
    """Fix entrypoint"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("FIX ENTRYPOINT TO CREATE WRAPPER AS ROOT")
    print("=" * 80)
    
    # Update docker-compose.yml entrypoint to create wrapper as root before switching to pentest
    print("\n1. Updating docker-compose.yml...")
    sftp = ssh.open_sftp()
    with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'r') as f:
        compose = f.read().decode('utf-8')
    
    # Update entrypoint to create wrapper as root, then switch to pentest
    compose = compose.replace(
        '    entrypoint: ["/bin/sh", "-c"]',
        '    entrypoint: ["/bin/sh", "-c", "mkdir -p /app/bin && echo \\"#!/bin/sh\\" > /app/bin/node && echo \\"exec /usr/bin/node \\\\\\"$@\\\\\\\\\\"\\" >> /app/bin/node && chmod +x /app/bin/node && chown pentest:pentest /app/bin/node && exec su pentest -c \\"/app/start-worker.sh\\""]'
    )
    
    # Remove command line
    compose_lines = compose.split('\n')
    new_lines = []
    skip_next = False
    for line in compose_lines:
        if 'command:' in line and 'mkdir' in line:
            skip_next = True
            continue
        if skip_next and ('dist/temporal' in line or 'worker.js' in line):
            skip_next = False
            continue
        new_lines.append(line)
    
    compose = '\n'.join(new_lines)
    
    with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'w') as f:
        f.write(compose.encode('utf-8'))
    sftp.close()
    
    # Update startup script to use /app/bin in PATH
    print("\n2. Updating startup script...")
    sftp = ssh.open_sftp()
    startup_script = """#!/bin/sh
set -e
# Set PATH explicitly - /app/bin first so wrapper is found
export PATH="/app/bin:/usr/bin:/usr/local/bin:/bin:/usr/sbin:/sbin"
export NODE="/usr/bin/node"
# Verify node is accessible
if ! command -v node >/dev/null 2>&1; then
    echo "ERROR: node not found in PATH: $PATH"
    ls -la /usr/bin/node /app/bin/node 2>&1 || true
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
    print("\n3. Restarting worker...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose stop worker && docker-compose rm -f worker && docker-compose up -d worker')
    restart_output = stdout.read().decode('utf-8', errors='replace')
    print(restart_output)
    
    import time
    time.sleep(5)
    
    # Verify
    print("\n4. Verifying...")
    stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon | grep worker')
    worker = stdout.read().decode('utf-8', errors='replace')
    if worker:
        container_id = worker.split()[0]
        print(f"   Worker container: {container_id}")
        
        stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "su pentest -c \'echo PATH=$PATH && which node && node --version && ls -la /app/bin/node\'"')
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
                print("\n5. Restarting backend...")
                stdin, stdout, stderr = ssh.exec_command('pm2 restart xaker-backend')
                print(stdout.read().decode('utf-8', errors='replace'))
                
                print("\n" + "=" * 80)
                print("✅ SUCCESS! FINAL FIX APPLIED")
                print("=" * 80)
                print("\nNode wrapper is created in /app/bin by root before switching to pentest")
                print("/app/bin is first in PATH, so spawn('node') will find it")
                print("\nTry a new pentest now!")
    
    ssh.close()

if __name__ == "__main__":
    import time
    fix_entrypoint()

