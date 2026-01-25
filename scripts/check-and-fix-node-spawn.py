#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check and fix node spawn issue"""

import paramiko
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def check_and_fix():
    """Check and fix"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("CHECKING AND FIXING NODE SPAWN ISSUE")
    print("=" * 80)
    
    # Check worker container
    stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon | grep worker')
    worker = stdout.read().decode('utf-8', errors='replace')
    if not worker:
        print("   ⚠️  Worker not running")
        ssh.close()
        return
    
    container_id = worker.split()[0]
    print(f"\n   Worker container: {container_id}")
    
    # Check PATH for pentest user
    print("\n1. Checking PATH for pentest user...")
    stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "su pentest -c \'echo PATH=$PATH\'"')
    path_output = stdout.read().decode('utf-8', errors='replace')
    print(f"   PATH: {path_output}")
    
    # Check if node is accessible
    print("\n2. Checking node accessibility...")
    stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "su pentest -c \'which node || echo NOT_FOUND\'"')
    which_output = stdout.read().decode('utf-8', errors='replace')
    print(f"   which node: {which_output}")
    
    # The issue: Claude Code SDK spawns 'node' but it's not in PATH for pentest user
    # Solution: Set NODE environment variable or ensure PATH includes /usr/local/bin
    
    # Update startup script to export PATH and NODE
    print("\n3. Updating startup script...")
    sftp = ssh.open_sftp()
    
    startup_script = """#!/bin/sh
set -e
export PATH="/usr/bin:/usr/local/bin:/bin:/usr/sbin:/sbin:$PATH"
export NODE="/usr/bin/node"
mkdir -p /usr/local/bin
ln -sf /usr/bin/node /usr/local/bin/node 2>/dev/null || true
# Also create symlink in /bin for maximum compatibility
ln -sf /usr/bin/node /bin/node 2>/dev/null || true
exec node dist/temporal/worker.js
"""
    
    with sftp.open('/opt/xaker/shannon/start-worker.sh', 'w') as f:
        f.write(startup_script.encode('utf-8'))
    
    sftp.close()
    ssh.exec_command('chmod +x /opt/xaker/shannon/start-worker.sh')
    
    # Also update docker-compose.yml to set NODE env var
    print("\n4. Updating docker-compose.yml to set NODE env var...")
    sftp = ssh.open_sftp()
    with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'r') as f:
        compose = f.read().decode('utf-8')
    
    # Add NODE env var if not present
    if 'NODE=' not in compose or 'NODE=/usr/bin/node' not in compose:
        compose_lines = compose.split('\n')
        for i, line in enumerate(compose_lines):
            if 'environment:' in line and 'worker:' in '\n'.join(compose_lines[max(0, i-10):i]):
                # Add NODE after TEMPORAL_ADDRESS
                for j in range(i+1, min(i+20, len(compose_lines))):
                    if 'TEMPORAL_ADDRESS' in compose_lines[j]:
                        compose_lines.insert(j+1, '      - NODE=/usr/bin/node')
                        print(f"   ✅ Added NODE env var at line {j+2}")
                        break
                break
        
        compose = '\n'.join(compose_lines)
        with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'w') as f:
            f.write(compose.encode('utf-8'))
    
    sftp.close()
    
    # Restart worker
    print("\n5. Restarting worker...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose stop worker && docker-compose rm -f worker && docker-compose up -d worker')
    restart_output = stdout.read().decode('utf-8', errors='replace')
    print(restart_output)
    
    import time
    time.sleep(5)
    
    # Verify
    print("\n6. Verifying fix...")
    stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon | grep worker')
    worker = stdout.read().decode('utf-8', errors='replace')
    if worker:
        container_id = worker.split()[0]
        stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "su pentest -c \'echo PATH=$PATH && echo NODE=$NODE && which node && node --version\'"')
        verify = stdout.read().decode('utf-8', errors='replace')
        print(verify)
        
        if 'v22' in verify:
            print("\n   ✅ Node is accessible!")
            
            # Restart backend
            print("\n7. Restarting backend...")
            stdin, stdout, stderr = ssh.exec_command('pm2 restart xaker-backend')
            print(stdout.read().decode('utf-8', errors='replace'))
            
            print("\n✅ SUCCESS! Node spawn issue should be fixed")
            print("Try a new pentest now!")
        else:
            print("\n   ⚠️  Node still not accessible")
    
    ssh.close()
    
    print("\n" + "=" * 80)
    print("FIX COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    import time
    check_and_fix()

