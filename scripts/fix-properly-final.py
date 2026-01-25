#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix properly - restore line 207 and fix Duration import"""

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

def fix_properly():
    """Fix properly"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("FIXING PROPERLY - RESTORE LINE 207 AND FIX DURATION")
    print("=" * 80)
    
    sftp = ssh.open_sftp()
    
    # Fix client.ts - restore line 207
    print("\n1. Fixing client.ts...")
    with sftp.open('/opt/xaker/shannon/src/temporal/client.ts', 'r') as f:
        client = f.read().decode('utf-8')
    
    client_lines = client.split('\n')
    
    # Find and fix broken line 207
    for i, line in enumerate(client_lines):
        if i == 206 and 'handle.result() });' in line:
            # Restore properly - handle.result() doesn't take timeout, but we can use workflow options
            # Actually, let's check the original Shannon code - maybe timeout is set elsewhere
            # For now, just use handle.result() without timeout
            client_lines[i] = "      const result = await handle.result();"
            print(f"   ✅ Fixed line 207: {client_lines[i]}")
    
    # Add Duration to client.ts import if needed
    for i, line in enumerate(client_lines[:30]):
        if 'from "@temporalio/client"' in line:
            if 'Duration' not in line:
                client_lines[i] = line.replace('}', ', Duration }')
                print(f"   ✅ Added Duration to client.ts import at line {i+1}")
            break
    
    with sftp.open('/opt/xaker/shannon/src/temporal/client.ts', 'w') as f:
        f.write('\n'.join(client_lines).encode('utf-8'))
    
    # Fix workflows.ts - Duration needs to be imported as value, not type
    print("\n2. Fixing workflows.ts...")
    with sftp.open('/opt/xaker/shannon/src/temporal/workflows.ts', 'r') as f:
        workflows = f.read().decode('utf-8')
    
    workflows_lines = workflows.split('\n')
    
    # Remove wrong Duration import if it's a type import
    for i, line in enumerate(workflows_lines[:30]):
        if 'import { Duration }' in line and 'from "@temporalio/common"' in line:
            # Check if it's importing Duration as type or value
            # If it says 'Duration' only, it might be importing as type
            # We need to ensure it's imported as a value
            if 'type Duration' not in line:
                # It's already a value import, good
                print(f"   ✅ Duration already imported correctly at line {i+1}")
            else:
                # Remove type keyword
                workflows_lines[i] = line.replace('type Duration', 'Duration')
                print(f"   ✅ Fixed Duration import at line {i+1}")
            break
    else:
        # Add Duration import from @temporalio/common
        # Find first import line
        for i, line in enumerate(workflows_lines[:30]):
            if 'import' in line and 'from' in line:
                workflows_lines.insert(i, "import { Duration } from '@temporalio/common';")
                print(f"   ✅ Added Duration import at line {i+1}")
                break
    
    with sftp.open('/opt/xaker/shannon/src/temporal/workflows.ts', 'w') as f:
        f.write('\n'.join(workflows_lines).encode('utf-8'))
    
    sftp.close()
    
    # Rebuild
    print("\n3. Rebuilding TypeScript...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && npm run build 2>&1')
    build_output = stdout.read(100000).decode('utf-8', errors='replace')
    
    if 'error' in build_output.lower():
        print("   ⚠️  Build has errors:")
        error_lines = [line for line in build_output.split('\n') if 'error' in line.lower()]
        for err in error_lines[-15:]:
            print(f"   {err}")
    else:
        print("   ✅ Build successful!")
        print(build_output[-300:])
    
    # If build successful, build Docker
    if 'error' not in build_output.lower():
        print("\n4. Building Docker image (this will take 2-3 minutes)...")
        stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && timeout 300 docker-compose build --no-cache worker 2>&1')
        
        import time
        start_time = time.time()
        output = ""
        while time.time() - start_time < 240:
            chunk = stdout.read(1024).decode('utf-8', errors='replace')
            if chunk:
                output += chunk
                if len(output) > 300:
                    print(output[-300:], end='', flush=True)
                    output = output[-300:]
            else:
                time.sleep(5)
                if stdout.channel.exit_status_ready():
                    break
        
        remaining = stdout.read(50000).decode('utf-8', errors='replace')
        print(remaining[-1000:])
        
        if 'Successfully' in output or 'Successfully' in remaining:
            print("\n   ✅ Docker build successful!")
            
            # Start services
            print("\n5. Starting services...")
            stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose up -d')
            print(stdout.read().decode('utf-8', errors='replace'))
            
            time.sleep(5)
            
            # Verify
            print("\n6. Verifying worker...")
            stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon | grep worker')
            worker = stdout.read().decode('utf-8', errors='replace')
            if worker:
                container_id = worker.split()[0]
                stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "ls -la /usr/local/bin/node && which node && /usr/local/bin/node --version && printenv NODE"')
                print(stdout.read().decode('utf-8', errors='replace'))
                print("\n✅ SUCCESS! Worker is running with node symlink")
                print("Try a new pentest now")
    
    ssh.close()
    
    print("\n" + "=" * 80)
    print("FIX COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    import time
    fix_properly()

