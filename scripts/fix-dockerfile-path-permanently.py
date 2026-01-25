#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix Dockerfile PATH permanently"""

import paramiko
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def fix_dockerfile():
    """Fix Dockerfile PATH"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("FIXING DOCKERFILE PATH PERMANENTLY")
    print("=" * 80)
    
    sftp = ssh.open_sftp()
    
    # Read Dockerfile
    with sftp.open('/opt/xaker/shannon/Dockerfile', 'r') as f:
        dockerfile = f.read().decode('utf-8')
    
    dockerfile_lines = dockerfile.split('\n')
    
    # Find USER pentest line
    user_line_idx = -1
    for i, line in enumerate(dockerfile_lines):
        if 'USER pentest' in line:
            user_line_idx = i
            break
    
    if user_line_idx == -1:
        print("   ⚠️  USER pentest line not found")
        ssh.close()
        return
    
    print(f"\n   Found USER pentest at line {user_line_idx+1}")
    
    # Check if PATH is set before USER
    path_set_before = False
    for i in range(max(0, user_line_idx-10), user_line_idx):
        if 'ENV PATH' in dockerfile_lines[i]:
            path_set_before = True
            print(f"   PATH already set at line {i+1}: {dockerfile_lines[i]}")
            break
    
    if not path_set_before:
        # Insert PATH before USER
        dockerfile_lines.insert(user_line_idx, 'ENV PATH="/usr/bin:/usr/local/bin:/bin:/usr/sbin:/sbin:$PATH"')
        print(f"   ✅ Added PATH before USER at line {user_line_idx+1}")
    
    # Also ensure PATH is set after USER (for shell sessions)
    # Check if there's a shell profile or we need to add it
    # Actually, ENV should work, but let's also add it to startup script
    
    dockerfile = '\n'.join(dockerfile_lines)
    
    # Write back
    with sftp.open('/opt/xaker/shannon/Dockerfile', 'w') as f:
        f.write(dockerfile.encode('utf-8'))
    
    sftp.close()
    
    # Update startup script to ensure PATH is set
    print("\n2. Updating startup script...")
    sftp = ssh.open_sftp()
    
    startup_script = """#!/bin/sh
set -e
# Set PATH explicitly
export PATH="/usr/bin:/usr/local/bin:/bin:/usr/sbin:/sbin"
export NODE="/usr/bin/node"
# Create symlinks
mkdir -p /usr/local/bin /bin
ln -sf /usr/bin/node /usr/local/bin/node 2>/dev/null || true
ln -sf /usr/bin/node /bin/node 2>/dev/null || true
# Verify
which node >/dev/null 2>&1 || echo "WARNING: node not in PATH"
# Start worker
exec node dist/temporal/worker.js
"""
    
    with sftp.open('/opt/xaker/shannon/start-worker.sh', 'w') as f:
        f.write(startup_script.encode('utf-8'))
    
    sftp.close()
    ssh.exec_command('chmod +x /opt/xaker/shannon/start-worker.sh')
    
    # Rebuild
    print("\n3. Rebuilding worker image (this will take 2-3 minutes)...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && timeout 300 docker-compose build --no-cache worker 2>&1')
    
    import time
    start_time = time.time()
    output = ""
    while time.time() - start_time < 240:
        chunk = stdout.read(1024).decode('utf-8', errors='replace')
        if chunk:
            output += chunk
            if len(output) > 500:
                print(output[-500:], end='', flush=True)
                output = output[-500:]
        else:
            time.sleep(5)
            if stdout.channel.exit_status_ready():
                break
    
    remaining = stdout.read(50000).decode('utf-8', errors='replace')
    print(remaining[-1000:])
    
    if 'Successfully' in output or 'Successfully' in remaining:
        print("\n   ✅ Docker build successful!")
        
        # Restart worker
        print("\n4. Restarting worker...")
        stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose stop worker && docker-compose rm -f worker && docker-compose up -d worker')
        restart_output = stdout.read().decode('utf-8', errors='replace')
        print(restart_output)
        
        time.sleep(5)
        
        # Verify
        print("\n5. Verifying fix...")
        stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon | grep worker')
        worker = stdout.read().decode('utf-8', errors='replace')
        if worker:
            container_id = worker.split()[0]
            stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "su pentest -c \'echo PATH=$PATH && which node && node --version\'"')
            verify = stdout.read().decode('utf-8', errors='replace')
            print(verify)
            
            if 'v22' in verify and 'node' in verify.lower():
                print("\n   ✅ Node is accessible for pentest user!")
                
                # Restart backend
                print("\n6. Restarting backend...")
                stdin, stdout, stderr = ssh.exec_command('pm2 restart xaker-backend')
                print(stdout.read().decode('utf-8', errors='replace'))
                
                print("\n✅ SUCCESS! PATH fixed permanently")
                print("Try a new pentest now!")
            else:
                print("\n   ⚠️  Node still not accessible")
                print("   Checking what's wrong...")
                stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "ls -la /usr/bin/node /usr/local/bin/node /bin/node 2>&1"')
                print(stdout.read().decode('utf-8', errors='replace'))
        else:
            print("   ⚠️  Worker not running")
    else:
        print("   ⚠️  Build failed or timed out")
    
    ssh.close()
    
    print("\n" + "=" * 80)
    print("FIX COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    import time
    fix_dockerfile()

