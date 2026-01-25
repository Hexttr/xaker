#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rebuild worker image"""

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

def rebuild_worker():
    """Rebuild worker image"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("REBUILDING WORKER IMAGE")
    print("=" * 80)
    
    # Rebuild with progress
    print("\nRebuilding worker image (this will take 2-3 minutes)...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose build --no-cache worker 2>&1')
    
    # Read output in chunks
    output_lines = []
    start_time = time.time()
    
    while time.time() - start_time < 300:
        if stdout.channel.recv_ready():
            chunk = stdout.channel.recv(4096).decode('utf-8', errors='replace')
            if chunk:
                output_lines.append(chunk)
                # Show last 3 lines
                lines = ''.join(output_lines).split('\n')
                if len(lines) > 3:
                    print('\n'.join(lines[-3:]), end='', flush=True)
        elif stdout.channel.exit_status_ready():
            break
        else:
            time.sleep(1)
    
    # Get remaining output
    remaining = stdout.read(100000).decode('utf-8', errors='replace')
    if remaining:
        output_lines.append(remaining)
    
    full_output = ''.join(output_lines)
    
    if 'Successfully' in full_output or 'Successfully built' in full_output:
        print("\n\n✅ Docker build successful!")
        
        # Restart worker
        print("\nRestarting worker...")
        stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose stop worker && docker-compose rm -f worker && docker-compose up -d worker')
        restart_output = stdout.read().decode('utf-8', errors='replace')
        print(restart_output)
        
        time.sleep(5)
        
        # Verify
        print("\nVerifying...")
        stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon | grep worker')
        worker = stdout.read().decode('utf-8', errors='replace')
        if worker:
            container_id = worker.split()[0]
            print(f"✅ Worker running: {container_id}")
            
            # Check node accessibility
            stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "su pentest -c \'which node && node --version\'"')
            verify = stdout.read().decode('utf-8', errors='replace')
            print(f"\nNode verification:\n{verify}")
            
            if 'v22' in verify:
                print("\n✅ Node is accessible!")
                
                # Check worker logs
                stdin, stdout, stderr = ssh.exec_command(f'docker logs {container_id} --tail=10 2>&1')
                logs = stdout.read().decode('utf-8', errors='replace')
                if 'Shannon worker started' in logs or 'RUNNING' in logs:
                    print("\n✅ Worker is running!")
                    
                    # Restart backend
                    print("\nRestarting backend...")
                    stdin, stdout, stderr = ssh.exec_command('pm2 restart xaker-backend')
                    print("✅ Backend restarted")
                    
                    print("\n" + "=" * 80)
                    print("✅ SUCCESS! Application is ready for pentests")
                    print("=" * 80)
                    return True
            else:
                print("\n⚠️ Node not accessible")
        else:
            print("⚠️ Worker not running")
    else:
        print("\n⚠️ Build may have issues")
        print("Last 20 lines of output:")
        lines = full_output.split('\n')
        print('\n'.join(lines[-20:]))
    
    ssh.close()
    return False

if __name__ == "__main__":
    rebuild_worker()

