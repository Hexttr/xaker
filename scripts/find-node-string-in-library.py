#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Find where 'node' string is used as command"""

import paramiko
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def find_node_string():
    """Find node string in library"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("Finding 'node' string usage in library...")
    
    stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon | grep worker')
    worker = stdout.read().decode('utf-8', errors='replace')
    if not worker:
        print("Worker not running")
        ssh.close()
        return
    
    container_id = worker.split()[0]
    lib_file = '/app/node_modules/@anthropic-ai/claude-agent-sdk/cli.js'
    
    # Find all occurrences of 'node' that might be commands
    print("\n1. Finding 'node' strings (excluding 'node:' module syntax)...")
    stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} grep -o "[\'\\"]node[\'\\"]" {lib_file} | head -20')
    node_strings = stdout.read().decode('utf-8', errors='replace')
    print(f"Found {len(node_strings.split())} occurrences")
    
    # Find context around 'node' strings
    print("\n2. Finding context around 'node' strings...")
    stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} grep -n "[\'\\"]node[\'\\"]" {lib_file} | grep -v "node:" | head -20')
    contexts = stdout.read().decode('utf-8', errors='replace')
    print(contexts[:2000])
    
    # Try to find execa/spawn calls that use 'node'
    print("\n3. Finding execa/spawn calls...")
    stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} grep -o ".{0,100}execa.{0,200}" {lib_file} | head -10')
    execa_calls = stdout.read().decode('utf-8', errors='replace')
    print(execa_calls[:2000])
    
    # Check if library uses process.execPath or similar
    print("\n4. Checking for process.execPath or similar...")
    stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} grep -n "process.execPath\|process.exec\|execPath" {lib_file} | head -10')
    exec_path = stdout.read().decode('utf-8', errors='replace')
    if exec_path:
        print(exec_path)
    else:
        print("   Not found")
    
    ssh.close()

if __name__ == "__main__":
    find_node_string()

