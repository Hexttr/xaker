#!/usr/bin/env python3
"""
Check GitHub Actions status
"""

import requests
import json
import sys

def check_workflow_status():
    """Check latest workflow run status"""
    repo = "Hexttr/xaker"
    api_url = f"https://api.github.com/repos/{repo}/actions/runs"
    
    print("=" * 60)
    print("CHECKING GITHUB ACTIONS STATUS")
    print("=" * 60)
    print(f"Repository: {repo}")
    print()
    
    try:
        # Get latest workflow runs
        response = requests.get(
            api_url,
            params={"per_page": 5, "branch": "prod"},
            headers={"Accept": "application/vnd.github.v3+json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            runs = data.get("workflow_runs", [])
            
            if runs:
                latest = runs[0]
                print(f"Latest workflow: {latest.get('name', 'Unknown')}")
                print(f"Status: {latest.get('status', 'Unknown')}")
                print(f"Conclusion: {latest.get('conclusion', 'Unknown')}")
                print(f"Created: {latest.get('created_at', 'Unknown')}")
                print(f"URL: {latest.get('html_url', 'N/A')}")
                print()
                
                if latest.get('status') == 'completed':
                    if latest.get('conclusion') == 'success':
                        print("✅ Deployment successful!")
                    else:
                        print(f"❌ Deployment failed: {latest.get('conclusion')}")
                        print(f"Check logs: {latest.get('html_url')}")
                elif latest.get('status') == 'in_progress':
                    print("⏳ Deployment in progress...")
                    print(f"Watch live: {latest.get('html_url')}")
                else:
                    print(f"Status: {latest.get('status')}")
                    print(f"Check: {latest.get('html_url')}")
            else:
                print("No workflow runs found")
                print("Make sure GitHub Actions is enabled for the repository")
        else:
            print(f"API Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Error: {e}")
        print("\nYou can check manually:")
        print(f"https://github.com/{repo}/actions")

if __name__ == "__main__":
    check_workflow_status()

