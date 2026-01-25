#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Simple start and patch"""

import paramiko
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def simple_start_patch():
    """Simple start and patch"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("SIMPLE START AND PATCH")
    print("=" * 80)
    
    # Update docker-compose with simple entrypoint
    print("\n1. Updating docker-compose.yml...")
    sftp = ssh.open_sftp()
    with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'r') as f:
        compose = f.read().decode('utf-8')
    
    # Replace entrypoint with simple one that just runs node
    compose = compose.replace(
        '    entrypoint: ["/bin/sh", "-c", "export PATH=/usr/bin:/usr/local/bin:/bin:/sbin && export NODE=/usr/bin/node && ln -sf /usr/bin/node /usr/local/bin/node && ln -sf /usr/bin/node /bin/node && cd /app && exec node dist/temporal/worker.js"]',
        '    entrypoint: ["node", "dist/temporal/worker.js"]'
    )
    
    # Ensure user is root
    if 'user: root' not in compose:
        compose_lines = compose.split('\n')
        for i, line in enumerate(compose_lines):
            if 'worker:' in line:
                compose_lines.insert(i+1, '    user: root')
                break
        compose = '\n'.join(compose_lines)
    
    with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'w') as f:
        f.write(compose.encode('utf-8'))
    sftp.close()
    print("   ✅ docker-compose.yml updated")
    
    # Start worker
    print("\n2. Starting worker...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose stop worker && docker-compose rm -f worker && docker-compose up -d worker 2>&1')
    start_output = stdout.read().decode('utf-8', errors='replace')
    print(start_output)
    
    import time
    time.sleep(5)
    
    # Find worker
    stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon_worker')
    worker = stdout.read().decode('utf-8', errors='replace')
    
    if worker:
        container_id = worker.split()[0]
        print(f"\n   ✅ Worker running: {container_id}")
        
        # Patch library
        print("\n3. Patching library...")
        lib_file = '/app/node_modules/@anthropic-ai/claude-agent-sdk/cli.js'
        
        # Patch with sed
        patch_cmd = f'docker exec {container_id} sh -c "sed -i \\"s/spawn(\\'node\\'/spawn(\\'\\/usr\\/bin\\/node\\'/g\\" {lib_file} && sed -i \\"s/spawn(\\\"node\\\"/spawn(\\\"\\/usr\\/bin\\/node\\\"/g\\" {lib_file} && sed -i \\"s/spawnSync(\\'node\\'/spawnSync(\\'\\/usr\\/bin\\/node\\'/g\\" {lib_file} && sed -i \\"s/spawnSync(\\\"node\\\"/spawnSync(\\\"\\/usr\\/bin\\/node\\\"/g\\" {lib_file}"'
        
        stdin, stdout, stderr = ssh.exec_command(patch_cmd)
        patch_output = stdout.read().decode('utf-8', errors='replace')
        patch_error = stderr.read().decode('utf-8', errors='replace')
        
        if patch_error and 'No such file' not in patch_error:
            print(f"   Warning: {patch_error[:200]}")
        
        # Verify
        print("\n4. Verifying patch...")
        stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} grep -c "spawn.*usr/bin/node" {lib_file} 2>&1')
        verify = stdout.read().decode('utf-8', errors='replace').strip()
        print(f"   Found {verify} occurrences")
        
        if verify != '0' and verify != '':
            print("   ✅ Patch successful!")
            
            # Restart worker
            print("\n5. Restarting worker...")
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
        print("\n   ⚠️ Worker not running")
        stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose logs worker --tail=20')
        print(stdout.read().decode('utf-8', errors='replace'))
    
    ssh.close()

if __name__ == "__main__":
    import time
    simple_start_patch()

