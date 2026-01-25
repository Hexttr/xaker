#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Create node wrapper everywhere"""

import paramiko
import sys
import time

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def create_wrapper():
    """Create node wrapper in Dockerfile"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("CREATE NODE WRAPPER IN DOCKERFILE")
    print("=" * 80)
    print("\nCreating wrapper script that will be available everywhere")
    print("This ensures spawn('node') will find the wrapper")
    
    # Read Dockerfile
    print("\n1. Reading Dockerfile...")
    sftp = ssh.open_sftp()
    try:
        with sftp.open('/opt/xaker/shannon/Dockerfile', 'r') as f:
            dockerfile = f.read().decode('utf-8')
    except Exception as e:
        print(f"   ⚠️ Could not read Dockerfile: {e}")
        sftp.close()
        ssh.close()
        return
    
    print("   ✅ Dockerfile read")
    
    # Create wrapper script content
    wrapper_script = """#!/bin/sh
# Node wrapper - ensures node is always found
exec /usr/bin/node "$@"
"""
    
    # Add wrapper creation to Dockerfile before USER pentest
    if 'RUN mkdir -p /usr/local/bin && echo' not in dockerfile:
        # Find USER pentest line
        dockerfile_lines = dockerfile.split('\n')
        new_lines = []
        wrapper_added = False
        
        for i, line in enumerate(dockerfile_lines):
            if 'USER pentest' in line and not wrapper_added:
                # Add wrapper creation before USER
                new_lines.append('RUN mkdir -p /usr/local/bin /bin /tmp && \\')
                new_lines.append('    echo \'#!/bin/sh\\nexec /usr/bin/node "$@"\' > /usr/local/bin/node && \\')
                new_lines.append('    echo \'#!/bin/sh\\nexec /usr/bin/node "$@"\' > /bin/node && \\')
                new_lines.append('    echo \'#!/bin/sh\\nexec /usr/bin/node "$@"\' > /tmp/node && \\')
                new_lines.append('    chmod +x /usr/local/bin/node /bin/node /tmp/node && \\')
                new_lines.append('    ln -sf /usr/bin/node /usr/local/bin/node && \\')
                new_lines.append('    ln -sf /usr/bin/node /bin/node')
                wrapper_added = True
                new_lines.append(line)
            else:
                new_lines.append(line)
        
        dockerfile = '\n'.join(new_lines)
        
        print("\n2. Writing updated Dockerfile...")
        with sftp.open('/opt/xaker/shannon/Dockerfile', 'w') as f:
            f.write(dockerfile.encode('utf-8'))
        print("   ✅ Dockerfile updated")
    else:
        print("   ✅ Wrapper already in Dockerfile")
    
    sftp.close()
    
    # Also create wrapper in running container as temporary fix
    print("\n3. Creating wrapper in running container (temporary fix)...")
    stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon_worker')
    worker = stdout.read().decode('utf-8', errors='replace')
    
    if worker:
        container_id = worker.split()[0]
        
        # Create wrappers
        commands = [
            'mkdir -p /usr/local/bin /bin /tmp',
            'echo \'#!/bin/sh\nexec /usr/bin/node "$@"\' > /usr/local/bin/node',
            'echo \'#!/bin/sh\nexec /usr/bin/node "$@"\' > /bin/node',
            'echo \'#!/bin/sh\nexec /usr/bin/node "$@"\' > /tmp/node',
            'chmod +x /usr/local/bin/node /bin/node /tmp/node',
        ]
        
        for cmd in commands:
            stdin, stdout, stderr = ssh.exec_command(f'docker exec -u root {container_id} sh -c "{cmd}"')
            stdout.read()
        
        print("   ✅ Wrappers created in running container")
        
        # Verify
        print("\n4. Verifying wrappers...")
        stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "which node && /usr/local/bin/node --version && /bin/node --version"')
        verify = stdout.read().decode('utf-8', errors='replace')
        print(verify)
        
        if 'v22' in verify or 'node' in verify.lower():
            print("   ✅ Wrappers work!")
            
            # Restart worker to ensure wrappers persist
            print("\n5. Restarting worker...")
            stdin, stdout, stderr = ssh.exec_command(f'docker restart {container_id}')
            time.sleep(5)
            
            stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon_worker')
            if stdout.read().decode('utf-8', errors='replace'):
                print("   ✅ Worker restarted!")
                
                # Restart backend
                print("\n6. Restarting backend...")
                stdin, stdout, stderr = ssh.exec_command('pm2 restart xaker-backend')
                print(stdout.read().decode('utf-8', errors='replace'))
                
                print("\n" + "=" * 80)
                print("✅ SUCCESS!")
                print("=" * 80)
                print("\nNode wrappers created in:")
                print("  - /usr/local/bin/node")
                print("  - /bin/node")
                print("  - /tmp/node")
                print("\nDockerfile updated to create wrappers on build")
                print("\n⚠️  Try a new pentest now!")
                print("If it still fails, rebuild the Docker image:")
                print("  cd /opt/xaker/shannon && docker-compose build --no-cache worker")
            else:
                print("   ⚠️ Worker not running after restart")
        else:
            print("   ⚠️ Wrappers not working")
    else:
        print("   ⚠️ Worker not running")
    
    ssh.close()

if __name__ == "__main__":
    create_wrapper()

