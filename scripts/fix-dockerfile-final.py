#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix Dockerfile to create symlink in final stage"""

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

def fix_dockerfile_final():
    """Fix Dockerfile final stage"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("FIXING DOCKERFILE FINAL STAGE")
    print("=" * 80)
    
    dockerfile_path = '/opt/xaker/shannon/Dockerfile'
    
    # Read Dockerfile
    print(f"\n1. Reading {dockerfile_path}...")
    sftp = ssh.open_sftp()
    with sftp.open(dockerfile_path, 'r') as f:
        content = f.read().decode('utf-8')
    
    lines = content.split('\n')
    
    # Find final stage (usually starts with FROM without AS)
    print("\n2. Finding final stage...")
    final_stage_start = -1
    for i, line in enumerate(lines):
        if line.strip().startswith('FROM ') and 'AS' not in line.upper() and final_stage_start == -1:
            # Check if this is after builder stage
            if i > 10:  # Probably final stage
                final_stage_start = i
                print(f"   Found final stage at line {i+1}: {line.strip()}")
                break
    
    # Find where to add symlink (after COPY or WORKDIR in final stage)
    if final_stage_start >= 0:
        print("\n3. Adding symlink in final stage...")
        new_lines = []
        symlink_added = False
        
        for i, line in enumerate(lines):
            new_lines.append(line)
            
            # In final stage, after COPY commands, add symlink
            if i >= final_stage_start and not symlink_added:
                # Look for COPY or WORKDIR or RUN commands
                if line.strip().startswith('COPY ') or line.strip().startswith('WORKDIR ') or (line.strip().startswith('RUN ') and 'node' not in line.lower()):
                    # Add symlink after this
                    new_lines.append('RUN mkdir -p /usr/local/bin && ln -sf /usr/bin/node /usr/local/bin/node || true')
                    symlink_added = True
                    print(f"   ✅ Added symlink after line {i+1}: {line.strip()[:50]}")
        
        # If not added, add at end of final stage
        if not symlink_added:
            # Find last RUN/COPY/WORKDIR before CMD/ENTRYPOINT
            for i in range(len(lines) - 1, final_stage_start, -1):
                if lines[i].strip().startswith('RUN ') or lines[i].strip().startswith('COPY ') or lines[i].strip().startswith('WORKDIR '):
                    new_lines.insert(i + 1, 'RUN mkdir -p /usr/local/bin && ln -sf /usr/bin/node /usr/local/bin/node || true')
                    print(f"   ✅ Added symlink after line {i+1}")
                    break
        
        # Write back
        print("\n4. Writing updated Dockerfile...")
        with sftp.open(dockerfile_path, 'w') as f:
            f.write('\n'.join(new_lines).encode('utf-8'))
        
        # Verify
        print("\n5. Verifying changes...")
        stdin, stdout, stderr = ssh.exec_command(f'grep -n "ln.*node" {dockerfile_path}')
        verify = stdout.read().decode('utf-8', errors='replace')
        print(verify)
        
        # Rebuild
        print("\n6. Rebuilding worker (this will take time)...")
        print("   Starting rebuild...")
        stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && timeout 300 docker-compose build --no-cache worker 2>&1 | tail -50')
        build_output = stdout.read().decode('utf-8', errors='replace')
        print(build_output[-2000:])
        
        # Restart
        print("\n7. Restarting worker...")
        stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose up -d worker')
        restart_output = stdout.read().decode('utf-8', errors='replace')
        print(restart_output)
        
        # Verify symlink
        import time
        time.sleep(3)
        print("\n8. Verifying symlink...")
        stdin, stdout, stderr = ssh.exec_command('docker exec shannon_worker_1 ls -la /usr/local/bin/node 2>&1')
        symlink = stdout.read().decode('utf-8', errors='replace')
        print(symlink)
        
        if 'node' in symlink.lower() or '->' in symlink:
            print("\n✅ Symlink created successfully!")
        else:
            print("\n⚠️  Symlink still not found")
    
    sftp.close()
    ssh.close()
    
    print("\n" + "=" * 80)
    print("FIX COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    fix_dockerfile_final()

