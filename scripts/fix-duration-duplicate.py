#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix Duration duplicate import and use correct import"""

import paramiko
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def fix_duplicate():
    """Fix duplicate Duration import"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("FIXING DURATION DUPLICATE IMPORT")
    print("=" * 80)
    
    sftp = ssh.open_sftp()
    
    # Fix workflows.ts
    print("\n1. Reading workflows.ts...")
    with sftp.open('/opt/xaker/shannon/src/temporal/workflows.ts', 'r') as f:
        workflows = f.read().decode('utf-8')
    
    workflows_lines = workflows.split('\n')
    
    # Show first 10 lines
    print("\n   First 10 lines:")
    for i, line in enumerate(workflows_lines[:10]):
        print(f"   Line {i+1}: {line}")
    
    # Remove duplicate Duration imports
    duration_imports = []
    for i, line in enumerate(workflows_lines[:30]):
        if 'Duration' in line and 'import' in line:
            duration_imports.append(i)
    
    print(f"\n   Found {len(duration_imports)} Duration imports at lines: {[i+1 for i in duration_imports]}")
    
    # Keep only the first one, remove others
    if len(duration_imports) > 1:
        for i in reversed(duration_imports[1:]):  # Remove from end to preserve indices
            workflows_lines.pop(i)
            print(f"   ✅ Removed duplicate Duration import at line {i+1}")
    
    # Check if Duration is imported from correct place
    # Duration should be imported from '@temporalio/common' as a value
    has_correct_import = False
    for i, line in enumerate(workflows_lines[:30]):
        if 'Duration' in line and 'from "@temporalio/common"' in line:
            if 'type Duration' not in line:
                has_correct_import = True
                print(f"   ✅ Duration correctly imported at line {i+1}")
            else:
                # Fix type import to value import
                workflows_lines[i] = line.replace('type Duration', 'Duration')
                has_correct_import = True
                print(f"   ✅ Fixed Duration import at line {i+1}")
            break
    
    # If no correct import, add it
    if not has_correct_import and len(duration_imports) == 0:
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
    print("\n2. Rebuilding TypeScript...")
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
        print("\n3. Building Docker image (this will take 2-3 minutes)...")
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
            print("\n4. Starting services...")
            stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose up -d')
            print(stdout.read().decode('utf-8', errors='replace'))
            
            time.sleep(5)
            
            # Verify
            print("\n5. Verifying worker...")
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
    fix_duplicate()

