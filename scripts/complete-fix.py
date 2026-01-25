#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Complete fix - ensure wrapper is created and PATH is set"""

import paramiko
import sys
import time

# Fix encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def complete_fix():
    """Complete fix"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("COMPLETE FIX")
    print("=" * 80)
    
    # Read Dockerfile
    print("\n1. Reading Dockerfile...")
    sftp = ssh.open_sftp()
    with sftp.open('/opt/xaker/shannon/Dockerfile', 'r') as f:
        content = f.read().decode('utf-8')
    
    lines = content.split('\n')
    
    # Find USER pentest line
    user_line_idx = -1
    for i, line in enumerate(lines):
        if 'USER pentest' in line:
            user_line_idx = i
            break
    
    if user_line_idx < 0:
        print("   ERROR: USER pentest not found")
        ssh.close()
        return
    
    print(f"   Found USER pentest at line {user_line_idx + 1}")
    
    # Check if wrapper creation is before USER
    wrapper_before = False
    path_before = False
    for i in range(max(0, user_line_idx - 10), user_line_idx):
        if '/app/bin/node' in lines[i] or 'mkdir -p /app/bin' in lines[i]:
            wrapper_before = True
        if 'ENV PATH="/app/bin' in lines[i] or "ENV PATH='/app/bin" in lines[i]:
            path_before = True
    
    print(f"   Wrapper before USER: {wrapper_before}")
    print(f"   PATH before USER: {path_before}")
    
    # Fix if needed
    if not wrapper_before or not path_before:
        print("\n2. Adding wrapper creation and PATH...")
        new_lines = []
        added = False
        
        for i, line in enumerate(lines):
            if 'USER pentest' in line and not added:
                # Insert before USER
                new_lines.append('# Create node wrapper accessible to pentest user')
                new_lines.append('RUN mkdir -p /app/bin && echo "#!/bin/sh" > /app/bin/node && echo "exec /usr/bin/node \"$@\"" >> /app/bin/node && chmod +x /app/bin/node')
                new_lines.append('ENV PATH="/app/bin:$PATH"')
                new_lines.append('')
                new_lines.append(line)
                added = True
            else:
                new_lines.append(line)
        
        # Write back
        print("   ✅ Writing updated Dockerfile...")
        with sftp.open('/opt/xaker/shannon/Dockerfile', 'w') as f:
            f.write('\n'.join(new_lines).encode('utf-8'))
        
        # Verify
        print("\n3. Verifying changes...")
        stdin, stdout, stderr = ssh.exec_command('grep -B 3 "USER pentest" /opt/xaker/shannon/Dockerfile | head -5')
        verify = stdout.read().decode('utf-8', errors='replace')
        print(verify)
        
        # Rebuild
        print("\n4. Rebuilding worker (this will take 2-3 minutes)...")
        stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose stop worker && docker-compose rm -f worker')
        time.sleep(2)
        
        stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && timeout 180 docker-compose build worker 2>&1')
        # Wait
        time.sleep(60)
        build_output = stdout.read(50000).decode('utf-8', errors='replace')
        if 'Successfully' in build_output:
            print("   ✅ Build appears successful")
        print(f"   Last 300 chars: {build_output[-300:]}")
        
        # Start
        print("\n5. Starting worker...")
        stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose up -d worker')
        start_output = stdout.read().decode('utf-8', errors='replace')
        print(start_output)
        
        time.sleep(5)
        
        # Verify
        print("\n6. Verifying wrapper...")
        stdin, stdout, stderr = ssh.exec_command('docker exec shannon_worker_1 sh -c "ls -la /app/bin/node 2>&1 && echo PATH: && printenv PATH"')
        verify_output = stdout.read().decode('utf-8', errors='replace')
        print(verify_output)
        
        if '/app/bin/node' in verify_output and '/app/bin' in verify_output:
            print("\n✅ SUCCESS! Wrapper created and PATH set")
            print("Try a new pentest now")
        else:
            print("\n⚠️  Wrapper or PATH may not be set correctly")
    else:
        print("\n2. Dockerfile already has wrapper, just rebuilding...")
        stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose stop worker && docker-compose rm -f worker && docker-compose build --no-cache worker 2>&1 | tail -20')
        time.sleep(60)
        build_output = stdout.read().decode('utf-8', errors='replace')
        print(build_output[-1000:])
        
        stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose up -d worker')
        print(stdout.read().decode('utf-8', errors='replace'))
    
    sftp.close()
    ssh.close()
    
    print("\n" + "=" * 80)
    print("FIX COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    complete_fix()

