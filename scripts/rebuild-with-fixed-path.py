#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rebuild Docker image with fixed PATH"""

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

def rebuild():
    """Rebuild with fixed PATH"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("REBUILDING DOCKER IMAGE WITH FIXED PATH")
    print("=" * 80)
    
    # Verify Dockerfile has PATH set
    print("\n1. Verifying Dockerfile...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && grep -A 2 -B 2 "USER pentest" Dockerfile')
    dockerfile_check = stdout.read().decode('utf-8', errors='replace')
    print(dockerfile_check)
    
    # Rebuild
    print("\n2. Rebuilding worker image (this will take 2-3 minutes)...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && timeout 300 docker-compose build --no-cache worker 2>&1')
    
    start_time = time.time()
    output = ""
    last_output = ""
    while time.time() - start_time < 300:
        chunk = stdout.read(1024).decode('utf-8', errors='replace')
        if chunk:
            output += chunk
            if len(output) > 500:
                # Show last 500 chars
                current_output = output[-500:]
                if current_output != last_output:
                    print(current_output, end='', flush=True)
                    last_output = current_output
                output = output[-500:]
        else:
            time.sleep(2)
            if stdout.channel.exit_status_ready():
                break
    
    remaining = stdout.read(100000).decode('utf-8', errors='replace')
    if remaining:
        print(remaining[-2000:])
    
    if 'Successfully' in output or 'Successfully' in remaining:
        print("\n\n   ✅ Docker build successful!")
        
        # Restart worker
        print("\n3. Restarting worker...")
        stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose stop worker && docker-compose rm -f worker && docker-compose up -d worker')
        restart_output = stdout.read().decode('utf-8', errors='replace')
        print(restart_output)
        
        time.sleep(5)
        
        # Verify
        print("\n4. Verifying fix...")
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
                print("\n5. Checking worker logs...")
                stdin, stdout, stderr = ssh.exec_command(f'docker logs {container_id} --tail=10 2>&1')
                logs = stdout.read().decode('utf-8', errors='replace')
                print(logs[-300:])
                
                # Restart backend
                print("\n6. Restarting backend...")
                stdin, stdout, stderr = ssh.exec_command('pm2 restart xaker-backend')
                print(stdout.read().decode('utf-8', errors='replace'))
                
                print("\n✅ SUCCESS! Docker image rebuilt with fixed PATH")
                print("Try a new pentest now!")
            else:
                print("\n   ⚠️  Node still not accessible")
                print("   Checking symlinks...")
                stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "ls -la /usr/bin/node /usr/local/bin/node /bin/node 2>&1"')
                print(stdout.read().decode('utf-8', errors='replace'))
        else:
            print("   ⚠️  Worker not running")
    else:
        print("\n   ⚠️  Build failed or timed out")
        print("   Check output above for errors")
    
    ssh.close()
    
    print("\n" + "=" * 80)
    print("REBUILD COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    rebuild()

