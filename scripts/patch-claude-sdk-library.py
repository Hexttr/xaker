#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Patch Claude SDK library directly"""

import paramiko
import sys
import base64

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def patch_claude_sdk():
    """Patch Claude SDK library"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("PATCHING CLAUDE SDK LIBRARY")
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
    
    # Find library file
    print("\n1. Finding Claude SDK library file...")
    stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} find /app/node_modules/@anthropic-ai/claude-agent-sdk -name "*.js" -type f | head -5')
    lib_files = stdout.read().decode('utf-8', errors='replace').strip().split('\n')
    lib_files = [f for f in lib_files if f]
    
    if not lib_files:
        print("   ⚠️ Library files not found")
        ssh.close()
        return
    
    print(f"   Found {len(lib_files)} files")
    for f in lib_files:
        print(f"   - {f}")
    
    # Check each file for spawn('node')
    patched = False
    for lib_file in lib_files:
        print(f"\n2. Checking {lib_file}...")
        stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} grep -c "spawn.*node\|spawnSync.*node" {lib_file} 2>/dev/null || echo "0"')
        match_count = stdout.read().decode('utf-8', errors='replace').strip()
        
        if match_count and match_count != '0':
            print(f"   Found {match_count} spawn calls with 'node'")
            
            # Read file
            stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} cat {lib_file}')
            file_content = stdout.read().decode('utf-8', errors='replace')
            
            if not file_content:
                continue
            
            # Replace spawn('node' with spawn('/usr/bin/node'
            original_content = file_content
            
            # Try different patterns
            replacements = [
                ("spawn('node'", "spawn('/usr/bin/node'"),
                ('spawn("node"', 'spawn("/usr/bin/node"'),
                ("spawnSync('node'", "spawnSync('/usr/bin/node'"),
                ('spawnSync("node"', 'spawnSync("/usr/bin/node"'),
            ]
            
            for old, new in replacements:
                if old in file_content:
                    file_content = file_content.replace(old, new)
                    print(f"   ✅ Replaced {old} with {new}")
                    patched = True
            
            if patched and file_content != original_content:
                # Write back using base64
                print(f"\n3. Writing patched file...")
                file_b64 = base64.b64encode(file_content.encode('utf-8')).decode('ascii')
                
                # Write file back
                stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "echo \'{file_b64}\' | base64 -d > {lib_file}"')
                error = stderr.read().decode('utf-8', errors='replace')
                
                if error and 'No such file' not in error:
                    print(f"   ⚠️ Error: {error}")
                else:
                    print(f"   ✅ File patched: {lib_file}")
                    
                    # Verify
                    stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} grep -n "/usr/bin/node" {lib_file} | head -3')
                    verify = stdout.read().decode('utf-8', errors='replace')
                    if verify:
                        print(f"   Verification:\n{verify}")
                    break
    
    if patched:
        # Restart worker
        print("\n4. Restarting worker...")
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
            print("\n5. Restarting backend...")
            stdin, stdout, stderr = ssh.exec_command('pm2 restart xaker-backend')
            print(stdout.read().decode('utf-8', errors='replace'))
            
            print("\n" + "=" * 80)
            print("✅ SUCCESS! Library patched")
            print("=" * 80)
            print("\nspawn('node') replaced with spawn('/usr/bin/node')")
            print("Try a new pentest now!")
        else:
            print("\n   ⚠️ Worker not running")
    else:
        print("\n   ⚠️ No spawn('node') patterns found in library files")
        print("   Library might be minified or use different pattern")
    
    ssh.close()

if __name__ == "__main__":
    import time
    patch_claude_sdk()

