#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Set NODE environment variable in docker-compose"""

import paramiko
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def set_node_env():
    """Set NODE env variable"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("SETTING NODE ENVIRONMENT VARIABLE")
    print("=" * 80)
    
    # Read docker-compose.yml
    print("\n1. Reading docker-compose.yml...")
    sftp = ssh.open_sftp()
    with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'r') as f:
        compose = f.read().decode('utf-8')
    
    # Check if NODE is already set
    if 'NODE=/usr/bin/node' in compose:
        print("   ✅ NODE already set")
    else:
        # Add NODE to environment
        print("\n2. Adding NODE to environment...")
        compose_lines = compose.split('\n')
        
        # Find worker service and add NODE
        in_worker = False
        in_env = False
        for i, line in enumerate(compose_lines):
            if 'worker:' in line:
                in_worker = True
            if in_worker and 'environment:' in line:
                in_env = True
            if in_worker and in_env:
                # Check if NODE already exists
                if 'NODE=' in line:
                    print("   NODE already in environment")
                    break
                # Add NODE after TEMPORAL_ADDRESS or at end of environment section
                if 'TEMPORAL_ADDRESS' in line:
                    compose_lines.insert(i+1, "            - NODE=/usr/bin/node")
                    print("   ✅ Added NODE after TEMPORAL_ADDRESS")
                    break
                # If we hit another service or top-level key, add before
                if line.strip() and not line.startswith(' ') and not line.startswith('-'):
                    compose_lines.insert(i, "            - NODE=/usr/bin/node")
                    print("   ✅ Added NODE at end of environment")
                    break
        
        compose = '\n'.join(compose_lines)
        
        # Write back
        with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'w') as f:
            f.write(compose.encode('utf-8'))
        sftp.close()
        
        print("   ✅ docker-compose.yml updated")
    
    # Also update startup script to export NODE
    print("\n3. Updating startup script to export NODE...")
    sftp = ssh.open_sftp()
    startup_script = """#!/bin/sh
set -e
# Set PATH explicitly
export PATH="/tmp:/app/bin:/usr/bin:/usr/local/bin:/bin:/usr/sbin:/sbin"
export NODE="/usr/bin/node"
# Create node wrapper in /tmp (writable by pentest user)
mkdir -p /tmp
echo '#!/bin/sh' > /tmp/node
echo 'exec /usr/bin/node "$@"' >> /tmp/node
chmod +x /tmp/node
# Verify node is accessible
if ! command -v node >/dev/null 2>&1; then
    echo "ERROR: node not found in PATH: $PATH"
    ls -la /usr/bin/node /tmp/node 2>&1 || true
    exit 1
fi
# Start worker
exec node dist/temporal/worker.js
"""
    
    with sftp.open('/opt/xaker/shannon/start-worker.sh', 'w') as f:
        f.write(startup_script.encode('utf-8'))
    sftp.close()
    ssh.exec_command('chmod +x /opt/xaker/shannon/start-worker.sh')
    print("   ✅ Startup script updated")
    
    # Restart worker
    print("\n4. Restarting worker...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose stop worker && docker-compose rm -f worker && docker-compose up -d worker')
    print(stdout.read().decode('utf-8', errors='replace'))
    
    import time
    time.sleep(5)
    
    # Verify
    print("\n5. Verifying NODE env variable...")
    stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon | grep worker')
    worker = stdout.read().decode('utf-8', errors='replace')
    if worker:
        container_id = worker.split()[0]
        stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "printenv NODE"')
        node_env = stdout.read().decode('utf-8', errors='replace').strip()
        print(f"   NODE env: {node_env}")
        
        stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "su pentest -c \'printenv NODE && which node && node --version\'"')
        verify = stdout.read().decode('utf-8', errors='replace')
        print(f"\n   Verification:\n{verify}")
        
        if '/usr/bin/node' in node_env and 'v22' in verify:
            print("\n   ✅ NODE env variable set!")
            
            # Restart backend
            print("\n6. Restarting backend...")
            stdin, stdout, stderr = ssh.exec_command('pm2 restart xaker-backend')
            print(stdout.read().decode('utf-8', errors='replace'))
            
            print("\n" + "=" * 80)
            print("✅ SUCCESS!")
            print("=" * 80)
            print("\nNODE=/usr/bin/node is set in environment")
            print("If library supports process.env.NODE, it will use it")
            print("Otherwise, wrapper in /tmp/node will be found via PATH")
            print("\nTry a new pentest now!")
    
    ssh.close()

if __name__ == "__main__":
    import time
    set_node_env()

