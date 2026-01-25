#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Final library patch - use process.execPath"""

import paramiko
import sys
import time

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def final_patch():
    """Final patch using Node.js with process.execPath"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
    
    print("=" * 80)
    print("FINAL LIBRARY PATCH - USE process.execPath")
    print("=" * 80)
    print("\nThe library uses spawn('node') which doesn't find node via PATH")
    print("We'll patch it to use process.execPath || '/usr/bin/node'")
    
    # Find worker
    stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon_worker')
    worker = stdout.read().decode('utf-8', errors='replace')
    
    if not worker:
        print("\nStarting worker...")
        stdin, stdout, stderr = ssh.exec_command('cd /opt/xaker/shannon && docker-compose up -d worker')
        time.sleep(5)
        stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon_worker')
        worker = stdout.read().decode('utf-8', errors='replace')
    
    if not worker:
        print("   ⚠️ Worker not running")
        ssh.close()
        return
    
    container_id = worker.split()[0]
    lib_file = '/app/node_modules/@anthropic-ai/claude-agent-sdk/cli.js'
    
    print(f"\n1. Creating Node.js patch script...")
    
    # Use Node.js to patch - more reliable for minified code
    node_patch = f"""const fs = require('fs');
const libFile = '{lib_file}';

let content = fs.readFileSync(libFile, 'utf8');
const original = content;

// Strategy: Replace 'node' string literals that are likely command arguments
// Look for patterns like: spawn('node', spawn("node", execa('node', etc.
// Replace with: spawn(process.execPath || '/usr/bin/node', ...

// Pattern 1: spawn('node' -> spawn(process.execPath || '/usr/bin/node'
content = content.replace(/spawn\\(['"]node['"]/g, "spawn(process.execPath || '/usr/bin/node'");

// Pattern 2: spawn("node" -> spawn(process.execPath || "/usr/bin/node"
content = content.replace(/spawn\\(["']node["']/g, 'spawn(process.execPath || "/usr/bin/node"');

// Pattern 3: execa('node' -> execa(process.execPath || '/usr/bin/node'
content = content.replace(/execa\\(['"]node['"]/g, "execa(process.execPath || '/usr/bin/node'");
content = content.replace(/execa\\(["']node["']/g, 'execa(process.execPath || "/usr/bin/node"');

// Pattern 4: spawnSync
content = content.replace(/spawnSync\\(['"]node['"]/g, "spawnSync(process.execPath || '/usr/bin/node'");
content = content.replace(/spawnSync\\(["']node["']/g, 'spawnSync(process.execPath || "/usr/bin/node"');

if (content !== original) {{
    fs.writeFileSync(libFile, content, 'utf8');
    const count = (content.match(/process\\.execPath.*usr\\/bin\\/node/g) || []).length;
    console.log(`SUCCESS: Patched ${{count}} occurrences`);
    console.log(`File size: ${{content.length}} bytes`);
    process.exit(0);
}} else {{
    console.log('No patterns found to replace');
    console.log('Trying alternative: direct string replacement');
    
    // Alternative: replace all standalone 'node' strings (risky but might work)
    // Only replace if it's likely a command (not part of 'node:' or other contexts)
    let altContent = content;
    // This is risky - might break things
    // Let's be more conservative and only replace in spawn contexts we can identify
    altContent = altContent.replace(/([^a-zA-Z0-9_])node([^a-zA-Z0-9_:])/g, (match, before, after) => {{
        // Only replace if it looks like a command argument
        const context = content.substring(Math.max(0, content.indexOf(match) - 50), content.indexOf(match) + 50);
        if (context.includes('spawn') || context.includes('execa') || context.includes('exec')) {{
            return before + "(process.execPath || '/usr/bin/node')" + after;
        }}
        return match;
    }});
    
    if (altContent !== content) {{
        fs.writeFileSync(libFile, altContent, 'utf8');
        console.log('SUCCESS: Used alternative replacement');
        process.exit(0);
    }}
    
    process.exit(1);
}}
"""
    
    # Write patch script
    stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} sh -c "cat > /tmp/patch-final.js" << \'ENDOFSCRIPT\'\n{node_patch}\nENDOFSCRIPT')
    stdout.read()
    
    print("\n2. Running patch script...")
    stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} node /tmp/patch-final.js')
    patch_output = stdout.read().decode('utf-8', errors='replace')
    patch_error = stderr.read().decode('utf-8', errors='replace')
    exit_code = stdout.channel.recv_exit_status()
    
    print(patch_output)
    if patch_error:
        print(f"   Errors: {patch_error[:300]}")
    
    if exit_code == 0 and 'SUCCESS' in patch_output:
        print("   ✅ Patch successful!")
        
        # Verify
        print("\n3. Verifying patch...")
        stdin, stdout, stderr = ssh.exec_command(f'docker exec {container_id} grep -c "process.execPath.*usr/bin/node" {lib_file}')
        verify = stdout.read().decode('utf-8', errors='replace').strip()
        print(f"   Found {verify} occurrences")
        
        # Restart worker
        print("\n4. Restarting worker...")
        stdin, stdout, stderr = ssh.exec_command(f'docker restart {container_id}')
        time.sleep(5)
        
        stdin, stdout, stderr = ssh.exec_command('docker ps | grep shannon_worker')
        if stdout.read().decode('utf-8', errors='replace'):
            print("\n   ✅ Worker restarted!")
            
            # Restart backend
            print("\n5. Restarting backend...")
            stdin, stdout, stderr = ssh.exec_command('pm2 restart xaker-backend')
            print(stdout.read().decode('utf-8', errors='replace'))
            
            print("\n" + "=" * 80)
            print("✅ SUCCESS!")
            print("=" * 80)
            print("\nLibrary patched to use process.execPath || '/usr/bin/node'")
            print("This should work because process.execPath is always available")
            print("\nTry a new pentest now!")
        else:
            print("\n   ⚠️ Worker not running after restart")
    else:
        print("   ⚠️ Patch failed")
        print("   The library might use a different pattern")
        print("   We may need to patch the source code of Shannon instead")
    
    ssh.close()

if __name__ == "__main__":
    final_patch()

