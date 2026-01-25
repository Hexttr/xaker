#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Patch minified file using sed"""

import paramiko
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def patch_minified():
    """Patch minified file"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("PATCHING MINIFIED FILE")
    print("=" * 80)
    
    file_path = '/app/node_modules/@anthropic-ai/claude-agent-sdk/cli.js'
    
    # Use sed to replace patterns
    print(f"\n1. Patching {file_path}...")
    
    # Try different patterns
    patterns = [
        ("spawn('node'", "spawn('/usr/bin/node'"),
        ('spawn("node"', 'spawn("/usr/bin/node"'),
        ("spawnSync('node'", "spawnSync('/usr/bin/node'"),
        ('spawnSync("node"', 'spawnSync("/usr/bin/node"'),
    ]
    
    for pattern, replacement in patterns:
        print(f"   Trying: {pattern} -> {replacement}")
        # Escape for sed
        pattern_escaped = pattern.replace("'", "'\"'\"'").replace('"', '\\"')
        replacement_escaped = replacement.replace("'", "'\"'\"'").replace('"', '\\"')
        
        cmd = f'docker exec shannon_worker_1 sed -i "s|{pattern_escaped}|{replacement_escaped}|g" {file_path} 2>&1'
        stdin, stdout, stderr = ssh.exec_command(cmd)
        result = stdout.read().decode('utf-8', errors='replace')
        errors = stderr.read().decode('utf-8', errors='replace')
        
        if not errors:
            print(f"   Pattern replaced")
        else:
            print(f"   Error: {errors[:100]}")
    
    # Verify changes
    print("\n2. Verifying changes...")
    stdin, stdout, stderr = ssh.exec_command(f'docker exec shannon_worker_1 grep -o "spawn.*node" {file_path} | head -5')
    matches = stdout.read().decode('utf-8', errors='replace')
    print(f"   Found spawn patterns: {matches[:200]}")
    
    # Restart worker
    print("\n3. Restarting worker...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose restart worker')
    print(stdout.read().decode('utf-8', errors='replace'))
    
    import time
    time.sleep(3)
    
    # Check worker logs
    print("\n4. Checking worker status...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose ps worker')
    status = stdout.read().decode('utf-8', errors='replace')
    print(status)
    
    ssh.close()
    
    print("\n" + "=" * 80)
    print("PATCH COMPLETE")
    print("=" * 80)
    print("Try a new pentest now")

if __name__ == "__main__":
    import time
    patch_minified()

