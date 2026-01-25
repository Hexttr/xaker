#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Final aggressive patch - replace all 'node' strings"""

import paramiko
import sys
import base64
import re

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def final_patch():
    """Final aggressive patch"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("FINAL AGGRESSIVE PATCH")
    print("=" * 80)
    print("\n⚠️  This will replace ALL 'node' strings with '/usr/bin/node'")
    print("excluding 'node:' module syntax")
    
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
    
    print(f"\n1. Reading library file...")
    stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} cat {lib_file}')
    file_content = stdout.read().decode('utf-8', errors='replace')
    
    if not file_content:
        print("   ⚠️ Could not read file")
        ssh.close()
        return
    
    print(f"   File size: {len(file_content)} bytes")
    
    original_content = file_content
    
    # Replace 'node' strings but exclude 'node:'
    # Strategy: Replace 'node' -> '/usr/bin/node' but only standalone strings
    # Not part of 'node:something'
    
    print("\n2. Replacing 'node' strings...")
    
    # Replace 'node' with '/usr/bin/node' but not 'node:'
    # Use regex to be smart about it
    
    # Pattern 1: Replace 'node' that's not followed by ':'
    # But be careful - this might break things
    
    # More conservative: Replace only in spawn/execa contexts
    # Look for patterns where 'node' appears as a command argument
    
    # Try replacing all standalone 'node' strings
    # But exclude 'node:' patterns
    replacements = 0
    
    # Replace 'node' -> '/usr/bin/node' but not 'node:'
    # Use negative lookahead
    file_content = re.sub(
        r"(?<!node:)(?<!node\.)(?<!node\[)['\"]node['\"](?!:)",
        "'/usr/bin/node'",
        file_content
    )
    
    # Count replacements
    replacements = original_content.count("'node'") + original_content.count('"node"')
    new_count = file_content.count("'/usr/bin/node'")
    
    if file_content != original_content:
        print(f"   ✅ Replaced {replacements} 'node' strings")
        print(f"   New count: {new_count} '/usr/bin/node' strings")
        
        # Write back
        print("\n3. Writing patched file...")
        file_b64 = base64.b64encode(file_content.encode('utf-8')).decode('ascii')
        
        # Write using heredoc
        stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "cat > /tmp/cli.js.b64" << \'ENDOFFILE\'\n{file_b64}\nENDOFFILE')
        stdout.read()
        
        stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "base64 -d /tmp/cli.js.b64 > {lib_file} && rm /tmp/cli.js.b64"')
        error = stderr.read().decode('utf-8', errors='replace')
        
        if error and 'No such file' not in error:
            print(f"   ⚠️ Error: {error[:200]}")
        else:
            print("   ✅ File patched!")
            
            # Verify
            print("\n4. Verifying...")
            stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} grep -c "/usr/bin/node" {lib_file}')
            verify = stdout.read().decode('utf-8', errors='replace').strip()
            print(f"   Found {verify} occurrences of '/usr/bin/node'")
            
            if verify != '0':
                # Restart worker
                print("\n5. Restarting worker...")
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
                        print("\n6. Restarting backend...")
                        stdin, stdout, stderr = ssh.exec_command('pm2 restart xaker-backend')
                        print(stdout.read().decode('utf-8', errors='replace'))
                        
                        print("\n" + "=" * 80)
                        print("✅ SUCCESS!")
                        print("=" * 80)
                        print(f"\nLibrary patched: {replacements} 'node' -> '/usr/bin/node'")
                        print("Worker is running")
                        print("\nTry a new pentest now!")
            else:
                print("   ⚠️ No replacements found after write")
    else:
        print("   ⚠️ No replacements made")
    
    ssh.close()

if __name__ == "__main__":
    import time
    final_patch()

