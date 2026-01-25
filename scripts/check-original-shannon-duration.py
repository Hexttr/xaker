#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check how Duration is used in original Shannon"""

import paramiko
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def check_original():
    """Check original Shannon usage"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("CHECKING ORIGINAL SHANNON DURATION USAGE")
    print("=" * 80)
    
    # Check package.json to see what Temporal packages are used
    print("\n1. Checking package.json...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && cat package.json | grep -A 5 -B 5 temporalio')
    print(stdout.read().decode('utf-8', errors='replace'))
    
    # Check if there's a way to create Duration from strings
    # In Temporal, retry policies can use strings directly!
    print("\n2. Checking current workflows.ts retry policies...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && sed -n "45,50p" src/temporal/workflows.ts')
    print(stdout.read().decode('utf-8', errors='replace'))
    
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && sed -n "62,67p" src/temporal/workflows.ts')
    print(stdout.read().decode('utf-8', errors='replace'))
    
    # Actually, in Temporal, retry policies CAN use strings directly!
    # Let's revert to strings instead of Duration.from()
    print("\n3. Temporal retry policies support strings directly!")
    print("   We should use strings like '5 minutes' instead of Duration.from()")
    
    ssh.close()
    
    print("\n" + "=" * 80)
    print("SOLUTION: Use strings directly in retry policies")
    print("=" * 80)

if __name__ == "__main__":
    check_original()

