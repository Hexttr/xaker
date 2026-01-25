#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix docker-compose.yml on server"""

import paramiko
import sys
import re

# Fix encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def fix_compose():
    """Fix docker-compose.yml"""
    print("=" * 80)
    print("FIXING DOCKER-COMPOSE.YML ON SERVER")
    print("=" * 80)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    try:
        # Read file
        print("\n1. Reading docker-compose.yml...")
        sftp = ssh.open_sftp()
        with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'r') as f:
            content = f.read().decode('utf-8')
        
        # Check if PATH already exists
        if 'PATH=/usr/bin' in content:
            print("   ✅ PATH already exists in docker-compose.yml")
            sftp.close()
            ssh.close()
            return
        
        print("   ⚠️  PATH not found, adding it...")
        
        # Fix: Add PATH after environment: in worker section
        lines = content.split('\n')
        new_lines = []
        in_worker_section = False
        found_environment = False
        path_added = False
        
        for i, line in enumerate(lines):
            new_lines.append(line)
            
            # Detect worker section
            if 'worker:' in line:
                in_worker_section = True
                found_environment = False
                path_added = False
            
            # Detect environment: line in worker section
            if in_worker_section and 'environment:' in line:
                found_environment = True
            
            # Add PATH right after environment: line
            if in_worker_section and found_environment and not path_added:
                # Check if next line is an environment variable
                if i + 1 < len(lines) and lines[i + 1].strip().startswith('- '):
                    # Insert PATH before first env var
                    new_lines.append('      - PATH=/usr/bin:/usr/local/bin:/bin:/usr/sbin:/sbin')
                    path_added = True
                    print(f"   ✅ PATH added after line {i+1}")
            
            # Exit worker section when we hit a new top-level key
            if in_worker_section and line.strip() and not line.startswith(' ') and not line.startswith('\t') and 'worker:' not in line:
                in_worker_section = False
        
        # If PATH wasn't added, try alternative method
        if not path_added:
            print("   ⚠️  Alternative method: inserting after environment:")
            new_lines = []
            for i, line in enumerate(lines):
                new_lines.append(line)
                if 'worker:' in line:
                    # Look ahead for environment:
                    j = i + 1
                    while j < len(lines) and (lines[j].startswith(' ') or lines[j].startswith('\t')):
                        if 'environment:' in lines[j]:
                            # Insert PATH after environment:
                            new_lines.append(lines[j])
                            new_lines.append('      - PATH=/usr/bin:/usr/local/bin:/bin:/usr/sbin:/sbin')
                            j += 1
                            # Skip the environment: line we already added
                            while j < len(lines) and (lines[j].startswith(' ') or lines[j].startswith('\t')):
                                new_lines.append(lines[j])
                                j += 1
                            break
                        new_lines.append(lines[j])
                        j += 1
                    # Skip lines we already processed
                    i = j - 1
                    continue
        
        # Write back
        print("\n2. Writing updated docker-compose.yml...")
        with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'w') as f:
            f.write('\n'.join(new_lines).encode('utf-8'))
        
        sftp.close()
        
        # Verify
        print("\n3. Verifying changes...")
        stdin, stdout, stderr = ssh.exec_command('grep -A 12 "worker:" /opt/xaker/shannon/docker-compose.yml | head -15')
        verify = stdout.read().decode('utf-8', errors='replace')
        print(verify)
        
        if 'PATH=/usr/bin' in verify:
            print("   ✅ PATH successfully added!")
        else:
            print("   ⚠️  PATH not found in output, but file was modified")
        
        # Restart worker
        print("\n4. Restarting worker...")
        stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose restart worker 2>&1')
        restart_output = stdout.read().decode('utf-8', errors='replace')
        print(restart_output)
        
        # Check status
        print("\n5. Checking worker status...")
        stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose ps worker 2>&1')
        status = stdout.read().decode('utf-8', errors='replace')
        print(status)
        
        ssh.close()
        
        print("\n" + "=" * 80)
        print("FIX COMPLETE")
        print("=" * 80)
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        ssh.close()

if __name__ == "__main__":
    fix_compose()

