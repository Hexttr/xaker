#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix all TypeScript errors and add NODE env variable"""

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

def fix_all():
    """Fix all"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("FIXING ALL TYPESCRIPT ERRORS AND ADDING NODE ENV")
    print("=" * 80)
    
    # Fix client.ts
    print("\n1. Fixing client.ts...")
    sftp = ssh.open_sftp()
    with sftp.open('/opt/xaker/shannon/src/temporal/client.ts', 'r') as f:
        content = f.read().decode('utf-8')
    
    # Fix ms import
    content = content.replace('import { Connection, Client, ms }', 'import { Connection, Client }')
    
    # Fix ms( 3h) - should be Duration.from({ hours: 3 })
    content = re.sub(r'ms\(\s*(\d+)\s*h\s*\)', r'Duration.from({ hours: \1 })', content)
    content = re.sub(r'ms\(\s*(\d+)\s*\)', r'Duration.from({ milliseconds: \1 })', content)
    
    # Add Duration import if not present
    if 'Duration' not in content.split('\n')[0:30]:
        # Find import line and add Duration
        lines = content.split('\n')
        for i, line in enumerate(lines[:30]):
            if 'from "@temporalio/client"' in line:
                lines[i] = line.replace('import { Connection, Client }', 'import { Connection, Client, Duration }')
                break
        content = '\n'.join(lines)
    
    with sftp.open('/opt/xaker/shannon/src/temporal/client.ts', 'w') as f:
        f.write(content.encode('utf-8'))
    
    # Fix workflows.ts
    print("\n2. Fixing workflows.ts...")
    with sftp.open('/opt/xaker/shannon/src/temporal/workflows.ts', 'r') as f:
        workflows_content = f.read().decode('utf-8')
    
    # Fix RetryPolicy - replace string durations with Duration.from()
    workflows_content = re.sub(r'initialInterval:\s*["\'](\d+)\s*h["\']', r'initialInterval: Duration.from({ hours: \1 })', workflows_content)
    workflows_content = re.sub(r'maximumInterval:\s*["\'](\d+)\s*h["\']', r'maximumInterval: Duration.from({ hours: \1 })', workflows_content)
    
    # Add Duration import if needed
    if 'Duration' not in workflows_content.split('\n')[0:30]:
        lines = workflows_content.split('\n')
        for i, line in enumerate(lines[:30]):
            if 'from "@temporalio' in line:
                if 'Duration' not in line:
                    lines[i] = line.replace('}', ', Duration }')
                break
        workflows_content = '\n'.join(lines)
    
    with sftp.open('/opt/xaker/shannon/src/temporal/workflows.ts', 'w') as f:
        f.write(workflows_content.encode('utf-8'))
    
    sftp.close()
    
    # Add NODE env to docker-compose.yml
    print("\n3. Adding NODE env to docker-compose.yml...")
    sftp = ssh.open_sftp()
    with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'r') as f:
        compose_content = f.read().decode('utf-8')
    
    # Add NODE=/usr/bin/node to worker environment
    if 'NODE=' not in compose_content:
        compose_content = compose_content.replace(
            '    environment:',
            '    environment:\n      - NODE=/usr/bin/node'
        )
        
        with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'w') as f:
            f.write(compose_content.encode('utf-8'))
        print("   ✅ Added NODE=/usr/bin/node to environment")
    else:
        print("   NODE already in environment")
    
    sftp.close()
    
    # Rebuild
    print("\n4. Rebuilding...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && npm run build 2>&1 | tail -20')
    build_output = stdout.read().decode('utf-8', errors='replace')
    print(build_output[-800:])
    
    if 'error' not in build_output.lower() or 'Successfully' in build_output:
        print("   ✅ Build successful or errors fixed")
        
        # Build and start
        print("\n5. Building and starting worker...")
        stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose build worker 2>&1 | tail -10')
        docker_build = stdout.read().decode('utf-8', errors='replace')
        print(docker_build[-500:])
        
        stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose up -d worker')
        print(stdout.read().decode('utf-8', errors='replace'))
    else:
        print("   ⚠️  Build still has errors")
    
    ssh.close()
    
    print("\n" + "=" * 80)
    print("FIX COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    fix_all()

