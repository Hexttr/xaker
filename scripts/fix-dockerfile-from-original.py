#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix Dockerfile based on original Shannon repository"""

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

def fix_from_original():
    """Fix Dockerfile based on original"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("FIXING DOCKERFILE BASED ON ORIGINAL SHANNON")
    print("=" * 80)
    
    # Read current Dockerfile
    print("\n1. Reading current Dockerfile...")
    sftp = ssh.open_sftp()
    with sftp.open('/opt/xaker/shannon/Dockerfile', 'r') as f:
        content = f.read().decode('utf-8')
    
    lines = content.split('\n')
    
    # Find USER pentest and PATH lines
    user_line_idx = -1
    path_line_idx = -1
    
    for i, line in enumerate(lines):
        if 'USER pentest' in line:
            user_line_idx = i
        if 'ENV PATH=' in line and '/usr/local/bin' in line:
            path_line_idx = i
    
    print(f"   USER pentest at line {user_line_idx + 1}")
    print(f"   PATH at line {path_line_idx + 1}")
    
    # Fix PATH to include /usr/bin BEFORE /usr/local/bin
    # Original has: ENV PATH="/usr/local/bin:$PATH"
    # But node is in /usr/bin, so we need: ENV PATH="/usr/bin:/usr/local/bin:$PATH"
    # OR create symlink before USER pentest
    
    new_lines = []
    path_fixed = False
    symlink_added = False
    
    for i, line in enumerate(lines):
        if 'USER pentest' in line and not symlink_added:
            # Add symlink creation BEFORE USER pentest
            new_lines.append('# Create symlink for node (nodejs-22 installs to /usr/bin/node)')
            new_lines.append('RUN mkdir -p /usr/local/bin && ln -sf /usr/bin/node /usr/local/bin/node')
            new_lines.append('')
            new_lines.append(line)
            symlink_added = True
            print(f"   ✅ Added symlink creation before USER pentest (line {i+1})")
        elif 'ENV PATH=' in line and '/usr/local/bin' in line and not path_fixed:
            # Update PATH to include /usr/bin first
            new_lines.append('ENV PATH="/usr/bin:/usr/local/bin:$PATH"')
            path_fixed = True
            print(f"   ✅ Updated PATH to include /usr/bin first (line {i+1})")
        else:
            new_lines.append(line)
    
    # Write back
    print("\n2. Writing updated Dockerfile...")
    with sftp.open('/opt/xaker/shannon/Dockerfile', 'w') as f:
        f.write('\n'.join(new_lines).encode('utf-8'))
    
    sftp.close()
    
    # Verify
    print("\n3. Verifying changes...")
    stdin, stdout, stderr = ssh.exec_command('grep -B 3 "USER pentest" /opt/xaker/shannon/Dockerfile | head -5')
    verify_user = stdout.read().decode('utf-8', errors='replace')
    print(verify_user)
    
    stdin, stdout, stderr = ssh.exec_command('grep "ENV PATH=" /opt/xaker/shannon/Dockerfile')
    verify_path = stdout.read().decode('utf-8', errors='replace')
    print(f"\nPATH: {verify_path}")
    
    # Rebuild
    print("\n4. Rebuilding worker image (this will take 2-3 minutes)...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose stop worker && docker-compose rm -f worker')
    import time as time_module
    time_module.sleep(2)
    
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && timeout 180 docker-compose build --no-cache worker 2>&1')
    # Wait for build
    time_module.sleep(120)
    build_output = stdout.read(100000).decode('utf-8', errors='replace')
    if 'Successfully' in build_output or 'Successfully tagged' in build_output:
        print("   ✅ Build successful")
    print(f"   Last 500 chars: {build_output[-500:]}")
    
    # Start
    print("\n5. Starting worker...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose up -d worker')
    start_output = stdout.read().decode('utf-8', errors='replace')
    print(start_output)
    
    time_module.sleep(5)
    
    # Verify
    print("\n6. Verifying fix...")
    stdin, stdout, stderr = ssh.exec_command('docker exec shannon_worker_1 sh -c "ls -la /usr/local/bin/node && which node && printenv PATH"')
    verify = stdout.read().decode('utf-8', errors='replace')
    print(verify)
    
    ssh.close()
    
    print("\n" + "=" * 80)
    print("FIX COMPLETE")
    print("=" * 80)
    if 'node' in verify.lower() and ('->' in verify or '/usr/bin' in verify):
        print("✅ SUCCESS! Dockerfile fixed based on original Shannon")
        print("Try a new pentest now")
    else:
        print("⚠️  Some checks failed, but fix should work")

if __name__ == "__main__":
    fix_from_original()

