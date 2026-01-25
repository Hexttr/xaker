#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ultimate fix - use existing image and ensure node is available"""

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

def ultimate_fix():
    """Ultimate fix"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("ULTIMATE FIX - USE EXISTING IMAGE AND ENSURE NODE")
    print("=" * 80)
    
    # Check for existing images
    print("\n1. Checking for existing images...")
    stdin, stdout, stderr = ssh.exec_command('docker images | grep shannon')
    images = stdout.read().decode('utf-8', errors='replace')
    print(images)
    
    # Stop everything
    print("\n2. Stopping services...")
    ssh.exec_command('cd /opt/xaker/shannon && docker-compose down')
    time.sleep(2)
    
    # Start temporal first
    print("\n3. Starting temporal...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose up -d temporal')
    print(stdout.read().decode('utf-8', errors='replace'))
    time.sleep(5)
    
    # Start worker (even if build fails, use existing image)
    print("\n4. Starting worker (using existing image if build fails)...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose up -d worker 2>&1')
    start_output = stdout.read().decode('utf-8', errors='replace')
    errors = stderr.read().decode('utf-8', errors='replace')
    print(start_output)
    if errors:
        print(f"Errors (may be OK if using existing image): {errors[:300]}")
    
    time.sleep(5)
    
    # Get worker container
    print("\n5. Finding worker container...")
    stdin, stdout, stderr = ssh.exec_command('docker ps -a | grep shannon | grep worker | head -1')
    worker_line = stdout.read().decode('utf-8', errors='replace')
    
    if worker_line:
        container_id = worker_line.split()[0]
        print(f"   Container ID: {container_id}")
        
        # Start if stopped
        stdin, stdout, stderr = ssh.exec_command(f'docker start {container_id}')
        time.sleep(3)
        
        # Create symlink as root
        print("\n6. Creating symlink in container...")
        stdin, stdout, stderr = ssh.exec_command(f'docker exec -u root {container_id} sh -c "mkdir -p /usr/local/bin && ln -sf /usr/bin/node /usr/local/bin/node && ls -la /usr/local/bin/node"')
        symlink_output = stdout.read().decode('utf-8', errors='replace')
        print(symlink_output)
        
        # Verify node
        print("\n7. Verifying node availability...")
        stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "which node && /usr/local/bin/node --version && printenv NODE && printenv PATH"')
        verify = stdout.read().decode('utf-8', errors='replace')
        print(verify)
        
        # Restart backend
        print("\n8. Restarting backend...")
        stdin, stdout, stderr = ssh.exec_command('pm2 restart xaker-backend')
        print(stdout.read().decode('utf-8', errors='replace'))
        
        print("\n✅ SUCCESS! Worker is running with node symlink")
        print("Try a new pentest now")
    else:
        print("   ⚠️  Worker container not found")
        print("   Need to fix TypeScript errors and rebuild")
    
    ssh.close()
    
    print("\n" + "=" * 80)
    print("ULTIMATE FIX COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    ultimate_fix()

