#!/bin/bash
# Start Parallel HEAL Image Downloads using Taxonomy
# Launches 5 tmux sessions for concurrent downloads

echo "============================================================"
echo "STARTING PARALLEL HEAL DOWNLOADS"
echo "Using taxonomy with 831 nodes, 3,274 search terms"
echo "============================================================"
echo ""

# Check if tmux is available
if ! command -v tmux &> /dev/null; then
    echo "❌ tmux is not installed. Installing..."
    sudo apt-get update && sudo apt-get install -y tmux
fi

# Create tmux session names
SESSION_PREFIX="heal_download"

# Kill any existing sessions
tmux kill-session -t ${SESSION_PREFIX}_batch1 2>/dev/null
tmux kill-session -t ${SESSION_PREFIX}_batch2 2>/dev/null
tmux kill-session -t ${SESSION_PREFIX}_batch3 2>/dev/null
tmux kill-session -t ${SESSION_PREFIX}_batch4 2>/dev/null
tmux kill-session -t ${SESSION_PREFIX}_batch5 2>/dev/null

echo "Launching 5 parallel download sessions..."
echo ""

# Batch 1: Cardiology + Respiratory (Priority HIGH, 436 nodes)
echo "[1/5] Starting Batch 1: Cardiology + Respiratory"
tmux new-session -d -s ${SESSION_PREFIX}_batch1 "
cd /home/dev/Development/irStudy
python3 scripts/download_heal_comprehensive.py \
    --specialties cardiology respiratory \
    --images-per-topic 8 \
    --output data/medical_images \
    --yes \
    2>&1 | tee logs/download_batch1.log
"

# Batch 2: Dermatology + Haematology (Priority HIGH, 131 nodes)
echo "[2/5] Starting Batch 2: Dermatology + Haematology"
tmux new-session -d -s ${SESSION_PREFIX}_batch2 "
cd /home/dev/Development/irStudy
python3 scripts/download_heal_comprehensive.py \
    --specialties dermatology hematology \
    --images-per-topic 8 \
    --output data/medical_images \
    --yes \
    2>&1 | tee logs/download_batch2.log
"

# Batch 3: Gastrointestinal + Pediatrics (Priority HIGH)
echo "[3/5] Starting Batch 3: Gastrointestinal + Pediatrics"
tmux new-session -d -s ${SESSION_PREFIX}_batch3 "
cd /home/dev/Development/irStudy
python3 scripts/download_heal_comprehensive.py \
    --specialties gastrointestinal pediatrics \
    --images-per-topic 8 \
    --output data/medical_images \
    --yes \
    2>&1 | tee logs/download_batch3.log
"

# Batch 4: Pathology + Anatomy (Supporting specialties)
echo "[4/5] Starting Batch 4: Pathology + Anatomy"
tmux new-session -d -s ${SESSION_PREFIX}_batch4 "
cd /home/dev/Development/irStudy
python3 scripts/download_heal_comprehensive.py \
    --specialties pathology anatomy \
    --images-per-topic 8 \
    --output data/medical_images \
    --yes \
    2>&1 | tee logs/download_batch4.log
"

# Batch 5: Infectious Disease + Bone Marrow (Additional coverage)
echo "[5/5] Starting Batch 5: Infectious Disease + Bone Marrow"
tmux new-session -d -s ${SESSION_PREFIX}_batch5 "
cd /home/dev/Development/irStudy
python3 scripts/download_heal_comprehensive.py \
    --specialties infectious_disease bone_marrow \
    --images-per-topic 8 \
    --output data/medical_images \
    --yes \
    2>&1 | tee logs/download_batch5.log
"

echo ""
echo "============================================================"
echo "✅ PARALLEL DOWNLOADS STARTED"
echo "============================================================"
echo ""
echo "Active tmux sessions:"
tmux list-sessions 2>/dev/null | grep heal_download || echo "No active sessions"
echo ""
echo "To monitor downloads:"
echo "  tmux attach -t heal_download_batch1   # Cardiology + Respiratory"
echo "  tmux attach -t heal_download_batch2   # Dermatology + Haematology"
echo "  tmux attach -t heal_download_batch3   # Neurology + Gastroenterology"
echo "  tmux attach -t heal_download_batch4   # Endocrinology + Obs/Gyn"
echo "  tmux attach -t heal_download_batch5   # Paediatrics + Emergency + Psychiatry"
echo ""
echo "To detach from tmux: Press Ctrl+B then D"
echo ""
echo "To check logs:"
echo "  tail -f logs/download_batch*.log"
echo ""
echo "To stop all downloads:"
echo "  ./stop_parallel_downloads.sh"
echo ""
echo "Estimated completion time:"
echo "  With 5 parallel workers: ~45-60 minutes"
echo "  Total images: ~6,300"
echo "============================================================"
