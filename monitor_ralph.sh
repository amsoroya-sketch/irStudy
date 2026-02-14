#!/bin/bash

# Ralph Monitoring Script
# Non-intrusive monitoring of Ralph execution

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Ralph Monitoring Dashboard${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo ""

# Check if Ralph is running
if pgrep -f "ralph_loop.sh" > /dev/null; then
    echo -e "${GREEN}✓ Ralph is running${NC}"
    RALPH_PID=$(pgrep -f "ralph_loop.sh")
    echo "  PID: $RALPH_PID"
else
    echo -e "${RED}✗ Ralph is not running${NC}"
fi

# Check tmux session
if tmux has-session -t ralph-irstudy-mvp 2>/dev/null; then
    echo -e "${GREEN}✓ Tmux session active: ralph-irstudy-mvp${NC}"
else
    echo -e "${YELLOW}○ No tmux session found${NC}"
fi

echo ""
echo -e "${BLUE}═══ Current Task ════════════════════════════════════════════${NC}"

# Extract current task from PROMPT.md
if [ -f PROMPT.md ]; then
    CURRENT_TASK=$(head -5 PROMPT.md | grep "CURRENT TASK" | sed 's/\*\*CURRENT TASK\*\*://' | xargs)
    echo "  $CURRENT_TASK"
else
    echo "  No PROMPT.md found"
fi

echo ""
echo -e "${BLUE}═══ Task Progress ═══════════════════════════════════════════${NC}"

# Show @fix_plan.md progress
if [ -f @fix_plan.md ]; then
    TOTAL=$(grep -c "^\- \[ \] \*\*TASK_" @fix_plan.md 2>/dev/null || echo "0")
    DONE=$(grep -c "^\- \[x\] \*\*TASK_" @fix_plan.md 2>/dev/null || echo "0")
    echo "  Completed: $DONE / $TOTAL tasks"
    echo ""
    grep "^\- \[.\] \*\*TASK_" @fix_plan.md | head -5
else
    echo "  No @fix_plan.md found"
fi

echo ""
echo -e "${BLUE}═══ Ralph Status ════════════════════════════════════════════${NC}"

# Show status.json
if [ -f status.json ]; then
    if command -v jq &> /dev/null; then
        cat status.json | jq -r '. | "  Loop: \(.loop_count) | Calls: \(.calls_made_this_hour)/\(.max_calls_per_hour) | Status: \(.status)"'
    else
        cat status.json
    fi
else
    echo "  No status.json yet (Ralph not started)"
fi

echo ""
echo -e "${BLUE}═══ Circuit Breaker ═════════════════════════════════════════${NC}"

# Check circuit breaker state
if [ -f .circuit_breaker_state ]; then
    STATE=$(cat .circuit_breaker_state | grep "STATE=" | cut -d'=' -f2)
    echo "  State: $STATE"
else
    echo "  State: UNKNOWN (file not found)"
fi

echo ""
echo -e "${BLUE}═══ Recent Activity ═════════════════════════════════════════${NC}"

# Show last 5 log entries
if [ -d logs ]; then
    LATEST_LOG=$(ls -t logs/claude_output_*.log 2>/dev/null | head -1)
    if [ -n "$LATEST_LOG" ]; then
        echo "  Latest log: $LATEST_LOG"
        echo "  Size: $(du -h "$LATEST_LOG" | cut -f1)"
        echo "  Modified: $(stat -c %y "$LATEST_LOG" 2>/dev/null || stat -f %Sm "$LATEST_LOG" 2>/dev/null)"
    else
        echo "  No Claude logs yet"
    fi
fi

# Show last Ralph log entries
if [ -f logs/ralph.log ]; then
    echo ""
    echo "  Last 3 Ralph log entries:"
    tail -3 logs/ralph.log | sed 's/^/    /'
fi

echo ""
echo -e "${BLUE}═══ Files Changed ═══════════════════════════════════════════${NC}"

# Show recently modified files (last hour)
echo "  Files modified in last hour:"
find . -type f -mmin -60 2>/dev/null | grep -v ".git\|node_modules\|venv\|__pycache__" | head -10 | sed 's/^/    /'

echo ""
echo -e "${BLUE}═══ Commands ════════════════════════════════════════════════${NC}"
echo ""
echo "  Attach to tmux:     tmux attach -t ralph-irstudy-mvp"
echo "  View live logs:     tail -f ralph_logs/task_*.log"
echo "  Check full status:  ./run_ralph_prds.sh --status"
echo "  Stop Ralph:         ./run_ralph_prds.sh --stop"
echo "  Reset state:        ralph --clean"
echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
