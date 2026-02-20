#!/bin/bash

# Screen Recording Script for YouTube Videos
# Records screen and system audio (what you hear from YouTube)
# Usage: ./record_screen.sh [output_filename] [audio_source]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default settings
OUTPUT_DIR="$HOME/Videos/recordings"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DEFAULT_FILENAME="screen_recording_${TIMESTAMP}.mp4"
OUTPUT_FILE="${1:-$DEFAULT_FILENAME}"

# Add .mp4 extension if not present
if [[ ! "$OUTPUT_FILE" =~ \.mp4$ ]]; then
    OUTPUT_FILE="${OUTPUT_FILE}.mp4"
fi

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"
FULL_PATH="$OUTPUT_DIR/$OUTPUT_FILE"

echo -e "${BLUE}=== Screen Recording Tool ===${NC}"
echo ""

# Check if ffmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo -e "${RED}Error: ffmpeg is not installed${NC}"
    echo "Install with: sudo apt install ffmpeg"
    exit 1
fi

# Detect display
DISPLAY_NUM="${DISPLAY:-:0}"
echo -e "${GREEN}Display:${NC} $DISPLAY_NUM"

# Get screen resolution
SCREEN_SIZE=$(xdpyinfo | grep dimensions | awk '{print $2}')
echo -e "${GREEN}Resolution:${NC} $SCREEN_SIZE"

# Detect audio sources
echo ""
echo -e "${YELLOW}Detecting audio sources...${NC}"
echo ""

# List available PulseAudio sources
if command -v pactl &> /dev/null; then
    echo "Available audio sources:"
    pactl list sources short | nl
    echo ""

    # Try to auto-detect monitor (system audio output)
    MONITOR_SOURCE=$(pactl list sources short | grep -i "monitor" | head -1 | awk '{print $2}')

    if [ -z "$MONITOR_SOURCE" ]; then
        # Fallback to first available source
        MONITOR_SOURCE=$(pactl list sources short | head -1 | awk '{print $2}')
    fi

    AUDIO_SOURCE="${2:-$MONITOR_SOURCE}"
    echo -e "${GREEN}Using audio source:${NC} $AUDIO_SOURCE"
    echo -e "${YELLOW}Tip: If audio doesn't work, run this script again with a different source number${NC}"
    echo -e "${YELLOW}Example: ./record_screen.sh my_video.mp4 source_name${NC}"
else
    echo -e "${YELLOW}Warning: PulseAudio not detected. Recording without audio.${NC}"
    AUDIO_SOURCE=""
fi

echo ""
echo -e "${BLUE}Recording will be saved to:${NC}"
echo "$FULL_PATH"
echo ""
echo -e "${GREEN}=== INSTRUCTIONS ===${NC}"
echo "1. Press ENTER to start recording"
echo "2. Switch to your YouTube video and play it"
echo "3. Press Ctrl+C in this terminal when done recording"
echo ""
read -p "Press ENTER to start recording..."

echo ""
echo -e "${RED}● RECORDING STARTED${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
echo ""

# Build ffmpeg command
FFMPEG_CMD="ffmpeg -video_size $SCREEN_SIZE -framerate 30 -f x11grab -i $DISPLAY_NUM"

# Add audio if available
if [ -n "$AUDIO_SOURCE" ]; then
    FFMPEG_CMD="$FFMPEG_CMD -f pulse -i $AUDIO_SOURCE"
fi

# Output settings
FFMPEG_CMD="$FFMPEG_CMD -c:v libx264 -preset ultrafast -crf 23"

if [ -n "$AUDIO_SOURCE" ]; then
    FFMPEG_CMD="$FFMPEG_CMD -c:a aac -b:a 192k"
fi

FFMPEG_CMD="$FFMPEG_CMD \"$FULL_PATH\""

# Trap Ctrl+C to stop recording gracefully
trap ctrl_c INT

function ctrl_c() {
    echo ""
    echo -e "${GREEN}■ Recording stopped${NC}"
    echo ""
    echo -e "${BLUE}Processing video...${NC}"
}

# Execute recording
eval $FFMPEG_CMD

echo ""
echo -e "${GREEN}=== Recording Complete ===${NC}"
echo ""
echo "Video saved: $FULL_PATH"

# Get file size
FILE_SIZE=$(du -h "$FULL_PATH" | cut -f1)
echo "File size: $FILE_SIZE"

# Get duration
DURATION=$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$FULL_PATH" 2>/dev/null)
DURATION_MIN=$(echo "scale=2; $DURATION / 60" | bc 2>/dev/null || echo "N/A")
echo "Duration: ${DURATION_MIN} minutes"

echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Review the recording: vlc '$FULL_PATH'"
echo "2. Process with video script: ./scripts/process_presentation_video.sh '$FULL_PATH'"
echo ""
