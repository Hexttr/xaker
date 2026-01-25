#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Create symlink in /usr/local/bin as root"""

import paramiko
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def create_symlink():
    """Create symlink as root"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("Creating symlink /usr/local/bin/node -> /usr/bin/node")
    
    # Create symlink as root
    cmd = 'docker exec -u root shannon_worker_1 sh -c "mkdir -p /usr/local/bin && ln -sf /usr/bin/node /usr/local/bin/node && ls -la /usr/local/bin/node"'
    stdin, stdout, stderr = ssh.exec_command(cmd)
    result = stdout.read().decode('utf-8', errors='replace')
    errors = stderr.read().decode('utf-8', errors='replace')
    
    print(result)
    if errors:
        print(f"Errors: {errors}")
    
    # Verify
    print("\nVerifying...")
    stdin, stdout, stderr = ssh.exec_command('docker exec shannon_worker_1 sh -c "which node && /usr/local/bin/node --version"')
    verify = stdout.read().decode('utf-8', errors='replace')
    print(verify)
    
    if 'node' in result.lower() or '->' in result:
        print("\nSUCCESS! Symlink created. Try a new pentest now.")
    else:
        print("\nSymlink may not be created. Check errors above.")
    
    ssh.close()

if __name__ == "__main__":
    create_symlink()

