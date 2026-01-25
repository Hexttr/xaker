#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix TypeScript errors in Shannon"""

import paramiko
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def fix_typescript():
    """Fix TypeScript errors"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("FIXING TYPESCRIPT ERRORS IN SHANNON")
    print("=" * 80)
    
    file_path = '/opt/xaker/shannon/src/temporal/client.ts'
    
    # Read file
    print(f"\n1. Reading {file_path}...")
    sftp = ssh.open_sftp()
    with sftp.open(file_path, 'r') as f:
        content = f.read().decode('utf-8')
    
    lines = content.split('\n')
    
    # Find line 29 and 207
    print("\n2. Checking problematic lines...")
    for i in [28, 206]:  # 0-indexed
        if i < len(lines):
            print(f"   Line {i+1}: {lines[i][:100]}")
    
    # Fix line 29 - remove 'ms' import if it doesn't exist
    # Fix line 207 - check what's wrong
    new_lines = []
    fixed = False
    
    for i, line in enumerate(lines):
        if i == 28 and 'ms' in line and 'from' in line:
            # Remove ms from import
            line = line.replace(', ms', '').replace('ms,', '').replace(' ms', '').replace('ms ', '')
            fixed = True
            print(f"   ✅ Fixed line {i+1}: removed 'ms' import")
        elif i == 206:
            # Check what's on line 207 (index 206)
            if 'ms(' in line or '.ms(' in line:
                # Replace ms() with Duration.from()
                line = line.replace('ms(', 'Duration.from({ milliseconds: ').replace(').ms(', ').toMillis()')
                # Or simpler - just remove the argument if it's causing issues
                if 'ms(' in line:
                    # Find the pattern and fix it
                    import re
                    line = re.sub(r'ms\((\d+)\s*h\)', r'Duration.from({ hours: \1 })', line)
                fixed = True
                print(f"   ✅ Fixed line {i+1}: replaced ms()")
        
        new_lines.append(line)
    
    if fixed:
        # Write back
        print("\n3. Writing fixed file...")
        with sftp.open(file_path, 'w') as f:
            f.write('\n'.join(new_lines).encode('utf-8'))
        
        # Rebuild
        print("\n4. Rebuilding...")
        stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && npm run build 2>&1 | tail -30')
        build_output = stdout.read().decode('utf-8', errors='replace')
        print(build_output[-1000:])
        
        if 'error' not in build_output.lower():
            print("   ✅ Build successful")
        else:
            print("   ⚠️  Build still has errors")
    else:
        print("\n3. No fixes needed or couldn't identify the issue")
        # Show context around problematic lines
        print("\n   Context around line 29:")
        for i in range(max(0, 25), min(len(lines), 35)):
            marker = ">>> " if i == 28 else "    "
            print(f"{marker}{i+1}: {lines[i]}")
        
        print("\n   Context around line 207:")
        for i in range(max(0, 203), min(len(lines), 213)):
            marker = ">>> " if i == 206 else "    "
            print(f"{marker}{i+1}: {lines[i]}")
    
    sftp.close()
    ssh.close()
    
    print("\n" + "=" * 80)
    print("FIX COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    fix_typescript()

