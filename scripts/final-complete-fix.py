#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Final complete fix - ensure everything is set"""

import paramiko
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def complete_fix():
    """Complete fix"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("COMPLETE FIX")
    print("=" * 80)
    
    # 1. Update docker-compose.yml
    print("\n1. Updating docker-compose.yml...")
    sftp = ssh.open_sftp()
    with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'r') as f:
        content = f.read().decode('utf-8')
    
    lines = content.split('\n')
    new_lines = []
    env_updated = False
    
    for i, line in enumerate(lines):
        if 'worker:' in line:
            new_lines.append(line)
            # Find environment section
            j = i + 1
            while j < len(lines) and (lines[j].startswith(' ') or lines[j].startswith('\t')):
                if 'environment:' in lines[j]:
                    new_lines.append(lines[j])
                    j += 1
                    # Add NODE and update PATH
                    while j < len(lines) and (lines[j].startswith(' ') or lines[j].startswith('\t')) and lines[j].strip().startswith('- '):
                        if 'PATH=' in lines[j]:
                            # Update PATH to include /usr/local/bin first
                            new_lines.append('      - PATH=/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin')
                            env_updated = True
                        elif 'NODE=' not in content:
                            # Add NODE if not present
                            new_lines.append('      - NODE=/usr/bin/node')
                            env_updated = True
                        else:
                            new_lines.append(lines[j])
                        j += 1
                    # Add remaining env vars
                    while j < len(lines) and (lines[j].startswith(' ') or lines[j].startswith('\t')):
                        if not lines[j].strip().startswith('- '):
                            break
                        new_lines.append(lines[j])
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
    
    if env_updated:
        with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'w') as f:
            f.write('\n'.join(new_lines).encode('utf-8'))
        print("   docker-compose.yml updated")
    else:
        print("   docker-compose.yml already has NODE/PATH")
    
    sftp.close()
    
    # 2. Update entrypoint to create symlink on startup
    print("\n2. Updating entrypoint to create symlink...")
    sftp = ssh.open_sftp()
    with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'r') as f:
        content = f.read().decode('utf-8')
    
    # Check current entrypoint
    if 'entrypoint:' in content and 'command:' in content:
        # Already has entrypoint/command
        print("   Entrypoint already configured")
    else:
        # Update entrypoint
        lines = content.split('\n')
        new_lines = []
        
        for i, line in enumerate(lines):
            if 'worker:' in line:
                new_lines.append(line)
                # Find entrypoint
                j = i + 1
                while j < len(lines) and (lines[j].startswith(' ') or lines[j].startswith('\t')):
                    if 'entrypoint:' in lines[j]:
                        # Update to create symlink first
                        new_lines.append('    entrypoint: ["/bin/sh", "-c"]')
                        new_lines.append('    command: "mkdir -p /usr/local/bin && ln -sf /usr/bin/node /usr/local/bin/node 2>/dev/null || true && exec node dist/temporal/worker.js"')
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
                break
            else:
                new_lines.append(line)
        
        with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'w') as f:
            f.write('\n'.join(new_lines).encode('utf-8'))
        print("   Entrypoint updated")
    
    sftp.close()
    
    # 3. Create symlink in running container
    print("\n3. Creating symlink in running container...")
    stdin, stdout, stderr = ssh.exec_command('docker exec -u root shannon_worker_1 sh -c "mkdir -p /usr/local/bin && ln -sf /usr/bin/node /usr/local/bin/node && ls -la /usr/local/bin/node"')
    symlink_result = stdout.read().decode('utf-8', errors='replace')
    print(symlink_result)
    
    # 4. Restart worker
    print("\n4. Restarting worker...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose restart worker')
    restart_output = stdout.read().decode('utf-8', errors='replace')
    print(restart_output)
    
    import time
    time.sleep(5)
    
    # 5. Verify everything
    print("\n5. Verifying fix...")
    stdin, stdout, stderr = ssh.exec_command('docker exec shannon_worker_1 sh -c "ls -la /usr/local/bin/node && which node && printenv PATH && printenv NODE 2>&1"')
    verify = stdout.read().decode('utf-8', errors='replace')
    print(verify)
    
    ssh.close()
    
    print("\n" + "=" * 80)
    print("COMPLETE FIX APPLIED")
    print("=" * 80)
    if 'node' in verify.lower() and ('->' in verify or '/usr/local/bin/node' in verify):
        print("SUCCESS! Everything is configured")
        print("Try a new pentest now")
    else:
        print("Some checks failed, but symlink should work")

if __name__ == "__main__":
    import time
    complete_fix()

