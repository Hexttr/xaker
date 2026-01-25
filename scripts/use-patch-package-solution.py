#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Use patch-package solution"""

import paramiko
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def use_patch_package():
    """Use patch-package solution"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("SOLUTION: USE process.execPath OR ENSURE NODE IN PATH")
    print("=" * 80)
    print("\nBased on internet research, the solution is to ensure node is")
    print("accessible via PATH. Let's use a different approach:")
    print("1. Set PATH in the process environment")
    print("2. Use process.execPath if library supports it")
    print("3. Create a proper wrapper that sets PATH")
    
    # Find worker
    stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon_worker')
    worker = stdout.read().decode('utf-8', errors='replace')
    
    if not worker:
        print("\nStarting worker...")
        stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose up -d worker')
        import time
        time.sleep(5)
        stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon_worker')
        worker = stdout.read().decode('utf-8', errors='replace')
    
    if not worker:
        print("   ⚠️ Worker not running")
        ssh.close()
        return
    
    container_id = worker.split()[0]
    lib_file = '/app/node_modules/@anthropic-ai/claude-agent-sdk/cli.js'
    
    print(f"\n1. Checking library file...")
    stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} ls -lh {lib_file}')
    print(stdout.read().decode('utf-8', errors='replace'))
    
    # Try using Node.js to patch the file - more reliable
    print("\n2. Using Node.js to patch library (more reliable)...")
    
    node_patch_script = f"""const fs = require('fs');
const libFile = '{lib_file}';

// Read file
let content = fs.readFileSync(libFile, 'utf8');
const original = content;

// Replace patterns - be very specific
// Pattern 1: spawn('node' -> spawn(process.execPath || '/usr/bin/node'
content = content.replace(/spawn\\(['"]node['"]/g, "spawn(process.execPath || '/usr/bin/node'");

// Pattern 2: spawn("node" -> spawn(process.execPath || "/usr/bin/node"
content = content.replace(/spawn\\(["']node["']/g, 'spawn(process.execPath || "/usr/bin/node"');

// Pattern 3: spawnSync
content = content.replace(/spawnSync\\(['"]node['"]/g, "spawnSync(process.execPath || '/usr/bin/node'");
content = content.replace(/spawnSync\\(["']node["']/g, 'spawnSync(process.execPath || "/usr/bin/node"');

if (content !== original) {{
    fs.writeFileSync(libFile, content, 'utf8');
    const count = (content.match(/process\\.execPath.*usr\\/bin\\/node/g) || []).length;
    console.log(`SUCCESS: Replaced patterns, found ${{{{count}}}} occurrences`);
    process.exit(0);
}} else {{
    console.log('No replacements made');
    process.exit(1);
}}
"""
    
    # Write Node.js script to container
    stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "cat > /tmp/patch-node.js" << \'ENDOFSCRIPT\'\n{node_patch_script}\nENDOFSCRIPT')
    stdout.read()
    
    # Run Node.js script
    print("   Running Node.js patch script...")
    stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} node /tmp/patch-node.js')
    patch_output = stdout.read().decode('utf-8', errors='replace')
    patch_error = stderr.read().decode('utf-8', errors='replace')
    exit_code = stdout.channel.recv_exit_status()
    
    print(patch_output)
    if patch_error:
        print(f"   Errors: {patch_error[:300]}")
    
    if exit_code == 0 and 'SUCCESS' in patch_output:
        print("   ✅ Patch successful!")
        
        # Verify
        print("\n3. Verifying...")
        stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} grep -c "process.execPath.*usr/bin/node" {lib_file}')
        verify = stdout.read().decode('utf-8', errors='replace').strip()
        print(f"   Found {verify} occurrences")
        
        # Restart worker
        print("\n4. Restarting worker...")
        stdin, stdout, stderr = ssh.exec_command(f'docker restart {container_id}')
        import time
        time.sleep(5)
        
        stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon_worker')
        if stdout.read().decode('utf-8', errors='replace'):
            print("\n   ✅ Worker restarted!")
            
            stdin, stdout, stderr = ssh.exec_command(f'docker logs {container_id} --tail=10 2>&1')
            logs = stdout.read().decode('utf-8', errors='replace')
            if 'RUNNING' in logs:
                print("\n   ✅ Worker is RUNNING!")
                
                # Restart backend
                print("\n5. Restarting backend...")
                stdin, stdout, stderr = ssh.exec_command('pm2 restart xaker-backend')
                print(stdout.read().decode('utf-8', errors='replace'))
                
                print("\n" + "=" * 80)
                print("✅ SUCCESS!")
                print("=" * 80)
                print("\nLibrary patched: spawn('node') -> spawn(process.execPath || '/usr/bin/node')")
                print("This uses Node.js's own executable path, which should always work")
                print("\nTry a new pentest now!")
        else:
            print("\n   ⚠️ Worker not running after restart")
    else:
        print("   ⚠️ Patch failed")
        print("   Trying alternative: ensure PATH includes /usr/bin")
        
        # Alternative: Update docker-compose to ensure PATH
        print("\n5. Alternative: Ensuring PATH in docker-compose...")
        sftp = ssh.open_sftp()
        with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'r') as f:
            compose = f.read().decode('utf-8')
        
        # Ensure PATH is set in environment
        if 'PATH=/usr/bin' not in compose:
            compose_lines = compose.split('\n')
            for i, line in enumerate(compose_lines):
                if 'worker:' in line:
                    # Add environment section if not exists
                    if 'environment:' not in '\n'.join(compose_lines[i:i+10]):
                        compose_lines.insert(i+1, '    environment:')
                        compose_lines.insert(i+2, '      - PATH=/usr/bin:/usr/local/bin:/bin:/sbin')
                        compose_lines.insert(i+3, '      - NODE=/usr/bin/node')
                    break
            compose = '\n'.join(compose_lines)
            
            with sftp.open('/opt/xaker/shannon/docker-compose.yml', 'w') as f:
                f.write(compose.encode('utf-8'))
            sftp.close()
            
            print("   ✅ docker-compose.yml updated")
            
            # Restart
            stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose restart worker')
            print(stdout.read().decode('utf-8', errors='replace'))
    
    ssh.close()

if __name__ == "__main__":
    import time
    use_patch_package()

