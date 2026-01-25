#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Create node wrapper in /app/bin"""

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

def create_wrapper():
    """Create node wrapper script"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("CREATING NODE WRAPPER")
    print("=" * 80)
    
    # Modify Dockerfile to create wrapper in /app/bin
    print("\n1. Modifying Dockerfile...")
    sftp = ssh.open_sftp()
    with sftp.open('/opt/xaker/shannon/Dockerfile', 'r') as f:
        content = f.read().decode('utf-8')
    
    lines = content.split('\n')
    new_lines = []
    wrapper_added = False
    
    for i, line in enumerate(lines):
        new_lines.append(line)
        
        # Add wrapper creation before USER pentest
        if 'USER pentest' in line and not wrapper_added:
            # Insert wrapper creation
            new_lines.insert(-1, '# Create node wrapper in /app/bin (accessible to pentest user)')
            new_lines.insert(-1, 'RUN mkdir -p /app/bin && echo "#!/bin/sh" > /app/bin/node && echo "exec /usr/bin/node \"$@\"" >> /app/bin/node && chmod +x /app/bin/node')
            new_lines.insert(-1, 'ENV PATH="/app/bin:$PATH"')
            wrapper_added = True
            print(f"   ✅ Added wrapper creation before USER pentest (line {i+1})")
    
    # Write back
    print("\n2. Writing updated Dockerfile...")
    with sftp.open('/opt/xaker/shannon/Dockerfile', 'w') as f:
        f.write('\n'.join(new_lines).encode('utf-8'))
    
    sftp.close()
    
    # Verify
    print("\n3. Verifying changes...")
    stdin, stdout, stderr = ssh.exec_command('grep -A 3 "USER pentest" /opt/xaker/shannon/Dockerfile | head -5')
    verify = stdout.read().decode('utf-8', errors='replace')
    print(verify)
    
    # Rebuild
    print("\n4. Rebuilding worker...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose build --no-cache worker 2>&1 | tail -30')
    build_output = stdout.read().decode('utf-8', errors='replace')
    print(build_output[-1500:])
    
    # Restart
    print("\n5. Restarting worker...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose up -d worker')
    restart_output = stdout.read().decode('utf-8', errors='replace')
    print(restart_output)
    
    import time
    time.sleep(3)
    
    # Verify wrapper
    print("\n6. Verifying wrapper...")
    stdin, stdout, stderr = ssh.exec_command('docker exec shannon_worker_1 ls -la /app/bin/node 2>&1')
    wrapper_check = stdout.read().decode('utf-8', errors='replace')
    print(wrapper_check)
    
    stdin, stdout, stderr = ssh.exec_command('docker exec shannon_worker_1 sh -c "which node && /app/bin/node --version 2>&1"')
    node_check = stdout.read().decode('utf-8', errors='replace')
    print(f"\nNode check: {node_check}")
    
    ssh.close()
    
    print("\n" + "=" * 80)
    print("WRAPPER CREATION COMPLETE")
    print("=" * 80)
    if "node" in wrapper_check.lower() or "node" in node_check.lower():
        print("✅ Wrapper created successfully!")
        print("Try a new pentest now")
    else:
        print("⚠️  Wrapper may not be created")

if __name__ == "__main__":
    create_wrapper()

