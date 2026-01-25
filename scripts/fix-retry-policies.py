#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix retry policies in workflows.ts"""

import paramiko
import sys
import re

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def fix_retry():
    """Fix retry policies"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("FIXING RETRY POLICIES")
    print("=" * 80)
    
    file_path = '/opt/xaker/shannon/src/temporal/workflows.ts'
    
    # Read file
    print(f"\n1. Reading {file_path}...")
    sftp = ssh.open_sftp()
    with sftp.open(file_path, 'r') as f:
        content = f.read().decode('utf-8')
    
    lines = content.split('\n')
    
    # Find PRODUCTION_RETRY and TESTING_RETRY definitions
    print("\n2. Finding retry policy definitions...")
    production_start = -1
    testing_start = -1
    
    for i, line in enumerate(lines):
        if 'PRODUCTION_RETRY' in line and '=' in line:
            production_start = i
            print(f"   Found PRODUCTION_RETRY at line {i+1}")
        if 'TESTING_RETRY' in line and '=' in line:
            testing_start = i
            print(f"   Found TESTING_RETRY at line {i+1}")
    
    # Fix PRODUCTION_RETRY
    if production_start >= 0:
        print("\n3. Fixing PRODUCTION_RETRY...")
        i = production_start + 1
        while i < len(lines) and i < production_start + 10:
            if 'initialInterval:' in lines[i]:
                print(f"   Line {i+1}: {lines[i]}")
                lines[i] = re.sub(
                    r'initialInterval:\s*["\'](\d+)\s*h["\']',
                    r'initialInterval: Duration.from({ hours: \1 })',
                    lines[i]
                )
                print(f"   Fixed: {lines[i]}")
            if 'maximumInterval:' in lines[i]:
                print(f"   Line {i+1}: {lines[i]}")
                lines[i] = re.sub(
                    r'maximumInterval:\s*["\'](\d+)\s*h["\']',
                    r'maximumInterval: Duration.from({ hours: \1 })',
                    lines[i]
                )
                print(f"   Fixed: {lines[i]}")
            if lines[i].strip() == '},' or lines[i].strip() == '};':
                break
            i += 1
    
    # Fix TESTING_RETRY
    if testing_start >= 0:
        print("\n4. Fixing TESTING_RETRY...")
        i = testing_start + 1
        while i < len(lines) and i < testing_start + 10:
            if 'initialInterval:' in lines[i]:
                print(f"   Line {i+1}: {lines[i]}")
                lines[i] = re.sub(
                    r'initialInterval:\s*["\'](\d+)\s*h["\']',
                    r'initialInterval: Duration.from({ hours: \1 })',
                    lines[i]
                )
                print(f"   Fixed: {lines[i]}")
            if 'maximumInterval:' in lines[i]:
                print(f"   Line {i+1}: {lines[i]}")
                lines[i] = re.sub(
                    r'maximumInterval:\s*["\'](\d+)\s*h["\']',
                    r'maximumInterval: Duration.from({ hours: \1 })',
                    lines[i]
                )
                print(f"   Fixed: {lines[i]}")
            if lines[i].strip() == '},' or lines[i].strip() == '};':
                break
            i += 1
    
    # Ensure Duration is imported
    print("\n5. Ensuring Duration is imported...")
    duration_imported = False
    for i, line in enumerate(lines[:30]):
        if 'from "@temporalio' in line:
            if 'Duration' in line:
                duration_imported = True
                print(f"   Duration already imported at line {i+1}")
            else:
                lines[i] = line.replace('}', ', Duration }')
                duration_imported = True
                print(f"   Added Duration import at line {i+1}")
                break
    
    # Write back
    print("\n6. Writing fixed file...")
    with sftp.open(file_path, 'w') as f:
        f.write('\n'.join(lines).encode('utf-8'))
    
    sftp.close()
    
    # Rebuild
    print("\n7. Rebuilding...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && npm run build 2>&1 | tail -10')
    build_output = stdout.read().decode('utf-8', errors='replace')
    print(build_output[-500:])
    
    if 'error' not in build_output.lower():
        print("   ✅ Build successful!")
    else:
        print("   ⚠️  Build still has errors")
    
    ssh.close()
    
    print("\n" + "=" * 80)
    print("FIX COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    fix_retry()

