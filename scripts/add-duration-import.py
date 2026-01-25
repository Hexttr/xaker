#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Add Duration import"""

import paramiko
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def add_import():
    """Add Duration import"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("ADDING DURATION IMPORT")
    print("=" * 80)
    
    file_path = '/opt/xaker/shannon/src/temporal/workflows.ts'
    
    sftp = ssh.open_sftp()
    with sftp.open(file_path, 'r') as f:
        content = f.read().decode('utf-8')
    
    lines = content.split('\n')
    
    # Find import line and add Duration
    for i, line in enumerate(lines[:30]):
        if 'from "@temporalio' in line:
            print(f"   Found import at line {i+1}: {line}")
            if 'Duration' not in line:
                lines[i] = line.replace('}', ', Duration }')
                print(f"   Added Duration: {lines[i]}")
            else:
                print("   Duration already imported")
            break
    
    with sftp.open(file_path, 'w') as f:
        f.write('\n'.join(lines).encode('utf-8'))
    
    sftp.close()
    
    # Rebuild
    print("\nRebuilding...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && npm run build 2>&1 | tail -3')
    build_output = stdout.read().decode('utf-8', errors='replace')
    print(build_output[-200:])
    
    if 'error' not in build_output.lower():
        print("✅ Build successful!")
        
        # Build Docker
        print("\nBuilding Docker image...")
        stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose build worker 2>&1 | tail -3')
        print(stdout.read().decode('utf-8', errors='replace')[-200:])
        
        # Start
        stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose up -d worker')
        print(stdout.read().decode('utf-8', errors='replace'))
        
        import time
        time.sleep(5)
        
        # Verify
        stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon | grep worker')
        worker = stdout.read().decode('utf-8', errors='replace')
        if worker:
            container_id = worker.split()[0]
            stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "ls -la /usr/local/bin/node && which node && printenv NODE"')
            print(stdout.read().decode('utf-8', errors='replace'))
    else:
        print("⚠️  Build has errors")
    
    ssh.close()
    
    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    import time
    add_import()

