#!/bin/bash

# YouTube Screen Recording Script
# Records a browser window or full screen with system audio
# Usage: ./record_youtube.sh [output_filename]

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

OUTPUT_DIR="$HOME/Videos/recordings"
mkdir -p "$OUTPUT_DIR"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_FILE="${1:-youtube_recording_${TIMESTAMP}}"
[[ "$OUTPUT_FILE" =~ \.mp4$ ]] || OUTPUT_FILE="${OUTPUT_FILE}.mp4"
FULL_PATH="$OUTPUT_DIR/$OUTPUT_FILE"

echo -e "${CYAN}"
echo "╔════════════════════════════════════════════════╗"
echo "║      YouTube Video Screen Recorder             ║"
echo "╚════════════════════════════════════════════════╝"
echo -e "${NC}"

# ── Dependency check ────────────────────────────────────────────────────────
for cmd in ffmpeg xdotool xwininfo; do
    if ! command -v "$cmd" &>/dev/null; then
        echo -e "${RED}Error: $cmd not installed.${NC}"
        echo "Run: ./scripts/install_recording_tools.sh"
        exit 1
    fi
done

# ── Audio source ─────────────────────────────────────────────────────────────
AUDIO_SOURCE=$(pactl list sources short 2>/dev/null | grep -i monitor | head -1 | awk '{print $2}')
if [ -z "$AUDIO_SOURCE" ]; then
    AUDIO_SOURCE=$(pactl list sources short 2>/dev/null | head -1 | awk '{print $2}')
fi

echo -e "${GREEN}Audio source:${NC} ${AUDIO_SOURCE:-none detected}"

# ── Find YouTube browser window ───────────────────────────────────────────────
find_youtube_window() {
    # Priority: YouTube tab title, then Chrome, then Firefox
    local WID

    # Search by window title containing YouTube
    WID=$(xdotool search --name "YouTube" 2>/dev/null | while read -r id; do
        name=$(xdotool getwindowname "$id" 2>/dev/null)
        # Only top-level windows that have a meaningful title
        if [ -n "$name" ] && [[ "$name" != "google-chrome-stable" ]] && [[ "$name" != "firefox" ]]; then
            echo "$id"
            break
        fi
    done | head -1)

    # Fallback: first Chrome window with a real title
    if [ -z "$WID" ]; then
        WID=$(xdotool search --class "google-chrome" 2>/dev/null | while read -r id; do
            name=$(xdotool getwindowname "$id" 2>/dev/null)
            if [ -n "$name" ] && [[ "$name" != "google-chrome-stable" ]]; then
                echo "$id"
                break
            fi
        done | head -1)
    fi

    # Fallback: Firefox
    if [ -z "$WID" ]; then
        WID=$(xdotool search --class "firefox" 2>/dev/null | while read -r id; do
            name=$(xdotool getwindowname "$id" 2>/dev/null)
            if [ -n "$name" ] && [[ "$name" != "firefox" ]]; then
                echo "$id"
                break
            fi
        done | head -1)
    fi

    echo "$WID"
}

echo ""
echo -e "${YELLOW}Searching for YouTube browser window...${NC}"
WINDOW_ID=$(find_youtube_window)

if [ -n "$WINDOW_ID" ]; then
    WIN_NAME=$(xdotool getwindowname "$WINDOW_ID" 2>/dev/null)
    echo -e "${GREEN}Found:${NC} $WIN_NAME"
    echo -e "${GREEN}Window ID:${NC} $WINDOW_ID"

    # Get geometry directly from xwininfo
    GEOM=$(xwininfo -id "$WINDOW_ID" 2>/dev/null)
    X=$(echo "$GEOM"    | grep "Absolute upper-left X" | awk '{print $NF}')
    Y=$(echo "$GEOM"    | grep "Absolute upper-left Y" | awk '{print $NF}')
    WIDTH=$(echo "$GEOM"  | grep "Width:"  | awk '{print $NF}')
    HEIGHT=$(echo "$GEOM" | grep "Height:" | awk '{print $NF}')

    echo -e "${GREEN}Geometry:${NC} ${WIDTH}x${HEIGHT} at +${X},+${Y}"

    SCREEN_SIZE="${WIDTH}x${HEIGHT}"
    OFFSET="+${X},+${Y}"

    USE_WINDOW=true
else
    echo -e "${YELLOW}No browser window detected. Recording full screen.${NC}"
    SCREEN_SIZE=$(xdpyinfo | grep dimensions | awk '{print $2}')
    OFFSET="+0,+0"
    USE_WINDOW=false
fi

# ── Let user pick full screen instead ────────────────────────────────────────
echo ""
echo -e "Recording: ${BLUE}${SCREEN_SIZE} at ${OFFSET}${NC}"
echo ""
read -r -p "Record this window? (y) or full screen (f): " CHOICE
CHOICE="${CHOICE:-y}"

if [[ "$CHOICE" =~ ^[Ff]$ ]]; then
    SCREEN_SIZE=$(xdpyinfo | grep dimensions | awk '{print $2}')
    OFFSET="+0,+0"
    echo -e "${BLUE}Switched to full screen: $SCREEN_SIZE${NC}"
fi

# ── Record ────────────────────────────────────────────────────────────────────
echo ""
echo -e "${CYAN}═══════════════════════════════════════════════${NC}"
echo -e "Output: ${BLUE}$FULL_PATH${NC}"
echo ""
echo -e "${YELLOW}Instructions:${NC}"
echo "  1. Press ENTER to start recording"
echo "  2. Switch to browser and play the YouTube video"
echo "  3. Press Ctrl+C in this terminal to stop"
echo -e "${CYAN}═══════════════════════════════════════════════${NC}"
read -r -p "Press ENTER to begin..."

# Focus browser window
if [ "$USE_WINDOW" = true ] && [ -n "$WINDOW_ID" ]; then
    xdotool windowactivate --sync "$WINDOW_ID" 2>/dev/null || true
fi

echo ""
echo -e "${RED}● REC${NC}  Recording... Press Ctrl+C to stop"
echo ""

# Build audio args
AUDIO_ARGS=""
if [ -n "$AUDIO_SOURCE" ]; then
    AUDIO_ARGS="-f pulse -i $AUDIO_SOURCE -c:a aac -b:a 192k"
fi

# Trap Ctrl+C gracefully (ffmpeg will also handle q key)
trap 'echo -e "\n${GREEN}■ Stopped${NC}"' INT

ffmpeg \
    -video_size "$SCREEN_SIZE" \
    -framerate 30 \
    -f x11grab \
    -i "${DISPLAY:-:0}${OFFSET}" \
    $AUDIO_ARGS \
    -c:v libx264 \
    -preset ultrafast \
    -crf 23 \
    -pix_fmt yuv420p \
    "$FULL_PATH" 2>&1 | grep --line-buffered -E "frame=|time=|error|Error" || true

# ── Done ──────────────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║         Recording Complete!                    ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════╝${NC}"
echo ""

if [ -f "$FULL_PATH" ]; then
    SIZE=$(du -h "$FULL_PATH" | cut -f1)
    RAW_DUR=$(ffprobe -v error -show_entries format=duration \
        -of default=noprint_wrappers=1:nokey=1 "$FULL_PATH" 2>/dev/null || echo 0)
    DUR_FMT=$(printf '%02d:%02d:%02d' \
        $((${RAW_DUR%.*}/3600)) \
        $((${RAW_DUR%.*}%3600/60)) \
        $((${RAW_DUR%.*}%60)))

    echo -e "${BLUE}File:${NC}     $FULL_PATH"
    echo -e "${BLUE}Size:${NC}     $SIZE"
    echo -e "${BLUE}Duration:${NC} $DUR_FMT"
else
    echo -e "${RED}Warning: Output file not found. Recording may have failed.${NC}"
fi

echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  Process (transcripts + screenshots):"
echo -e "  ${CYAN}./scripts/process_presentation_video.sh '$FULL_PATH' 60${NC}"
echo ""
