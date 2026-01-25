#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix PATH in docker-compose.yml"""

import paramiko
import sys
import os

# Fix encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def fix_path():
    """Fix PATH in docker-compose.yml"""
    print("=" * 80)
    print("FIXING PATH IN DOCKER-COMPOSE.YML")
    print("=" * 80)
    
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
        
        # Read docker-compose.yml
        print("\n1. Reading docker-compose.yml...")
        stdin, stdout, stderr = ssh.exec_command("cat /opt/xaker/shannon/docker-compose.yml")
        compose_content = stdout.read().decode('utf-8', errors='replace')
        
        # Check if PATH already exists
        if 'PATH=' in compose_content and 'worker:' in compose_content:
            print("   PATH already exists, checking...")
            if 'PATH=/usr/bin' in compose_content:
                print("   ✅ PATH already set correctly")
                ssh.close()
                return
        
        # Add PATH to worker environment
        print("\n2. Adding PATH to worker environment...")
        
        # Create a Python script to fix the file
        fix_script = """
import re

with open('/opt/xaker/shannon/docker-compose.yml', 'r') as f:
    content = f.read()

# Find worker section and add PATH after environment:
if 'worker:' in content and 'PATH=' not in content:
    # Add PATH after environment: line in worker section
    pattern = r'(worker:.*?environment:\s*\n)'
    replacement = r'\\1      - PATH=/usr/bin:/usr/local/bin:/bin:/usr/sbin:/sbin\\n'
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    with open('/opt/xaker/shannon/docker-compose.yml', 'w') as f:
        f.write(content)
    print('PATH added')
else:
    print('PATH already exists or worker section not found')
"""
        
        stdin, stdout, stderr = ssh.exec_command(f"python3 -c {repr(fix_script)}")
        output = stdout.read().decode('utf-8', errors='replace')
        errors = stderr.read().decode('utf-8', errors='replace')
        print(output)
        if errors:
            print(f"Errors: {errors}")
        
        # Verify
        print("\n3. Verifying changes...")
        stdin, stdout, stderr = ssh.exec_command("grep -A 10 'worker:' /opt/xaker/shannon/docker-compose.yml | head -15")
        verify = stdout.read().decode('utf-8', errors='replace')
        print(verify)
        
        # Restart worker
        print("\n4. Restarting worker...")
        stdin, stdout, stderr = ssh.exec_command("cd /opt/xaker/shannon && docker-compose restart worker 2>&1")
        restart_output = stdout.read().decode('utf-8', errors='replace')
        print(restart_output)
        
        ssh.close()
        
        print("\n" + "=" * 80)
        print("PATH FIXED")
        print("=" * 80)
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_path()

