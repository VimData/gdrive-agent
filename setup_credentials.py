#!/usr/bin/env python3
"""
Helper script to copy Google credentials from Downloads folder.
"""

import shutil
from pathlib import Path

def copy_credentials():
    """Copy credentials.json from Downloads to project root."""
    downloads = Path.home() / "Downloads"
    source = downloads / "credentials.json"
    dest = Path.cwd() / "credentials.json"
    
    print(f"Looking for credentials.json in: {downloads}")
    
    if source.exists():
        print(f"✓ Found: {source.name}")
        print(f"Copying to: {dest}")
        shutil.copy2(source, dest)
        print(f"✓ Successfully copied credentials.json")
        print(f"\nYou can now run the agent:")
        print(f"  ANALYZE_IMAGES=0 uv run main.py")
        print(f"  or")
        print(f"  ANALYZE_IMAGES=1 uv run main.py")
    else:
        print(f"✗ credentials.json not found in Downloads")
        print(f"\nTo set up credentials:")
        print(f"1. Go to https://console.cloud.google.com")
        print(f"2. Create OAuth 2.0 credentials (Desktop app)")
        print(f"3. Download the JSON file")
        print(f"4. Rename it to 'credentials.json'")
        print(f"5. Save it to your Downloads folder")
        print(f"6. Run this script again: python3 setup_credentials.py")

if __name__ == "__main__":
    copy_credentials()
