#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Find exact spawn node call"""

import paramiko
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def find_exact():
    """Find exact spawn node"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("Finding exact spawn('node') call...")
    
    stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon | grep worker')
    worker = stdout.read().decode('utf-8', errors='replace')
    if not worker:
        print("Worker not running")
        ssh.close()
        return
    
    container_id = worker.split()[0]
    lib_file = '/app/node_modules/@anthropic-ai/claude-agent-sdk/cli.js'
    
    # Search for 'node' near spawn
    print("\n1. Searching for 'node' string near spawn calls...")
    stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} grep -o ".{0,50}spawn.{0,50}node.{0,50}" {lib_file} | head -10')
    matches = stdout.read().decode('utf-8', errors='replace')
    print(matches[:2000])
    
    # Try to find the exact pattern
    print("\n2. Reading file and searching for patterns...")
    stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} cat {lib_file} | grep -o "spawn[^(]*([^)]*node[^)]*)" | head -10')
    exact_matches = stdout.read().decode('utf-8', errors='replace')
    print(exact_matches[:2000])
    
    # Try sed to find context
    print("\n3. Finding context around spawn calls...")
    stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sed -n "s/.*spawn.*node.*/&/p" {lib_file} | head -5')
    context = stdout.read().decode('utf-8', errors='replace')
    print(context[:2000])
    
    ssh.close()

if __name__ == "__main__":
    find_exact()

