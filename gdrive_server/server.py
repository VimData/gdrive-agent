from mcp.server.fastmcp import FastMCP
from .drive_api import DriveAPI
import os
import sys
import base64
import requests
import subprocess
import tempfile
from pathlib import Path

# Ollama configuration
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434")
VISION_MODEL = os.getenv("VISION_MODEL", "llava:7b")

# Initialize FastMCP server
mcp = FastMCP("Google Drive MCP Server")

# Initialize Drive API
try:
    drive = DriveAPI()
except Exception as e:
    sys.stderr.write(f"Failed to initialize Drive API: {e}\n")
    drive = None


def extract_video_frame(video_path: str) -> str:
    """
    Extracts the first keyframe from a video file.
    Returns path to temporary PNG file, or None if extraction fails.
    """
    try:
        # Create temporary file for frame
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp_path = tmp.name
        
        # Use ffmpeg to extract first frame
        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-vf", "select=eq(n\\,0)",
            "-q:v", "2",
            "-y",
            tmp_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, timeout=30)
        
        if result.returncode == 0 and os.path.exists(tmp_path):
            return tmp_path
        else:
            return None
    except Exception as e:
        sys.stderr.write(f"Error extracting video frame: {e}\n")
        return None


@mcp.tool()
def analyze_image(local_path: str) -> str:
    """
    Analyzes an image or video using Ollama vision model and suggests an appropriate filename.
    For videos, extracts the first keyframe for analysis.
    
    Args:
        local_path: Absolute path to the image or video file.
        
    Returns:
        A suggested filename for the file.
    """
    if not os.path.exists(local_path):
        return f"Error: File not found at {local_path}"
    
    try:
        import re
        
        path_obj = Path(local_path)
        ext = path_obj.suffix.lower()
        
        # Check if it's a video and extract frame if needed
        frame_path = None
        is_video = ext in ['.mov', '.mp4', '.mkv', '.avi', '.webm']
        
        if is_video:
            frame_path = extract_video_frame(local_path)
            if not frame_path:
                return f"error_video_frame_{path_obj.stem}{ext}"
            # Read the extracted frame
            with open(frame_path, "rb") as img_file:
                image_data = base64.standard_b64encode(img_file.read()).decode("utf-8")
        else:
            # Read image directly
            with open(local_path, "rb") as img_file:
                image_data = base64.standard_b64encode(img_file.read()).decode("utf-8")
        
        # Call Ollama vision model with explicit instruction for filename
        prompt = (
            "Analyze this screenshot and generate a short, descriptive filename (no extension). "
            "Requirements: 2-4 words, all lowercase, use underscores for spaces only, "
            "alphanumeric and underscore only [a-z0-9_]. "
            "Examples: login_screen, payment_form, error_message, dashboard_view. "
            "Return ONLY the filename, nothing else."
        )
        
        payload = {
            "model": VISION_MODEL,
            "prompt": prompt,
            "images": [image_data],
            "stream": False,
            "temperature": 0.3,
        }
        
        response = requests.post(
            f"{OLLAMA_API_URL}/api/generate",
            json=payload,
            timeout=120
        )
        
        if response.status_code != 200:
            return f"Error: Ollama API returned {response.status_code}"
        
        result = response.json()
        suggested_name = result.get("response", "").strip()
        
        if not suggested_name:
            suggested_name = f"screenshot_{path_obj.stem[:20]}"
        
        # Aggressive sanitization
        suggested_name = suggested_name.lower()
        # Keep only a-z, 0-9, space, underscore, hyphen
        suggested_name = re.sub(r"[^a-z0-9_\-\s]", "", suggested_name)
        # Replace hyphens and spaces with underscores
        suggested_name = suggested_name.replace("-", "_").replace(" ", "_")
        # Collapse multiple underscores
        suggested_name = re.sub(r"_+", "_", suggested_name).strip("_")
        # Remove file extension if somehow included
        if "." in suggested_name:
            suggested_name = suggested_name.rsplit(".", 1)[0]
        
        # Final fallback
        if not suggested_name or len(suggested_name) < 2:
            suggested_name = f"screenshot_{path_obj.stem[:15]}"
        
        result = f"{suggested_name}{ext}"
        
        # Cleanup temporary frame file if it was created
        if frame_path and os.path.exists(frame_path):
            try:
                os.remove(frame_path)
            except:
                pass
        
        return result
        
    except requests.exceptions.ConnectionError:
        if frame_path and os.path.exists(frame_path):
            try:
                os.remove(frame_path)
            except:
                pass
        return f"Error: Cannot connect to Ollama at {OLLAMA_API_URL}. Make sure Ollama is running with 'ollama serve'."
    except requests.exceptions.Timeout:
        if frame_path and os.path.exists(frame_path):
            try:
                os.remove(frame_path)
            except:
                pass
        return "Error: Ollama request timed out."
    except Exception as e:
        if frame_path and os.path.exists(frame_path):
            try:
                os.remove(frame_path)
            except:
                pass
        return f"Error analyzing image: {str(e)}"


@mcp.tool()
def upload_file(local_path: str, folder_id: str) -> str:
    """
    Uploads a file to Google Drive.
    
    Args:
        local_path: Absolute path to the local file.
        folder_id: ID of the folder in Google Drive to upload to.
        
    Returns:
        The ID of the uploaded file.
    """
    if not drive:
        return "Error: Drive API not initialized."
    
    if not os.path.exists(local_path):
        return f"Error: File not found at {local_path}"
        
    try:
        file_id = drive.upload_file(local_path, folder_id)
        return f"Successfully uploaded file. File ID: {file_id}"
    except Exception as e:
        return f"Error uploading file: {str(e)}"


@mcp.tool()
def ensure_folder_structure(year: int, month: int, media_type: str = "images") -> str:
    """
    Ensures the /media_type/year/month folder structure exists in Google Drive.
    
    Args:
        year: The year (e.g., 2024).
        month: The month (e.g., 11).
        media_type: Type of media - 'images' or 'videos' (default: 'images').
        
    Returns:
        The ID of the month folder.
    """
    if not drive:
        return "Error: Drive API not initialized."
        
    try:
        folder_id = drive.ensure_folder_structure(year, month, media_type)
        return folder_id
    except Exception as e:
        return f"Error ensuring folder structure: {str(e)}"


if __name__ == "__main__":
    mcp.run()
