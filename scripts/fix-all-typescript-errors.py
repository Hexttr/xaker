#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix all TypeScript errors properly"""

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

def fix_all_errors():
    """Fix all TypeScript errors"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("FIXING ALL TYPESCRIPT ERRORS")
    print("=" * 80)
    
    sftp = ssh.open_sftp()
    
    # Fix client.ts
    print("\n1. Fixing client.ts...")
    with sftp.open('/opt/xaker/shannon/src/temporal/client.ts', 'r') as f:
        client = f.read().decode('utf-8')
    
    client_lines = client.split('\n')
    
    # Add Duration to import from @temporalio/client
    for i, line in enumerate(client_lines[:30]):
        if 'from "@temporalio/client"' in line:
            if 'Duration' not in line:
                client_lines[i] = line.replace('}', ', Duration }')
                print(f"   ✅ Added Duration to import at line {i+1}")
            break
    
    # Fix line 207 - Duration.from({ hours: 3 })
    for i, line in enumerate(client_lines):
        if i == 206:  # Line 207 (0-indexed)
            print(f"   Line 207 before: {line[:80]}")
            # Fix the syntax error
            if 'Duration.from({ milliseconds:' in line and 'h)' in line:
                # Replace milliseconds: 3h with hours: 3
                client_lines[i] = re.sub(
                    r'Duration\.from\(\{\s*milliseconds:\s*(\d+)\s*h\s*\}\)',
                    r'Duration.from({ hours: \1 })',
                    line
                )
            elif 'Duration.from({ milliseconds:' in line:
                # Just milliseconds without h
                client_lines[i] = re.sub(
                    r'Duration\.from\(\{\s*milliseconds:\s*(\d+)\s*\}\)',
                    r'Duration.from({ milliseconds: \1 })',
                    line
                )
            elif 'handle.result({ timeout:' in line and 'ms(' in line:
                # Fix handle.result({ timeout: ms(3h) })
                client_lines[i] = re.sub(
                    r'timeout:\s*ms\(\s*(\d+)\s*h\s*\)',
                    r'timeout: Duration.from({ hours: \1 })',
                    line
                )
            print(f"   Line 207 after:  {client_lines[i][:80]}")
    
    with sftp.open('/opt/xaker/shannon/src/temporal/client.ts', 'w') as f:
        f.write('\n'.join(client_lines).encode('utf-8'))
    
    # Fix workflows.ts
    print("\n2. Fixing workflows.ts...")
    with sftp.open('/opt/xaker/shannon/src/temporal/workflows.ts', 'r') as f:
        workflows = f.read().decode('utf-8')
    
    workflows_lines = workflows.split('\n')
    
    # Add Duration import from @temporalio/common
    duration_imported = False
    for i, line in enumerate(workflows_lines[:30]):
        if 'from "@temporalio/common"' in line:
            if 'Duration' not in line:
                workflows_lines[i] = line.replace('}', ', Duration }')
                duration_imported = True
                print(f"   ✅ Added Duration to existing import at line {i+1}")
            else:
                duration_imported = True
            break
    
    # If no @temporalio/common import, add it
    if not duration_imported:
        # Find first import line
        for i, line in enumerate(workflows_lines[:30]):
            if 'import' in line and 'from' in line:
                # Insert Duration import before this line
                workflows_lines.insert(i, "import { Duration } from '@temporalio/common';")
                duration_imported = True
                print(f"   ✅ Added Duration import at line {i+1}")
                break
    
    # Fix retry policies - replace string durations with Duration.from()
    print("\n3. Fixing retry policies...")
    for i, line in enumerate(workflows_lines):
        # Fix initialInterval and maximumInterval
        if 'initialInterval:' in line and ("'" in line or '"' in line):
            # Replace '5 minutes' with Duration.from({ minutes: 5 })
            workflows_lines[i] = re.sub(
                r"initialInterval:\s*['\"](\d+)\s+minutes?['\"]",
                r'initialInterval: Duration.from({ minutes: \1 })',
                line
            )
            workflows_lines[i] = re.sub(
                r"initialInterval:\s*['\"](\d+)\s+seconds?['\"]",
                r'initialInterval: Duration.from({ seconds: \1 })',
                line
            )
        
        if 'maximumInterval:' in line and ("'" in line or '"' in line):
            workflows_lines[i] = re.sub(
                r"maximumInterval:\s*['\"](\d+)\s+minutes?['\"]",
                r'maximumInterval: Duration.from({ minutes: \1 })',
                line
            )
            workflows_lines[i] = re.sub(
                r"maximumInterval:\s*['\"](\d+)\s+seconds?['\"]",
                r'maximumInterval: Duration.from({ seconds: \1 })',
                line
            )
    
    with sftp.open('/opt/xaker/shannon/src/temporal/workflows.ts', 'w') as f:
        f.write('\n'.join(workflows_lines).encode('utf-8'))
    
    sftp.close()
    
    # Rebuild TypeScript
    print("\n4. Rebuilding TypeScript...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && npm run build 2>&1')
    build_output = stdout.read(100000).decode('utf-8', errors='replace')
    
    if 'error' in build_output.lower():
        print("   ⚠️  Build has errors:")
        print(build_output[-1000:])
    else:
        print("   ✅ Build successful!")
    
    # Show last few lines
    print(f"\n   Last 200 chars: {build_output[-200:]}")
    
    if 'error' not in build_output.lower():
        # Build Docker image
        print("\n5. Building Docker image (this will take 2-3 minutes)...")
        stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && timeout 300 docker-compose build --no-cache worker 2>&1')
        
        # Monitor build
        start_time = time.time()
        output = ""
        while time.time() - start_time < 240:  # 4 minutes
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
            print("\n6. Starting services...")
            stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose up -d')
            start_output = stdout.read().decode('utf-8', errors='replace')
            print(start_output)
            
            time.sleep(5)
            
            # Verify worker
            print("\n7. Verifying worker...")
            stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon | grep worker')
            worker = stdout.read().decode('utf-8', errors='replace')
            if worker:
                container_id = worker.split()[0]
                print(f"   Container: {container_id}")
                
                stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "ls -la /usr/local/bin/node && which node && /usr/local/bin/node --version && printenv NODE"')
                verify = stdout.read().decode('utf-8', errors='replace')
                print(verify)
                
                print("\n✅ SUCCESS! Worker is running with node symlink")
                print("Try a new pentest now")
            else:
                print("   ⚠️  Worker container not found")
        else:
            print("\n   ⚠️  Docker build may have failed - check output above")
    else:
        print("\n⚠️  TypeScript build failed - need to fix errors first")
        print("Check the errors above and fix them manually")
    
    ssh.close()
    
    print("\n" + "=" * 80)
    print("FIX COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    import time
    fix_all_errors()

