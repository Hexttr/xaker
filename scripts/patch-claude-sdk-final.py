#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Patch Claude SDK library - final attempt"""

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

def patch_final():
    """Patch final"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("PATCHING CLAUDE SDK - FINAL")
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
    
    lib_file = '/app/node_modules/@anthropic-ai/claude-agent-sdk/cli.js'
    
    # Read file
    print("\n1. Reading library file...")
    stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} cat {lib_file}')
    file_content = stdout.read().decode('utf-8', errors='replace')
    
    if not file_content:
        print("   ⚠️ Could not read file")
        ssh.close()
        return
    
    print(f"   File size: {len(file_content)} bytes")
    
    # Find spawn patterns
    print("\n2. Searching for spawn patterns...")
    stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} grep -o "spawn[^(]*node[^)]*" {lib_file} | head -5')
    spawn_patterns = stdout.read().decode('utf-8', errors='replace')
    print(f"   Found patterns:\n{spawn_patterns}")
    
    # Try to replace all variations
    original_content = file_content
    replacements_made = 0
    
    # Replace patterns - try different variations
    replacements = [
        # Direct string replacements
        ("spawn('node'", "spawn('/usr/bin/node'"),
        ('spawn("node"', 'spawn("/usr/bin/node"'),
        ("spawnSync('node'", "spawnSync('/usr/bin/node'"),
        ('spawnSync("node"', 'spawnSync("/usr/bin/node"'),
        # With spaces
        ("spawn( 'node'", "spawn( '/usr/bin/node'"),
        ('spawn( "node"', 'spawn( "/usr/bin/node"'),
        # Minified might use different quotes or no spaces
        ("spawn('node'", "spawn('/usr/bin/node'"),
        ('spawn("node"', 'spawn("/usr/bin/node"'),
    ]
    
    for old, new in replacements:
        count = file_content.count(old)
        if count > 0:
            file_content = file_content.replace(old, new)
            replacements_made += count
            print(f"   ✅ Replaced {count} occurrences: {old} -> {new}")
    
    if replacements_made > 0 and file_content != original_content:
        print(f"\n3. Total replacements: {replacements_made}")
        
        # Write back using base64
        print("   Writing patched file...")
        file_b64 = base64.b64encode(file_content.encode('utf-8')).decode('ascii')
        
        # Write file back
        stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "echo \'{file_b64}\' | base64 -d > {lib_file}"')
        error = stderr.read().decode('utf-8', errors='replace')
        
        if error and 'No such file' not in error and 'Text file busy' not in error:
            print(f"   ⚠️ Error: {error}")
        else:
            print("   ✅ File patched!")
            
            # Verify
            print("\n4. Verifying patch...")
            stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} grep -c "/usr/bin/node" {lib_file}')
            verify_count = stdout.read().decode('utf-8', errors='replace').strip()
            print(f"   Found {verify_count} occurrences of '/usr/bin/node'")
            
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
                print("✅ SUCCESS! Library patched")
                print("=" * 80)
                print(f"\nReplaced {replacements_made} spawn('node') calls with spawn('/usr/bin/node')")
                print("Try a new pentest now!")
            else:
                print("\n   ⚠️ Worker not running")
    else:
        print("\n   ⚠️ No replacements made")
        print("   Showing first 1000 chars of file to understand structure:")
        print(file_content[:1000])
    
    ssh.close()

if __name__ == "__main__":
    import time
    patch_final()

