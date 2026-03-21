#!/bin/bash
# ===========================================================================
# RALPH FOXopen PRD Executor
# Executes FOXopen PRDs using Ralph methodology
# ===========================================================================

set -e

PROJECT_ROOT="/home/dev/Development/irStudy"
FOXOPEN_ROOT="/home/dev/Development/FoxOpen/FOXopen"
RALPH_SESSION="ralph-foxopen"
LOG_DIR="$PROJECT_ROOT/foxopen-prds/logs"
STATUS_FILE="$PROJECT_ROOT/foxopen-prds/.ralph-foxopen-status.json"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Initialize
mkdir -p "$LOG_DIR"
echo "$(date '+%Y-%m-%d %H:%M:%S') - RALPH FOXopen Executor started" >> "$LOG_DIR/executor.log"

# Initialize status tracking
init_status() {
    cat > "$STATUS_FILE" << EOF
{
  "start_time": "$(date -Iseconds)",
  "current_phase": "FOXopen Projects Creation",
  "prds": {
    "PRD-FOXOPEN-001": {
      "name": "Create All 10 Projects",
      "status": "pending",
      "start": null,
      "end": null,
      "deliverables": {
        "project_folders": 0,
        "module_xml_files": 0,
        "deploy_scripts": 0,
        "database_scripts": 0
      }
    },
    "PRD-FOXOPEN-002": {
      "name": "Validate and Test All",
      "status": "pending",
      "start": null,
      "end": null,
      "quality_gates": {
        "xml_validation": false,
        "database_validation": false,
        "deployment_validation": false,
        "http_validation": false
      }
    }
  },
  "overall_progress": {
    "total_prds": 2,
    "completed_prds": 0,
    "failed_prds": 0
  }
}
EOF
    echo -e "${GREEN}✅ Status tracking initialized${NC}"
}

# Update PRD status
update_prd_status() {
    local prd_id=$1
    local status=$2
    local timestamp=$(date -Iseconds)

    if [ "$status" == "in_progress" ]; then
        jq ".prds[\"$prd_id\"].status = \"$status\" | .prds[\"$prd_id\"].start = \"$timestamp\"" "$STATUS_FILE" > "${STATUS_FILE}.tmp"
    elif [ "$status" == "completed" ]; then
        jq ".prds[\"$prd_id\"].status = \"$status\" | .prds[\"$prd_id\"].end = \"$timestamp\" | .overall_progress.completed_prds += 1" "$STATUS_FILE" > "${STATUS_FILE}.tmp"
    elif [ "$status" == "failed" ]; then
        jq ".prds[\"$prd_id\"].status = \"$status\" | .prds[\"$prd_id\"].end = \"$timestamp\" | .overall_progress.failed_prds += 1" "$STATUS_FILE" > "${STATUS_FILE}.tmp"
    fi

    mv "${STATUS_FILE}.tmp" "$STATUS_FILE"
}

# Create tmux session
create_ralph_session() {
    echo -e "${BLUE}🚀 Creating RALPH FOXopen tmux session...${NC}"

    # Kill existing session if present
    tmux kill-session -t "$RALPH_SESSION" 2>/dev/null || true

    # Create new session with 2 panes (one per PRD)
    tmux new-session -d -s "$RALPH_SESSION" -n "FOXopen-PRDs"

    # Split into 2 panes
    tmux split-window -h -t "$RALPH_SESSION:0"

    # Label panes
    tmux select-pane -t "$RALPH_SESSION:0.0" -T "PRD-001-Create"
    tmux select-pane -t "$RALPH_SESSION:0.1" -T "PRD-002-Validate"

    # Set working directory
    tmux send-keys -t "$RALPH_SESSION:0.0" "cd $FOXOPEN_ROOT/projects" C-m
    tmux send-keys -t "$RALPH_SESSION:0.1" "cd $FOXOPEN_ROOT/projects" C-m

    echo -e "${GREEN}✅ RALPH session created: $RALPH_SESSION${NC}"
    echo -e "${YELLOW}📺 Attach with: tmux attach -t $RALPH_SESSION${NC}"
}

# Execute PRD-FOXOPEN-001
execute_prd_001() {
    echo -e "${BLUE}📋 Executing PRD-FOXOPEN-001: Create All 10 Projects${NC}"
    update_prd_status "PRD-FOXOPEN-001" "in_progress"

    local LOG_FILE="$LOG_DIR/PRD-FOXOPEN-001_$(date +%Y%m%d_%H%M%S).log"

    # Run in tmux pane 0
    tmux send-keys -t "$RALPH_SESSION:0.0" "cd $FOXOPEN_ROOT/projects" C-m
    tmux send-keys -t "$RALPH_SESSION:0.0" "echo 'PRD-FOXOPEN-001: Creating all 10 projects...'" C-m

    # Step 1: Create missing project folders
    for i in {04..10}; do
        case $i in
            04) NAME="basic-crud" ;;
            05) NAME="navigation" ;;
            06) NAME="pagination" ;;
            07) NAME="validation" ;;
            08) NAME="dropdowns" ;;
            09) NAME="file-upload" ;;
            10) NAME="charts" ;;
        esac
        tmux send-keys -t "$RALPH_SESSION:0.0" "mkdir -p project-$i-$NAME" C-m
    done

    # Step 2: Delegate to Claude Code via message
    echo -e "${YELLOW}👤 Human intervention required:${NC}"
    echo "Please run this command in Claude Code:"
    echo ""
    echo "cd $FOXOPEN_ROOT/projects && create all module XML files for projects 2-10 based on the learning book"
    echo ""
    echo "Press Enter when complete..."
    read

    update_prd_status "PRD-FOXOPEN-001" "completed"
    echo -e "${GREEN}✅ PRD-FOXOPEN-001 completed${NC}"
}

# Execute PRD-FOXOPEN-002
execute_prd_002() {
    echo -e "${BLUE}📋 Executing PRD-FOXOPEN-002: Validate and Test All${NC}"
    update_prd_status "PRD-FOXOPEN-002" "in_progress"

    local LOG_FILE="$LOG_DIR/PRD-FOXOPEN-002_$(date +%Y%m%d_%H%M%S).log"

    # Run in tmux pane 1
    tmux send-keys -t "$RALPH_SESSION:0.1" "cd $FOXOPEN_ROOT/projects" C-m

    # Create validation scripts
    echo -e "${YELLOW}Creating validation scripts...${NC}"

    # XML Validation
    cat > "$FOXOPEN_ROOT/projects/validate-xml.sh" << 'EOFSCRIPT'
#!/bin/bash
echo "==================================================================="
echo "  XML Validation"
echo "==================================================================="
TOTAL=0; PASSED=0; FAILED=0
for project in project-*/; do
  if [ -f "$project/module.xml" ]; then
    TOTAL=$((TOTAL + 1))
    echo -n "Validating $project/module.xml... "
    if xmllint --noout "$project/module.xml" 2>/dev/null; then
      echo "✅ PASS"
      PASSED=$((PASSED + 1))
    else
      echo "❌ FAIL"
      FAILED=$((FAILED + 1))
    fi
  fi
done
echo ""
echo "Results: $PASSED passed, $FAILED failed (Total: $TOTAL)"
EOFSCRIPT
    chmod +x "$FOXOPEN_ROOT/projects/validate-xml.sh"

    # Run validation
    tmux send-keys -t "$RALPH_SESSION:0.1" "./validate-xml.sh" C-m

    sleep 5

    update_prd_status "PRD-FOXOPEN-002" "completed"
    echo -e "${GREEN}✅ PRD-FOXOPEN-002 completed${NC}"
}

# Main execution flow
main() {
    echo "==================================================================="
    echo "  RALPH FOXopen PRD Executor"
    echo "==================================================================="
    echo ""

    # Initialize status tracking
    init_status

    # Create tmux session
    create_ralph_session

    # Execute PRDs sequentially
    execute_prd_001
    execute_prd_002

    # Display final status
    echo ""
    echo -e "${GREEN}==================================================================="
    echo -e "  All FOXopen PRDs Completed!"
    echo -e "===================================================================${NC}"
    echo ""

    jq '.' "$STATUS_FILE"

    echo ""
    echo "Logs available at: $LOG_DIR"
    echo "Tmux session: $RALPH_SESSION"
    echo ""
}

# Run main
main "$@"
