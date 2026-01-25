#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Create node symlinks everywhere"""

import paramiko
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def create_symlinks():
    """Create node symlinks everywhere"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("CREATE NODE SYMLINKS EVERYWHERE")
    print("=" * 80)
    
    stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon | grep worker')
    worker = stdout.read().decode('utf-8', errors='replace')
    if not worker:
        print("Worker not running")
        ssh.close()
        return
    
    container_id = worker.split()[0]
    
    # Create symlinks in all possible locations
    print("\n1. Creating node symlinks in all possible locations...")
    
    locations = [
        '/usr/local/bin/node',
        '/usr/bin/node',
        '/bin/node',
        '/sbin/node',
        '/app/bin/node',
        '/tmp/node',
        '/opt/node',
        '/home/node',
    ]
    
    symlink_script = "#!/bin/sh\n"
    for loc in locations:
        symlink_script += f"mkdir -p $(dirname {loc}) 2>/dev/null || true\n"
        symlink_script += f"ln -sf /usr/bin/node {loc} 2>/dev/null || true\n"
    
    symlink_script += "echo 'Symlinks created'\n"
    symlink_script += "ls -la /usr/bin/node /usr/local/bin/node /bin/node /tmp/node 2>&1 || true\n"
    
    # Execute in container
    stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "{symlink_script}"')
    result = stdout.read().decode('utf-8', errors='replace')
    error = stderr.read().decode('utf-8', errors='replace')
    
    print(result)
    if error and 'No such file' not in error:
        print(f"   Errors: {error}")
    
    # Update PATH to include all locations
    print("\n2. Updating PATH to include all locations...")
    sftp = ssh.open_sftp()
    startup_script = """#!/bin/sh
set -e
# Set PATH with all possible node locations
export PATH="/usr/bin:/usr/local/bin:/bin:/sbin:/app/bin:/tmp:/opt:/home:$PATH"
export NODE="/usr/bin/node"
# Create symlinks
mkdir -p /usr/local/bin /bin /sbin /app/bin /tmp /opt /home 2>/dev/null || true
ln -sf /usr/bin/node /usr/local/bin/node 2>/dev/null || true
ln -sf /usr/bin/node /bin/node 2>/dev/null || true
ln -sf /usr/bin/node /sbin/node 2>/dev/null || true
ln -sf /usr/bin/node /app/bin/node 2>/dev/null || true
ln -sf /usr/bin/node /tmp/node 2>/dev/null || true
# Verify node is accessible
if ! command -v node >/dev/null 2>&1; then
    echo "ERROR: node not found in PATH: $PATH"
    ls -la /usr/bin/node /usr/local/bin/node /bin/node 2>&1 || true
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
    
    # Also update docker-compose entrypoint
    print("\n3. Updating docker-compose.yml entrypoint...")
    sftp = ssh.open_sftp()
    with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'r') as f:
        compose = f.read().decode('utf-8')
    
    # Update entrypoint to set PATH and create symlinks
    compose = compose.replace(
        '    entrypoint: ["/bin/sh", "-c", "export PATH=/usr/bin:/usr/local/bin:/bin:/usr/sbin:/sbin && export NODE=/usr/bin/node && cd /app && exec node dist/temporal/worker.js"]',
        '    entrypoint: ["/bin/sh", "-c", "export PATH=/usr/bin:/usr/local/bin:/bin:/sbin:/app/bin:/tmp:/opt:/home:$PATH && export NODE=/usr/bin/node && mkdir -p /usr/local/bin /bin /sbin /app/bin /tmp && ln -sf /usr/bin/node /usr/local/bin/node && ln -sf /usr/bin/node /bin/node && ln -sf /usr/bin/node /sbin/node && ln -sf /usr/bin/node /app/bin/node && ln -sf /usr/bin/node /tmp/node && cd /app && exec node dist/temporal/worker.js"]'
    )
    
    with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'w') as f:
        f.write(compose.encode('utf-8'))
    sftp.close()
    print("   ✅ docker-compose.yml updated")
    
    # Restart worker
    print("\n4. Restarting worker...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose stop worker && docker-compose rm -f worker && docker-compose up -d worker')
    print(stdout.read().decode('utf-8', errors='replace'))
    
    import time
    time.sleep(5)
    
    # Verify
    print("\n5. Verifying...")
    stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon | grep worker')
    worker_check = stdout.read().decode('utf-8', errors='replace')
    if worker_check:
        container_id = worker_check.split()[0]
        stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "which node && node --version && ls -la /usr/bin/node /usr/local/bin/node /bin/node /tmp/node 2>&1 | head -10"')
        verify = stdout.read().decode('utf-8', errors='replace')
        print(f"\n   Verification:\n{verify}")
        
        if 'v22' in verify:
            print("\n   ✅ Node accessible from multiple locations!")
            
            # Restart backend
            print("\n6. Restarting backend...")
            stdin, stdout, stderr = ssh.exec_command('pm2 restart xaker-backend')
            print(stdout.read().decode('utf-8', errors='replace'))
            
            print("\n" + "=" * 80)
            print("✅ SUCCESS!")
            print("=" * 80)
            print("\nNode symlinks created in:")
            print("  - /usr/bin/node")
            print("  - /usr/local/bin/node")
            print("  - /bin/node")
            print("  - /sbin/node")
            print("  - /app/bin/node")
            print("  - /tmp/node")
            print("\nPATH includes all these locations")
            print("Library should find node regardless of where it looks")
            print("\nTry a new pentest now!")
    
    ssh.close()

if __name__ == "__main__":
    import time
    create_symlinks()

