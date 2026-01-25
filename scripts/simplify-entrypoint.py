#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Simplify entrypoint"""

import paramiko
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def simplify():
    """Simplify entrypoint"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("Simplifying entrypoint...")
    
    sftp = ssh.open_sftp()
    with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'r') as f:
        compose = f.read().decode('utf-8')
    
    # Simplify: use startup script but ensure wrapper is created first
    compose_lines = compose.split('\n')
    for i, line in enumerate(compose_lines):
        if 'entrypoint:' in line and 'worker:' in '\n'.join(compose_lines[max(0, i-5):i]):
            # Replace with simple entrypoint that runs startup script
            compose_lines[i] = '    entrypoint: ["/bin/sh", "/app/start-worker.sh"]'
            # Remove command if exists
            if i+1 < len(compose_lines) and 'command:' in compose_lines[i+1]:
                compose_lines.pop(i+1)
            break
    
    compose = '\n'.join(compose_lines)
    
    # Update startup script to create wrapper first (as root, then switch)
    startup_script = """#!/bin/sh
set -e
# Create wrapper as root (we're running as root initially)
mkdir -p /app/bin
echo '#!/bin/sh' > /app/bin/node
echo 'exec /usr/bin/node "$@"' >> /app/bin/node
chmod +x /app/bin/node
chown pentest:pentest /app/bin/node
# Switch to pentest user
exec su pentest -c 'export PATH="/app/bin:/usr/bin:/usr/local/bin:/bin:/usr/sbin:/sbin" && export NODE="/usr/bin/node" && cd /app && node dist/temporal/worker.js'
"""
    
    with sftp.open('/opt/xaker/shannon/start-worker.sh', 'w') as f:
        f.write(startup_script.encode('utf-8'))
    
    ssh.exec_command('chmod +x /opt/xaker/shannon/start-worker.sh')
    
    with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'w') as f:
        f.write(compose.encode('utf-8'))
    
    sftp.close()
    
    print("✅ Updated")
    
    # Restart
    print("Restarting worker...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose stop worker && docker-compose rm -f worker && docker-compose up -d worker')
    print(stdout.read().decode('utf-8', errors='replace'))
    
    import time
    time.sleep(5)
    
    stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon | grep worker')
    worker = stdout.read().decode('utf-8', errors='replace')
    if worker:
        container_id = worker.split()[0]
        stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "su pentest -c \'which node && node --version\'"')
        print(stdout.read().decode('utf-8', errors='replace'))
        
        stdin, stdout, stderr = ssh.exec_command(f'docker logs {container_id} --tail=10 2>&1')
        logs = stdout.read().decode('utf-8', errors='replace')
        if 'Shannon worker started' in logs:
            print("\n✅ SUCCESS! Worker running!")
            stdin, stdout, stderr = ssh.exec_command('pm2 restart xaker-backend')
            print("✅ Backend restarted")
            print("\n✅ Application ready for pentests!")
    
    ssh.close()

if __name__ == "__main__":
    import time
    simplify()

