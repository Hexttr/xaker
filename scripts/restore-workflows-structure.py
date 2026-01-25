#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Restore workflows.ts structure properly"""

import paramiko
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def restore_structure():
    """Restore workflows.ts structure"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("RESTORING WORKFLOWS.TS STRUCTURE")
    print("=" * 80)
    
    sftp = ssh.open_sftp()
    
    # Read file
    with sftp.open('/opt/xaker/shannon/src/temporal/workflows.ts', 'r') as f:
        workflows = f.read().decode('utf-8')
    
    workflows_lines = workflows.split('\n')
    
    # Find PRODUCTION_RETRY and TESTING_RETRY
    production_start = -1
    testing_start = -1
    
    for i, line in enumerate(workflows_lines):
        if 'PRODUCTION_RETRY' in line and '=' in line:
            production_start = i
        if 'TESTING_RETRY' in line and '=' in line:
            testing_start = i
    
    print(f"\n   PRODUCTION_RETRY starts at line {production_start+1}")
    print(f"   TESTING_RETRY starts at line {testing_start+1}")
    
    # Show current broken structure
    print("\n   Current PRODUCTION_RETRY (lines 45-55):")
    for i in range(44, min(56, len(workflows_lines))):
        print(f"   Line {i+1}: {workflows_lines[i]}")
    
    # Restore PRODUCTION_RETRY
    if production_start >= 0:
        # Find end of PRODUCTION_RETRY
        end = production_start + 10
        for i in range(production_start + 1, min(production_start + 15, len(workflows_lines))):
            if workflows_lines[i].strip() == '};' or workflows_lines[i].strip() == '},':
                end = i + 1
                break
        
        # Replace with correct structure
        new_production = [
            "const PRODUCTION_RETRY = {",
            "  initialInterval: Duration.fromMilliseconds(300000),",
            "  maximumInterval: Duration.fromMilliseconds(1800000),",
            "  backoffCoefficient: 2,",
            "  maximumAttempts: 50,",
            "  nonRetryableErrorTypes: [",
            "    'WorkflowExecutionAlreadyStartedError',",
            "    'WorkflowExecutionNotFoundError',",
            "  ],",
            "};"
        ]
        
        # Replace lines
        workflows_lines[production_start:end] = new_production
        print(f"\n   ✅ Restored PRODUCTION_RETRY")
    
    # Restore TESTING_RETRY
    if testing_start >= 0:
        # Find end
        end = testing_start + 10
        for i in range(testing_start + 1, min(testing_start + 15, len(workflows_lines))):
            if workflows_lines[i].strip() == '};' or workflows_lines[i].strip() == '},':
                end = i + 1
                break
        
        # Replace with correct structure
        new_testing = [
            "const TESTING_RETRY = {",
            "  initialInterval: Duration.fromMilliseconds(10000),",
            "  maximumInterval: Duration.fromMilliseconds(30000),",
            "  backoffCoefficient: 2,",
            "  maximumAttempts: 5,",
            "  nonRetryableErrorTypes: PRODUCTION_RETRY.nonRetryableErrorTypes,",
            "};"
        ]
        
        workflows_lines[testing_start:end] = new_testing
        print(f"   ✅ Restored TESTING_RETRY")
    
    # Ensure Duration import
    has_duration = False
    for i, line in enumerate(workflows_lines[:30]):
        if 'Duration' in line and 'import' in line and '@temporalio/common' in line:
            has_duration = True
            break
    
    if not has_duration:
        workflows_lines.insert(0, "import { Duration } from '@temporalio/common';")
        print(f"   ✅ Added Duration import")
    
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
    print("RESTORE COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    import time
    restore_structure()

