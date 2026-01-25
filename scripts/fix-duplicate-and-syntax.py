#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix duplicate input and syntax error"""

import paramiko
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def fix_duplicate_and_syntax():
    """Fix duplicate input and syntax error"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("FIXING DUPLICATE INPUT AND SYNTAX ERROR")
    print("=" * 80)
    
    sftp = ssh.open_sftp()
    
    # Read file
    with sftp.open('/opt/xaker/shannon/src/temporal/workflows.ts', 'r') as f:
        workflows = f.read().decode('utf-8')
    
    workflows_lines = workflows.split('\n')
    
    # Fix line 93-94: remove duplicate input
    print("\n   Lines 93-95:")
    for i in range(92, min(96, len(workflows_lines))):
        print(f"   {i+1:3d}: {workflows_lines[i]}")
    
    if workflows_lines[92].strip() == 'export async function pentestPipelineWorkflow(':
        if ', input: PipelineInput' in workflows_lines[93]:
            # Remove duplicate from line 94
            workflows_lines[93] = workflows_lines[93].replace(', input: PipelineInput', '')
            print("\n   ✅ Removed duplicate input parameter")
        elif 'input: PipelineInput' in workflows_lines[93]:
            # Move to line 93
            workflows_lines[92] = 'export async function pentestPipelineWorkflow(input: PipelineInput'
            workflows_lines[93] = workflows_lines[93].replace('input: PipelineInput', '').strip()
            if workflows_lines[93].startswith(','):
                workflows_lines[93] = workflows_lines[93][1:].strip()
            print("\n   ✅ Fixed function signature")
    
    # Fix line 242: remove extra colon
    print("\n   Line 242:")
    if 241 < len(workflows_lines):
        print(f"   Before: {workflows_lines[241]}")
        if workflows_lines[241].strip().startswith(': String'):
            workflows_lines[241] = '          String(result.reason);'
            print(f"   After:  {workflows_lines[241]}")
            print("   ✅ Fixed syntax error")
    
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
    fix_duplicate_and_syntax()

