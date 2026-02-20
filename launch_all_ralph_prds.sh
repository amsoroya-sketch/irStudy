#!/bin/bash

# Launch All Ralph PRD Executions in Separate Tmux Sessions
# Created: 2026-02-16
# Purpose: Execute multiple Ralph PRD projects concurrently with monitoring

set -e

PROJECT_ROOT="/home/dev/Development/irStudy"
cd "$PROJECT_ROOT"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
PURPLE='\033[0;35m'
NC='\033[0m'

print_banner() {
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  🚀 Ralph PRD Multi-Execution Launcher${NC}"
    echo -e "${BLUE}  irStudy Platform - Concurrent PRD Implementation${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo ""
}

print_banner

# PRD Project Definitions
# Format: "SESSION_NAME|PROJECT_DIR|DESCRIPTION|PRIORITY|STATUS"
declare -a PRD_PROJECTS=(
    "ralph-main|.|Main Project - Phase 1 MVP Tasks (14 PRDs)|P0-Critical|READY"
    "ralph-emr|emr-practice-system/emr-ralph-project|EMR PRD Refinement (AMC Alignment)|P1-High|READY"
    "ralph-backend|backend-features-15-feb|Backend Monitoring & Documentation|P2-Medium|COMPLETE"
)

echo -e "${YELLOW}📋 Discovered Ralph PRD Projects:${NC}"
echo ""

project_count=0
ready_count=0

for project in "${PRD_PROJECTS[@]}"; do
    IFS='|' read -r session_name project_dir description priority status <<< "$project"
    project_count=$((project_count + 1))

    # Check if PROMPT.md exists
    if [ -f "$PROJECT_ROOT/$project_dir/PROMPT.md" ]; then
        status_color=$GREEN
        if [ "$status" = "COMPLETE" ]; then
            status_color=$YELLOW
        fi

        echo -e "${status_color}[$project_count]${NC} ${BLUE}$session_name${NC}"
        echo "    📁 Path: $project_dir"
        echo "    📝 Description: $description"
        echo "    🎯 Priority: $priority"
        echo "    ✅ Status: $status"
        echo ""

        if [ "$status" = "READY" ]; then
            ready_count=$((ready_count + 1))
        fi
    else
        echo -e "${RED}[$project_count]${NC} ${RED}$session_name${NC} - PROMPT.md NOT FOUND"
        echo "    📁 Path: $project_dir (INVALID)"
        echo ""
    fi
done

echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Total Projects: $project_count${NC}"
echo -e "${GREEN}Ready to Execute: $ready_count${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo ""

# Check if tmux is installed
if ! command -v tmux &> /dev/null; then
    echo -e "${RED}ERROR: tmux is not installed${NC}"
    echo "Install with: sudo apt-get install tmux"
    exit 1
fi

# Function to create Ralph session
create_ralph_session() {
    local session_name=$1
    local project_dir=$2
    local description=$3

    echo -e "${BLUE}Creating tmux session: $session_name${NC}"

    # Check if session already exists
    if tmux has-session -t "$session_name" 2>/dev/null; then
        echo -e "${YELLOW}  ⚠️  Session $session_name already exists${NC}"
        read -p "  Kill and recreate? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            tmux kill-session -t "$session_name"
            echo -e "${GREEN}  ✓ Old session killed${NC}"
        else
            echo -e "${YELLOW}  ⊙ Skipping $session_name${NC}"
            return 0
        fi
    fi

    # Create new detached session
    tmux new-session -d -s "$session_name" -c "$PROJECT_ROOT/$project_dir"

    # Split window horizontally for monitor (top = main, bottom = monitor)
    tmux split-window -v -t "$session_name" -c "$PROJECT_ROOT/$project_dir"

    # Resize monitor pane to 30% of screen
    tmux resize-pane -t "$session_name:0.1" -y 10

    # Send Ralph loop command to main pane (top)
    tmux send-keys -t "$session_name:0.0" "echo ''" Enter
    tmux send-keys -t "$session_name:0.0" "echo '🚀 Ralph PRD Execution - $description'" Enter
    tmux send-keys -t "$session_name:0.0" "echo ''" Enter
    tmux send-keys -t "$session_name:0.0" "echo 'Starting in 5 seconds... (Ctrl+C to cancel)'" Enter
    tmux send-keys -t "$session_name:0.0" "sleep 5" Enter
    tmux send-keys -t "$session_name:0.0" "~/ralph_loop.sh --calls 50 --verbose" Enter

    # Send monitoring command to monitor pane (bottom)
    tmux send-keys -t "$session_name:0.1" "watch -n 5 'cat status.json 2>/dev/null | jq . || echo \"No status yet\"'" Enter

    # Set pane titles
    tmux select-pane -t "$session_name:0.0" -T "Ralph Loop"
    tmux select-pane -t "$session_name:0.1" -T "Status Monitor"

    # Focus on main pane
    tmux select-pane -t "$session_name:0.0"

    echo -e "${GREEN}  ✓ Session $session_name created${NC}"
}

# Ask user which projects to launch
echo -e "${YELLOW}Which PRD projects do you want to execute?${NC}"
echo ""
echo "  [1] Main Project (Phase 1 MVP - 14 tasks)"
echo "  [2] EMR PRD Refinement (AMC Alignment)"
echo "  [3] Backend Monitoring (COMPLETE - skip)"
echo "  [A] All READY projects (exclude COMPLETE)"
echo "  [Q] Quit"
echo ""
read -p "Enter your choice (1, 2, 3, A, Q): " -n 1 -r
echo
echo ""

case $REPLY in
    1)
        echo -e "${GREEN}Launching: Main Project${NC}"
        create_ralph_session "ralph-main" "." "Phase 1 MVP Tasks (14 PRDs)"
        ;;
    2)
        echo -e "${GREEN}Launching: EMR PRD Refinement${NC}"
        create_ralph_session "ralph-emr" "emr-practice-system/emr-ralph-project" "EMR PRD Refinement (AMC Alignment)"
        ;;
    3)
        echo -e "${YELLOW}Backend Monitoring is marked COMPLETE. Skipping.${NC}"
        echo -e "${BLUE}To run anyway:${NC}"
        echo "  cd backend-features-15-feb && ~/ralph_loop.sh"
        ;;
    A|a)
        echo -e "${GREEN}Launching all READY projects...${NC}"
        echo ""
        create_ralph_session "ralph-main" "." "Phase 1 MVP Tasks (14 PRDs)"
        sleep 2
        create_ralph_session "ralph-emr" "emr-practice-system/emr-ralph-project" "EMR PRD Refinement (AMC Alignment)"
        ;;
    Q|q)
        echo -e "${BLUE}Exiting without launching.${NC}"
        exit 0
        ;;
    *)
        echo -e "${RED}Invalid choice. Exiting.${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Ralph PRD Sessions Created${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}Available tmux sessions:${NC}"
tmux list-sessions 2>/dev/null || echo "No sessions running"
echo ""
echo -e "${BLUE}Commands:${NC}"
echo ""
echo -e "  ${GREEN}Attach to main:${NC}      tmux attach -t ralph-main"
echo -e "  ${GREEN}Attach to EMR:${NC}       tmux attach -t ralph-emr"
echo -e "  ${GREEN}List sessions:${NC}       tmux list-sessions"
echo -e "  ${GREEN}Kill session:${NC}        tmux kill-session -t <name>"
echo -e "  ${GREEN}Kill all Ralph:${NC}      tmux kill-session -a -t ralph-"
echo ""
echo -e "  ${PURPLE}Detach from session:${NC} Ctrl+B then D"
echo -e "  ${PURPLE}Switch panes:${NC}        Ctrl+B then ↑/↓"
echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}Would you like to attach to a session now?${NC}"
read -p "Enter session name (ralph-main, ralph-emr) or press Enter to exit: " session_choice

if [ -n "$session_choice" ]; then
    if tmux has-session -t "$session_choice" 2>/dev/null; then
        echo -e "${GREEN}Attaching to $session_choice...${NC}"
        tmux attach -t "$session_choice"
    else
        echo -e "${RED}Session $session_choice not found${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}Done! Sessions are running in the background.${NC}"
