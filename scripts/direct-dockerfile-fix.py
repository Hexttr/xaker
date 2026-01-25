#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Direct Dockerfile fix"""

import paramiko
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def direct_fix():
    """Direct fix"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("DIRECT DOCKERFILE FIX")
    print("=" * 80)
    
    # Read Dockerfile
    sftp = ssh.open_sftp()
    with sftp.open('/opt/xaker/shannon/Dockerfile', 'r') as f:
        content = f.read().decode('utf-8')
    
    lines = content.split('\n')
    new_lines = []
    user_found = False
    wrapper_added = False
    
    for i, line in enumerate(lines):
        if 'USER pentest' in line and not wrapper_added:
            # Insert wrapper creation BEFORE USER
            new_lines.append('# Create node wrapper for pentest user')
            new_lines.append('RUN mkdir -p /app/bin && \\')
            new_lines.append('    echo "#!/bin/sh" > /app/bin/node && \\')
            new_lines.append('    echo "exec /usr/bin/node \\"$@\\"" >> /app/bin/node && \\')
            new_lines.append('    chmod +x /app/bin/node')
            new_lines.append('ENV PATH="/app/bin:$PATH"')
            new_lines.append('')
            new_lines.append(line)
            wrapper_added = True
            user_found = True
            print(f"Added wrapper before USER pentest at line {i+1}")
        else:
            new_lines.append(line)
    
    # Write back
    with sftp.open('/opt/xaker/shannon/Dockerfile', 'w') as f:
        f.write('\n'.join(new_lines).encode('utf-8'))
    
    sftp.close()
    
    # Verify
    print("\nVerifying Dockerfile...")
    stdin, stdout, stderr = ssh.exec_command('grep -B 5 "USER pentest" /opt/xaker/shannon/Dockerfile | head -8')
    verify = stdout.read().decode('utf-8', errors='replace')
    print(verify)
    
    # Rebuild command
    print("\n" + "=" * 80)
    print("Dockerfile fixed!")
    print("=" * 80)
    print("Now run on server:")
    print("cd /opt/xaker/shannon")
    print("docker-compose stop worker")
    print("docker-compose rm -f worker")
    print("docker-compose build --no-cache worker")
    print("docker-compose up -d worker")
    print("docker exec shannon_worker_1 ls -la /app/bin/node")
    
    ssh.close()

if __name__ == "__main__":
    direct_fix()

