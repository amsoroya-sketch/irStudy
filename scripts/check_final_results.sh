#!/bin/bash
echo "========================================================================"
echo "RAG MCQ GENERATION - FINAL RESULTS"
echo "========================================================================"
echo ""

# Count total generated
total=$(jq '[.mcqs[] | select(.generated_by == "rag_ollama")] | length' data/mcqs/missing_topics_comprehensive_mcqs.json 2>/dev/null)
echo "📊 Total MCQs with RAG citations: ${total}/658"
echo ""

# Check each batch completion
echo "📋 Batch Completion Status:"
for batch in {1..33}; do
    if [ -f "logs/mcq_rag_generation/batch_${batch}.log" ]; then
        if grep -q "GENERATION SUMMARY" "logs/mcq_rag_generation/batch_${batch}.log" 2>/dev/null; then
            generated=$(grep "Successfully generated:" "logs/mcq_rag_generation/batch_${batch}.log" | tail -1 | awk '{print $3}')
            failed=$(grep "Failed:" "logs/mcq_rag_generation/batch_${batch}.log" | tail -1 | awk '{print $2}')
            echo "   ✅ Batch ${batch}: ${generated} generated, ${failed} failed"
        else
            echo "   ❌ Batch ${batch}: Did not complete"
        fi
    fi
done

echo ""
echo "========================================================================"
