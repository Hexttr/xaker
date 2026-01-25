#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix all Duration imports"""

import paramiko
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def fix_all_imports():
    """Fix all Duration imports"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("FIXING ALL DURATION IMPORTS")
    print("=" * 80)
    
    sftp = ssh.open_sftp()
    
    # Fix client.ts
    print("\n1. Fixing client.ts...")
    with sftp.open('/opt/xaker/shannon/src/temporal/client.ts', 'r') as f:
        client_content = f.read().decode('utf-8')
    
    client_lines = client_content.split('\n')
    
    # Find import and add Duration
    for i, line in enumerate(client_lines[:30]):
        if 'from "@temporalio/client"' in line:
            if 'Duration' not in line:
                client_lines[i] = line.replace('}', ', Duration }')
                print(f"   Added Duration to client.ts import at line {i+1}")
            break
    
    # Fix line 207 - Duration.from({ hours: 3 })
    for i, line in enumerate(client_lines):
        if i == 206:  # Line 207
            if 'Duration.from({ milliseconds:' in line and 'h)' in line:
                client_lines[i] = line.replace('Duration.from({ milliseconds:', 'Duration.from({ hours:').replace('h)', '})')
                print(f"   Fixed client.ts line 207")
    
    with sftp.open('/opt/xaker/shannon/src/temporal/client.ts', 'w') as f:
        f.write('\n'.join(client_lines).encode('utf-8'))
    
    # Fix workflows.ts
    print("\n2. Fixing workflows.ts...")
    with sftp.open('/opt/xaker/shannon/src/temporal/workflows.ts', 'r') as f:
        workflows_content = f.read().decode('utf-8')
    
    workflows_lines = workflows_content.split('\n')
    
    # Find import and add Duration
    for i, line in enumerate(workflows_lines[:30]):
        if 'from "@temporalio' in line:
            if 'Duration' not in line:
                workflows_lines[i] = line.replace('}', ', Duration }')
                print(f"   Added Duration to workflows.ts import at line {i+1}")
            break
    
    with sftp.open('/opt/xaker/shannon/src/temporal/workflows.ts', 'w') as f:
        f.write('\n'.join(workflows_lines).encode('utf-8'))
    
    sftp.close()
    
    # Rebuild
    print("\n3. Rebuilding...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && npm run build 2>&1 | tail -3')
    build_output = stdout.read().decode('utf-8', errors='replace')
    print(build_output[-200:])
    
    if 'error' not in build_output.lower():
        print("✅ Build successful!")
        
        # Build Docker
        print("\n4. Building Docker image...")
        stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose build worker 2>&1 | tail -5')
        docker_build = stdout.read().decode('utf-8', errors='replace')
        print(docker_build[-300:])
        
        # Start
        print("\n5. Starting services...")
        stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose up -d')
        start_output = stdout.read().decode('utf-8', errors='replace')
        print(start_output)
        
        time.sleep(5)
        
        # Verify
        print("\n6. Verifying worker...")
        stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon | grep worker')
        worker = stdout.read().decode('utf-8', errors='replace')
        if worker:
            container_id = worker.split()[0]
            stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "ls -la /usr/local/bin/node && which node && printenv NODE"')
            print(stdout.read().decode('utf-8', errors='replace'))
    else:
        print("⚠️  Build still has errors")
    
    ssh.close()
    
    print("\n" + "=" * 80)
    print("FIX COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    import time
    fix_all_imports()

