#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Patch library using Python"""

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

def patch_with_python():
    """Patch with Python"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("PATCH LIBRARY USING PYTHON")
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
    
    print(f"\n1. Reading library file...")
    stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} cat {lib_file}')
    file_content = stdout.read().decode('utf-8', errors='replace')
    
    if not file_content:
        print("   ⚠️ Could not read file")
        ssh.close()
        return
    
    print(f"   File size: {len(file_content)} bytes")
    
    # Find all occurrences of 'node' that might be commands
    print("\n2. Finding 'node' command patterns...")
    
    # Look for patterns like: spawn('node', spawn("node", execa('node', etc.
    # But exclude 'node:' (module syntax)
    
    original_content = file_content
    
    # Use regex to find and replace
    # Pattern: spawn/execa/spawnSync followed by ( then 'node' or "node"
    patterns = [
        (r"(spawn|execa|spawnSync)\s*\(\s*['\"]node['\"]", r"\1('/usr/bin/node'"),
        (r"(spawn|execa|spawnSync)\s*\(\s*[\"']node[\"']", r'\1("/usr/bin/node"'),
    ]
    
    replacements = 0
    for pattern, replacement in patterns:
        matches = len(re.findall(pattern, file_content))
        if matches > 0:
            file_content = re.sub(pattern, replacement, file_content)
            replacements += matches
            print(f"   ✅ Replaced {matches} occurrences: {pattern}")
    
    # Also try simple string replacement for 'node' -> '/usr/bin/node'
    # But only if it's not part of 'node:' or other contexts
    # This is risky but might work
    
    # Count how many 'node' strings exist (excluding 'node:')
    node_count = len(re.findall(r"(?<!node:)(?<!node\.)(?<!node\[)['\"]node['\"]", file_content))
    print(f"   Found {node_count} potential 'node' command strings")
    
    if replacements > 0 or file_content != original_content:
        print(f"\n3. Total replacements: {replacements}")
        
        # Write back using base64
        print("   Writing patched file...")
        file_b64 = base64.b64encode(file_content.encode('utf-8')).decode('ascii')
        
        # Write in chunks if needed
        if len(file_b64) > 1000000:
            print("   File is large, writing in chunks...")
            # Use heredoc
            stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "cat > /tmp/cli.js.b64" << \'ENDOFFILE\'\n{file_b64}\nENDOFFILE')
            stdout.read()
            stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "base64 -d /tmp/cli.js.b64 > {lib_file} && rm /tmp/cli.js.b64"')
        else:
            stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "echo \'{file_b64}\' | base64 -d > {lib_file}"')
        
        error = stderr.read().decode('utf-8', errors='replace')
        if error and 'No such file' not in error:
            print(f"   ⚠️ Error: {error[:200]}")
        else:
            print("   ✅ File patched!")
            
            # Verify
            print("\n4. Verifying...")
            stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} grep -c "/usr/bin/node" {lib_file}')
            verify = stdout.read().decode('utf-8', errors='replace').strip()
            print(f"   Found {verify} occurrences of '/usr/bin/node'")
            
            if verify != '0':
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
                        print(f"\nLibrary patched: {replacements} replacements")
                        print("Worker is running")
                        print("\nTry a new pentest now!")
            else:
                print("   ⚠️ No replacements found after write")
    else:
        print("\n   ⚠️ No patterns found to replace")
        print("   Showing first 2000 chars to understand structure:")
        print(file_content[:2000])
    
    ssh.close()

if __name__ == "__main__":
    import time
    patch_with_python()

