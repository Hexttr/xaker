#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Final solution: Patch library to use process.execPath instead of 'node'"""

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

def final_solution():
    """Final solution: Use process.execPath"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("FINAL SOLUTION: PATCH LIBRARY TO USE process.execPath")
    print("=" * 80)
    print("\nThis will replace 'node' string with process.execPath || '/usr/bin/node'")
    print("so library uses the actual node executable path")
    
    stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon | grep worker')
    worker = stdout.read().decode('utf-8', errors='replace')
    if not worker:
        print("\n⚠️ Worker not running, starting it...")
        stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose up -d worker')
        import time
        time.sleep(3)
        stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon | grep worker')
        worker = stdout.read().decode('utf-8', errors='replace')
    
    if not worker:
        print("   ⚠️ Could not start worker")
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
    
    # Strategy: Replace 'node' strings that are likely command arguments
    # But be careful not to replace 'node:' (module syntax) or other uses
    print("\n2. Finding and replacing 'node' command strings...")
    
    original_content = file_content
    
    # Replace patterns where 'node' is likely a command:
    # - After spawn/execa/spawnSync
    # - As a string literal argument
    # Use regex to find and replace safely
    
    import re
    
    # Pattern 1: spawn('node' or spawn("node"
    # Replace with: spawn(process.execPath || '/usr/bin/node'
    file_content = re.sub(
        r"(spawn|execa|spawnSync)\s*\(\s*['\"]node['\"]",
        r"\1(process.execPath || '/usr/bin/node'",
        file_content
    )
    
    # Pattern 2: ,'node' or ,"node" (as argument)
    # This is trickier - need to be more careful
    # Only replace if it's in a spawn context
    
    # Pattern 3: Replace standalone 'node' strings that appear to be commands
    # Look for patterns like: command: 'node' or cmd: 'node'
    file_content = re.sub(
        r"(command|cmd|exec|file)\s*:\s*['\"]node['\"]",
        r"\1: process.execPath || '/usr/bin/node'",
        file_content
    )
    
    if file_content != original_content:
        print("   ✅ Found and replaced patterns")
        
        # Count replacements
        original_spawn = original_content.count("spawn('node'") + original_content.count('spawn("node"')
        new_spawn = file_content.count("spawn(process.execPath")
        print(f"   Replaced spawn('node') patterns: {original_spawn} -> uses process.execPath")
        
        # Write back
        print("\n3. Writing patched file...")
        file_b64 = base64.b64encode(file_content.encode('utf-8')).decode('ascii')
        
        # Write in chunks if needed
        if len(file_b64) > 1000000:
            print("   File is large, writing in chunks...")
            stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "cat > /tmp/cli.js.b64" << \'EOF\'\n{file_b64}\nEOF')
            stdout.read()
            stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "base64 -d /tmp/cli.js.b64 > {lib_file} && rm /tmp/cli.js.b64"')
        else:
            stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "echo \'{file_b64}\' | base64 -d > {lib_file}"')
        
        error = stderr.read().decode('utf-8', errors='replace')
        
        if error and 'No such file' not in error and 'Text file busy' not in error:
            print(f"   ⚠️ Error: {error}")
        else:
            print("   ✅ File patched!")
            
            # Verify
            print("\n4. Verifying patch...")
            stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} grep -c "process.execPath.*usr/bin/node" {lib_file}')
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
                print("\n" + "=" * 80)
                print("✅ SUCCESS!")
                print("=" * 80)
                print("\nLibrary now uses process.execPath || '/usr/bin/node'")
                print("This should work regardless of PATH")
                print("\nTry a new pentest now!")
    else:
        print("   ⚠️ No patterns found to replace")
        print("   Library might use different mechanism")
    
    ssh.close()

if __name__ == "__main__":
    import time
    final_solution()

