#!/bin/bash
# Monitor RAG MCQ generation progress

echo "========================================================================"
echo "RAG MCQ GENERATION - PROGRESS MONITOR"
echo "========================================================================"
echo ""

# Check tmux sessions
echo "📺 Active tmux sessions:"
tmux list-sessions 2>/dev/null | grep "mcq_rag_batch" || echo "   No active batch sessions"
echo ""

# Check log files
echo "📊 Batch progress:"
for log in logs/mcq_rag_generation/batch_*.log; do
    if [ -f "$log" ]; then
        batch_num=$(basename "$log" | grep -o '[0-9]*')
        generated=$(grep -o "Generated: [0-9]*" "$log" | tail -1 | grep -o '[0-9]*' || echo "0")
        failed=$(grep -o "Failed: [0-9]*" "$log" | tail -1 | grep -o '[0-9]*' || echo "0")
        echo "   Batch ${batch_num}: Generated=${generated}, Failed=${failed}"
    fi
done
echo ""

# Check overall progress
echo "📈 Overall progress:"
if [ -f "MCQ_RAG_GENERATION_PROGRESS.md" ]; then
    tail -10 MCQ_RAG_GENERATION_PROGRESS.md
else
    echo "   No progress file yet"
fi

echo ""
echo "========================================================================"
