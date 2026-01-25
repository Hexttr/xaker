#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check worker PATH"""

import paramiko
import sys

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

SERVER_HOST = "5.129.235.52"
SERVER_USER = "root"
SERVER_PASSWORD = "cY7^kCCA_6uQ5S"
SERVER_PORT = 22

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASSWORD, timeout=10)

print("Checking PATH in worker container...")
stdin, stdout, stderr = ssh.exec_command('docker exec shannon_worker_1 sh -c "echo PATH=$PATH && which node && node --version"')
print(stdout.read().decode('utf-8', errors='replace'))

print("\nWorker is running. The PATH should include /usr/bin.")
print("If PATH is correct, try running a pentest now.")
print("\nIf it still fails, the library might need to be patched differently.")

ssh.close()

