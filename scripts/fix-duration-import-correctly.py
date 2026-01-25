#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix Duration import correctly"""

import paramiko
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def fix_duration():
    """Fix Duration import"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("FIXING DURATION IMPORT CORRECTLY")
    print("=" * 80)
    
    file_path = '/opt/xaker/shannon/src/temporal/workflows.ts'
    
    sftp = ssh.open_sftp()
    with sftp.open(file_path, 'r') as f:
        content = f.read().decode('utf-8')
    
    lines = content.split('\n')
    
    # Find import section
    print("\n1. Finding imports...")
    import_start = -1
    import_end = -1
    
    for i, line in enumerate(lines[:30]):
        if 'import' in line and 'from' in line and '@temporalio' in line:
            import_start = i
            print(f"   Found import start at line {i+1}: {line[:60]}")
            # Find end of import
            j = i
            while j < len(lines) and j < i + 10:
                if '}' in lines[j] and import_start >= 0:
                    import_end = j
                    print(f"   Found import end at line {j+1}")
                    break
                j += 1
            break
    
    # Add Duration to import
    if import_start >= 0 and import_end >= 0:
        print("\n2. Adding Duration to import...")
        # Check if Duration already there
        import_block = '\n'.join(lines[import_start:import_end+1])
        if 'Duration' not in import_block:
            # Add Duration before closing brace
            if '}' in lines[import_end]:
                lines[import_end] = lines[import_end].replace('}', ', Duration }')
                print(f"   Added Duration at line {import_end+1}")
            else:
                # Insert before closing brace
                lines.insert(import_end, '  Duration,')
                print(f"   Inserted Duration at line {import_end+1}")
        else:
            print("   Duration already imported")
    
    # Write back
    with sftp.open(file_path, 'w') as f:
        f.write('\n'.join(lines).encode('utf-8'))
    
    sftp.close()
    
    # Rebuild
    print("\n3. Rebuilding...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && npm run build 2>&1 | tail -3')
    build_output = stdout.read().decode('utf-8', errors='replace')
    print(build_output[-200:])
    
    if 'error' not in build_output.lower():
        print("✅ Build successful!")
        
        # Build and start
        print("\n4. Building and starting...")
        stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose build worker 2>&1 | tail -3')
        print(stdout.read().decode('utf-8', errors='replace')[-200:])
        
        stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose up -d worker')
        print(stdout.read().decode('utf-8', errors='replace'))
        
        import time
        time.sleep(5)
        
        # Verify
        stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon | grep worker')
        worker = stdout.read().decode('utf-8', errors='replace')
        if worker:
            container_id = worker.split()[0]
            stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "ls -la /usr/local/bin/node && which node && printenv NODE"')
            print(stdout.read().decode('utf-8', errors='replace'))
    else:
        print("⚠️  Build has errors")
    
    ssh.close()
    
    print("\n" + "=" * 80)
    print("FIX COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    import time
    fix_duration()

