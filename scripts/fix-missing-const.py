#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix missing const declarations"""

import paramiko
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def fix_missing_const():
    """Fix missing const declarations"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("FIXING MISSING CONST DECLARATIONS")
    print("=" * 80)
    
    sftp = ssh.open_sftp()
    
    # Read file
    with sftp.open('/opt/xaker/shannon/src/temporal/workflows.ts', 'r') as f:
        workflows = f.read().decode('utf-8')
    
    workflows_lines = workflows.split('\n')
    
    # Fix line 44-45: add const PRODUCTION_RETRY = {
    if workflows_lines[44].strip() == '// Retry configuration for production (long intervals for billing recovery)':
        if workflows_lines[45].strip().startswith('initialInterval:'):
            # Insert const declaration
            workflows_lines.insert(45, "const PRODUCTION_RETRY = {")
            print("   ✅ Added const PRODUCTION_RETRY = {")
    
    # Fix line 47: remove duplicate and broken line
    for i in range(45, min(50, len(workflows_lines))):
        if 'maximumInterval: Duration.fromMilliseconds(1800000,' in workflows_lines[i]:
            workflows_lines.pop(i)
            print(f"   ✅ Removed broken duplicate line {i+1}")
            break
    
    # Fix line 61-62: add const TESTING_RETRY = {
    for i, line in enumerate(workflows_lines):
        if 'Retry configuration for pipeline testing' in line:
            if i+1 < len(workflows_lines) and workflows_lines[i+1].strip().startswith('initialInterval:'):
                workflows_lines.insert(i+1, "const TESTING_RETRY = {")
                print(f"   ✅ Added const TESTING_RETRY = {{ at line {i+2}")
            break
    
    # Remove broken duplicate maximumInterval lines
    for i, line in enumerate(workflows_lines):
        if 'maximumInterval: Duration.fromMilliseconds(30000,' in line:
            workflows_lines.pop(i)
            print(f"   ✅ Removed broken duplicate line {i+1}")
            break
    
    # Remove Duration import if exists (we're using numbers)
    for i, line in enumerate(workflows_lines[:30]):
        if 'Duration' in line and 'import' in line:
            workflows_lines.pop(i)
            print(f"   ✅ Removed Duration import")
            break
    
    # Write back
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
    fix_missing_const()

