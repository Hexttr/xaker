#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Add missing command line"""

import paramiko
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def add_missing_command():
    """Add missing command"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("ADDING MISSING COMMAND LINE")
    print("=" * 80)
    
    sftp = ssh.open_sftp()
    
    # Read docker-compose.yml
    with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'r') as f:
        compose = f.read().decode('utf-8')
    
    compose_lines = compose.split('\n')
    
    # Find worker section and add command after entrypoint
    in_worker = False
    for i, line in enumerate(compose_lines):
        if 'worker:' in line:
            in_worker = True
        elif in_worker and 'entrypoint:' in line:
            # Check if next line is command or environment
            if i+1 < len(compose_lines):
                next_line = compose_lines[i+1]
                if 'command:' not in next_line and 'environment:' not in next_line:
                    # Insert command line
                    compose_lines.insert(i+1, '    command: "mkdir -p /usr/local/bin && ln -sf /usr/bin/node /usr/local/bin/node 2>/dev/null || true && exec node dist/temporal/worker.js"')
                    print(f"   ✅ Added command line after entrypoint at line {i+2}")
                    break
                elif 'environment:' in next_line:
                    # Insert command before environment
                    compose_lines.insert(i+1, '    command: "mkdir -p /usr/local/bin && ln -sf /usr/bin/node /usr/local/bin/node 2>/dev/null || true && exec node dist/temporal/worker.js"')
                    print(f"   ✅ Added command line before environment at line {i+2}")
                    break
        elif in_worker and line.strip() and not line.startswith(' ') and not line.startswith('\t'):
            # End of worker section
            break
    
    compose = '\n'.join(compose_lines)
    
    # Write back
    with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'w') as f:
        f.write(compose.encode('utf-8'))
    
    sftp.close()
    
    # Show what we wrote
    print("\n   Updated docker-compose.yml worker section:")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && cat docker-compose.yml | grep -A 6 worker:')
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
    add_missing_command()

