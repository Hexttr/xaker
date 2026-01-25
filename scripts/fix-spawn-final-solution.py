#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Final solution: Create node wrapper in PATH"""

import paramiko
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def final_solution():
    """Final solution: Create node wrapper"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("FINAL SOLUTION: NODE WRAPPER IN PATH")
    print("=" * 80)
    
    # Find worker container
    stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon | grep worker')
    worker = stdout.read().decode('utf-8', errors='replace')
    if not worker:
        print("Worker not running")
        ssh.close()
        return
    
    container_id = worker.split()[0]
    print(f"Worker container: {container_id}")
    
    # Create node wrapper script in /usr/local/bin (which is in PATH)
    print("\n1. Creating node wrapper script...")
    wrapper_script = """#!/bin/sh
exec /usr/bin/node "$@"
"""
    
    # Write wrapper to container
    stdin, stdout, stderr = ssh.exec_command(f'docker exec -u root {container_id} sh -c "echo \'#!/bin/sh\nexec /usr/bin/node \"$@\"\' > /usr/local/bin/node && chmod +x /usr/local/bin/node"')
    result = stdout.read().decode('utf-8', errors='replace')
    error = stderr.read().decode('utf-8', errors='replace')
    
    if error and 'No such file' not in error:
        print(f"   ⚠️ Error: {error}")
    else:
        print("   ✅ Wrapper created")
        
        # Verify
        print("\n2. Verifying wrapper...")
        stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "which node && node --version && ls -la /usr/local/bin/node"')
        verify = stdout.read().decode('utf-8', errors='replace')
        print(verify)
        
        if 'v22' in verify:
            print("\n   ✅ Node wrapper is working!")
            
            # Also update startup script to ensure wrapper exists
            print("\n3. Updating startup script to create wrapper...")
            sftp = ssh.open_sftp()
            startup_script = """#!/bin/sh
set -e
# Set PATH explicitly
export PATH="/usr/bin:/usr/local/bin:/bin:/usr/sbin:/sbin"
export NODE="/usr/bin/node"
# Create node wrapper in /usr/local/bin (in PATH)
mkdir -p /usr/local/bin
echo '#!/bin/sh' > /usr/local/bin/node
echo 'exec /usr/bin/node "$@"' >> /usr/local/bin/node
chmod +x /usr/local/bin/node
# Create symlinks
ln -sf /usr/bin/node /usr/local/bin/node 2>/dev/null || true
ln -sf /usr/bin/node /bin/node 2>/dev/null || true
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
            
            # Restart worker
            print("\n4. Restarting worker...")
            stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose restart worker')
            print(stdout.read().decode('utf-8', errors='replace'))
            
            import time
            time.sleep(5)
            
            # Verify again
            stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon | grep worker')
            worker = stdout.read().decode('utf-8', errors='replace')
            if worker:
                container_id = worker.split()[0]
                stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "su pentest -c \'which node && node --version\'"')
                verify2 = stdout.read().decode('utf-8', errors='replace')
                print(f"\n   Final verification:\n{verify2}")
                
                if 'v22' in verify2:
                    print("\n   ✅ Node is accessible for pentest user!")
                    
                    # Restart backend
                    print("\n5. Restarting backend...")
                    stdin, stdout, stderr = ssh.exec_command('pm2 restart xaker-backend')
                    print(stdout.read().decode('utf-8', errors='replace'))
                    
                    print("\n" + "=" * 80)
                    print("✅ SUCCESS! Node wrapper created")
                    print("=" * 80)
                    print("\nThe wrapper script in /usr/local/bin/node will be found")
                    print("when spawn('node') is called, because /usr/local/bin is in PATH")
                    print("\nTry a new pentest now!")
                else:
                    print("\n   ⚠️ Node still not accessible for pentest user")
    
    ssh.close()

if __name__ == "__main__":
    import time
    final_solution()

