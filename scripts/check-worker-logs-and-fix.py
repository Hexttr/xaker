#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check worker logs and fix"""

import paramiko
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def check_logs_and_fix():
    """Check logs and fix"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("CHECKING WORKER LOGS AND FIXING")
    print("=" * 80)
    
    # Check worker logs
    print("\n1. Checking worker logs...")
    stdin, stdout, stderr = ssh.exec_command('docker ps -a | grep shannon | grep worker | head -1')
    worker_line = stdout.read().decode('utf-8', errors='replace')
    
    if worker_line:
        container_id = worker_line.split()[0]
        print(f"   Worker container: {container_id}")
        
        stdin, stdout, stderr = ssh.exec_command(f'docker logs {container_id} 2>&1')
        logs = stdout.read().decode('utf-8', errors='replace')
        print(f"\n   Worker logs:\n{logs[-2000:]}")
        
        # Check entrypoint
        print("\n2. Checking entrypoint...")
        stdin, stdout, stderr = ssh.exec_command(f'docker inspect {container_id} | grep -A 5 Entrypoint')
        entrypoint = stdout.read().decode('utf-8', errors='replace')
        print(entrypoint)
        
        # Check if entrypoint is correct
        if 'dist/temporal/worker.js' not in logs and 'dist/shannon.js' not in logs:
            print("\n3. Entrypoint might be wrong, checking docker-compose.yml...")
            stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && grep -A 3 "entrypoint:" docker-compose.yml')
            compose_entrypoint = stdout.read().decode('utf-8', errors='replace')
            print(compose_entrypoint)
            
            # Fix entrypoint if needed
            if 'dist/shannon.js' in compose_entrypoint:
                print("\n   ⚠️  Entrypoint points to dist/shannon.js, but should be dist/temporal/worker.js")
                # Fix docker-compose.yml
                sftp = ssh.open_sftp()
                with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'r') as f:
                    compose = f.read().decode('utf-8')
                
                # Fix entrypoint
                compose = compose.replace(
                    'ENTRYPOINT ["node", "dist/shannon.js"]',
                    'ENTRYPOINT ["/bin/sh", "-c"]'
                )
                compose = compose.replace(
                    'entrypoint: ["node", "dist/shannon.js"]',
                    'entrypoint: ["/bin/sh", "-c"]'
                )
                
                # Ensure command is correct
                if 'command:' in compose and 'dist/temporal/worker.js' not in compose:
                    compose = compose.replace(
                        'command:',
                        'command: "mkdir -p /usr/local/bin && ln -sf /usr/bin/node /usr/local/bin/node 2>/dev/null || true && exec node dist/temporal/worker.js"'
                    )
                
                with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'w') as f:
                    f.write(compose.encode('utf-8'))
                
                sftp.close()
                print("   ✅ Fixed docker-compose.yml")
                
                # Restart worker
                print("\n4. Restarting worker...")
                stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose up -d worker')
                print(stdout.read().decode('utf-8', errors='replace'))
                
                time.sleep(5)
                
                # Check again
                stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon | grep worker')
                worker = stdout.read().decode('utf-8', errors='replace')
                if worker:
                    container_id = worker.split()[0]
                    stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "ls -la /usr/local/bin/node && which node && /usr/local/bin/node --version"')
                    print(stdout.read().decode('utf-8', errors='replace'))
                    print("\n   ✅ Worker is running!")
    
    ssh.close()
    
    print("\n" + "=" * 80)
    print("CHECK COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    import time
    check_logs_and_fix()

