#!/bin/bash
# Live Progress Watcher - Shows file size changes every 30 seconds

echo "=========================================="
echo "OSCE Regeneration - Live Progress Monitor"
echo "Started: $(date)"
echo "=========================================="
echo ""
echo "Watching file sizes (updates every 30 seconds)"
echo "Press Ctrl+C to exit"
echo ""

while true; do
    clear
    echo "=========================================="
    echo "OSCE File Sizes - $(date +%H:%M:%S)"
    echo "=========================================="
    echo ""

    echo "Cardiology (Target: ~800KB when complete):"
    ls -lh data/osces/cardiology_50_osces.json 2>/dev/null | awk '{print "  "$5" - Last modified: "$6,$7,$8}'

    echo ""
    echo "Respiratory (Target: ~900KB when complete):"
    ls -lh data/osces/respiratory_50_osces.json 2>/dev/null | awk '{print "  "$5" - Last modified: "$6,$7,$8}'

    echo ""
    echo "Psychiatry (Already 460KB - adding 6 more):"
    ls -lh data/osces/psychiatry_40_osces_regenerated.json 2>/dev/null | awk '{print "  "$5" - Last modified: "$6,$7,$8}'

    echo ""
    echo "=========================================="

    # Check if process still running
    if ps -ef | grep -q "[c]omplete_partial_osces.py"; then
        echo "Status: ✅ Regeneration process RUNNING"

        # Count Claude subprocesses
        CLAUDE_COUNT=$(ps -ef | grep -c "[c]laude.*660243")
        if [ $CLAUDE_COUNT -gt 0 ]; then
            echo "Claude API: 🔄 Active ($CLAUDE_COUNT subprocess)"
        else
            echo "Claude API: ⏸️  Idle (waiting)"
        fi
    else
        echo "Status: ⚠️  Process not found (may have completed or failed)"
        echo ""
        echo "Check tmux session: tmux attach -t osce-regen"
        break
    fi

    echo "=========================================="
    echo "Refreshing in 30 seconds... (Ctrl+C to exit)"

    sleep 30
done
