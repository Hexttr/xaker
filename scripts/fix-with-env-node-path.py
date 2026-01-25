#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix by ensuring NODE env variable is set in activities"""

import paramiko
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def fix_with_env():
    """Fix by ensuring NODE env variable"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("FIX: ENSURE NODE ENV VARIABLE IN DOCKER-COMPOSE")
    print("=" * 80)
    print("\nBased on research, the issue is that spawn() doesn't inherit PATH")
    print("properly. We need to ensure NODE=/usr/bin/node is set in environment.")
    
    # Update docker-compose.yml
    print("\n1. Updating docker-compose.yml...")
    sftp = ssh.open_sftp()
    with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'r') as f:
        compose = f.read().decode('utf-8')
    
    # Ensure NODE is explicitly set
    compose_lines = compose.split('\n')
    new_lines = []
    in_worker = False
    in_env = False
    
    for i, line in enumerate(compose_lines):
        if 'worker:' in line:
            in_worker = True
            new_lines.append(line)
            continue
        
        if in_worker:
            if 'environment:' in line:
                in_env = True
                new_lines.append(line)
                continue
            
            if in_env:
                # Check if NODE is already set
                if 'NODE=' in line:
                    # Replace if exists
                    new_lines.append('      - NODE=/usr/bin/node')
                    continue
                elif line.strip() and not line.startswith(' ') and not line.startswith('-'):
                    # End of environment section
                    if 'NODE=' not in '\n'.join(new_lines[-10:]):
                        new_lines.append('      - NODE=/usr/bin/node')
                    in_env = False
                    new_lines.append(line)
                    continue
                elif not line.strip() or line.startswith(' ') or line.startswith('-'):
                    new_lines.append(line)
                    continue
            
            if line.strip() and not line.startswith(' ') and not line.startswith('#'):
                # End of worker service
                if in_env and 'NODE=' not in '\n'.join(new_lines[-10:]):
                    new_lines.append('      - NODE=/usr/bin/node')
                in_worker = False
                in_env = False
                new_lines.append(line)
                continue
        
        new_lines.append(line)
    
    # If NODE wasn't added, add it after environment:
    compose = '\n'.join(new_lines)
    if 'NODE=/usr/bin/node' not in compose:
        # Find worker: and add environment section
        compose_lines = compose.split('\n')
        for i, line in enumerate(compose_lines):
            if 'worker:' in line:
                # Check if environment exists
                if 'environment:' not in '\n'.join(compose_lines[i:i+10]):
                    compose_lines.insert(i+1, '    environment:')
                    compose_lines.insert(i+2, '      - NODE=/usr/bin/node')
                    compose_lines.insert(i+3, '      - PATH=/usr/bin:/usr/local/bin:/bin:/sbin')
                break
        compose = '\n'.join(compose_lines)
    
    with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'w') as f:
        f.write(compose.encode('utf-8'))
    sftp.close()
    print("   ✅ docker-compose.yml updated")
    
    # Also update start-worker.sh to export NODE
    print("\n2. Updating start-worker.sh...")
    try:
        with sftp.open('/opt/xaker/shannon/start-worker.sh', 'r') as f:
            start_script = f.read().decode('utf-8')
        
        if 'export NODE=/usr/bin/node' not in start_script:
            start_script = start_script.replace(
                'export PATH=',
                'export NODE=/usr/bin/node\nexport PATH='
            )
        
        with sftp.open('/opt/xaker/shannon/start-worker.sh', 'w') as f:
            f.write(start_script.encode('utf-8'))
        print("   ✅ start-worker.sh updated")
    except Exception as e:
        print(f"   ⚠️ Could not update start-worker.sh: {e}")
    
    sftp.close()
    
    # Restart worker
    print("\n3. Restarting worker...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose stop worker && docker-compose rm -f worker && docker-compose up -d worker')
    restart_output = stdout.read().decode('utf-8', errors='replace')
    print(restart_output)
    
    import time
    time.sleep(5)
    
    # Verify
    print("\n4. Verifying NODE env variable...")
    stdin, stdout, stderr = ssh.exec_command('docker exec shannon_worker_1 sh -c "echo NODE=$NODE && echo PATH=$PATH"')
    env_check = stdout.read().decode('utf-8', errors='replace')
    print(env_check)
    
    if '/usr/bin/node' in env_check:
        print("\n   ✅ NODE environment variable is set!")
        
        stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon_worker')
        if stdout.read().decode('utf-8', errors='replace'):
            print("\n   ✅ Worker is running!")
            
            # Restart backend
            print("\n5. Restarting backend...")
            stdin, stdout, stderr = ssh.exec_command('pm2 restart xaker-backend')
            print(stdout.read().decode('utf-8', errors='replace'))
            
            print("\n" + "=" * 80)
            print("✅ SUCCESS!")
            print("=" * 80)
            print("\nNODE=/usr/bin/node is now set in environment")
            print("This should help spawn() find node")
            print("\n⚠️  IMPORTANT: If this still doesn't work, the library")
            print("   might need to be patched to use NODE env variable")
            print("\nTry a new pentest now!")
    else:
        print("\n   ⚠️ NODE not set correctly")
    
    ssh.close()

if __name__ == "__main__":
    import time
    fix_with_env()

