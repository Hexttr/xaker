#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix claude-executor.ts to pass PATH in spawn"""

import paramiko
import sys
import re

# Fix encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def fix_executor():
    """Fix claude-executor.ts"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("FIXING CLAUDE-EXECUTOR.TS")
    print("=" * 80)
    
    file_path = '/opt/xaker/shannon/src/ai/claude-executor.ts'
    
    # Read file
    print(f"\n1. Reading {file_path}...")
    sftp = ssh.open_sftp()
    try:
        with sftp.open(file_path, 'r') as f:
            content = f.read().decode('utf-8')
    except Exception as e:
        print(f"   ERROR: {e}")
        ssh.close()
        return
    
    print(f"   File size: {len(content)} bytes")
    
    # Find spawn calls
    print("\n2. Searching for spawn calls...")
    spawn_pattern = r'spawn\([^)]+\)'
    spawn_matches = list(re.finditer(spawn_pattern, content))
    print(f"   Found {len(spawn_matches)} spawn calls")
    
    for i, match in enumerate(spawn_matches[:5]):
        start = max(0, match.start() - 100)
        end = min(len(content), match.end() + 100)
        context = content[start:end]
        print(f"\n   Match {i+1} (around line {content[:match.start()].count(chr(10))+1}):")
        print(f"   {context[:200]}")
    
    # Check if PATH is already in env
    if 'process.env.PATH' in content or 'PATH:' in content:
        print("\n   ✅ PATH already referenced in code")
    else:
        print("\n   ⚠️  PATH not found in spawn calls")
    
    # Find spawn calls with node
    node_spawn_pattern = r'spawn\([\'"](node|/usr/bin/node)[\'"]'
    node_matches = list(re.finditer(node_spawn_pattern, content))
    print(f"\n3. Found {len(node_matches)} spawn calls with 'node'")
    
    # Try to fix: ensure env includes PATH
    if node_matches:
        print("\n4. Attempting to fix spawn calls...")
        lines = content.split('\n')
        modified = False
        
        for i, line in enumerate(lines):
            # Look for spawn calls
            if 'spawn(' in line and 'node' in line:
                # Check if env is passed
                if 'env:' not in line and 'env' not in line:
                    # Need to check next few lines for options
                    options_start = i
                    options_end = min(i + 10, len(lines))
                    options_block = '\n'.join(lines[options_start:options_end])
                    
                    # Check if there's already an options object
                    if '{' in options_block and '}' in options_block:
                        # Find the options object and add env
                        print(f"   Found spawn at line {i+1}, checking options...")
                        # This is complex, need to parse properly
                    else:
                        # Simple case: add env to spawn call
                        if 'spawn(' in line and ')' in line:
                            # Replace spawn('node', ...) with spawn('node', ..., {env: {...}})
                            print(f"   Line {i+1}: {line[:100]}")
        
        if not modified:
            print("   ⚠️  Could not auto-fix, manual intervention needed")
    
    # Alternative: Use full path to node
    print("\n5. Alternative: Replace 'node' with '/usr/bin/node'...")
    if "'node'" in content or '"node"' in content:
        new_content = content.replace("'node'", "'/usr/bin/node'").replace('"node"', '"/usr/bin/node"')
        if new_content != content:
            print("   ✅ Replaced 'node' with '/usr/bin/node'")
            # Write back
            with sftp.open(file_path, 'w') as f:
                f.write(new_content.encode('utf-8'))
            print("   ✅ File updated")
            
            # Rebuild
            print("\n6. Rebuilding Shannon...")
            stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && npm run build 2>&1 | tail -20')
            build_output = stdout.read().decode('utf-8', errors='replace')
            print(build_output)
            
            # Restart worker
            print("\n7. Restarting worker...")
            stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose restart worker')
            restart_output = stdout.read().decode('utf-8', errors='replace')
            print(restart_output)
        else:
            print("   ⚠️  No 'node' strings found to replace")
    else:
        print("   ⚠️  No 'node' strings found")
    
    sftp.close()
    ssh.close()
    
    print("\n" + "=" * 80)
    print("FIX COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    fix_executor()

