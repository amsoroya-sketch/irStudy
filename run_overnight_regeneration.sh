#!/bin/bash
# Overnight OSCE Regeneration - Sequential Execution
# Estimated total time: 5.5 hours
# Rate limited: 5 seconds between Claude API calls

set -e  # Exit on error

LOG_DIR="logs/osce_regeneration_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$LOG_DIR"

echo "=========================================="
echo "OSCE Overnight Regeneration Started"
echo "Date: $(date)"
echo "Log Directory: $LOG_DIR"
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
    echo "Original: $original_file"
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

# Phase 1: Cardiology (50 OSCEs, ~150 minutes)
echo "PHASE 1: CARDIOLOGY REGENERATION"
echo "Estimated time: 2.5 hours (50 OSCEs × 3 min each)"
echo ""

run_regeneration \
    "Cardiology" \
    "data/osces/cardiology_50_osces.json" \
    "data/osces/cardiology_50_osces.json" \
    "cardiology"

CARDIOLOGY_STATUS=$?

# Phase 2: Respiratory (50 OSCEs, ~150 minutes)
echo "PHASE 2: RESPIRATORY REGENERATION"
echo "Estimated time: 2.5 hours (50 OSCEs × 3 min each)"
echo ""

run_regeneration \
    "Respiratory" \
    "data/osces/respiratory_50_osces.json" \
    "data/osces/respiratory_50_osces.json" \
    "respiratory"

RESPIRATORY_STATUS=$?

# Phase 3: Psychiatry Retry (6 failed OSCEs, ~20 minutes)
echo "PHASE 3: PSYCHIATRY RETRY (Failed OSCEs)"
echo "Estimated time: 20 minutes (6 OSCEs × 3 min each)"
echo ""

run_regeneration \
    "Psychiatry_Retry" \
    "data/osces/psychiatry_40_osces_regenerated.json" \
    "data/osces/psychiatry_40_osces.json" \
    "psychiatry"

PSYCHIATRY_STATUS=$?

# Summary Report
echo ""
echo "=========================================="
echo "OVERNIGHT REGENERATION COMPLETE"
echo "Completed at: $(date)"
echo "=========================================="
echo ""
echo "Results:"
echo "  Cardiology:  $([ $CARDIOLOGY_STATUS -eq 0 ] && echo '✅ SUCCESS' || echo '❌ FAILED')"
echo "  Respiratory: $([ $RESPIRATORY_STATUS -eq 0 ] && echo '✅ SUCCESS' || echo '❌ FAILED')"
echo "  Psychiatry:  $([ $PSYCHIATRY_STATUS -eq 0 ] && echo '✅ SUCCESS' || echo '❌ FAILED')"
echo ""
echo "Logs saved to: $LOG_DIR"
echo ""

# Create summary file
cat > "$LOG_DIR/SUMMARY.txt" <<EOF
OSCE Overnight Regeneration Summary
====================================

Started:  $(head -n 1 $LOG_DIR/*.log | grep -m1 "Date:" || echo "Unknown")
Completed: $(date)

Results:
  Cardiology:  $([ $CARDIOLOGY_STATUS -eq 0 ] && echo 'SUCCESS' || echo 'FAILED')
  Respiratory: $([ $RESPIRATORY_STATUS -eq 0 ] && echo 'SUCCESS' || echo 'FAILED')
  Psychiatry:  $([ $PSYCHIATRY_STATUS -eq 0 ] && echo 'SUCCESS' || echo 'FAILED')

Log Files:
$(ls -1 $LOG_DIR/*.log)

Next Steps:
1. Review logs for any errors
2. Validate placeholder detection (should be 0%)
3. Run full evaluation system
4. Deploy regenerated files to production

EOF

echo "Summary saved to: $LOG_DIR/SUMMARY.txt"
echo ""

# Exit with success if all passed, failure if any failed
[ $CARDIOLOGY_STATUS -eq 0 ] && [ $RESPIRATORY_STATUS -eq 0 ] && [ $PSYCHIATRY_STATUS -eq 0 ]
