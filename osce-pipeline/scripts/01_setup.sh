#!/bin/bash
# PRD_OSCE_001: Setup — Install yt-dlp and verify dependencies
set -euo pipefail

echo "=== OSCE Pipeline Setup ==="

# 1. Install yt-dlp
if ! command -v yt-dlp &>/dev/null; then
    echo "Installing yt-dlp..."
    if command -v pipx &>/dev/null; then
        pipx install yt-dlp
    else
        pip3 install --user yt-dlp
    fi
else
    echo "yt-dlp already installed: $(yt-dlp --version)"
fi

# 2. Verify ffmpeg
if ! command -v ffmpeg &>/dev/null; then
    echo "ERROR: ffmpeg not found. Install with: sudo apt install ffmpeg"
    exit 1
fi
echo "ffmpeg: $(ffmpeg -version 2>&1 | head -1)"

# 3. Verify jq
if ! command -v jq &>/dev/null; then
    echo "Installing jq..."
    sudo apt-get install -y jq
fi
echo "jq: $(jq --version)"

# 4. Verify Whisper venv
WHISPER_VENV="$HOME/.venvs/whisper"
if [ ! -f "$WHISPER_VENV/bin/python" ]; then
    echo "Creating Whisper venv..."
    python3 -m venv "$WHISPER_VENV"
fi
if ! "$WHISPER_VENV/bin/python" -c "import whisper" 2>/dev/null; then
    echo "Installing openai-whisper..."
    "$WHISPER_VENV/bin/pip" install openai-whisper
fi
echo "Whisper venv: OK"

# 5. Verify MSDev venv
MSDEV_VENV="/home/dev/Development/MSDev/Archive/docs/ai-agents/diagrams/venv"
if [ ! -f "$MSDEV_VENV/bin/python" ]; then
    echo "ERROR: MSDev venv not found at $MSDEV_VENV"
    exit 1
fi
"$MSDEV_VENV/bin/python" -c "import matplotlib, graphviz, seaborn" && echo "MSDev venv: OK"

echo ""
echo "=== Setup complete ==="
