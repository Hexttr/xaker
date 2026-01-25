#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Create node wrapper script in /usr/local/bin"""

import paramiko
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def create_wrapper():
    """Create wrapper script"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("CREATING NODE WRAPPER SCRIPT")
    print("=" * 80)
    
    # Create wrapper script
    wrapper_script = """#!/bin/sh
# Node wrapper script
exec /usr/bin/node "$@"
"""
    
    print("\n1. Creating wrapper script...")
    # Write via echo
    cmd = f'docker exec -u root shannon_worker_1 sh -c "echo \'#!/bin/sh\nexec /usr/bin/node \\"$@\\"\n\' > /usr/local/bin/node && chmod +x /usr/local/bin/node"'
    stdin, stdout, stderr = ssh.exec_command(cmd)
    result = stdout.read().decode('utf-8', errors='replace')
    errors = stderr.read().decode('utf-8', errors='replace')
    
    if errors:
        print(f"   Error: {errors[:200]}")
    else:
        print("   Wrapper script created")
    
    # Verify
    print("\n2. Verifying wrapper...")
    stdin, stdout, stderr = ssh.exec_command('docker exec shannon_worker_1 ls -la /usr/local/bin/node && docker exec shannon_worker_1 cat /usr/local/bin/node')
    verify = stdout.read().decode('utf-8', errors='replace')
    print(verify)
    
    # Test wrapper
    print("\n3. Testing wrapper...")
    stdin, stdout, stderr = ssh.exec_command('docker exec shannon_worker_1 /usr/local/bin/node --version')
    version = stdout.read().decode('utf-8', errors='replace')
    print(f"   Node version: {version}")
    
    # Also create symlink as backup
    print("\n4. Creating symlink as backup...")
    ssh.exec_command('docker exec -u root shannon_worker_1 ln -sf /usr/bin/node /usr/local/bin/node-link 2>&1')
    
    ssh.close()
    
    print("\n" + "=" * 80)
    print("WRAPPER CREATED")
    print("=" * 80)
    if 'node' in verify.lower():
        print("SUCCESS! Wrapper script created")
        print("Try a new pentest now")
    else:
        print("Wrapper may not be created correctly")

if __name__ == "__main__":
    create_wrapper()

