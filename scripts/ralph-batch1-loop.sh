#!/bin/bash
# Ralph Batch 1 Production Loop
# Automated persona generation for 207 FRACP-equivalent personas

set -e  # Exit on error
set -u  # Exit on undefined variable

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CONFIG_FILE="$PROJECT_ROOT/clinical-content-prds/validation-system/batch1_full_config.json"
STATE_FILE="$PROJECT_ROOT/clinical-content-prds/.batch1_state.json"
OUTPUT_DIR="$PROJECT_ROOT/clinical-content-prds/batch1-output"
LOG_FILE="$OUTPUT_DIR/ralph_batch1.log"

# Python environment
PYTHON_BIN="$PROJECT_ROOT/backend/venv/bin/python3"
GENERATOR_SCRIPT="$PROJECT_ROOT/clinical-content-prds/validation-system/batch1_persona_generator.py"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Parse arguments
RESUME=false
while [[ $# -gt 0 ]]; do
  case $1 in
    --resume)
      RESUME=true
      shift
      ;;
    *)
      echo "Usage: $0 [--resume]"
      exit 1
      ;;
  esac
done

# Initialize or load state
if [[ "$RESUME" == "true" && -f "$STATE_FILE" ]]; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] Resuming from previous state..."
  START_INDEX=$(cat "$STATE_FILE" | python3 -c "import sys, json; print(json.load(sys.stdin)['completed_personas'])")
else
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting new batch..."
  START_INDEX=0
  $PYTHON_BIN "$GENERATOR_SCRIPT" --init-state --config "$CONFIG_FILE" --state "$STATE_FILE"
fi

# Load total persona count
TOTAL_PERSONAS=$(cat "$CONFIG_FILE" | python3 -c "import sys, json; print(json.load(sys.stdin)['total_personas'])")

# Main loop
echo "[$(date '+%Y-%m-%d %H:%M:%S')] ===== RALPH BATCH 1 PRODUCTION STARTED ====="
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Total personas: $TOTAL_PERSONAS"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting from index: $START_INDEX"

for ((i=$START_INDEX; i<$TOTAL_PERSONAS; i++)); do
  echo ""
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] ========================================="
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] Processing persona $((i+1))/$TOTAL_PERSONAS..."

  # Generate and validate persona
  if $PYTHON_BIN "$GENERATOR_SCRIPT" --index "$i" --config "$CONFIG_FILE" --state "$STATE_FILE"; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ✅ Persona $((i+1)) completed successfully"
  else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ❌ Persona $((i+1)) failed - flagged for manual review"
    # Continue to next persona (don't block entire batch)
  fi

  # Progress update
  COMPLETED=$(cat "$STATE_FILE" | python3 -c "import sys, json; print(json.load(sys.stdin)['completed_personas'])")
  PROGRESS=$(echo "scale=1; $COMPLETED * 100 / $TOTAL_PERSONAS" | bc)
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] Progress: $PROGRESS% ($COMPLETED/$TOTAL_PERSONAS)"

  # Rate limiting (Claude API: 90 req/min limit, use 60 req/min for safety)
  sleep 1
done

echo ""
echo "[$(date '+%Y-%m-%d %H:%M:%S')] ===== RALPH BATCH 1 PRODUCTION COMPLETE ====="
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Total completed: $COMPLETED/$TOTAL_PERSONAS"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Output directory: $OUTPUT_DIR"
