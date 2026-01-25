#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Final fix: Set NODE env var and ensure PATH"""

import paramiko
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def final_fix():
    """Final fix"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("FINAL FIX: NODE ENV VAR AND PATH")
    print("=" * 80)
    
    # Update startup script to export NODE and PATH
    print("\n1. Updating startup script...")
    sftp = ssh.open_sftp()
    
    startup_script = """#!/bin/sh
set -e
# Set PATH explicitly - this is critical
export PATH="/usr/bin:/usr/local/bin:/bin:/usr/sbin:/sbin"
# Set NODE environment variable - some libraries use this
export NODE="/usr/bin/node"
# Create symlinks in multiple locations
mkdir -p /usr/local/bin /bin
ln -sf /usr/bin/node /usr/local/bin/node 2>/dev/null || true
ln -sf /usr/bin/node /bin/node 2>/dev/null || true
# Verify node is accessible
if ! which node >/dev/null 2>&1; then
    echo "ERROR: node not found in PATH: $PATH"
    exit 1
fi
# Start worker
exec node dist/temporal/worker.js
"""
    
    with sftp.open('/opt/xaker/shannon/start-worker.sh', 'w') as f:
        f.write(startup_script.encode('utf-8'))
    
    sftp.close()
    ssh.exec_command('chmod +x /opt/xaker/shannon/start-worker.sh')
    
    # Update docker-compose.yml to ensure NODE is set
    print("\n2. Updating docker-compose.yml...")
    sftp = ssh.open_sftp()
    with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'r') as f:
        compose = f.read().decode('utf-8')
    
    compose_lines = compose.split('\n')
    node_env_set = False
    for i, line in enumerate(compose_lines):
        if 'NODE=' in line and '/usr/bin/node' in line:
            node_env_set = True
            break
    
    if not node_env_set:
        # Find environment section and add NODE
        for i, line in enumerate(compose_lines):
            if 'environment:' in line and 'worker:' in '\n'.join(compose_lines[max(0, i-10):i]):
                # Add NODE after TEMPORAL_ADDRESS
                for j in range(i+1, min(i+20, len(compose_lines))):
                    if 'TEMPORAL_ADDRESS' in compose_lines[j]:
                        compose_lines.insert(j+1, '      - NODE=/usr/bin/node')
                        compose_lines.insert(j+2, '      - PATH=/usr/bin:/usr/local/bin:/bin:/usr/sbin:/sbin')
                        print(f"   ✅ Added NODE and PATH env vars at line {j+2}")
                        break
                break
    
    compose = '\n'.join(compose_lines)
    with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'w') as f:
        f.write(compose.encode('utf-8'))
    
    sftp.close()
    
    # Update Dockerfile to set PATH before USER
    print("\n3. Updating Dockerfile...")
    sftp = ssh.open_sftp()
    with sftp.open('/opt/xaker/shannon/Dockerfile', 'r') as f:
        dockerfile = f.read().decode('utf-8')
    
    dockerfile_lines = dockerfile.split('\n')
    path_set = False
    for i, line in enumerate(dockerfile_lines):
        if 'USER pentest' in line:
            # Check if PATH is set before
            for j in range(max(0, i-5), i):
                if 'ENV PATH' in dockerfile_lines[j]:
                    path_set = True
                    break
            if not path_set:
                dockerfile_lines.insert(i, 'ENV PATH="/usr/bin:/usr/local/bin:/bin:/usr/sbin:/sbin:$PATH"')
                dockerfile_lines.insert(i+1, 'ENV NODE="/usr/bin/node"')
                print(f"   ✅ Added PATH and NODE before USER at line {i+1}")
            break
    
    dockerfile = '\n'.join(dockerfile_lines)
    with sftp.open('/opt/xaker/shannon/Dockerfile', 'w') as f:
        f.write(dockerfile.encode('utf-8'))
    
    sftp.close()
    
    # Restart worker (no rebuild needed if just env vars changed)
    print("\n4. Restarting worker...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose stop worker && docker-compose rm -f worker && docker-compose up -d worker')
    restart_output = stdout.read().decode('utf-8', errors='replace')
    print(restart_output)
    
    import time
    time.sleep(5)
    
    # Verify
    print("\n5. Verifying fix...")
    stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon | grep worker')
    worker = stdout.read().decode('utf-8', errors='replace')
    if worker:
        container_id = worker.split()[0]
        stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "su pentest -c \'echo PATH=$PATH && echo NODE=$NODE && which node && node --version\'"')
        verify = stdout.read().decode('utf-8', errors='replace')
        print(verify)
        
        if 'v22' in verify and 'node' in verify.lower():
            print("\n   ✅ Node is accessible!")
            
            # Restart backend
            print("\n6. Restarting backend...")
            stdin, stdout, stderr = ssh.exec_command('pm2 restart xaker-backend')
            print(stdout.read().decode('utf-8', errors='replace'))
            
            print("\n✅ SUCCESS! NODE env var and PATH set")
            print("Try a new pentest now!")
        else:
            print("\n   ⚠️  Node still not accessible")
            print("   May need to rebuild image")
    
    ssh.close()
    
    print("\n" + "=" * 80)
    print("FIX COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    import time
    final_fix()

