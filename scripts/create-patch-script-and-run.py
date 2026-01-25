#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Create patch script and run"""

import paramiko
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def create_patch_script():
    """Create patch script and run"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("CREATE PATCH SCRIPT AND RUN")
    print("=" * 80)
    
    # Find worker container
    stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon_worker')
    worker = stdout.read().decode('utf-8', errors='replace')
    
    if not worker:
        print("\nStarting worker...")
        stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose up -d worker')
        import time
        time.sleep(5)
        stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon_worker')
        worker = stdout.read().decode('utf-8', errors='replace')
    
    if not worker:
        print("   ⚠️ Worker not running")
        ssh.close()
        return
    
    container_id = worker.split()[0]
    print(f"\n1. Worker running: {container_id}")
    
    # Create patch script
    print("\n2. Creating patch script...")
    patch_script = """#!/bin/sh
LIB_FILE="/app/node_modules/@anthropic-ai/claude-agent-sdk/cli.js"
sed -i "s/spawn('node'/spawn('\\/usr\\/bin\\/node'/g" "$LIB_FILE"
sed -i 's/spawn("node"/spawn("\\/usr\\/bin\\/node"/g' "$LIB_FILE"
sed -i "s/spawnSync('node'/spawnSync('\\/usr\\/bin\\/node'/g" "$LIB_FILE"
sed -i 's/spawnSync("node"/spawnSync("\\/usr\\/bin\\/node"/g' "$LIB_FILE"
echo "Patch complete"
grep -c "spawn.*usr/bin/node" "$LIB_FILE" || echo "0"
"""
    
    # Write script to container
    stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "cat > /tmp/patch.sh" << \'ENDOFSCRIPT\'\n{patch_script}\nENDOFSCRIPT')
    stdout.read()
    
    # Make executable and run
    print("\n3. Running patch script...")
    stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "chmod +x /tmp/patch.sh && /tmp/patch.sh"')
    patch_output = stdout.read().decode('utf-8', errors='replace')
    patch_error = stderr.read().decode('utf-8', errors='replace')
    
    print(patch_output)
    if patch_error:
        print(f"   Errors: {patch_error[:200]}")
    
    # Check result
    verify = patch_output.strip().split('\n')[-1] if patch_output else '0'
    print(f"\n4. Verification: {verify} replacements")
    
    if verify != '0' and verify != '':
        print("   ✅ Patch successful!")
        
        # Restart worker
        print("\n5. Restarting worker...")
        stdin, stdout, stderr = ssh.exec_command(f'docker restart {container_id}')
        import time
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
                print(f"\nLibrary patched: {verify} spawn('node') -> spawn('/usr/bin/node')")
                print("Worker is running")
                print("\nTry a new pentest now!")
        else:
            print("\n   ⚠️ Worker not running after restart")
    else:
        print("   ⚠️ No replacements found")
        print("   Library might use different pattern")
    
    ssh.close()

if __name__ == "__main__":
    import time
    create_patch_script()

