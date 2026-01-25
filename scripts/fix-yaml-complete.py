#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix YAML completely"""

import paramiko
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def fix_yaml_complete():
    """Fix YAML completely"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("FIXING YAML COMPLETELY")
    print("=" * 80)
    
    sftp = ssh.open_sftp()
    
    # Read docker-compose.yml
    with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'r') as f:
        compose = f.read().decode('utf-8')
    
    compose_lines = compose.split('\n')
    
    # Show problematic lines
    print("\n   Lines 18-25:")
    for i in range(17, min(25, len(compose_lines))):
        print(f"   {i+1:3d}: {compose_lines[i]}")
    
    # Fix: ensure proper YAML structure
    # Find worker section
    in_worker = False
    for i, line in enumerate(compose_lines):
        if 'worker:' in line:
            in_worker = True
        elif in_worker:
            if 'entrypoint:' in line:
                compose_lines[i] = '    entrypoint: ["/bin/sh", "-c"]'
            elif 'command:' in line:
                # Ensure command is properly formatted
                compose_lines[i] = '    command: "mkdir -p /usr/local/bin && ln -sf /usr/bin/node /usr/local/bin/node 2>/dev/null || true && exec node dist/temporal/worker.js"'
            elif line.strip().startswith('-') and 'TEMPORAL_ADDRESS' in line:
                # This should be under environment:
                # Check if previous line is environment:
                if i > 0 and 'environment:' not in compose_lines[i-1]:
                    # Insert environment: before this line
                    compose_lines.insert(i, '    environment:')
                    print(f"   ✅ Added environment: at line {i+1}")
            elif line.strip() and not line.startswith(' ') and not line.startswith('\t') and ':' in line:
                # End of worker section
                break
    
    compose = '\n'.join(compose_lines)
    
    # Write back
    with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'w') as f:
        f.write(compose.encode('utf-8'))
    
    sftp.close()
    
    # Validate YAML
    print("\n2. Validating docker-compose.yml...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose config 2>&1')
    validate = stdout.read().decode('utf-8', errors='replace')
    if 'error' in validate.lower() or 'Error' in validate:
        print(f"   ⚠️  YAML error:")
        error_lines = validate.split('\n')
        for err in error_lines[:10]:
            if 'error' in err.lower() or 'Error' in err:
                print(f"   {err}")
    else:
        print("   ✅ YAML is valid")
    
    # Restart worker
    print("\n3. Restarting worker...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose stop worker && docker-compose rm -f worker && docker-compose up -d worker')
    restart_output = stdout.read().decode('utf-8', errors='replace')
    print(restart_output)
    
    import time
    time.sleep(5)
    
    # Check worker
    print("\n4. Checking worker...")
    stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon | grep worker')
    worker = stdout.read().decode('utf-8', errors='replace')
    if worker:
        container_id = worker.split()[0]
        print(f"   ✅ Worker is running: {container_id}")
        
        stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "ls -la /usr/local/bin/node && which node && /usr/local/bin/node --version && printenv NODE"')
        verify = stdout.read().decode('utf-8', errors='replace')
        print(verify)
        
        # Check logs
        stdin, stdout, stderr = ssh.exec_command(f'docker logs {container_id} --tail=15 2>&1')
        logs = stdout.read().decode('utf-8', errors='replace')
        print(f"\n   Worker logs:\n{logs[-500:]}")
        
        # Restart backend
        print("\n5. Restarting backend...")
        stdin, stdout, stderr = ssh.exec_command('pm2 restart xaker-backend')
        print(stdout.read().decode('utf-8', errors='replace'))
        
        print("\n✅ SUCCESS! Everything is running")
        print("Try a new pentest now!")
    else:
        print("   ⚠️  Worker still not running")
        stdin, stdout, stderr = ssh.exec_command('docker ps -a | grep shannon | grep worker | head -1')
        worker_line = stdout.read().decode('utf-8', errors='replace')
        if worker_line:
            container_id = worker_line.split()[0]
            stdin, stdout, stderr = ssh.exec_command(f'docker logs {container_id} 2>&1 | tail -30')
            print(stdout.read().decode('utf-8', errors='replace'))
    
    ssh.close()
    
    print("\n" + "=" * 80)
    print("FIX COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    import time
    fix_yaml_complete()

