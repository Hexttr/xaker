#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check build status and verify"""

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

def check_status():
    """Check build status"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("CHECKING BUILD STATUS")
    print("=" * 80)
    
    # Check TypeScript build
    print("\n1. Checking TypeScript build...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && npm run build 2>&1 | tail -5')
    build_output = stdout.read().decode('utf-8', errors='replace')
    if 'error' not in build_output.lower():
        print("   ✅ TypeScript build successful!")
    else:
        print(f"   ⚠️  TypeScript build has errors: {build_output[-200:]}")
    
    # Check Docker images
    print("\n2. Checking Docker images...")
    stdin, stdout, stderr = ssh.exec_command('docker images | grep shannon')
    images = stdout.read().decode('utf-8', errors='replace')
    print(images)
    
    # Check services
    print("\n3. Checking services...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose ps')
    services = stdout.read().decode('utf-8', errors='replace')
    print(services)
    
    # Check worker
    print("\n4. Checking worker...")
    stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon | grep worker')
    worker = stdout.read().decode('utf-8', errors='replace')
    if worker:
        container_id = worker.split()[0]
        print(f"   Worker container: {container_id}")
        
        stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "ls -la /usr/local/bin/node && which node && /usr/local/bin/node --version && printenv NODE"')
        verify = stdout.read().decode('utf-8', errors='replace')
        print(verify)
        
        if '/usr/local/bin/node' in verify:
            print("\n   ✅ Node symlink is working!")
    else:
        print("   ⚠️  Worker container not running")
    
    # Restart backend
    print("\n5. Restarting backend...")
    stdin, stdout, stderr = ssh.exec_command('pm2 restart xaker-backend')
    print(stdout.read().decode('utf-8', errors='replace'))
    
    ssh.close()
    
    print("\n" + "=" * 80)
    print("STATUS CHECK COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    check_status()

