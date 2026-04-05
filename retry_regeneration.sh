#!/bin/bash
# Retry OSCE Regeneration - With 10s delays to avoid rate limiting
# Estimated time: 94 OSCEs × 3-4 min = 6-8 hours

set -e

LOG_DIR="logs/osce_retry_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$LOG_DIR"

echo "=========================================="
echo "OSCE Regeneration RETRY Started"
echo "Date: $(date)"
echo "Log Directory: $LOG_DIR"
echo "Rate limiting: 10 seconds between calls"
echo "=========================================="
echo ""

# Function to log and execute
run_regeneration() {
    local name=$1
    local input_file=$2
    local original_file=$3
    local specialty=$4
    local log_file="$LOG_DIR/${name}_$(date +%H%M%S).log"

    echo "Starting: $name"
    echo "Input: $input_file"
    echo "Log: $log_file"
    echo "Time: $(date)"
    echo ""

    python3 scripts/complete_partial_osces.py \
        "$input_file" \
        "$original_file" \
        "$specialty" \
        2>&1 | tee "$log_file"

    local exit_code=$?

    if [ $exit_code -eq 0 ]; then
        echo "✅ $name COMPLETED at $(date)"
    else
        echo "❌ $name FAILED with exit code $exit_code at $(date)"
    fi

    echo "=========================================="
    echo ""

    return $exit_code
}

# Phase 1: Cardiology (38 remaining OSCEs, ~4 hours with 10s delays)
echo "PHASE 1: CARDIOLOGY RETRY"
echo "Remaining: 38 OSCEs"
echo "Estimated time: 4 hours"
echo ""

run_regeneration \
    "Cardiology_Retry" \
    "data/osces/cardiology_50_osces.json" \
    "data/osces/cardiology_50_osces.json" \
    "cardiology"

CARDIOLOGY_STATUS=$?

# Wait 5 minutes between phases to let rate limits fully reset
echo "Waiting 5 minutes before respiratory phase..."
sleep 300

# Phase 2: Respiratory (50 OSCEs, ~5 hours)
echo "PHASE 2: RESPIRATORY RETRY"
echo "Remaining: 50 OSCEs"
echo "Estimated time: 5 hours"
echo ""

run_regeneration \
    "Respiratory_Retry" \
    "data/osces/respiratory_50_osces.json" \
    "data/osces/respiratory_50_osces.json" \
    "respiratory"

RESPIRATORY_STATUS=$?

# Wait 5 minutes before psychiatry
echo "Waiting 5 minutes before psychiatry phase..."
sleep 300

# Phase 3: Psychiatry (6 OSCEs, ~40 minutes)
echo "PHASE 3: PSYCHIATRY RETRY"
echo "Remaining: 6 OSCEs"
echo "Estimated time: 40 minutes"
echo ""

run_regeneration \
    "Psychiatry_Final_Retry" \
    "data/osces/psychiatry_40_osces_regenerated.json" \
    "data/osces/psychiatry_40_osces.json" \
    "psychiatry"

PSYCHIATRY_STATUS=$?

# Summary
echo ""
echo "=========================================="
echo "REGENERATION RETRY COMPLETE"
echo "Completed at: $(date)"
echo "=========================================="
echo ""
echo "Results:"
echo "  Cardiology:  $([ $CARDIOLOGY_STATUS -eq 0 ] && echo '✅ SUCCESS' || echo '❌ FAILED')"
echo "  Respiratory: $([ $RESPIRATORY_STATUS -eq 0 ] && echo '✅ SUCCESS' || echo '❌ FAILED')"
echo "  Psychiatry:  $([ $PSYCHIATRY_STATUS -eq 0 ] && echo '✅ SUCCESS' || echo '❌ FAILED')"
echo ""
echo "Logs: $LOG_DIR"
echo ""

# Create summary
cat > "$LOG_DIR/SUMMARY.txt" <<EOF
OSCE Regeneration RETRY Summary
================================

Started:  $(head -n 1 $LOG_DIR/*.log | grep -m1 "Date:" || echo "Unknown")
Completed: $(date)

Results:
  Cardiology:  $([ $CARDIOLOGY_STATUS -eq 0 ] && echo 'SUCCESS' || echo 'FAILED')
  Respiratory: $([ $RESPIRATORY_STATUS -eq 0 ] && echo 'SUCCESS' || echo 'FAILED')
  Psychiatry:  $([ $PSYCHIATRY_STATUS -eq 0 ] && echo 'SUCCESS' || echo 'FAILED')

Rate Limiting: 10 seconds between calls (6 calls/min max)

Log Files:
$(ls -1 $LOG_DIR/*.log)

Next Steps:
1. Validate placeholder detection (target: 0%)
2. Run full evaluation system
3. Check quality of generated OSCEs
4. Deploy if quality is acceptable
EOF

echo "Summary: $LOG_DIR/SUMMARY.txt"
echo ""

[ $CARDIOLOGY_STATUS -eq 0 ] && [ $RESPIRATORY_STATUS -eq 0 ] && [ $PSYCHIATRY_STATUS -eq 0 ]
