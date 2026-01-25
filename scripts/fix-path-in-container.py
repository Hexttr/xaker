#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix PATH in running container"""

import paramiko
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def fix_path():
    """Fix PATH in docker-compose.yml"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    # Update PATH in docker-compose.yml
    sftp = ssh.open_sftp()
    with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'r') as f:
        content = f.read().decode('utf-8')
    
    # Check if /app/bin is in PATH
    if '/app/bin' not in content:
        # Add /app/bin to PATH
        lines = content.split('\n')
        new_lines = []
        path_found = False
        
        for i, line in enumerate(lines):
            new_lines.append(line)
            if 'worker:' in line:
                # Look for environment section
                j = i + 1
                while j < len(lines) and (lines[j].startswith(' ') or lines[j].startswith('\t')):
                    if 'PATH=' in lines[j]:
                        # Update PATH
                        if '/app/bin' not in lines[j]:
                            new_lines[-1] = lines[j].replace('PATH=', 'PATH=/app/bin:')
                            path_found = True
                            print(f"Updated PATH at line {j+1}")
                        break
                    new_lines.append(lines[j])
                    j += 1
                break
        
        if not path_found:
            # Add PATH if not found
            for i, line in enumerate(lines):
                new_lines.append(line)
                if 'worker:' in line:
                    # Find environment section
                    j = i + 1
                    while j < len(lines) and (lines[j].startswith(' ') or lines[j].startswith('\t')):
                        if 'environment:' in lines[j]:
                            # Add PATH after environment
                            new_lines.append('      - PATH=/app/bin:/usr/bin:/usr/local/bin:/bin:/usr/sbin:/sbin')
                            print("Added PATH to environment")
                            break
                        new_lines.append(lines[j])
                        j += 1
                    break
        
        with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'w') as f:
            f.write('\n'.join(new_lines).encode('utf-8'))
        
        print("Updated docker-compose.yml")
        
        # Restart worker
        print("Restarting worker...")
        ssh.exec_command('cd /opt/xaker/shannon && docker-compose restart worker')
        import time
        time.sleep(3)
        
        # Verify
        stdin, stdout, stderr = ssh.exec_command('docker exec shannon_worker_1 printenv PATH')
        path = stdout.read().decode('utf-8', errors='replace')
        print(f"PATH in container: {path}")
        
        if '/app/bin' in path:
            print("SUCCESS! PATH updated. Try a new pentest.")
        else:
            print("PATH may not be updated correctly")
    else:
        print("PATH already includes /app/bin")
    
    sftp.close()
    ssh.close()

if __name__ == "__main__":
    fix_path()

