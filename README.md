# Google Drive Screenshot Agent

This is a standalone desktop agent that scans for screenshots and uploads them to Google Drive using the Model Context Protocol (MCP).

## Prerequisites

- Python 3.8+
- Google Cloud Project with Drive API enabled
- `credentials.json` file from Google Cloud Console

## Setup

1.  **Credentials**: Place your `credentials.json` file in the root directory of this project.
2.  **Dependencies**: This project uses `uv` for dependency management.
    ```bash
    # Install uv (if not already installed)
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # Create virtual environment and install dependencies
    uv venv
    uv pip install -r requirements.txt
    ```

## Running the Agent

You can run the agent using the provided script:

```bash
./run.sh
```

Or manually with uv:

```bash
uv run main.py
```

## Configuration

### Environment Variables

- `ANALYZE_IMAGES` (default: `1`)
  - Set to `1`, `true`, or `yes` to enable AI-powered analysis and intelligent filenames
  - Set to `0`, `false`, or `no` to disable analysis and use original filenames
  - Example: `ANALYZE_IMAGES=0 uv run main.py`

- `VISION_MODEL` (default: `llava:7b`)
  - Ollama vision model to use for analysis (only used if `ANALYZE_IMAGES=1`)
  - Example: `VISION_MODEL=moondream:latest uv run main.py`

- `OLLAMA_API_URL` (default: `http://localhost:11434`)
  - URL of your Ollama server

### File Configuration

- **Watch Directory**: By default, the agent watches the `~/Desktop` directory. You can modify `main.py` to change this.
- **File Types**: The agent detects:
  - Screenshots: `.png`, `.jpg`, `.jpeg` files with "Screenshot" in the name
  - Screen Recordings: `.mov`, `.mp4`, `.mkv`, `.avi`, `.webm` with "Screen" or "Recording" in the name

## Architecture

- **gdrive_server/**: Contains the MCP Server implementation and Google Drive API wrapper.
- **agent_client/**: Contains the MCP Client and Screenshot Scanner.
- **main.py**: Entry point that starts the client and server.
