import os
import asyncio
import time
import datetime
import shutil
import subprocess
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from .scanner import Scanner

class AgentClient:
    def __init__(self, watch_directory, analyze_images=True):
        self.scanner = Scanner(watch_directory)
        self.analyze_images = analyze_images
        # We will start the server as a module
        # self.server_script = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'gdrive_server', 'server.py')
    
    def _print_report(self, report):
        """Print a formatted report of the processing results."""
        print("\n" + "="*60)
        print("PROCESSING REPORT")
        print("="*60)
        print(f"Total files found: {report['total_files_found']}")
        print(f"Files processed: {report['processed']}")
        print(f"Successful: {report['successful']}")
        print(f"Failed: {report['failed']}")
        
        if report['files']:
            print("\nDetails:")
            for i, file_info in enumerate(report['files'], 1):
                print(f"\n  {i}. {file_info['original_name']}")
                print(f"     Type: {file_info.get('type', 'unknown')}")
                if 'suggested_name' in file_info:
                    print(f"     → Renamed to: {file_info['suggested_name']}")
                print(f"     Status: {file_info['status']}")
                if 'error' in file_info:
                    print(f"     Error: {file_info['error']}")
        
        print("\n" + "="*60 + "\n")
        
    async def run(self):
        # Define server parameters
        python_exe = sys.executable
        
        server_params = StdioServerParameters(
            command=python_exe,
            args=["-m", "gdrive_server.server"],
            env=os.environ.copy()
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                print("Connected to MCP Server.")
                print("Scanning for screenshots...")
                
                files = self.scanner.scan()
                report = {
                    "total_files_found": len(files),
                    "processed": 0,
                    "successful": 0,
                    "failed": 0,
                    "files": []
                }
                
                if not files:
                    print("\nNo screenshots or recordings found.")
                else:
                    print(f"\nFound {len(files)} file(s). Processing...\n")
                    
                    for filepath, file_type in files:
                        filename = os.path.basename(filepath)
                        file_report = {"original_name": filename, "type": file_type, "status": "failed"}
                        
                        try:
                            # Analyze image/video and get suggested name (if enabled)
                            if self.analyze_images:
                                print(f"Analyzing {filename} ({file_type})...")
                                analysis_result = await session.call_tool("analyze_image", arguments={"local_path": filepath})
                                suggested_name = analysis_result.content[0].text.strip()
                                print(f"  → Suggested name: {suggested_name}")
                                file_report["suggested_name"] = suggested_name
                                
                                # Rename file with suggested name
                                dir_path = os.path.dirname(filepath)
                                new_filepath = os.path.join(dir_path, suggested_name)
                                
                                if new_filepath != filepath:
                                    try:
                                        os.rename(filepath, new_filepath)
                                        print(f"  ✓ Renamed")
                                        filepath = new_filepath
                                    except OSError as e:
                                        print(f"  ⚠ Warning: Could not rename: {e}")
                            else:
                                print(f"Processing {filename} ({file_type})...")
                            
                            # Extract date from file metadata
                            timestamp = os.path.getmtime(filepath)
                            dt = datetime.datetime.fromtimestamp(timestamp)
                            year = dt.year
                            month = dt.month
                            
                            # Ensure folder structure (Images or Videos)
                            media_type = "videos" if file_type == "video" else "images"
                            result = await session.call_tool("ensure_folder_structure", arguments={"year": year, "month": month, "media_type": media_type})
                            folder_id = result.content[0].text
                            
                            if "Error" in folder_id:
                                print(f"  ✗ Failed to create folder structure: {folder_id}")
                                file_report["error"] = folder_id
                                report["failed"] += 1
                                continue
                            
                            print(f"  → Uploading to Google Drive ({year}/{month})...")
                            upload_result = await session.call_tool("upload_file", arguments={"local_path": filepath, "folder_id": folder_id})
                            upload_text = upload_result.content[0].text
                            print(f"  → {upload_text}")
                            
                            if "Successfully" in upload_text:
                                self.scanner.mark_processed(filepath)
                                try:
                                    os.remove(filepath)
                                    print(f"  ✓ Deleted local file")
                                    file_report["status"] = "success"
                                    report["successful"] += 1
                                except OSError as e:
                                    print(f"  ⚠ Could not delete: {e}")
                                    file_report["status"] = "uploaded_but_not_deleted"
                                    report["successful"] += 1
                            else:
                                print(f"  ✗ Upload failed")
                                file_report["error"] = upload_text
                                report["failed"] += 1
                        
                        except Exception as e:
                            print(f"  ✗ Error: {str(e)}")
                            file_report["error"] = str(e)
                            report["failed"] += 1
                        
                        report["files"].append(file_report)
                        report["processed"] += 1
                        print()
                
                # Generate and print final report
                self._print_report(report)

if __name__ == "__main__":
    import asyncio
    # Default to Desktop for now
    watch_dir = os.path.expanduser("~/Desktop")
    client = AgentClient(watch_dir)
    asyncio.run(client.run())
