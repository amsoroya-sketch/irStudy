#!/bin/bash
# Check MCQ generation rate across all batches

echo "========================================================================"
echo "RAG MCQ GENERATION - REAL-TIME STATUS"
echo "========================================================================"
echo ""

# Count total generated
total_generated=$(jq '[.mcqs[] | select(.generated_by == "rag_ollama")] | length' data/mcqs/missing_topics_comprehensive_mcqs.json 2>/dev/null)
echo "📊 Total MCQs with RAG citations: ${total_generated}/658"
echo ""

# Check live batch status from logs
echo "📈 Active Batch Progress:"
for batch in {1..10}; do
    if [ -f "logs/mcq_rag_generation/batch_${batch}.log" ]; then
        progress=$(tail -20 "logs/mcq_rag_generation/batch_${batch}.log" | grep "Generating MCQs:" | tail -1 | grep -o "[0-9]*%")
        current=$(tail -20 "logs/mcq_rag_generation/batch_${batch}.log" | grep "Generating MCQs:" | tail -1 | grep -o "| [0-9]*/20" | grep -o "[0-9]*/" | tr -d "/")
        if [ ! -z "$progress" ]; then
            echo "   Batch ${batch}: ${progress} (${current:-0}/20 MCQs)"
        fi
    fi
done

echo ""
echo "========================================================================"
