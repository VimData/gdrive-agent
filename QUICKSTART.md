# 🚀 Quick Start - 5 Minutes

## Step 1: Clone & Check
```bash
git clone https://github.com/VimData/gdrive-agent.git
cd gdrive-agent

# Run health check
python3 doctor.py
```

## Step 2: Install Dependencies
```bash
# Create virtual environment
uv venv

# Install packages
uv pip install -r requirements.txt
```

## Step 3: Setup Credentials
**Option A (Easy - if you downloaded credentials.json):**
```bash
# Put credentials.json in your Downloads folder, then:
python3 setup_credentials.py
```

**Option B (Manual):**
1. Go to https://console.cloud.google.com
2. Create OAuth 2.0 credentials (Desktop app)
3. Download JSON file
4. Save as `credentials.json` in project root

## Step 4: Run!
```bash
# Without AI (fast, lightweight)
ANALYZE_IMAGES=0 uv run main.py

# With AI (smart naming)
ANALYZE_IMAGES=1 uv run main.py
```

---

## What It Does

1. **Scans** for "screenshot" or "screen-capture" files
2. **Analyzes** with Ollama (optional AI naming)
3. **Organizes** on Google Drive: `2025/11/images`, `2025/11/videos`
4. **Uploads** all files
5. **Cleans up** local copies

---

## Commands Cheat Sheet

| Task | Command |
|------|---------|
| Check everything | `python3 doctor.py` |
| Copy credentials | `python3 setup_credentials.py` |
| Run without AI | `ANALYZE_IMAGES=0 uv run main.py` |
| Run with AI | `ANALYZE_IMAGES=1 uv run main.py` |
| Install ffmpeg | `brew install ffmpeg` |
| Start Ollama | `ollama serve` |
| Pull vision model | `ollama pull llava:7b` |

---

## Common Issues

| Issue | Fix |
|-------|-----|
| FFmpeg not found | `brew install ffmpeg` |
| Ollama not responding | `ollama serve` (in another terminal) |
| Credentials missing | `python3 setup_credentials.py` |
| Python packages missing | `uv pip install -r requirements.txt` |

---

## Requires

- Python 3.8+
- Google Drive API credentials
- (Optional) FFmpeg for video processing
- (Optional) Ollama for AI naming

---

## Helpful Files

- **README.md** - Full project documentation
- **CONFIG.md** - All configuration options
- **SETUP.md** - Detailed setup guide
- **doctor.py** - Dependency checker
- **setup_credentials.py** - Credentials helper

---

**Questions?** Check the docs or run `python3 doctor.py`!
