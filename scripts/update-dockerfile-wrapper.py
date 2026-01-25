#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Update Dockerfile to create wrapper script instead of symlink"""

import paramiko
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def update_dockerfile():
    """Update Dockerfile"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("UPDATING DOCKERFILE TO CREATE WRAPPER SCRIPT")
    print("=" * 80)
    
    sftp = ssh.open_sftp()
    
    # Read Dockerfile
    with sftp.open('/opt/xaker/shannon/Dockerfile', 'r') as f:
        dockerfile = f.read().decode('utf-8')
    
    dockerfile_lines = dockerfile.split('\n')
    
    # Find lines that create symlink and replace with wrapper script
    for i, line in enumerate(dockerfile_lines):
        if 'ln -sf /usr/bin/node /usr/local/bin/node' in line:
            # Replace with wrapper script creation
            dockerfile_lines[i] = 'RUN mkdir -p /usr/local/bin && echo "#!/bin/sh" > /usr/local/bin/node && echo "exec /usr/bin/node \\"$@\\"" >> /usr/local/bin/node && chmod +x /usr/local/bin/node'
            print(f"   ✅ Replaced symlink with wrapper script at line {i+1}")
    
    dockerfile = '\n'.join(dockerfile_lines)
    
    # Write back
    with sftp.open('/opt/xaker/shannon/Dockerfile', 'w') as f:
        f.write(dockerfile.encode('utf-8'))
    
    sftp.close()
    
    # Update startup script too
    print("\n2. Updating startup script...")
    sftp = ssh.open_sftp()
    startup_script = """#!/bin/sh
set -e
# Set PATH explicitly
export PATH="/usr/bin:/usr/local/bin:/bin:/usr/sbin:/sbin"
export NODE="/usr/bin/node"
# Create node wrapper script in /usr/local/bin (in PATH)
mkdir -p /usr/local/bin
if [ ! -f /usr/local/bin/node ] || [ -L /usr/local/bin/node ]; then
    rm -f /usr/local/bin/node
    echo '#!/bin/sh' > /usr/local/bin/node
    echo 'exec /usr/bin/node "$@"' >> /usr/local/bin/node
    chmod +x /usr/local/bin/node
fi
# Verify node is accessible
if ! command -v node >/dev/null 2>&1; then
    echo "ERROR: node not found in PATH: $PATH"
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
    
    print("\n3. Rebuilding Docker image (this will take 2-3 minutes)...")
    print("   This is the FINAL fix - wrapper script will be created in Dockerfile")
    
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && timeout 300 docker-compose build --no-cache worker 2>&1 | tail -30')
    
    import time
    start = time.time()
    output = ""
    while time.time() - start < 240:
        chunk = stdout.read(1024).decode('utf-8', errors='replace')
        if chunk:
            output += chunk
            if len(output) > 500:
                print(output[-500:], end='', flush=True)
                output = output[-500:]
        else:
            time.sleep(2)
            if stdout.channel.exit_status_ready():
                break
    
    remaining = stdout.read(50000).decode('utf-8', errors='replace')
    print(remaining[-1000:])
    
    if 'Successfully' in output or 'Successfully' in remaining:
        print("\n✅ Docker build successful!")
        
        # Restart worker
        print("\n4. Restarting worker...")
        stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose stop worker && docker-compose rm -f worker && docker-compose up -d worker')
        print(stdout.read().decode('utf-8', errors='replace'))
        
        time.sleep(5)
        
        # Verify
        print("\n5. Verifying...")
        stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon | grep worker')
        worker = stdout.read().decode('utf-8', errors='replace')
        if worker:
            container_id = worker.split()[0]
            stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "su pentest -c \'which node && node --version && ls -la /usr/local/bin/node\'"')
            verify = stdout.read().decode('utf-8', errors='replace')
            print(verify)
            
            if 'v22' in verify and 'exec' in verify:
                print("\n✅ Node wrapper is working!")
                
                # Restart backend
                print("\n6. Restarting backend...")
                stdin, stdout, stderr = ssh.exec_command('pm2 restart xaker-backend')
                print(stdout.read().decode('utf-8', errors='replace'))
                
                print("\n" + "=" * 80)
                print("✅ SUCCESS! FINAL FIX APPLIED")
                print("=" * 80)
                print("\nNode wrapper script is now created in Dockerfile")
                print("When spawn('node') is called, it will find /usr/local/bin/node")
                print("which is a wrapper script that executes /usr/bin/node")
                print("\nTry a new pentest now!")
    
    ssh.close()

if __name__ == "__main__":
    import time
    update_dockerfile()

