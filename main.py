import asyncio
import os
import sys
from agent_client.client import AgentClient

def main():
    print("Starting Google Drive Screenshot Agent...")
    
    # Configuration flag: Enable/disable AI image analysis for naming
    # Set ANALYZE_IMAGES=0 or ANALYZE_IMAGES=false to disable
    analyze_images = os.getenv("ANALYZE_IMAGES", "1").lower() not in ["0", "false", "no"]
    if analyze_images:
        print("[Config] Image analysis: ENABLED")
    else:
        print("[Config] Image analysis: DISABLED")
    
    # Check for credentials
    if not os.path.exists('credentials.json'):
        print("Error: credentials.json not found. Please place it in the application directory.")
        print("You can download it from the Google Cloud Console.")
        return

    # Determine watch directory (default to Desktop)
    watch_dir = os.path.expanduser("~/Desktop")
    # Use test directory instead due to Desktop permission restrictions
    watch_dir = os.path.join(os.path.dirname(__file__), "test_screenshots")
    
    # Initialize and run client
    client = AgentClient(watch_dir, analyze_images=analyze_images)
    
    try:
        asyncio.run(client.run())
    except KeyboardInterrupt:
        print("\nStopping agent...")
    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()
