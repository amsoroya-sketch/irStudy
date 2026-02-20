#!/bin/bash
# PRD_OSCE_002: Extract audio + transcribe with Whisper
# Usage: ./03_transcribe.sh <SLUG>
set -uo pipefail

SLUG="$1"
PIPELINE_DIR="/home/dev/Development/irStudy/osce-pipeline"
OUTPUT_DIR="$PIPELINE_DIR/output/$SLUG"
WHISPER_PYTHON="$HOME/.venvs/whisper/bin/python"

# Find video file
VIDEO_FILE=$(ls "$OUTPUT_DIR"/video.* 2>/dev/null | grep -v "\.json$" | head -1)
if [ -z "$VIDEO_FILE" ]; then
    echo "ERROR: No video file found in $OUTPUT_DIR"
    exit 1
fi

echo "Video: $VIDEO_FILE"

# Extract audio (16kHz mono WAV for Whisper)
AUDIO_FILE="$OUTPUT_DIR/audio.wav"
echo "Extracting audio..."
ffmpeg -i "$VIDEO_FILE" -ar 16000 -ac 1 -c:a pcm_s16le "$AUDIO_FILE" -y -loglevel error
echo "Audio extracted: $AUDIO_FILE"

echo "Transcribing with Whisper (base model)..."

# Run Whisper — pass SLUG as env var, use - to read from stdin to avoid heredoc quoting issues
OSCE_SLUG="$SLUG" OSCE_BASE="$OUTPUT_DIR" "$WHISPER_PYTHON" - << 'PYEOF'
import whisper, json, os
from datetime import timedelta
from pathlib import Path

BASE = Path(os.environ["OSCE_BASE"])
AUDIO = BASE / "audio.wav"

if not AUDIO.exists():
    raise FileNotFoundError(f"audio.wav not found at {AUDIO}")

print("Loading Whisper base model...")
model = whisper.load_model("base")
print("Transcribing...")
result = model.transcribe(str(AUDIO), verbose=False)

# Plain transcript
(BASE / "transcript.txt").write_text(result["text"].strip(), encoding="utf-8")

# Timestamped transcript
lines = []
for seg in result["segments"]:
    ts = str(timedelta(seconds=int(seg["start"])))
    lines.append(f"[{ts}] {seg['text'].strip()}")
(BASE / "timestamped.txt").write_text("\n".join(lines), encoding="utf-8")

# Full JSON
result_clean = {k: v for k, v in result.items() if k != "audio"}
(BASE / "transcript.json").write_text(json.dumps(result_clean, indent=2), encoding="utf-8")

print(f"Transcript: {len(result['text'].split())} words")
PYEOF

# Write status
cat > "$OUTPUT_DIR/status.json" << EOF
{
  "step": "transcribed",
  "slug": "$SLUG",
  "updated_at": "$(date -Iseconds)"
}
EOF

echo "Transcription complete: $SLUG"
