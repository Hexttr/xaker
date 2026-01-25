#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cleanup and start worker"""

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

def cleanup_and_start():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("Cleaning up old containers and starting worker...")
    
    # Remove old containers
    stdin, stdout, stderr = ssh.exec_command('docker ps -a | grep shannon | grep worker | awk \'{print $1}\' | xargs -r docker rm -f')
    print("Removed old containers")
    
    # Start worker
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose up -d worker')
    output = stdout.read().decode('utf-8', errors='replace')
    print(output)
    
    time.sleep(5)
    
    # Verify
    stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon | grep worker')
    worker = stdout.read().decode('utf-8', errors='replace')
    if worker:
        container_id = worker.split()[0]
        print(f"✅ Worker running: {container_id}")
        
        stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "su pentest -c \'which node && node --version\'"')
        verify = stdout.read().decode('utf-8', errors='replace')
        print(f"Node check: {verify}")
        
        if 'v22' in verify:
            print("\n✅ Node is accessible!")
            stdin, stdout, stderr = ssh.exec_command('pm2 restart xaker-backend')
            print("✅ Backend restarted")
            print("\n" + "=" * 80)
            print("✅ SUCCESS! Application ready for pentests")
            print("=" * 80)
        else:
            print("\n⚠️ Node not accessible - may need rebuild")
    else:
        print("⚠️ Worker not running")
    
    ssh.close()

if __name__ == "__main__":
    cleanup_and_start()

