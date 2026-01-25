#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test command execution"""

import paramiko
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def test_command():
    """Test command execution"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("TESTING COMMAND EXECUTION")
    print("=" * 80)
    
    # Test command manually in a container
    print("\n1. Testing command in a container...")
    stdin, stdout, stderr = ssh.exec_command('docker run --rm shannon_worker:latest /bin/sh -c "mkdir -p /usr/local/bin && ln -sf /usr/bin/node /usr/local/bin/node && which node && node --version && ls -la /usr/local/bin/node"')
    test_output = stdout.read().decode('utf-8', errors='replace')
    print(test_output)
    
    # The issue might be that docker-compose is passing command incorrectly
    # Let's check what docker-compose actually runs
    print("\n2. Checking what docker-compose runs...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose config | grep -A 10 worker:')
    config_output = stdout.read().decode('utf-8', errors='replace')
    print(config_output)
    
    # Try using a different approach - create a startup script
    print("\n3. Creating startup script...")
    startup_script = """#!/bin/sh
set -e
mkdir -p /usr/local/bin
ln -sf /usr/bin/node /usr/local/bin/node 2>/dev/null || true
exec node dist/temporal/worker.js
"""
    
    sftp = ssh.open_sftp()
    with sftp.open('/opt/xaker/shannon/start-worker.sh', 'w') as f:
        f.write(startup_script.encode('utf-8'))
    
    # Make it executable
    ssh.exec_command('chmod +x /opt/xaker/shannon/start-worker.sh')
    
    # Update docker-compose to use the script
    with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'r') as f:
        compose = f.read().decode('utf-8')
    
    # Replace entrypoint and command with script
    compose = compose.replace(
        '    entrypoint: ["/bin/sh", "-c"]',
        '    entrypoint: ["/bin/sh", "/app/start-worker.sh"]'
    )
    compose = compose.replace(
        '    command: "mkdir -p /usr/local/bin && ln -sf /usr/bin/node /usr/local/bin/node 2>/dev/null || true && exec node dist/temporal/worker.js"',
        ''
    )
    
    # Also need to mount the script
    if 'volumes:' not in compose or './start-worker.sh:/app/start-worker.sh' not in compose:
        # Add volume mount for script
        compose_lines = compose.split('\n')
        for i, line in enumerate(compose_lines):
            if 'worker:' in line:
                # Find volumes section
                for j in range(i+1, min(i+30, len(compose_lines))):
                    if 'volumes:' in compose_lines[j]:
                        # Add script mount
                        compose_lines.insert(j+1, '      - ./start-worker.sh:/app/start-worker.sh:ro')
                        print("   ✅ Added script volume mount")
                        break
                break
        
        compose = '\n'.join(compose_lines)
    
    with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'w') as f:
        f.write(compose.encode('utf-8'))
    
    sftp.close()
    
    # Restart worker
    print("\n4. Restarting worker with script...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose stop worker && docker-compose rm -f worker && docker-compose up -d worker')
    restart_output = stdout.read().decode('utf-8', errors='replace')
    print(restart_output)
    
    import time
    time.sleep(5)
    
    # Check worker
    print("\n5. Checking worker...")
    stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon | grep worker')
    worker = stdout.read().decode('utf-8', errors='replace')
    if worker:
        container_id = worker.split()[0]
        print(f"   ✅ Worker is running: {container_id}")
        
        stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "ls -la /usr/local/bin/node && which node && /usr/local/bin/node --version"')
        verify = stdout.read().decode('utf-8', errors='replace')
        print(verify)
        
        # Check logs
        stdin, stdout, stderr = ssh.exec_command(f'docker logs {container_id} --tail=15 2>&1')
        logs = stdout.read().decode('utf-8', errors='replace')
        print(f"\n   Worker logs:\n{logs[-500:]}")
        
        # Restart backend
        print("\n6. Restarting backend...")
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
    print("TEST COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    import time
    test_command()

