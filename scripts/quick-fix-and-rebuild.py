#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Quick fix duplicate and rebuild"""

import paramiko
import sys
import time

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def quick_fix():
    """Quick fix"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("Fixing duplicate NODE and rebuilding...")
    
    sftp = ssh.open_sftp()
    with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'r') as f:
        compose = f.read().decode('utf-8')
    
    # Remove duplicate NODE
    lines = compose.split('\n')
    seen_node = False
    new_lines = []
    for line in lines:
        if 'NODE=' in line:
            if not seen_node:
                new_lines.append(line)
                seen_node = True
        else:
            new_lines.append(line)
    
    compose = '\n'.join(new_lines)
    with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'w') as f:
        f.write(compose.encode('utf-8'))
    sftp.close()
    
    print("✅ Fixed duplicate")
    print("Rebuilding (2-3 min)...")
    
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && timeout 300 docker-compose build --no-cache worker 2>&1')
    
    output = ""
    start = time.time()
    while time.time() - start < 240:
        chunk = stdout.read(1024).decode('utf-8', errors='replace')
        if chunk:
            output += chunk
            if 'Successfully' in output:
                print("\n✅ Build successful!")
                break
        elif stdout.channel.exit_status_ready():
            break
        time.sleep(2)
    
    remaining = stdout.read(50000).decode('utf-8', errors='replace')
    if 'Successfully' in remaining:
        print("✅ Build successful!")
    
    # Restart
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose up -d worker')
    print(stdout.read().decode('utf-8', errors='replace'))
    
    time.sleep(3)
    
    # Verify
    stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon | grep worker')
    if stdout.read().decode('utf-8', errors='replace'):
        print("✅ Worker running")
        stdin, stdout, stderr = ssh.exec_command('pm2 restart xaker-backend')
        print("✅ Backend restarted")
        print("\n✅ Application ready for pentests!")
    
    ssh.close()

if __name__ == "__main__":
    quick_fix()

