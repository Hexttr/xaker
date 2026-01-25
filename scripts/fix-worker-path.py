#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix PATH in docker-compose.yml for worker"""

import paramiko
import sys

# Fix encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def fix_compose():
    """Fix docker-compose.yml"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    # Read file
    sftp = ssh.open_sftp()
    with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'r') as f:
        content = f.read().decode('utf-8')
    
    # Check if PATH already exists
    if 'PATH=/usr/bin' in content:
        print("PATH already exists")
        ssh.close()
        return
    
    # Add PATH after environment: in worker section
    lines = content.split('\n')
    new_lines = []
    in_worker = False
    env_added = False
    
    for i, line in enumerate(lines):
        new_lines.append(line)
        
        if 'worker:' in line:
            in_worker = True
            env_added = False
        elif in_worker and 'environment:' in line:
            env_added = True
        elif in_worker and env_added and line.strip().startswith('- ') and 'PATH' not in content:
            # Insert PATH before first env var
            if 'PATH=' not in '\n'.join(new_lines):
                new_lines.insert(-1, '      - PATH=/usr/bin:/usr/local/bin:/bin:/usr/sbin:/sbin')
                env_added = False  # Don't add again
        elif in_worker and line.strip() and not line.strip().startswith('- ') and not line.strip().startswith('#'):
            in_worker = False
    
    # Write back
    with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'w') as f:
        f.write('\n'.join(new_lines).encode('utf-8'))
    
    sftp.close()
    
    # Verify
    stdin, stdout, stderr = ssh.exec_command('grep -A 12 "worker:" /opt/xaker/shannon/docker-compose.yml | head -15')
    print(stdout.read().decode('utf-8', errors='replace'))
    
    # Restart
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose restart worker')
    print(stdout.read().decode('utf-8', errors='replace'))
    
    ssh.close()
    print("Done")

if __name__ == "__main__":
    fix_compose()

