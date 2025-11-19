import os
import time
from datetime import datetime

class Scanner:
    def __init__(self, watch_directory):
        self.watch_directory = watch_directory
        self.processed_files = set()

    def scan(self):
        """
        Scans the directory for screenshots and screen recordings.
        Only processes files explicitly named 'screenshot' or 'screen-capture' (case-insensitive).
        Returns a list of (filepath, file_type) tuples where file_type is 'image' or 'video'.
        """
        found_files = []
        if not os.path.exists(self.watch_directory):
            print(f"Warning: Directory {self.watch_directory} does not exist.")
            return found_files

        for filename in os.listdir(self.watch_directory):
            filepath = os.path.join(self.watch_directory, filename)
            
            # Skip directories and already processed files
            if os.path.isdir(filepath) or filepath in self.processed_files:
                continue
            
            lower_name = filename.lower()
            file_type = None
            
            # Check if filename contains 'screenshot' or 'screen-capture' (case-insensitive)
            is_screenshot = 'screenshot' in lower_name or 'screen shot' in lower_name
            is_screen_capture = 'screen-capture' in lower_name or 'screen_capture' in lower_name
            
            if not (is_screenshot or is_screen_capture):
                continue
            
            # Check for image extensions
            if lower_name.endswith(('.png', '.jpg', '.jpeg')):
                file_type = 'image'
            # Check for video extensions (screen recordings)
            elif lower_name.endswith(('.mov', '.mp4', '.mkv', '.avi', '.webm')):
                file_type = 'video'
            
            if file_type:
                found_files.append((filepath, file_type))
        
        return found_files

    def mark_processed(self, filepath):
        self.processed_files.add(filepath)

if __name__ == "__main__":
    # Test scanner
    scanner = Scanner(os.path.expanduser("~/Desktop"))
    print(f"Scanning {scanner.watch_directory}...")
    files = scanner.scan()
    print(f"Found {len(files)} screenshots.")
    for f in files:
        print(f)
