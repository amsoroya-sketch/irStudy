#!/bin/bash
# Ralph Production Launch PRD Execution Loop
# Automated execution of production launch PRDs using Claude CLI

set -e  # Exit on error
set -u  # Exit on undefined variable

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PRD_BASE_DIR="$PROJECT_ROOT/production-launch-prds"
STATE_FILE="$PROJECT_ROOT/.ralph-production-launch-state.json"
LOG_DIR="$PRD_BASE_DIR/logs"
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')

# Create log directory
mkdir -p "$LOG_DIR"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Initialize state file if doesn't exist
if [ ! -f "$STATE_FILE" ]; then
    cat > "$STATE_FILE" <<EOF
{
  "started_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "current_phase": "phase1-frontend",
  "completed_prds": [],
  "failed_prds": [],
  "current_prd": null,
  "total_prds": 0,
  "completed_count": 0,
  "execution_order": [
    "phase1-frontend",
    "phase2-scoring",
    "phase3-studycards",
    "phase4-emr",
    "phase5-content",
    "phase6-mockexam",
    "phase7-testing",
    "phase8-integration"
  ]
}
EOF
    echo -e "${GREEN}✅ Initialized state file: $STATE_FILE${NC}"
fi

# Function to update state
update_state() {
    local field=$1
    local value=$2
    python3 -c "
import json
with open('$STATE_FILE') as f:
    state = json.load(f)
state['$field'] = $value
with open('$STATE_FILE', 'w') as f:
    json.dump(state, f, indent=2)
"
}

# Function to mark PRD as completed
mark_completed() {
    local prd_name=$1
    python3 -c "
import json
with open('$STATE_FILE') as f:
    state = json.load(f)
if '$prd_name' not in state['completed_prds']:
    state['completed_prds'].append('$prd_name')
    state['completed_count'] = len(state['completed_prds'])
with open('$STATE_FILE', 'w') as f:
    json.dump(state, f, indent=2)
"
    echo -e "${GREEN}✅ Completed: $prd_name${NC}"
}

# Function to mark PRD as failed
mark_failed() {
    local prd_name=$1
    local error_msg=$2
    python3 -c "
import json
with open('$STATE_FILE') as f:
    state = json.load(f)
state['failed_prds'].append({'prd': '$prd_name', 'error': '''$error_msg''', 'timestamp': '$(date -u +%Y-%m-%dT%H:%M:%SZ)'})
with open('$STATE_FILE', 'w') as f:
    json.dump(state, f, indent=2)
"
    echo -e "${RED}❌ Failed: $prd_name${NC}"
    echo -e "${RED}   Error: $error_msg${NC}"
}

# Function to execute a single PRD
execute_prd() {
    local prd_file=$1
    local prd_name=$(basename "$prd_file" .md)
    local log_file="$LOG_DIR/${prd_name}_${TIMESTAMP}.log"

    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}📋 Executing PRD: $prd_name${NC}"
    echo -e "${BLUE}📁 File: $prd_file${NC}"
    echo -e "${BLUE}📝 Log: $log_file${NC}"
    echo -e "${BLUE}⏰ Started: $(date '+%Y-%m-%d %H:%M:%S')${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    # Update current PRD in state
    update_state "current_prd" "\"$prd_name\""

    # Read PRD content
    if [ ! -f "$prd_file" ]; then
        mark_failed "$prd_name" "PRD file not found"
        return 1
    fi

    # Execute via Claude CLI
    echo -e "${YELLOW}🤖 Invoking Claude CLI...${NC}"

    if cat "$prd_file" | claude > "$log_file" 2>&1; then
        echo -e "${GREEN}✅ Claude CLI execution completed successfully${NC}"
        mark_completed "$prd_name"

        # Show summary from log
        echo -e "${GREEN}📊 Execution Summary:${NC}"
        tail -n 20 "$log_file" | grep -E "(✅|❌|completed|failed|error)" || echo "  (No summary available)"

        return 0
    else
        local exit_code=$?
        echo -e "${RED}❌ Claude CLI execution failed (exit code: $exit_code)${NC}"

        # Show error from log
        echo -e "${RED}📋 Error Details:${NC}"
        tail -n 30 "$log_file"

        mark_failed "$prd_name" "Claude CLI exit code $exit_code"
        return 1
    fi
}

# Function to get phase PRDs
get_phase_prds() {
    local phase=$1
    local phase_dir="$PRD_BASE_DIR/$phase"

    if [ ! -d "$phase_dir" ]; then
        echo -e "${YELLOW}⚠️  Phase directory not found: $phase_dir${NC}"
        return 1
    fi

    find "$phase_dir" -name "PRD-*.md" -type f | sort
}

# Function to display progress
show_progress() {
    python3 -c "
import json
with open('$STATE_FILE') as f:
    state = json.load(f)

total = state.get('total_prds', 0)
completed = state.get('completed_count', 0)
failed = len(state.get('failed_prds', []))

print()
print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
print('📊 PROGRESS SUMMARY')
print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
print(f'✅ Completed: {completed}/{total}')
print(f'❌ Failed: {failed}')
print(f'📋 Current Phase: {state.get(\"current_phase\", \"N/A\")}')
if state.get('current_prd'):
    print(f'🔄 Current PRD: {state[\"current_prd\"]}')
print('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
print()
"
}

# Main execution loop
main() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}🚀 Ralph Production Launch PRD Execution Loop${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}📁 PRD Directory: $PRD_BASE_DIR${NC}"
    echo -e "${BLUE}📝 State File: $STATE_FILE${NC}"
    echo -e "${BLUE}📋 Log Directory: $LOG_DIR${NC}"
    echo -e "${BLUE}⏰ Started: $(date '+%Y-%m-%d %H:%M:%S')${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo

    # Get execution order from state
    local phases=$(python3 -c "
import json
with open('$STATE_FILE') as f:
    state = json.load(f)
print(' '.join(state['execution_order']))
")

    # Count total PRDs
    local total_prds=0
    for phase in $phases; do
        local count=$(get_phase_prds "$phase" | wc -l)
        total_prds=$((total_prds + count))
    done

    update_state "total_prds" "$total_prds"

    echo -e "${GREEN}📊 Total PRDs to execute: $total_prds${NC}"
    echo

    # Execute PRDs phase by phase
    for phase in $phases; do
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${BLUE}🏗️  PHASE: $phase${NC}"
        echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo

        update_state "current_phase" "\"$phase\""

        local phase_prds=$(get_phase_prds "$phase")

        if [ -z "$phase_prds" ]; then
            echo -e "${YELLOW}⚠️  No PRDs found for phase: $phase${NC}"
            continue
        fi

        local prd_count=$(echo "$phase_prds" | wc -l)
        echo -e "${GREEN}📋 PRDs in this phase: $prd_count${NC}"
        echo

        # Execute each PRD in phase
        while IFS= read -r prd_file; do
            execute_prd "$prd_file"
            echo

            # Show progress after each PRD
            show_progress

            # Brief pause between PRDs
            sleep 2
        done <<< "$phase_prds"

        echo -e "${GREEN}✅ Phase $phase completed${NC}"
        echo
    done

    # Final summary
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}🎉 EXECUTION COMPLETE${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    show_progress

    echo -e "${GREEN}⏰ Finished: $(date '+%Y-%m-%d %H:%M:%S')${NC}"
    echo -e "${GREEN}📋 Logs available in: $LOG_DIR${NC}"
    echo
}

# Run main
main "$@"
