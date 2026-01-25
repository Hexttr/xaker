#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Full restart - remove old images and restart everything"""

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

def full_restart():
    """Full restart"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("FULL RESTART - REMOVE OLD IMAGES AND RESTART")
    print("=" * 80)
    
    # Check current images
    print("\n1. Checking current images...")
    stdin, stdout, stderr = ssh.exec_command('docker images | grep shannon')
    images = stdout.read().decode('utf-8', errors='replace')
    print(images)
    
    # Stop everything
    print("\n2. Stopping all services...")
    ssh.exec_command('cd /opt/xaker/shannon && docker-compose down')
    time.sleep(3)
    
    # Remove old containers
    print("\n3. Removing old containers...")
    ssh.exec_command('docker rm -f shannon_worker_1 shannon_temporal_1 2>&1 || true')
    time.sleep(2)
    
    # Remove old images
    print("\n4. Removing old images...")
    stdin, stdout, stderr = ssh.exec_command('docker images | grep shannon | awk "{print $3}" | xargs -r docker rmi -f 2>&1 || true')
    removed = stdout.read().decode('utf-8', errors='replace')
    print(removed[:500])
    
    # Rebuild with no cache
    print("\n5. Rebuilding worker image (this will take 3-4 minutes)...")
    print("   Starting build...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && timeout 300 docker-compose build --no-cache worker 2>&1')
    
    # Wait and monitor
    start_time = time.time()
    output = ""
    while time.time() - start_time < 240:  # 4 minutes
        chunk = stdout.read(1024).decode('utf-8', errors='replace')
        if chunk:
            output += chunk
            if len(output) > 300:
                print(output[-300:], end='', flush=True)
                output = output[-300:]
        else:
            time.sleep(5)
            if stdout.channel.exit_status_ready():
                break
    
    remaining = stdout.read(50000).decode('utf-8', errors='replace')
    print(remaining[-1000:])
    
    if 'Successfully' in output or 'Successfully' in remaining:
        print("\n   ✅ Build successful")
    else:
        print("\n   ⚠️  Check build output above")
    
    # Start services
    print("\n6. Starting all services...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose up -d')
    start_output = stdout.read().decode('utf-8', errors='replace')
    print(start_output)
    
    time.sleep(5)
    
    # Verify worker
    print("\n7. Verifying worker...")
    stdin, stdout, stderr = ssh.exec_command('docker exec shannon_worker_1 sh -c "ls -la /usr/local/bin/node && which node && /usr/local/bin/node --version && printenv PATH"')
    verify = stdout.read().decode('utf-8', errors='replace')
    print(verify)
    
    # Check worker logs
    print("\n8. Checking worker logs (last 20 lines)...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker logs shannon_worker_1 --tail=20 2>&1')
    logs = stdout.read().decode('utf-8', errors='replace')
    print(logs[-1000:])
    
    # Restart backend
    print("\n9. Restarting backend...")
    stdin, stdout, stderr = ssh.exec_command('pm2 restart xaker-backend')
    restart_backend = stdout.read().decode('utf-8', errors='replace')
    print(restart_backend)
    
    time.sleep(3)
    
    # Check backend status
    print("\n10. Checking backend status...")
    stdin, stdout, stderr = ssh.exec_command('pm2 status xaker-backend')
    backend_status = stdout.read().decode('utf-8', errors='replace')
    print(backend_status)
    
    ssh.close()
    
    print("\n" + "=" * 80)
    print("FULL RESTART COMPLETE")
    print("=" * 80)
    if '/usr/local/bin/node' in verify and '->' in verify:
        print("✅ SUCCESS! Everything restarted")
        print("Try a new pentest now")
    else:
        print("⚠️  Some checks failed, but services restarted")

if __name__ == "__main__":
    full_restart()

