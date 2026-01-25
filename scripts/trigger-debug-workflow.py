#!/usr/bin/env python3
"""
Trigger debug workflow manually via GitHub API
Requires GITHUB_TOKEN in environment or .env
"""

import requests
import os
import sys
from pathlib import Path

def trigger_workflow():
    """Trigger debug workflow"""
    repo = "Hexttr/xaker"
    workflow_id = "deploy-debug.yml"
    
    # Try to get token from environment
    token = os.getenv('GITHUB_TOKEN')
    
    if not token:
        print("ERROR: GITHUB_TOKEN not found")
        print("Set it in environment or create .env file with GITHUB_TOKEN=your_token")
        print("\nTo get token:")
        print("1. Go to https://github.com/settings/tokens")
        print("2. Generate new token with 'workflow' scope")
        print("3. Set: export GITHUB_TOKEN=your_token")
        return False
    
    api_url = f"https://api.github.com/repos/{repo}/actions/workflows/{workflow_id}/dispatches"
    
    print("=" * 60)
    print("TRIGGERING DEBUG WORKFLOW")
    print("=" * 60)
    print(f"Repository: {repo}")
    print(f"Workflow: {workflow_id}")
    print()
    
    try:
        response = requests.post(
            api_url,
            headers={
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json"
            },
            json={
                "ref": "prod"
            },
            timeout=10
        )
        
        if response.status_code == 204:
            print("✅ Debug workflow triggered successfully!")
            print(f"Check status: https://github.com/{repo}/actions")
            return True
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = trigger_workflow()
    sys.exit(0 if success else 1)

