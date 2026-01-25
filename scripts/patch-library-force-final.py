#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Force patch library - replace all spawn('node' with spawn('/usr/bin/node'"""

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

def force_patch():
    """Force patch library"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("FORCE PATCH LIBRARY - REPLACE spawn('node') WITH spawn('/usr/bin/node')")
    print("=" * 80)
    
    stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon | grep worker')
    worker = stdout.read().decode('utf-8', errors='replace')
    if not worker:
        print("Worker not running")
        ssh.close()
        return
    
    container_id = worker.split()[0]
    lib_file = '/app/node_modules/@anthropic-ai/claude-agent-sdk/cli.js'
    
    print(f"\n1. Reading library file ({lib_file})...")
    stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} cat {lib_file}')
    file_content = stdout.read().decode('utf-8', errors='replace')
    
    if not file_content:
        print("   ⚠️ Could not read file")
        ssh.close()
        return
    
    print(f"   File size: {len(file_content)} bytes")
    
    # Count current spawn('node') patterns
    spawn_node_patterns = [
        "spawn('node'",
        'spawn("node"',
        "spawnSync('node'",
        'spawnSync("node"',
    ]
    
    print("\n2. Counting spawn('node') patterns...")
    counts = {}
    for pattern in spawn_node_patterns:
        count = file_content.count(pattern)
        counts[pattern] = count
        if count > 0:
            print(f"   Found {count} occurrences of: {pattern}")
    
    if sum(counts.values()) == 0:
        print("   ⚠️ No spawn('node') patterns found")
        print("   File might be minified differently")
        print("   Trying to find any spawn calls with 'node'...")
        
        # Try to find spawn calls that might use node
        stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} grep -o "spawn[^(]*([^)]*node[^)]*)" {lib_file} | head -10')
        matches = stdout.read().decode('utf-8', errors='replace')
        if matches:
            print(f"   Found potential matches:\n{matches[:500]}")
        else:
            print("   No matches found")
            ssh.close()
            return
    
    # Replace all patterns
    print("\n3. Replacing spawn('node') with spawn('/usr/bin/node')...")
    original_content = file_content
    
    replacements = [
        ("spawn('node'", "spawn('/usr/bin/node'"),
        ('spawn("node"', 'spawn("/usr/bin/node"'),
        ("spawnSync('node'", "spawnSync('/usr/bin/node'"),
        ('spawnSync("node"', 'spawnSync("/usr/bin/node"'),
    ]
    
    total_replacements = 0
    for old, new in replacements:
        count = file_content.count(old)
        if count > 0:
            file_content = file_content.replace(old, new)
            total_replacements += count
            print(f"   ✅ Replaced {count} occurrences: {old} -> {new}")
    
    if total_replacements > 0 and file_content != original_content:
        print(f"\n   Total replacements: {total_replacements}")
        
        # Write back using base64
        print("\n4. Writing patched file...")
        file_b64 = base64.b64encode(file_content.encode('utf-8')).decode('ascii')
        
        # Split into chunks if too large (base64 encoding)
        chunk_size = 1000000  # 1MB chunks
        if len(file_b64) > chunk_size:
            print(f"   File is large ({len(file_b64)} bytes), writing in chunks...")
            # Write to temp file first
            stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "cat > /tmp/cli.js.b64" << \'EOF\'\n{file_b64}\nEOF')
            stdout.read()
            # Decode and move
            stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "base64 -d /tmp/cli.js.b64 > {lib_file} && rm /tmp/cli.js.b64"')
        else:
            stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "echo \'{file_b64}\' | base64 -d > {lib_file}"')
        
        error = stderr.read().decode('utf-8', errors='replace')
        
        if error and 'No such file' not in error and 'Text file busy' not in error:
            print(f"   ⚠️ Error: {error}")
        else:
            print("   ✅ File patched!")
            
            # Verify
            print("\n5. Verifying patch...")
            stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} grep -c "/usr/bin/node" {lib_file}')
            verify_count = stdout.read().decode('utf-8', errors='replace').strip()
            print(f"   Found {verify_count} occurrences of '/usr/bin/node'")
            
            # Show a sample
            stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} grep -n "spawn.*usr/bin/node" {lib_file} | head -3')
            sample = stdout.read().decode('utf-8', errors='replace')
            if sample:
                print(f"   Sample:\n{sample[:300]}")
            
            # Restart worker
            print("\n6. Restarting worker...")
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
                print("\n7. Restarting backend...")
                stdin, stdout, stderr = ssh.exec_command('pm2 restart xaker-backend')
                print(stdout.read().decode('utf-8', errors='replace'))
                
                print("\n" + "=" * 80)
                print("✅ SUCCESS! Library patched")
                print("=" * 80)
                print(f"\nReplaced {total_replacements} spawn('node') calls with spawn('/usr/bin/node')")
                print("Library will now use full path to node")
                print("\nTry a new pentest now!")
            else:
                print("\n   ⚠️ Worker not running")
    else:
        print("\n   ⚠️ No replacements made")
        print("   Library might use different pattern")
    
    ssh.close()

if __name__ == "__main__":
    import time
    force_patch()

