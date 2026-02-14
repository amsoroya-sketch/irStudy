#!/bin/bash
# Launch all RAG MCQ generation batches

echo "========================================================================"
echo "LAUNCHING ALL RAG MCQ GENERATION BATCHES"
echo "========================================================================"
echo ""
echo "Total MCQs: 658"
echo "Batch size: 20"
echo "Total batches: 33 (32 full + 1 partial)"
echo ""

# Generate batch commands (33 batches total)
# Batches 1-32: 20 MCQs each
# Batch 33: 18 MCQs (658 - 640 = 18)

START_BATCH=${1:-4}  # Start from batch 4 (batches 1-3 already running)
END_BATCH=${2:-33}

echo "Starting batches ${START_BATCH} to ${END_BATCH}..."
echo ""

for ((batch=${START_BATCH}; batch<=${END_BATCH}; batch++)); do
    start_idx=$(( (batch - 1) * 20 ))
    
    # Last batch only has 18 MCQs
    if [ $batch -eq 33 ]; then
        batch_size=18
    else
        batch_size=20
    fi
    
    echo "Launching Batch ${batch}: MCQs ${start_idx} to $((start_idx + batch_size - 1))"
    bash scripts/run_rag_mcq_batch.sh ${batch} ${start_idx} ${batch_size}
    
    # Small delay between launches to avoid overwhelming the system
    sleep 1
done

echo ""
echo "========================================================================"
echo "✅ All batches launched!"
echo "========================================================================"
echo ""
echo "Monitor progress: bash scripts/monitor_rag_generation.sh"
echo "View specific batch: tmux attach -t mcq_rag_batch_N"
echo "View logs: tail -f logs/mcq_rag_generation/batch_N.log"
echo ""
