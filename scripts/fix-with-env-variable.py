#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix by setting NODE environment variable"""

import paramiko
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def fix_with_env():
    """Fix by setting NODE env variable"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("FIXING WITH ENVIRONMENT VARIABLE")
    print("=" * 80)
    
    # Update docker-compose.yml to add NODE env variable
    print("\n1. Updating docker-compose.yml...")
    sftp = ssh.open_sftp()
    with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'r') as f:
        content = f.read().decode('utf-8')
    
    # Check if NODE is already set
    if 'NODE=' in content and 'worker:' in content:
        print("   NODE already set")
    else:
        # Add NODE environment variable
        lines = content.split('\n')
        new_lines = []
        node_added = False
        
        for i, line in enumerate(lines):
            new_lines.append(line)
            
            if 'worker:' in line:
                # Find environment section
                j = i + 1
                while j < len(lines) and (lines[j].startswith(' ') or lines[j].startswith('\t')):
                    if 'environment:' in lines[j]:
                        # Add NODE after environment
                        new_lines.append('      - NODE=/usr/bin/node')
                        new_lines.append('      - PATH=/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin')
                        node_added = True
                        print("   Added NODE and PATH to environment")
                        break
                    new_lines.append(lines[j])
                    j += 1
                if node_added:
                    # Skip lines we already added
                    while j < len(lines) and (lines[j].startswith(' ') or lines[j].startswith('\t')):
                        new_lines.append(lines[j])
                        j += 1
                    break
        
        if node_added:
            with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'w') as f:
                f.write('\n'.join(new_lines).encode('utf-8'))
            print("   docker-compose.yml updated")
    
    sftp.close()
    
    # Verify
    print("\n2. Verifying docker-compose.yml...")
    stdin, stdout, stderr = ssh.exec_command('grep -A 10 "worker:" /opt/xaker/shannon/docker-compose.yml | grep -E "NODE|PATH" | head -5')
    verify = stdout.read().decode('utf-8', errors='replace')
    print(verify)
    
    # Restart worker
    print("\n3. Restarting worker...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose restart worker')
    restart_output = stdout.read().decode('utf-8', errors='replace')
    print(restart_output)
    
    import time
    time.sleep(3)
    
    # Verify env variables
    print("\n4. Verifying environment variables...")
    stdin, stdout, stderr = ssh.exec_command('docker exec shannon_worker_1 printenv | grep -E "NODE|PATH"')
    env_vars = stdout.read().decode('utf-8', errors='replace')
    print(env_vars)
    
    # Verify symlink
    print("\n5. Verifying symlink...")
    stdin, stdout, stderr = ssh.exec_command('docker exec shannon_worker_1 ls -la /usr/local/bin/node')
    symlink = stdout.read().decode('utf-8', errors='replace')
    print(symlink)
    
    ssh.close()
    
    print("\n" + "=" * 80)
    print("FIX COMPLETE")
    print("=" * 80)
    print("NODE and PATH environment variables set")
    print("Symlink created")
    print("Try a new pentest now")

if __name__ == "__main__":
    import time
    fix_with_env()

