#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix imports correctly by reading actual file content"""

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

def fix_imports():
    """Fix imports correctly"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("FIXING IMPORTS CORRECTLY")
    print("=" * 80)
    
    sftp = ssh.open_sftp()
    
    # Fix workflows.ts
    print("\n1. Reading workflows.ts...")
    with sftp.open('/opt/xaker/shannon/src/temporal/workflows.ts', 'r') as f:
        workflows = f.read().decode('utf-8')
    
    workflows_lines = workflows.split('\n')
    
    # Show first 30 lines to see imports
    print("\n   First 30 lines:")
    for i, line in enumerate(workflows_lines[:30]):
        if 'import' in line.lower():
            print(f"   Line {i+1}: {line}")
    
    # Check if Duration is imported
    has_duration = False
    for i, line in enumerate(workflows_lines[:30]):
        if 'Duration' in line and 'import' in line:
            has_duration = True
            print(f"\n   ✅ Duration already imported at line {i+1}")
            break
    
    if not has_duration:
        # Add Duration import from @temporalio/common
        # Find where to insert (after other imports)
        insert_pos = -1
        for i, line in enumerate(workflows_lines[:30]):
            if 'from "@temporalio/common"' in line:
                # Add Duration to this import
                if 'Duration' not in line:
                    workflows_lines[i] = line.replace('}', ', Duration }')
                    print(f"\n   ✅ Added Duration to existing @temporalio/common import at line {i+1}")
                    has_duration = True
                    break
            elif 'from "@temporalio' in line and insert_pos == -1:
                insert_pos = i
        
        if not has_duration:
            # Add new import line
            if insert_pos >= 0:
                workflows_lines.insert(insert_pos + 1, "import { Duration } from '@temporalio/common';")
                print(f"\n   ✅ Added new Duration import at line {insert_pos + 2}")
            else:
                # Insert at the beginning
                workflows_lines.insert(0, "import { Duration } from '@temporalio/common';")
                print(f"\n   ✅ Added Duration import at line 1")
    
    with sftp.open('/opt/xaker/shannon/src/temporal/workflows.ts', 'w') as f:
        f.write('\n'.join(workflows_lines).encode('utf-8'))
    
    # Fix client.ts
    print("\n2. Reading client.ts...")
    with sftp.open('/opt/xaker/shannon/src/temporal/client.ts', 'r') as f:
        client = f.read().decode('utf-8')
    
    client_lines = client.split('\n')
    
    # Show imports
    print("\n   First 30 lines:")
    for i, line in enumerate(client_lines[:30]):
        if 'import' in line.lower():
            print(f"   Line {i+1}: {line}")
    
    # Check if Duration is imported
    has_duration_client = False
    for i, line in enumerate(client_lines[:30]):
        if 'Duration' in line and 'import' in line:
            has_duration_client = True
            print(f"\n   ✅ Duration already imported at line {i+1}")
            break
    
    if not has_duration_client:
        # Add Duration to @temporalio/client import
        for i, line in enumerate(client_lines[:30]):
            if 'from "@temporalio/client"' in line:
                if 'Duration' not in line:
                    client_lines[i] = line.replace('}', ', Duration }')
                    print(f"\n   ✅ Added Duration to @temporalio/client import at line {i+1}")
                    has_duration_client = True
                    break
    
    # Fix line 207 - handle.result() doesn't take timeout argument
    print("\n3. Fixing client.ts line 207...")
    for i, line in enumerate(client_lines):
        if i == 206:  # Line 207
            print(f"   Before: {line}")
            # handle.result() doesn't take arguments in Temporal
            # We need to use handle.result() without timeout, or use a different approach
            # Actually, timeout should be set on the workflow execution, not on result()
            # Let's remove the timeout argument
            if 'timeout:' in line:
                # Remove timeout argument
                client_lines[i] = re.sub(
                    r'handle\.result\(\{\s*timeout:.*?\}\)',
                    'handle.result()',
                    line
                )
                print(f"   After:  {client_lines[i]}")
    
    with sftp.open('/opt/xaker/shannon/src/temporal/client.ts', 'w') as f:
        f.write('\n'.join(client_lines).encode('utf-8'))
    
    sftp.close()
    
    # Rebuild
    print("\n4. Rebuilding TypeScript...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && npm run build 2>&1')
    build_output = stdout.read(100000).decode('utf-8', errors='replace')
    
    if 'error' in build_output.lower():
        print("   ⚠️  Build has errors:")
        # Extract errors
        error_lines = [line for line in build_output.split('\n') if 'error' in line.lower()]
        for err in error_lines[-10:]:
            print(f"   {err}")
    else:
        print("   ✅ Build successful!")
        print(build_output[-500:])
    
    ssh.close()
    
    print("\n" + "=" * 80)
    print("FIX COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    fix_imports()

