#!/usr/bin/env python3
"""
Final deployment script - saves output to files and reads them
"""

import subprocess
import os
import time
from pathlib import Path

def main():
    plink = r"C:\Program Files\PuTTY\plink.exe"
    server = "root@5.129.235.52"
    password = "cY7^kCCA_6uQ5S"
    port = 22
    
    if not os.path.exists(plink):
        print(f"ERROR: PuTTY plink not found at {plink}")
        return False
    
    print("=" * 60)
    print("AUTOMATIC DEPLOYMENT")
    print("=" * 60)
    print(f"Server: {server}")
    print()
    
    commands = [
        ("cd /root/xaker && git pull origin prod", "1/4 Pulling changes"),
        ("cd /root/xaker/backend && npm run build", "2/4 Building backend"),
        ("pm2 restart xaker-backend", "3/4 Restarting backend"),
        ("pm2 status xaker-backend", "4/4 Checking status")
    ]
    
    for cmd, desc in commands:
        print(f"\n[{desc}]")
        print("-" * 60)
        print(f"Executing: {cmd}")
        
        output_file = f"deploy_output_{int(time.time())}.txt"
        
        try:
            # Run command and save output
            with open(output_file, 'w', encoding='utf-8') as f:
                process = subprocess.Popen(
                    [plink, '-ssh', '-P', str(port), '-pw', password, server, cmd],
                    stdout=f,
                    stderr=subprocess.STDOUT,
                    stdin=subprocess.PIPE,
                    text=True
                )
                process.stdin.write('y\n')  # Accept host key
                process.stdin.close()
                process.wait(timeout=600)
            
            # Read and display output
            if os.path.exists(output_file):
                with open(output_file, 'r', encoding='utf-8') as f:
                    output = f.read()
                    if output:
                        print(output)
                os.remove(output_file)
            
            print(f"Exit code: {process.returncode}")
            
        except subprocess.TimeoutExpired:
            print("ERROR: Command timed out")
            if os.path.exists(output_file):
                os.remove(output_file)
        except Exception as e:
            print(f"ERROR: {e}")
            if os.path.exists(output_file):
                os.remove(output_file)
    
    print("\n" + "=" * 60)
    print("DEPLOYMENT COMPLETE")
    print("=" * 60)
    return True

if __name__ == "__main__":
    main()


