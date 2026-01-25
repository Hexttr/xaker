#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verify and rebuild if needed"""

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

def verify_and_rebuild():
    """Verify and rebuild"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("VERIFYING AND REBUILDING")
    print("=" * 80)
    
    # Check Dockerfile
    print("\n1. Checking Dockerfile...")
    stdin, stdout, stderr = ssh.exec_command('grep -A 2 "USER pentest" /opt/xaker/shannon/Dockerfile | head -5')
    dockerfile_check = stdout.read().decode('utf-8', errors='replace')
    print(dockerfile_check)
    
    stdin, stdout, stderr = ssh.exec_command('grep "ENV PATH=" /opt/xaker/shannon/Dockerfile | tail -1')
    path_check = stdout.read().decode('utf-8', errors='replace')
    print(f"PATH: {path_check}")
    
    # Stop and remove
    print("\n2. Stopping and removing worker...")
    ssh.exec_command('cd /opt/xaker/shannon && docker-compose stop worker')
    time.sleep(2)
    ssh.exec_command('cd /opt/xaker/shannon && docker-compose rm -f worker')
    time.sleep(2)
    
    # Rebuild with no cache
    print("\n3. Rebuilding worker (this will take 2-3 minutes)...")
    print("   Starting build...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && timeout 300 docker-compose build --no-cache worker 2>&1')
    
    # Monitor build
    output = ""
    start_time = time.time()
    while time.time() - start_time < 180:  # 3 minutes max
        chunk = stdout.read(1024).decode('utf-8', errors='replace')
        if chunk:
            output += chunk
            # Print last 200 chars
            if len(output) > 200:
                print(output[-200:], end='', flush=True)
                output = output[-200:]
        else:
            time.sleep(5)
            if stdout.channel.exit_status_ready():
                break
    
    remaining = stdout.read(50000).decode('utf-8', errors='replace')
    print(remaining[-1000:])
    
    if 'Successfully' in output or 'Successfully' in remaining:
        print("\n   ✅ Build successful")
    else:
        print("\n   ⚠️  Build may not be complete")
    
    # Start
    print("\n4. Starting worker...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose up -d worker')
    print(stdout.read().decode('utf-8', errors='replace'))
    
    time.sleep(5)
    
    # Verify
    print("\n5. Verifying fix...")
    stdin, stdout, stderr = ssh.exec_command('docker exec shannon_worker_1 sh -c "ls -la /usr/local/bin/node && which node && /usr/local/bin/node --version && printenv PATH"')
    verify = stdout.read().decode('utf-8', errors='replace')
    print(verify)
    
    ssh.close()
    
    print("\n" + "=" * 80)
    print("VERIFICATION COMPLETE")
    print("=" * 80)
    if '/usr/local/bin/node' in verify and '->' in verify:
        print("✅ SUCCESS! Everything is configured correctly")
        print("Try a new pentest now")
    else:
        print("⚠️  Some checks failed")

if __name__ == "__main__":
    verify_and_rebuild()

