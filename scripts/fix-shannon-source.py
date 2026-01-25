#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix Shannon source code to pass PATH to spawn"""

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

def fix_source():
    """Fix Shannon source"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("FIXING SHANNON SOURCE")
    print("=" * 80)
    
    # Find activities file
    print("\n1. Finding activities file...")
    stdin, stdout, stderr = ssh.exec_command('find /opt/xaker/shannon -name "activities.*" -type f | grep -E "\\.(ts|js)$" | head -5')
    files = stdout.read().decode('utf-8', errors='replace').strip().split('\n')
    files = [f for f in files if f]
    
    if not files:
        print("   No activities file found, checking dist...")
        stdin, stdout, stderr = ssh.exec_command('find /opt/xaker/shannon/dist -name "*activities*" -type f | head -5')
        files = stdout.read().decode('utf-8', errors='replace').strip().split('\n')
        files = [f for f in files if f]
    
    print(f"   Found {len(files)} files")
    
    # Check each file
    for file_path in files:
        print(f"\n2. Checking {file_path}...")
        
        # Read file
        stdin, stdout, stderr = ssh.exec_command(f'cat {file_path}')
        content = stdout.read().decode('utf-8', errors='replace')
        
        # Look for spawn or claude-agent-sdk usage
        if 'spawn' in content.lower() or 'claude-agent' in content.lower() or 'claudeCode' in content:
            print(f"   Found relevant code in {file_path}")
            
            # Check if it's TypeScript source
            if file_path.endswith('.ts') and 'src' in file_path:
                print("   This is TypeScript source - need to rebuild")
                # Try to add PATH to spawn options
                if 'spawn(' in content or 'spawnSync(' in content:
                    # Find spawn calls and add env with PATH
                    lines = content.split('\n')
                    new_lines = []
                    modified = False
                    
                    for i, line in enumerate(lines):
                        new_lines.append(line)
                        
                        # Look for spawn calls
                        if 'spawn(' in line or 'spawnSync(' in line:
                            # Check if next lines have options
                            j = i + 1
                            while j < len(lines) and (lines[j].strip().startswith(',') or lines[j].strip().startswith('{')):
                                if 'env:' in lines[j] or 'env =' in lines[j]:
                                    # Already has env, add PATH to it
                                    if 'PATH' not in lines[j]:
                                        new_lines[-1] = line.replace('env:', 'env: { ...env, PATH: process.env.PATH || "/usr/local/bin:/usr/bin:/bin" },')
                                        modified = True
                                    break
                                elif '{' in lines[j] and '}' not in lines[j]:
                                    # Multi-line options, add env
                                    indent = len(lines[j]) - len(lines[j].lstrip())
                                    new_lines.append(' ' * indent + 'env: { ...process.env, PATH: "/usr/local/bin:/usr/bin:/bin" },')
                                    modified = True
                                    break
                                new_lines.append(lines[j])
                                j += 1
                    
                    if modified:
                        # Write back
                        sftp = ssh.open_sftp()
                        with sftp.open(file_path, 'w') as f:
                            f.write('\n'.join(new_lines).encode('utf-8'))
                        sftp.close()
                        print("   File modified - need to rebuild")
                    else:
                        print("   Could not find spawn calls to modify")
            
            # Check dist file
            elif file_path.endswith('.js') and 'dist' in file_path:
                print("   This is compiled JS - patching directly")
                # Try to patch compiled JS
                # This is harder, but we can try
                if 'spawn(' in content:
                    # Try to add PATH to options
                    content = re.sub(
                        r'(spawn\([^,]+,\s*[^,]+,\s*\{)([^}]*)(\})',
                        r'\1\2, env: { ...process.env, PATH: "/usr/local/bin:/usr/bin:/bin" }\3',
                        content
                    )
                    
                    # Write back
                    sftp = ssh.open_sftp()
                    with sftp.open(file_path, 'w') as f:
                        f.write(content.encode('utf-8'))
                    sftp.close()
                    print("   File patched")
    
    # Rebuild if source was modified
    print("\n3. Rebuilding if needed...")
    stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && npm run build 2>&1 | tail -20')
    build_output = stdout.read().decode('utf-8', errors='replace')
    if 'error' not in build_output.lower():
        print("   Build successful")
    else:
        print(f"   Build errors: {build_output[-500:]}")
    
    # Restart worker
    print("\n4. Restarting worker...")
    ssh.exec_command('cd /opt/xaker/shannon && docker-compose restart worker')
    
    ssh.close()
    
    print("\n" + "=" * 80)
    print("FIX COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    fix_source()

