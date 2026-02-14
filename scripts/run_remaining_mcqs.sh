#!/bin/bash
# Generate remaining 64 MCQs using RAG system

cd /home/dev/Development/irStudy

source venv/bin/activate

indices=$(cat remaining_indices.txt)

echo "Starting RAG generation for 64 remaining MCQs..."
echo "Indices: ${indices:0:100}..."
echo ""
echo "Using RAG System:"
echo "  - Qdrant vector DB (9,950 chunks)"
echo "  - S-PubMedBert embeddings"
echo "  - Ollama deepseek-r1:7b (NOT Claude)"
echo ""

python3 scripts/generate_mcqs_by_index.py --indices "$indices"
