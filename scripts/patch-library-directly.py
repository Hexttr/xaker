#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Patch library directly to use full path to node"""

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

def patch_library():
    """Patch library directly"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("PATCHING LIBRARY DIRECTLY")
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
    
    # Find files with spawn('node')
    print("\n1. Finding files with spawn('node')...")
    stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} find /app/node_modules/@anthropic-ai -name "*.js" -type f -exec grep -l "spawn.*node" {{}} \\; 2>/dev/null | head -5')
    files = stdout.read().decode('utf-8', errors='replace').strip().split('\n')
    files = [f for f in files if f]
    
    if not files:
        print("   No files found, searching in dist...")
        stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} find /app/dist -name "*.js" -type f -exec grep -l "spawn.*node" {{}} \\; 2>/dev/null | head -5')
        files = stdout.read().decode('utf-8', errors='replace').strip().split('\n')
        files = [f for f in files if f]
    
    if files:
        print(f"   Found {len(files)} files:")
        for f in files:
            print(f"   - {f}")
        
        # Patch first file
        file_path = files[0]
        print(f"\n2. Patching {file_path}...")
        
        # Read file
        stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} cat {file_path}')
        file_content = stdout.read().decode('utf-8', errors='replace')
        
        # Replace spawn('node' with spawn(process.env.NODE || '/usr/bin/node'
        original_content = file_content
        file_content = file_content.replace("spawn('node'", "spawn(process.env.NODE || '/usr/bin/node'")
        file_content = file_content.replace('spawn("node"', 'spawn(process.env.NODE || "/usr/bin/node"')
        file_content = file_content.replace("spawnSync('node'", "spawnSync(process.env.NODE || '/usr/bin/node'")
        file_content = file_content.replace('spawnSync("node"', 'spawnSync(process.env.NODE || "/usr/bin/node"')
        
        if file_content != original_content:
            print("   ✅ Found spawn('node') calls, patching...")
            
            # Write back using base64 to avoid shell escaping issues
            file_content_b64 = base64.b64encode(file_content.encode('utf-8')).decode('ascii')
            
            # Write file back
            stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "echo \'{file_content_b64}\' | base64 -d > {file_path}"')
            result = stdout.read().decode('utf-8', errors='replace')
            error = stderr.read().decode('utf-8', errors='replace')
            
            if error:
                print(f"   ⚠️ Error: {error}")
            else:
                print("   ✅ File patched!")
                
                # Verify
                stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} grep -n "spawn.*node" {file_path} | head -3')
                verify = stdout.read().decode('utf-8', errors='replace')
                print(f"\n   Verification:\n{verify}")
                
                # Restart worker
                print("\n3. Restarting worker...")
                stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose restart worker')
                print(stdout.read().decode('utf-8', errors='replace'))
                
                time.sleep(3)
                
                # Restart backend
                print("\n4. Restarting backend...")
                stdin, stdout, stderr = ssh.exec_command('pm2 restart xaker-backend')
                print(stdout.read().decode('utf-8', errors='replace'))
                
                print("\n" + "=" * 80)
                print("✅ SUCCESS! Library patched")
                print("=" * 80)
                print("\nTry a new pentest now!")
        else:
            print("   ⚠️ No simple spawn('node') patterns found")
            print("   File might be minified or use different pattern")
    else:
        print("   ⚠️ No files found with spawn('node')")
        print("   The library might use a different method")
    
    ssh.close()

if __name__ == "__main__":
    import time
    patch_library()

