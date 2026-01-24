#!/usr/bin/env python3
"""
Deploy via HTTP API endpoint
Simple and reliable - no SSH needed!
"""

import requests
import sys
from pathlib import Path

def load_deploy_token():
    """Load deploy token from .env or use default"""
    env_path = Path(__file__).parent.parent / "backend" / ".env"
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                if line.startswith('DEPLOY_TOKEN='):
                    return line.split('=', 1)[1].strip()
    return None

def deploy():
    """Deploy via API"""
    api_url = "https://pentest.red/api/deploy"
    token = load_deploy_token()
    
    if not token:
        print("ERROR: DEPLOY_TOKEN not found in backend/.env")
        print("Add to backend/.env: DEPLOY_TOKEN=your-secret-token")
        return False
    
    print("=" * 60)
    print("DEPLOYING VIA API")
    print("=" * 60)
    print(f"API: {api_url}")
    print()
    
    try:
        response = requests.post(
            api_url,
            headers={
                'X-Deploy-Token': token,
                'Content-Type': 'application/json'
            },
            timeout=600  # 10 minutes
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Deployment successful!")
            print()
            
            for i, cmd_result in enumerate(result.get('results', []), 1):
                print(f"[{i}] {cmd_result.get('command', 'Unknown')}")
                print("-" * 60)
                if cmd_result.get('success'):
                    if cmd_result.get('stdout'):
                        print(cmd_result['stdout'])
                else:
                    print(f"❌ Error: {cmd_result.get('error', 'Unknown error')}")
                    if cmd_result.get('stderr'):
                        print(cmd_result['stderr'])
                print()
            
            return True
        elif response.status_code == 401:
            print("❌ ERROR: Invalid deploy token")
            print("Check DEPLOY_TOKEN in backend/.env")
            return False
        else:
            print(f"❌ ERROR: HTTP {response.status_code}")
            print(response.text)
            return False
            
    except requests.exceptions.Timeout:
        print("❌ ERROR: Request timed out")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    success = deploy()
    sys.exit(0 if success else 1)

