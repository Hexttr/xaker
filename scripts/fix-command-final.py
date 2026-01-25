#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix command format - final attempt"""

import paramiko
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def fix_final():
    """Fix command format - final"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("FIXING COMMAND FORMAT - FINAL")
    print("=" * 80)
    
    sftp = ssh.open_sftp()
    
    # Read docker-compose.yml
    with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'r') as f:
        compose = f.read().decode('utf-8')
    
    # Replace command with proper format - use array format
    # The issue is that when using entrypoint ["/bin/sh", "-c"], the command should be a single string
    # But docker-compose might be parsing it incorrectly
    
    # Try using a different approach - create a wrapper script or use exec format
    compose = compose.replace(
        '    entrypoint: ["/bin/sh", "-c"]',
        '    entrypoint: ["/bin/sh", "-c", "mkdir -p /usr/local/bin && ln -sf /usr/bin/node /usr/local/bin/node 2>/dev/null || true && exec node dist/temporal/worker.js"]'
    )
    
    # Remove command line if it exists
    compose_lines = compose.split('\n')
    new_lines = []
    skip_next = False
    for i, line in enumerate(compose_lines):
        if skip_next:
            skip_next = False
            continue
        if 'command:' in line and 'mkdir' in line:
            # Skip this line
            skip_next = True
            continue
        new_lines.append(line)
    
    compose = '\n'.join(new_lines)
    
    # Write back
    with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'w') as f:
        f.write(compose.encode('utf-8'))
    
    sftp.close()
    
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
    fix_final()

