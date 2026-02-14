#!/bin/bash
################################################################################
# Restart Download Scripts
# Resumes interrupted downloads with progress tracking
################################################################################

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

EXTERNAL_DRIVE="/mnt/data"
DOWNLOAD_DIR="${EXTERNAL_DRIVE}/medical_resources"
LOG_DIR="${DOWNLOAD_DIR}/logs"
PROJECT_DIR="/home/dev/Development/irStudy"

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  Medical Resources Download Restart${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# Check external drive
if [ ! -d "${EXTERNAL_DRIVE}" ]; then
    echo -e "${YELLOW}ERROR: External drive not found at ${EXTERNAL_DRIVE}${NC}"
    echo "Please mount the drive first"
    exit 1
fi

echo -e "${GREEN}✓ External drive found${NC}"
df -h ${EXTERNAL_DRIVE} | tail -1
echo ""

# Status summary
echo -e "${BLUE}Current Download Status:${NC}"
echo "-------------------------------------------"
du -sh ${DOWNLOAD_DIR}/*/ 2>/dev/null | grep -E "(statpearls|cochrane|australian)" || echo "No downloads found"
echo ""

# Check for NCBI API key
if [ -z "${NCBI_API_KEY}" ]; then
    echo -e "${YELLOW}WARNING: NCBI_API_KEY not set!${NC}"
    echo "StatPearls download will not start."
    echo "To fix: export NCBI_API_KEY='your_key_here'"
    echo ""
fi

################################################################################
# Restart Options
################################################################################

echo -e "${BLUE}Select downloads to restart:${NC}"
echo "1) StatPearls only (2,054/10,000 done, needs API key)"
echo "2) Cochrane only (1,016/2,353 done)"
echo "3) Both StatPearls + Cochrane"
echo "4) Show status and exit"
echo ""
read -p "Enter choice [1-4]: " choice

case $choice in
    1)
        if [ -z "${NCBI_API_KEY}" ]; then
            echo -e "${YELLOW}ERROR: NCBI_API_KEY required${NC}"
            exit 1
        fi
        echo -e "${GREEN}Starting StatPearls download...${NC}"
        python3 "${PROJECT_DIR}/scripts/download_statpearls.py" \
            --output "${DOWNLOAD_DIR}/statpearls" \
            --api-key "${NCBI_API_KEY}" \
            > "${LOG_DIR}/statpearls_restart_$(date +%Y%m%d_%H%M%S).log" 2>&1 &

        STATPEARLS_PID=$!
        echo "StatPearls PID: $STATPEARLS_PID"
        echo "$STATPEARLS_PID" > "${LOG_DIR}/statpearls.pid"
        echo -e "${GREEN}✓ StatPearls download started in background${NC}"
        echo "Monitor: tail -f ${LOG_DIR}/statpearls_restart_*.log"
        ;;

    2)
        echo -e "${GREEN}Starting Cochrane download...${NC}"
        python3 "${PROJECT_DIR}/scripts/download_cochrane_from_export.py" \
            --export-file "/home/dev/Downloads/citation-export(2).txt" \
            --output-dir "${DOWNLOAD_DIR}/cochrane" \
            > "${LOG_DIR}/cochrane_restart_$(date +%Y%m%d_%H%M%S).log" 2>&1 &

        COCHRANE_PID=$!
        echo "Cochrane PID: $COCHRANE_PID"
        echo "$COCHRANE_PID" > "${LOG_DIR}/cochrane.pid"
        echo -e "${GREEN}✓ Cochrane download started in background${NC}"
        echo "Monitor: tail -f ${LOG_DIR}/cochrane_restart_*.log"
        ;;

    3)
        if [ -z "${NCBI_API_KEY}" ]; then
            echo -e "${YELLOW}WARNING: Skipping StatPearls (no API key)${NC}"
        else
            echo -e "${GREEN}Starting StatPearls download...${NC}"
            python3 "${PROJECT_DIR}/scripts/download_statpearls.py" \
                --output "${DOWNLOAD_DIR}/statpearls" \
                --api-key "${NCBI_API_KEY}" \
                > "${LOG_DIR}/statpearls_restart_$(date +%Y%m%d_%H%M%S).log" 2>&1 &

            STATPEARLS_PID=$!
            echo "StatPearls PID: $STATPEARLS_PID"
            echo "$STATPEARLS_PID" > "${LOG_DIR}/statpearls.pid"
            echo -e "${GREEN}✓ StatPearls download started${NC}"
        fi

        echo -e "${GREEN}Starting Cochrane download...${NC}"
        python3 "${PROJECT_DIR}/scripts/download_cochrane_from_export.py" \
            --export-file "/home/dev/Downloads/citation-export(2).txt" \
            --output-dir "${DOWNLOAD_DIR}/cochrane" \
            > "${LOG_DIR}/cochrane_restart_$(date +%Y%m%d_%H%M%S).log" 2>&1 &

        COCHRANE_PID=$!
        echo "Cochrane PID: $COCHRANE_PID"
        echo "$COCHRANE_PID" > "${LOG_DIR}/cochrane.pid"
        echo -e "${GREEN}✓ Cochrane download started${NC}"

        echo ""
        echo -e "${GREEN}✓ Both downloads running in background${NC}"
        ;;

    4)
        echo -e "${BLUE}Current Status:${NC}"
        cat "${DOWNLOAD_DIR}/DOWNLOAD_STATUS.md" 2>/dev/null || echo "No status file found"
        exit 0
        ;;

    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo -e "${BLUE}================================================${NC}"
echo -e "${GREEN}Downloads Started Successfully${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""
echo "Monitoring commands:"
echo "  Watch progress: watch -n 10 'du -sh ${DOWNLOAD_DIR}/*'"
echo "  StatPearls log: tail -f ${LOG_DIR}/statpearls_restart_*.log"
echo "  Cochrane log: tail -f ${LOG_DIR}/cochrane_restart_*.log"
echo "  Check processes: ps aux | grep -E '(statpearls|cochrane)'"
echo ""
echo "To stop downloads:"
echo "  kill \$(cat ${LOG_DIR}/statpearls.pid) 2>/dev/null"
echo "  kill \$(cat ${LOG_DIR}/cochrane.pid) 2>/dev/null"
echo ""
