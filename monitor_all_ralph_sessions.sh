#!/bin/bash

# Multi-Session Ralph Monitor
# Shows status of all concurrent Ralph PRD executions

PROJECT_ROOT="/home/dev/Development/irStudy"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Session definitions (must match launch script)
declare -A SESSIONS=(
    ["ralph-main"]=".|Main Project (Phase 1 MVP)"
    ["ralph-emr"]="emr-practice-system/emr-ralph-project|EMR PRD Refinement"
    ["ralph-backend"]="backend-features-15-feb|Backend Monitoring"
)

clear

while true; do
    clear
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║               🤖 MULTI-SESSION RALPH MONITOR                          ║${NC}"
    echo -e "${BLUE}║                  irStudy Platform PRD Execution                       ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${CYAN}$(date '+%Y-%m-%d %H:%M:%S')${NC} | Refresh: 5s | Press Ctrl+C to exit"
    echo ""

    active_count=0
    total_loops=0

    for session_name in "${!SESSIONS[@]}"; do
        IFS='|' read -r project_dir description <<< "${SESSIONS[$session_name]}"

        echo -e "${PURPLE}┌─ $session_name ─────────────────────────────────────────────────────────┐${NC}"

        # Check if session exists
        if tmux has-session -t "$session_name" 2>/dev/null; then
            active_count=$((active_count + 1))
            echo -e "${PURPLE}│${NC} ${GREEN}● ACTIVE${NC}"

            # Try to read status.json from project directory
            status_file="$PROJECT_ROOT/$project_dir/status.json"

            if [ -f "$status_file" ]; then
                # Parse JSON status
                loop_count=$(jq -r '.loop_count // "0"' "$status_file" 2>/dev/null)
                calls_made=$(jq -r '.calls_made_this_hour // "0"' "$status_file" 2>/dev/null)
                max_calls=$(jq -r '.max_calls_per_hour // "50"' "$status_file" 2>/dev/null)
                status=$(jq -r '.status // "unknown"' "$status_file" 2>/dev/null)
                last_action=$(jq -r '.last_action // "n/a"' "$status_file" 2>/dev/null)

                total_loops=$((total_loops + loop_count))

                echo -e "${PURPLE}│${NC} Description:    $description"
                echo -e "${PURPLE}│${NC} Loop Count:     ${CYAN}#$loop_count${NC}"
                echo -e "${PURPLE}│${NC} Status:         ${GREEN}$status${NC}"
                echo -e "${PURPLE}│${NC} API Calls:      $calls_made/$max_calls"
                echo -e "${PURPLE}│${NC} Last Action:    $last_action"

                # Check for circuit breaker
                cb_file="$PROJECT_ROOT/$project_dir/.circuit_breaker_state"
                if [ -f "$cb_file" ]; then
                    cb_state=$(jq -r '.state // "UNKNOWN"' "$cb_file" 2>/dev/null)
                    if [ "$cb_state" = "OPEN" ]; then
                        echo -e "${PURPLE}│${NC} ${RED}⚠️  Circuit Breaker: OPEN${NC}"
                    fi
                fi

                # Check @fix_plan.md progress
                fix_plan="$PROJECT_ROOT/$project_dir/@fix_plan.md"
                if [ -f "$fix_plan" ]; then
                    total_tasks=$(grep -c "^\- \[.\] " "$fix_plan" 2>/dev/null || echo "0")
                    done_tasks=$(grep -c "^\- \[x\] " "$fix_plan" 2>/dev/null || echo "0")
                    if [ "$total_tasks" -gt 0 ]; then
                        percent=$((done_tasks * 100 / total_tasks))
                        echo -e "${PURPLE}│${NC} Task Progress:  $done_tasks/$total_tasks (${percent}%)"
                    fi
                fi
            else
                echo -e "${PURPLE}│${NC} Description:    $description"
                echo -e "${PURPLE}│${NC} ${YELLOW}⏳ Starting up...${NC}"
            fi
        else
            echo -e "${PURPLE}│${NC} ${RED}○ STOPPED${NC}"
            echo -e "${PURPLE}│${NC} Description:    $description"
            echo -e "${PURPLE}│${NC} ${YELLOW}Use launch script to start${NC}"
        fi

        echo -e "${PURPLE}└─────────────────────────────────────────────────────────────────────────┘${NC}"
        echo ""
    done

    # Summary statistics
    echo -e "${BLUE}┌─ Overall Statistics ────────────────────────────────────────────────────┐${NC}"
    echo -e "${BLUE}│${NC} Active Sessions:  $active_count / ${#SESSIONS[@]}"
    echo -e "${BLUE}│${NC} Total Loops:      $total_loops"
    echo -e "${BLUE}└─────────────────────────────────────────────────────────────────────────┘${NC}"
    echo ""

    # Recent activity from main project
    echo -e "${YELLOW}┌─ Recent Activity (Main Project) ────────────────────────────────────────┐${NC}"
    if [ -f "$PROJECT_ROOT/logs/ralph.log" ]; then
        tail -n 5 "$PROJECT_ROOT/logs/ralph.log" | while IFS= read -r line; do
            echo -e "${YELLOW}│${NC} $line"
        done
    else
        echo -e "${YELLOW}│${NC} No log file found"
    fi
    echo -e "${YELLOW}└─────────────────────────────────────────────────────────────────────────┘${NC}"
    echo ""

    # Commands
    echo -e "${CYAN}Commands:${NC}"
    echo -e "  ${GREEN}tmux attach -t ralph-main${NC}     Attach to main project"
    echo -e "  ${GREEN}tmux attach -t ralph-emr${NC}      Attach to EMR project"
    echo -e "  ${GREEN}tmux list-sessions${NC}            List all sessions"
    echo -e "  ${RED}tmux kill-session -t <name>${NC}   Stop a session"
    echo ""

    sleep 5
done
