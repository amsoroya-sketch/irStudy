#!/bin/bash
# PRD_OSCE_001: Download a single video
# Usage: ./02_download.sh <URL> <SLUG>
set -uo pipefail

URL="$1"
SLUG="$2"
PIPELINE_DIR="/home/dev/Development/irStudy/osce-pipeline"
OUTPUT_DIR="$PIPELINE_DIR/output/$SLUG"

mkdir -p "$OUTPUT_DIR"

echo "Downloading: $URL"
echo "Output dir: $OUTPUT_DIR"

yt-dlp \
    -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" \
    --write-info-json \
    --no-playlist \
    --cookies-from-browser chrome \
    --js-runtimes node \
    --remote-components ejs:github \
    --output "$OUTPUT_DIR/video.%(ext)s" \
    "$URL"

# Copy info JSON to metadata.json
INFO_FILE=$(ls "$OUTPUT_DIR"/video.info.json 2>/dev/null | head -1)
if [ -n "$INFO_FILE" ]; then
    cp "$INFO_FILE" "$OUTPUT_DIR/metadata.json"
else
    echo "{\"title\": \"$SLUG\", \"url\": \"$URL\"}" > "$OUTPUT_DIR/metadata.json"
fi

# Write status
cat > "$OUTPUT_DIR/status.json" << EOF
{
  "step": "downloaded",
  "slug": "$SLUG",
  "url": "$URL",
  "updated_at": "$(date -Iseconds)"
}
EOF

echo "Downloaded: $SLUG"
