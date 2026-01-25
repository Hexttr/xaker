#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Start worker and patch library"""

import paramiko
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def start_and_patch():
    """Start worker and patch"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("START WORKER AND PATCH LIBRARY")
    print("=" * 80)
    
    # Update docker-compose to use existing image without rebuild
    print("\n1. Updating docker-compose.yml...")
    sftp = ssh.open_sftp()
    with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'r') as f:
        compose = f.read().decode('utf-8')
    
    # Ensure entrypoint is simple
    if 'entrypoint: ["/bin/sh", "/app/start-worker.sh"]' not in compose:
        compose = compose.replace(
            '    entrypoint:',
            '    entrypoint: ["/bin/sh", "/app/start-worker.sh"]\n    # entrypoint:'
        )
    
    # Ensure user is root
    if 'user: root' not in compose:
        compose_lines = compose.split('\n')
        for i, line in enumerate(compose_lines):
            if 'worker:' in line and 'user:' not in '\n'.join(compose_lines[i:i+5]):
                compose_lines.insert(i+1, '    user: root')
                break
        compose = '\n'.join(compose_lines)
    
    with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'w') as f:
        f.write(compose.encode('utf-8'))
    sftp.close()
    print("   ✅ docker-compose.yml updated")
    
    # Start worker (using existing image)
    print("\n2. Starting worker (using existing image)...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose up -d worker 2>&1')
    start_output = stdout.read().decode('utf-8', errors='replace')
    start_error = stderr.read().decode('utf-8', errors='replace')
    print(start_output)
    if start_error:
        print(f"   Errors: {start_error}")
    
    import time
    time.sleep(5)
    
    # Check if worker is running
    stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon | grep worker')
    worker = stdout.read().decode('utf-8', errors='replace')
    
    if not worker:
        print("\n   ⚠️ Worker not running, checking logs...")
        stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose logs worker --tail=20')
        logs = stdout.read().decode('utf-8', errors='replace')
        print(logs)
        
        # Try to start with docker run directly
        print("\n   Trying to start with docker run...")
        stdin, stdout, stderr = ssh.exec_command('docker run -d --name shannon_worker_temp --network shannon_default -e TEMPORAL_ADDRESS=temporal:7233 -e NODE=/usr/bin/node -e PATH=/usr/bin:/usr/local/bin:/bin:/sbin -v /opt/xaker/shannon:/app -w /app shannon_worker sh -c "export PATH=/usr/bin:/usr/local/bin:/bin:/sbin && ln -sf /usr/bin/node /usr/local/bin/node && ln -sf /usr/bin/node /bin/node && cd /app && node dist/temporal/worker.js"')
        print(stdout.read().decode('utf-8', errors='replace'))
        time.sleep(3)
        
        stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon_worker')
        worker = stdout.read().decode('utf-8', errors='replace')
    
    if worker:
        container_id = worker.split()[0]
        print(f"\n   ✅ Worker running: {container_id}")
        
        # Now patch the library
        print("\n3. Patching library with sed...")
        lib_file = '/app/node_modules/@anthropic-ai/claude-agent-sdk/cli.js'
        
        # Replace spawn('node' with spawn('/usr/bin/node'
        stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sed -i "s/spawn(\'node\'/spawn(\'\\/usr\\/bin\\/node\'/g" {lib_file}')
        sed_error1 = stderr.read().decode('utf-8', errors='replace')
        
        # Replace spawn("node" with spawn("/usr/bin/node"
        stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sed -i \'s/spawn("node"/spawn("\\/usr\\/bin\\/node"/g\' {lib_file}')
        sed_error2 = stderr.read().decode('utf-8', errors='replace')
        
        # Replace spawnSync
        stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sed -i "s/spawnSync(\'node\'/spawnSync(\'\\/usr\\/bin\\/node\'/g" {lib_file}')
        sed_error3 = stderr.read().decode('utf-8', errors='replace')
        
        stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sed -i \'s/spawnSync("node"/spawnSync("\\/usr\\/bin\\/node"/g\' {lib_file}')
        sed_error4 = stderr.read().decode('utf-8', errors='replace')
        
        if sed_error1 or sed_error2 or sed_error3 or sed_error4:
            errors = sed_error1 + sed_error2 + sed_error3 + sed_error4
            if 'No such file' not in errors:
                print(f"   ⚠️ Errors: {errors}")
        
        # Verify
        print("\n4. Verifying patch...")
        stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} grep -c "spawn.*usr/bin/node" {lib_file}')
        verify = stdout.read().decode('utf-8', errors='replace').strip()
        print(f"   Found {verify} occurrences of spawn('/usr/bin/node')")
        
        if verify != '0':
            print("   ✅ Patch successful!")
            
            # Restart worker to apply patch
            print("\n5. Restarting worker to apply patch...")
            stdin, stdout, stderr = ssh.exec_command(f'docker restart {container_id}')
            print(stdout.read().decode('utf-8', errors='replace'))
            
            time.sleep(5)
            
            # Check worker
            stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon_worker')
            worker_check = stdout.read().decode('utf-8', errors='replace')
            if worker_check:
                print("\n   ✅ Worker restarted!")
                
                stdin, stdout, stderr = ssh.exec_command(f'docker logs {container_id} --tail=10 2>&1')
                logs = stdout.read().decode('utf-8', errors='replace')
                if 'RUNNING' in logs:
                    print("\n   ✅ Worker is RUNNING!")
                    
                    # Restart backend
                    print("\n6. Restarting backend...")
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
        print("\n   ⚠️ Could not start worker")
    
    ssh.close()

if __name__ == "__main__":
    import time
    start_and_patch()

