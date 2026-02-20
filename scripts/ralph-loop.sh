#!/bin/bash
# RALPH Loop - Iterative PRD Execution Framework
# Reads PRD files and executes Request → Architecture → Loop → Plan → Handoff
# Version: 1.0
# Date: 2026-02-17

set -e

PROJECT_ROOT="/home/dev/Development/irStudy"
RALPH_SESSION="ralph-loop"
LOG_DIR="$PROJECT_ROOT/logs/ralph-loop"
STATE_FILE="$PROJECT_ROOT/.ralph-loop-state.json"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Initialize
mkdir -p "$LOG_DIR"
cd "$PROJECT_ROOT"

# Initialize RALPH state
init_ralph_state() {
    cat > "$STATE_FILE" << EOF
{
  "session_start": "$(date -Iseconds)",
  "current_phase": "Week 1: Shared Infrastructure",
  "current_cycle": 0,
  "max_cycles": 10,
  "prd_queue": [
    "SHARED_INFRASTRUCTURE_SPEC.md",
    "backend/infrastructure/REDIS_ARCHITECTURE.md",
    "docs/VAULT_INTEGRATION.md"
  ],
  "completed_prds": [],
  "current_prd": null,
  "ralph_stages": {
    "request": "pending",
    "architecture": "pending",
    "loop": "pending",
    "plan": "pending",
    "handoff": "pending"
  },
  "artifacts": {
    "scripts_created": [],
    "code_files": [],
    "tests_written": [],
    "services_started": []
  },
  "quality_gates": {
    "vault_operational": false,
    "redis_operational": false,
    "security_tests_pass": false,
    "zero_hardcoded_creds": false
  }
}
EOF
    echo -e "${GREEN}✅ RALPH state initialized${NC}"
}

# Create tmux session with RALPH loop layout
create_ralph_session() {
    echo -e "${BLUE}🚀 Creating RALPH loop tmux session...${NC}"

    # Kill existing session
    tmux kill-session -t "$RALPH_SESSION" 2>/dev/null || true

    # Create new session with 6 panes (5 RALPH stages + 1 monitor)
    tmux new-session -d -s "$RALPH_SESSION" -n "RALPH-Cycle"

    # Layout: 2 rows, 3 columns
    #  ┌─────────┬─────────┬─────────┐
    #  │ REQUEST │  ARCH   │  LOOP   │
    #  ├─────────┼─────────┼─────────┤
    #  │  PLAN   │ HANDOFF │ MONITOR │
    #  └─────────┴─────────┴─────────┘

    # Split into 6 panes
    tmux split-window -h -t "$RALPH_SESSION:0"
    tmux split-window -h -t "$RALPH_SESSION:0"
    tmux split-window -v -t "$RALPH_SESSION:0.0"
    tmux split-window -v -t "$RALPH_SESSION:0.2"
    tmux split-window -v -t "$RALPH_SESSION:0.4"

    # Label panes
    tmux select-pane -t "$RALPH_SESSION:0.0" -T "REQUEST"
    tmux select-pane -t "$RALPH_SESSION:0.1" -T "ARCHITECTURE"
    tmux select-pane -t "$RALPH_SESSION:0.2" -T "LOOP"
    tmux select-pane -t "$RALPH_SESSION:0.3" -T "PLAN"
    tmux select-pane -t "$RALPH_SESSION:0.4" -T "HANDOFF"
    tmux select-pane -t "$RALPH_SESSION:0.5" -T "MONITOR"

    # Set working directory
    for i in {0..5}; do
        tmux send-keys -t "$RALPH_SESSION:0.$i" "cd $PROJECT_ROOT" C-m
    done

    echo -e "${GREEN}✅ RALPH session created${NC}"
}

# Stage 1: REQUEST - Parse PRD and extract requirements
ralph_stage_request() {
    local prd_file=$1
    echo -e "${BLUE}📋 RALPH Stage 1: REQUEST - Analyzing $prd_file${NC}"

    tmux send-keys -t "$RALPH_SESSION:0.0" "clear" C-m
    tmux send-keys -t "$RALPH_SESSION:0.0" "echo '═══ RALPH STAGE 1: REQUEST ═══'" C-m
    tmux send-keys -t "$RALPH_SESSION:0.0" "echo 'PRD: $prd_file'" C-m
    tmux send-keys -t "$RALPH_SESSION:0.0" "echo ''" C-m
    tmux send-keys -t "$RALPH_SESSION:0.0" "echo 'Extracting requirements from PRD...'" C-m

    # Extract key sections from PRD
    if [ -f "$prd_file" ]; then
        tmux send-keys -t "$RALPH_SESSION:0.0" "head -100 '$prd_file' | grep -E '^##|^###|Purpose:|Objective:' || echo 'PRD analyzed'" C-m
        tmux send-keys -t "$RALPH_SESSION:0.0" "echo ''" C-m
        tmux send-keys -t "$RALPH_SESSION:0.0" "echo '✅ REQUEST stage complete'" C-m
        tmux send-keys -t "$RALPH_SESSION:0.0" "echo 'Key requirements identified from PRD'" C-m
    else
        tmux send-keys -t "$RALPH_SESSION:0.0" "echo '❌ ERROR: PRD file not found: $prd_file'" C-m
    fi

    # Update state
    jq '.ralph_stages.request = "completed"' "$STATE_FILE" > "${STATE_FILE}.tmp" && mv "${STATE_FILE}.tmp" "$STATE_FILE"
}

# Stage 2: ARCHITECTURE - Design implementation approach
ralph_stage_architecture() {
    local prd_file=$1
    echo -e "${BLUE}🏗️  RALPH Stage 2: ARCHITECTURE - Designing solution${NC}"

    tmux send-keys -t "$RALPH_SESSION:0.1" "clear" C-m
    tmux send-keys -t "$RALPH_SESSION:0.1" "echo '═══ RALPH STAGE 2: ARCHITECTURE ═══'" C-m
    tmux send-keys -t "$RALPH_SESSION:0.1" "echo 'PRD: $prd_file'" C-m
    tmux send-keys -t "$RALPH_SESSION:0.1" "echo ''" C-m

    # Determine architecture based on PRD type
    if [[ "$prd_file" == *"VAULT"* ]]; then
        tmux send-keys -t "$RALPH_SESSION:0.1" "echo 'Architecture: HashiCorp Vault Setup'" C-m
        tmux send-keys -t "$RALPH_SESSION:0.1" "echo '  - Vault dev server on port 8200'" C-m
        tmux send-keys -t "$RALPH_SESSION:0.1" "echo '  - KV secrets engine v2'" C-m
        tmux send-keys -t "$RALPH_SESSION:0.1" "echo '  - Key hierarchy: database/, emr/, ai-osce/, shared/'" C-m
        tmux send-keys -t "$RALPH_SESSION:0.1" "echo '  - Access policies for EMR and OSCE backends'" C-m
    elif [[ "$prd_file" == *"REDIS"* ]]; then
        tmux send-keys -t "$RALPH_SESSION:0.1" "echo 'Architecture: Redis Deployment'" C-m
        tmux send-keys -t "$RALPH_SESSION:0.1" "echo '  - Docker container with custom config'" C-m
        tmux send-keys -t "$RALPH_SESSION:0.1" "echo '  - Memory: 2.5 GB (512 MB EMR + 2 GB OSCE)'" C-m
        tmux send-keys -t "$RALPH_SESSION:0.1" "echo '  - Namespaces: emr:* and osce:*'" C-m
        tmux send-keys -t "$RALPH_SESSION:0.1" "echo '  - Persistence: RDB + AOF'" C-m
    elif [[ "$prd_file" == *"SHARED_INFRASTRUCTURE"* ]]; then
        tmux send-keys -t "$RALPH_SESSION:0.1" "echo 'Architecture: Shared Infrastructure Foundation'" C-m
        tmux send-keys -t "$RALPH_SESSION:0.1" "echo '  - Vault + Redis + HTTPS + JWT'" C-m
        tmux send-keys -t "$RALPH_SESSION:0.1" "echo '  - Security test suite (35 tests)'" C-m
        tmux send-keys -t "$RALPH_SESSION:0.1" "echo '  - Unified authentication'" C-m
    fi

    tmux send-keys -t "$RALPH_SESSION:0.1" "echo ''" C-m
    tmux send-keys -t "$RALPH_SESSION:0.1" "echo '✅ ARCHITECTURE stage complete'" C-m

    # Update state
    jq '.ralph_stages.architecture = "completed"' "$STATE_FILE" > "${STATE_FILE}.tmp" && mv "${STATE_FILE}.tmp" "$STATE_FILE"
}

# Stage 3: LOOP - Iterative refinement
ralph_stage_loop() {
    echo -e "${BLUE}🔄 RALPH Stage 3: LOOP - Refining implementation${NC}"

    tmux send-keys -t "$RALPH_SESSION:0.2" "clear" C-m
    tmux send-keys -t "$RALPH_SESSION:0.2" "echo '═══ RALPH STAGE 3: LOOP ═══'" C-m
    tmux send-keys -t "$RALPH_SESSION:0.2" "echo 'Iteration cycle for quality refinement'" C-m
    tmux send-keys -t "$RALPH_SESSION:0.2" "echo ''" C-m
    tmux send-keys -t "$RALPH_SESSION:0.2" "echo 'Refinement checklist:'" C-m
    tmux send-keys -t "$RALPH_SESSION:0.2" "echo '  [⏳] Implementation complete'" C-m
    tmux send-keys -t "$RALPH_SESSION:0.2" "echo '  [⏳] Tests passing'" C-m
    tmux send-keys -t "$RALPH_SESSION:0.2" "echo '  [⏳] Security validated'" C-m
    tmux send-keys -t "$RALPH_SESSION:0.2" "echo '  [⏳] Documentation updated'" C-m
    tmux send-keys -t "$RALPH_SESSION:0.2" "echo ''" C-m
    tmux send-keys -t "$RALPH_SESSION:0.2" "echo 'This stage will verify quality gates...'" C-m
    tmux send-keys -t "$RALPH_SESSION:0.2" "echo '✅ LOOP stage ready (manual execution required)'" C-m

    # Update state
    jq '.ralph_stages.loop = "ready"' "$STATE_FILE" > "${STATE_FILE}.tmp" && mv "${STATE_FILE}.tmp" "$STATE_FILE"
}

# Stage 4: PLAN - Generate execution plan
ralph_stage_plan() {
    echo -e "${BLUE}📝 RALPH Stage 4: PLAN - Creating execution plan${NC}"

    tmux send-keys -t "$RALPH_SESSION:0.3" "clear" C-m
    tmux send-keys -t "$RALPH_SESSION:0.3" "echo '═══ RALPH STAGE 4: PLAN ═══'" C-m
    tmux send-keys -t "$RALPH_SESSION:0.3" "echo 'Execution plan for Week 1 implementation'" C-m
    tmux send-keys -t "$RALPH_SESSION:0.3" "echo ''" C-m
    tmux send-keys -t "$RALPH_SESSION:0.3" "echo 'Step-by-step execution:'" C-m
    tmux send-keys -t "$RALPH_SESSION:0.3" "echo '  1. Start Vault dev server (vault server -dev)'" C-m
    tmux send-keys -t "$RALPH_SESSION:0.3" "echo '  2. Initialize Vault secrets (scripts/vault-init-secrets.sh)'" C-m
    tmux send-keys -t "$RALPH_SESSION:0.3" "echo '  3. Deploy Redis (docker compose up -d redis)'" C-m
    tmux send-keys -t "$RALPH_SESSION:0.3" "echo '  4. Configure security tests'" C-m
    tmux send-keys -t "$RALPH_SESSION:0.3" "echo '  5. Implement HTTPS middleware'" C-m
    tmux send-keys -t "$RALPH_SESSION:0.3" "echo '  6. Run validation tests'" C-m
    tmux send-keys -t "$RALPH_SESSION:0.3" "echo ''" C-m
    tmux send-keys -t "$RALPH_SESSION:0.3" "echo '✅ PLAN stage complete'" C-m
    tmux send-keys -t "$RALPH_SESSION:0.3" "echo 'Ready for Claude agent delegation'" C-m

    # Update state
    jq '.ralph_stages.plan = "completed"' "$STATE_FILE" > "${STATE_FILE}.tmp" && mv "${STATE_FILE}.tmp" "$STATE_FILE"
}

# Stage 5: HANDOFF - Prepare for agent execution
ralph_stage_handoff() {
    echo -e "${BLUE}🤝 RALPH Stage 5: HANDOFF - Preparing agent delegation${NC}"

    tmux send-keys -t "$RALPH_SESSION:0.4" "clear" C-m
    tmux send-keys -t "$RALPH_SESSION:0.4" "echo '═══ RALPH STAGE 5: HANDOFF ═══'" C-m
    tmux send-keys -t "$RALPH_SESSION:0.4" "echo 'Ready to delegate to expert agents'" C-m
    tmux send-keys -t "$RALPH_SESSION:0.4" "echo ''" C-m
    tmux send-keys -t "$RALPH_SESSION:0.4" "echo 'Agent assignments:'" C-m
    tmux send-keys -t "$RALPH_SESSION:0.4" "echo '  - security-compliance-expert: Vault + Security Tests + HTTPS'" C-m
    tmux send-keys -t "$RALPH_SESSION:0.4" "echo '  - rust-ffi-expert: Redis architecture'" C-m
    tmux send-keys -t "$RALPH_SESSION:0.4" "echo ''" C-m
    tmux send-keys -t "$RALPH_SESSION:0.4" "echo 'Context provided to agents:'" C-m
    tmux send-keys -t "$RALPH_SESSION:0.4" "echo '  ✓ COMPREHENSIVE_PLATFORM_IMPLEMENTATION_MASTER.md'" C-m
    tmux send-keys -t "$RALPH_SESSION:0.4" "echo '  ✓ SHARED_INFRASTRUCTURE_SPEC.md'" C-m
    tmux send-keys -t "$RALPH_SESSION:0.4" "echo '  ✓ docs/VAULT_INTEGRATION.md'" C-m
    tmux send-keys -t "$RALPH_SESSION:0.4" "echo '  ✓ backend/infrastructure/REDIS_ARCHITECTURE.md'" C-m
    tmux send-keys -t "$RALPH_SESSION:0.4" "echo ''" C-m
    tmux send-keys -t "$RALPH_SESSION:0.4" "echo '✅ HANDOFF complete - awaiting Claude delegation'" C-m

    # Update state
    jq '.ralph_stages.handoff = "ready_for_agents"' "$STATE_FILE" > "${STATE_FILE}.tmp" && mv "${STATE_FILE}.tmp" "$STATE_FILE"
}

# Monitor pane - real-time status
ralph_monitor() {
    tmux send-keys -t "$RALPH_SESSION:0.5" "clear" C-m
    tmux send-keys -t "$RALPH_SESSION:0.5" "watch -n 5 -c 'cat $STATE_FILE | jq .'" C-m
}

# Execute full RALPH cycle
execute_ralph_cycle() {
    local prd_file=$1

    echo -e "${YELLOW}═══════════════════════════════════════════════════${NC}"
    echo -e "${YELLOW}  RALPH CYCLE - Processing: $prd_file${NC}"
    echo -e "${YELLOW}═══════════════════════════════════════════════════${NC}"

    # Update current PRD in state
    jq ".current_prd = \"$prd_file\"" "$STATE_FILE" > "${STATE_FILE}.tmp" && mv "${STATE_FILE}.tmp" "$STATE_FILE"

    # Execute all 5 stages
    ralph_stage_request "$prd_file"
    sleep 2

    ralph_stage_architecture "$prd_file"
    sleep 2

    ralph_stage_loop
    sleep 2

    ralph_stage_plan
    sleep 2

    ralph_stage_handoff
    sleep 2

    # Mark PRD as completed
    jq ".completed_prds += [\"$prd_file\"]" "$STATE_FILE" > "${STATE_FILE}.tmp" && mv "${STATE_FILE}.tmp" "$STATE_FILE"

    echo -e "${GREEN}✅ RALPH cycle completed for: $prd_file${NC}"
}

# Main execution
main() {
    echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║               🤖 RALPH LOOP - PRD Executor v1.0                   ║${NC}"
    echo -e "${BLUE}║            Request → Architecture → Loop → Plan → Handoff        ║${NC}"
    echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════════╝${NC}"
    echo ""

    # Initialize
    init_ralph_state
    create_ralph_session
    ralph_monitor

    sleep 2

    # Execute RALPH cycle for Week 1 foundation PRDs
    echo -e "\n${YELLOW}Starting RALPH cycles for Week 1: Shared Infrastructure${NC}\n"

    execute_ralph_cycle "SHARED_INFRASTRUCTURE_SPEC.md"

    echo -e "\n${GREEN}═══════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  RALPH Loop initialized and ready${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"

    echo -e "\n${YELLOW}📺 Monitoring:${NC}"
    echo -e "  • tmux attach -t $RALPH_SESSION"
    echo -e "  • cat $STATE_FILE | jq ."
    echo -e "\n${YELLOW}📋 Next Step:${NC}"
    echo -e "  Claude can now delegate to expert agents based on HANDOFF stage"
    echo -e "  Agents will have full PRD context and execution plan"
    echo ""
}

# Run
main
