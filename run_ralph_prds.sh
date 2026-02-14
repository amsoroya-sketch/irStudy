#!/bin/bash
set -e

# Ralph PRD Automation Script for irStudy MVP Phase 1
# Runs all 14 PRDs sequentially in tmux sessions with monitoring

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PRD_DIR="$SCRIPT_DIR/planning/phase1-mvp-implementation-feb7-2026/prds"
RALPH_LOGS_DIR="$SCRIPT_DIR/ralph_logs"
TMUX_SESSION="ralph-irstudy-mvp"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# PRD task list (in execution order)
PRDS=(
    "PRD_TASK_001_API_SECURITY_AUDIT.md"
    "PRD_TASK_002_QUESTION_MANAGEMENT_CRUD.md"
    "PRD_TASK_003_STUDY_CARD_SYSTEM.md"
    "PRD_TASK_004_USER_PROGRESS_TRACKING.md"
    "PRD_TASK_005_SPACED_REPETITION_ENGINE.md"
    "PRD_TASK_006_QUIZ_INTERFACE_REDESIGN.md"
    "PRD_TASK_007_CITATION_DISPLAY_COMPONENT.md"
    "PRD_TASK_008_PERFORMANCE_DASHBOARD.md"
    "PRD_TASK_009_MOBILE_RESPONSIVE_DESIGN.md"
    "PRD_TASK_010_E2E_TESTING_SUITE.md"
    "PRD_TASK_011_RAG_EXPLANATION_ENGINE.md"
    "PRD_TASK_012_LOAD_TESTING_OPTIMIZATION.md"
    "PRD_TASK_013_DEPLOYMENT_PIPELINE.md"
    "PRD_TASK_014_MVP_VALIDATION_LAUNCH.md"
)

# Task names for display
TASK_NAMES=(
    "TASK_001: API Security Audit (6-8h)"
    "TASK_002: Question Management CRUD (6-8h)"
    "TASK_003: Study Card System (4-5h)"
    "TASK_004: User Progress Tracking (4-5h)"
    "TASK_005: Spaced Repetition Engine (3-4h)"
    "TASK_006: Quiz Interface Redesign (8-10h)"
    "TASK_007: Citation Display Component (3-4h)"
    "TASK_008: Performance Dashboard (6-8h)"
    "TASK_009: Mobile Responsive Design (4-5h)"
    "TASK_010: E2E Testing Suite (6-8h)"
    "TASK_011: RAG Explanation Engine (5-6h)"
    "TASK_012: Load Testing & Optimization (4-5h)"
    "TASK_013: Deployment Pipeline (5-6h)"
    "TASK_014: MVP Validation & Launch (4-5h)"
)

print_banner() {
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  Ralph PRD Automation - irStudy MVP Phase 1 Implementation${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
}

print_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --task NUM          Start from specific task (1-14)"
    echo "  --dry-run           Show execution plan without running"
    echo "  --monitor-only      Attach to existing tmux session"
    echo "  --stop              Stop all Ralph sessions"
    echo "  --status            Show current status"
    echo "  --clean             Clean all Ralph state files"
    echo "  -h, --help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                  # Run all 14 PRDs from start"
    echo "  $0 --task 5         # Start from TASK_005"
    echo "  $0 --monitor-only   # Attach to running session"
    echo "  $0 --status         # Show progress"
}

check_dependencies() {
    echo -e "${BLUE}[1/4] Checking dependencies...${NC}"

    # Check tmux
    if ! command -v tmux &> /dev/null; then
        echo -e "${RED}ERROR: tmux is not installed${NC}"
        echo "Install with: sudo apt-get install tmux"
        exit 1
    fi

    # Check ralph
    if ! command -v ralph &> /dev/null; then
        echo -e "${RED}ERROR: Ralph is not installed${NC}"
        echo "Install from: https://github.com/anthropics/ralph-claude-code"
        exit 1
    fi

    # Check PRD directory
    if [ ! -d "$PRD_DIR" ]; then
        echo -e "${RED}ERROR: PRD directory not found: $PRD_DIR${NC}"
        exit 1
    fi

    echo -e "${GREEN}✓ All dependencies satisfied${NC}"
}

initialize_ralph() {
    echo -e "${BLUE}[2/4] Initializing Ralph in irStudy project...${NC}"

    cd "$SCRIPT_DIR"

    # Create logs directory
    mkdir -p "$RALPH_LOGS_DIR"

    # Initialize Ralph files if they don't exist
    if [ ! -f "@fix_plan.md" ]; then
        echo -e "${YELLOW}Creating @fix_plan.md from PRD list...${NC}"
        cat > @fix_plan.md <<'EOF'
# irStudy MVP Phase 1 Implementation Plan

## Week 1: Backend Foundation (5 tasks, 22-29 hours)
- [ ] TASK_001: API Security Audit (6-8h) - P0-Critical
- [ ] TASK_002: Question Management CRUD (6-8h) - P0-Critical
- [ ] TASK_003: Study Card System (4-5h) - P1-High
- [ ] TASK_004: User Progress Tracking (4-5h) - P1-High
- [ ] TASK_005: Spaced Repetition Engine (3-4h) - P1-High

## Week 2: Frontend Development (4 tasks, 21-27 hours)
- [ ] TASK_006: Quiz Interface Redesign (8-10h) - P0-Critical
- [ ] TASK_007: Citation Display Component (3-4h) - P1-High
- [ ] TASK_008: Performance Dashboard (6-8h) - P1-High
- [ ] TASK_009: Mobile Responsive Design (4-5h) - P1-High

## Week 3: Integration & Launch (5 tasks, 24-30 hours)
- [ ] TASK_010: E2E Testing Suite (6-8h) - P0-Critical
- [ ] TASK_011: RAG Explanation Engine (5-6h) - P1-High
- [ ] TASK_012: Load Testing & Optimization (4-5h) - P1-High
- [ ] TASK_013: Deployment Pipeline (5-6h) - P0-Critical
- [ ] TASK_014: MVP Validation & Launch (4-5h) - P0-Critical
EOF
    fi

    if [ ! -f "@AGENT.md" ]; then
        echo -e "${YELLOW}Creating @AGENT.md...${NC}"
        cat > @AGENT.md <<'EOF'
# Build & Run Instructions

## Backend (FastAPI)
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn src.main:app --reload
```

## Frontend (React + Vite)
```bash
cd frontend
npm install
npm run dev
```

## Database
```bash
docker-compose up -d postgres redis qdrant
cd backend
alembic upgrade head
```

## Tests
```bash
# Backend tests
cd backend
pytest tests/ -v

# Frontend tests
cd frontend
npm test
```
EOF
    fi

    echo -e "${GREEN}✓ Ralph initialization complete${NC}"
}

create_tmux_session() {
    local task_num=$1
    local prd_file=$2
    local task_name=$3

    echo -e "${BLUE}[3/4] Creating tmux session for ${task_name}...${NC}"

    # Kill existing session if it exists
    tmux kill-session -t "$TMUX_SESSION" 2>/dev/null || true

    # Create new tmux session with 3 panes
    tmux new-session -d -s "$TMUX_SESSION" -n "ralph-task-${task_num}"

    # Pane 0: Ralph execution
    tmux send-keys -t "$TMUX_SESSION:0.0" "cd $SCRIPT_DIR" C-m
    tmux send-keys -t "$TMUX_SESSION:0.0" "clear" C-m
    tmux send-keys -t "$TMUX_SESSION:0.0" "echo '═══════════════════════════════════════════════════════════'" C-m
    tmux send-keys -t "$TMUX_SESSION:0.0" "echo '  Ralph Execution: ${task_name}'" C-m
    tmux send-keys -t "$TMUX_SESSION:0.0" "echo '═══════════════════════════════════════════════════════════'" C-m
    tmux send-keys -t "$TMUX_SESSION:0.0" "echo ''" C-m

    # Split horizontally for logs
    tmux split-window -h -t "$TMUX_SESSION:0"

    # Pane 1: Live logs
    tmux send-keys -t "$TMUX_SESSION:0.1" "cd $SCRIPT_DIR" C-m
    tmux send-keys -t "$TMUX_SESSION:0.1" "clear" C-m
    tmux send-keys -t "$TMUX_SESSION:0.1" "echo '═══════════════════════════════════════════════════════════'" C-m
    tmux send-keys -t "$TMUX_SESSION:0.1" "echo '  Live Logs'" C-m
    tmux send-keys -t "$TMUX_SESSION:0.1" "echo '═══════════════════════════════════════════════════════════'" C-m
    tmux send-keys -t "$TMUX_SESSION:0.1" "tail -f logs/*.log 2>/dev/null || echo 'Waiting for logs...'" C-m

    # Split pane 0 vertically for status
    tmux split-window -v -t "$TMUX_SESSION:0.0" -p 30

    # Pane 2: Status monitoring
    tmux send-keys -t "$TMUX_SESSION:0.2" "cd $SCRIPT_DIR" C-m
    tmux send-keys -t "$TMUX_SESSION:0.2" "clear" C-m
    tmux send-keys -t "$TMUX_SESSION:0.2" "watch -n 5 'cat status.json 2>/dev/null | jq . || echo \"Waiting for status...\"'" C-m

    # Select main pane
    tmux select-pane -t "$TMUX_SESSION:0.0"

    echo -e "${GREEN}✓ Tmux session created: $TMUX_SESSION${NC}"
}

run_ralph_task() {
    local task_num=$1
    local prd_file=$2
    local task_name=$3

    echo -e "${BLUE}[4/4] Executing Ralph for ${task_name}...${NC}"

    cd "$SCRIPT_DIR"

    # Copy PRD to PROMPT.md
    echo -e "${YELLOW}Copying PRD to PROMPT.md...${NC}"
    cp "$PRD_DIR/$prd_file" PROMPT.md

    # Create log file for this task
    local log_file="$RALPH_LOGS_DIR/task_$(printf '%03d' $task_num)_$(date +%Y%m%d_%H%M%S).log"

    # Run Ralph in tmux pane 0 with monitoring
    tmux send-keys -t "$TMUX_SESSION:0.0" "ralph --no-continue --calls 50 --timeout 30 2>&1 | tee $log_file" C-m

    echo -e "${GREEN}✓ Ralph execution started${NC}"
    echo -e "${YELLOW}Tmux session: $TMUX_SESSION${NC}"
    echo -e "${YELLOW}Log file: $log_file${NC}"
    echo ""
    echo -e "${GREEN}To attach to session:${NC} tmux attach -t $TMUX_SESSION"
    echo -e "${GREEN}To detach:${NC} Ctrl+B, then D"
    echo -e "${GREEN}To stop:${NC} $0 --stop"
}

run_all_tasks() {
    local start_task=${1:-1}

    print_banner
    check_dependencies
    initialize_ralph

    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  Execution Plan${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "Total PRDs: ${#PRDS[@]}"
    echo "Starting from: Task $start_task (${TASK_NAMES[$((start_task-1))]})"
    echo ""

    for i in "${!PRDS[@]}"; do
        local task_num=$((i + 1))
        if [ $task_num -ge $start_task ]; then
            echo -e "${GREEN}[$task_num/${#PRDS[@]}]${NC} ${TASK_NAMES[$i]}"
        else
            echo -e "${YELLOW}[$task_num/${#PRDS[@]}]${NC} ${TASK_NAMES[$i]} (skipped)"
        fi
    done

    echo ""
    read -p "Press ENTER to start, or Ctrl+C to cancel..."

    # Run first task
    local task_idx=$((start_task - 1))
    create_tmux_session "$start_task" "${PRDS[$task_idx]}" "${TASK_NAMES[$task_idx]}"
    run_ralph_task "$start_task" "${PRDS[$task_idx]}" "${TASK_NAMES[$task_idx]}"

    echo ""
    echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}  Ralph is now running Task $start_task${NC}"
    echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Monitor progress: tmux attach -t $TMUX_SESSION"
    echo "2. When task completes, run: $0 --task $((start_task + 1))"
    echo "3. Or use: $0 --status to check progress"
    echo ""
    echo "Task completion checklist:"
    echo "- Watch for 'TASK_${task_num}: ✅ DONE' in @fix_plan.md"
    echo "- Verify git commit created"
    echo "- Check Ralph exit status"
    echo ""
}

dry_run() {
    print_banner
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  Dry Run - Execution Plan${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo ""

    for i in "${!PRDS[@]}"; do
        local task_num=$((i + 1))
        echo -e "${GREEN}Task $task_num:${NC} ${TASK_NAMES[$i]}"
        echo "  PRD: ${PRDS[$i]}"
        echo "  Week: $( [ $task_num -le 5 ] && echo '1 (Backend)' || ( [ $task_num -le 9 ] && echo '2 (Frontend)' || echo '3 (Integration)' ) )"
        echo ""
    done

    echo "Total estimated time: 67-86 hours"
    echo "PRD directory: $PRD_DIR"
    echo "Logs directory: $RALPH_LOGS_DIR"
    echo "Tmux session: $TMUX_SESSION"
}

monitor_only() {
    if tmux has-session -t "$TMUX_SESSION" 2>/dev/null; then
        echo -e "${GREEN}Attaching to session: $TMUX_SESSION${NC}"
        tmux attach -t "$TMUX_SESSION"
    else
        echo -e "${RED}ERROR: No active Ralph session found${NC}"
        echo "Start a session with: $0"
        exit 1
    fi
}

stop_sessions() {
    echo -e "${YELLOW}Stopping all Ralph sessions...${NC}"
    tmux kill-session -t "$TMUX_SESSION" 2>/dev/null && echo -e "${GREEN}✓ Session stopped${NC}" || echo -e "${YELLOW}No active session found${NC}"
}

show_status() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  Ralph Status - irStudy MVP${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo ""

    # Check tmux session
    if tmux has-session -t "$TMUX_SESSION" 2>/dev/null; then
        echo -e "${GREEN}✓ Ralph session active: $TMUX_SESSION${NC}"
    else
        echo -e "${YELLOW}○ No active Ralph session${NC}"
    fi

    # Check fix_plan.md progress
    if [ -f "$SCRIPT_DIR/@fix_plan.md" ]; then
        echo ""
        echo "Task Progress:"
        grep -E '^\- \[.\] TASK_' "$SCRIPT_DIR/@fix_plan.md" | head -14 || echo "No tasks found"
    fi

    # Show latest log
    echo ""
    echo "Latest log files:"
    ls -lt "$RALPH_LOGS_DIR" 2>/dev/null | head -5 || echo "No logs yet"

    # Show Ralph status
    if [ -f "$SCRIPT_DIR/status.json" ]; then
        echo ""
        echo "Ralph Status:"
        cat "$SCRIPT_DIR/status.json" | jq . 2>/dev/null || cat "$SCRIPT_DIR/status.json"
    fi
}

clean_state() {
    echo -e "${YELLOW}Cleaning Ralph state files...${NC}"
    cd "$SCRIPT_DIR"
    ralph --clean
    echo -e "${GREEN}✓ State files cleaned${NC}"
}

# Main script
main() {
    local start_task=1

    case "${1:-}" in
        --task)
            start_task=${2:-1}
            if [ $start_task -lt 1 ] || [ $start_task -gt 14 ]; then
                echo -e "${RED}ERROR: Task number must be between 1 and 14${NC}"
                exit 1
            fi
            run_all_tasks $start_task
            ;;
        --dry-run)
            dry_run
            ;;
        --monitor-only)
            monitor_only
            ;;
        --stop)
            stop_sessions
            ;;
        --status)
            show_status
            ;;
        --clean)
            clean_state
            ;;
        -h|--help)
            print_usage
            ;;
        "")
            run_all_tasks
            ;;
        *)
            echo -e "${RED}ERROR: Unknown option: $1${NC}"
            print_usage
            exit 1
            ;;
    esac
}

main "$@"
