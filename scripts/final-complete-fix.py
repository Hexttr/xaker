#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Final complete fix - restore workflows.ts and build everything"""

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

def final_complete_fix():
    """Final complete fix"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("FINAL COMPLETE FIX")
    print("=" * 80)
    
    sftp = ssh.open_sftp()
    
    # Read workflows.ts completely
    print("\n1. Reading workflows.ts...")
    with sftp.open('/opt/xaker/shannon/src/temporal/workflows.ts', 'r') as f:
        workflows = f.read().decode('utf-8')
    
    workflows_lines = workflows.split('\n')
    
    # Find PRODUCTION_RETRY and TESTING_RETRY
    production_start = -1
    production_end = -1
    testing_start = -1
    testing_end = -1
    
    for i, line in enumerate(workflows_lines):
        if 'const PRODUCTION_RETRY' in line:
            production_start = i
        elif production_start >= 0 and production_end == -1:
            if line.strip() == '};':
                production_end = i + 1
        if 'const TESTING_RETRY' in line:
            testing_start = i
        elif testing_start >= 0 and testing_end == -1:
            if line.strip() == '};':
                testing_end = i + 1
    
    print(f"   PRODUCTION_RETRY: lines {production_start+1}-{production_end}")
    print(f"   TESTING_RETRY: lines {testing_start+1}-{testing_end}")
    
    # Show current broken structure
    if production_start >= 0:
        print("\n   Current PRODUCTION_RETRY:")
        for i in range(production_start, min(production_start + 15, len(workflows_lines))):
            print(f"   Line {i+1}: {workflows_lines[i]}")
    
    # Check for Duration import
    has_duration_import = False
    duration_import_line = -1
    for i, line in enumerate(workflows_lines[:30]):
        if 'Duration' in line and 'import' in line:
            has_duration_import = True
            duration_import_line = i
            print(f"\n   Duration import found at line {i+1}: {line}")
            break
    
    # Fix Duration import - use @temporalio/common but check if it's a value
    # Actually, Duration.fromMilliseconds should work from @temporalio/common
    # Let's check the actual import
    if has_duration_import:
        # Check if it's importing Duration as type or value
        if 'type Duration' in workflows_lines[duration_import_line]:
            # It's a type import, we need value
            workflows_lines[duration_import_line] = workflows_lines[duration_import_line].replace('type Duration', 'Duration')
            print(f"   ✅ Fixed Duration import - removed 'type'")
        elif '@temporalio/common' not in workflows_lines[duration_import_line]:
            # Wrong import, replace it
            workflows_lines[duration_import_line] = "import { Duration } from '@temporalio/common';"
            print(f"   ✅ Fixed Duration import - changed to @temporalio/common")
    else:
        # Add Duration import
        workflows_lines.insert(0, "import { Duration } from '@temporalio/common';")
        print(f"   ✅ Added Duration import")
        # Adjust indices
        production_start += 1
        production_end += 1
        testing_start += 1
        testing_end += 1
    
    # Restore PRODUCTION_RETRY - remove duplicates and fix structure
    if production_start >= 0 and production_end > production_start:
        # Read current content
        current_production = workflows_lines[production_start:production_end]
        
        # Find duplicate maximumInterval
        has_duplicate = False
        for i, line in enumerate(current_production):
            if 'maximumInterval:' in line and i > 0:
                # Check if previous line also has maximumInterval
                if 'maximumInterval:' in current_production[i-1]:
                    has_duplicate = True
                    # Remove this duplicate line
                    current_production.pop(i)
                    print(f"   ✅ Removed duplicate maximumInterval")
                    break
        
        # Ensure proper structure
        new_production = []
        for line in current_production:
            # Skip broken lines
            if 'maximumInterval: Duration.fromMilliseconds(1800000,' in line:
                # Fix incomplete line
                new_production.append("  maximumInterval: Duration.fromMilliseconds(1800000),")
            elif 'ms(' in line and 'Duration' in line:
                # Remove ms() wrapper
                line = line.replace('ms(', '').replace(')', '')
                new_production.append(line)
            else:
                new_production.append(line)
        
        workflows_lines[production_start:production_end] = new_production
        print(f"   ✅ Fixed PRODUCTION_RETRY structure")
    
    # Restore TESTING_RETRY
    if testing_start >= 0 and testing_end > testing_start:
        current_testing = workflows_lines[testing_start:testing_end]
        
        # Find duplicate maximumInterval
        for i, line in enumerate(current_testing):
            if 'maximumInterval:' in line and i > 0:
                if 'maximumInterval:' in current_testing[i-1]:
                    current_testing.pop(i)
                    print(f"   ✅ Removed duplicate maximumInterval in TESTING_RETRY")
                    break
        
        # Fix broken lines
        new_testing = []
        for line in current_testing:
            if 'maximumInterval: Duration.fromMilliseconds(30000,' in line:
                new_testing.append("  maximumInterval: Duration.fromMilliseconds(30000),")
            elif 'ms(' in line and 'Duration' in line:
                line = line.replace('ms(', '').replace(')', '')
                new_testing.append(line)
            else:
                new_testing.append(line)
        
        workflows_lines[testing_start:testing_end] = new_testing
        print(f"   ✅ Fixed TESTING_RETRY structure")
    
    # Write back
    with sftp.open('/opt/xaker/shannon/src/temporal/workflows.ts', 'w') as f:
        f.write('\n'.join(workflows_lines).encode('utf-8'))
    
    sftp.close()
    
    # Rebuild TypeScript
    print("\n2. Rebuilding TypeScript...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && npm run build 2>&1')
    build_output = stdout.read(100000).decode('utf-8', errors='replace')
    
    if 'error' in build_output.lower():
        print("   ⚠️  Build has errors:")
        error_lines = [line for line in build_output.split('\n') if 'error' in line.lower()]
        for err in error_lines[-20:]:
            print(f"   {err}")
        
        # If Duration is still a type issue, try using numbers directly
        if "'Duration' only refers to a type" in build_output:
            print("\n   Trying alternative: using numbers directly...")
            sftp = ssh.open_sftp()
            with sftp.open('/opt/xaker/shannon/src/temporal/workflows.ts', 'r') as f:
                workflows = f.read().decode('utf-8')
            
            # Replace Duration.fromMilliseconds(X) with just X (numbers)
            workflows = re.sub(
                r'Duration\.fromMilliseconds\((\d+)\)',
                r'\1',
                workflows
            )
            
            # Remove Duration import
            workflows_lines = workflows.split('\n')
            for i, line in enumerate(workflows_lines[:30]):
                if 'Duration' in line and 'import' in line:
                    workflows_lines.pop(i)
                    break
            
            with sftp.open('/opt/xaker/shannon/src/temporal/workflows.ts', 'w') as f:
                f.write('\n'.join(workflows_lines).encode('utf-8'))
            
            sftp.close()
            
            # Rebuild again
            stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && npm run build 2>&1')
            build_output = stdout.read(100000).decode('utf-8', errors='replace')
    
    if 'error' not in build_output.lower():
        print("   ✅ Build successful!")
        print(build_output[-300:])
        
        # Build Docker image
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
            start_output = stdout.read().decode('utf-8', errors='replace')
            print(start_output)
            
            time.sleep(5)
            
            # Verify worker
            print("\n5. Verifying worker...")
            stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon | grep worker')
            worker = stdout.read().decode('utf-8', errors='replace')
            if worker:
                container_id = worker.split()[0]
                print(f"   Container: {container_id}")
                
                stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "ls -la /usr/local/bin/node && which node && /usr/local/bin/node --version && printenv NODE"')
                verify = stdout.read().decode('utf-8', errors='replace')
                print(verify)
                
                # Restart backend
                print("\n6. Restarting backend...")
                stdin, stdout, stderr = ssh.exec_command('pm2 restart xaker-backend')
                print(stdout.read().decode('utf-8', errors='replace'))
                
                print("\n✅ SUCCESS! Everything is fixed and running")
                print("Try a new pentest now")
            else:
                print("   ⚠️  Worker container not found")
        else:
            print("\n   ⚠️  Docker build may have failed - check output above")
    else:
        print("   ⚠️  TypeScript build failed - check errors above")
    
    ssh.close()
    
    print("\n" + "=" * 80)
    print("FIX COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    import time
    final_complete_fix()
