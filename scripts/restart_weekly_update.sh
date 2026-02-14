#!/bin/bash
################################################################################
# Restart Weekly Medical Resources Update
#
# Simple one-command restart script that:
# - Reads state file to determine what failed
# - Resumes from where it left off
# - No need to specify options - it figures it out automatically
################################################################################

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

PROJECT_DIR="/home/dev/Development/irStudy"
STATE_FILE="/mnt/data/medical_resources/weekly_update_state.json"

echo -e "${BLUE}======================================================================${NC}"
echo -e "${BLUE}  Restart Weekly Medical Resources Update${NC}"
echo -e "${BLUE}======================================================================${NC}"
echo ""

# Check state file exists
if [ ! -f "${STATE_FILE}" ]; then
    echo -e "${RED}ERROR: State file not found: ${STATE_FILE}${NC}"
    echo "Run init_weekly_state.py first"
    exit 1
fi

# Check for NCBI API key
if [ -z "${NCBI_API_KEY}" ]; then
    echo -e "${YELLOW}WARNING: NCBI_API_KEY not set${NC}"
    echo "StatPearls updates will be skipped"
    echo ""
    echo "To enable StatPearls:"
    echo "  export NCBI_API_KEY='your_key_here'"
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Show current state
echo -e "${BLUE}Current Status:${NC}"
python3 "${PROJECT_DIR}/scripts/check_weekly_update_status.sh" 2>/dev/null || echo "  (Status checker not yet available)"
echo ""

# Run update
echo -e "${GREEN}Starting weekly update...${NC}"
echo ""

python3 "${PROJECT_DIR}/scripts/weekly_medical_update.py" "$@"

RESULT=$?

echo ""
if [ $RESULT -eq 0 ]; then
    echo -e "${GREEN}✅ Update completed successfully!${NC}"
else
    echo -e "${RED}❌ Update completed with errors (exit code: $RESULT)${NC}"
    echo -e "${YELLOW}Check logs: /mnt/data/medical_resources/logs/weekly_update_*.log${NC}"
fi

exit $RESULT
