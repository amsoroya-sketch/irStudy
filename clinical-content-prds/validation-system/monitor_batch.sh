#!/bin/bash
# Batch Persona Generation Monitor
# Usage: ./monitor_batch.sh

clear
echo "═══════════════════════════════════════════════════════"
echo "  RAG Persona Batch Generation Monitor"
echo "═══════════════════════════════════════════════════════"
echo

# Check if tmux session is running
if tmux has-session -t persona-batch 2>/dev/null; then
    echo "✅ Tmux session: RUNNING"
else
    echo "❌ Tmux session: NOT FOUND"
    echo
    echo "Start with: tmux attach -t persona-batch"
    exit 1
fi

echo

# Count completed personas
COMPLETED=$(ls clinical-content-prds/validation-system/batch1_personas/*.json 2>/dev/null | wc -l)
TOTAL=207
PERCENT=$((COMPLETED * 100 / TOTAL))

echo "📊 Progress: $COMPLETED/$TOTAL personas ($PERCENT%)"
echo

# Progress bar
BAR_WIDTH=50
FILLED=$((COMPLETED * BAR_WIDTH / TOTAL))
EMPTY=$((BAR_WIDTH - FILLED))

printf "["
printf "%${FILLED}s" | tr ' ' '█'
printf "%${EMPTY}s" | tr ' ' '░'
printf "] $PERCENT%%\n"
echo

# Estimated time remaining
if [ $COMPLETED -gt 0 ]; then
    REMAINING=$((TOTAL - COMPLETED))
    EST_SECONDS=$((REMAINING * 6))  # 6 seconds per persona
    EST_MINUTES=$((EST_SECONDS / 60))
    echo "⏱️  Estimated time remaining: ~$EST_MINUTES minutes"
    echo
fi

# Citation statistics
TOTAL_CITATIONS=$(grep -c '"qdrant_point_id"' clinical-content-prds/validation-system/batch1_personas/*.json 2>/dev/null || echo "0")
AUSTRALIAN_CITATIONS=$(grep '"source_category": "gp_primary_care"' clinical-content-prds/validation-system/batch1_personas/*.json 2>/dev/null | wc -l)

if [ $TOTAL_CITATIONS -gt 0 ]; then
    AUS_PERCENT=$((AUSTRALIAN_CITATIONS * 100 / TOTAL_CITATIONS))
    echo "📚 Citations generated: $TOTAL_CITATIONS"
    echo "🇦🇺 Australian sources: $AUSTRALIAN_CITATIONS ($AUS_PERCENT%)"
    echo
fi

# Recent output
echo "═══════════════════════════════════════════════════════"
echo "Recent progress (last 10 lines):"
echo "═══════════════════════════════════════════════════════"
tail -10 clinical-content-prds/validation-system/batch1_generation.log 2>/dev/null | grep -E "^\[|✓ Saved:" || echo "No log output yet"
echo

# Commands
echo "═══════════════════════════════════════════════════════"
echo "Commands:"
echo "═══════════════════════════════════════════════════════"
echo "  Watch live:      tail -f clinical-content-prds/validation-system/batch1_generation.log"
echo "  Attach to tmux:  tmux attach -t persona-batch"
echo "  Kill session:    tmux kill-session -t persona-batch"
echo "  Re-run monitor:  ./clinical-content-prds/validation-system/monitor_batch.sh"
echo

if [ $COMPLETED -eq $TOTAL ]; then
    echo "🎉 BATCH GENERATION COMPLETE!"
    echo
    echo "View report: cat clinical-content-prds/validation-system/batch1_generation_report.json"
fi
