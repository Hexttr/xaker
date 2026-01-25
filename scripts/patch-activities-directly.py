#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Patch activities.js directly to use full path"""

import paramiko
import sys
import base64
import re

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def patch_activities():
    """Patch activities.js directly"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("PATCHING ACTIVITIES.JS DIRECTLY")
    print("=" * 80)
    
    # Find worker container
    stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon | grep worker')
    worker = stdout.read().decode('utf-8', errors='replace')
    if not worker:
        print("Worker not running")
        ssh.close()
        return
    
    container_id = worker.split()[0]
    print(f"Worker container: {container_id}")
    
    # Read activities.js
    print("\n1. Reading activities.js...")
    stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} cat /app/dist/temporal/activities.js')
    activities_content = stdout.read().decode('utf-8', errors='replace')
    
    if not activities_content:
        print("   ⚠️ Could not read activities.js")
        ssh.close()
        return
    
    print(f"   File size: {len(activities_content)} bytes")
    
    # Find spawn calls
    print("\n2. Searching for spawn('node') patterns...")
    
    # Try different patterns
    patterns_to_replace = [
        (r"spawn\(['\"]node['\"]", r"spawn(process.env.NODE || '/usr/bin/node'"),
        (r'spawn\(["\']node["\']', r"spawn(process.env.NODE || '/usr/bin/node'"),
        (r"spawnSync\(['\"]node['\"]", r"spawnSync(process.env.NODE || '/usr/bin/node'"),
        (r'spawnSync\(["\']node["\']', r"spawnSync(process.env.NODE || '/usr/bin/node'"),
    ]
    
    original_content = activities_content
    modified = False
    
    for pattern, replacement in patterns_to_replace:
        if re.search(pattern, activities_content):
            print(f"   Found pattern: {pattern}")
            activities_content = re.sub(pattern, replacement, activities_content)
            modified = True
    
    if not modified:
        # Try finding spawn calls differently
        print("   No simple patterns found, searching for spawn calls...")
        spawn_matches = list(re.finditer(r'spawn(?:Sync)?\([^)]+\)', activities_content))
        print(f"   Found {len(spawn_matches)} spawn calls")
        
        for i, match in enumerate(spawn_matches[:5]):
            print(f"   {i+1}. {match.group()[:100]}")
        
        # Try to replace 'node' string in spawn calls
        # This is more aggressive but should work
        def replace_spawn_node(match):
            full_match = match.group(0)
            if 'Sync' in full_match:
                return full_match.replace("'node'", "process.env.NODE || '/usr/bin/node'").replace('"node"', 'process.env.NODE || "/usr/bin/node"')
            else:
                return full_match.replace("'node'", "process.env.NODE || '/usr/bin/node'").replace('"node"', 'process.env.NODE || "/usr/bin/node"')
        
        activities_content = re.sub(
            r'spawn(?:Sync)?\(["\']node["\']',
            replace_spawn_node,
            activities_content
        )
        
        if activities_content != original_content:
            modified = True
    
    if modified:
        print("\n3. Patching file...")
        
        # Write back using base64 to avoid shell escaping issues
        activities_b64 = base64.b64encode(activities_content.encode('utf-8')).decode('ascii')
        
        # Write file back
        stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "echo \'{activities_b64}\' | base64 -d > /app/dist/temporal/activities.js"')
        result = stdout.read().decode('utf-8', errors='replace')
        error = stderr.read().decode('utf-8', errors='replace')
        
        if error and 'No such file' not in error:
            print(f"   ⚠️ Error: {error}")
        else:
            print("   ✅ File patched!")
            
            # Verify
            print("\n4. Verifying patch...")
            stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} grep -n "spawn.*node\|NODE.*usr/bin" /app/dist/temporal/activities.js | head -5')
            verify = stdout.read().decode('utf-8', errors='replace')
            print(f"   {verify}")
            
            # Restart worker
            print("\n5. Restarting worker...")
            stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose restart worker')
            print(stdout.read().decode('utf-8', errors='replace'))
            
            import time
            time.sleep(5)
            
            # Check worker
            stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon | grep worker')
            worker_check = stdout.read().decode('utf-8', errors='replace')
            if worker_check:
                print("\n   ✅ Worker restarted!")
                
                # Restart backend
                print("\n6. Restarting backend...")
                stdin, stdout, stderr = ssh.exec_command('pm2 restart xaker-backend')
                print(stdout.read().decode('utf-8', errors='replace'))
                
                print("\n" + "=" * 80)
                print("✅ SUCCESS! Activities.js patched")
                print("=" * 80)
                print("\nspawn('node') replaced with spawn(process.env.NODE || '/usr/bin/node')")
                print("Try a new pentest now!")
            else:
                print("\n   ⚠️ Worker not running")
    else:
        print("\n   ⚠️ No spawn('node') patterns found")
        print("   File might be minified differently")
        print("   Showing first 500 chars of file:")
        print(activities_content[:500])
    
    ssh.close()

if __name__ == "__main__":
    import time
    patch_activities()

