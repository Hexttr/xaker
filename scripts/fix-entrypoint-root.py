#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix entrypoint to run as root"""

import paramiko
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def fix_entrypoint_root():
    """Fix entrypoint to run as root"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("FIXING ENTRYPOINT TO RUN AS ROOT")
    print("=" * 80)
    
    # Update docker-compose.yml entrypoint to run as root
    print("\n1. Updating docker-compose.yml...")
    sftp = ssh.open_sftp()
    with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'r') as f:
        compose = f.read().decode('utf-8')
    
    # Replace entrypoint to run as root
    compose = compose.replace(
        '    entrypoint: ["/bin/sh", "/app/start-worker.sh"]',
        '    entrypoint: ["/bin/sh", "-c", "export PATH=/usr/bin:/usr/local/bin:/bin:/usr/sbin:/sbin && export NODE=/usr/bin/node && cd /app && exec node dist/temporal/worker.js"]'
    )
    
    # Also add user: root
    if 'user:' not in compose or 'user: root' not in compose:
        compose_lines = compose.split('\n')
        for i, line in enumerate(compose_lines):
            if 'worker:' in line:
                # Add user: root after worker:
                compose_lines.insert(i+1, '    user: root')
                break
        compose = '\n'.join(compose_lines)
    
    with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'w') as f:
        f.write(compose.encode('utf-8'))
    sftp.close()
    print("   ✅ docker-compose.yml updated")
    
    # Restart worker
    print("\n2. Restarting worker...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose stop worker && docker-compose rm -f worker && docker-compose up -d worker')
    print(stdout.read().decode('utf-8', errors='replace'))
    
    import time
    time.sleep(5)
    
    # Verify
    print("\n3. Verifying...")
    stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon | grep worker')
    worker = stdout.read().decode('utf-8', errors='replace')
    if worker:
        container_id = worker.split()[0]
        stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "whoami && which node && node --version"')
        verify = stdout.read().decode('utf-8', errors='replace')
        print(f"\n   Verification:\n{verify}")
        
        if 'root' in verify and 'v22' in verify:
            print("\n   ✅ Worker running as root!")
            
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
                print("✅ SUCCESS!")
                print("=" * 80)
                print("\nWorker is running as root")
                print("Node is accessible: /usr/bin/node")
                print("PATH includes /usr/bin")
                print("\n⚠️  Security note: Running as root is less secure")
                print("but solves the spawn node ENOENT issue")
                print("\nTry a new pentest now!")
            else:
                print("\n   ⚠️ Worker may not be fully started")
        else:
            print("\n   ⚠️ Still running as pentest or node not accessible")
    else:
        print("   ⚠️ Worker not running")
    
    ssh.close()

if __name__ == "__main__":
    import time
    fix_entrypoint_root()

