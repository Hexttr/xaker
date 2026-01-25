#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix entrypoint to create symlink permanently"""

import paramiko
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def fix_entrypoint():
    """Fix entrypoint"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("FIXING ENTRYPOINT PERMANENTLY")
    print("=" * 80)
    
    # Read docker-compose.yml
    print("\n1. Reading docker-compose.yml...")
    sftp = ssh.open_sftp()
    with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'r') as f:
        content = f.read().decode('utf-8')
    
    lines = content.split('\n')
    new_lines = []
    entrypoint_found = False
    
    for i, line in enumerate(lines):
        if 'worker:' in line:
            new_lines.append(line)
            # Find entrypoint/command
            j = i + 1
            while j < len(lines) and (lines[j].startswith(' ') or lines[j].startswith('\t')):
                if 'entrypoint:' in lines[j] or 'command:' in lines[j]:
                    # Update entrypoint to create symlink first
                    new_lines.append('    entrypoint: ["/bin/sh", "-c"]')
                    new_lines.append('    command: "mkdir -p /usr/local/bin && ln -sf /usr/bin/node /usr/local/bin/node 2>/dev/null || true && exec node dist/temporal/worker.js"')
                    entrypoint_found = True
                    # Skip old entrypoint/command
                    while j < len(lines) and (lines[j].startswith(' ') or lines[j].startswith('\t')):
                        if 'entrypoint:' in lines[j] or 'command:' in lines[j]:
                            j += 1
                            continue
                        if not lines[j].startswith(' ') and not lines[j].startswith('\t'):
                            break
                        j += 1
                    break
                new_lines.append(lines[j])
                j += 1
            # Add remaining lines
            while j < len(lines):
                new_lines.append(lines[j])
                j += 1
            break
        else:
            new_lines.append(line)
    
    if not entrypoint_found:
        # Add entrypoint if not found
        for i, line in enumerate(lines):
            if 'worker:' in line:
                new_lines.append(line)
                # Find where to add
                j = i + 1
                while j < len(lines) and (lines[j].startswith(' ') or lines[j].startswith('\t')):
                    new_lines.append(lines[j])
                    j += 1
                # Add entrypoint before next service
                new_lines.append('    entrypoint: ["/bin/sh", "-c"]')
                new_lines.append('    command: "mkdir -p /usr/local/bin && ln -sf /usr/bin/node /usr/local/bin/node 2>/dev/null || true && exec node dist/temporal/worker.js"')
                # Add remaining
                while j < len(lines):
                    new_lines.append(lines[j])
                    j += 1
                break
            else:
                new_lines.append(line)
    
    # Write back
    print("\n2. Writing updated docker-compose.yml...")
    with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'w') as f:
        f.write('\n'.join(new_lines).encode('utf-8'))
    
    sftp.close()
    
    # Verify
    print("\n3. Verifying changes...")
    stdin, stdout, stderr = ssh.exec_command('grep -A 2 "worker:" /opt/xaker/shannon/docker-compose.yml | grep -A 2 entrypoint')
    verify = stdout.read().decode('utf-8', errors='replace')
    print(verify)
    
    # Restart worker
    print("\n4. Restarting worker...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose restart worker')
    restart_output = stdout.read().decode('utf-8', errors='replace')
    print(restart_output)
    
    import time
    time.sleep(5)
    
    # Verify symlink
    print("\n5. Verifying symlink...")
    stdin, stdout, stderr = ssh.exec_command('docker exec shannon_worker_1 ls -la /usr/local/bin/node')
    symlink = stdout.read().decode('utf-8', errors='replace')
    print(symlink)
    
    ssh.close()
    
    print("\n" + "=" * 80)
    print("FIX COMPLETE")
    print("=" * 80)
    if 'node' in symlink.lower() and '->' in symlink:
        print("SUCCESS! Entrypoint updated, symlink created automatically")
        print("Try a new pentest now")
    else:
        print("Symlink may not be created - check entrypoint")

if __name__ == "__main__":
    import time
    fix_entrypoint()

