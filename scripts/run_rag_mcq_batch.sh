#!/bin/bash
# Run RAG MCQ generation batch in tmux

BATCH_NUM=$1
START_IDX=$2
BATCH_SIZE=${3:-20}

SESSION_NAME="mcq_rag_batch_${BATCH_NUM}"
LOG_FILE="logs/mcq_rag_generation/batch_${BATCH_NUM}.log"

echo "Starting Batch ${BATCH_NUM}: MCQs ${START_IDX} to $((START_IDX + BATCH_SIZE - 1))"

# Kill existing session if it exists
tmux kill-session -t ${SESSION_NAME} 2>/dev/null

# Create new tmux session
tmux new-session -d -s ${SESSION_NAME}

# Run generation in tmux
tmux send-keys -t ${SESSION_NAME} "cd /home/dev/Development/irStudy" Enter
tmux send-keys -t ${SESSION_NAME} "source venv/bin/activate" Enter
tmux send-keys -t ${SESSION_NAME} "python scripts/generate_mcqs_from_rag.py --batch-size ${BATCH_SIZE} --start ${START_IDX} 2>&1 | tee ${LOG_FILE}" Enter

echo "✅ Batch ${BATCH_NUM} started in tmux session: ${SESSION_NAME}"
echo "   View logs: tail -f ${LOG_FILE}"
echo "   Attach to session: tmux attach -t ${SESSION_NAME}"
