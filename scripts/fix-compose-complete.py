#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix docker-compose.yml completely based on original"""

import paramiko
import sys

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
    
    print("=" * 80)
    print("FIXING DOCKER-COMPOSE.YML COMPLETELY")
    print("=" * 80)
    
    # Read current docker-compose.yml
    print("\n1. Reading current docker-compose.yml...")
    sftp = ssh.open_sftp()
    with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'r') as f:
        content = f.read().decode('utf-8')
    
    lines = content.split('\n')
    
    # Check if volumes section exists at the end
    has_volumes_section = False
    volumes_line_idx = -1
    
    for i, line in enumerate(lines):
        if line.strip() == 'volumes:' and i > len(lines) - 5:
            has_volumes_section = True
            volumes_line_idx = i
            break
    
    print(f"   Volumes section exists: {has_volumes_section} at line {volumes_line_idx + 1}")
    
    # Fix volumes section
    if not has_volumes_section or 'temporal-data:' not in content:
        print("\n2. Adding/fixing volumes section...")
        new_lines = []
        volumes_added = False
        
        for i, line in enumerate(lines):
            # Remove old volumes section if exists but incomplete
            if line.strip() == 'volumes:' and not volumes_added:
                # Skip old incomplete volumes
                continue
            elif line.strip().startswith('temporal-data') and not volumes_added:
                # Skip old temporal-data line
                continue
            else:
                new_lines.append(line)
            
            # Add volumes at the end before last empty lines
            if i == len(lines) - 1 and not volumes_added:
                # Remove trailing empty lines
                while new_lines and not new_lines[-1].strip():
                    new_lines.pop()
                
                new_lines.append('')
                new_lines.append('volumes:')
                new_lines.append('  temporal-data:')
                volumes_added = True
        
        # Write back
        with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'w') as f:
            f.write('\n'.join(new_lines).encode('utf-8'))
        print("   ✅ Volumes section added/fixed")
    else:
        print("\n2. Volumes section already exists")
    
    sftp.close()
    
    # Verify
    print("\n3. Verifying docker-compose.yml...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose config 2>&1')
    verify = stdout.read().decode('utf-8', errors='replace')
    if 'error' in verify.lower() or 'Error' in verify:
        print(f"   ⚠️  Errors: {verify[-500:]}")
    else:
        print("   ✅ docker-compose.yml is valid")
    
    # Start services
    print("\n4. Starting services...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose down && docker-compose up -d')
    start_output = stdout.read().decode('utf-8', errors='replace')
    errors = stderr.read().decode('utf-8', errors='replace')
    print(start_output)
    if errors:
        print(f"Errors: {errors}")
    
    import time
    time.sleep(5)
    
    # Check status
    print("\n5. Checking status...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose ps')
    status = stdout.read().decode('utf-8', errors='replace')
    print(status)
    
    # Verify worker
    print("\n6. Verifying worker...")
    stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon | grep worker')
    worker = stdout.read().decode('utf-8', errors='replace')
    if worker:
        container_id = worker.split()[0]
        print(f"   Worker container: {container_id}")
        
        stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "ls -la /usr/local/bin/node && which node && /usr/local/bin/node --version"')
        verify_worker = stdout.read().decode('utf-8', errors='replace')
        print(verify_worker)
    
    ssh.close()
    
    print("\n" + "=" * 80)
    print("FIX COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    import time
    fix_compose()

