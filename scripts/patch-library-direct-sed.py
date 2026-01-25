#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Patch library directly using sed"""

import paramiko
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def patch_with_sed():
    """Patch library using sed"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("PATCHING LIBRARY DIRECTLY WITH SED")
    print("=" * 80)
    
    # Start worker if needed
    stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon | grep worker')
    worker = stdout.read().decode('utf-8', errors='replace')
    if not worker:
        print("\nStarting worker...")
        stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose up -d worker')
        import time
        time.sleep(5)
        stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon | grep worker')
        worker = stdout.read().decode('utf-8', errors='replace')
    
    if not worker:
        print("   ⚠️ Could not start worker")
        ssh.close()
        return
    
    container_id = worker.split()[0]
    lib_file = '/app/node_modules/@anthropic-ai/claude-agent-sdk/cli.js'
    
    print(f"\n1. Checking current file...")
    stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} ls -lh {lib_file}')
    file_info = stdout.read().decode('utf-8', errors='replace')
    print(f"   {file_info.strip()}")
    
    # Count current spawn('node') patterns
    print("\n2. Counting spawn('node') patterns...")
    stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} grep -o "spawn(\'node\'" {lib_file} | wc -l')
    count1 = stdout.read().decode('utf-8', errors='replace').strip()
    stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} grep -o \'spawn("node"\' {lib_file} | wc -l')
    count2 = stdout.read().decode('utf-8', errors='replace').strip()
    
    print(f"   Found {count1} spawn('node') and {count2} spawn(\"node\")")
    
    # Use sed to replace directly in file
    print("\n3. Patching file with sed...")
    
    # Replace spawn('node' with spawn('/usr/bin/node'
    stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sed -i "s/spawn(\'node\'/spawn(\'\\/usr\\/bin\\/node\'/g" {lib_file}')
    sed_output1 = stdout.read().decode('utf-8', errors='replace')
    sed_error1 = stderr.read().decode('utf-8', errors='replace')
    
    # Replace spawn("node" with spawn("/usr/bin/node"
    stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sed -i \'s/spawn("node"/spawn("\\/usr\\/bin\\/node"/g\' {lib_file}')
    sed_output2 = stdout.read().decode('utf-8', errors='replace')
    sed_error2 = stderr.read().decode('utf-8', errors='replace')
    
    # Replace spawnSync('node' with spawnSync('/usr/bin/node'
    stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sed -i "s/spawnSync(\'node\'/spawnSync(\'\\/usr\\/bin\\/node\'/g" {lib_file}')
    sed_output3 = stdout.read().decode('utf-8', errors='replace')
    sed_error3 = stderr.read().decode('utf-8', errors='replace')
    
    # Replace spawnSync("node" with spawnSync("/usr/bin/node"
    stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sed -i \'s/spawnSync("node"/spawnSync("\\/usr\\/bin\\/node"/g\' {lib_file}')
    sed_output4 = stdout.read().decode('utf-8', errors='replace')
    sed_error4 = stderr.read().decode('utf-8', errors='replace')
    
    if sed_error1 or sed_error2 or sed_error3 or sed_error4:
        errors = sed_error1 + sed_error2 + sed_error3 + sed_error4
        if 'No such file' not in errors:
            print(f"   ⚠️ Errors: {errors}")
    
    # Verify replacements
    print("\n4. Verifying replacements...")
    stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} grep -c "spawn(\'/usr/bin/node\'" {lib_file}')
    verify1 = stdout.read().decode('utf-8', errors='replace').strip()
    stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} grep -c \'spawn("/usr/bin/node"\' {lib_file}')
    verify2 = stdout.read().decode('utf-8', errors='replace').strip()
    
    print(f"   Found {verify1} spawn('/usr/bin/node') and {verify2} spawn(\"/usr/bin/node\")")
    
    if verify1 != '0' or verify2 != '0':
        print("   ✅ Replacements successful!")
        
        # Show a sample
        stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} grep -n "spawn.*usr/bin/node" {lib_file} | head -3')
        sample = stdout.read().decode('utf-8', errors='replace')
        if sample:
            print(f"\n   Sample:\n{sample[:500]}")
        
        # Restart worker
        print("\n5. Restarting worker...")
        stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose restart worker')
        restart_output = stdout.read().decode('utf-8', errors='replace')
        print(restart_output)
        
        import time
        time.sleep(5)
        
        # Check worker
        stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon | grep worker')
        worker_check = stdout.read().decode('utf-8', errors='replace')
        if worker_check:
            print("\n   ✅ Worker restarted!")
            
            # Check logs
            stdin, stdout, stderr = ssh.exec_command(f'docker logs {worker_check.split()[0]} --tail=10 2>&1')
            logs = stdout.read().decode('utf-8', errors='replace')
            if 'RUNNING' in logs:
                print("\n   ✅ Worker is RUNNING!")
                
                # Restart backend
                print("\n6. Restarting backend...")
                stdin, stdout, stderr = ssh.exec_command('pm2 restart xaker-backend')
                print(stdout.read().decode('utf-8', errors='replace'))
                
                print("\n" + "=" * 80)
                print("✅ SUCCESS! Library patched")
                print("=" * 80)
                print(f"\nReplaced spawn('node') with spawn('/usr/bin/node')")
                print("Library will now use full path to node")
                print("\nTry a new pentest now!")
            else:
                print("\n   ⚠️ Worker may not be fully started")
                print(f"   Logs: {logs[-300:]}")
        else:
            print("\n   ⚠️ Worker not running")
    else:
        print("   ⚠️ No replacements found")
        print("   File might use different pattern")
        
        # Try to find what pattern is used
        print("\n   Searching for spawn patterns...")
        stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} grep -o "spawn[^(]*([^)]*node[^)]*)" {lib_file} | head -5')
        patterns = stdout.read().decode('utf-8', errors='replace')
        if patterns:
            print(f"   Found patterns:\n{patterns[:500]}")
    
    ssh.close()

if __name__ == "__main__":
    import time
    patch_with_sed()

