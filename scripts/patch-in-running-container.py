#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Patch library in running container"""

import paramiko
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def patch_running():
    """Patch in running container"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("PATCH LIBRARY IN RUNNING CONTAINER")
    print("=" * 80)
    
    # Find any worker container (running or stopped)
    stdin, stdout, stderr = ssh.exec_command('docker ps -a | grep shannon_worker | head -1')
    container_line = stdout.read().decode('utf-8', errors='replace')
    
    if not container_line:
        print("   ⚠️ No worker container found")
        ssh.close()
        return
    
    container_id = container_line.split()[0]
    print(f"\n1. Found container: {container_id}")
    
    # Check if it's running
    if 'Up' in container_line:
        print("   ✅ Container is running")
    else:
        print("   ⚠️ Container is stopped, starting it...")
        stdin, stdout, stderr = ssh.exec_command(f'docker start {container_id}')
        import time
        time.sleep(3)
    
    lib_file = '/app/node_modules/@anthropic-ai/claude-agent-sdk/cli.js'
    
    # Check if file exists
    print(f"\n2. Checking library file...")
    stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} ls -lh {lib_file} 2>&1')
    file_check = stdout.read().decode('utf-8', errors='replace')
    if 'No such file' in file_check:
        print(f"   ⚠️ File not found: {file_check}")
        ssh.close()
        return
    print(f"   ✅ File exists: {file_check.strip()}")
    
    # Patch with sed
    print("\n3. Patching with sed...")
    
    # Replace spawn('node' with spawn('/usr/bin/node'
    print("   Replacing spawn('node'...")
    stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sed -i "s/spawn(\'node\'/spawn(\'\\/usr\\/bin\\/node\'/g" {lib_file} 2>&1')
    sed_output1 = stdout.read().decode('utf-8', errors='replace')
    sed_error1 = stderr.read().decode('utf-8', errors='replace')
    if sed_error1 and 'No such file' not in sed_error1:
        print(f"   Error: {sed_error1}")
    
    # Replace spawn("node" with spawn("/usr/bin/node"
    print("   Replacing spawn(\"node\"...")
    stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sed -i \'s/spawn("node"/spawn("\\/usr\\/bin\\/node"/g\' {lib_file} 2>&1')
    sed_output2 = stdout.read().decode('utf-8', errors='replace')
    sed_error2 = stderr.read().decode('utf-8', errors='replace')
    if sed_error2 and 'No such file' not in sed_error2:
        print(f"   Error: {sed_error2}")
    
    # Replace spawnSync
    print("   Replacing spawnSync('node'...")
    stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sed -i "s/spawnSync(\'node\'/spawnSync(\'\\/usr\\/bin\\/node\'/g" {lib_file} 2>&1')
    sed_output3 = stdout.read().decode('utf-8', errors='replace')
    sed_error3 = stderr.read().decode('utf-8', errors='replace')
    if sed_error3 and 'No such file' not in sed_error3:
        print(f"   Error: {sed_error3}")
    
    print("   Replacing spawnSync(\"node\"...")
    stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sed -i \'s/spawnSync("node"/spawnSync("\\/usr\\/bin\\/node"/g\' {lib_file} 2>&1')
    sed_output4 = stdout.read().decode('utf-8', errors='replace')
    sed_error4 = stderr.read().decode('utf-8', errors='replace')
    if sed_error4 and 'No such file' not in sed_error4:
        print(f"   Error: {sed_error4}")
    
    # Verify
    print("\n4. Verifying patch...")
    stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} grep -c "spawn.*usr/bin/node" {lib_file} 2>&1')
    verify = stdout.read().decode('utf-8', errors='replace').strip()
    print(f"   Found {verify} occurrences of spawn('/usr/bin/node')")
    
    if verify != '0' and verify != '':
        print("   ✅ Patch successful!")
        
        # Show sample
        stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} grep -n "spawn.*usr/bin/node" {lib_file} | head -3')
        sample = stdout.read().decode('utf-8', errors='replace')
        if sample:
            print(f"\n   Sample:\n{sample[:300]}")
        
        # Restart container
        print("\n5. Restarting container...")
        stdin, stdout, stderr = ssh.exec_command(f'docker restart {container_id}')
        print(stdout.read().decode('utf-8', errors='replace'))
        
        import time
        time.sleep(5)
        
        # Check if running
        stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon_worker')
        worker_check = stdout.read().decode('utf-8', errors='replace')
        if worker_check:
            print("\n   ✅ Worker is running!")
            
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
            print("\n   ⚠️ Worker not running after restart")
    else:
        print("   ⚠️ No replacements found")
        print("   Library might use different pattern")
    
    ssh.close()

if __name__ == "__main__":
    import time
    patch_running()

