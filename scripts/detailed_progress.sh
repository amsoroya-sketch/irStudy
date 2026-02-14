#!/bin/bash
echo "========================================"
echo "RAG MCQ GENERATION - DETAILED PROGRESS"
echo "========================================"
echo ""

# Total generated
total=$(jq '[.mcqs[] | select(.generated_by == "rag_ollama")] | length' data/mcqs/missing_topics_comprehensive_mcqs.json 2>/dev/null)
echo "📊 Total Generated: ${total}/658 ($(echo "scale=1; $total * 100 / 658" | bc)%)"
echo ""

# Check which batches completed
echo "✅ Completed Batches:"
for batch in {1..33}; do
    if [ -f "logs/mcq_rag_generation/batch_${batch}.log" ]; then
        if grep -q "GENERATION SUMMARY" "logs/mcq_rag_generation/batch_${batch}.log" 2>/dev/null; then
            generated=$(grep "Successfully generated:" "logs/mcq_rag_generation/batch_${batch}.log" | tail -1 | grep -o '[0-9]*' | head -1)
            echo "   Batch ${batch}: ${generated:-?}/20 MCQs"
        fi
    fi
done

echo ""
echo "⏳ In Progress:"
for batch in {1..10}; do
    if [ -f "logs/mcq_rag_generation/batch_${batch}.log" ]; then
        if ! grep -q "GENERATION SUMMARY" "logs/mcq_rag_generation/batch_${batch}.log" 2>/dev/null; then
            progress=$(tail -10 "logs/mcq_rag_generation/batch_${batch}.log" | grep "Generating MCQs:" | tail -1)
            if [ ! -z "$progress" ]; then
                echo "   Batch ${batch}: ${progress}"
            fi
        fi
    fi
done

echo ""
echo "========================================"
