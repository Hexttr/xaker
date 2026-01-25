#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix worker entrypoint to ensure node is available"""

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

def fix_entrypoint():
    """Fix docker-compose.yml entrypoint"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("FIXING WORKER ENTRYPOINT")
    print("=" * 80)
    
    # Read docker-compose.yml
    print("\n1. Reading docker-compose.yml...")
    sftp = ssh.open_sftp()
    with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'r') as f:
        content = f.read().decode('utf-8')
    
    # Check current entrypoint
    print("\n2. Current entrypoint:")
    if 'entrypoint:' in content:
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'entrypoint:' in line:
                print(f"   {line}")
                if i + 1 < len(lines):
                    print(f"   {lines[i+1]}")
                break
    
    # Modify entrypoint to create symlink first
    print("\n3. Modifying entrypoint...")
    lines = content.split('\n')
    new_lines = []
    entrypoint_found = False
    
    for i, line in enumerate(lines):
        new_lines.append(line)
        
        if 'worker:' in line:
            entrypoint_found = False
        elif 'entrypoint:' in line and 'worker:' in '\n'.join(new_lines[-10:]):
            entrypoint_found = True
            # Replace entrypoint with script that creates symlink
            if '["node"' in line or '["node"' in lines[i+1] if i+1 < len(lines) else False:
                # Replace with script
                new_lines[-1] = '    entrypoint: ["/bin/sh", "-c"]'
                new_lines.append('    command: "ln -sf /usr/bin/node /usr/local/bin/node 2>/dev/null; exec node dist/temporal/worker.js"')
                # Skip next line if it's the old entrypoint value
                if i + 1 < len(lines) and ('node' in lines[i+1] or 'dist/temporal' in lines[i+1]):
                    i += 1  # Skip next line
                print("   ✅ Entrypoint modified to create symlink")
                break
    
    if not entrypoint_found:
        print("   ⚠️  Entrypoint not found or already modified")
        # Try alternative: add command instead
        for i, line in enumerate(lines):
            if 'worker:' in line:
                # Find environment section
                j = i + 1
                while j < len(lines) and (lines[j].startswith(' ') or lines[j].startswith('\t')):
                    if 'command:' in lines[j]:
                        break
                    j += 1
                # Insert command before depends_on
                if 'command:' not in '\n'.join(lines[i:j]):
                    # Insert after environment
                    for k in range(i, min(i+20, len(lines))):
                        if 'environment:' in lines[k]:
                            # Find end of environment
                            m = k + 1
                            while m < len(lines) and (lines[m].startswith(' ') or lines[m].startswith('\t')) and lines[m].strip().startswith('-'):
                                m += 1
                            # Insert command
                            new_lines.insert(m, '    command: ["/bin/sh", "-c", "ln -sf /usr/bin/node /usr/local/bin/node 2>/dev/null; exec node dist/temporal/worker.js"]')
                            print("   ✅ Command added")
                            break
                break
    
    # Write back
    print("\n4. Writing updated docker-compose.yml...")
    with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'w') as f:
        f.write('\n'.join(new_lines).encode('utf-8'))
    
    sftp.close()
    
    # Verify
    print("\n5. Verifying changes...")
    stdin, stdout, stderr = ssh.exec_command('grep -A 5 "worker:" /opt/xaker/shannon/docker-compose.yml | head -10')
    verify = stdout.read().decode('utf-8', errors='replace')
    print(verify)
    
    # Rebuild and restart
    print("\n6. Rebuilding and restarting worker...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose up -d --build worker 2>&1')
    rebuild_output = stdout.read().decode('utf-8', errors='replace')
    print(rebuild_output)
    
    # Check status
    print("\n7. Checking worker status...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose ps worker')
    status = stdout.read().decode('utf-8', errors='replace')
    print(status)
    
    ssh.close()
    
    print("\n" + "=" * 80)
    print("FIX COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    fix_entrypoint()

