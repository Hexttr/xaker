#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix Shannon Dockerfile to create node symlink"""

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

def fix_dockerfile():
    """Fix Dockerfile to create node symlink"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("FIXING SHANNON DOCKERFILE")
    print("=" * 80)
    
    dockerfile_path = '/opt/xaker/shannon/Dockerfile'
    
    # Read Dockerfile
    print(f"\n1. Reading {dockerfile_path}...")
    sftp = ssh.open_sftp()
    try:
        with sftp.open(dockerfile_path, 'r') as f:
            content = f.read().decode('utf-8')
    except Exception as e:
        print(f"   ERROR: {e}")
        ssh.close()
        return
    
    print(f"   File size: {len(content)} bytes")
    
    # Check if symlink already exists
    if 'ln -s' in content and 'node' in content:
        print("   ✅ Symlink command already exists")
    else:
        print("   ⚠️  No symlink command found")
    
    # Find where to add symlink (after nodejs installation)
    lines = content.split('\n')
    new_lines = []
    nodejs_installed = False
    symlink_added = False
    
    for i, line in enumerate(lines):
        new_lines.append(line)
        
        # After nodejs installation, add symlink
        if 'nodejs' in line.lower() and ('apk add' in line or 'install' in line):
            nodejs_installed = True
        elif nodejs_installed and not symlink_added and line.strip() and not line.strip().startswith('#'):
            # Add symlink after nodejs installation
            new_lines.append('RUN mkdir -p /usr/local/bin && ln -sf /usr/bin/node /usr/local/bin/node || true')
            symlink_added = True
            print(f"   ✅ Added symlink command after line {i+1}")
            nodejs_installed = False
    
    # If not added, add at the end before CMD/ENTRYPOINT
    if not symlink_added:
        # Find last RUN command or before CMD/ENTRYPOINT
        for i in range(len(lines) - 1, -1, -1):
            if lines[i].strip().startswith('RUN ') or lines[i].strip().startswith('CMD ') or lines[i].strip().startswith('ENTRYPOINT '):
                new_lines.insert(i, 'RUN mkdir -p /usr/local/bin && ln -sf /usr/bin/node /usr/local/bin/node || true')
                print(f"   ✅ Added symlink command before line {i+1}")
                break
    
    # Write back
    print("\n2. Writing updated Dockerfile...")
    with sftp.open(dockerfile_path, 'w') as f:
        f.write('\n'.join(new_lines).encode('utf-8'))
    
    sftp.close()
    
    # Verify
    print("\n3. Verifying changes...")
    stdin, stdout, stderr = ssh.exec_command(f'grep -n "ln.*node" {dockerfile_path}')
    verify = stdout.read().decode('utf-8', errors='replace')
    print(verify)
    
    # Rebuild worker
    print("\n4. Rebuilding worker image...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose build worker 2>&1 | tail -30')
    build_output = stdout.read().decode('utf-8', errors='replace')
    print(build_output)
    
    # Restart worker
    print("\n5. Restarting worker...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose up -d worker')
    restart_output = stdout.read().decode('utf-8', errors='replace')
    print(restart_output)
    
    # Verify symlink exists
    print("\n6. Verifying symlink in container...")
    time.sleep(3)
    stdin, stdout, stderr = ssh.exec_command('docker exec shannon_worker_1 ls -la /usr/local/bin/node 2>&1')
    symlink_check = stdout.read().decode('utf-8', errors='replace')
    print(symlink_check)
    
    ssh.close()
    
    print("\n" + "=" * 80)
    print("DOCKERFILE FIX COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    import time
    fix_dockerfile()

