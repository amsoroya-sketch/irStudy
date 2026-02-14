#!/bin/bash
# Monitor Cochrane download progress

clear
echo "=================================="
echo "Cochrane Download Monitor"
echo "=================================="
echo ""

while true; do
    # Count successful downloads
    SUCCESS=$(ls -1 ~/cochrane_downloads/*.pdf 2>/dev/null | wc -l)

    # Get total size
    SIZE=$(du -sh ~/cochrane_downloads/ 2>/dev/null | cut -f1)

    # Get last log line
    LAST_LINE=$(tail -1 ~/cochrane_full_download.log 2>/dev/null)

    # Count successes and failures from log
    SUCCESS_COUNT=$(grep -c "✓ Downloaded:" ~/cochrane_full_download.log 2>/dev/null)
    FAILED_COUNT=$(grep -c "✗ Download failed:" ~/cochrane_full_download.log 2>/dev/null)
    ALREADY_EXISTS=$(grep -c "✓ Already exists:" ~/cochrane_full_download.log 2>/dev/null)

    # Extract current progress
    PROGRESS=$(grep -oP '\[\d+/2353\]' ~/cochrane_full_download.log 2>/dev/null | tail -1)

    echo "$(date '+%H:%M:%S') - Progress: $PROGRESS"
    echo "  ✓ Successfully downloaded: $SUCCESS_COUNT"
    echo "  ⊘ Already existed: $ALREADY_EXISTS"
    echo "  ✗ Failed: $FAILED_COUNT"
    echo "  Total PDFs on disk: $SUCCESS ($SIZE)"
    echo ""
    echo "Last activity:"
    echo "  $LAST_LINE"
    echo ""
    echo "Press Ctrl+C to stop monitoring..."
    echo ""

    sleep 10
    clear
done
