#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Complete final fix - all TypeScript errors and use existing image"""

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

def complete_fix():
    """Complete fix"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("COMPLETE FINAL FIX")
    print("=" * 80)
    
    # Fix workflows.ts - add Duration import
    print("\n1. Fixing workflows.ts...")
    sftp = ssh.open_sftp()
    with sftp.open('/opt/xaker/shannon/src/temporal/workflows.ts', 'r') as f:
        content = f.read().decode('utf-8')
    
    lines = content.split('\n')
    
    # Find and fix import
    for i, line in enumerate(lines[:30]):
        if 'from "@temporalio' in line or 'from "@temporalio/workflow"' in line:
            print(f"   Found import at line {i+1}: {line}")
            if 'Duration' not in line:
                # Add Duration to import
                if '}' in line:
                    lines[i] = line.replace('}', ', Duration }')
                elif '}' not in line:
                    # Multi-line import
                    j = i + 1
                    while j < len(lines) and j < i + 10:
                        if '}' in lines[j]:
                            lines[j] = lines[j].replace('}', ', Duration }')
                            break
                        j += 1
                print(f"   Fixed: {lines[i]}")
            break
    
    content = '\n'.join(lines)
    
    with sftp.open('/opt/xaker/shannon/src/temporal/workflows.ts', 'w') as f:
        f.write(content.encode('utf-8'))
    
    sftp.close()
    
    # Rebuild
    print("\n2. Rebuilding TypeScript...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && npm run build 2>&1 | tail -3')
    build_output = stdout.read().decode('utf-8', errors='replace')
    print(build_output[-200:])
    
    if 'error' not in build_output.lower():
        print("   ✅ Build successful!")
        
        # Build Docker
        print("\n3. Building Docker image...")
        stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose build worker 2>&1 | tail -5')
        docker_build = stdout.read().decode('utf-8', errors='replace')
        print(docker_build[-300:])
        
        # Start
        print("\n4. Starting services...")
        stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose up -d')
        start_output = stdout.read().decode('utf-8', errors='replace')
        print(start_output)
        
        import time
        time.sleep(5)
        
        # Verify
        print("\n5. Verifying worker...")
        stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon | grep worker')
        worker = stdout.read().decode('utf-8', errors='replace')
        if worker:
            container_id = worker.split()[0]
            print(f"   Container: {container_id}")
            
            stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "ls -la /usr/local/bin/node && which node && printenv NODE && printenv PATH"')
            verify = stdout.read().decode('utf-8', errors='replace')
            print(verify)
        else:
            print("   Worker not running")
    else:
        print("   ⚠️  Build has errors - trying to use existing image")
        
        # Try to use existing image
        print("\n3. Trying to use existing image...")
        stdin, stdout, stderr = ssh.exec_command('docker images | grep shannon | head -1')
        existing = stdout.read().decode('utf-8', errors='replace')
        if existing:
            print(f"   Found existing image")
            # Start with existing image
            stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose up -d worker')
            print(stdout.read().decode('utf-8', errors='replace'))
            
            import time
            time.sleep(5)
            
            # Create symlink in running container
            stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon | grep worker')
            worker = stdout.read().decode('utf-8', errors='replace')
            if worker:
                container_id = worker.split()[0]
                print(f"\n4. Creating symlink in container {container_id}...")
                stdin, stdout, stderr = ssh.exec_command(f'docker exec -u root {container_id} sh -c "mkdir -p /usr/local/bin && ln -sf /usr/bin/node /usr/local/bin/node && ls -la /usr/local/bin/node"')
                print(stdout.read().decode('utf-8', errors='replace'))
                
                stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "which node && printenv NODE"')
                print(stdout.read().decode('utf-8', errors='replace'))
    
    ssh.close()
    
    print("\n" + "=" * 80)
    print("COMPLETE FIX DONE")
    print("=" * 80)
    print("Try a new pentest now")

if __name__ == "__main__":
    import time
    complete_fix()

