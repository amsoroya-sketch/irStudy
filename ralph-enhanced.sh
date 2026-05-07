#!/bin/bash
# Ralph Enhanced - With Context Budget Tracking
# Version: 2.0
# Enhancements:
# - Token usage monitoring per iteration
# - Skill invocation tracking
# - Context budget alerts
# - Learning pattern detection

set -e

# Default configuration
MAX_ITERATIONS=100
USE_MONITOR=false

# Parse command-line arguments
for arg in "$@"; do
  case $arg in
    --monitor|-m)
      USE_MONITOR=true
      shift
      ;;
    --help|-h)
      echo "Ralph Enhanced - MoneySmart v2 with Context Optimization"
      echo ""
      echo "Usage:"
      echo "  $0 [OPTIONS] [MAX_ITERATIONS]"
      echo ""
      echo "Options:"
      echo "  --monitor, -m    Launch with tmux split-screen monitor"
      echo "  --help, -h       Show this help message"
      echo ""
      echo "Enhancements:"
      echo "  ✓ Token usage tracking per iteration"
      echo "  ✓ Skill invocation monitoring"
      echo "  ✓ Context budget alerts (warn at 150K/200K)"
      echo "  ✓ Learning pattern auto-detection"
      echo ""
      exit 0
      ;;
    [0-9]*)
      MAX_ITERATIONS=$arg
      shift
      ;;
  esac
done

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PRD_FILE="$SCRIPT_DIR/prd-sprint-1.json"
PROMPT_FILE="$SCRIPT_DIR/prompt.md"
PROGRESS_FILE="$SCRIPT_DIR/progress.txt"
CONTEXT_FILE="$SCRIPT_DIR/.ralph_context.md"
CLAUDE_CMD="claude"

# ✅ NEW: Context tracking configuration
MAX_CONTEXT_TOKENS=200000
CONTEXT_WARNING_THRESHOLD=150000
CONTEXT_CRITICAL_THRESHOLD=180000
ITERATION_TOKEN_LOG="$SCRIPT_DIR/ralph_context_usage.log"
SKILL_USAGE_LOG="$SCRIPT_DIR/ralph_skill_usage.log"
LEARNING_LOG="$SCRIPT_DIR/ralph_learning_patterns.log"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Initialize progress file
if [ ! -f "$PROGRESS_FILE" ]; then
  echo "# Ralph Enhanced Progress Log - MoneySmart v2" > "$PROGRESS_FILE"
  echo "Started: $(date)" >> "$PROGRESS_FILE"
  echo "---" >> "$PROGRESS_FILE"
fi

# ✅ NEW: Initialize context tracking logs
if [ ! -f "$ITERATION_TOKEN_LOG" ]; then
  echo "# Ralph Context Usage Log" > "$ITERATION_TOKEN_LOG"
  echo "# Format: iteration,task_id,skills_loaded,estimated_tokens,timestamp" >> "$ITERATION_TOKEN_LOG"
  echo "# " >> "$ITERATION_TOKEN_LOG"
fi

if [ ! -f "$SKILL_USAGE_LOG" ]; then
  echo "# Ralph Skill Usage Log" > "$SKILL_USAGE_LOG"
  echo "# Format: iteration,task_id,skill_name,invoked_count,timestamp" >> "$SKILL_USAGE_LOG"
  echo "# " >> "$SKILL_USAGE_LOG"
fi

# ✅ NEW: Token estimation function
estimate_tokens() {
  local file=$1
  if [ ! -f "$file" ]; then
    echo 0
    return
  fi

  local char_count=$(wc -c < "$file" 2>/dev/null || echo 0)
  # Rough estimate: 1 token ~= 4 characters
  echo $((char_count / 4))
}

# ✅ NEW: Count skill invocations from context
count_skill_invocations() {
  local context_file=$1
  local skills_loaded=0

  # Count references to skill files
  skills_loaded=$(grep -o "\.claude/skills/[a-z-]*/SKILL\.md" "$context_file" 2>/dev/null | sort -u | wc -l || echo 0)

  echo $skills_loaded
}

# ✅ NEW: Log context usage
log_context_usage() {
  local iteration=$1
  local task_id=$2

  local total_tokens=$(estimate_tokens "$CONTEXT_FILE")
  local skills_loaded=$(count_skill_invocations "$CONTEXT_FILE")
  local timestamp=$(date +%Y-%m-%d\ %H:%M:%S)

  # Log to CSV
  echo "$iteration,$task_id,$skills_loaded,$total_tokens,$timestamp" >> "$ITERATION_TOKEN_LOG"

  # Display status
  echo -e "${CYAN}📊 Context Usage:${NC}"
  echo -e "   Iteration: $iteration"
  echo -e "   Skills loaded: $skills_loaded"
  echo -e "   Estimated tokens: $total_tokens / $MAX_CONTEXT_TOKENS"

  # Warnings
  if [ "$total_tokens" -gt "$CONTEXT_CRITICAL_THRESHOLD" ]; then
    echo -e "${RED}   ⚠️  CRITICAL: Context approaching limit (${total_tokens}/${MAX_CONTEXT_TOKENS})${NC}"
    echo -e "${RED}   Consider reducing skill count or using progressive loading${NC}"
  elif [ "$total_tokens" -gt "$CONTEXT_WARNING_THRESHOLD" ]; then
    echo -e "${YELLOW}   ⚠️  WARNING: Context usage high (${total_tokens}/${MAX_CONTEXT_TOKENS})${NC}"
  else
    echo -e "${GREEN}   ✓ Context usage nominal${NC}"
  fi

  # Calculate iterations remaining before compaction
  local avg_tokens_per_iteration=$((total_tokens / (iteration > 0 ? iteration : 1)))
  local iterations_remaining=$((MAX_CONTEXT_TOKENS / avg_tokens_per_iteration))
  echo -e "   Est. iterations before compaction: ${iterations_remaining}"
}

# ✅ NEW: Detect learning patterns from failures
detect_learning_patterns() {
  local task_id=$1
  local output_file=$2

  # Check for repeated failures (pattern detection)
  local failure_count=$(grep -c "ERROR\|FAILED\|VIOLATION" "$output_file" 2>/dev/null || echo 0)

  if [ "$failure_count" -gt 3 ]; then
    echo -e "${YELLOW}🧠 Learning Pattern Detected:${NC}"
    echo -e "   Task $task_id failed $failure_count times"

    # Extract error patterns
    local error_patterns=$(grep -o "ERROR:.*\|FAILED:.*\|VIOLATION:.*" "$output_file" 2>/dev/null | head -5)

    # Log to learning file
    echo "---" >> "$LEARNING_LOG"
    echo "Task: $task_id" >> "$LEARNING_LOG"
    echo "Timestamp: $(date)" >> "$LEARNING_LOG"
    echo "Failure Count: $failure_count" >> "$LEARNING_LOG"
    echo "Error Patterns:" >> "$LEARNING_LOG"
    echo "$error_patterns" >> "$LEARNING_LOG"
    echo "" >> "$LEARNING_LOG"

    echo -e "${YELLOW}   Logged to: $LEARNING_LOG${NC}"
    echo -e "${YELLOW}   Consider: Auto-filling PROJECT_CONSTRAINTS.md template${NC}"
  fi
}

# ✅ NEW: Display context dashboard
show_context_dashboard() {
  echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "${CYAN}  Ralph Enhanced - Context Dashboard${NC}"
  echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

  if [ -f "$ITERATION_TOKEN_LOG" ]; then
    echo ""
    echo -e "${BLUE}Last 5 Iterations:${NC}"
    tail -5 "$ITERATION_TOKEN_LOG" | while IFS=',' read -r iter task skills tokens ts; do
      if [ "$iter" != "#" ] && [ "$iter" != "iteration" ]; then
        echo -e "  Iteration $iter ($task): $tokens tokens, $skills skills - $ts"
      fi
    done
  fi

  if [ -f "$SKILL_USAGE_LOG" ]; then
    echo ""
    echo -e "${BLUE}Top Skills Used:${NC}"
    tail -20 "$SKILL_USAGE_LOG" | cut -d',' -f3 | sort | uniq -c | sort -rn | head -5 | while read count skill; do
      echo -e "  $skill: $count invocations"
    done
  fi

  if [ -f "$LEARNING_LOG" ]; then
    local pattern_count=$(grep -c "^Task:" "$LEARNING_LOG" 2>/dev/null || echo 0)
    echo ""
    echo -e "${YELLOW}Learning Patterns Detected: $pattern_count${NC}"
  fi

  echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# Check prerequisites
check_prerequisites() {
  echo -e "${BLUE}Checking prerequisites...${NC}"

  if ! command -v jq &> /dev/null; then
    echo -e "${RED}Error: jq is not installed${NC}"
    exit 1
  fi

  if ! command -v claude &> /dev/null; then
    echo -e "${RED}Error: Claude Code CLI is not installed${NC}"
    exit 1
  fi

  if [ ! -f "$PRD_FILE" ]; then
    echo -e "${RED}Error: PRD file not found: $PRD_FILE${NC}"
    exit 1
  fi

  echo -e "${GREEN}✓ All prerequisites met${NC}"
}

# Get next incomplete task
get_next_task() {
  local task_json=$(jq -r '.userStories[] | select(.passes == false) | @json' "$PRD_FILE" | head -1)

  if [ -z "$task_json" ]; then
    echo ""
    return 1
  fi

  echo "$task_json"
  return 0
}

# Generate context with skill optimization hints
generate_context() {
  local task_json=$1
  local task_id=$(echo "$task_json" | jq -r '.id')
  local task_title=$(echo "$task_json" | jq -r '.title')
  local skills_required=$(echo "$task_json" | jq -r '.skills_required[]?' 2>/dev/null || echo "")

  echo -e "${BLUE}Generating optimized context for task: $task_id${NC}"

  cat > "$CONTEXT_FILE" << EOF
# RALPH Enhanced Execution Context - MoneySmart v2

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## CONTEXT OPTIMIZATION NOTICE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Skills Required for This Task:** $skills_required

**Optimization Directive:**
- Load ONLY skills listed above
- Use progressive loading (SKILL.md only, reference docs on demand)
- Reference PROJECT_CONSTRAINTS.md via \`Read\` (don't duplicate)
- Estimated context budget: 10,000 tokens for this task

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## PART 1: EXECUTION WORKFLOW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

$(cat "$PROMPT_FILE")

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## PART 2: CURRENT TASK - $task_id
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Title:** $task_title

**Full Task JSON:**
\`\`\`json
$task_json
\`\`\`

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## PART 3: BEGIN EXECUTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Execute task $task_id following workflow in PART 1.
EOF

  echo -e "${GREEN}✓ Context file generated with optimization hints${NC}"
}

# Execute Claude with monitoring
execute_claude() {
  local iteration=$1
  local task_json=$2
  local task_id=$(echo "$task_json" | jq -r '.id')

  echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "${PURPLE}  Ralph Enhanced - Iteration $iteration${NC}"
  echo -e "${PURPLE}  Task: $task_id${NC}"
  echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

  # Log context usage BEFORE execution
  log_context_usage "$iteration" "$task_id"

  # Execute Claude
  local output_file="logs/ralph_${task_id}_$(date +%Y%m%d_%H%M%S).log"
  mkdir -p logs

  echo -e "${BLUE}Executing Claude Code...${NC}"

  # Clear session for fresh instance
  rm -f .claude_session_id .claude_continue 2>/dev/null

  if cat "$CONTEXT_FILE" | $CLAUDE_CMD > "$output_file" 2>&1; then
    echo -e "${GREEN}✓ Claude Code execution completed${NC}"

    # ✅ NEW: Detect learning patterns
    detect_learning_patterns "$task_id" "$output_file"

    if grep -q "passes.*true" "$output_file" 2>/dev/null; then
      echo -e "${GREEN}✓ Task marked as complete${NC}"
      return 0
    else
      echo -e "${YELLOW}⚠️  Task not completed in this iteration${NC}"
      return 1
    fi
  else
    echo -e "${RED}✗ Claude Code execution failed${NC}"
    return 1
  fi
}

# Main loop
main() {
  check_prerequisites

  echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "${GREEN}  Ralph Enhanced v2.0 - Context Optimized${NC}"
  echo -e "${GREEN}  Max Iterations: $MAX_ITERATIONS${NC}"
  echo -e "${GREEN}  Context Budget: $MAX_CONTEXT_TOKENS tokens${NC}"
  echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

  local iteration=1

  while [ $iteration -le $MAX_ITERATIONS ]; do
    # Get next task
    local task_json=$(get_next_task)
    if [ -z "$task_json" ]; then
      echo -e "${GREEN}✓ All tasks complete!${NC}"
      show_context_dashboard
      exit 0
    fi

    # Generate context
    generate_context "$task_json"

    # Execute
    if execute_claude "$iteration" "$task_json"; then
      echo -e "${GREEN}✓ Iteration $iteration successful${NC}"
    else
      echo -e "${YELLOW}⚠️  Iteration $iteration completed with warnings${NC}"
    fi

    iteration=$((iteration + 1))
    echo ""
  done

  echo -e "${YELLOW}Max iterations ($MAX_ITERATIONS) reached${NC}"
  show_context_dashboard
}

# Run
main
