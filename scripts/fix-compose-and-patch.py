#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix compose and patch library"""

import paramiko
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def fix_and_patch():
    """Fix compose and patch"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("FIX DOCKER-COMPOSE AND PATCH LIBRARY")
    print("=" * 80)
    
    # Clean up old containers
    print("\n1. Cleaning up old containers...")
    stdin, stdout, stderr = ssh.exec_command('docker ps -a | grep shannon_worker | awk \'{print $1}\' | xargs -r docker rm -f')
    print(stdout.read().decode('utf-8', errors='replace'))
    
    # Update docker-compose.yml
    print("\n2. Updating docker-compose.yml...")
    sftp = ssh.open_sftp()
    with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'r') as f:
        compose = f.read().decode('utf-8')
    
    # Ensure worker service has correct entrypoint
    compose_lines = compose.split('\n')
    new_lines = []
    in_worker = False
    entrypoint_set = False
    user_set = False
    
    for i, line in enumerate(compose_lines):
        if 'worker:' in line:
            in_worker = True
            new_lines.append(line)
            continue
        
        if in_worker:
            if 'entrypoint:' in line:
                # Replace entrypoint
                new_lines.append('    entrypoint: ["/bin/sh", "-c", "export PATH=/usr/bin:/usr/local/bin:/bin:/sbin && export NODE=/usr/bin/node && ln -sf /usr/bin/node /usr/local/bin/node && ln -sf /usr/bin/node /bin/node && cd /app && exec node dist/temporal/worker.js"]')
                entrypoint_set = True
                continue
            elif 'user:' in line:
                new_lines.append('    user: root')
                user_set = True
                continue
            elif line.strip() and not line.startswith(' ') and not line.startswith('#'):
                # End of worker service
                if not entrypoint_set:
                    new_lines.append('    entrypoint: ["/bin/sh", "-c", "export PATH=/usr/bin:/usr/local/bin:/bin:/sbin && export NODE=/usr/bin/node && ln -sf /usr/bin/node /usr/local/bin/node && ln -sf /usr/bin/node /bin/node && cd /app && exec node dist/temporal/worker.js"]')
                if not user_set:
                    new_lines.append('    user: root')
                in_worker = False
                new_lines.append(line)
                continue
        
        new_lines.append(line)
    
    compose = '\n'.join(new_lines)
    
    with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'w') as f:
        f.write(compose.encode('utf-8'))
    sftp.close()
    print("   ✅ docker-compose.yml updated")
    
    # Start worker
    print("\n3. Starting worker...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose up -d worker 2>&1')
    start_output = stdout.read().decode('utf-8', errors='replace')
    print(start_output)
    
    import time
    time.sleep(5)
    
    # Find worker container
    stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon_worker')
    worker = stdout.read().decode('utf-8', errors='replace')
    
    if worker:
        container_id = worker.split()[0]
        print(f"\n   ✅ Worker running: {container_id}")
        
        # Patch library
        print("\n4. Patching library...")
        lib_file = '/app/node_modules/@anthropic-ai/claude-agent-sdk/cli.js'
        
        # Use sed to replace
        commands = [
            f'sed -i "s/spawn(\'node\'/spawn(\'\\/usr\\/bin\\/node\'/g" {lib_file}',
            f'sed -i \'s/spawn("node"/spawn("\\/usr\\/bin\\/node"/g\' {lib_file}',
            f'sed -i "s/spawnSync(\'node\'/spawnSync(\'\\/usr\\/bin\\/node\'/g" {lib_file}',
            f'sed -i \'s/spawnSync("node"/spawnSync("\\/usr\\/bin\\/node"/g\' {lib_file}',
        ]
        
        for cmd in commands:
            stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "{cmd}" 2>&1')
            error = stderr.read().decode('utf-8', errors='replace')
            if error and 'No such file' not in error:
                print(f"   Warning: {error[:100]}")
        
        # Verify
        print("\n5. Verifying patch...")
        stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} grep -c "spawn.*usr/bin/node" {lib_file} 2>&1')
        verify = stdout.read().decode('utf-8', errors='replace').strip()
        print(f"   Found {verify} occurrences")
        
        if verify != '0' and verify != '':
            print("   ✅ Patch successful!")
            
            # Restart worker
            print("\n6. Restarting worker...")
            stdin, stdout, stderr = ssh.exec_command(f'docker restart {container_id}')
            time.sleep(5)
            
            stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon_worker')
            if stdout.read().decode('utf-8', errors='replace'):
                print("\n   ✅ Worker restarted!")
                
                stdin, stdout, stderr = ssh.exec_command(f'docker logs {container_id} --tail=10 2>&1')
                logs = stdout.read().decode('utf-8', errors='replace')
                if 'RUNNING' in logs:
                    print("\n   ✅ Worker is RUNNING!")
                    
                    # Restart backend
                    print("\n7. Restarting backend...")
                    stdin, stdout, stderr = ssh.exec_command('pm2 restart xaker-backend')
                    print(stdout.read().decode('utf-8', errors='replace'))
                    
                    print("\n" + "=" * 80)
                    print("✅ SUCCESS!")
                    print("=" * 80)
                    print("\nLibrary patched: spawn('node') -> spawn('/usr/bin/node')")
                    print("Worker is running")
                    print("\nTry a new pentest now!")
        else:
            print("   ⚠️ No replacements found")
    else:
        print("\n   ⚠️ Worker not running")
        stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose logs worker --tail=20')
        print(stdout.read().decode('utf-8', errors='replace'))
    
    ssh.close()

if __name__ == "__main__":
    import time
    fix_and_patch()

