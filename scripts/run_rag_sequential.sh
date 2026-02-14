#!/bin/bash
# Run RAG MCQ generation sequentially to avoid overwhelming Ollama

echo "========================================================================"
echo "RAG MCQ GENERATION - SEQUENTIAL MODE"
echo "========================================================================"
echo ""
echo "Running batches sequentially to avoid resource exhaustion"
echo "Total: 658 MCQs across 33 batches"
echo ""

START_BATCH=${1:-4}  # Start from batch 4 (1-3 already done)
END_BATCH=${2:-33}

for batch in $(seq $START_BATCH $END_BATCH); do
    start_idx=$(( (batch - 1) * 20 ))
    
    # Last batch only has 18 MCQs
    if [ $batch -eq 33 ]; then
        batch_size=18
    else
        batch_size=20
    fi
    
    echo "========================================================================"
    echo "Batch ${batch}/${END_BATCH}: MCQs ${start_idx}-$((start_idx + batch_size - 1))"
    echo "========================================================================"
    
    # Run directly (not in tmux since we're sequential)
    source venv/bin/activate
    python scripts/generate_mcqs_from_rag.py --batch-size ${batch_size} --start ${start_idx} 2>&1 | tee logs/mcq_rag_generation/batch_${batch}_retry.log
    
    exit_code=$?
    if [ $exit_code -eq 0 ]; then
        echo "✅ Batch ${batch} completed successfully"
    else
        echo "❌ Batch ${batch} failed with exit code ${exit_code}"
        echo "   Continuing to next batch..."
    fi
    
    echo ""
    sleep 2  # Small delay between batches
done

echo "========================================================================"
echo "✅ Sequential generation complete!"
echo "========================================================================"

# Final count
total=$(jq '[.mcqs[] | select(.generated_by == "rag_ollama")] | length' data/mcqs/missing_topics_comprehensive_mcqs.json 2>/dev/null)
echo "📊 Total MCQs with RAG citations: ${total}/658"
