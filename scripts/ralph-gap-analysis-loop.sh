#!/bin/bash

# Ralph Loop Script - Gap Analysis Implementation
# Created: 2026-03-13
# Purpose: Systematically implement all gap analysis PRDs

set -euo pipefail

# Configuration
PROJECT_ROOT="/home/dev/Development/irStudy"
PRD_DIR="$PROJECT_ROOT/gap-analysis-prds"
STATE_FILE="$PROJECT_ROOT/.ralph-gap-analysis-state.json"
LOG_DIR="$PROJECT_ROOT/logs"
LOG_FILE="$LOG_DIR/ralph-gap-analysis-$(date +%Y%m%d_%H%M%S).log"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Create log directory
mkdir -p "$LOG_DIR"

# Logging function
log() {
    echo -e "${2:-$NC}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}" | tee -a "$LOG_FILE"
}

log_success() { log "$1" "$GREEN"; }
log_error() { log "$1" "$RED"; }
log_warning() { log "$1" "$YELLOW"; }
log_info() { log "$1" "$BLUE"; }

# Initialize state file if not exists
initialize_state() {
    if [ ! -f "$STATE_FILE" ]; then
        log_info "Creating initial state file..."
        cat > "$STATE_FILE" <<EOF
{
  "version": "1.0",
  "created": "$(date -Iseconds)",
  "phase": "phase1-p0-blockers",
  "current_prd": "PRD_GAP_001",
  "completed_prds": [],
  "current_cycle": 0,
  "max_cycles": 30,
  "quality_gates": {
    "test_pass_rate": 1.0,
    "code_coverage": 0.7,
    "security_violations": 0,
    "build_errors": 0
  },
  "phases": {
    "phase1-p0-blockers": {
      "status": "in_progress",
      "prds": ["PRD_GAP_001", "PRD_GAP_002", "PRD_GAP_003", "PRD_GAP_004"],
      "completed": []
    },
    "phase2-core-functionality": {
      "status": "pending",
      "prds": ["PRD_GAP_005", "PRD_GAP_006", "PRD_GAP_007", "PRD_GAP_008"],
      "completed": []
    },
    "phase3-production-readiness": {
      "status": "pending",
      "prds": ["PRD_GAP_009", "PRD_GAP_010", "PRD_GAP_011"],
      "completed": []
    },
    "phase4-deployment": {
      "status": "pending",
      "prds": ["PRD_GAP_012"],
      "completed": []
    }
  }
}
EOF
        log_success "State file created: $STATE_FILE"
    fi
}

# Get current phase and PRD from state
get_current_state() {
    PHASE=$(jq -r '.phase' "$STATE_FILE")
    CURRENT_PRD=$(jq -r '.current_prd' "$STATE_FILE")
    CURRENT_CYCLE=$(jq -r '.current_cycle' "$STATE_FILE")
    MAX_CYCLES=$(jq -r '.max_cycles' "$STATE_FILE")

    log_info "Current State: Phase=$PHASE, PRD=$CURRENT_PRD, Cycle=$CURRENT_CYCLE/$MAX_CYCLES"
}

# Update state file
update_state() {
    local field=$1
    local value=$2

    jq --arg field "$field" --arg value "$value" '.[$field] = $value' "$STATE_FILE" > "${STATE_FILE}.tmp"
    mv "${STATE_FILE}.tmp" "$STATE_FILE"

    log_info "State updated: $field = $value"
}

# Mark PRD as complete
mark_prd_complete() {
    local prd=$1
    local phase=$2

    # Add to completed array
    jq --arg prd "$prd" --arg phase "$phase" \
       '.phases[$phase].completed += [$prd] | .completed_prds += [$prd]' \
       "$STATE_FILE" > "${STATE_FILE}.tmp"
    mv "${STATE_FILE}.tmp" "$STATE_FILE"

    log_success "✅ PRD $prd marked complete in $phase"
}

# Get next PRD to execute
get_next_prd() {
    local phase=$1
    local completed=$(jq -r ".phases[\"$phase\"].completed[]" "$STATE_FILE" 2>/dev/null || echo "")
    local all_prds=$(jq -r ".phases[\"$phase\"].prds[]" "$STATE_FILE")

    for prd in $all_prds; do
        if ! echo "$completed" | grep -q "^$prd$"; then
            echo "$prd"
            return 0
        fi
    done

    # All PRDs in phase complete
    echo "PHASE_COMPLETE"
}

# Move to next phase
next_phase() {
    local current_phase=$1

    case "$current_phase" in
        "phase1-p0-blockers")
            echo "phase2-core-functionality"
            ;;
        "phase2-core-functionality")
            echo "phase3-production-readiness"
            ;;
        "phase3-production-readiness")
            echo "phase4-deployment"
            ;;
        "phase4-deployment")
            echo "COMPLETE"
            ;;
        *)
            echo "UNKNOWN"
            ;;
    esac
}

# Run quality gates
run_quality_gates() {
    log_info "Running quality gates..."

    local pass=true

    # 1. Test pass rate
    log_info "Checking test pass rate..."
    cd "$PROJECT_ROOT/backend"
    if [ -d "venv" ]; then
        source venv/bin/activate
        TEST_OUTPUT=$(pytest --tb=short -q 2>&1 || true)
        PASSED=$(echo "$TEST_OUTPUT" | grep -oP '\d+(?= passed)' || echo "0")
        FAILED=$(echo "$TEST_OUTPUT" | grep -oP '\d+(?= failed)' || echo "0")

        if [ "$FAILED" -gt 0 ]; then
            log_error "❌ Test failures detected: $FAILED failed"
            pass=false
        else
            log_success "✅ All tests passing ($PASSED passed)"
        fi
    fi

    # 2. Build errors
    log_info "Checking frontend build..."
    cd "$PROJECT_ROOT/frontend"
    if BUILD_OUTPUT=$(npm run build 2>&1); then
        log_success "✅ Frontend builds successfully"
    else
        log_error "❌ Frontend build failed"
        echo "$BUILD_OUTPUT" | tail -20
        pass=false
    fi

    # 3. Security violations
    log_info "Checking security violations..."
    cd "$PROJECT_ROOT"
    VIOLATIONS=$(grep -rn "sk-ant-\|password\s*=\s*['\"]" backend/src/ frontend/src/ 2>/dev/null | wc -l || echo "0")

    if [ "$VIOLATIONS" -gt 0 ]; then
        log_error "❌ Security violations detected: $VIOLATIONS"
        pass=false
    else
        log_success "✅ No security violations"
    fi

    # 4. Vault/Redis operational (if Phase 1 complete)
    local phase_1_complete=$(jq -r '.phases["phase1-p0-blockers"].status' "$STATE_FILE")
    if [ "$phase_1_complete" = "complete" ]; then
        log_info "Checking Vault status..."
        if vault status >/dev/null 2>&1; then
            log_success "✅ Vault operational"
        else
            log_warning "⚠️  Vault not operational"
        fi

        log_info "Checking Redis status..."
        if redis-cli -p 6380 PING >/dev/null 2>&1; then
            log_success "✅ Redis operational"
        else
            log_warning "⚠️  Redis not operational"
        fi
    fi

    if [ "$pass" = true ]; then
        log_success "✅ All quality gates PASSED"
        return 0
    else
        log_error "❌ Quality gates FAILED"
        return 1
    fi
}

# Execute single PRD with Claude Code
execute_prd() {
    local prd=$1
    local phase=$2
    local prd_file="$PRD_DIR/$phase/${prd}.md"

    log_info "=========================================="
    log_info "Executing PRD: $prd"
    log_info "Phase: $phase"
    log_info "PRD File: $prd_file"
    log_info "=========================================="

    if [ ! -f "$prd_file" ]; then
        log_error "PRD file not found: $prd_file"
        return 1
    fi

    # Read PRD content
    PRD_CONTENT=$(cat "$prd_file")

    # Create Claude Code prompt
    PROMPT="You are implementing a Product Requirements Document (PRD) as part of the irStudy platform gap analysis.

**CURRENT PRD**: $prd
**PHASE**: $phase
**PRD FILE**: $prd_file

**INSTRUCTIONS**:
1. Read the PRD file completely (path: $prd_file)
2. Read PROJECT_CONSTRAINTS.md from constraints/ folder
3. Implement ALL tasks in the PRD in order
4. Run ALL tests after each task
5. Verify ALL acceptance criteria before marking complete
6. Use Vault for all secrets (no hardcoded credentials)
7. Write tests for ALL new code

**QUALITY GATES (MUST PASS)**:
- Test pass rate: 100%
- Build errors: 0
- Security violations: 0
- All performance targets met

**RETURN**:
- Summary of work completed
- Test results (pass/fail counts)
- Any blockers encountered
- Status: COMPLETE or IN_PROGRESS

**START IMPLEMENTATION NOW**"

    log_info "Sending prompt to Claude Code..."
    echo "$PROMPT"

    log_warning "⏸️  PAUSED - Manual execution required"
    log_info "Claude Code will execute the PRD implementation."
    log_info "Press ENTER when PRD is complete to continue..."

    # Wait for user confirmation
    read -r

    # Ask user if PRD is complete
    echo ""
    read -p "Is PRD $prd COMPLETE? (yes/no): " answer

    if [ "$answer" = "yes" ]; then
        mark_prd_complete "$prd" "$phase"

        # Run quality gates
        if run_quality_gates; then
            log_success "✅ PRD $prd completed successfully"
            return 0
        else
            log_error "❌ Quality gates failed for PRD $prd"
            return 1
        fi
    else
        log_warning "PRD $prd marked as IN_PROGRESS"
        return 1
    fi
}

# Main loop
main_loop() {
    log_info "=========================================="
    log_info "RALPH GAP ANALYSIS LOOP STARTED"
    log_info "=========================================="
    log_info "Project: irStudy Medical Education Platform"
    log_info "Purpose: Implement gap analysis PRDs systematically"
    log_info "Log File: $LOG_FILE"
    log_info ""

    initialize_state

    while true; do
        get_current_state

        # Check cycle limit
        if [ "$CURRENT_CYCLE" -ge "$MAX_CYCLES" ]; then
            log_error "Max cycles ($MAX_CYCLES) reached. Exiting."
            break
        fi

        # Increment cycle
        CURRENT_CYCLE=$((CURRENT_CYCLE + 1))
        update_state "current_cycle" "$CURRENT_CYCLE"

        log_info "=========================================="
        log_info "CYCLE $CURRENT_CYCLE / $MAX_CYCLES"
        log_info "=========================================="

        # Get next PRD
        NEXT_PRD=$(get_next_prd "$PHASE")

        if [ "$NEXT_PRD" = "PHASE_COMPLETE" ]; then
            log_success "✅ Phase $PHASE complete!"

            # Update phase status
            jq --arg phase "$PHASE" '.phases[$phase].status = "complete"' "$STATE_FILE" > "${STATE_FILE}.tmp"
            mv "${STATE_FILE}.tmp" "$STATE_FILE"

            # Move to next phase
            NEXT_PHASE=$(next_phase "$PHASE")

            if [ "$NEXT_PHASE" = "COMPLETE" ]; then
                log_success "🎉 ALL PHASES COMPLETE! 🎉"
                log_success "Gap analysis implementation finished."
                break
            elif [ "$NEXT_PHASE" = "UNKNOWN" ]; then
                log_error "Unknown phase transition from $PHASE"
                break
            else
                log_info "Moving to next phase: $NEXT_PHASE"
                update_state "phase" "$NEXT_PHASE"
                PHASE="$NEXT_PHASE"

                # Get first PRD of new phase
                NEXT_PRD=$(get_next_prd "$PHASE")
                update_state "current_prd" "$NEXT_PRD"
            fi
        else
            # Execute PRD
            update_state "current_prd" "$NEXT_PRD"

            if execute_prd "$NEXT_PRD" "$PHASE"; then
                log_success "PRD $NEXT_PRD completed"
            else
                log_warning "PRD $NEXT_PRD not complete, will retry in next cycle"
            fi
        fi

        log_info ""
        log_info "Cycle $CURRENT_CYCLE complete. Sleeping 5 seconds..."
        sleep 5
    done

    log_info "=========================================="
    log_info "RALPH GAP ANALYSIS LOOP ENDED"
    log_info "=========================================="
    log_info "Final state saved to: $STATE_FILE"
    log_info "Logs saved to: $LOG_FILE"
}

# Start main loop
main_loop
