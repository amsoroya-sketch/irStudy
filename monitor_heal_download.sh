#!/bin/bash
# Monitor HEAL download progress in tmux session

echo "=============================================="
echo "HEAL Download Monitor"
echo "=============================================="
echo ""

# Check if session exists
if ! tmux has-session -t heal_download 2>/dev/null; then
    echo "❌ Tmux session 'heal_download' not found"
    echo ""
    echo "To start a new download:"
    echo "  tmux new-session -s heal_download"
    echo "  source venv/bin/activate"
    echo "  ./download_heal_comprehensive.sh --phase 1"
    exit 1
fi

echo "✓ Tmux session 'heal_download' is running"
echo ""

# Show recent output
echo "Recent output (last 30 lines):"
echo "----------------------------------------------"
tmux capture-pane -t heal_download -p | tail -30
echo "----------------------------------------------"
echo ""

# Check log file
if [ -f "heal_download_phase1.log" ]; then
    TOTAL_LINES=$(wc -l < heal_download_phase1.log)
    IMAGES_DOWNLOADED=$(grep -c "Downloaded.*images" heal_download_phase1.log 2>/dev/null || echo "0")
    TOPICS_COMPLETED=$(grep -c "✓ Downloaded.*images" heal_download_phase1.log 2>/dev/null || echo "0")

    echo "Progress from log file:"
    echo "  Total log lines: $TOTAL_LINES"
    echo "  Topics completed: $TOPICS_COMPLETED"
    echo "  Download operations: $IMAGES_DOWNLOADED"
    echo ""
fi

# Check downloaded files
if [ -d "data/medical_images/heal" ]; then
    IMAGE_COUNT=$(find data/medical_images/heal -name "*.jpg" 2>/dev/null | wc -l)
    FOLDER_COUNT=$(find data/medical_images/heal -type d -mindepth 2 -maxdepth 2 2>/dev/null | wc -l)
    TOTAL_SIZE=$(du -sh data/medical_images/heal 2>/dev/null | cut -f1)

    echo "Downloaded so far:"
    echo "  Images: $IMAGE_COUNT files"
    echo "  Topic folders: $FOLDER_COUNT"
    echo "  Total size: $TOTAL_SIZE"
    echo ""
fi

echo "Commands:"
echo "  Watch live:     tmux attach -t heal_download"
echo "  Detach:         Press Ctrl+B, then D"
echo "  Monitor:        ./monitor_heal_download.sh"
echo "  View log:       tail -f heal_download_phase1.log"
echo "  Kill session:   tmux kill-session -t heal_download"
echo ""
