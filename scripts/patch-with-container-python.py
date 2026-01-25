#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Patch using Python inside container"""

import paramiko
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def patch_container_python():
    """Patch using Python in container"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("PATCH USING PYTHON INSIDE CONTAINER")
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
    
    print(f"\n1. Creating Python patch script in container...")
    
    # Create Python script that will do the patching
    python_script = f"""import re
import sys

lib_file = '{lib_file}'

# Read file
with open(lib_file, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

original = content

# Replace 'node' -> '/usr/bin/node' but not 'node:'
# Use regex with negative lookahead/lookbehind
content = re.sub(r"(?<!node:)(?<!node\\.)(?<!node\\[)['\\"]node['\\"](?!:)", "'/usr/bin/node'", content)

# Also try replacing in spawn contexts
content = re.sub(r"(spawn|execa|spawnSync)\\s*\\(\\s*['\\"]node['\\"]", r"\\1('/usr/bin/node'", content)
content = re.sub(r'(spawn|execa|spawnSync)\\s*\\(\\s*["\\']node["\\']', r'\\1("/usr/bin/node"', content)

if content != original:
    # Write back
    with open(lib_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Count replacements
    count = content.count("/usr/bin/node")
    print(f"SUCCESS: Replaced strings, found {{count}} occurrences of '/usr/bin/node'")
    sys.exit(0)
else:
    print("No replacements made")
    sys.exit(1)
"""
    
    # Write Python script to container
    stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "cat > /tmp/patch.py" << \'ENDOFSCRIPT\'\n{python_script}\nENDOFSCRIPT')
    stdout.read()
    
    # Run Python script
    print("\n2. Running Python patch script...")
    stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} python3 /tmp/patch.py')
    patch_output = stdout.read().decode('utf-8', errors='replace')
    patch_error = stderr.read().decode('utf-8', errors='replace')
    exit_code = stdout.channel.recv_exit_status()
    
    print(patch_output)
    if patch_error:
        print(f"   Errors: {patch_error[:300]}")
    
    if exit_code == 0 and 'SUCCESS' in patch_output:
        print("   ✅ Patch successful!")
        
        # Verify
        print("\n3. Verifying...")
        stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} grep -c "/usr/bin/node" {lib_file}')
        verify = stdout.read().decode('utf-8', errors='replace').strip()
        print(f"   Found {verify} occurrences")
        
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
                print("\nLibrary patched using Python")
                print("Worker is running")
                print("\nTry a new pentest now!")
    else:
        print("   ⚠️ Patch failed or no replacements made")
    
    ssh.close()

if __name__ == "__main__":
    import time
    patch_container_python()

