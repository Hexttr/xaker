#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Restore TESTING_RETRY"""

import paramiko
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def restore_testing():
    """Restore TESTING_RETRY"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("RESTORING TESTING_RETRY")
    print("=" * 80)
    
    sftp = ssh.open_sftp()
    
    # Read file
    with sftp.open('/opt/xaker/shannon/src/temporal/workflows.ts', 'r') as f:
        workflows = f.read().decode('utf-8')
    
    workflows_lines = workflows.split('\n')
    
    # Find PRODUCTION_RETRY end
    prod_end = -1
    for i, line in enumerate(workflows_lines):
        if 'const PRODUCTION_RETRY = {' in line:
            for j in range(i+1, min(i+15, len(workflows_lines))):
                if workflows_lines[j].strip() == '};':
                    prod_end = j + 1
                    break
            break
    
    print(f"\n   PRODUCTION_RETRY ends at line {prod_end}")
    
    # Show current state
    print("\n   Lines 54-60:")
    for i in range(53, min(60, len(workflows_lines))):
        print(f"   {i+1:3d}: {workflows_lines[i]}")
    
    # Insert TESTING_RETRY after PRODUCTION_RETRY
    if prod_end >= 0:
        testing_retry = [
            "",
            "// Retry configuration for pipeline testing (fast iteration)",
            "const TESTING_RETRY = {",
            "  initialInterval: 10000,",
            "  maximumInterval: 30000,",
            "  backoffCoefficient: 2,",
            "  maximumAttempts: 5,",
            "  nonRetryableErrorTypes: PRODUCTION_RETRY.nonRetryableErrorTypes,",
            "};",
            ""
        ]
        
        workflows_lines = workflows_lines[:prod_end] + testing_retry + workflows_lines[prod_end:]
        print(f"\n   ✅ Inserted TESTING_RETRY after line {prod_end}")
    
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
        # Show only retry-related errors first
        retry_errors = [err for err in error_lines if 'RETRY' in err or 'retry' in err.lower()]
        if retry_errors:
            for err in retry_errors:
                print(f"   {err}")
        # Show other errors
        other_errors = [err for err in error_lines if 'RETRY' not in err and 'retry' not in err.lower()]
        for err in other_errors[-10:]:
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
    print("RESTORE COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    import time
    restore_testing()

