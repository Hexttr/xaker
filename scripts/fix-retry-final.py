#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix retry policies with minutes/seconds"""

import paramiko
import sys
import re

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def fix_retry_final():
    """Fix retry policies"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("FIXING RETRY POLICIES FINAL")
    print("=" * 80)
    
    file_path = '/opt/xaker/shannon/src/temporal/workflows.ts'
    
    # Read file
    sftp = ssh.open_sftp()
    with sftp.open(file_path, 'r') as f:
        content = f.read().decode('utf-8')
    
    # Fix all string durations to Duration.from()
    # '5 minutes' -> Duration.from({ minutes: 5 })
    content = re.sub(
        r"initialInterval:\s*['\"](\d+)\s+minutes?['\"]",
        r'initialInterval: Duration.from({ minutes: \1 })',
        content
    )
    content = re.sub(
        r"maximumInterval:\s*['\"](\d+)\s+minutes?['\"]",
        r'maximumInterval: Duration.from({ minutes: \1 })',
        content
    )
    content = re.sub(
        r"initialInterval:\s*['\"](\d+)\s+seconds?['\"]",
        r'initialInterval: Duration.from({ seconds: \1 })',
        content
    )
    content = re.sub(
        r"maximumInterval:\s*['\"](\d+)\s+seconds?['\"]",
        r'maximumInterval: Duration.from({ seconds: \1 })',
        content
    )
    
    # Ensure Duration is imported
    lines = content.split('\n')
    for i, line in enumerate(lines[:30]):
        if 'from "@temporalio' in line:
            if 'Duration' not in line:
                lines[i] = line.replace('}', ', Duration }')
            break
    
    content = '\n'.join(lines)
    
    # Write back
    with sftp.open(file_path, 'w') as f:
        f.write(content.encode('utf-8'))
    
    sftp.close()
    
    # Rebuild
    print("\nRebuilding...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && npm run build 2>&1 | tail -5')
    build_output = stdout.read().decode('utf-8', errors='replace')
    print(build_output[-300:])
    
    if 'error' not in build_output.lower():
        print("✅ Build successful!")
        
        # Build and start
        print("\nBuilding and starting worker...")
        stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose build worker 2>&1 | tail -5')
        print(stdout.read().decode('utf-8', errors='replace')[-300:])
        
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
    print("FIX COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    import time
    fix_retry_final()

