#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix duplicate NODE env var"""

import paramiko
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def fix_duplicate():
    """Fix duplicate NODE"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("FIXING DUPLICATE NODE ENV VAR")
    print("=" * 80)
    
    sftp = ssh.open_sftp()
    
    # Read docker-compose.yml
    with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'r') as f:
        compose = f.read().decode('utf-8')
    
    compose_lines = compose.split('\n')
    
    # Find and remove duplicates
    seen_node = False
    seen_path = False
    new_lines = []
    
    for i, line in enumerate(compose_lines):
        if 'NODE=' in line:
            if not seen_node:
                new_lines.append(line)
                seen_node = True
            else:
                print(f"   Removed duplicate NODE at line {i+1}")
        elif 'PATH=' in line and 'environment:' in '\n'.join(compose_lines[max(0, i-5):i]):
            if not seen_path:
                new_lines.append(line)
                seen_path = True
            else:
                print(f"   Removed duplicate PATH at line {i+1}")
        else:
            new_lines.append(line)
    
    compose = '\n'.join(new_lines)
    
    # Write back
    with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'w') as f:
        f.write(compose.encode('utf-8'))
    
    sftp.close()
    
    # Validate
    print("\nValidating docker-compose.yml...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose config 2>&1 | head -5')
    validate = stdout.read().decode('utf-8', errors='replace')
    if 'error' in validate.lower():
        print(f"⚠️ Error: {validate}")
    else:
        print("✅ docker-compose.yml is valid")
        
        # Rebuild
        print("\nRebuilding worker image...")
        stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && timeout 300 docker-compose build --no-cache worker 2>&1 | tail -30')
        
        import time
        start_time = time.time()
        output = ""
        while time.time() - start_time < 240:
            chunk = stdout.read(1024).decode('utf-8', errors='replace')
            if chunk:
                output += chunk
                if len(output) > 500:
                    print(output[-500:], end='', flush=True)
                    output = output[-500:]
            else:
                time.sleep(2)
                if stdout.channel.exit_status_ready():
                    break
        
        remaining = stdout.read(50000).decode('utf-8', errors='replace')
        print(remaining[-1000:])
        
        if 'Successfully' in output or 'Successfully' in remaining:
            print("\n✅ Docker build successful!")
            
            # Restart worker
            print("\nRestarting worker...")
            stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose stop worker && docker-compose rm -f worker && docker-compose up -d worker')
            print(stdout.read().decode('utf-8', errors='replace'))
            
            time.sleep(5)
            
            # Verify
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
                    
                    # Restart backend
                    print("\nRestarting backend...")
                    stdin, stdout, stderr = ssh.exec_command('pm2 restart xaker-backend')
                    print("✅ Backend restarted")
                    
                    print("\n" + "=" * 80)
                    print("✅ SUCCESS! Application is ready")
                    print("=" * 80)
    
    ssh.close()

if __name__ == "__main__":
    fix_duplicate()

