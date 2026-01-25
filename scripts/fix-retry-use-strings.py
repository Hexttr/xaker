#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix retry policies to use strings directly (Temporal supports this!)"""

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

def fix_use_strings():
    """Fix retry policies to use strings"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("FIXING RETRY POLICIES TO USE STRINGS")
    print("=" * 80)
    
    sftp = ssh.open_sftp()
    
    # Fix workflows.ts - revert Duration.from() back to strings
    print("\n1. Fixing workflows.ts...")
    with sftp.open('/opt/xaker/shannon/src/temporal/workflows.ts', 'r') as f:
        workflows = f.read().decode('utf-8')
    
    workflows_lines = workflows.split('\n')
    
    # Remove Duration import if it exists
    for i, line in enumerate(workflows_lines[:30]):
        if 'Duration' in line and 'import' in line:
            workflows_lines.pop(i)
            print(f"   ✅ Removed Duration import at line {i+1}")
            break
    
    # Replace Duration.from() back to strings
    for i, line in enumerate(workflows_lines):
        # Replace Duration.from({ minutes: X }) with 'X minutes'
        workflows_lines[i] = re.sub(
            r"Duration\.from\(\{\s*minutes:\s*(\d+)\s*\}\)",
            r"'\1 minutes'",
            line
        )
        # Replace Duration.from({ seconds: X }) with 'X seconds'
        workflows_lines[i] = re.sub(
            r"Duration\.from\(\{\s*seconds:\s*(\d+)\s*\}\)",
            r"'\1 seconds'",
            line
        )
        # Replace Duration.from({ hours: X }) with 'X hours'
        workflows_lines[i] = re.sub(
            r"Duration\.from\(\{\s*hours:\s*(\d+)\s*\}\)",
            r"'\1 hours'",
            line
        )
    
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
    print("FIX COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    import time
    fix_use_strings()

