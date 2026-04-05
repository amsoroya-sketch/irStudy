#!/bin/bash
# Monitor Overnight Regeneration Progress

echo "=========================================="
echo "OSCE Regeneration Monitor"
echo "=========================================="
echo ""

# Find latest log directory (check retry first, then original)
LATEST_LOG_DIR=$(ls -td logs/osce_retry_* logs/osce_regeneration_* 2>/dev/null | head -n1)

if [ -z "$LATEST_LOG_DIR" ]; then
    echo "No regeneration logs found. Has the process started?"
    echo ""
    echo "To start regeneration, run:"
    echo "  ./run_overnight_regeneration.sh"
    echo ""
    exit 1
fi

echo "Log Directory: $LATEST_LOG_DIR"
echo ""

# Check if tmux session exists
if tmux has-session -t osce-retry 2>/dev/null; then
    echo "✅ RETRY session is RUNNING"
    echo ""
    echo "To attach and view live progress:"
    echo "  tmux attach -t osce-retry"
    echo ""
    echo "To detach (without stopping): Press Ctrl+B, then D"
    echo ""
elif tmux has-session -t osce-regen 2>/dev/null; then
    echo "✅ Original session is RUNNING"
    echo ""
    echo "To attach and view live progress:"
    echo "  tmux attach -t osce-regen"
    echo ""
    echo "To detach (without stopping): Press Ctrl+B, then D"
    echo ""
else
    echo "⚠️  Regeneration session not found in tmux"
    echo ""
fi

# Show latest log files
echo "Latest Log Files:"
ls -lh "$LATEST_LOG_DIR"/*.log 2>/dev/null || echo "  (no logs yet)"
echo ""

# Show progress from latest log
LATEST_LOG=$(ls -t "$LATEST_LOG_DIR"/*.log 2>/dev/null | head -n1)

if [ -n "$LATEST_LOG" ]; then
    echo "=========================================="
    echo "Latest Progress (last 20 lines):"
    echo "=========================================="
    tail -n 20 "$LATEST_LOG"
    echo ""
fi

# Count completed OSCEs
COMPLETED=$(grep -h "✅ Replaced NULL OSCE" "$LATEST_LOG_DIR"/*.log 2>/dev/null | wc -l)
FAILED=$(grep -h "❌ Generation failed" "$LATEST_LOG_DIR"/*.log 2>/dev/null | wc -l)

echo "=========================================="
echo "Summary:"
echo "=========================================="
echo "  Completed: $COMPLETED OSCEs"
echo "  Failed: $FAILED OSCEs"
echo "  Total Processed: $((COMPLETED + FAILED))"
echo "  Target: 106 OSCEs (50 cardiology + 50 respiratory + 6 psychiatry)"
echo ""

# Estimate time remaining
if [ $COMPLETED -gt 0 ]; then
    REMAINING=$((106 - COMPLETED - FAILED))
    MINUTES_REMAINING=$((REMAINING * 3))
    HOURS=$((MINUTES_REMAINING / 60))
    MINS=$((MINUTES_REMAINING % 60))
    echo "  Estimated time remaining: ${HOURS}h ${MINS}m"
    echo ""
fi

echo "To check again, run: ./monitor_regeneration.sh"
echo ""
