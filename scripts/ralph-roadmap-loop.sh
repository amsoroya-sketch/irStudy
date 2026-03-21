#!/bin/bash
# Ralph Roadmap PRD Execution Loop
# Automated execution of roadmap PRDs using Claude CLI

set -e  # Exit on error
set -u  # Exit on undefined variable

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PRD_DIR="$PROJECT_ROOT/clinical-content-prds/roadmap-prds"
STATE_FILE="$PROJECT_ROOT/.ralph-roadmap-state.json"
LOG_DIR="$PROJECT_ROOT/clinical-content-prds/roadmap-prds/logs"
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')

# Create log directory
mkdir -p "$LOG_DIR"

# Initialize state file if doesn't exist
if [ ! -f "$STATE_FILE" ]; then
    cat > "$STATE_FILE" <<EOF
{
  "started_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "current_phase": "week1-critical",
  "completed_prds": [],
  "failed_prds": [],
  "current_prd": null,
  "total_prds": 0,
  "completed_count": 0
}
EOF
    echo "✅ Initialized state file: $STATE_FILE"
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
}

# Function to mark PRD as failed
mark_failed() {
    local prd_name=$1
    local error_msg=$2
    python3 -c "
import json
with open('$STATE_FILE') as f:
    state = json.load(f)
state['failed_prds'].append({'prd': '$prd_name', 'error': '$error_msg', 'timestamp': '$(date -u +%Y-%m-%dT%H:%M:%SZ)'})
with open('$STATE_FILE', 'w') as f:
    json.dump(state, f, indent=2)
"
}

# Function to execute a single PRD
execute_prd() {
    local prd_file=$1
    local prd_name=$(basename "$prd_file" .md)
    local log_file="$LOG_DIR/${prd_name}_${TIMESTAMP}.log"

    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "  Executing: $prd_name"
    echo "  PRD File: $prd_file"
    echo "  Log File: $log_file"
    echo "═══════════════════════════════════════════════════════════════"
    echo ""

    # Update state
    python3 -c "
import json
with open('$STATE_FILE') as f:
    state = json.load(f)
state['current_prd'] = '$prd_name'
with open('$STATE_FILE', 'w') as f:
    json.dump(state, f, indent=2)
"

    # Execute PRD using Claude CLI
    echo "📋 Reading PRD: $prd_file"
    echo ""

    # Build Claude CLI prompt
    PROMPT="You are a senior software engineer implementing this PRD. Follow these steps:

1. **READ THE PRD**: Carefully read the entire PRD from this file: $prd_file

2. **UNDERSTAND REQUIREMENTS**: Identify:
   - Success criteria
   - Technical specifications
   - Implementation steps
   - Acceptance criteria

3. **IMPLEMENT THE PRD**: Execute all implementation steps exactly as specified in the PRD.

4. **TEST YOUR WORK**: Run all test commands specified in the PRD.

5. **VERIFY SUCCESS**: Check that all acceptance criteria are met.

6. **REPORT RESULTS**: Summarize what was completed, what tests passed, and any issues encountered.

IMPORTANT:
- Follow the PRD exactly - don't skip steps
- Run all test commands to verify your work
- If anything fails, report it clearly
- Create all files and scripts as specified
- Use exact file paths from the PRD

PRD to implement: $(basename "$prd_file")

Begin implementation now."

    # Execute with Claude CLI
    if claude "$PROMPT" 2>&1 | tee "$log_file"; then
        echo ""
        echo "✅ PRD $prd_name completed successfully"
        mark_completed "$prd_name"
        return 0
    else
        echo ""
        echo "❌ PRD $prd_name failed"
        mark_failed "$prd_name" "Claude execution failed - see log: $log_file"
        return 1
    fi
}

# Main execution loop
main() {
    echo "═══════════════════════════════════════════════════════════════"
    echo "  Ralph Roadmap PRD Execution Loop"
    echo "  Started: $(date)"
    echo "═══════════════════════════════════════════════════════════════"
    echo ""

    # Find all PRD files in order
    PHASES=("week1-critical" "week2-important" "month2-scaling")

    for phase in "${PHASES[@]}"; do
        phase_dir="$PRD_DIR/$phase"

        if [ ! -d "$phase_dir" ]; then
            echo "⚠️  Phase directory not found: $phase_dir"
            continue
        fi

        echo ""
        echo "═══════════════════════════════════════════════════════════════"
        echo "  Phase: $phase"
        echo "═══════════════════════════════════════════════════════════════"

        # Update state
        python3 -c "
import json
with open('$STATE_FILE') as f:
    state = json.load(f)
state['current_phase'] = '$phase'
with open('$STATE_FILE', 'w') as f:
    json.dump(state, f, indent=2)
"

        # Execute PRDs in this phase
        for prd_file in "$phase_dir"/PRD-*.md; do
            if [ -f "$prd_file" ]; then
                prd_name=$(basename "$prd_file" .md)

                # Check if already completed
                is_completed=$(python3 -c "
import json
with open('$STATE_FILE') as f:
    state = json.load(f)
print('yes' if '$prd_name' in state.get('completed_prds', []) else 'no')
")

                if [ "$is_completed" = "yes" ]; then
                    echo "⏭️  Skipping (already completed): $prd_name"
                    continue
                fi

                # Execute PRD
                if execute_prd "$prd_file"; then
                    echo "✅ Success: $prd_name"
                else
                    echo "❌ Failed: $prd_name"
                    echo "   Check log: $LOG_DIR/${prd_name}_${TIMESTAMP}.log"

                    # Ask user if they want to continue
                    echo ""
                    read -p "Continue to next PRD? (y/n) " -n 1 -r
                    echo
                    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                        echo "❌ Stopping execution"
                        exit 1
                    fi
                fi

                # Rate limiting (Claude API)
                echo "⏸️  Waiting 5 seconds before next PRD..."
                sleep 5
            fi
        done
    done

    # Final summary
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "  Execution Complete"
    echo "═══════════════════════════════════════════════════════════════"
    echo ""

    python3 -c "
import json
with open('$STATE_FILE') as f:
    state = json.load(f)

print(f\"Total PRDs: {state.get('total_prds', 0)}\")
print(f\"Completed: {state['completed_count']}\")
print(f\"Failed: {len(state.get('failed_prds', []))}\")
print(f\"Success Rate: {state['completed_count'] / max(state.get('total_prds', 1), 1) * 100:.1f}%\")
print()
print('Completed PRDs:')
for prd in state.get('completed_prds', []):
    print(f'  ✅ {prd}')

if state.get('failed_prds'):
    print()
    print('Failed PRDs:')
    for failed in state['failed_prds']:
        print(f\"  ❌ {failed['prd']}: {failed['error']}\")
"
}

# Run main function
main

echo ""
echo "View state: cat $STATE_FILE"
echo "View logs: ls -lh $LOG_DIR/"
