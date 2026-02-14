#!/bin/bash
echo "Stopping all HEAL download sessions..."
tmux kill-session -t heal_download_batch1 2>/dev/null
tmux kill-session -t heal_download_batch2 2>/dev/null
tmux kill-session -t heal_download_batch3 2>/dev/null
tmux kill-session -t heal_download_batch4 2>/dev/null
tmux kill-session -t heal_download_batch5 2>/dev/null
echo "✅ All download sessions stopped"
