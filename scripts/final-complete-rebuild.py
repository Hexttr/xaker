#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Final complete rebuild"""

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

def final_rebuild():
    """Final rebuild"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("FINAL COMPLETE REBUILD")
    print("=" * 80)
    
    # Fix duplicate NODE
    print("\n1. Fixing duplicate NODE...")
    sftp = ssh.open_sftp()
    with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'r') as f:
        compose = f.read().decode('utf-8')
    
    lines = compose.split('\n')
    seen_node = False
    new_lines = []
    for line in lines:
        if 'NODE=' in line and 'worker:' in '\n'.join(lines[max(0, lines.index(line)-10):lines.index(line)]):
            if not seen_node:
                new_lines.append(line)
                seen_node = True
        else:
            new_lines.append(line)
    
    compose = '\n'.join(new_lines)
    with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'w') as f:
        f.write(compose.encode('utf-8'))
    sftp.close()
    print("   ✅ Fixed")
    
    # Validate
    print("\n2. Validating...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose config > /dev/null 2>&1 && echo "OK" || echo "FAIL"')
    if 'OK' in stdout.read().decode('utf-8', errors='replace'):
        print("   ✅ Valid")
    else:
        print("   ⚠️ Invalid")
        return
    
    # Rebuild
    print("\n3. Rebuilding worker image (2-3 minutes)...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose build --no-cache worker 2>&1')
    
    output = ""
    start = time.time()
    while time.time() - start < 300:
        if stdout.channel.recv_ready():
            chunk = stdout.channel.recv(4096).decode('utf-8', errors='replace')
            output += chunk
            if 'Successfully' in chunk:
                print("\n   ✅ Build successful!")
                break
        elif stdout.channel.exit_status_ready():
            break
        time.sleep(1)
    
    remaining = stdout.read(100000).decode('utf-8', errors='replace')
    if 'Successfully' in remaining:
        print("   ✅ Build successful!")
    
    # Restart worker
    print("\n4. Restarting worker...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose stop worker && docker-compose rm -f worker && docker-compose up -d worker')
    print(stdout.read().decode('utf-8', errors='replace'))
    
    time.sleep(5)
    
    # Verify
    print("\n5. Verifying...")
    stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon | grep worker')
    worker = stdout.read().decode('utf-8', errors='replace')
    if worker:
        container_id = worker.split()[0]
        print(f"   ✅ Worker running: {container_id}")
        
        stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "su pentest -c \'which node && node --version\'"')
        verify = stdout.read().decode('utf-8', errors='replace')
        print(f"   {verify}")
        
        if 'v22' in verify:
            print("\n   ✅ Node accessible!")
            
            # Restart backend
            print("\n6. Restarting backend...")
            stdin, stdout, stderr = ssh.exec_command('pm2 restart xaker-backend')
            print("   ✅ Backend restarted")
            
            print("\n" + "=" * 80)
            print("✅ SUCCESS! Application is ready for pentests")
            print("=" * 80)
            print("\nYou can now launch pentests at https://pentest.red/app")
        else:
            print("\n   ⚠️ Node not accessible")
    else:
        print("   ⚠️ Worker not running")
    
    ssh.close()

if __name__ == "__main__":
    final_rebuild()

