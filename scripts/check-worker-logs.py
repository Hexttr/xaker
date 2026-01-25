#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check Shannon worker logs in real-time"""

import paramiko
import sys
import os
import time

# Fix encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

def check_worker():
    """Check worker logs"""
    print("=" * 80)
    print("CHECKING SHANNON WORKER LOGS")
    print("=" * 80)
    
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)
        
        # Get recent worker logs
        print("\n1. Recent worker logs (last 100 lines)...")
        stdin, stdout, stderr = ssh.exec_command("cd /opt/xaker/shannon && docker-compose logs --tail=100 worker 2>&1 | tail -100")
        worker_logs = stdout.read().decode('utf-8', errors='replace')
        print(worker_logs[-5000:])
        
        # Check if worker is processing tasks
        print("\n2. Checking for task processing...")
        if "task" in worker_logs.lower() or "workflow" in worker_logs.lower():
            print("   ✅ Worker is processing tasks")
        else:
            print("   ⚠️  No task processing detected")
        
        # Check Temporal workflow status
        print("\n3. Checking Temporal workflow status...")
        stdin, stdout, stderr = ssh.exec_command("cd /opt/xaker/shannon && docker-compose exec -T temporal tctl workflow list 2>&1 | head -20 || echo 'Cannot check workflows'")
        workflow_status = stdout.read().decode('utf-8', errors='replace')
        print(workflow_status)
        
        ssh.close()
        
        print("\n" + "=" * 80)
        print("ANALYSIS")
        print("=" * 80)
        print("If worker is running but no tasks are processed:")
        print("  1. Workflow may be waiting for input")
        print("  2. Workflow may have failed silently")
        print("  3. Check Temporal UI at http://5.129.235.52:8233")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_worker()

