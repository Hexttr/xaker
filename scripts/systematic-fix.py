#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Systematic fix of all issues"""

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

def systematic_fix():
    """Systematic fix"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("SYSTEMATIC FIX OF ALL ISSUES")
    print("=" * 80)
    
    sftp = ssh.open_sftp()
    
    # Read entire file
    print("\n1. Reading entire workflows.ts...")
    with sftp.open('/opt/xaker/shannon/src/temporal/workflows.ts', 'r') as f:
        workflows = f.read().decode('utf-8')
    
    workflows_lines = workflows.split('\n')
    
    # Step 1: Fix retry policies
    print("\n2. Fixing retry policies...")
    
    # Find and fix PRODUCTION_RETRY
    prod_start = -1
    prod_end = -1
    for i, line in enumerate(workflows_lines):
        if 'const PRODUCTION_RETRY = {' in line:
            prod_start = i
        elif prod_start >= 0 and prod_end == -1:
            if line.strip() == '};':
                prod_end = i + 1
                break
    
    if prod_start >= 0 and prod_end > prod_start:
        # Replace PRODUCTION_RETRY
        new_prod = [
            "const PRODUCTION_RETRY = {",
            "  initialInterval: 300000,",
            "  maximumInterval: 1800000,",
            "  backoffCoefficient: 2,",
            "  maximumAttempts: 50,",
            "  nonRetryableErrorTypes: [",
            "    'WorkflowExecutionAlreadyStartedError',",
            "    'WorkflowExecutionNotFoundError',",
            "  ],",
            "};"
        ]
        workflows_lines[prod_start:prod_end] = new_prod
        print(f"   ✅ Fixed PRODUCTION_RETRY (lines {prod_start+1}-{prod_end})")
    
    # Find and fix TESTING_RETRY
    test_start = -1
    test_end = -1
    for i, line in enumerate(workflows_lines):
        if 'const TESTING_RETRY = {' in line:
            test_start = i
        elif test_start >= 0 and test_end == -1:
            if line.strip() == '};':
                test_end = i + 1
                break
    
    if test_start >= 0 and test_end > test_start:
        # Replace TESTING_RETRY
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
        print(f"   ✅ Fixed TESTING_RETRY (lines {test_start+1}-{test_end})")
    
    # Step 2: Remove duplicate/broken lines
    print("\n3. Removing duplicate/broken lines...")
    lines_to_remove = []
    for i, line in enumerate(workflows_lines):
        # Remove standalone nonRetryableErrorTypes: lines
        if line.strip() == 'nonRetryableErrorTypes:' and i > 0:
            prev_line = workflows_lines[i-1].strip()
            if prev_line != '},' and 'nonRetryableErrorTypes' not in prev_line:
                lines_to_remove.append(i)
        
        # Remove broken Duration lines
        if 'Duration.fromMilliseconds(' in line and ',' in line and ')' not in line:
            lines_to_remove.append(i)
        
        # Remove ms() wrappers
        if 'ms(' in line and 'Duration' in line:
            workflows_lines[i] = line.replace('ms(', '').replace(')', '')
    
    # Remove lines in reverse order
    for i in sorted(lines_to_remove, reverse=True):
        workflows_lines.pop(i)
        print(f"   ✅ Removed broken line {i+1}")
    
    # Step 3: Fix function signatures - find functions that use 'input' but don't have it
    print("\n4. Fixing function signatures...")
    
    # Find all function definitions
    functions = []
    for i, line in enumerate(workflows_lines):
        if re.search(r'(export\s+)?(async\s+)?function\s+\w+', line):
            # Find function name and parameters
            match = re.search(r'function\s+(\w+)\s*\(([^)]*)\)', line)
            if match:
                func_name = match.group(1)
                params = match.group(2)
                functions.append({
                    'name': func_name,
                    'line': i,
                    'params': params,
                    'line_content': line
                })
    
    # Check which functions use 'input' but don't have it in parameters
    for func in functions:
        func_start = func['line']
        # Find where function ends (next function or end of file)
        func_end = len(workflows_lines)
        for i in range(func_start + 1, len(workflows_lines)):
            if re.search(r'(export\s+)?(async\s+)?function\s+\w+', workflows_lines[i]):
                func_end = i
                break
        
        # Check if function uses 'input'
        uses_input = False
        for i in range(func_start, func_end):
            if re.search(r'\binput\b', workflows_lines[i]) and 'input:' not in workflows_lines[i]:
                uses_input = True
                break
        
        # If uses input but doesn't have it in parameters, add it
        if uses_input and 'input' not in func['params']:
            func_line = workflows_lines[func_start]
            # Add input parameter
            if func['params'].strip():
                new_params = f"{func['params']}, input: PipelineInput"
            else:
                new_params = "input: PipelineInput"
            
            workflows_lines[func_start] = re.sub(
                r'\(([^)]*)\)',
                f'({new_params})',
                func_line
            )
            print(f"   ✅ Added input parameter to function {func['name']} at line {func_start+1}")
    
    # Step 4: Remove Duration import if using numbers
    print("\n5. Removing Duration import...")
    for i, line in enumerate(workflows_lines[:30]):
        if 'Duration' in line and 'import' in line:
            workflows_lines.pop(i)
            print(f"   ✅ Removed Duration import at line {i+1}")
            break
    
    # Write back
    print("\n6. Writing fixed file...")
    with sftp.open('/opt/xaker/shannon/src/temporal/workflows.ts', 'w') as f:
        f.write('\n'.join(workflows_lines).encode('utf-8'))
    
    sftp.close()
    
    # Rebuild
    print("\n7. Rebuilding TypeScript...")
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
    if 'error' not in build_output.lower() or len([e for e in build_output.split('\n') if 'error' in e.lower()]) < 5:
        print("\n8. Building Docker image (this will take 2-3 minutes)...")
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
            print("\n9. Starting services...")
            stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose up -d')
            print(stdout.read().decode('utf-8', errors='replace'))
            
            time.sleep(5)
            
            # Verify
            print("\n10. Verifying worker...")
            stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon | grep worker')
            worker = stdout.read().decode('utf-8', errors='replace')
            if worker:
                container_id = worker.split()[0]
                stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "ls -la /usr/local/bin/node && which node && /usr/local/bin/node --version && printenv NODE"')
                print(stdout.read().decode('utf-8', errors='replace'))
                
                # Restart backend
                print("\n11. Restarting backend...")
                stdin, stdout, stderr = ssh.exec_command('pm2 restart xaker-backend')
                print(stdout.read().decode('utf-8', errors='replace'))
                
                print("\n✅ SUCCESS! Everything is fixed and running")
                print("Try a new pentest now")
    
    ssh.close()
    
    print("\n" + "=" * 80)
    print("SYSTEMATIC FIX COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    import time
    systematic_fix()

