#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Final fix - TypeScript errors and use existing image if available"""

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

def final_fix():
    """Final fix"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("FINAL FIX - TYPESCRIPT AND DOCKER")
    print("=" * 80)
    
    # Check for existing image
    print("\n1. Checking for existing images...")
    stdin, stdout, stderr = ssh.exec_command('docker images | grep shannon')
    images = stdout.read().decode('utf-8', errors='replace')
    print(images)
    
    # Fix client.ts line 207
    print("\n2. Fixing client.ts line 207...")
    sftp = ssh.open_sftp()
    with sftp.open('/opt/xaker/shannon/src/temporal/client.ts', 'r') as f:
        content = f.read().decode('utf-8')
    
    # Fix the problematic line
    content = content.replace(
        'Duration.from({ milliseconds:  3h)',
        'Duration.from({ hours: 3 })'
    )
    content = content.replace(
        'Duration.from({ milliseconds: 3h)',
        'Duration.from({ hours: 3 })'
    )
    
    with sftp.open('/opt/xaker/shannon/src/temporal/client.ts', 'w') as f:
        f.write(content.encode('utf-8'))
    
    # Fix workflows.ts - find PRODUCTION_RETRY and TESTING_RETRY
    print("\n3. Fixing workflows.ts...")
    with sftp.open('/opt/xaker/shannon/src/temporal/workflows.ts', 'r') as f:
        workflows = f.read().decode('utf-8')
    
    # Find and fix PRODUCTION_RETRY and TESTING_RETRY
    workflows_lines = workflows.split('\n')
    for i, line in enumerate(workflows_lines):
        if 'PRODUCTION_RETRY' in line or 'TESTING_RETRY' in line:
            # Find the definition
            if '=' in line and 'initialInterval' in workflows_lines[i+1] if i+1 < len(workflows_lines) else False:
                # Fix the next few lines
                j = i + 1
                while j < len(workflows_lines) and j < i + 10:
                    if 'initialInterval:' in workflows_lines[j] and '"' in workflows_lines[j]:
                        # Replace string with Duration.from()
                        workflows_lines[j] = re.sub(
                            r'initialInterval:\s*["\'](\d+)\s*h["\']',
                            r'initialInterval: Duration.from({ hours: \1 })',
                            workflows_lines[j]
                        )
                    if 'maximumInterval:' in workflows_lines[j] and '"' in workflows_lines[j]:
                        workflows_lines[j] = re.sub(
                            r'maximumInterval:\s*["\'](\d+)\s*h["\']',
                            r'maximumInterval: Duration.from({ hours: \1 })',
                            workflows_lines[j]
                        )
                    if workflows_lines[j].strip() == '},' or workflows_lines[j].strip() == '};':
                        break
                    j += 1
    
    # Ensure Duration is imported
    if 'Duration' not in '\n'.join(workflows_lines[:30]):
        for i, line in enumerate(workflows_lines[:30]):
            if 'from "@temporalio' in line:
                if 'Duration' not in line:
                    workflows_lines[i] = line.replace('}', ', Duration }')
                break
    
    with sftp.open('/opt/xaker/shannon/src/temporal/workflows.ts', 'w') as f:
        f.write('\n'.join(workflows_lines).encode('utf-8'))
    
    sftp.close()
    
    # Rebuild
    print("\n4. Rebuilding TypeScript...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && npm run build 2>&1 | tail -15')
    build_output = stdout.read().decode('utf-8', errors='replace')
    print(build_output[-600:])
    
    if 'error' not in build_output.lower():
        print("   ✅ Build successful")
        
        # Build Docker image
        print("\n5. Building Docker image...")
        stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose build worker 2>&1 | tail -10')
        docker_build = stdout.read().decode('utf-8', errors='replace')
        print(docker_build[-500:])
        
        # Start
        print("\n6. Starting services...")
        stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose up -d')
        start_output = stdout.read().decode('utf-8', errors='replace')
        print(start_output)
        
        import time
        time.sleep(5)
        
        # Verify
        print("\n7. Verifying worker...")
        stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon | grep worker')
        worker = stdout.read().decode('utf-8', errors='replace')
        if worker:
            container_id = worker.split()[0]
            stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "ls -la /usr/local/bin/node && which node && printenv NODE"')
            verify = stdout.read().decode('utf-8', errors='replace')
            print(verify)
    else:
        print("   ⚠️  Build still has errors - check output above")
    
    ssh.close()
    
    print("\n" + "=" * 80)
    print("FINAL FIX COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    import time
    final_fix()

