#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix entrypoint correctly"""

import paramiko
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def fix_entrypoint_correct():
    """Fix entrypoint correctly"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("FIXING ENTRYPOINT CORRECTLY")
    print("=" * 80)
    
    sftp = ssh.open_sftp()
    
    # Read docker-compose.yml
    with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'r') as f:
        compose = f.read().decode('utf-8')
    
    # The correct format for docker-compose with entrypoint ["/bin/sh", "-c"] is:
    # entrypoint: ["/bin/sh", "-c"]
    # command: "your command here"
    # But the command should be a single string, not an array
    
    # Fix: ensure command is a proper string
    compose_lines = compose.split('\n')
    in_worker = False
    for i, line in enumerate(compose_lines):
        if 'worker:' in line:
            in_worker = True
        elif in_worker and line.strip() and not line.startswith(' ') and not line.startswith('\t') and ':' in line:
            # End of worker section
            break
        elif in_worker and 'entrypoint:' in line:
            # Ensure entrypoint is correct
            compose_lines[i] = '    entrypoint: ["/bin/sh", "-c"]'
        elif in_worker and 'command:' in line:
            # Ensure command is a single string
            if '[' in line or ']' in line:
                # It's an array, convert to string
                compose_lines[i] = '    command: "mkdir -p /usr/local/bin && ln -sf /usr/bin/node /usr/local/bin/node 2>/dev/null || true && exec node dist/temporal/worker.js"'
            elif '"' not in line and "'" not in line:
                # It's not a string, make it a string
                compose_lines[i] = '    command: "mkdir -p /usr/local/bin && ln -sf /usr/bin/node /usr/local/bin/node 2>/dev/null || true && exec node dist/temporal/worker.js"'
            else:
                # It's already a string, but check if it's correct
                if 'dist/temporal/worker.js' not in line:
                    compose_lines[i] = '    command: "mkdir -p /usr/local/bin && ln -sf /usr/bin/node /usr/local/bin/node 2>/dev/null || true && exec node dist/temporal/worker.js"'
    
    compose = '\n'.join(compose_lines)
    
    # Write back
    with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'w') as f:
        f.write(compose.encode('utf-8'))
    
    sftp.close()
    
    # Show what we wrote
    print("\n   Updated docker-compose.yml worker section:")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && cat docker-compose.yml | grep -A 5 worker:')
    print(stdout.read().decode('utf-8', errors='replace'))
    
    # Restart worker
    print("\n2. Restarting worker...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose stop worker && docker-compose rm -f worker && docker-compose up -d worker')
    restart_output = stdout.read().decode('utf-8', errors='replace')
    print(restart_output)
    
    import time
    time.sleep(5)
    
    # Check worker
    print("\n3. Checking worker...")
    stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon | grep worker')
    worker = stdout.read().decode('utf-8', errors='replace')
    if worker:
        container_id = worker.split()[0]
        print(f"   ✅ Worker is running: {container_id}")
        
        stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "ls -la /usr/local/bin/node && which node && /usr/local/bin/node --version && printenv NODE"')
        verify = stdout.read().decode('utf-8', errors='replace')
        print(verify)
        
        # Check logs
        stdin, stdout, stderr = ssh.exec_command(f'docker logs {container_id} --tail=15 2>&1')
        logs = stdout.read().decode('utf-8', errors='replace')
        print(f"\n   Worker logs:\n{logs[-500:]}")
        
        # Restart backend
        print("\n4. Restarting backend...")
        stdin, stdout, stderr = ssh.exec_command('pm2 restart xaker-backend')
        print(stdout.read().decode('utf-8', errors='replace'))
        
        print("\n✅ SUCCESS! Everything is running")
        print("Try a new pentest now!")
    else:
        print("   ⚠️  Worker still not running")
        # Try to run command manually to see what happens
        print("\n   Trying to run command manually...")
        stdin, stdout, stderr = ssh.exec_command('docker run --rm shannon_worker:latest /bin/sh -c "mkdir -p /usr/local/bin && ln -sf /usr/bin/node /usr/local/bin/node && which node && node --version"')
        manual_test = stdout.read().decode('utf-8', errors='replace')
        print(manual_test)
        
        # Check logs
        stdin, stdout, stderr = ssh.exec_command('docker ps -a | grep shannon | grep worker | head -1')
        worker_line = stdout.read().decode('utf-8', errors='replace')
        if worker_line:
            container_id = worker_line.split()[0]
            stdin, stdout, stderr = ssh.exec_command(f'docker logs {container_id} 2>&1 | tail -30')
            print(stdout.read().decode('utf-8', errors='replace'))
    
    ssh.close()
    
    print("\n" + "=" * 80)
    print("FIX COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    import time
    fix_entrypoint_correct()

