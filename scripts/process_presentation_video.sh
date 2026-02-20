#!/bin/bash

# Video Processing Script for Presentations
# Extracts audio, generates transcripts, and captures screenshots
# Usage: ./process_presentation_video.sh <video_file> [screenshot_interval_seconds]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if video file is provided
if [ -z "$1" ]; then
    echo -e "${RED}Error: No video file specified${NC}"
    echo "Usage: $0 <video_file> [screenshot_interval_seconds]"
    echo "Example: $0 my_presentation.mp4 30"
    exit 1
fi

VIDEO_FILE="$1"
SCREENSHOT_INTERVAL="${2:-30}" # Default: 30 seconds

# Check if video file exists
if [ ! -f "$VIDEO_FILE" ]; then
    echo -e "${RED}Error: Video file '$VIDEO_FILE' not found${NC}"
    exit 1
fi

# Create output directory based on video filename
BASENAME=$(basename "$VIDEO_FILE" | sed 's/\.[^.]*$//')
OUTPUT_DIR="processed_${BASENAME}_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUTPUT_DIR"

echo -e "${GREEN}=== Video Processing Started ===${NC}"
echo "Video: $VIDEO_FILE"
echo "Output directory: $OUTPUT_DIR"
echo "Screenshot interval: ${SCREENSHOT_INTERVAL}s"
echo ""

# Step 1: Extract audio
echo -e "${YELLOW}[1/4] Extracting audio...${NC}"
AUDIO_FILE="$OUTPUT_DIR/${BASENAME}_audio.wav"
ffmpeg -i "$VIDEO_FILE" -vn -acodec pcm_s16le -ar 16000 -ac 1 "$AUDIO_FILE" -y 2>&1 | grep -i "duration\|error" || true
echo -e "${GREEN}✓ Audio extracted: $AUDIO_FILE${NC}"
echo ""

# Step 2: Generate transcript using Whisper
echo -e "${YELLOW}[2/4] Generating transcript with Whisper AI...${NC}"
echo "This may take a few minutes depending on video length..."

# Use dedicated venv for whisper (avoids system Python restrictions)
WHISPER_VENV="$HOME/.venvs/whisper"
WHISPER_PYTHON="$WHISPER_VENV/bin/python"

# Set up venv if not present
if [ ! -f "$WHISPER_PYTHON" ]; then
    echo -e "${YELLOW}Setting up Whisper virtual environment...${NC}"
    python3 -m venv "$WHISPER_VENV"
fi

# Install whisper into venv if not present
if ! "$WHISPER_PYTHON" -c "import whisper" 2>/dev/null; then
    echo -e "${YELLOW}Installing Whisper into venv (one-time setup)...${NC}"
    "$WHISPER_VENV/bin/pip" install openai-whisper
fi

"$WHISPER_PYTHON" << EOF
import whisper
import json
from datetime import timedelta

print("Loading Whisper model (base)...")
model = whisper.load_model("base")

print("Transcribing audio...")
result = model.transcribe("$AUDIO_FILE", verbose=False)

# Save full transcript
transcript_file = "$OUTPUT_DIR/${BASENAME}_transcript.txt"
with open(transcript_file, 'w', encoding='utf-8') as f:
    f.write(result['text'])

# Save timestamped transcript
timestamped_file = "$OUTPUT_DIR/${BASENAME}_transcript_timestamped.txt"
with open(timestamped_file, 'w', encoding='utf-8') as f:
    for segment in result['segments']:
        start = str(timedelta(seconds=int(segment['start'])))
        end = str(timedelta(seconds=int(segment['end'])))
        f.write(f"[{start} -> {end}] {segment['text']}\n")

# Save JSON format
json_file = "$OUTPUT_DIR/${BASENAME}_transcript.json"
with open(json_file, 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print(f"✓ Transcript saved: {transcript_file}")
print(f"✓ Timestamped transcript: {timestamped_file}")
print(f"✓ JSON data: {json_file}")
EOF

echo ""

# Step 3: Capture screenshots
echo -e "${YELLOW}[3/4] Capturing screenshots every ${SCREENSHOT_INTERVAL} seconds...${NC}"
SCREENSHOTS_DIR="$OUTPUT_DIR/screenshots"
mkdir -p "$SCREENSHOTS_DIR"

ffmpeg -i "$VIDEO_FILE" -vf "fps=1/${SCREENSHOT_INTERVAL}" "$SCREENSHOTS_DIR/screenshot_%04d.png" -y 2>&1 | grep -i "frame\|error" || true

SCREENSHOT_COUNT=$(ls -1 "$SCREENSHOTS_DIR"/*.png 2>/dev/null | wc -l)
echo -e "${GREEN}✓ Captured $SCREENSHOT_COUNT screenshots${NC}"
echo ""

# Step 4: Generate summary report
echo -e "${YELLOW}[4/4] Generating summary report...${NC}"

# Get video duration
DURATION=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$VIDEO_FILE" 2>/dev/null)
DURATION_MIN=$(echo "$DURATION / 60" | bc)

# Get video resolution
RESOLUTION=$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 "$VIDEO_FILE" 2>/dev/null)

cat > "$OUTPUT_DIR/SUMMARY.md" << SUMMARY
# Video Processing Summary

**Date:** $(date '+%Y-%m-%d %H:%M:%S')
**Video File:** $VIDEO_FILE
**Duration:** ${DURATION_MIN} minutes
**Resolution:** $RESOLUTION

## Output Files

### Audio
- \`${BASENAME}_audio.wav\` - Extracted audio (16kHz mono WAV)

### Transcripts
- \`${BASENAME}_transcript.txt\` - Plain text transcript
- \`${BASENAME}_transcript_timestamped.txt\` - Timestamped segments
- \`${BASENAME}_transcript.json\` - Full JSON with metadata

### Screenshots
- \`screenshots/\` - ${SCREENSHOT_COUNT} screenshots captured every ${SCREENSHOT_INTERVAL} seconds

## Next Steps

1. Review the transcript for accuracy
2. Edit timestamps if needed
3. Use screenshots for presentation slides or documentation
4. Archive or delete the audio file if not needed

---
Generated by video processing script
SUMMARY

echo -e "${GREEN}✓ Summary report: $OUTPUT_DIR/SUMMARY.md${NC}"
echo ""

# Final summary
echo -e "${GREEN}=== Processing Complete ===${NC}"
echo "All outputs saved to: $OUTPUT_DIR"
echo ""
echo "Files created:"
echo "  - Audio: ${BASENAME}_audio.wav"
echo "  - Transcript: ${BASENAME}_transcript.txt"
echo "  - Timestamped: ${BASENAME}_transcript_timestamped.txt"
echo "  - JSON data: ${BASENAME}_transcript.json"
echo "  - Screenshots: $SCREENSHOT_COUNT images in screenshots/"
echo "  - Summary: SUMMARY.md"
echo ""
echo -e "${YELLOW}Tip: Open $OUTPUT_DIR/SUMMARY.md for a complete overview${NC}"
