#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Final restart - check imports and restart everything"""

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

def final_restart():
    """Final restart"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("FINAL RESTART - CHECK IMPORTS AND RESTART ALL")
    print("=" * 80)
    
    # Check workflows.ts imports
    print("\n1. Checking workflows.ts imports...")
    sftp = ssh.open_sftp()
    with sftp.open('/opt/xaker/shannon/src/temporal/workflows.ts', 'r') as f:
        workflows = f.read().decode('utf-8')
    
    # Show first 30 lines
    workflows_lines = workflows.split('\n')
    print("   First 30 lines:")
    for i, line in enumerate(workflows_lines[:30]):
        if 'import' in line or 'Duration' in line:
            print(f"   Line {i+1}: {line}")
    
    # Check if Duration is imported
    if 'Duration' not in '\n'.join(workflows_lines[:30]):
        print("\n2. Adding Duration import...")
        # Find first import line
        for i, line in enumerate(workflows_lines[:30]):
            if 'import' in line and 'from' in line:
                # Add Duration import before this line
                workflows_lines.insert(i, "import { Duration } from '@temporalio/common';")
                print(f"   Added Duration import at line {i+1}")
                break
        
        with sftp.open('/opt/xaker/shannon/src/temporal/workflows.ts', 'w') as f:
            f.write('\n'.join(workflows_lines).encode('utf-8'))
    else:
        print("\n2. Duration already imported")
    
    sftp.close()
    
    # Rebuild
    print("\n3. Rebuilding TypeScript...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && npm run build 2>&1 | tail -3')
    build_output = stdout.read().decode('utf-8', errors='replace')
    print(build_output[-200:])
    
    if 'error' not in build_output.lower():
        print("✅ Build successful!")
        
        # Build Docker
        print("\n4. Building Docker image...")
        stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose build worker 2>&1 | tail -5')
        time.sleep(60)
        docker_build = stdout.read(50000).decode('utf-8', errors='replace')
        if 'Successfully' in docker_build:
            print("✅ Docker build successful")
        print(docker_build[-500:])
    else:
        print("⚠️  Build has errors - will try to use existing setup")
    
    # Restart everything
    print("\n5. Restarting all services...")
    ssh.exec_command('cd /opt/xaker/shannon && docker-compose down')
    time.sleep(2)
    
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose up -d')
    print(stdout.read().decode('utf-8', errors='replace'))
    
    time.sleep(5)
    
    # Create symlink in worker
    print("\n6. Ensuring node symlink in worker...")
    stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon | grep worker')
    worker = stdout.read().decode('utf-8', errors='replace')
    if worker:
        container_id = worker.split()[0]
        stdin, stdout, stderr = ssh.exec_command(f'docker exec -u root {container_id} sh -c "mkdir -p /usr/local/bin && ln -sf /usr/bin/node /usr/local/bin/node && ls -la /usr/local/bin/node"')
        print(stdout.read().decode('utf-8', errors='replace'))
        
        stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "which node && printenv NODE"')
        print(stdout.read().decode('utf-8', errors='replace'))
    
    # Restart backend
    print("\n7. Restarting backend...")
    stdin, stdout, stderr = ssh.exec_command('pm2 restart xaker-backend')
    print(stdout.read().decode('utf-8', errors='replace'))
    
    ssh.close()
    
    print("\n" + "=" * 80)
    print("FINAL RESTART COMPLETE")
    print("=" * 80)
    print("All services restarted. Try a new pentest now.")

if __name__ == "__main__":
    final_restart()

