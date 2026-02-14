#!/bin/bash
# Generate null MCQs in background

cd /home/dev/Development/irStudy

source venv/bin/activate

indices=$(cat null_indices.txt)

echo "Starting generation for 100 null MCQs..."
echo "Indices: ${indices:0:100}..."

python3 scripts/generate_mcqs_by_index.py --indices "$indices"
