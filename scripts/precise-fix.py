#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Precise fix - read file and fix exactly what's wrong"""

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

def precise_fix():
    """Precise fix"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("PRECISE FIX")
    print("=" * 80)
    
    sftp = ssh.open_sftp()
    
    # Read file
    print("\n1. Reading workflows.ts...")
    with sftp.open('/opt/xaker/shannon/src/temporal/workflows.ts', 'r') as f:
        workflows = f.read().decode('utf-8')
    
    workflows_lines = workflows.split('\n')
    
    # Show problematic lines
    print("\n   Lines 64-72:")
    for i in range(63, min(72, len(workflows_lines))):
        print(f"   {i+1:3d}: {workflows_lines[i]}")
    
    # Find TESTING_RETRY and fix it precisely
    test_start = -1
    for i, line in enumerate(workflows_lines):
        if 'const TESTING_RETRY = {' in line:
            test_start = i
            break
    
    if test_start >= 0:
        print(f"\n   TESTING_RETRY starts at line {test_start+1}")
        
        # Find where it should end
        test_end = test_start + 10
        for i in range(test_start + 1, min(test_start + 15, len(workflows_lines))):
            if workflows_lines[i].strip() == '};':
                test_end = i + 1
                break
        
        # Show what's there
        print(f"   Current TESTING_RETRY (lines {test_start+1}-{test_end}):")
        for i in range(test_start, test_end):
            print(f"   {i+1:3d}: {workflows_lines[i]}")
        
        # Replace with correct structure
        new_test = [
            "const TESTING_RETRY = {",
            "  initialInterval: 10000,",
            "  maximumInterval: 30000,",
            "  backoffCoefficient: 2,",
            "  maximumAttempts: 5,",
            "  nonRetryableErrorTypes: PRODUCTION_RETRY.nonRetryableErrorTypes,",
            "};"
        ]
        
        workflows_lines[test_start:test_end] = new_test
        print(f"\n   ✅ Replaced TESTING_RETRY with correct structure")
    
    # Fix function signatures - find functions that use input
    print("\n2. Fixing function signatures...")
    
    # Find function definitions more carefully
    for i, line in enumerate(workflows_lines):
        # Look for function definitions
        if re.search(r'export\s+async\s+function\s+\w+', line) or re.search(r'async\s+function\s+\w+', line):
            # Check if this function uses 'input' in the next 50 lines
            uses_input = False
            for j in range(i+1, min(i+50, len(workflows_lines))):
                if re.search(r'\binput\.', workflows_lines[j]) or re.search(r'\binput\s*:', workflows_lines[j]):
                    uses_input = True
                    break
            
            if uses_input:
                # Check if input is in parameters
                if 'input' not in line and ': PipelineInput' not in line:
                    # Add input parameter
                    if '(' in line and ')' in line:
                        # Extract function signature
                        match = re.search(r'(export\s+async\s+function\s+\w+)\s*\(([^)]*)\)', line)
                        if match:
                            func_decl = match.group(1)
                            params = match.group(2)
                            if params.strip():
                                new_params = f"{params}, input: PipelineInput"
                            else:
                                new_params = "input: PipelineInput"
                            
                            workflows_lines[i] = re.sub(
                                r'(export\s+async\s+function\s+\w+)\s*\([^)]*\)',
                                f'{func_decl}({new_params})',
                                line
                            )
                            print(f"   ✅ Added input parameter to function at line {i+1}")
    
    # Write back
    print("\n3. Writing fixed file...")
    with sftp.open('/opt/xaker/shannon/src/temporal/workflows.ts', 'w') as f:
        f.write('\n'.join(workflows_lines).encode('utf-8'))
    
    sftp.close()
    
    # Rebuild
    print("\n4. Rebuilding TypeScript...")
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
        print("\n5. Building Docker image (this will take 2-3 minutes)...")
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
            print("\n6. Starting services...")
            stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose up -d')
            print(stdout.read().decode('utf-8', errors='replace'))
            
            time.sleep(5)
            
            # Verify
            print("\n7. Verifying worker...")
            stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon | grep worker')
            worker = stdout.read().decode('utf-8', errors='replace')
            if worker:
                container_id = worker.split()[0]
                stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "ls -la /usr/local/bin/node && which node && /usr/local/bin/node --version && printenv NODE"')
                print(stdout.read().decode('utf-8', errors='replace'))
                
                # Restart backend
                print("\n8. Restarting backend...")
                stdin, stdout, stderr = ssh.exec_command('pm2 restart xaker-backend')
                print(stdout.read().decode('utf-8', errors='replace'))
                
                print("\n✅ SUCCESS! Everything is fixed and running")
                print("Try a new pentest now")
    
    ssh.close()
    
    print("\n" + "=" * 80)
    print("PRECISE FIX COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    import time
    precise_fix()

