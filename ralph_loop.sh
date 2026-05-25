#!/bin/bash

# Claude Code Ralph Loop with Rate Limiting and Documentation
# Adaptation of the Ralph technique for Claude Code with usage management

set -euo pipefail  # Exit on error, undefined vars, and pipe failures

# Source library components
SCRIPT_DIR="$(dirname "${BASH_SOURCE[0]}")"
source "$SCRIPT_DIR/lib/date_utils.sh"
source "$SCRIPT_DIR/lib/error_detector.sh"
source "$SCRIPT_DIR/lib/response_analyzer.sh"
source "$SCRIPT_DIR/lib/circuit_breaker.sh"
source "$SCRIPT_DIR/lib/permission_checker.sh"
source "$SCRIPT_DIR/lib/log_rotation.sh"
source "$SCRIPT_DIR/lib/dry_run.sh"
source "$SCRIPT_DIR/lib/config.sh"
source "$SCRIPT_DIR/lib/github_sync.sh"
source "$SCRIPT_DIR/lib/tralph_validator.sh"

# Load configuration from .ralphrc files (hierarchy: defaults -> global -> project -> env)
if ! load_config; then
    echo -e "${RED}ERROR: Failed to load configuration${NC}" >&2
    exit 1
fi

# Configuration - Load from .ralphrc or use defaults
PROMPT_FILE="PROMPT.md"
LOG_DIR="logs"
LOG_FILE="$LOG_DIR/ralph.log"
DOCS_DIR="docs/generated"
STATUS_FILE="status.json"
PROGRESS_FILE="progress.json"
CLAUDE_CODE_CMD="claude"
SLEEP_DURATION=3600     # 1 hour in seconds
CALL_COUNT_FILE=".call_count"
TIMESTAMP_FILE=".last_reset"
USE_TMUX=false

# Load configuration from .ralphrc files (hierarchy applied in lib/config.sh)
# These values override defaults but can be overridden by CLI args
MAX_CALLS_PER_HOUR=$(get_config "limits.max_calls_per_hour")
VERBOSE_PROGRESS=false  # Default: no verbose progress updates (CLI only)
CLAUDE_TIMEOUT_MINUTES=15  # Default: 15 minutes timeout (CLI only)

# Log rotation configuration from .ralphrc
RALPH_LOG_ROTATION="$(get_config "logging.rotation")"
RALPH_LOG_MAX_SIZE="$(get_config "logging.max_size")"
RALPH_LOG_MAX_FILES="$(get_config "logging.max_files")"
RALPH_LOG_COMPRESS="$(get_config "logging.compress")"

# Modern Claude CLI configuration from .ralphrc
CLAUDE_OUTPUT_FORMAT="$(get_config "output.format")"
CLAUDE_ALLOWED_TOOLS="$(get_config "execution.allowed_tools")"
CLAUDE_USE_CONTINUE=$(get_config "execution.continue_session")
CLAUDE_SESSION_FILE=".claude_session_id"
CLAUDE_MIN_VERSION="2.0.76"

# Session management configuration from .ralphrc
RALPH_SESSION_FILE=".ralph_session"
RALPH_SESSION_HISTORY_FILE=".ralph_session_history"
CLAUDE_SESSION_EXPIRY_HOURS=$(get_config "session.expiry_hours")

# Valid tool patterns for --allowed-tools validation
# Tools can be exact matches or pattern matches with wildcards in parentheses
VALID_TOOL_PATTERNS=(
    "Write"
    "Read"
    "Edit"
    "MultiEdit"
    "Glob"
    "Grep"
    "Task"
    "TodoWrite"
    "WebFetch"
    "WebSearch"
    "Bash"
    "Bash(git *)"
    "Bash(npm *)"
    "Bash(bats *)"
    "Bash(python *)"
    "Bash(node *)"
    "NotebookEdit"
)

# Exit detection configuration
EXIT_SIGNALS_FILE=".exit_signals"
MAX_CONSECUTIVE_TEST_LOOPS=3
MAX_CONSECUTIVE_DONE_SIGNALS=2
TEST_PERCENTAGE_THRESHOLD=30  # If more than 30% of recent loops are test-only, flag it

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Project constraints for learning system (TASK-001)
CONSTRAINTS_CONTENT=""

# GitHub import configuration (Phase 5-001)
GITHUB_IMPORT_ISSUE=""
GITHUB_IMPORT_REPO=""
GITHUB_LABELS=()
GITHUB_MILESTONE=""
GITHUB_STATE="open"
GITHUB_LIMIT="50"
GITHUB_DRY_RUN=false
GITHUB_OUTPUT_DIR="specs/tasks"

# Initialize directories
mkdir -p "$LOG_DIR" "$DOCS_DIR"

# Validate required dependencies
validate_dependencies() {
    local missing_deps=()

    # Required dependency: jq (JSON processing)
    if ! command -v jq &>/dev/null; then
        missing_deps+=("jq")
    fi

    # Required dependency: git (version control)
    if ! command -v git &>/dev/null; then
        missing_deps+=("git")
    fi

    # Report missing dependencies
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        echo "ERROR: Missing required dependencies: ${missing_deps[*]}" >&2
        echo "" >&2
        echo "Install with:" >&2
        echo "  Ubuntu/Debian: sudo apt-get install ${missing_deps[*]}" >&2
        echo "  macOS: brew install ${missing_deps[*]}" >&2
        echo "  CentOS/RHEL: sudo yum install ${missing_deps[*]}" >&2
        exit 1
    fi
}

# Call dependency validation immediately
validate_dependencies

# Check if tmux is available
check_tmux_available() {
    if ! command -v tmux &> /dev/null; then
        log_status "ERROR" "tmux is not installed. Please install tmux or run without --monitor flag."
        echo "Install tmux:"
        echo "  Ubuntu/Debian: sudo apt-get install tmux"
        echo "  macOS: brew install tmux"
        echo "  CentOS/RHEL: sudo yum install tmux"
        exit 1
    fi
}

# Setup tmux session with monitor
setup_tmux_session() {
    local session_name="ralph-$(date +%s)"
    local ralph_home="${RALPH_HOME:-$HOME/.ralph}"
    local logs_dir="$(pwd)/logs"

    log_status "INFO" "Setting up tmux session: $session_name"

    # Ensure logs directory exists
    mkdir -p "$logs_dir"

    # Create new tmux session detached
    tmux new-session -d -s "$session_name" -c "$(pwd)"

    # Split window vertically (50% | 50%)
    tmux split-window -h -t "$session_name" -c "$(pwd)"

    # Split the right pane horizontally (50% | 25% | 25%)
    tmux split-window -v -t "$session_name:0.1" -c "$(pwd)"

    # Pane 0 (left 50%): Ralph loop
    # Pane 1 (top-right 25%): Ralph log tail
    # Pane 2 (bottom-right 25%): Claude output log viewer

    # Start Ralph log viewer in top-right pane (pane 1)
    tmux send-keys -t "$session_name:0.1" "echo '📋 Ralph Log (live)' && tail -f logs/ralph.log 2>/dev/null || (echo 'Waiting for ralph.log...' && sleep 2 && tail -f logs/ralph.log)" Enter

    # Start Claude output viewer in bottom-right pane (pane 2)
    if [[ -f "$ralph_home/lib/claude_log_viewer.sh" ]]; then
        tmux send-keys -t "$session_name:0.2" "'$ralph_home/lib/claude_log_viewer.sh' logs" Enter
    else
        # Fallback to inline viewer
        tmux send-keys -t "$session_name:0.2" "while true; do LATEST=\$(ls -t logs/claude_output_*.log 2>/dev/null | head -1); if [[ -n \"\$LATEST\" ]]; then clear; echo '🤖 '\$LATEST; jq -r '.result // .error // \"Empty\"' \"\$LATEST\" 2>/dev/null || cat \"\$LATEST\"; fi; sleep 3; done" Enter
    fi

    # Start ralph loop in the left pane (exclude tmux flag to avoid recursion)
    local ralph_cmd
    if command -v ralph &> /dev/null; then
        ralph_cmd="ralph"
    else
        ralph_cmd="'$ralph_home/ralph_loop.sh'"
    fi

    if [[ "$MAX_CALLS_PER_HOUR" != "100" ]]; then
        ralph_cmd="$ralph_cmd --calls $MAX_CALLS_PER_HOUR"
    fi
    if [[ "$PROMPT_FILE" != "PROMPT.md" ]]; then
        ralph_cmd="$ralph_cmd --prompt '$PROMPT_FILE'"
    fi

    tmux send-keys -t "$session_name:0.0" "$ralph_cmd" Enter

    # Focus on left pane (main ralph loop)
    tmux select-pane -t "$session_name:0.0"

    # Set window title
    tmux rename-window -t "$session_name:0" "Ralph: Loop | Logs | Claude"

    log_status "SUCCESS" "Tmux session created with 3 panes:"
    log_status "INFO" "  Left:        Ralph Loop (main)"
    log_status "INFO" "  Top-Right:   Ralph Log (live tail)"
    log_status "INFO" "  Bottom-Right: Claude Output (live)"
    log_status "INFO" ""
    log_status "INFO" "Navigation: Ctrl+B then Arrow Keys"
    log_status "INFO" "Detach: Ctrl+B then D"
    log_status "INFO" "Reattach: tmux attach -t $session_name"

    # Attach to session (this will block until session ends)
    tmux attach-session -t "$session_name"

    exit 0
}

# Initialize call tracking
init_call_tracking() {
    log_status "INFO" "DEBUG: Entered init_call_tracking..."
    local current_hour=$(date +%Y%m%d%H)
    local last_reset_hour=""

    if [[ -f "$TIMESTAMP_FILE" ]]; then
        last_reset_hour=$(cat "$TIMESTAMP_FILE")
    fi

    # Reset counter if it's a new hour
    if [[ "$current_hour" != "$last_reset_hour" ]]; then
        echo "0" > "$CALL_COUNT_FILE"
        echo "$current_hour" > "$TIMESTAMP_FILE"
        log_status "INFO" "Call counter reset for new hour: $current_hour"
    fi

    # Initialize exit signals tracking if it doesn't exist
    if [[ ! -f "$EXIT_SIGNALS_FILE" ]]; then
        echo '{"test_only_loops": [], "done_signals": [], "completion_indicators": []}' > "$EXIT_SIGNALS_FILE"
    fi

    # Initialize circuit breaker
    init_circuit_breaker

    log_status "INFO" "DEBUG: Completed init_call_tracking successfully"
}

# Reset all Ralph state files (for --clean flag)
reset_state_files() {
    local files_removed=()

    # Remove state files if they exist
    if [[ -f "$EXIT_SIGNALS_FILE" ]]; then
        rm -f "$EXIT_SIGNALS_FILE"
        files_removed+=("exit_signals")
    fi

    if [[ -f "$CALL_COUNT_FILE" ]]; then
        rm -f "$CALL_COUNT_FILE"
        files_removed+=("call_count")
    fi

    if [[ -f ".circuit_breaker_state" ]]; then
        rm -f ".circuit_breaker_state"
        files_removed+=("circuit_breaker_state")
    fi

    if [[ -f ".circuit_breaker_history" ]]; then
        rm -f ".circuit_breaker_history"
        files_removed+=("circuit_breaker_history")
    fi

    # Reset session (uses function from ralph_loop.sh)
    if declare -f reset_session > /dev/null; then
        reset_session "manual_clean_flag"
        files_removed+=("session")
    fi

    # Reinitialize empty exit signals
    echo '{"test_only_loops": [], "done_signals": [], "completion_indicators": []}' > "$EXIT_SIGNALS_FILE"

    # Report what was cleaned
    if [[ ${#files_removed[@]} -gt 0 ]]; then
        echo -e "${YELLOW}⚠️  Cleaned stale state files: ${files_removed[*]}${NC}"
        echo -e "${GREEN}✅ Ralph state reset. Starting fresh.${NC}"
    else
        echo -e "${GREEN}✅ No stale state files found. State is clean.${NC}"
    fi
}

# Validate Ralph is running from a valid project directory
validate_working_directory() {
    local has_prompt=false
    local has_fix_plan=false
    local in_ralph_install=false

    # Check for Ralph control files
    [[ -f "PROMPT.md" ]] && has_prompt=true
    [[ -f "@fix_plan.md" ]] && has_fix_plan=true

    # Check if in Ralph's installation directory
    if [[ "$PWD" == *"ralph-claude-code"* ]] || [[ "$PWD" == *".ralph"* ]]; then
        in_ralph_install=true
    fi

    # Error: Running from Ralph's installation directory
    if [[ "$in_ralph_install" == true && "$has_prompt" == false && "$has_fix_plan" == false ]]; then
        echo -e "${RED}❌ ERROR: Ralph appears to be running from its installation directory!${NC}"
        echo -e "${RED}   Current directory: $PWD${NC}"
        echo -e "${YELLOW}   Ralph must run from your project directory, not from:${NC}"
        echo -e "${YELLOW}   - ~/.ralph/ (installation directory)${NC}"
        echo -e "${YELLOW}   - */ralph-claude-code/ (source repository)${NC}"
        echo ""
        echo -e "${GREEN}Fix:${NC}"
        echo -e "${GREEN}   cd /path/to/your/project${NC}"
        echo -e "${GREEN}   ralph --calls 50${NC}"
        echo ""
        return 1
    fi

    # Warning: No Ralph control files found
    if [[ "$has_prompt" == false && "$has_fix_plan" == false ]]; then
        echo -e "${YELLOW}⚠️  WARNING: No PROMPT.md or @fix_plan.md found in current directory${NC}"
        echo -e "${YELLOW}   Current directory: $PWD${NC}"
        echo -e "${YELLOW}   Are you in the correct project directory?${NC}"
        echo ""
        echo -n "Continue anyway? (y/N) "
        read -r response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            echo -e "${RED}Aborted.${NC}"
            return 1
        fi
        echo ""
    fi

    return 0
}

# Log function with timestamps and colors
log_status() {
    local level=$1
    local message=$2
    local timestamp

    # Check log rotation before writing (Phase 3.001)
    # Only check periodically to avoid performance impact
    if [[ "$RALPH_LOG_ROTATION" == "true" ]]; then
        rotate_log_if_needed "$LOG_FILE"
    fi

    # Use built-in printf for timestamps (60% faster than date subprocess)
    # Requires bash 4.2+, fallback to date if not available
    if ((BASH_VERSINFO[0] > 4 || (BASH_VERSINFO[0] == 4 && BASH_VERSINFO[1] >= 2))); then
        printf -v timestamp '%(%Y-%m-%d %H:%M:%S)T' -1
    else
        timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    fi

    local color=""

    case $level in
        "INFO")  color=$BLUE ;;
        "WARN")  color=$YELLOW ;;
        "ERROR") color=$RED ;;
        "SUCCESS") color=$GREEN ;;
        "LOOP") color=$PURPLE ;;
    esac

    # Route ERROR messages to stderr, everything else to stdout
    if [[ "$level" == "ERROR" ]]; then
        echo -e "${color}[$timestamp] [$level] $message${NC}" >&2
    else
        echo -e "${color}[$timestamp] [$level] $message${NC}"
    fi
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
}

# Update status JSON for external monitoring
update_status() {
    local loop_count=$1
    local calls_made=$2
    local last_action=$3
    local status=$4
    local exit_reason=${5:-""}
    
    cat > "$STATUS_FILE" << STATUSEOF
{
    "timestamp": "$(get_iso_timestamp)",
    "loop_count": $loop_count,
    "calls_made_this_hour": $calls_made,
    "max_calls_per_hour": $MAX_CALLS_PER_HOUR,
    "last_action": "$last_action",
    "status": "$status",
    "exit_reason": "$exit_reason",
    "next_reset": "$(get_next_hour_time)"
}
STATUSEOF
}

# Check if we can make another call
can_make_call() {
    local calls_made=0
    if [[ -f "$CALL_COUNT_FILE" ]]; then
        calls_made=$(cat "$CALL_COUNT_FILE")
    fi
    
    if [[ $calls_made -ge $MAX_CALLS_PER_HOUR ]]; then
        return 1  # Cannot make call
    else
        return 0  # Can make call
    fi
}

# Increment call counter
increment_call_counter() {
    local calls_made=0
    if [[ -f "$CALL_COUNT_FILE" ]]; then
        calls_made=$(cat "$CALL_COUNT_FILE")
    fi
    
    ((calls_made++))
    echo "$calls_made" > "$CALL_COUNT_FILE"
    echo "$calls_made"
}

# Wait for rate limit reset with countdown
wait_for_reset() {
    local calls_made=$(cat "$CALL_COUNT_FILE" 2>/dev/null || echo "0")
    log_status "WARN" "Rate limit reached ($calls_made/$MAX_CALLS_PER_HOUR). Waiting for reset..."
    
    # Calculate time until next hour
    local current_minute=$(date +%M)
    local current_second=$(date +%S)
    local wait_time=$(((60 - current_minute - 1) * 60 + (60 - current_second)))
    
    log_status "INFO" "Sleeping for $wait_time seconds until next hour..."
    
    # Countdown display
    while [[ $wait_time -gt 0 ]]; do
        local hours=$((wait_time / 3600))
        local minutes=$(((wait_time % 3600) / 60))
        local seconds=$((wait_time % 60))
        
        printf "\r${YELLOW}Time until reset: %02d:%02d:%02d${NC}" $hours $minutes $seconds
        sleep 1
        ((wait_time--))
    done
    printf "\n"
    
    # Reset counter
    echo "0" > "$CALL_COUNT_FILE"
    echo "$(date +%Y%m%d%H)" > "$TIMESTAMP_FILE"
    log_status "SUCCESS" "Rate limit reset! Ready for new calls."
}

# Check if we should gracefully exit
should_exit_gracefully() {
    log_status "INFO" "DEBUG: Checking exit conditions..." >&2
    
    if [[ ! -f "$EXIT_SIGNALS_FILE" ]]; then
        log_status "INFO" "DEBUG: No exit signals file found, continuing..." >&2
        return 1  # Don't exit, file doesn't exist
    fi
    
    local signals=$(cat "$EXIT_SIGNALS_FILE")
    log_status "INFO" "DEBUG: Exit signals content: $signals" >&2
    
    # Count recent signals (last 5 loops) - with error handling
    local recent_test_loops
    local recent_done_signals  
    local recent_completion_indicators
    
    recent_test_loops=$(echo "$signals" | jq '.test_only_loops | length' 2>/dev/null || echo "0")
    recent_done_signals=$(echo "$signals" | jq '.done_signals | length' 2>/dev/null || echo "0")
    recent_completion_indicators=$(echo "$signals" | jq '.completion_indicators | length' 2>/dev/null || echo "0")
    
    log_status "INFO" "DEBUG: Exit counts - test_loops:$recent_test_loops, done_signals:$recent_done_signals, completion:$recent_completion_indicators" >&2
    
    # Check for exit conditions
    
    # 1. Too many consecutive test-only loops
    if [[ $recent_test_loops -ge $MAX_CONSECUTIVE_TEST_LOOPS ]]; then
        log_status "WARN" "Exit condition: Too many test-focused loops ($recent_test_loops >= $MAX_CONSECUTIVE_TEST_LOOPS)"
        echo "test_saturation"
        return 0
    fi
    
    # 2. Multiple "done" signals
    if [[ $recent_done_signals -ge $MAX_CONSECUTIVE_DONE_SIGNALS ]]; then
        log_status "WARN" "Exit condition: Multiple completion signals ($recent_done_signals >= $MAX_CONSECUTIVE_DONE_SIGNALS)"
        echo "completion_signals"
        return 0
    fi
    
    # 3. Strong completion indicators (but validate against @fix_plan.md)
    if [[ $recent_completion_indicators -ge 2 ]]; then
        # Before exiting, cross-reference with @fix_plan.md to avoid false positives
        if [[ -f "@fix_plan.md" ]]; then
            local todo_count=$(grep -c "TODO\|Status.*TODO\|TODO:" "@fix_plan.md" 2>/dev/null || echo "0")

            if [[ $todo_count -gt 0 ]]; then
                log_status "WARN" "Exit signals indicate completion, but @fix_plan.md has $todo_count TODO items" >&2
                log_status "WARN" "Ignoring stale completion indicators and continuing..." >&2
                # Reset completion indicators to prevent repeated false exits
                signals=$(echo "$signals" | jq '.completion_indicators = []' 2>/dev/null)
                echo "$signals" > "$EXIT_SIGNALS_FILE" 2>/dev/null || true
                # Do NOT exit - echo empty string to continue loop (return 0 would exit with success but not set variable)
                echo ""
                return 0
            else
                log_status "WARN" "Exit condition: Strong completion indicators ($recent_completion_indicators)"
                echo "project_complete"
                return 0
            fi
        else
            log_status "WARN" "Exit condition: Strong completion indicators ($recent_completion_indicators)"
            echo "project_complete"
            return 0
        fi
    fi

    # 4. Check fix_plan.md for completion
    if [[ -f "@fix_plan.md" ]]; then
        local total_items=$(grep -c "^- \[" "@fix_plan.md" 2>/dev/null)
        local completed_items=$(grep -c "^- \[x\]" "@fix_plan.md" 2>/dev/null)
        
        # Handle case where grep returns no matches (exit code 1)
        [[ -z "$total_items" ]] && total_items=0
        [[ -z "$completed_items" ]] && completed_items=0
        
        log_status "INFO" "DEBUG: @fix_plan.md check - total_items:$total_items, completed_items:$completed_items" >&2
        
        if [[ $total_items -gt 0 ]] && [[ $completed_items -eq $total_items ]]; then
            log_status "WARN" "Exit condition: All fix_plan.md items completed ($completed_items/$total_items)" >&2
            echo "plan_complete"
            return 0
        fi
    else
        log_status "INFO" "DEBUG: @fix_plan.md file not found" >&2
    fi
    
    log_status "INFO" "DEBUG: No exit conditions met, continuing loop" >&2
    echo ""  # Return empty string instead of using return code
}

# =============================================================================
# MODERN CLI HELPER FUNCTIONS (Phase 1.1)
# =============================================================================

# Check Claude CLI version for compatibility with modern flags
check_claude_version() {
    local version=$($CLAUDE_CODE_CMD --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)

    if [[ -z "$version" ]]; then
        log_status "WARN" "Cannot detect Claude CLI version, assuming compatible"
        return 0
    fi

    # Compare versions (simplified semver comparison)
    local required="$CLAUDE_MIN_VERSION"

    # Convert to comparable integers (major * 10000 + minor * 100 + patch)
    local ver_parts=(${version//./ })
    local req_parts=(${required//./ })

    local ver_num=$((${ver_parts[0]:-0} * 10000 + ${ver_parts[1]:-0} * 100 + ${ver_parts[2]:-0}))
    local req_num=$((${req_parts[0]:-0} * 10000 + ${req_parts[1]:-0} * 100 + ${req_parts[2]:-0}))

    if [[ $ver_num -lt $req_num ]]; then
        log_status "WARN" "Claude CLI version $version < $required. Some modern features may not work."
        log_status "WARN" "Consider upgrading: npm update -g @anthropic-ai/claude-code"
        return 1
    fi

    log_status "INFO" "Claude CLI version $version (>= $required) - modern features enabled"
    return 0
}

# Validate allowed tools against whitelist
# Returns 0 if valid, 1 if invalid with error message
validate_allowed_tools() {
    local tools_input=$1

    if [[ -z "$tools_input" ]]; then
        return 0  # Empty is valid (uses defaults)
    fi

    # Split by comma
    local IFS=','
    read -ra tools <<< "$tools_input"

    for tool in "${tools[@]}"; do
        # Trim whitespace
        tool=$(echo "$tool" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')

        if [[ -z "$tool" ]]; then
            continue
        fi

        local valid=false

        # Check against valid patterns
        for pattern in "${VALID_TOOL_PATTERNS[@]}"; do
            if [[ "$tool" == "$pattern" ]]; then
                valid=true
                break
            fi

            # Check for Bash(*) pattern - any Bash with parentheses is allowed
            if [[ "$tool" =~ ^Bash\(.+\)$ ]]; then
                valid=true
                break
            fi
        done

        if [[ "$valid" == "false" ]]; then
            echo "Error: Invalid tool in --allowed-tools: '$tool'"
            echo "Valid tools: ${VALID_TOOL_PATTERNS[*]}"
            echo "Note: Bash(...) patterns with any content are allowed (e.g., 'Bash(git *)')"
            return 1
        fi
    done

    return 0
}

# Build loop context for Claude Code session
# Provides loop-specific context via --append-system-prompt
build_loop_context() {
    local loop_count=$1
    local context=""

    # Add loop number
    context="Loop #${loop_count}. "

    # Extract incomplete tasks from @fix_plan.md
    if [[ -f "@fix_plan.md" ]]; then
        local incomplete_tasks=$(grep -c "^- \[ \]" "@fix_plan.md" 2>/dev/null || echo "0")
        context+="Remaining tasks: ${incomplete_tasks}. "
    fi

    # Add circuit breaker state
    if [[ -f ".circuit_breaker_state" ]]; then
        local cb_state=$(jq -r '.state // "UNKNOWN"' .circuit_breaker_state 2>/dev/null)
        if [[ "$cb_state" != "CLOSED" && "$cb_state" != "null" && -n "$cb_state" ]]; then
            context+="Circuit breaker: ${cb_state}. "
        fi
    fi

    # Add previous loop summary (truncated)
    if [[ -f ".response_analysis" ]]; then
        local prev_summary=$(jq -r '.analysis.work_summary // ""' .response_analysis 2>/dev/null | head -c 200)
        if [[ -n "$prev_summary" && "$prev_summary" != "null" ]]; then
            context+="Previous: ${prev_summary}"
        fi
    fi

    # Limit total length to ~500 chars
    echo "${context:0:500}"
}

# Get session file age in hours (cross-platform)
# Returns: age in hours on stdout, or -1 if stat fails
# Note: Returns 0 for files less than 1 hour old
get_session_file_age_hours() {
    local file=$1

    if [[ ! -f "$file" ]]; then
        echo "0"
        return
    fi

    local os_type
    os_type=$(uname)

    local file_mtime
    if [[ "$os_type" == "Darwin" ]]; then
        # macOS (BSD stat)
        file_mtime=$(stat -f %m "$file" 2>/dev/null)
    else
        # Linux (GNU stat)
        file_mtime=$(stat -c %Y "$file" 2>/dev/null)
    fi

    # Handle stat failure - return -1 to indicate error
    # This prevents false expiration when stat fails
    if [[ -z "$file_mtime" || "$file_mtime" == "0" ]]; then
        echo "-1"
        return
    fi

    local current_time
    current_time=$(date +%s)

    local age_seconds=$((current_time - file_mtime))
    local age_hours=$((age_seconds / 3600))

    echo "$age_hours"
}

# Initialize or resume Claude session (with expiration check)
#
# Session Expiration Strategy:
# - Default expiration: 24 hours (configurable via CLAUDE_SESSION_EXPIRY_HOURS)
# - 24 hours chosen because: long enough for multi-day projects, short enough
#   to prevent stale context from causing unpredictable behavior
# - Sessions auto-expire to ensure Claude starts fresh periodically
#
# Returns (stdout):
#   - Session ID string: when resuming a valid, non-expired session
#   - Empty string: when starting new session (no file, expired, or stat error)
#
# Return codes:
#   - 0: Always returns success (caller should check stdout for session ID)
#
init_claude_session() {
    if [[ -f "$CLAUDE_SESSION_FILE" ]]; then
        # Check session age
        local age_hours
        age_hours=$(get_session_file_age_hours "$CLAUDE_SESSION_FILE")

        # Handle stat failure (-1) - treat as needing new session
        # Don't expire sessions when we can't determine age
        if [[ $age_hours -eq -1 ]]; then
            log_status "WARN" "Could not determine session age, starting new session"
            rm -f "$CLAUDE_SESSION_FILE"
            echo ""
            return 0
        fi

        # Check if session has expired
        if [[ $age_hours -ge $CLAUDE_SESSION_EXPIRY_HOURS ]]; then
            log_status "INFO" "Session expired (${age_hours}h old, max ${CLAUDE_SESSION_EXPIRY_HOURS}h), starting new session"
            rm -f "$CLAUDE_SESSION_FILE"
            echo ""
            return 0
        fi

        # Session is valid, try to read it
        local session_id=$(cat "$CLAUDE_SESSION_FILE" 2>/dev/null)
        if [[ -n "$session_id" ]]; then
            log_status "INFO" "Resuming Claude session: ${session_id:0:20}... (${age_hours}h old)"
            echo "$session_id"
            return 0
        fi
    fi

    log_status "INFO" "Starting new Claude session"
    echo ""
}

# Save session ID after successful execution
save_claude_session() {
    local output_file=$1

    # Try to extract session ID from JSON output
    if [[ -f "$output_file" ]]; then
        local session_id=$(jq -r '.metadata.session_id // .session_id // empty' "$output_file" 2>/dev/null)
        if [[ -n "$session_id" && "$session_id" != "null" ]]; then
            echo "$session_id" > "$CLAUDE_SESSION_FILE"
            log_status "INFO" "Saved Claude session: ${session_id:0:20}..."
        fi
    fi
}

# =============================================================================
# SESSION LIFECYCLE MANAGEMENT FUNCTIONS (Phase 1.2)
# =============================================================================

# Get current session ID from Ralph session file
# Returns: session ID string or empty if not found
get_session_id() {
    if [[ ! -f "$RALPH_SESSION_FILE" ]]; then
        echo ""
        return 0
    fi

    # Extract session_id from JSON file (SC2155: separate declare from assign)
    local session_id
    session_id=$(jq -r '.session_id // ""' "$RALPH_SESSION_FILE" 2>/dev/null)
    local jq_status=$?

    # Handle jq failure or null/empty results
    if [[ $jq_status -ne 0 || -z "$session_id" || "$session_id" == "null" ]]; then
        session_id=""
    fi
    echo "$session_id"
    return 0
}

# Reset session with reason logging
# Usage: reset_session "reason_for_reset"
reset_session() {
    local reason=${1:-"manual_reset"}

    # Get current timestamp
    local reset_timestamp
    reset_timestamp=$(get_iso_timestamp)

    # Always create/overwrite the session file using jq for safe JSON escaping
    jq -n \
        --arg session_id "" \
        --arg created_at "" \
        --arg last_used "" \
        --arg reset_at "$reset_timestamp" \
        --arg reset_reason "$reason" \
        '{
            session_id: $session_id,
            created_at: $created_at,
            last_used: $last_used,
            reset_at: $reset_at,
            reset_reason: $reset_reason
        }' > "$RALPH_SESSION_FILE"

    # Also clear the Claude session file for consistency
    rm -f "$CLAUDE_SESSION_FILE" 2>/dev/null

    # Log the session transition (non-fatal to prevent script exit under set -e)
    log_session_transition "active" "reset" "$reason" "${loop_count:-0}" || true

    log_status "INFO" "Session reset: $reason"
}

# Log session state transitions to history file
# Usage: log_session_transition from_state to_state reason loop_number
log_session_transition() {
    local from_state=$1
    local to_state=$2
    local reason=$3
    local loop_number=${4:-0}

    # Get timestamp once (SC2155: separate declare from assign)
    local ts
    ts=$(get_iso_timestamp)

    # Create transition entry using jq for safe JSON (SC2155: separate declare from assign)
    local transition
    transition=$(jq -n -c \
        --arg timestamp "$ts" \
        --arg from_state "$from_state" \
        --arg to_state "$to_state" \
        --arg reason "$reason" \
        --argjson loop_number "$loop_number" \
        '{
            timestamp: $timestamp,
            from_state: $from_state,
            to_state: $to_state,
            reason: $reason,
            loop_number: $loop_number
        }')

    # Read history file defensively - fallback to empty array on any failure
    local history
    if [[ -f "$RALPH_SESSION_HISTORY_FILE" ]]; then
        history=$(cat "$RALPH_SESSION_HISTORY_FILE" 2>/dev/null)
        # Validate JSON, fallback to empty array if corrupted
        if ! echo "$history" | jq empty 2>/dev/null; then
            history='[]'
        fi
    else
        history='[]'
    fi

    # Append transition and keep only last 50 entries
    local updated_history
    updated_history=$(echo "$history" | jq ". += [$transition] | .[-50:]" 2>/dev/null)
    local jq_status=$?

    # Only write if jq succeeded
    if [[ $jq_status -eq 0 && -n "$updated_history" ]]; then
        echo "$updated_history" > "$RALPH_SESSION_HISTORY_FILE"
    else
        # Fallback: start fresh with just this transition
        echo "[$transition]" > "$RALPH_SESSION_HISTORY_FILE"
    fi
}

# Generate a unique session ID using timestamp and random component
generate_session_id() {
    local ts
    ts=$(date +%s)
    local rand
    rand=$RANDOM
    echo "ralph-${ts}-${rand}"
}

# Initialize session tracking (called at loop start)
init_session_tracking() {
    local ts
    ts=$(get_iso_timestamp)

    # Create session file if it doesn't exist
    if [[ ! -f "$RALPH_SESSION_FILE" ]]; then
        local new_session_id
        new_session_id=$(generate_session_id)

        jq -n \
            --arg session_id "$new_session_id" \
            --arg created_at "$ts" \
            --arg last_used "$ts" \
            --arg reset_at "" \
            --arg reset_reason "" \
            '{
                session_id: $session_id,
                created_at: $created_at,
                last_used: $last_used,
                reset_at: $reset_at,
                reset_reason: $reset_reason
            }' > "$RALPH_SESSION_FILE"

        log_status "INFO" "Initialized session tracking (session: $new_session_id)"
        return 0
    fi

    # Validate existing session file
    if ! jq empty "$RALPH_SESSION_FILE" 2>/dev/null; then
        log_status "WARN" "Corrupted session file detected, recreating..."
        local new_session_id
        new_session_id=$(generate_session_id)

        jq -n \
            --arg session_id "$new_session_id" \
            --arg created_at "$ts" \
            --arg last_used "$ts" \
            --arg reset_at "$ts" \
            --arg reset_reason "corrupted_file_recovery" \
            '{
                session_id: $session_id,
                created_at: $created_at,
                last_used: $last_used,
                reset_at: $reset_at,
                reset_reason: $reset_reason
            }' > "$RALPH_SESSION_FILE"
    fi
}

# Update last_used timestamp in session file (called on each loop iteration)
update_session_last_used() {
    if [[ ! -f "$RALPH_SESSION_FILE" ]]; then
        return 0
    fi

    local ts
    ts=$(get_iso_timestamp)

    # Update last_used in existing session file
    local updated
    updated=$(jq --arg last_used "$ts" '.last_used = $last_used' "$RALPH_SESSION_FILE" 2>/dev/null)
    local jq_status=$?

    if [[ $jq_status -eq 0 && -n "$updated" ]]; then
        echo "$updated" > "$RALPH_SESSION_FILE"
    fi
}

# Global array for Claude command arguments (avoids shell injection)
declare -a CLAUDE_CMD_ARGS=()

# Build Claude CLI command with modern flags using array (shell-injection safe)
# Populates global CLAUDE_CMD_ARGS array for direct execution
# Uses -p flag with prompt content (Claude CLI does not have --prompt-file)
build_claude_command() {
    local prompt_file=$1
    local loop_context=$2
    local session_id=$3

    # Reset global array
    CLAUDE_CMD_ARGS=("$CLAUDE_CODE_CMD")

    # Check if prompt file exists
    if [[ ! -f "$prompt_file" ]]; then
        log_status "ERROR" "Prompt file not found: $prompt_file"
        log_status "INFO" "To fix:"
        log_status "INFO" "  1. Create the prompt file: touch $prompt_file"
        log_status "INFO" "  2. Or use a different prompt: --prompt /path/to/your/prompt.md"
        log_status "INFO" "  3. Or use the template: cp templates/PROMPT.md $prompt_file"
        return 1
    fi

    # Add output format flag
    if [[ "$CLAUDE_OUTPUT_FORMAT" == "json" ]]; then
        CLAUDE_CMD_ARGS+=("--output-format" "json")
    fi

    # Add allowed tools (each tool as separate array element)
    if [[ -n "$CLAUDE_ALLOWED_TOOLS" ]]; then
        CLAUDE_CMD_ARGS+=("--allowedTools")
        # Split by comma and add each tool
        local IFS=','
        read -ra tools_array <<< "$CLAUDE_ALLOWED_TOOLS"
        for tool in "${tools_array[@]}"; do
            # Trim whitespace
            tool=$(echo "$tool" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
            if [[ -n "$tool" ]]; then
                CLAUDE_CMD_ARGS+=("$tool")
            fi
        done
    fi

    # Add allowed directories (each directory with its own --add-dir flag)
    if [[ -n "${CLAUDE_ALLOWED_DIRS:-}" ]]; then
        # Split by comma and add each directory with --add-dir
        local IFS=','
        read -ra dirs_array <<< "$CLAUDE_ALLOWED_DIRS"
        for dir in "${dirs_array[@]}"; do
            # Trim whitespace
            dir=$(echo "$dir" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
            if [[ -n "$dir" ]]; then
                CLAUDE_CMD_ARGS+=("--add-dir" "$dir")
            fi
        done
    fi

    # Add session continuity flag
    if [[ "$CLAUDE_USE_CONTINUE" == "true" ]]; then
        CLAUDE_CMD_ARGS+=("--continue")
    fi

    # Add loop context as system prompt (no escaping needed - array handles it)
    if [[ -n "$loop_context" ]]; then
        CLAUDE_CMD_ARGS+=("--append-system-prompt" "$loop_context")
    fi

    # Add project constraints to system prompt (TASK-001 integration)
    if [[ -n "${CONSTRAINTS_CONTENT:-}" ]]; then
        local constraints_prompt="PROJECT CONSTRAINTS (from PROJECT_CONSTRAINTS.md):

The following constraints have been learned from previous development cycles. Review them carefully before implementing to avoid repeating past mistakes.

---

$CONSTRAINTS_CONTENT

---

CRITICAL: Follow all constraints above when implementing changes."
        CLAUDE_CMD_ARGS+=("--append-system-prompt" "$constraints_prompt")
    fi

    # Read prompt file content and use -p flag
    # Note: Claude CLI uses -p for prompts, not --prompt-file (which doesn't exist)
    # Array-based approach maintains shell injection safety
    local prompt_content
    local enhanced_prompt_file="${prompt_file}.ralph_enhanced"

    # Check if memory injection script exists for IbStudy project
    local memory_injection_script=""
    if [[ -f "scripts/inject-memory-context.sh" ]]; then
        memory_injection_script="scripts/inject-memory-context.sh"
    elif [[ -f "../IbStudy/scripts/inject-memory-context.sh" ]]; then
        memory_injection_script="../IbStudy/scripts/inject-memory-context.sh"
    fi

    # Inject memory context if script available and prompt not already enhanced
    if [[ -n "$memory_injection_script" ]] && [[ -x "$memory_injection_script" ]]; then
        if ! grep -q "## CRITICAL: Project Memory References" "$prompt_file" 2>/dev/null; then
            log_status "INFO" "🧠 Injecting memory context into prompt..."
            if "$memory_injection_script" "$prompt_file" "$enhanced_prompt_file" 2>&1 | grep -q "✅"; then
                log_status "INFO" "✅ Memory context injected successfully"
                prompt_content=$(cat "$enhanced_prompt_file")
                # Cleanup enhanced file after reading
                rm -f "$enhanced_prompt_file"
            else
                log_status "WARN" "⚠️  Memory injection failed, using original prompt"
                prompt_content=$(cat "$prompt_file")
            fi
        else
            log_status "INFO" "ℹ️  Memory context already present in prompt"
            prompt_content=$(cat "$prompt_file")
        fi
    else
        # No memory injection script - use prompt as-is
        prompt_content=$(cat "$prompt_file")
    fi

    CLAUDE_CMD_ARGS+=("-p" "$prompt_content")
}

# Auto-detect project type from directory structure (TASK-002)
detect_project_type() {
    local project_root="${1:-.}"

    log_status "INFO" "Detecting project type..."

    # Check for Flutter
    if [[ -f "$project_root/pubspec.yaml" ]]; then
        echo "flutter"
        return 0
    fi

    # Check for Python
    if [[ -f "$project_root/setup.py" ]] || \
       [[ -f "$project_root/pyproject.toml" ]] || \
       [[ -f "$project_root/requirements.txt" ]]; then
        echo "python"
        return 0
    fi

    # Check for Rust
    if [[ -f "$project_root/Cargo.toml" ]]; then
        echo "rust"
        return 0
    fi

    # Check for Node.js
    if [[ -f "$project_root/package.json" ]]; then
        echo "nodejs"
        return 0
    fi

    # Check for Go
    if [[ -f "$project_root/go.mod" ]]; then
        echo "go"
        return 0
    fi

    # Unknown project type - use generic plugin
    echo "generic"
    return 1
}

# Load appropriate plugin for project (TASK-002)
load_project_plugin() {
    local project_root="${1:-.}"
    local plugin_dir="${SCRIPT_DIR}/plugins"

    # Auto-detect if not specified
    if [[ -z "${RALPH_PLUGIN:-}" ]]; then
        RALPH_PLUGIN=$(detect_project_type "$project_root")
    fi

    log_status "INFO" "Loading plugin: $RALPH_PLUGIN"

    # Load plugin file
    local plugin_file="$plugin_dir/${RALPH_PLUGIN}.sh"

    if [[ ! -f "$plugin_file" ]]; then
        log_status "WARN" "Plugin not found: $plugin_file"
        log_status "INFO" "Available plugins:"
        find "$plugin_dir" -maxdepth 1 -name "*.sh" -type f -exec basename {} \; 2>/dev/null || true
        log_status "INFO" "Continuing without plugin support"
        return 1
    fi

    # Source plugin
    source "$plugin_file"

    # Verify required functions exist
    if ! type plugin_name &>/dev/null; then
        log_status "ERROR" "Plugin missing required function: plugin_name()"
        return 1
    fi

    log_status "INFO" "Loaded plugin: $(plugin_name) v$(plugin_version)"
    return 0
}

# Load project constraints from PROJECT_CONSTRAINTS.md (TASK-001)
load_project_constraints() {
    local constraints_file="PROJECT_CONSTRAINTS.md"

    # Reset constraints content
    CONSTRAINTS_CONTENT=""

    if [[ ! -f "$constraints_file" ]]; then
        log_status "INFO" "No PROJECT_CONSTRAINTS.md found - running without constraints"
        return 0
    fi

    log_status "INFO" "Loading project constraints..."

    # Read constraints content using command substitution (more efficient than cat)
    CONSTRAINTS_CONTENT=$(<"$constraints_file")

    # Count constraint sections (headers starting with ##)
    local constraint_count=$(grep -c "^##" "$constraints_file" || echo "0")
    local constraint_lines=$(echo "$CONSTRAINTS_CONTENT" | wc -l)

    log_status "INFO" "Loaded $constraint_count constraint categories ($constraint_lines lines) from PROJECT_CONSTRAINTS.md"

    return 0
}

# Check task prerequisites before execution
# Returns 0 if prerequisites are satisfied or don't exist
# Returns 2 if prerequisites exist but verification fails
check_task_prerequisites() {
    local task_number="$1"
    local task_dir="tasks/$(printf '%03d' $task_number)"

    # Check if task directory exists
    if [[ ! -d "$task_dir" ]]; then
        # No task directory means no prerequisites
        return 0
    fi

    # Check if task has a prerequisite script
    if [[ ! -f "$task_dir/prereq.sh" ]]; then
        # No prerequisite script means Ralph can execute autonomously
        log_status "INFO" "✅ Task $task_number has no prerequisites (autonomous execution)"
        return 0
    fi

    # Task has prerequisites - check if they're satisfied
    if [[ -f "$task_dir/verify.sh" ]]; then
        log_status "INFO" "🔍 Checking prerequisites for Task $task_number..."

        # Run verification script
        local verify_log="$LOG_DIR/verify_task_${task_number}_$(date '+%Y-%m-%d_%H-%M-%S').log"
        if bash "$task_dir/verify.sh" > "$verify_log" 2>&1; then
            log_status "INFO" "✅ Task $task_number prerequisites satisfied"
            cat "$verify_log" >> "$LOG_FILE"
            return 0
        else
            # Prerequisites not satisfied
            log_status "ERROR" "⚠️  Task $task_number prerequisites NOT met"
            log_status "ERROR" ""
            log_status "ERROR" "Verification failed. See details in: $verify_log"
            log_status "ERROR" ""
            log_status "ERROR" "To resolve:"
            log_status "ERROR" "  1. Run the prerequisite script: ./$task_dir/prereq.sh"
            log_status "ERROR" "  2. Verify it succeeded: ./$task_dir/verify.sh"
            log_status "ERROR" "  3. Restart Ralph: ralph --resume"
            log_status "ERROR" ""

            # Show verification output
            cat "$verify_log" >> "$LOG_FILE"
            cat "$verify_log"

            # Exit with prerequisite failure code
            return 2
        fi
    else
        # Has prereq.sh but no verify.sh - warn and continue
        log_status "WARN" "⚠️  Task $task_number has prereq.sh but no verify.sh"
        log_status "WARN" "   Assuming prerequisites are satisfied (no way to verify)"
        return 0
    fi
}

# Extract current task number from @fix_plan.md
# Returns the first uncompleted task number, or 0 if all complete
extract_current_task_number() {
    local fix_plan="${FIX_PLAN_FILE:-@fix_plan.md}"

    if [[ ! -f "$fix_plan" ]]; then
        echo "0"
        return
    fi

    # Find first task that is not marked as complete
    # Looks for lines like: "#### Task 001: ..." followed by "**Status**: TODO"
    local in_task=false
    local task_number=""

    while IFS= read -r line; do
        # Detect task header
        if [[ "$line" =~ ^####[[:space:]]+Task[[:space:]]+([0-9]+): ]]; then
            task_number="${BASH_REMATCH[1]}"
            in_task=true
            continue
        fi

        # Check status line
        if [[ "$in_task" == true ]] && [[ "$line" =~ ^\*\*Status\*\*:[[:space:]]*(TODO|IN[[:space:]]PROGRESS) ]]; then
            # Found uncompleted task
            echo "$task_number"
            return
        fi

        # Exit task context
        if [[ "$in_task" == true ]] && [[ "$line" =~ ^#### ]]; then
            in_task=false
        fi
    done < "$fix_plan"

    # All tasks complete
    echo "0"
}

# Main execution function
execute_claude_code() {
    local timestamp=$(date '+%Y-%m-%d_%H-%M-%S')
    local output_file="$LOG_DIR/claude_output_${timestamp}.log"
    local loop_count=$1
    local calls_made=$(cat "$CALL_COUNT_FILE" 2>/dev/null || echo "0")
    calls_made=$((calls_made + 1))

    # Check if in dry-run mode
    if is_dry_run; then
        log_status "LOOP" "[DRY RUN] Simulating execution (Loop #$loop_count)"
        echo ""
        
        # Simulate the provider call
        local provider="${RALPH_PROVIDER:-claude}"
        simulate_provider_call "$PROMPT_FILE" "$loop_count" "$provider" > "$output_file"
        
        # Show output
        if is_dry_run_verbose; then
            cat "$output_file"
        fi
        
        # Update status for dry run
        update_status "$loop_count" "$calls_made" "dry_run_simulated" "simulated"
        
        # Simulate one iteration and exit
        if [[ $loop_count -ge 1 ]]; then
            log_status "SUCCESS" "[DRY RUN] Simulation complete. Exiting."
            update_status "$loop_count" "$calls_made" "dry_run_complete" "completed"
            # Signal to exit gracefully
            return 100  # Special code for dry run completion
        fi
        
        return 0
    fi

    log_status "LOOP" "Executing Claude Code (Call $calls_made/$MAX_CALLS_PER_HOUR)"
    local timeout_seconds=$((CLAUDE_TIMEOUT_MINUTES * 60))
    log_status "INFO" "⏳ Starting Claude Code execution... (timeout: ${CLAUDE_TIMEOUT_MINUTES}m)"

    # Load project constraints (TASK-001 integration)
    load_project_constraints

    # Build loop context for session continuity
    local loop_context=""
    if [[ "$CLAUDE_USE_CONTINUE" == "true" ]]; then
        loop_context=$(build_loop_context "$loop_count")
        if [[ -n "$loop_context" && "$VERBOSE_PROGRESS" == "true" ]]; then
            log_status "INFO" "Loop context: $loop_context"
        fi
    fi

    # Check Ralph session expiration before initializing Claude session
    # This ensures stale Ralph sessions are reset with proper audit logging
    if [[ -f "$RALPH_SESSION_FILE" ]]; then
        local ralph_status
        ralph_status=$(check_ralph_session_expired "$RALPH_SESSION_FILE" "$((CLAUDE_SESSION_EXPIRY_HOURS * 3600))")
        if [[ "$ralph_status" == "expired" ]]; then
            reset_expired_ralph_session "$RALPH_SESSION_FILE" "ttl_exceeded"
            log_status "INFO" "Ralph session expired and was reset (older than ${CLAUDE_SESSION_EXPIRY_HOURS}h)"
        fi
    fi

    # Initialize or resume session
    local session_id=""
    if [[ "$CLAUDE_USE_CONTINUE" == "true" ]]; then
        session_id=$(init_claude_session)
    fi

    # Build the Claude CLI command with modern flags
    # Note: We use the modern CLI with -p flag when CLAUDE_OUTPUT_FORMAT is "json"
    # For backward compatibility, fall back to stdin piping for text mode
    local use_modern_cli=false

    if [[ "$CLAUDE_OUTPUT_FORMAT" == "json" ]]; then
        # Modern approach: use CLI flags (builds CLAUDE_CMD_ARGS array)
        if build_claude_command "$PROMPT_FILE" "$loop_context" "$session_id"; then
            use_modern_cli=true
            log_status "INFO" "Using modern CLI mode (JSON output)"
        else
            log_status "WARN" "Failed to build modern CLI command, falling back to legacy mode"
        fi
    else
        log_status "INFO" "Using legacy CLI mode (text output)"
    fi

    # Execute Claude Code
    if [[ "$use_modern_cli" == "true" ]]; then
        # Modern execution with command array (shell-injection safe)
        # Execute array directly without bash -c to prevent shell metacharacter interpretation
        if timeout ${timeout_seconds}s "${CLAUDE_CMD_ARGS[@]}" > "$output_file" 2>&1 &
        then
            :  # Continue to wait loop
        else
            log_status "ERROR" "❌ Failed to start Claude Code process (modern mode)"
            log_status "INFO" "To fix:"
            log_status "INFO" "  1. Check if Claude Code is installed: which npx"
            log_status "INFO" "  2. Update Claude Code: npm install -g @anthropic/claude-code@latest"
            log_status "INFO" "  3. Check API key is set: echo \$ANTHROPIC_API_KEY"
            # Fall back to legacy mode
            log_status "INFO" "Falling back to legacy mode..."
            use_modern_cli=false
        fi
    fi

    # Fall back to legacy stdin piping if modern mode failed or not enabled
    if [[ "$use_modern_cli" == "false" ]]; then
        if timeout ${timeout_seconds}s $CLAUDE_CODE_CMD < "$PROMPT_FILE" > "$output_file" 2>&1 &
        then
            :  # Continue to wait loop
        else
            log_status "ERROR" "❌ Failed to start Claude Code process"
            log_status "INFO" "To fix:"
            log_status "INFO" "  1. Verify Claude Code is installed: npx @anthropic/claude-code --version"
            log_status "INFO" "  2. Check API key: export ANTHROPIC_API_KEY=your-key-here"
            log_status "INFO" "  3. Test manually: npx @anthropic/claude-code 'Hello Claude'"
            log_status "INFO" "  4. Check logs for details: tail -100 $output_file"
            return 1
        fi
    fi

    # Get PID and monitor progress
    local claude_pid=$!
    local exit_code

    # Optimize progress loop: skip expensive operations when verbose mode is disabled
    if [[ "$VERBOSE_PROGRESS" == "true" ]]; then
        # Full progress tracking with spinner, file monitoring, and logging
        local progress_counter=0
        while kill -0 $claude_pid 2>/dev/null; do
            progress_counter=$((progress_counter + 1))
            case $((progress_counter % 4)) in
                1) progress_indicator="⠋" ;;
                2) progress_indicator="⠙" ;;
                3) progress_indicator="⠹" ;;
                0) progress_indicator="⠸" ;;
            esac

            # Get last line from output if available
            local last_line=""
            if [[ -f "$output_file" && -s "$output_file" ]]; then
                last_line=$(tail -1 "$output_file" 2>/dev/null | head -c 80)
            fi

            # Update progress file for monitor
            cat > "$PROGRESS_FILE" << EOF
{
    "status": "executing",
    "indicator": "$progress_indicator",
    "elapsed_seconds": $((progress_counter * 10)),
    "last_output": "$last_line",
    "timestamp": "$(date '+%Y-%m-%d %H:%M:%S')"
}
EOF

            # Log progress
            if [[ -n "$last_line" ]]; then
                log_status "INFO" "$progress_indicator Claude Code: $last_line... (${progress_counter}0s)"
            else
                log_status "INFO" "$progress_indicator Claude Code working... (${progress_counter}0s elapsed)"
            fi

            sleep 10
        done

        # Wait for the process to finish and get exit code
        wait $claude_pid
        exit_code=$?
    else
        # Simplified non-verbose mode: just wait for completion (5-10% faster)
        wait $claude_pid
        exit_code=$?
    fi

    if [ $exit_code -eq 0 ]; then
        # Only increment counter on successful execution
        echo "$calls_made" > "$CALL_COUNT_FILE"

        # Clear progress file
        echo '{"status": "completed", "timestamp": "'$(date '+%Y-%m-%d %H:%M:%S')'"}' > "$PROGRESS_FILE"

        log_status "SUCCESS" "✅ Claude Code execution completed successfully"

        # Save session ID from JSON output (Phase 1.1)
        if [[ "$CLAUDE_USE_CONTINUE" == "true" ]]; then
            save_claude_session "$output_file"
        fi

        # Analyze the response
        log_status "INFO" "🔍 Analyzing Claude Code response..."
        analyze_response "$output_file" "$loop_count"
        local analysis_exit_code=$?

        # Update exit signals based on analysis
        update_exit_signals

        # Log analysis summary
        log_analysis_summary

        # Get file change count for circuit breaker
        local files_changed=$(git diff --name-only 2>/dev/null | wc -l || echo 0)
        local has_errors="false"

        # Use shared error detection logic (lib/error_detector.sh)
        if [[ "$(has_errors_in_file "$output_file")" == "true" ]]; then
            has_errors="true"

            # Debug logging: show what triggered error detection
            if [[ "$VERBOSE_PROGRESS" == "true" ]]; then
                log_status "DEBUG" "Error patterns found:"
                get_error_lines "$output_file" 3 | while IFS= read -r line; do
                    log_status "DEBUG" "  $line"
                done
            fi

            log_status "WARN" "Errors detected in output, check: $output_file"
        fi
        local output_length=$(wc -c < "$output_file" 2>/dev/null || echo 0)

        # Record result in circuit breaker
        record_loop_result "$loop_count" "$files_changed" "$has_errors" "$output_length"
        local circuit_result=$?

        if [[ $circuit_result -ne 0 ]]; then
            log_status "WARN" "Circuit breaker opened - halting execution"
            return 3  # Special code for circuit breaker trip
        fi

        return 0
    else
        # Clear progress file on failure
        echo '{"status": "failed", "timestamp": "'$(date '+%Y-%m-%d %H:%M:%S')'"}' > "$PROGRESS_FILE"

        # Check if the failure is due to API 5-hour limit
        if grep -qi "5.*hour.*limit\|limit.*reached.*try.*back\|usage.*limit.*reached" "$output_file"; then
            log_status "ERROR" "🚫 Claude API 5-hour usage limit reached"
            return 2  # Special return code for API limit
        else
            log_status "ERROR" "❌ Claude Code execution failed, check: $output_file"
            return 1
        fi
    fi
}

# Cleanup function
cleanup() {
    log_status "INFO" "Ralph loop interrupted. Cleaning up..."
    reset_session "manual_interrupt"
    update_status "$loop_count" "$(cat "$CALL_COUNT_FILE" 2>/dev/null || echo "0")" "interrupted" "stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Global variable for loop count (needed by cleanup function)
loop_count=0

# Main loop
main() {
    
    log_status "SUCCESS" "🚀 Ralph loop starting with Claude Code"
    log_status "INFO" "Max calls per hour: $MAX_CALLS_PER_HOUR"
    log_status "INFO" "Logs: $LOG_DIR/ | Docs: $DOCS_DIR/ | Status: $STATUS_FILE"
    
    # Check if this is a Ralph project directory
    if [[ ! -f "$PROMPT_FILE" ]]; then
        log_status "ERROR" "Prompt file '$PROMPT_FILE' not found!"
        echo ""

        # Check if this looks like a partial Ralph project
        if [[ -f "@fix_plan.md" ]] || [[ -d "specs" ]] || [[ -f "@AGENT.md" ]]; then
            echo "This appears to be a Ralph project but is missing PROMPT.md."
            echo "You may need to create or restore the PROMPT.md file."
        else
            echo "This directory is not a Ralph project."
        fi

        echo ""
        echo "To fix this:"
        echo "  1. Create a new project: ralph-setup my-project"
        echo "  2. Import existing requirements: ralph-import requirements.md"
        echo "  3. Navigate to an existing Ralph project directory"
        echo "  4. Or create PROMPT.md manually in this directory"
        echo ""
        echo "Ralph projects should contain: PROMPT.md, @fix_plan.md, specs/, src/, etc."
        exit 1
    fi

    # Validate PRD follows T-RALPH V2.0 standards
    log_status "INFO" ""
    log_status "INFO" "📋 Validating PRD against T-RALPH V2.0 standards..."
    log_status "INFO" "Master standards: /home/dev/Development/ralph-dashboard/docs/specifications/prd-standards/"

    if ! validate_tralph_prd "$PROMPT_FILE" false; then
        echo ""
        log_status "ERROR" "PRD validation failed. Ralph cannot proceed with non-compliant PRD."
        log_status "INFO" ""
        log_status "INFO" "To fix:"
        log_status "INFO" "  1. Read T-RALPH V2.0 standards:"
        log_status "INFO" "     cat /home/dev/Development/ralph-dashboard/docs/specifications/prd-standards/README.md"
        log_status "INFO" ""
        log_status "INFO" "  2. Generate compliant template:"
        log_status "INFO" "     generate_tralph_template \"$PROMPT_FILE\" \"My Feature\" 51"
        log_status "INFO" ""
        log_status "INFO" "  3. Or skip validation (NOT RECOMMENDED):"
        log_status "INFO" "     export SKIP_TRALPH_VALIDATION=true"
        log_status "INFO" ""

        # Allow skipping validation via environment variable (for legacy PRDs)
        if [[ "${SKIP_TRALPH_VALIDATION:-false}" != "true" ]]; then
            exit 1
        else
            log_status "WARN" "⚠️  T-RALPH validation skipped (SKIP_TRALPH_VALIDATION=true)"
            log_status "WARN" "This PRD may not follow best practices for autonomous execution"
        fi
    fi
    echo ""

    # Load project-specific configuration if exists
    if [[ -f ".ralph_config" ]]; then
        log_status "INFO" "Loading project-specific configuration from .ralph_config"
        # shellcheck source=/dev/null
        source ".ralph_config"

        # Log overridden settings
        [[ -n "${CLAUDE_ALLOWED_TOOLS:-}" ]] && log_status "INFO" "  Allowed tools: $CLAUDE_ALLOWED_TOOLS"
        [[ -n "${CLAUDE_ALLOWED_DIRS:-}" ]] && log_status "INFO" "  Allowed dirs: $CLAUDE_ALLOWED_DIRS"
        [[ -n "${MAX_LOOPS:-}" ]] && log_status "INFO" "  Max loops: $MAX_LOOPS"
    fi

    # Initialize session tracking before entering the loop
    init_session_tracking

    # Load project plugin based on auto-detection (TASK-002)
    if load_project_plugin "."; then
        log_status "INFO" "Plugin system initialized"
        # Run pre-flight check if plugin supports it
        if type plugin_preflight &>/dev/null; then
            log_status "INFO" "Running plugin pre-flight check..."
            if plugin_preflight; then
                log_status "SUCCESS" "Pre-flight check passed"
            else
                log_status "ERROR" "Pre-flight check failed - please fix issues before running Ralph"
                exit 1
            fi
        fi
    else
        log_status "INFO" "Continuing without plugin support"
    fi

    log_status "INFO" "Starting main loop..."
    log_status "INFO" "DEBUG: About to enter while loop, loop_count=$loop_count"
    
    while true; do
        loop_count=$((loop_count + 1))
        log_status "INFO" "DEBUG: Successfully incremented loop_count to $loop_count"

        # Update session last_used timestamp
        update_session_last_used

        log_status "INFO" "Loop #$loop_count - calling init_call_tracking..."
        init_call_tracking
        
        log_status "LOOP" "=== Starting Loop #$loop_count ==="
        
        # Update GitHub issue status on first loop
        if [[ $loop_count -eq 1 ]] && _github_sync_is_enabled 2>/dev/null; then
            log_status "INFO" "🔄 Notifying GitHub: Starting work on issue #$GITHUB_ISSUE"
            update_github_issue_status "in_progress" "2-3 hours" || true
        fi
        
        # Check circuit breaker before attempting execution
        if should_halt_execution; then
            reset_session "circuit_breaker_open"
            update_status "$loop_count" "$(cat "$CALL_COUNT_FILE")" "circuit_breaker_open" "halted" "stagnation_detected"
            log_status "ERROR" "🛑 Circuit breaker has opened - execution halted"
            # Update GitHub issue status on circuit breaker
            if _github_sync_is_enabled 2>/dev/null; then
                update_github_issue_status "error" "Circuit breaker opened: Execution halted due to stagnation detection" || true
            fi
            break
        fi

        # Check rate limits
        if ! can_make_call; then
            wait_for_reset
            continue
        fi

        # Check for graceful exit conditions
        local exit_reason=$(should_exit_gracefully)
        if [[ "$exit_reason" != "" ]]; then
            log_status "SUCCESS" "🏁 Graceful exit triggered: $exit_reason"
            reset_session "project_complete"
            update_status "$loop_count" "$(cat "$CALL_COUNT_FILE")" "graceful_exit" "completed" "$exit_reason"
            
            # Update GitHub issue status on completion
            if _github_sync_is_enabled 2>/dev/null; then
                log_status "INFO" "🔄 Notifying GitHub: Work completed on issue #$GITHUB_ISSUE"
                local summary
                summary=$(generate_completion_summary "$loop_count" "" "$(date +%s)")
                update_github_issue_status "completed" "$summary" || true
            fi

            log_status "SUCCESS" "🎉 Ralph has completed the project! Final stats:"
            log_status "INFO" "  - Total loops: $loop_count"
            log_status "INFO" "  - API calls used: $(cat "$CALL_COUNT_FILE")"
            log_status "INFO" "  - Exit reason: $exit_reason"

            break
        fi
        
        # Update status
        local calls_made=$(cat "$CALL_COUNT_FILE" 2>/dev/null || echo "0")
        update_status "$loop_count" "$calls_made" "executing" "running"

        # Check prerequisites for current task
        local current_task
        current_task=$(extract_current_task_number)

        if [[ "$current_task" != "0" ]]; then
            log_status "INFO" "📋 Current task: Task $current_task"

            # Check if prerequisites are satisfied
            if ! check_task_prerequisites "$current_task"; then
                # Prerequisites not met - exit gracefully
                log_status "ERROR" "❌ Cannot proceed without prerequisites"
                update_status "$loop_count" "$(cat "$CALL_COUNT_FILE")" "blocked" "prerequisite_failed"
                # Update GitHub issue status on prerequisite failure
                if _github_sync_is_enabled 2>/dev/null; then
                    update_github_issue_status "error" "Prerequisites not met for Task $current_task" || true
                fi
                exit 2
            fi
        fi

        # Execute Claude Code
        execute_claude_code "$loop_count"
        local exec_result=$?
        
        if [ $exec_result -eq 100 ]; then
            # Dry run completed - exit gracefully
            reset_session "dry_run_complete"
            update_status "$loop_count" "$(cat "$CALL_COUNT_FILE")" "dry_run_complete" "completed"
            log_status "SUCCESS" "🏁 Dry run completed successfully"
            break
        elif [ $exec_result -eq 0 ]; then
            update_status "$loop_count" "$(cat "$CALL_COUNT_FILE")" "completed" "success"

            # Brief pause between successful executions
            sleep 5
        elif [ $exec_result -eq 3 ]; then
            # Circuit breaker opened
            reset_session "circuit_breaker_trip"
            update_status "$loop_count" "$(cat "$CALL_COUNT_FILE")" "circuit_breaker_open" "halted" "stagnation_detected"
            log_status "ERROR" "🛑 Circuit breaker has opened - halting loop"
            log_status "INFO" "Run 'ralph --reset-circuit' to reset the circuit breaker after addressing issues"
            # Update GitHub issue status on circuit breaker trip
            if _github_sync_is_enabled 2>/dev/null; then
                update_github_issue_status "error" "Circuit breaker opened during loop execution: Stagnation detected" || true
            fi
            break
        elif [ $exec_result -eq 2 ]; then
            # API 5-hour limit reached - handle specially
            update_status "$loop_count" "$(cat "$CALL_COUNT_FILE")" "api_limit" "paused"
            log_status "WARN" "🛑 Claude API 5-hour limit reached!"
            # Update GitHub issue status on API limit
            if _github_sync_is_enabled 2>/dev/null; then
                update_github_issue_status "paused" "Claude API 5-hour usage limit reached - waiting for reset" || true
            fi
            
            # Ask user whether to wait or exit
            echo -e "\n${YELLOW}The Claude API 5-hour usage limit has been reached.${NC}"
            echo -e "${YELLOW}You can either:${NC}"
            echo -e "  ${GREEN}1)${NC} Wait for the limit to reset (usually within an hour)"
            echo -e "  ${GREEN}2)${NC} Exit the loop and try again later"
            echo -e "\n${BLUE}Choose an option (1 or 2):${NC} "
            
            # Read user input with timeout
            read -t 30 -n 1 user_choice
            echo  # New line after input
            
            if [[ "$user_choice" == "2" ]] || [[ -z "$user_choice" ]]; then
                log_status "INFO" "User chose to exit (or timed out). Exiting loop..."
                update_status "$loop_count" "$(cat "$CALL_COUNT_FILE")" "api_limit_exit" "stopped" "api_5hour_limit"
                # Update GitHub issue status on API limit exit
                if _github_sync_is_enabled 2>/dev/null; then
                    update_github_issue_status "paused" "Execution paused due to Claude API 5-hour limit" || true
                fi
                break
            else
                log_status "INFO" "User chose to wait. Waiting for API limit reset..."
                # Wait for longer period when API limit is hit
                local wait_minutes=60
                log_status "INFO" "Waiting $wait_minutes minutes before retrying..."
                
                # Countdown display
                local wait_seconds=$((wait_minutes * 60))
                while [[ $wait_seconds -gt 0 ]]; do
                    local minutes=$((wait_seconds / 60))
                    local seconds=$((wait_seconds % 60))
                    printf "\r${YELLOW}Time until retry: %02d:%02d${NC}" $minutes $seconds
                    sleep 1
                    ((wait_seconds--))
                done
                printf "\n"
            fi
        else
            update_status "$loop_count" "$(cat "$CALL_COUNT_FILE")" "failed" "error"
            log_status "WARN" "Execution failed, waiting 30 seconds before retry..."
            sleep 30
        fi
        
        log_status "LOOP" "=== Completed Loop #$loop_count ==="
    done
}

# Help function
show_help() {
    cat << HELPEOF
Ralph Loop for Claude Code

Usage: $0 [OPTIONS]

IMPORTANT: This command must be run from a Ralph project directory.
           Use 'ralph-setup project-name' to create a new project first.

Options:
    -h, --help              Show this help message
    -c, --calls NUM         Set max calls per hour (default: $MAX_CALLS_PER_HOUR)
    -p, --prompt FILE       Set prompt file (default: $PROMPT_FILE)
    -s, --status            Show current status and exit
    -m, --monitor           Start with tmux session and live monitor (requires tmux)
    -v, --verbose           Show detailed progress updates during execution
    -t, --timeout MIN       Set Claude Code execution timeout in minutes (default: $CLAUDE_TIMEOUT_MINUTES)
    --clean                 Reset all Ralph state files (exit signals, call count, circuit breaker)
    --check-permissions     Review and approve permissions required by @fix_plan.md
    --reset-circuit         Reset circuit breaker to CLOSED state
    --circuit-status        Show circuit breaker status and exit
    --reset-session         Reset session state and exit (clears session continuity)

Config Options (Phase 3-003):
    --show-config           Display current configuration and exit
    --show-config-verbose   Display current configuration with source info
    --config FILE           Load configuration from specific file

Dry Run Options (Phase 3-002):
    --dry-run [FILE]        Simulate execution without API calls or file changes
                            Optional: specify PRD file to validate (default: PROMPT.md)
    --dry-run-verbose       Show verbose output during dry run (prompt preview, etc.)
    --validate-all DIR      Validate all PRDs in directory (default: specs/)

Modern CLI Options (Phase 1.1):
    --output-format FORMAT  Set Claude output format: json or text (default: $CLAUDE_OUTPUT_FORMAT)
    --allowed-tools TOOLS   Comma-separated list of allowed tools (default: $CLAUDE_ALLOWED_TOOLS)
    --no-continue           Disable session continuity across loops
    --session-expiry HOURS  Set session expiration time in hours (default: $CLAUDE_SESSION_EXPIRY_HOURS)

GitHub Integration Options (Phase 5-001):
    --import-github-issue REPO#NUM  Import single GitHub issue as PRD (e.g., owner/repo#123)
    --import-github-issues REPO     Import multiple issues from repository
                                    Supports: --label, --milestone, --state filters
    --github-label LABEL            Filter by label (can be used multiple times)
    --github-milestone NAME         Filter by milestone name
    --github-state STATE            Filter by state: open, closed, all (default: open)
    --github-limit NUM              Limit number of issues to import (default: 50)
    --github-dry-run                Preview import without creating files
    --github-output-dir DIR         Output directory for PRDs (default: specs/tasks)

Files created:
    - $LOG_DIR/: All execution logs
    - $DOCS_DIR/: Generated documentation
    - $STATUS_FILE: Current status (JSON)
    - .ralph_session: Session lifecycle tracking
    - .ralph_session_history: Session transition history (last 50)
    - .call_count: API call counter for rate limiting
    - .last_reset: Timestamp of last rate limit reset

Example workflow:
    ralph-setup my-project     # Create project
    cd my-project             # Enter project directory
    $0 --monitor             # Start Ralph with monitoring

Examples:
    $0 --calls 50 --prompt my_prompt.md
    $0 --monitor             # Start with integrated tmux monitoring
    $0 --monitor --timeout 30   # 30-minute timeout for complex tasks
    $0 --verbose --timeout 5    # 5-minute timeout with detailed progress
    $0 --output-format text     # Use legacy text output format
    $0 --no-continue            # Disable session continuity
    $0 --session-expiry 48      # 48-hour session expiration

Dry Run Examples:
    $0 --dry-run                # Dry run with PROMPT.md
    $0 --dry-run specs/TASK-001.md   # Dry run specific PRD
    $0 --dry-run --dry-run-verbose   # Verbose dry run output
    $0 --validate-all specs/    # Validate all PRDs in specs directory

GitHub Import Examples:
    $0 --import-github-issue owner/repo#123           # Import single issue
    $0 --import-github-issues owner/repo              # Import all open issues
    $0 --import-github-issues owner/repo --github-label ralph --github-label ready
    $0 --import-github-issues owner/repo --github-milestone "v1.0"
    $0 --import-github-issues owner/repo --github-dry-run  # Preview only

GitHub Sync Examples:
    $0 --github-issue owner/repo#123                  # Sync status with issue
    $0 --github-issue owner/repo#123 --github-enabled # Enable bidirectional sync

HELPEOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -c|--calls)
            MAX_CALLS_PER_HOUR="$2"
            shift 2
            ;;
        -p|--prompt)
            PROMPT_FILE="$2"
            shift 2
            ;;
        -s|--status)
            if [[ -f "$STATUS_FILE" ]]; then
                echo "Current Status:"
                cat "$STATUS_FILE" | jq . 2>/dev/null || cat "$STATUS_FILE"
            else
                echo "No status file found. Ralph may not be running."
            fi
            exit 0
            ;;
        -m|--monitor)
            USE_TMUX=true
            shift
            ;;
        -v|--verbose)
            VERBOSE_PROGRESS=true
            shift
            ;;
        -t|--timeout)
            if [[ "$2" =~ ^[1-9][0-9]*$ ]] && [[ "$2" -le 120 ]]; then
                CLAUDE_TIMEOUT_MINUTES="$2"
            else
                echo "Error: Timeout must be a positive integer between 1 and 120 minutes"
                exit 1
            fi
            shift 2
            ;;
        --clean)
            # Reset all Ralph state files
            reset_state_files
            exit 0
            ;;
        --reset-circuit)
            # Source the circuit breaker library
            SCRIPT_DIR="$(dirname "${BASH_SOURCE[0]}")"
            source "$SCRIPT_DIR/lib/circuit_breaker.sh"
            source "$SCRIPT_DIR/lib/date_utils.sh"
            reset_circuit_breaker "Manual reset via command line"
            reset_session "manual_circuit_reset"
            exit 0
            ;;
        --reset-session)
            # Reset session state only
            SCRIPT_DIR="$(dirname "${BASH_SOURCE[0]}")"
            source "$SCRIPT_DIR/lib/date_utils.sh"
            reset_session "manual_reset_flag"
            echo -e "\033[0;32m✅ Session state reset successfully\033[0m"
            exit 0
            ;;
        --circuit-status)
            # Source the circuit breaker library
            SCRIPT_DIR="$(dirname "${BASH_SOURCE[0]}")"
            source "$SCRIPT_DIR/lib/circuit_breaker.sh"
            show_circuit_status
            exit 0
            ;;
        --show-config)
            show_config
            echo ""
            show_config_summary
            exit 0
            ;;
        --show-config-verbose)
            show_config --verbose
            echo ""
            show_config_summary
            exit 0
            ;;
        --config)
            if [[ ! -f "$2" ]]; then
                echo "Error: Config file not found: $2" >&2
                exit 1
            fi
            if ! validate_config "$2"; then
                exit 1
            fi
            # Reload config from specified file
            if ! _config_load_file "$2" "cli"; then
                echo "Error: Failed to load config from $2" >&2
                exit 1
            fi
            shift 2
            ;;
        --output-format)
            if [[ "$2" == "json" || "$2" == "text" ]]; then
                CLAUDE_OUTPUT_FORMAT="$2"
            else
                echo "Error: --output-format must be 'json' or 'text'"
                exit 1
            fi
            shift 2
            ;;
        --allowed-tools)
            if ! validate_allowed_tools "$2"; then
                exit 1
            fi
            CLAUDE_ALLOWED_TOOLS="$2"
            shift 2
            ;;
        --no-continue)
            CLAUDE_USE_CONTINUE=false
            shift
            ;;
        --session-expiry)
            if [[ -z "$2" || ! "$2" =~ ^[1-9][0-9]*$ ]]; then
                echo "Error: --session-expiry requires a positive integer (hours)"
                exit 1
            fi
            CLAUDE_SESSION_EXPIRY_HOURS="$2"
            shift 2
            ;;
        --check-permissions)
            # Run pre-flight permission check
            if run_preflight_check "@fix_plan.md" ".ralph_config" "true"; then
                echo "✓ Permission check complete"
                exit 0
            else
                echo "✗ Permission check failed"
                exit 1
            fi
            ;;
        --dry-run)
            # Dry run mode - simulate without API calls
            DRY_RUN_MODE=true
            # Check if next argument is a file (not another flag)
            if [[ -n "${2:-}" ]] && [[ ! "$2" =~ ^-- ]]; then
                DRY_RUN_PRD_FILE="$2"
                shift 2
            else
                DRY_RUN_PRD_FILE="$PROMPT_FILE"
                shift
            fi
            ;;
        --dry-run-verbose)
            DRY_RUN_VERBOSE=true
            shift
            ;;
        --validate-all)
            # Validate all PRDs in directory
            VALIDATE_ALL_DIR="${2:-specs}"
            source "$SCRIPT_DIR/lib/dry_run.sh"
            echo ""
            if validate_all_prds "$VALIDATE_ALL_DIR"; then
                echo ""
                echo -e "\033[0;32m✓ All PRDs are valid\033[0m"
                exit 0
            else
                echo ""
                echo -e "\033[0;31m✗ Some PRDs have validation errors\033[0m"
                exit 1
            fi
            ;;
        --import-github-issue)
            # Import single GitHub issue as PRD
            GITHUB_IMPORT_ISSUE="$2"
            shift 2
            ;;
        --import-github-issues)
            # Import multiple GitHub issues
            GITHUB_IMPORT_REPO="$2"
            shift 2
            ;;
        --github-label)
            # Add label filter for GitHub import
            GITHUB_LABELS+=("$2")
            shift 2
            ;;
        --github-milestone)
            # Add milestone filter for GitHub import
            GITHUB_MILESTONE="$2"
            shift 2
            ;;
        --github-state)
            # Set state filter for GitHub import
            GITHUB_STATE="$2"
            shift 2
            ;;
        --github-limit)
            # Set limit for GitHub import
            GITHUB_LIMIT="$2"
            shift 2
            ;;
        --github-dry-run)
            # Enable dry-run mode for GitHub import
            GITHUB_DRY_RUN=true
            shift
            ;;
        --github-output-dir)
            # Set output directory for imported PRDs
            GITHUB_OUTPUT_DIR="$2"
            shift 2
            ;;
        --github-issue)
            # Specify GitHub issue for status synchronization
            # Format: owner/repo#number or https://github.com/owner/repo/issues/number
            GITHUB_ISSUE_SPEC="$2"
            shift 2
            ;;
        --github-enabled)
            # Enable GitHub sync (requires GITHUB_TOKEN and --github-issue)
            GITHUB_SYNC_ENABLED="true"
            shift
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Sync CLI arguments back to config (CLI overrides everything)
set_config "limits.max_calls_per_hour" "$MAX_CALLS_PER_HOUR" "cli"
set_config "output.format" "$CLAUDE_OUTPUT_FORMAT" "cli"
set_config "execution.allowed_tools" "$CLAUDE_ALLOWED_TOOLS" "cli"
set_config "execution.continue_session" "$CLAUDE_USE_CONTINUE" "cli"
set_config "session.expiry_hours" "$CLAUDE_SESSION_EXPIRY_HOURS" "cli"

# Export config to environment variables for child processes
export_config_to_env

# Handle GitHub issue sync setup (Phase 5-002)
if [[ -n "${GITHUB_ISSUE_SPEC:-}" ]]; then
    # Parse the GitHub issue reference
    if parse_github_ref "$GITHUB_ISSUE_SPEC" 2>/dev/null; then
        export GITHUB_REPO="${GITHUB_OWNER}/${GITHUB_REPO}"
        export GITHUB_ISSUE="$GITHUB_ISSUE"
        
        if [[ "$GITHUB_SYNC_ENABLED" == "true" ]]; then
            log_status "INFO" "🔗 GitHub sync enabled for issue: $GITHUB_REPO#$GITHUB_ISSUE"
            
            # Verify GitHub token is available
            if [[ -z "${GITHUB_TOKEN:-${RALPH_GITHUB_TOKEN:-}}" ]]; then
                log_status "WARN" "GitHub sync enabled but GITHUB_TOKEN not set"
                log_status "INFO" "Set GITHUB_TOKEN environment variable for write access"
            fi
        else
            log_status "INFO" "GitHub issue tracking: $GITHUB_REPO#$GITHUB_ISSUE (sync disabled)"
        fi
    else
        echo "ERROR: Invalid GitHub issue format: $GITHUB_ISSUE_SPEC" >&2
        echo "Expected: owner/repo#123 or https://github.com/owner/repo/issues/123" >&2
        exit 1
    fi
fi

# Only execute when run directly, not when sourced
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    # Handle GitHub issue import (Phase 5-001)
    if [[ -n "$GITHUB_IMPORT_ISSUE" ]]; then
        source "$SCRIPT_DIR/lib/github_to_prd.sh"
        
        echo "Importing GitHub issue: $GITHUB_IMPORT_ISSUE"
        echo ""
        
        # Parse owner/repo#number format
        if ! parse_github_ref "$GITHUB_IMPORT_ISSUE"; then
            exit 1
        fi
        
        local repo
        repo=$(get_github_repo_string)
        
        local dry_run_flag=""
        [[ "$GITHUB_DRY_RUN" == true ]] && dry_run_flag="--dry-run"
        
        if ! convert_issue_to_prd "$repo" "$GITHUB_ISSUE" \
                --output-dir "$GITHUB_OUTPUT_DIR" \
                $dry_run_flag; then
            echo "ERROR: Failed to import issue" >&2
            exit 1
        fi
        exit 0
    fi
    
    if [[ -n "$GITHUB_IMPORT_REPO" ]]; then
        source "$SCRIPT_DIR/lib/github_to_prd.sh"
        
        echo "Importing GitHub issues from: $GITHUB_IMPORT_REPO"
        echo ""
        
        # Build filter arguments
        local filter_args=()
        [[ -n "$GITHUB_STATE" ]] && filter_args+=("--state" "$GITHUB_STATE")
        [[ -n "$GITHUB_MILESTONE" ]] && filter_args+=("--milestone" "$GITHUB_MILESTONE")
        for label in "${GITHUB_LABELS[@]}"; do
            filter_args+=("--label" "$label")
        done
        
        local dry_run_flag=""
        [[ "$GITHUB_DRY_RUN" == true ]] && dry_run_flag="--dry-run"
        
        if ! convert_issues_to_prds "$GITHUB_IMPORT_REPO" \
                --output-dir "$GITHUB_OUTPUT_DIR" \
                --limit "$GITHUB_LIMIT" \
                $dry_run_flag \
                "${filter_args[@]}"; then
            echo "ERROR: Failed to import issues" >&2
            exit 1
        fi
        exit 0
    fi
    
    # Handle dry-run mode (run before validation for quick validation)
    if [[ "$DRY_RUN_MODE" == "true" ]]; then
        # Initialize dry run
        init_dry_run "$DRY_RUN_PRD_FILE"
        
        # Run full dry run simulation
        if run_dry_run "$DRY_RUN_PRD_FILE"; then
            exit 0
        else
            exit 1
        fi
    fi
    
    # Validate working directory before starting
    if ! validate_working_directory; then
        exit 1
    fi

    # Run pre-flight permission check (only if .ralph_config doesn't exist or is outdated)
    if [[ ! -f ".ralph_config" ]] || [[ "@fix_plan.md" -nt ".ralph_config" ]]; then
        echo ""
        log_status "INFO" "🔍 Running permission pre-flight check..."
        if ! run_preflight_check "@fix_plan.md" ".ralph_config" "false"; then
            log_status "ERROR" "Permission check failed. Ralph cannot proceed without required permissions."
            log_status "INFO" "Tip: Run 'ralph --check-permissions' to review and approve permissions."
            exit 1
        fi
        echo ""
    fi

    # If tmux mode requested, set it up
    if [[ "$USE_TMUX" == "true" ]]; then
        check_tmux_available
        setup_tmux_session
    fi

    # Start the main loop
    main
fi
