#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix TypeScript errors properly"""

import paramiko
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def fix_properly():
    """Fix properly"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("FIXING TYPESCRIPT ERRORS PROPERLY")
    print("=" * 80)
    
    # Fix client.ts line 207
    print("\n1. Fixing client.ts line 207...")
    sftp = ssh.open_sftp()
    with sftp.open('/opt/xaker/shannon/src/temporal/client.ts', 'r') as f:
        content = f.read().decode('utf-8')
    
    lines = content.split('\n')
    
    # Find and fix line 207
    for i, line in enumerate(lines):
        if i == 206:  # Line 207 (0-indexed)
            print(f"   Original line 207: {line}")
            # Fix ms( 3h) -> Duration.from({ hours: 3 })
            if 'ms(' in line and 'h' in line:
                # Replace ms( 3h) with Duration.from({ hours: 3 })
                import re
                new_line = re.sub(r'ms\(\s*(\d+)\s*h\s*\)', r'Duration.from({ hours: \1 })', line)
                lines[i] = new_line
                print(f"   Fixed line 207: {new_line}")
    
    # Ensure Duration is imported
    if 'Duration' not in '\n'.join(lines[:30]):
        for i, line in enumerate(lines[:30]):
            if 'from "@temporalio/client"' in line:
                if 'Duration' not in line:
                    lines[i] = line.replace('}', ', Duration }')
                    print(f"   Added Duration import at line {i+1}")
                break
    
    with sftp.open('/opt/xaker/shannon/src/temporal/client.ts', 'w') as f:
        f.write('\n'.join(lines).encode('utf-8'))
    
    # Fix workflows.ts
    print("\n2. Fixing workflows.ts...")
    with sftp.open('/opt/xaker/shannon/src/temporal/workflows.ts', 'r') as f:
        workflows = f.read().decode('utf-8')
    
    workflows_lines = workflows.split('\n')
    
    # Fix lines 74 and 81
    for i, line in enumerate(workflows_lines):
        if i == 73 or i == 80:  # Lines 74 and 81
            print(f"   Original line {i+1}: {line[:80]}")
            # Replace string durations with Duration.from()
            import re
            new_line = re.sub(r'initialInterval:\s*["\'](\d+)\s*h["\']', r'initialInterval: Duration.from({ hours: \1 })', line)
            new_line = re.sub(r'maximumInterval:\s*["\'](\d+)\s*h["\']', r'maximumInterval: Duration.from({ hours: \1 })', new_line)
            workflows_lines[i] = new_line
            print(f"   Fixed line {i+1}: {new_line[:80]}")
    
    # Ensure Duration is imported
    if 'Duration' not in '\n'.join(workflows_lines[:30]):
        for i, line in enumerate(workflows_lines[:30]):
            if 'from "@temporalio' in line:
                if 'Duration' not in line:
                    workflows_lines[i] = line.replace('}', ', Duration }')
                    print(f"   Added Duration import at line {i+1}")
                break
    
    with sftp.open('/opt/xaker/shannon/src/temporal/workflows.ts', 'w') as f:
        f.write('\n'.join(workflows_lines).encode('utf-8'))
    
    sftp.close()
    
    # Rebuild
    print("\n3. Rebuilding...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && npm run build 2>&1')
    build_output = stdout.read(100000).decode('utf-8', errors='replace')
    if 'error' not in build_output.lower():
        print("   ✅ Build successful")
    else:
        print(f"   Build output (last 500): {build_output[-500:]}")
    
    ssh.close()
    
    print("\n" + "=" * 80)
    print("FIX COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    fix_properly()

