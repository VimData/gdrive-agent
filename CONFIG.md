# Configuration Guide

## Quick Start

### Enable Image Analysis (Default)
```bash
uv run main.py
```
or explicitly:
```bash
ANALYZE_IMAGES=1 uv run main.py
```

**Result**: Files are analyzed with AI, renamed with intelligent names (e.g., `dashboard.png`, `login_form.png`), then uploaded.

### Disable Image Analysis
```bash
ANALYZE_IMAGES=0 uv run main.py
```

**Result**: Files are uploaded with original names, no AI processing. Faster and no dependencies on Ollama or models.

---

## Environment Variables

### `ANALYZE_IMAGES` (Boolean)
- **Default**: `1` (enabled)
- **Accepted values**: `1`, `true`, `yes`, `0`, `false`, `no`
- **Effect**: Controls whether files are analyzed with vision models to generate intelligent filenames

**Scenarios:**
- Set to `0` if you don't have Ollama/models installed
- Set to `0` for faster processing (skips AI analysis)
- Set to `1` to get descriptive automatic naming

### `VISION_MODEL` (String)
- **Default**: `llava:7b`
- **Only used if**: `ANALYZE_IMAGES=1`
- **Other options**: 
  - `moondream:latest` - Smaller, faster model
  - `llava:latest` - Alternative LLaVA version
  - Any Ollama-compatible vision model

Example:
```bash
VISION_MODEL=moondream:latest ANALYZE_IMAGES=1 uv run main.py
```

### `OLLAMA_API_URL` (String)
- **Default**: `http://localhost:11434`
- **Effect**: URL where your Ollama server is running
- **Only used if**: `ANALYZE_IMAGES=1`

Example (remote server):
```bash
OLLAMA_API_URL=http://192.168.1.100:11434 uv run main.py
```

---

## System Requirements

### Required for all configurations:
- Python 3.8+
- Google Cloud credentials (`credentials.json`)
- Internet connection (for Google Drive API)

### Required only if `ANALYZE_IMAGES=1`:
- Ollama installed and running (`ollama serve`)
- Vision model downloaded (e.g., `ollama pull llava:7b`)
- ffmpeg (for video frame extraction): `brew install ffmpeg`

### Not required if `ANALYZE_IMAGES=0`:
- Ollama
- Vision models
- ffmpeg

---

## Usage Examples

### Minimal Setup (No AI)
```bash
# Just backup to Google Drive with original filenames
ANALYZE_IMAGES=0 uv run main.py
```

### Full Setup (With AI)
```bash
# Start Ollama with a vision model
ollama serve &
ollama pull llava:7b

# Run agent with analysis enabled
ANALYZE_IMAGES=1 uv run main.py
```

### Custom Vision Model
```bash
ANALYZE_IMAGES=1 VISION_MODEL=moondream:latest uv run main.py
```

### Remote Ollama Server
```bash
OLLAMA_API_URL=http://remote-host:11434 ANALYZE_IMAGES=1 uv run main.py
```

---

## Processing Flow

### With `ANALYZE_IMAGES=1` (Default)
```
Scan directory
    ↓
Find screenshots/videos (named "Screenshot" or "Screen-Capture")
    ↓
Extract keyframe (if video)
    ↓
Analyze with vision model
    ↓
Generate intelligent filename
    ↓
Rename local file
    ↓
Upload to Google Drive → 2025/11/images or 2025/11/videos
    ↓
Delete local file
    ↓
Report with suggested names
```

### With `ANALYZE_IMAGES=0`
```
Scan directory
    ↓
Find screenshots/videos (named "Screenshot" or "Screen-Capture")
    ↓
Upload to Google Drive → 2025/11/images or 2025/11/videos (original filename)
    ↓
Delete local file
    ↓
Report
```

## Google Drive Folder Structure

```
Google Drive Root
├── 2025/
│   ├── 11/
│   │   ├── images/
│   │   │   ├── screenshot_1.png
│   │   │   ├── dashboard.png
│   │   │   └── login_form.jpg
│   │   └── videos/
│   │       ├── screen_recording_1.mp4
│   │       └── tutorial.mov
│   └── 12/
│       ├── images/
│       └── videos/
```

---

## Performance Notes

- With analysis **disabled**: ~1-2 seconds per file (no AI overhead)
- With analysis **enabled**: ~5-15 seconds per file (depends on model)
- Video processing adds ~10-20 seconds for keyframe extraction
- First run may be slower due to model loading

