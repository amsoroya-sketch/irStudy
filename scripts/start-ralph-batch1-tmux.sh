#!/bin/bash
# Ralph Batch 1 - Tmux Startup Script
# Sets up tmux session and launches Ralph loop

set -e

echo "========================================="
echo "Ralph Batch 1 Production - Tmux Setup"
echo "========================================="
echo ""

# Check if ANTHROPIC_API_KEY is set
if [ -z "$ANTHROPIC_API_KEY" ]; then
  echo "⚠️  ANTHROPIC_API_KEY not set!"
  echo ""
  echo "Please set your API key first:"
  echo "  export ANTHROPIC_API_KEY='your-key-here'"
  echo ""
  echo "Or run this script with the key:"
  echo "  ANTHROPIC_API_KEY='your-key' $0"
  echo ""
  exit 1
fi

# Navigate to project root
cd /home/dev/Development/irStudy

# Check if tmux session already exists
if tmux has-session -t ralph-batch1 2>/dev/null; then
  echo "⚠️  tmux session 'ralph-batch1' already exists!"
  echo ""
  echo "Options:"
  echo "  1. Attach to existing session: tmux attach -t ralph-batch1"
  echo "  2. Kill existing session: tmux kill-session -t ralph-batch1"
  echo ""
  exit 1
fi

# Create tmux session
echo "📺 Creating tmux session 'ralph-batch1'..."
tmux new-session -d -s ralph-batch1 -c /home/dev/Development/irStudy

# Set up environment in tmux
echo "🔧 Setting up environment..."
tmux send-keys -t ralph-batch1 "cd /home/dev/Development/irStudy" C-m
tmux send-keys -t ralph-batch1 "source backend/venv/bin/activate" C-m
tmux send-keys -t ralph-batch1 "export ANTHROPIC_API_KEY='$ANTHROPIC_API_KEY'" C-m
tmux send-keys -t ralph-batch1 "clear" C-m

# Display ready message
tmux send-keys -t ralph-batch1 "echo '========================================='" C-m
tmux send-keys -t ralph-batch1 "echo 'Ralph Batch 1 Production - Ready'" C-m
tmux send-keys -t ralph-batch1 "echo '========================================='" C-m
tmux send-keys -t ralph-batch1 "echo ''" C-m
tmux send-keys -t ralph-batch1 "echo '📋 Configuration:'" C-m
tmux send-keys -t ralph-batch1 "echo '   - Personas: 207 (across 5 specialties)'" C-m
tmux send-keys -t ralph-batch1 "echo '   - Quality Gates: 13 (100% deployment readiness)'" C-m
tmux send-keys -t ralph-batch1 "echo '   - Expected Duration: 60-90 minutes'" C-m
tmux send-keys -t ralph-batch1 "echo '   - Expected Cost: ~\$10-15 (Claude API)'" C-m
tmux send-keys -t ralph-batch1 "echo ''" C-m
tmux send-keys -t ralph-batch1 "echo '🚀 To start Ralph loop:'" C-m
tmux send-keys -t ralph-batch1 "echo '   ./scripts/ralph-batch1-loop.sh'" C-m
tmux send-keys -t ralph-batch1 "echo ''" C-m
tmux send-keys -t ralph-batch1 "echo '⏸️  To resume after interruption:'" C-m
tmux send-keys -t ralph-batch1 "echo '   ./scripts/ralph-batch1-loop.sh --resume'" C-m
tmux send-keys -t ralph-batch1 "echo ''" C-m
tmux send-keys -t ralph-batch1 "echo '📊 Monitor progress (in separate terminal):'" C-m
tmux send-keys -t ralph-batch1 "echo '   watch -n 60 cat clinical-content-prds/.batch1_state.json'" C-m
tmux send-keys -t ralph-batch1 "echo ''" C-m
tmux send-keys -t ralph-batch1 "echo '🔓 Detach from tmux: Ctrl+B then D'" C-m
tmux send-keys -t ralph-batch1 "echo '🔗 Reattach: tmux attach -t ralph-batch1'" C-m
tmux send-keys -t ralph-batch1 "echo '========================================='" C-m
tmux send-keys -t ralph-batch1 "echo ''" C-m

echo "✅ tmux session 'ralph-batch1' created successfully!"
echo ""
echo "📺 Attaching to session..."
echo "   (Press Ctrl+B then D to detach)"
echo ""
sleep 2

# Attach to session
tmux attach -t ralph-batch1
