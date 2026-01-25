#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix entrypoint to use simple startup script"""

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
    print("FIXING ENTRYPOINT - USE SIMPLE STARTUP SCRIPT")
    print("=" * 80)
    
    # Update startup script
    print("\n1. Updating startup script...")
    sftp = ssh.open_sftp()
    startup_script = """#!/bin/sh
set -e
export PATH="/usr/bin:/usr/local/bin:/bin:/sbin:/app/bin:/tmp:$PATH"
export NODE="/usr/bin/node"
mkdir -p /usr/local/bin /bin /sbin /app/bin /tmp
ln -sf /usr/bin/node /usr/local/bin/node 2>/dev/null || true
ln -sf /usr/bin/node /bin/node 2>/dev/null || true
ln -sf /usr/bin/node /sbin/node 2>/dev/null || true
ln -sf /usr/bin/node /app/bin/node 2>/dev/null || true
ln -sf /usr/bin/node /tmp/node 2>/dev/null || true
cd /app
exec node dist/temporal/worker.js
"""
    
    with sftp.open('/opt/xaker/shannon/start-worker.sh', 'w') as f:
        f.write(startup_script.encode('utf-8'))
    sftp.close()
    ssh.exec_command('chmod +x /opt/xaker/shannon/start-worker.sh')
    print("   ✅ Startup script updated")
    
    # Update docker-compose.yml to use simple entrypoint
    print("\n2. Updating docker-compose.yml...")
    sftp = ssh.open_sftp()
    with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'r') as f:
        compose = f.read().decode('utf-8')
    
    # Replace entrypoint with simple one
    compose = compose.replace(
        '    entrypoint: ["/bin/sh", "-c", "export PATH=/usr/bin:/usr/local/bin:/bin:/sbin:/app/bin:/tmp:/opt:/home:$PATH && export NODE=/usr/bin/node && mkdir -p /usr/local/bin /bin /sbin /app/bin /tmp && ln -sf /usr/bin/node /usr/local/bin/node && ln -sf /usr/bin/node /bin/node && ln -sf /usr/bin/node /sbin/node && ln -sf /usr/bin/node /app/bin/node && ln -sf /usr/bin/node /tmp/node && cd /app && exec node dist/temporal/worker.js"]',
        '    entrypoint: ["/bin/sh", "/app/start-worker.sh"]'
    )
    
    # Ensure user is root
    if 'user: root' not in compose:
        compose_lines = compose.split('\n')
        for i, line in enumerate(compose_lines):
            if 'worker:' in line:
                compose_lines.insert(i+1, '    user: root')
                break
        compose = '\n'.join(compose_lines)
    
    with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'w') as f:
        f.write(compose.encode('utf-8'))
    sftp.close()
    print("   ✅ docker-compose.yml updated")
    
    # Copy startup script to container
    print("\n3. Copying startup script to container...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose build worker 2>&1 | tail -5')
    build_output = stdout.read().decode('utf-8', errors='replace')
    print(build_output)
    
    # Restart worker
    print("\n4. Restarting worker...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose stop worker && docker-compose rm -f worker && docker-compose up -d worker')
    restart_output = stdout.read().decode('utf-8', errors='replace')
    print(restart_output)
    
    import time
    time.sleep(5)
    
    # Verify
    print("\n5. Verifying...")
    stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon | grep worker')
    worker_check = stdout.read().decode('utf-8', errors='replace')
    if worker_check:
        container_id = worker_check.split()[0]
        stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "whoami && which node && node --version"')
        verify = stdout.read().decode('utf-8', errors='replace')
        print(f"\n   Verification:\n{verify}")
        
        if 'root' in verify and 'v22' in verify:
            print("\n   ✅ Worker running!")
            
            stdin, stdout, stderr = ssh.exec_command(f'docker logs {container_id} --tail=10 2>&1')
            logs = stdout.read().decode('utf-8', errors='replace')
            if 'RUNNING' in logs:
                print("\n   ✅ Worker is RUNNING!")
                stdin, stdout, stderr = ssh.exec_command('pm2 restart xaker-backend')
                print("   ✅ Backend restarted")
                print("\n✅ SUCCESS! Worker is running with node accessible")
                print("Try a new pentest now!")
    else:
        print("   ⚠️ Worker not running")
        stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose logs worker --tail=20')
        print(stdout.read().decode('utf-8', errors='replace'))
    
    ssh.close()

if __name__ == "__main__":
    import time
    fix_entrypoint()

