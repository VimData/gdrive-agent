# Setup Guide for gdrive-agent

## Quick Start (2 minutes)

### 1. Health Check
```bash
# First, check if your system has everything needed
python3 doctor.py
```

The doctor script will check:
- ✅ Python version (3.8+)
- ✅ UV package manager
- ✅ ffmpeg (for video processing)
- ✅ Ollama (optional, for AI naming)
- ✅ Google Drive credentials
- ✅ Project structure

### 2. Install Dependencies
```bash
# Create virtual environment
uv venv

# Activate it
source .venv/bin/activate

# Install requirements
uv pip install -r requirements.txt
```

### 3. Setup Google Drive Authentication
```bash
# Run the auth setup
python3 setup_auth.py
```

Or manually:
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project
3. Enable "Google Drive API"
4. Create OAuth 2.0 credentials (Desktop app)
5. Download the JSON file
6. Save it as `credentials.json` in the project root

### 4. Run the Agent
```bash
# Without AI analysis (lightweight)
ANALYZE_IMAGES=0 uv run main.py

# With AI analysis (intelligent naming)
ANALYZE_IMAGES=1 uv run main.py
```

## System Requirements

### Must Have
- **Python 3.8+** - Runtime
- **UV** - Dependency manager
- **Google Drive API credentials** - For authentication

### Optional (depends on features)
- **ffmpeg** - For video frame extraction
  - macOS: `brew install ffmpeg`
  - Ubuntu: `sudo apt-get install ffmpeg`
- **Ollama** - For AI-powered image analysis
  - [Download](https://ollama.ai)
  - Run: `ollama serve`

## Troubleshooting with Doctor

### Issue: "FFmpeg not found"
```bash
# Install FFmpeg
brew install ffmpeg

# Or disable video analysis
ANALYZE_IMAGES=0 uv run main.py
```

### Issue: "Ollama not running"
```bash
# Start Ollama server
ollama serve

# Or run without AI analysis
ANALYZE_IMAGES=0 uv run main.py
```

### Issue: "Python packages missing"
```bash
# Activate virtual environment
source .venv/bin/activate

# Reinstall dependencies
uv pip install -r requirements.txt
```

### Issue: "credentials.json not found"
```bash
# Run the auth setup
python3 setup_auth.py

# Or manually download from Google Cloud Console
# and place in the project root as credentials.json
```

## Features Overview

| Feature | ANALYZE_IMAGES=1 | ANALYZE_IMAGES=0 |
|---------|------------------|------------------|
| Process screenshots | ✅ | ✅ |
| Process videos | ✅ | ✅ |
| Extract video frames | ✅ | ❌ |
| AI naming suggestions | ✅ | ❌ |
| Auto-organize by type | ✅ | ✅ |
| Speed | Slower (5-15s/file) | Fast (1-2s/file) |
| Requires Ollama | ✅ | ❌ |
| Requires ffmpeg | ✅ | ❌ |

## Folder Organization

Files are organized on Google Drive as:
```
2025/
├── 11/
│   ├── images/
│   │   ├── screenshot_1.png
│   │   └── dashboard.png
│   └── videos/
│       ├── recording_1.mp4
│       └── tutorial.mov
└── 12/
    ├── images/
    └── videos/
```

## File Detection Rules

The agent only processes files that are explicitly named:
- **Screenshots**: Contains "screenshot" or "screen shot"
- **Screen Recordings**: Contains "screen-capture" or "screen_capture"

**Supported formats:**
- Images: `.png`, `.jpg`, `.jpeg`
- Videos: `.mov`, `.mp4`, `.mkv`, `.avi`, `.webm`

## Configuration Variables

```bash
# Enable/disable AI analysis (default: 1)
ANALYZE_IMAGES=0  # Disable AI
ANALYZE_IMAGES=1  # Enable AI

# Specify vision model (default: llava:7b)
VISION_MODEL=moondream:latest

# Specify Ollama server (default: localhost:11434)
OLLAMA_API_URL=http://remote-host:11434
```

## Common Commands

```bash
# Check if everything is ready
python3 doctor.py

# Run without AI (lightweight)
ANALYZE_IMAGES=0 uv run main.py

# Run with AI analysis
ANALYZE_IMAGES=1 uv run main.py

# Pull a different vision model
ollama pull moondream:latest

# View available Ollama models
ollama list

# Start Ollama server
ollama serve
```

## What Happens When You Run It

1. **Scan**: Looks for files named "screenshot" or "screen-capture"
2. **Analyze** (if enabled): Extracts keyframe from videos, analyzes with AI
3. **Organize**: Creates `YEAR/MONTH/TYPE` folders on Google Drive
4. **Upload**: Uploads renamed files to appropriate folder
5. **Cleanup**: Deletes local files after successful upload
6. **Report**: Prints detailed summary of what was processed

## Need Help?

1. Run `python3 doctor.py` first - it will tell you what's missing
2. Check `CONFIG.md` for detailed configuration options
3. Read `README.md` for project overview
4. Check GitHub issues: https://github.com/VimData/gdrive-agent/issues
