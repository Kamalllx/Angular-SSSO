"""
Google Calendar Setup Helper
"""

import os
import json
from pathlib import Path

def setup_google_calendar():
    """Setup Google Calendar API step by step"""
    
    print("🗓️  Google Calendar API Setup")
    print("="*40)
    
    print("Step 1: Check for credentials file...")
    cred_file = "creds.json"
    
    if os.path.exists(cred_file):
        print(f"✅ Found {cred_file}")
        
        # Validate JSON
        try:
            with open(cred_file, 'r') as f:
                cred_data = json.load(f)
            
            if "installed" in cred_data or "web" in cred_data:
                print("✅ Credentials file appears valid")
            else:
                print("❌ Credentials file format incorrect")
                print("   Make sure to download OAuth 2.0 credentials (not service account)")
                return False
                
        except json.JSONDecodeError:
            print("❌ Credentials file is not valid JSON")
            return False
    else:
        print(f"❌ {cred_file} not found")
        print("\n📋 To set up Google Calendar API:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a new project or select existing")
        print("3. Enable Google Calendar API")
        print("4. Create OAuth 2.0 credentials (Desktop Application)")
        print("5. Download JSON file and rename to 'creds.json'")
        print("6. Place creds.json in the backend folder")
        return False
    
    print("\nStep 2: Check required packages...")

    # Mapping of pip package names to import names
    required_packages = {
        "google-api-python-client": "googleapiclient",
        "google-auth-httplib2": "google_auth_httplib2",
        "google-auth-oauthlib": "google_auth_oauthlib"
    }

    missing_packages = []
    for pip_name, import_name in required_packages.items():
        try:
            __import__(import_name)
            print(f"✅ {pip_name} installed")
        except ImportError:
            print(f"❌ {pip_name} missing")
            missing_packages.append(pip_name)

    if missing_packages:
        print(f"\n📦 Install missing packages:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    print("\n✅ Google Calendar API setup complete!")
    print("🔄 Restart the backend to use Google Calendar integration")
    return True

if __name__ == "__main__":
    setup_google_calendar()
