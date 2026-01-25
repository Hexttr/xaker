#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ultimate fix: Replace 'node' string with '/usr/bin/node' in command context"""

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

def ultimate_fix():
    """Ultimate fix"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("ULTIMATE FIX: REPLACE 'node' WITH '/usr/bin/node'")
    print("=" * 80)
    
    # Start worker if not running
    stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon | grep worker')
    worker = stdout.read().decode('utf-8', errors='replace')
    if not worker:
        print("\nStarting worker...")
        stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose up -d worker')
        import time
        time.sleep(5)
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
    
    # Strategy: Replace 'node' strings that appear to be commands
    # Be very careful not to break the code
    print("\n2. Replacing 'node' command strings...")
    
    original_content = file_content
    
    # Replace 'node' with '/usr/bin/node' but only in command contexts
    # This is risky but necessary
    
    # Method: Replace 'node' string literals that are likely commands
    # We'll replace standalone 'node' strings, but be careful about 'node:'
    
    # Simple approach: Replace all 'node' strings except those followed by ':'
    # This will catch 'node' as command but not 'node:module' syntax
    
    # But this is too risky - might break things
    # Instead, let's replace specific patterns we know are commands
    
    # Pattern: strings like 'node' that appear after spawn/execa
    import re
    
    # Find all 'node' strings and their context
    # Replace only those that appear to be commands
    
    # More conservative: Replace only in spawn/execa contexts
    # Look for patterns like: spawn('node', ...) or execa('node', ...)
    
    # Try to find the exact pattern
    # In minified code, it might be: spawn('node' or spawn("node"
    
    # Replace with full path
    replacements = 0
    
    # Pattern 1: Direct spawn('node' or spawn("node"
    patterns = [
        (r"spawn\s*\(\s*['\"]node['\"]", r"spawn('/usr/bin/node'"),
        (r'spawn\s*\(\s*["\']node["\']', r'spawn("/usr/bin/node"'),
        (r"execa\s*\(\s*['\"]node['\"]", r"execa('/usr/bin/node'"),
        (r'execa\s*\(\s*["\']node["\']', r'execa("/usr/bin/node"'),
        (r"spawnSync\s*\(\s*['\"]node['\"]", r"spawnSync('/usr/bin/node'"),
        (r'spawnSync\s*\(\s*["\']node["\']', r'spawnSync("/usr/bin/node"'),
    ]
    
    for pattern, replacement in patterns:
        matches = len(re.findall(pattern, file_content))
        if matches > 0:
            file_content = re.sub(pattern, replacement, file_content)
            replacements += matches
            print(f"   ✅ Replaced {matches} occurrences: {pattern}")
    
    if replacements > 0 and file_content != original_content:
        print(f"\n   Total replacements: {replacements}")
        
        # Write back
        print("\n3. Writing patched file...")
        file_b64 = base64.b64encode(file_content.encode('utf-8')).decode('ascii')
        
        # Write using heredoc to avoid shell escaping issues
        stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "cat > /tmp/cli.js.b64" << \'ENDOFFILE\'\n{file_b64}\nENDOFFILE')
        stdout.read()
        
        stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "base64 -d /tmp/cli.js.b64 > {lib_file} && rm /tmp/cli.js.b64"')
        error = stderr.read().decode('utf-8', errors='replace')
        
        if error and 'No such file' not in error:
            print(f"   ⚠️ Error: {error}")
        else:
            print("   ✅ File patched!")
            
            # Verify
            print("\n4. Verifying...")
            stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} grep -c "/usr/bin/node" {lib_file}')
            verify = stdout.read().decode('utf-8', errors='replace').strip()
            print(f"   Found {verify} occurrences of '/usr/bin/node'")
            
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
                print(f"\nReplaced {replacements} spawn('node') calls with spawn('/usr/bin/node')")
                print("Library will now use full path to node")
                print("\nTry a new pentest now!")
    else:
        print("   ⚠️ No patterns found to replace")
        print("   Library might use different mechanism")
        print("   Showing first 2000 chars of file to understand structure:")
        print(file_content[:2000])
    
    ssh.close()

if __name__ == "__main__":
    import time
    ultimate_fix()

