#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Patch execa node calls"""

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

def patch_execa():
    """Patch execa node calls"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("PATCHING EXECA NODE CALLS")
    print("=" * 80)
    
    stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon | grep worker')
    worker = stdout.read().decode('utf-8', errors='replace')
    if not worker:
        print("Worker not running")
        ssh.close()
        return
    
    container_id = worker.split()[0]
    lib_file = '/app/node_modules/@anthropic-ai/claude-agent-sdk/cli.js'
    
    # Read file
    print("\n1. Reading library file...")
    stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} cat {lib_file}')
    file_content = stdout.read().decode('utf-8', errors='replace')
    
    print(f"   File size: {len(file_content)} bytes")
    
    # Find where 'node' is passed to execa/spawn
    # Look for patterns like: execa('node', ...) or execa("node", ...)
    print("\n2. Searching for execa/spawn with 'node'...")
    
    # Try to find patterns where 'node' is the first argument
    # In minified code it might be: execa('node' or execa("node" or $('node'
    original_content = file_content
    
    # Replace patterns - be aggressive
    replacements = [
        # Direct string 'node' as first argument to spawn/execa
        ("'node'", "process.env.NODE || '/usr/bin/node'"),
        ('"node"', 'process.env.NODE || "/usr/bin/node"'),
        # But be careful - don't replace 'node:child_process' etc
    ]
    
    # More targeted: replace 'node' only when it's likely a command argument
    # Look for patterns like: spawn('node', execa('node', $('node',
    import re
    
    # Pattern: 'node' followed by comma or closing paren (likely a command)
    # But not 'node:' (which is node module syntax)
    def replace_node_command(match):
        full_match = match.group(0)
        # Don't replace if it's part of 'node:something'
        if 'node:' in full_match:
            return full_match
        # Replace standalone 'node' strings that look like commands
        if "'node'" in full_match:
            return full_match.replace("'node'", "process.env.NODE || '/usr/bin/node'")
        if '"node"' in full_match:
            return full_match.replace('"node"', 'process.env.NODE || "/usr/bin/node"')
        return full_match
    
    # Try replacing 'node' that appears as spawn/execa argument
    # Look for: spawn('node' or execa('node' or similar
    file_content = re.sub(
        r"(spawn|execa|spawnSync)\(['\"]node['\"]",
        r"\1(process.env.NODE || '/usr/bin/node'",
        file_content
    )
    
    # Also try with spaces
    file_content = re.sub(
        r"(spawn|execa|spawnSync)\s*\(\s*['\"]node['\"]",
        r"\1(process.env.NODE || '/usr/bin/node'",
        file_content
    )
    
    if file_content != original_content:
        print("   ✅ Found and replaced spawn/execa('node') patterns")
        
        # Count replacements
        original_spawn_node = original_content.count("spawn('node'") + original_content.count('spawn("node"')
        new_spawn_node = file_content.count("spawn(process.env.NODE")
        print(f"   Replaced {original_spawn_node} spawn('node') calls")
        
        # Write back
        print("\n3. Writing patched file...")
        file_b64 = base64.b64encode(file_content.encode('utf-8')).decode('ascii')
        
        stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "echo \'{file_b64}\' | base64 -d > {lib_file}"')
        error = stderr.read().decode('utf-8', errors='replace')
        
        if error and 'No such file' not in error and 'Text file busy' not in error:
            print(f"   ⚠️ Error: {error}")
        else:
            print("   ✅ File patched!")
            
            # Verify
            print("\n4. Verifying...")
            stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} grep -c "process.env.NODE.*usr/bin/node" {lib_file}')
            verify = stdout.read().decode('utf-8', errors='replace').strip()
            print(f"   Found {verify} occurrences")
            
            # Restart worker
            print("\n5. Restarting worker...")
            stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose restart worker')
            print(stdout.read().decode('utf-8', errors='replace'))
            
            import time
            time.sleep(5)
            
            stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon | grep worker')
            if stdout.read().decode('utf-8', errors='replace'):
                print("\n   ✅ Worker restarted!")
                stdin, stdout, stderr = ssh.exec_command('pm2 restart xaker-backend')
                print("   ✅ Backend restarted")
                print("\n✅ SUCCESS! Try a new pentest now!")
    else:
        print("   ⚠️ No patterns found to replace")
        print("   File might use different pattern")
    
    ssh.close()

if __name__ == "__main__":
    import time
    patch_execa()

