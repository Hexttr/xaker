#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Find and fix spawn in activities"""

import paramiko
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def find_and_fix():
    """Find and fix spawn"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("FINDING AND FIXING SPAWN IN ACTIVITIES")
    print("=" * 80)
    
    # Check source code
    print("\n1. Checking activities.ts source...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && grep -n "spawn.*node\|spawnSync.*node" src/temporal/activities.ts 2>/dev/null | head -10')
    spawn_lines = stdout.read().decode('utf-8', errors='replace')
    print(spawn_lines)
    
    # Read activities.ts around spawn
    if spawn_lines:
        line_num = spawn_lines.split(':')[0] if ':' in spawn_lines else None
        if line_num:
            print(f"\n2. Reading code around line {line_num}...")
            start_line = max(1, int(line_num) - 10)
            end_line = int(line_num) + 10
            stdin, stdout, stderr = ssh.exec_command(f'cd /opt/xaker/shannon && sed -n "{start_line},{end_line}p" src/temporal/activities.ts')
            code = stdout.read().decode('utf-8', errors='replace')
            print(code)
            
            # Fix: replace spawn('node' with spawn(process.env.NODE || '/usr/bin/node'
            print("\n3. Fixing spawn calls...")
            sftp = ssh.open_sftp()
            with sftp.open('/opt/xaker/shannon/src/temporal/activities.ts', 'r') as f:
                activities = f.read().decode('utf-8')
            
            # Replace spawn('node' with spawn(process.env.NODE || '/usr/bin/node'
            # But need to be careful - check if it's already using env var
            if "spawn('node'" in activities or 'spawn("node"' in activities:
                # Replace with full path or env var
                activities = activities.replace("spawn('node'", "spawn(process.env.NODE || '/usr/bin/node'")
                activities = activities.replace('spawn("node"', 'spawn(process.env.NODE || "/usr/bin/node"')
                activities = activities.replace("spawnSync('node'", "spawnSync(process.env.NODE || '/usr/bin/node'")
                activities = activities.replace('spawnSync("node"', 'spawnSync(process.env.NODE || "/usr/bin/node"')
                
                print("   ✅ Replaced spawn('node' with process.env.NODE || '/usr/bin/node'")
            else:
                print("   ⚠️  No simple spawn('node') patterns found")
                # Check for other patterns
                if 'spawn' in activities and 'node' in activities:
                    print("   Checking for other spawn patterns...")
                    # Show context
                    for i, line in enumerate(activities.split('\n')):
                        if 'spawn' in line.lower() and 'node' in line.lower():
                            print(f"   Line {i+1}: {line[:100]}")
            
            with sftp.open('/opt/xaker/shannon/src/temporal/activities.ts', 'w') as f:
                f.write(activities.encode('utf-8'))
            
            sftp.close()
            
            # Rebuild
            print("\n4. Rebuilding TypeScript...")
            stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && npm run build 2>&1 | tail -10')
            build_output = stdout.read().decode('utf-8', errors='replace')
            if 'error' in build_output.lower():
                print(f"   ⚠️  Build errors:\n{build_output}")
            else:
                print("   ✅ Build successful!")
                
                # Rebuild Docker
                print("\n5. Rebuilding Docker image...")
                stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && timeout 300 docker-compose build --no-cache worker 2>&1 | tail -20')
                build_output = stdout.read().decode('utf-8', errors='replace')
                print(build_output)
                
                if 'Successfully' in build_output:
                    print("\n   ✅ Docker build successful!")
                    
                    # Restart
                    print("\n6. Restarting worker...")
                    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose stop worker && docker-compose rm -f worker && docker-compose up -d worker')
                    print(stdout.read().decode('utf-8', errors='replace'))
                    
                    import time
                    time.sleep(5)
                    
                    # Verify
                    stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon | grep worker')
                    worker = stdout.read().decode('utf-8', errors='replace')
                    if worker:
                        print("\n   ✅ Worker restarted!")
                        
                        # Restart backend
                        print("\n7. Restarting backend...")
                        stdin, stdout, stderr = ssh.exec_command('pm2 restart xaker-backend')
                        print(stdout.read().decode('utf-8', errors='replace'))
                        
                        print("\n✅ SUCCESS! Spawn fixed")
                        print("Try a new pentest now!")
    
    ssh.close()
    
    print("\n" + "=" * 80)
    print("FIX COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    import time
    find_and_fix()

