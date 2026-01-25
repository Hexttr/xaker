#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Force patch library by replacing 'node' with '/usr/bin/node'"""

import paramiko
import sys

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
    print("FORCE PATCHING LIBRARY")
    print("=" * 80)
    
    file_path = '/app/node_modules/@anthropic-ai/claude-agent-sdk/cli.js'
    
    print(f"\n1. Reading {file_path}...")
    # Read file in chunks
    stdin, stdout, stderr = ssh.exec_command(f'docker exec shannon_worker_1 wc -l {file_path}')
    line_count = int(stdout.read().decode('utf-8', errors='replace').split()[0])
    print(f"   File has {line_count} lines")
    
    # Use sed to replace all occurrences
    print("\n2. Patching file with sed...")
    
    # Replace patterns using sed
    patterns = [
        ("spawn('node'", "spawn('/usr/bin/node'"),
        ('spawn("node"', 'spawn("/usr/bin/node"'),
        ("spawnSync('node'", "spawnSync('/usr/bin/node'"),
        ('spawnSync("node"', 'spawnSync("/usr/bin/node"'),
    ]
    
    for pattern, replacement in patterns:
        print(f"   Replacing: {pattern} -> {replacement}")
        # Escape for sed
        pattern_escaped = pattern.replace("'", "'\"'\"'").replace('"', '\\"')
        replacement_escaped = replacement.replace("'", "'\"'\"'").replace('"', '\\"')
        
        cmd = f'docker exec shannon_worker_1 sed -i "s|{pattern_escaped}|{replacement_escaped}|g" {file_path} 2>&1'
        stdin, stdout, stderr = ssh.exec_command(cmd)
        result = stdout.read().decode('utf-8', errors='replace')
        errors = stderr.read().decode('utf-8', errors='replace')
        
        if errors:
            print(f"   Error: {errors[:200]}")
        else:
            print(f"   Pattern replaced")
    
    # Verify changes
    print("\n3. Verifying changes...")
    stdin, stdout, stderr = ssh.exec_command(f'docker exec shannon_worker_1 grep -o "spawn.*node" {file_path} | head -5')
    matches = stdout.read().decode('utf-8', errors='replace')
    print(f"   Found patterns: {matches[:500]}")
    
    # Count replacements
    stdin, stdout, stderr = ssh.exec_command(f'docker exec shannon_worker_1 grep -c "/usr/bin/node" {file_path}')
    count = stdout.read().decode('utf-8', errors='replace').strip()
    print(f"   Found {count} occurrences of /usr/bin/node")
    
    # Restart worker
    print("\n4. Restarting worker...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose restart worker')
    restart_output = stdout.read().decode('utf-8', errors='replace')
    print(restart_output)
    
    import time
    time.sleep(5)
    
    # Check worker logs
    print("\n5. Checking worker status...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose ps worker')
    status = stdout.read().decode('utf-8', errors='replace')
    print(status)
    
    ssh.close()
    
    print("\n" + "=" * 80)
    print("FORCE PATCH COMPLETE")
    print("=" * 80)
    if count and int(count) > 0:
        print(f"SUCCESS! Replaced {count} occurrences")
        print("Try a new pentest now")
    else:
        print("No replacements found - file may not be patched")

if __name__ == "__main__":
    import time
    force_patch()

