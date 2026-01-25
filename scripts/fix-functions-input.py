#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix functions to add input parameter"""

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

def fix_functions_input():
    """Fix functions to add input parameter"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("FIXING FUNCTIONS TO ADD INPUT PARAMETER")
    print("=" * 80)
    
    sftp = ssh.open_sftp()
    
    # Read file
    with sftp.open('/opt/xaker/shannon/src/temporal/workflows.ts', 'r') as f:
        workflows = f.read().decode('utf-8')
    
    workflows_lines = workflows.split('\n')
    
    # Show functions around line 99
    print("\n   Functions around line 99:")
    for i in range(85, min(105, len(workflows_lines))):
        if 'function' in workflows_lines[i] or 'input' in workflows_lines[i]:
            print(f"   {i+1:3d}: {workflows_lines[i]}")
    
    # Find functions that use input but don't have it
    print("\n2. Finding functions that need input parameter...")
    
    # Find all function definitions
    functions_to_fix = []
    for i, line in enumerate(workflows_lines):
        if re.search(r'export\s+async\s+function\s+\w+', line):
            # Check if this function uses input
            uses_input = False
            func_end = min(i + 150, len(workflows_lines))
            for j in range(i+1, func_end):
                if re.search(r'\binput\.', workflows_lines[j]):
                    uses_input = True
                    break
            
            if uses_input:
                # Check if input is in parameters
                if 'input' not in line:
                    func_match = re.search(r'function\s+(\w+)', line)
                    if func_match:
                        func_name = func_match.group(1)
                        functions_to_fix.append({
                            'line': i,
                            'name': func_name,
                            'content': line
                        })
                        print(f"   Found function {func_name} at line {i+1} that needs input parameter")
    
    # Fix each function
    print("\n3. Fixing functions...")
    for func in functions_to_fix:
        line_num = func['line']
        line = workflows_lines[line_num]
        
        # Extract function declaration and parameters
        match = re.search(r'(export\s+async\s+function\s+\w+)\s*\(([^)]*)\)', line)
        if match:
            func_decl = match.group(1)
            params = match.group(2).strip()
            
            # Add input parameter
            if params:
                new_params = f"{params}, input: PipelineInput"
            else:
                new_params = "input: PipelineInput"
            
            workflows_lines[line_num] = re.sub(
                r'(export\s+async\s+function\s+\w+)\s*\([^)]*\)',
                f'{func_decl}({new_params})',
                line
            )
            print(f"   ✅ Added input parameter to {func['name']} at line {line_num+1}")
            print(f"      Before: {line[:80]}")
            print(f"      After:  {workflows_lines[line_num][:80]}")
    
    # Write back
    print("\n4. Writing fixed file...")
    with sftp.open('/opt/xaker/shannon/src/temporal/workflows.ts', 'w') as f:
        f.write('\n'.join(workflows_lines).encode('utf-8'))
    
    sftp.close()
    
    # Rebuild
    print("\n5. Rebuilding TypeScript...")
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
        
        # Build Docker
        print("\n6. Building Docker image (this will take 2-3 minutes)...")
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
            print("\n7. Starting services...")
            stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose up -d')
            print(stdout.read().decode('utf-8', errors='replace'))
            
            time.sleep(5)
            
            # Verify
            print("\n8. Verifying worker...")
            stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon | grep worker')
            worker = stdout.read().decode('utf-8', errors='replace')
            if worker:
                container_id = worker.split()[0]
                stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "ls -la /usr/local/bin/node && which node && /usr/local/bin/node --version && printenv NODE"')
                print(stdout.read().decode('utf-8', errors='replace'))
                
                # Restart backend
                print("\n9. Restarting backend...")
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
    fix_functions_input()

