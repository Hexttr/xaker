#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Do rebuild now"""

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

def do_rebuild():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("Starting Docker rebuild (2-3 minutes)...")
    print("=" * 80)
    
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose build --no-cache worker 2>&1')
    
    start = time.time()
    last_line = ""
    
    while time.time() - start < 300:
        if stdout.channel.recv_ready():
            chunk = stdout.channel.recv(4096).decode('utf-8', errors='replace')
            if chunk:
                lines = chunk.split('\n')
                for line in lines:
                    if line.strip() and ('Step' in line or 'Successfully' in line or 'ERROR' in line):
                        if line != last_line:
                            print(line)
                            last_line = line
                if 'Successfully' in chunk:
                    print("\n✅ Build successful!")
                    break
        elif stdout.channel.exit_status_ready():
            break
        time.sleep(0.5)
    
    remaining = stdout.read(100000).decode('utf-8', errors='replace')
    if 'Successfully' in remaining:
        print("✅ Build successful!")
    
    print("\nRestarting worker...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose stop worker && docker-compose rm -f worker && docker-compose up -d worker')
    print(stdout.read().decode('utf-8', errors='replace'))
    
    time.sleep(5)
    
    print("\nVerifying...")
    stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon | grep worker')
    worker = stdout.read().decode('utf-8', errors='replace')
    if worker:
        container_id = worker.split()[0]
        stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "su pentest -c \'which node && node --version\'"')
        verify = stdout.read().decode('utf-8', errors='replace')
        print(verify)
        if 'v22' in verify:
            print("\n✅ Node is accessible!")
            stdin, stdout, stderr = ssh.exec_command('pm2 restart xaker-backend')
            print("✅ Backend restarted")
            print("\n" + "=" * 80)
            print("✅ SUCCESS! Application ready for pentests")
            print("=" * 80)
    
    ssh.close()

if __name__ == "__main__":
    do_rebuild()

