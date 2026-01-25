#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix node path in container"""

import paramiko
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def fix_node_path():
    """Fix node path in container"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("FIXING NODE PATH IN CONTAINER")
    print("=" * 80)
    
    # Check current container state
    print("\n1. Checking current container state...")
    stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon | grep worker')
    worker = stdout.read().decode('utf-8', errors='replace')
    if worker:
        container_id = worker.split()[0]
        print(f"   Worker container: {container_id}")
        
        # Check PATH for pentest user
        stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "su pentest -c \'echo $PATH && which node && ls -la /usr/local/bin/node\'"')
        path_check = stdout.read().decode('utf-8', errors='replace')
        print(f"\n   PATH check for pentest user:\n{path_check}")
        
        # Check if /usr/local/bin is in PATH
        if '/usr/local/bin' not in path_check:
            print("\n   ⚠️  /usr/local/bin is not in PATH for pentest user")
            
            # Fix PATH in startup script
            print("\n2. Updating startup script to set PATH...")
            sftp = ssh.open_sftp()
            
            startup_script = """#!/bin/sh
set -e
export PATH="/usr/bin:/usr/local/bin:$PATH"
mkdir -p /usr/local/bin
ln -sf /usr/bin/node /usr/local/bin/node 2>/dev/null || true
# Verify node is accessible
which node || echo "WARNING: node not found in PATH"
node --version || echo "WARNING: node not executable"
exec node dist/temporal/worker.js
"""
            
            with sftp.open('/opt/xaker/shannon/start-worker.sh', 'w') as f:
                f.write(startup_script.encode('utf-8'))
            
            sftp.close()
            
            # Make executable
            ssh.exec_command('chmod +x /opt/xaker/shannon/start-worker.sh')
            
            # Also update Dockerfile to set PATH before USER
            print("\n3. Updating Dockerfile to set PATH before USER...")
            sftp = ssh.open_sftp()
            with sftp.open('/opt/xaker/shannon/Dockerfile', 'r') as f:
                dockerfile = f.read().decode('utf-8')
            
            # Ensure PATH is set before USER pentest
            dockerfile_lines = dockerfile.split('\n')
            for i, line in enumerate(dockerfile_lines):
                if 'USER pentest' in line:
                    # Insert PATH before USER
                    dockerfile_lines.insert(i, 'ENV PATH="/usr/bin:/usr/local/bin:$PATH"')
                    print(f"   ✅ Added PATH before USER at line {i+1}")
                    break
            
            dockerfile = '\n'.join(dockerfile_lines)
            with sftp.open('/opt/xaker/shannon/Dockerfile', 'w') as f:
                f.write(dockerfile.encode('utf-8'))
            
            sftp.close()
            
            # Rebuild and restart
            print("\n4. Rebuilding worker image...")
            stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose build --no-cache worker 2>&1 | tail -20')
            build_output = stdout.read().decode('utf-8', errors='replace')
            print(build_output)
            
            if 'Successfully' in build_output:
                print("\n5. Restarting worker...")
                stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose stop worker && docker-compose rm -f worker && docker-compose up -d worker')
                restart_output = stdout.read().decode('utf-8', errors='replace')
                print(restart_output)
                
                import time
                time.sleep(5)
                
                # Verify
                print("\n6. Verifying fix...")
                stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon | grep worker')
                worker = stdout.read().decode('utf-8', errors='replace')
                if worker:
                    container_id = worker.split()[0]
                    stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "su pentest -c \'echo PATH=$PATH && which node && node --version\'"')
                    verify = stdout.read().decode('utf-8', errors='replace')
                    print(verify)
                    
                    if 'v22' in verify:
                        print("\n   ✅ Node is accessible for pentest user!")
                        
                        # Restart backend
                        print("\n7. Restarting backend...")
                        stdin, stdout, stderr = ssh.exec_command('pm2 restart xaker-backend')
                        print(stdout.read().decode('utf-8', errors='replace'))
                        
                        print("\n✅ SUCCESS! Node path fixed")
                        print("Try a new pentest now!")
                    else:
                        print("\n   ⚠️  Node still not accessible")
                else:
                    print("   ⚠️  Worker not running")
            else:
                print("   ⚠️  Build failed")
        else:
            print("\n   ✅ /usr/local/bin is in PATH")
            # But node still not found - check permissions
            print("\n   Checking permissions...")
            stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "ls -la /usr/local/bin/node && su pentest -c \'test -x /usr/local/bin/node && echo OK || echo FAIL\'"')
            perm_check = stdout.read().decode('utf-8', errors='replace')
            print(perm_check)
    
    ssh.close()
    
    print("\n" + "=" * 80)
    print("FIX COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    import time
    fix_node_path()

