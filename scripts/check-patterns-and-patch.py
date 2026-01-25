#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check patterns and patch"""

import paramiko
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def check_and_patch():
    """Check patterns and patch"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("CHECK PATTERNS AND PATCH")
    print("=" * 80)
    
    # Find worker
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
    lib_file = '/app/node_modules/@anthropic-ai/claude-agent-sdk/cli.js'
    
    print(f"\n1. Checking patterns in library...")
    
    # Check for different patterns
    check_script = f"""#!/bin/sh
LIB_FILE="{lib_file}"
echo "Checking for spawn patterns..."
grep -o "spawn.*node" "$LIB_FILE" | head -10
echo "---"
grep -o 'spawn.*"node"' "$LIB_FILE" | head -10
echo "---"
grep -o "spawn.*'node'" "$LIB_FILE" | head -10
"""
    
    stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "cat > /tmp/check.sh" << \'EOF\'\n{check_script}\nEOF')
    stdout.read()
    
    stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "chmod +x /tmp/check.sh && /tmp/check.sh"')
    patterns = stdout.read().decode('utf-8', errors='replace')
    print(patterns)
    
    # Try aggressive replacement - replace any 'node' string that might be a command
    print("\n2. Trying aggressive patch...")
    patch_script = f"""#!/bin/sh
LIB_FILE="{lib_file}"
# Try replacing 'node' with '/usr/bin/node' in various contexts
# But be careful not to break 'node:' module syntax
perl -i -pe "s/(spawn|execa|spawnSync)\\((['\\"])(node)\\2/spawn('\\/usr\\/bin\\/node'/g" "$LIB_FILE" 2>/dev/null || \\
perl -i -pe 's/(spawn|execa|spawnSync)\\((["'"'"'])(node)\\2/spawn("\\/usr\\/bin\\/node"/g' "$LIB_FILE" 2>/dev/null || \\
sed -i 's/"node"/"\\/usr\\/bin\\/node"/g' "$LIB_FILE" || \\
sed -i "s/'node'/'\\/usr\\/bin\\/node'/g" "$LIB_FILE"
echo "Patch attempted"
grep -c "/usr/bin/node" "$LIB_FILE" || echo "0"
"""
    
    stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "cat > /tmp/patch2.sh" << \'EOF\'\n{patch_script}\nEOF')
    stdout.read()
    
    stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "chmod +x /tmp/patch2.sh && /tmp/patch2.sh"')
    patch_output = stdout.read().decode('utf-8', errors='replace')
    patch_error = stderr.read().decode('utf-8', errors='replace')
    
    print(patch_output)
    if patch_error:
        print(f"   Errors: {patch_error[:300]}")
    
    verify = patch_output.strip().split('\n')[-1] if patch_output else '0'
    print(f"\n3. Verification: {verify} occurrences of '/usr/bin/node'")
    
    if verify != '0' and verify != '':
        print("   ✅ Patch successful!")
        
        # Restart worker
        print("\n4. Restarting worker...")
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
                print("\n5. Restarting backend...")
                stdin, stdout, stderr = ssh.exec_command('pm2 restart xaker-backend')
                print(stdout.read().decode('utf-8', errors='replace'))
                
                print("\n" + "=" * 80)
                print("✅ SUCCESS!")
                print("=" * 80)
                print(f"\nLibrary patched: {verify} occurrences replaced")
                print("Worker is running")
                print("\nTry a new pentest now!")
    
    ssh.close()

if __name__ == "__main__":
    import time
    check_and_patch()

