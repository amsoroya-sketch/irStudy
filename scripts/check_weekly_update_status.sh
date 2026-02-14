#!/bin/bash
################################################################################
# Check Weekly Update Status
#
# Quick status check showing:
# - Last run date
# - Success/failure status
# - Resources updated
# - Disk usage
################################################################################

STATE_FILE="/mnt/data/medical_resources/weekly_update_state.json"
DOWNLOAD_DIR="/mnt/data/medical_resources"

if [ ! -f "${STATE_FILE}" ]; then
    echo "⚠️  State file not found - run init_weekly_state.py first"
    exit 1
fi

# Extract info from state file using jq (if available) or python
if command -v jq &> /dev/null; then
    LAST_RUN=$(jq -r '.last_run // "Never"' "${STATE_FILE}")
    TOTAL_RUNS=$(jq -r '.run_summary.total_runs' "${STATE_FILE}")
    STATUS=$(jq -r '.run_summary.last_run_status // "N/A"' "${STATE_FILE}")
else
    # Fallback to python
    LAST_RUN=$(python3 -c "import json; d=json.load(open('${STATE_FILE}')); print(d.get('last_run', 'Never'))")
    TOTAL_RUNS=$(python3 -c "import json; d=json.load(open('${STATE_FILE}')); print(d['run_summary']['total_runs'])")
    STATUS=$(python3 -c "import json; d=json.load(open('${STATE_FILE}')); print(d['run_summary'].get('last_run_status', 'N/A'))")
fi

# Disk usage
DISK_USAGE=$(du -sh ${DOWNLOAD_DIR} 2>/dev/null | cut -f1)
FREE_SPACE=$(df -h ${DOWNLOAD_DIR} 2>/dev/null | tail -1 | awk '{print $4}')

# Display status
echo "================================================================"
echo "WEEKLY UPDATE STATUS"
echo "================================================================"
echo "Last run: ${LAST_RUN}"
echo "Total runs: ${TOTAL_RUNS}"
echo "Last status: ${STATUS}"
echo ""
echo "Disk usage: ${DISK_USAGE}"
echo "Free space: ${FREE_SPACE}"
echo "================================================================"
