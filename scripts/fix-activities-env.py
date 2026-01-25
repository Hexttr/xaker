#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix activities.ts to pass PATH in env"""

import paramiko
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def fix_activities():
    """Fix activities.ts"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("FIXING ACTIVITIES.TS")
    print("=" * 80)
    
    file_path = '/opt/xaker/shannon/src/temporal/activities.ts'
    
    # Read file
    print(f"\n1. Reading {file_path}...")
    sftp = ssh.open_sftp()
    with sftp.open(file_path, 'r') as f:
        content = f.read().decode('utf-8')
    
    print(f"   File size: {len(content)} bytes")
    
    # Find where claude-agent-sdk is used
    if 'claude-agent-sdk' in content or 'ClaudeCode' in content:
        print("   Found claude-agent-sdk usage")
        
        # Look for initialization or configuration
        lines = content.split('\n')
        new_lines = []
        modified = False
        
        for i, line in enumerate(lines):
            new_lines.append(line)
            
            # Look for ClaudeCode initialization or config
            if 'new ClaudeCode' in line or 'ClaudeCode(' in line or 'claudeCode' in line.lower():
                # Check if env is passed
                j = i + 1
                env_found = False
                while j < len(lines) and j < i + 20:
                    if 'env:' in lines[j] or 'environment:' in lines[j].lower():
                        env_found = True
                        # Check if PATH is in env
                        if 'PATH' not in lines[j] and 'path' not in lines[j].lower():
                            # Add PATH to env
                            indent = len(lines[j]) - len(lines[j].lstrip())
                            new_lines.append(' ' * indent + 'PATH: "/usr/local/bin:/usr/bin:/bin",')
                            modified = True
                            print(f"   Added PATH to env at line {j+1}")
                        break
                    elif '{' in lines[j] and '}' in lines[j]:
                        # Single line object, add PATH
                        if 'PATH' not in lines[j]:
                            # Insert before closing brace
                            new_lines[-1] = line.replace('}', ', PATH: "/usr/local/bin:/usr/bin:/bin" }')
                            modified = True
                            print(f"   Added PATH to object at line {i+1}")
                        break
                    j += 1
                
                if not env_found and not modified:
                    # Add env object
                    indent = len(line) - len(line.lstrip())
                    new_lines.append(' ' * indent + 'env: {')
                    new_lines.append(' ' * (indent + 2) + 'PATH: "/usr/local/bin:/usr/bin:/bin",')
                    new_lines.append(' ' * indent + '},')
                    modified = True
                    print(f"   Added env object at line {i+1}")
        
        if modified:
            # Write back
            print("\n2. Writing updated file...")
            with sftp.open(file_path, 'w') as f:
                f.write('\n'.join(new_lines).encode('utf-8'))
            
            # Rebuild
            print("\n3. Rebuilding...")
            stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && npm run build 2>&1 | tail -30')
            build_output = stdout.read().decode('utf-8', errors='replace')
            if 'error' not in build_output.lower() or 'Successfully' in build_output:
                print("   Build successful")
            else:
                print(f"   Build output: {build_output[-1000:]}")
            
            # Restart worker
            print("\n4. Restarting worker...")
            ssh.exec_command('cd /opt/xaker/shannon && docker-compose restart worker')
        else:
            print("\n2. No changes needed or could not find place to add PATH")
            print("   Checking file content around claude-agent usage...")
            # Show context
            for i, line in enumerate(lines):
                if 'claude' in line.lower() or 'ClaudeCode' in line:
                    start = max(0, i - 5)
                    end = min(len(lines), i + 10)
                    print(f"\n   Lines {start+1}-{end}:")
                    for j in range(start, end):
                        marker = ">>> " if j == i else "    "
                        print(f"{marker}{j+1}: {lines[j]}")
                    break
    else:
        print("   claude-agent-sdk not found in file")
    
    sftp.close()
    ssh.close()
    
    print("\n" + "=" * 80)
    print("FIX COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    fix_activities()

