#!/bin/bash
set -e

# Auto-Advance Script for Ralph PRD Execution
# Automatically runs all 14 PRDs sequentially with minimal manual intervention

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TMUX_SESSION="ralph-irstudy-mvp"
START_TASK=${1:-1}
MAX_WAIT_HOURS=12  # Maximum hours to wait per task before timing out

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Ralph Auto-Advance Mode - irStudy MVP Phase 1${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}This will run all 14 PRDs automatically.${NC}"
echo -e "${YELLOW}Expected total time: 67-86 hours${NC}"
echo ""
echo "Starting from: Task $START_TASK"
echo "Maximum wait per task: $MAX_WAIT_HOURS hours"
echo ""
read -p "Press ENTER to start, or Ctrl+C to cancel..."

# Log file for this run
RUN_LOG="$SCRIPT_DIR/ralph_logs/auto_advance_$(date +%Y%m%d_%H%M%S).log"
mkdir -p "$SCRIPT_DIR/ralph_logs"

log() {
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] $1"
    echo -e "$msg" | tee -a "$RUN_LOG"
}

check_task_completion() {
    local task_num=$1
    local task_id=$(printf 'TASK_%03d' $task_num)

    # Check if task is marked done in @fix_plan.md
    if grep -q "$task_id.*✅ DONE" "$SCRIPT_DIR/@fix_plan.md" 2>/dev/null; then
        return 0  # Task complete
    fi

    # Check if Ralph session is still running
    if tmux has-session -t "$TMUX_SESSION" 2>/dev/null; then
        return 1  # Task still running
    fi

    # Session ended but task not marked done - check git commits
    if git log --oneline -1 | grep -q "$task_id"; then
        log "${YELLOW}Task $task_num: Ralph session ended, git commit found${NC}"
        return 0  # Consider complete if git commit exists
    fi

    log "${RED}WARNING: Task $task_num session ended without completion markers${NC}"
    return 2  # Ended without completion
}

wait_for_task() {
    local task_num=$1
    local task_name=$2
    local max_wait_seconds=$((MAX_WAIT_HOURS * 3600))
    local wait_start=$(date +%s)
    local last_status_time=$wait_start

    log "${BLUE}Waiting for $task_name to complete...${NC}"

    while true; do
        local current_time=$(date +%s)
        local elapsed=$((current_time - wait_start))

        # Check completion every 30 seconds
        check_task_completion $task_num
        local completion_status=$?

        if [ $completion_status -eq 0 ]; then
            log "${GREEN}✓ $task_name completed successfully${NC}"
            return 0
        elif [ $completion_status -eq 2 ]; then
            log "${RED}✗ $task_name ended without completion${NC}"
            log "${YELLOW}Check logs: $SCRIPT_DIR/ralph_logs/task_$(printf '%03d' $task_num)_*.log${NC}"
            return 1
        fi

        # Show status every 5 minutes
        if [ $((elapsed - (last_status_time - wait_start))) -ge 300 ]; then
            local hours=$((elapsed / 3600))
            local minutes=$(((elapsed % 3600) / 60))
            log "${YELLOW}Still running... (${hours}h ${minutes}m elapsed)${NC}"
            last_status_time=$current_time
        fi

        # Check timeout
        if [ $elapsed -ge $max_wait_seconds ]; then
            log "${RED}TIMEOUT: Task $task_num exceeded $MAX_WAIT_HOURS hours${NC}"
            log "${YELLOW}Stopping task and moving to next...${NC}"
            tmux kill-session -t "$TMUX_SESSION" 2>/dev/null || true
            return 2
        fi

        sleep 30
    done
}

run_all_tasks() {
    local total_tasks=14
    local completed=0
    local failed=0
    local start_time=$(date +%s)

    log "${GREEN}════════════════════════════════════════════════════════════════${NC}"
    log "${GREEN}  Starting Auto-Advance from Task $START_TASK${NC}"
    log "${GREEN}════════════════════════════════════════════════════════════════${NC}"

    for task_num in $(seq $START_TASK $total_tasks); do
        log ""
        log "${BLUE}[$(date '+%H:%M:%S')] Starting TASK_$(printf '%03d' $task_num) ($(($task_num - $START_TASK + 1))/$((total_tasks - $START_TASK + 1)))${NC}"

        # Start the task
        "$SCRIPT_DIR/run_ralph_prds.sh" --task $task_num >> "$RUN_LOG" 2>&1

        # Wait for completion
        if wait_for_task $task_num "TASK_$(printf '%03d' $task_num)"; then
            completed=$((completed + 1))
            log "${GREEN}✓ Task $task_num complete${NC}"
        else
            failed=$((failed + 1))
            log "${RED}✗ Task $task_num failed or timed out${NC}"

            # Prompt for continuation
            echo ""
            echo -e "${YELLOW}Task $task_num did not complete successfully.${NC}"
            echo -e "${YELLOW}Options:${NC}"
            echo "  1. Continue to next task (default)"
            echo "  2. Retry current task"
            echo "  3. Stop auto-advance"
            echo ""
            read -t 60 -p "Choice [1-3] (auto-continue in 60s): " choice || choice=1

            case $choice in
                2)
                    log "${YELLOW}Retrying Task $task_num...${NC}"
                    task_num=$((task_num - 1))  # Retry current task
                    ;;
                3)
                    log "${RED}Auto-advance stopped by user${NC}"
                    break
                    ;;
                *)
                    log "${YELLOW}Continuing to next task...${NC}"
                    ;;
            esac
        fi

        # Short delay between tasks
        sleep 10
    done

    # Summary
    local end_time=$(date +%s)
    local total_time=$((end_time - start_time))
    local hours=$((total_time / 3600))
    local minutes=$(((total_time % 3600) / 60))

    log ""
    log "${GREEN}════════════════════════════════════════════════════════════════${NC}"
    log "${GREEN}  Auto-Advance Complete${NC}"
    log "${GREEN}════════════════════════════════════════════════════════════════${NC}"
    log ""
    log "Total time: ${hours}h ${minutes}m"
    log "Tasks completed: $completed/$((total_tasks - START_TASK + 1))"
    log "Tasks failed: $failed"
    log ""
    log "Full log: $RUN_LOG"
    log ""

    if [ $completed -eq $((total_tasks - START_TASK + 1)) ]; then
        log "${GREEN}🎉 All tasks completed successfully!${NC}"
        log ""
        log "Next steps:"
        log "1. Verify all 14 commits: git log --oneline | grep TASK_"
        log "2. Run full test suite: cd backend && pytest; cd ../frontend && npm test"
        log "3. Deploy to production: Follow TASK_013 deployment checklist"
        log "4. Onboard beta users: Run scripts from TASK_014"
        return 0
    else
        log "${YELLOW}⚠️  Some tasks did not complete. Review logs for details.${NC}"
        return 1
    fi
}

# Run the auto-advance
run_all_tasks
exit_code=$?

log ""
log "Auto-advance script finished with exit code: $exit_code"
exit $exit_code
