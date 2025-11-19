#!/bin/bash

# Check for credentials
if [ ! -f "credentials.json" ]; then
    echo "Error: credentials.json not found!"
    echo "Please place your Google Cloud credentials.json file in this directory."
    exit 1
fi

# Check for uv
if ! command -v uv &> /dev/null; then
    echo "Error: uv is not installed. Please install it: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Install dependencies if needed
echo "Syncing dependencies..."
uv pip install -r requirements.txt

# Run the agent
echo "Starting Google Drive Screenshot Agent..."
uv run main.py
