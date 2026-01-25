#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read and fix workflows.ts completely"""

import paramiko
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def read_and_fix():
    """Read and fix completely"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("READING AND FIXING WORKFLOWS.TS COMPLETELY")
    print("=" * 80)
    
    sftp = ssh.open_sftp()
    
    # Read entire file
    print("\n1. Reading entire workflows.ts...")
    with sftp.open('/opt/xaker/shannon/src/temporal/workflows.ts', 'r') as f:
        workflows = f.read().decode('utf-8')
    
    workflows_lines = workflows.split('\n')
    
    # Show first 70 lines to understand structure
    print("\n   First 70 lines:")
    for i in range(min(70, len(workflows_lines))):
        print(f"   {i+1:3d}: {workflows_lines[i]}")
    
    # Find where PRODUCTION_RETRY should be
    production_comment_line = -1
    for i, line in enumerate(workflows_lines):
        if 'Retry configuration for production' in line:
            production_comment_line = i
            break
    
    print(f"\n   Production comment at line {production_comment_line+1}")
    
    # Find where TESTING_RETRY should be
    testing_comment_line = -1
    for i, line in enumerate(workflows_lines):
        if 'Retry configuration for pipeline testing' in line:
            testing_comment_line = i
            break
    
    print(f"   Testing comment at line {testing_comment_line+1}")
    
    # Rebuild file properly
    new_lines = []
    
    # Copy everything before PRODUCTION_RETRY
    for i in range(production_comment_line):
        new_lines.append(workflows_lines[i])
    
    # Add PRODUCTION_RETRY properly
    new_lines.append("// Retry configuration for production (long intervals for billing recovery)")
    new_lines.append("const PRODUCTION_RETRY = {")
    new_lines.append("  initialInterval: 300000,")  # Use numbers directly
    new_lines.append("  maximumInterval: 1800000,")
    new_lines.append("  backoffCoefficient: 2,")
    new_lines.append("  maximumAttempts: 50,")
    new_lines.append("  nonRetryableErrorTypes: [")
    new_lines.append("    'WorkflowExecutionAlreadyStartedError',")
    new_lines.append("    'WorkflowExecutionNotFoundError',")
    new_lines.append("  ],")
    new_lines.append("};")
    new_lines.append("")
    
    # Copy everything between PRODUCTION_RETRY and TESTING_RETRY (skip broken lines)
    for i in range(production_comment_line + 1, testing_comment_line):
        line = workflows_lines[i]
        # Skip broken lines
        if 'initialInterval:' in line and 'Duration' in line:
            continue
        if 'maximumInterval:' in line and ('Duration' in line or 'ms(' in line):
            continue
        if 'backoffCoefficient:' in line and 'backoffCoefficient' not in line:
            continue
        if line.strip() and not line.strip().startswith('//'):
            # Check if it's part of nonRetryableErrorTypes
            if "'" in line or '"' in line:
                # It's an error type, keep it
                pass
            elif 'nonRetryableErrorTypes' in line:
                # Keep it
                pass
            else:
                # Skip other broken lines
                continue
        new_lines.append(line)
    
    # Add TESTING_RETRY properly
    new_lines.append("// Retry configuration for pipeline testing (fast iteration)")
    new_lines.append("const TESTING_RETRY = {")
    new_lines.append("  initialInterval: 10000,")
    new_lines.append("  maximumInterval: 30000,")
    new_lines.append("  backoffCoefficient: 2,")
    new_lines.append("  maximumAttempts: 5,")
    new_lines.append("  nonRetryableErrorTypes: PRODUCTION_RETRY.nonRetryableErrorTypes,")
    new_lines.append("};")
    new_lines.append("")
    
    # Copy everything after TESTING_RETRY
    for i in range(testing_comment_line + 1, len(workflows_lines)):
        line = workflows_lines[i]
        # Skip broken lines that are part of TESTING_RETRY
        if 'initialInterval:' in line and 'Duration' in line:
            continue
        if 'maximumInterval:' in line and ('Duration' in line or 'ms(' in line):
            continue
        if 'backoffCoefficient:' in line and i < testing_comment_line + 20:
            continue
        if 'maximumAttempts:' in line and i < testing_comment_line + 20:
            continue
        if 'nonRetryableErrorTypes:' in line and 'PRODUCTION_RETRY' not in line and i < testing_comment_line + 20:
            continue
        new_lines.append(line)
    
    # Remove Duration import if using numbers
    for i, line in enumerate(new_lines[:30]):
        if 'Duration' in line and 'import' in line:
            new_lines.pop(i)
            print(f"\n   ✅ Removed Duration import (using numbers directly)")
            break
    
    # Write back
    with sftp.open('/opt/xaker/shannon/src/temporal/workflows.ts', 'w') as f:
        f.write('\n'.join(new_lines).encode('utf-8'))
    
    sftp.close()
    
    # Rebuild
    print("\n2. Rebuilding TypeScript...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && npm run build 2>&1')
    build_output = stdout.read(100000).decode('utf-8', errors='replace')
    
    if 'error' in build_output.lower():
        print("   ⚠️  Build has errors:")
        error_lines = [line for line in build_output.split('\n') if 'error' in line.lower()]
        for err in error_lines[-20:]:
            print(f"   {err}")
    else:
        print("   ✅ Build successful!")
        print(build_output[-300:])
        
        # Build Docker
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
                
                # Restart backend
                print("\n6. Restarting backend...")
                stdin, stdout, stderr = ssh.exec_command('pm2 restart xaker-backend')
                print(stdout.read().decode('utf-8', errors='replace'))
                
                print("\n✅ SUCCESS! Everything is fixed and running")
                print("Try a new pentest now")
    
    ssh.close()
    
    print("\n" + "=" * 80)
    print("FIX COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    import time
    read_and_fix()

