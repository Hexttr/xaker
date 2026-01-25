#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix function signature precisely"""

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

def fix_signature_precise():
    """Fix function signature precisely"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("FIXING FUNCTION SIGNATURE PRECISELY")
    print("=" * 80)
    
    sftp = ssh.open_sftp()
    
    # Read file
    with sftp.open('/opt/xaker/shannon/src/temporal/workflows.ts', 'r') as f:
        workflows = f.read().decode('utf-8')
    
    workflows_lines = workflows.split('\n')
    
    # Show function at line 93
    print("\n   Function at line 93:")
    for i in range(92, min(100, len(workflows_lines))):
        print(f"   {i+1:3d}: {workflows_lines[i]}")
    
    # Find pentestPipelineWorkflow function
    for i, line in enumerate(workflows_lines):
        if 'function pentestPipelineWorkflow' in line:
            print(f"\n   Found function at line {i+1}: {line}")
            
            # Check if it's multi-line
            if '(' in line and ')' not in line:
                # Multi-line function signature
                # Find closing parenthesis
                sig_lines = [line]
                for j in range(i+1, min(i+10, len(workflows_lines))):
                    sig_lines.append(workflows_lines[j])
                    if ')' in workflows_lines[j]:
                        break
                
                # Check if input is in signature
                full_sig = ' '.join(sig_lines)
                if 'input' not in full_sig:
                    # Add input parameter before closing parenthesis
                    for j in range(len(sig_lines)-1, -1, -1):
                        if ')' in sig_lines[j]:
                            # Insert before closing parenthesis
                            if sig_lines[j].strip() == ')':
                                sig_lines.insert(j, "  input: PipelineInput,")
                            else:
                                sig_lines[j] = sig_lines[j].replace(')', ', input: PipelineInput)')
                            break
                    
                    # Replace lines
                    workflows_lines[i:i+len(sig_lines)] = sig_lines
                    print(f"   ✅ Added input parameter to multi-line function")
                    break
            else:
                # Single-line function signature
                if 'input' not in line:
                    # Add input parameter
                    if '(' in line and ')' in line:
                        # Extract parameters
                        match = re.search(r'\(([^)]*)\)', line)
                        if match:
                            params = match.group(1).strip()
                            if params:
                                new_params = f"{params}, input: PipelineInput"
                            else:
                                new_params = "input: PipelineInput"
                            
                            workflows_lines[i] = re.sub(
                                r'\([^)]*\)',
                                f'({new_params})',
                                line
                            )
                            print(f"   ✅ Added input parameter to single-line function")
                            print(f"      After: {workflows_lines[i][:100]}")
                            break
    
    # Write back
    print("\n2. Writing fixed file...")
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
        
        # Build Docker
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
                
                # Restart backend
                print("\n7. Restarting backend...")
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
    fix_signature_precise()

