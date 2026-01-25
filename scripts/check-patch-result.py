#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check if patch was applied"""

import paramiko
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def check_patch():
    """Check patch"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    file_path = '/app/node_modules/@anthropic-ai/claude-agent-sdk/cli.js'
    
    print("Checking if patch was applied...")
    
    # Check for patched patterns
    stdin, stdout, stderr = ssh.exec_command(f'docker exec shannon_worker_1 grep -o "spawn.*/usr/bin/node" {file_path} | head -5')
    patched = stdout.read().decode('utf-8', errors='replace')
    
    stdin, stdout, stderr = ssh.exec_command(f'docker exec shannon_worker_1 grep -o "spawn.*[\'\\\"]node[\'\\\"]" {file_path} | head -5')
    unpatched = stdout.read().decode('utf-8', errors='replace')
    
    print(f"Patched patterns: {patched[:300]}")
    print(f"Unpatched patterns: {unpatched[:300]}")
    
    if patched and not unpatched:
        print("SUCCESS! File is patched")
    elif patched and unpatched:
        print("PARTIAL: Some patterns patched, some not")
    else:
        print("FAILED: File not patched")
        print("Trying alternative approach...")
        
        # Try to find the exact location
        stdin, stdout, stderr = ssh.exec_command(f'docker exec shannon_worker_1 grep -n "node" {file_path} | grep -i spawn | head -10')
        spawn_lines = stdout.read().decode('utf-8', errors='replace')
        print(f"Spawn lines with node: {spawn_lines[:500]}")
    
    ssh.close()

if __name__ == "__main__":
    check_patch()

