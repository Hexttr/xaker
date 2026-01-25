#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix docker-compose.yml volumes"""

import paramiko
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def fix_volumes():
    """Fix volumes"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("FIXING DOCKER-COMPOSE VOLUMES")
    print("=" * 80)
    
    # Read docker-compose.yml
    print("\n1. Reading docker-compose.yml...")
    sftp = ssh.open_sftp()
    with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'r') as f:
        content = f.read().decode('utf-8')
    
    # Check if volumes section exists
    if 'volumes:' in content and 'temporal-data:' in content:
        print("   Volumes section already exists")
    else:
        print("   Adding volumes section...")
        lines = content.split('\n')
        new_lines = []
        volumes_added = False
        
        for i, line in enumerate(lines):
            new_lines.append(line)
            # Add volumes at the end
            if i == len(lines) - 1 and not volumes_added:
                new_lines.append('')
                new_lines.append('volumes:')
                new_lines.append('  temporal-data:')
                volumes_added = True
        
        # Write back
        with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'w') as f:
            f.write('\n'.join(new_lines).encode('utf-8'))
        print("   ✅ Volumes section added")
    
    sftp.close()
    
    # Verify
    print("\n2. Verifying docker-compose.yml...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose config 2>&1 | tail -5')
    verify = stdout.read().decode('utf-8', errors='replace')
    print(verify)
    
    # Start services
    print("\n3. Starting services...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose up -d')
    start_output = stdout.read().decode('utf-8', errors='replace')
    print(start_output)
    
    import time
    time.sleep(5)
    
    # Check status
    print("\n4. Checking status...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose ps')
    status = stdout.read().decode('utf-8', errors='replace')
    print(status)
    
    ssh.close()
    
    print("\n" + "=" * 80)
    print("FIX COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    import time
    fix_volumes()

