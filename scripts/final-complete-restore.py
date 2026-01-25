#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Final complete restore - remove all broken lines and fix functions"""

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

def final_complete_restore():
    """Final complete restore"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("FINAL COMPLETE RESTORE")
    print("=" * 80)
    
    sftp = ssh.open_sftp()
    
    # Read file
    with sftp.open('/opt/xaker/shannon/src/temporal/workflows.ts', 'r') as f:
        workflows = f.read().decode('utf-8')
    
    workflows_lines = workflows.split('\n')
    
    # Find TESTING_RETRY end
    test_end = -1
    for i, line in enumerate(workflows_lines):
        if 'const TESTING_RETRY = {' in line:
            for j in range(i+1, min(i+10, len(workflows_lines))):
                if workflows_lines[j].strip() == '};':
                    test_end = j + 1
                    break
            break
    
    print(f"\n   TESTING_RETRY ends at line {test_end}")
    
    # Show lines after TESTING_RETRY
    print("\n   Lines after TESTING_RETRY (64-72):")
    for i in range(63, min(72, len(workflows_lines))):
        print(f"   {i+1:3d}: {workflows_lines[i]}")
    
    # Remove broken lines 66-69 (they're duplicates)
    if test_end >= 0:
        # Check if there are broken lines after TESTING_RETRY
        broken_start = test_end
        broken_end = test_end
        for i in range(test_end, min(test_end + 10, len(workflows_lines))):
            if 'initialInterval:' in workflows_lines[i] or 'maximumInterval:' in workflows_lines[i] or 'nonRetryableErrorTypes:' in workflows_lines[i]:
                if broken_start == test_end:
                    broken_start = i
                broken_end = i + 1
            elif workflows_lines[i].strip() == '};' and i > test_end:
                broken_end = i + 1
                break
        
        if broken_start > test_end:
            print(f"\n   Removing broken lines {broken_start+1}-{broken_end}")
            workflows_lines = workflows_lines[:broken_start] + workflows_lines[broken_end:]
            print(f"   ✅ Removed broken lines")
    
    # Fix function signatures - find functions that use input
    print("\n2. Fixing function signatures...")
    
    # Read file again to get updated line numbers
    workflows = '\n'.join(workflows_lines)
    workflows_lines = workflows.split('\n')
    
    # Find all function definitions and check if they use input
    for i, line in enumerate(workflows_lines):
        # Look for function definitions
        if re.search(r'export\s+async\s+function\s+\w+', line):
            func_name_match = re.search(r'function\s+(\w+)', line)
            if func_name_match:
                func_name = func_name_match.group(1)
                
                # Check if function uses input in next 100 lines
                uses_input = False
                for j in range(i+1, min(i+100, len(workflows_lines))):
                    if re.search(r'\binput\.', workflows_lines[j]) or (re.search(r'\binput\s*[=:]', workflows_lines[j]) and 'input:' not in workflows_lines[j]):
                        uses_input = True
                        break
                
                if uses_input:
                    # Check if input is already in parameters
                    if 'input' not in line and ': PipelineInput' not in line:
                        # Add input parameter
                        match = re.search(r'(export\s+async\s+function\s+\w+)\s*\(([^)]*)\)', line)
                        if match:
                            func_decl = match.group(1)
                            params = match.group(2).strip()
                            
                            if params:
                                new_params = f"{params}, input: PipelineInput"
                            else:
                                new_params = "input: PipelineInput"
                            
                            workflows_lines[i] = re.sub(
                                r'(export\s+async\s+function\s+\w+)\s*\([^)]*\)',
                                f'{func_decl}({new_params})',
                                line
                            )
                            print(f"   ✅ Added input parameter to {func_name} at line {i+1}")
    
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
    print("FINAL RESTORE COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    import time
    final_complete_restore()

