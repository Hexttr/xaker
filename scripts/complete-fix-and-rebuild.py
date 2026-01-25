#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Complete fix and rebuild"""

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

def complete_fix():
    """Complete fix and rebuild"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("COMPLETE FIX AND REBUILD")
    print("=" * 80)
    
    sftp = ssh.open_sftp()
    
    # 1. Update Dockerfile - ensure PATH is set before USER pentest
    print("\n1. Updating Dockerfile...")
    with sftp.open('/opt/xaker/shannon/Dockerfile', 'r') as f:
        dockerfile = f.read().decode('utf-8')
    
    dockerfile_lines = dockerfile.split('\n')
    
    # Find USER pentest line
    user_idx = -1
    for i, line in enumerate(dockerfile_lines):
        if 'USER pentest' in line:
            user_idx = i
            break
    
    if user_idx >= 0:
        # Check if PATH is already set before USER
        path_set = False
        for i in range(max(0, user_idx-5), user_idx):
            if 'ENV PATH' in dockerfile_lines[i]:
                path_set = True
                # Update it to ensure it's correct
                dockerfile_lines[i] = 'ENV PATH="/usr/bin:/usr/local/bin:/bin:/usr/sbin:/sbin:$PATH"'
                dockerfile_lines.insert(i+1, 'ENV NODE="/usr/bin/node"')
                print(f"   ✅ Updated PATH at line {i+1}")
                break
        
        if not path_set:
            # Insert PATH and NODE before USER
            dockerfile_lines.insert(user_idx, 'ENV PATH="/usr/bin:/usr/local/bin:/bin:/usr/sbin:/sbin:$PATH"')
            dockerfile_lines.insert(user_idx+1, 'ENV NODE="/usr/bin/node"')
            print(f"   ✅ Added PATH and NODE before USER at line {user_idx+1}")
    
    dockerfile = '\n'.join(dockerfile_lines)
    with sftp.open('/opt/xaker/shannon/Dockerfile', 'w') as f:
        f.write(dockerfile.encode('utf-8'))
    
    # 2. Update startup script
    print("\n2. Updating startup script...")
    startup_script = """#!/bin/sh
set -e
# Set PATH explicitly - critical for spawn to work
export PATH="/usr/bin:/usr/local/bin:/bin:/usr/sbin:/sbin"
export NODE="/usr/bin/node"
# Create symlinks in multiple locations for maximum compatibility
mkdir -p /usr/local/bin /bin
ln -sf /usr/bin/node /usr/local/bin/node 2>/dev/null || true
ln -sf /usr/bin/node /bin/node 2>/dev/null || true
# Verify node is accessible
if ! command -v node >/dev/null 2>&1; then
    echo "ERROR: node not found in PATH: $PATH"
    ls -la /usr/bin/node /usr/local/bin/node /bin/node 2>&1 || true
    exit 1
fi
# Start worker
exec node dist/temporal/worker.js
"""
    
    with sftp.open('/opt/xaker/shannon/start-worker.sh', 'w') as f:
        f.write(startup_script.encode('utf-8'))
    
    ssh.exec_command('chmod +x /opt/xaker/shannon/start-worker.sh')
    
    # 3. Update docker-compose.yml
    print("\n3. Updating docker-compose.yml...")
    with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'r') as f:
        compose = f.read().decode('utf-8')
    
    compose_lines = compose.split('\n')
    node_set = False
    path_set = False
    
    for i, line in enumerate(compose_lines):
        if 'environment:' in line and 'worker:' in '\n'.join(compose_lines[max(0, i-10):i]):
            # Find TEMPORAL_ADDRESS and add NODE and PATH after it
            for j in range(i+1, min(i+20, len(compose_lines))):
                if 'TEMPORAL_ADDRESS' in compose_lines[j]:
                    if not node_set:
                        compose_lines.insert(j+1, '      - NODE=/usr/bin/node')
                        compose_lines.insert(j+2, '      - PATH=/usr/bin:/usr/local/bin:/bin:/usr/sbin:/sbin')
                        node_set = True
                        path_set = True
                        print(f"   ✅ Added NODE and PATH env vars at line {j+2}")
                    break
            break
    
    compose = '\n'.join(compose_lines)
    with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'w') as f:
        f.write(compose.encode('utf-8'))
    
    sftp.close()
    
    # 4. Rebuild Docker image
    print("\n4. Rebuilding Docker image (this will take 2-3 minutes)...")
    print("   Please wait...")
    
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && timeout 300 docker-compose build --no-cache worker 2>&1')
    
    start_time = time.time()
    output = ""
    last_chunk_time = time.time()
    
    while time.time() - start_time < 300:
        chunk = stdout.read(1024).decode('utf-8', errors='replace')
        if chunk:
            output += chunk
            last_chunk_time = time.time()
            # Show progress every 10 seconds
            if time.time() - last_chunk_time > 10 or len(output) > 1000:
                if 'Step' in chunk or 'Successfully' in chunk or 'ERROR' in chunk:
                    print(chunk[-200:], end='', flush=True)
        else:
            time.sleep(2)
            if stdout.channel.exit_status_ready():
                break
    
    remaining = stdout.read(100000).decode('utf-8', errors='replace')
    if remaining:
        print(remaining[-2000:])
    
    if 'Successfully' in output or 'Successfully' in remaining:
        print("\n\n   ✅ Docker build successful!")
        
        # 5. Restart worker
        print("\n5. Restarting worker...")
        stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose stop worker && docker-compose rm -f worker && docker-compose up -d worker')
        restart_output = stdout.read().decode('utf-8', errors='replace')
        print(restart_output)
        
        time.sleep(5)
        
        # 6. Verify
        print("\n6. Verifying fix...")
        stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon | grep worker')
        worker = stdout.read().decode('utf-8', errors='replace')
        if worker:
            container_id = worker.split()[0]
            print(f"   Worker container: {container_id}")
            
            # Check PATH and NODE for pentest user
            stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "su pentest -c \'echo PATH=$PATH && echo NODE=$NODE && which node && node --version\'"')
            verify = stdout.read().decode('utf-8', errors='replace')
            print(f"\n   Verification:\n{verify}")
            
            if 'v22' in verify and ('node' in verify.lower() or '/usr/bin/node' in verify):
                print("\n   ✅ Node is accessible for pentest user!")
                
                # Check worker logs
                print("\n7. Checking worker logs...")
                stdin, stdout, stderr = ssh.exec_command(f'docker logs {container_id} --tail=15 2>&1')
                logs = stdout.read().decode('utf-8', errors='replace')
                print(logs[-500:])
                
                if 'Shannon worker started' in logs or 'RUNNING' in logs:
                    print("\n   ✅ Worker is running!")
                    
                    # Restart backend
                    print("\n8. Restarting backend...")
                    stdin, stdout, stderr = ssh.exec_command('pm2 restart xaker-backend')
                    backend_output = stdout.read().decode('utf-8', errors='replace')
                    print(backend_output[-300:])
                    
                    print("\n" + "=" * 80)
                    print("✅ SUCCESS! Everything is fixed and running")
                    print("=" * 80)
                    print("\nThe application is ready to conduct pentests!")
                    print("Try launching a new pentest at https://pentest.red/app")
                else:
                    print("\n   ⚠️  Worker may not be fully started yet")
            else:
                print("\n   ⚠️  Node still not accessible")
                print("   Checking symlinks...")
                stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "ls -la /usr/bin/node /usr/local/bin/node /bin/node 2>&1"')
                print(stdout.read().decode('utf-8', errors='replace'))
        else:
            print("   ⚠️  Worker not running")
            # Check logs
            stdin, stdout, stderr = ssh.exec_command('docker ps -a | grep shannon | grep worker | head -1')
            worker_line = stdout.read().decode('utf-8', errors='replace')
            if worker_line:
                container_id = worker_line.split()[0]
                stdin, stdout, stderr = ssh.exec_command(f'docker logs {container_id} --tail=20 2>&1')
                print(stdout.read().decode('utf-8', errors='replace'))
    else:
        print("\n   ⚠️  Build may have failed")
        print("   Check output above for errors")
    
    ssh.close()
    
    print("\n" + "=" * 80)
    print("COMPLETE FIX FINISHED")
    print("=" * 80)

if __name__ == "__main__":
    complete_fix()

