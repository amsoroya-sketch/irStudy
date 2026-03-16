#!/bin/bash
#
# Ralph Loop - Week 2 AI OSCE Implementation
# Continues from PRD_001 (migration complete) through PRD_005
#

set -euo pipefail

PROJECT_ROOT="/home/dev/Development/irStudy"
STATE_FILE="$PROJECT_ROOT/.ralph-loop-state.json"
LOG_FILE="$PROJECT_ROOT/ralph-week2.log"

cd "$PROJECT_ROOT"

echo "==================================================================="
echo "RALPH LOOP - Week 2 AI OSCE Implementation"
echo "==================================================================="
echo "Started: $(date)"
echo ""

# Read current state
if [ ! -f "$STATE_FILE" ]; then
    echo "ERROR: State file not found: $STATE_FILE"
    exit 1
fi

CURRENT_PRD=$(jq -r '.current_prd' "$STATE_FILE")
CURRENT_TASK=$(jq -r '.current_task' "$STATE_FILE")

echo "Current PRD: $CURRENT_PRD"
echo "Current Task: $CURRENT_TASK"
echo ""

# PRD Queue
PRD_QUEUE=(
    "ai-osce-ralph-prds/PRD_AI_OSCE_001_DATABASE_AND_APIS.md"
    "ai-osce-ralph-prds/PRD_AI_OSCE_002_AI_INTEGRATION.md"
    "ai-osce-ralph-prds/PRD_AI_OSCE_003_WEBSOCKET_INFRASTRUCTURE.md"
    "ai-osce-ralph-prds/PRD_AI_OSCE_004_SCORING_SYSTEM.md"
    "ai-osce-ralph-prds/PRD_AI_OSCE_005_FRONTEND_IMPLEMENTATION.md"
)

# Start with PRD_001 completion (API endpoints + tests)
echo "==================================================================="
echo "STEP 1: Complete PRD_001 (API Endpoints + Tests)"
echo "==================================================================="

PROMPT=$(cat <<'ENDPROMPT'
You are the project-manager-coordinator for the irStudy AI OSCE implementation.

CONTEXT:
- Week 1 (Shared Infrastructure) is COMPLETE
- PRD_001 Database Migration is COMPLETE:
  * 4 tables created: patient_personas, mock_exams, ai_osce_attempts, ai_osce_scores
  * 5 user_progress columns added
  * Models exist in backend/src/db/models.py

CURRENT TASK: Complete PRD_001 API endpoints + integration tests

DELEGATION INSTRUCTIONS:
1. Delegate to rust-ffi-expert to implement 6 API endpoints:
   - GET /api/v1/patient-personas (list with filters)
   - GET /api/v1/patient-personas/{persona_id}
   - POST /api/v1/osce-sessions (create new session)
   - GET /api/v1/osce-sessions/{attempt_id}
   - GET /api/v1/osce-sessions/{attempt_id}/transcript
   - GET /api/v1/osce-sessions/{attempt_id}/score

2. Ensure rust-ffi-expert:
   - Uses ai_osce_attempts and ai_osce_scores table names
   - Gets all secrets from Vault (zero hardcoded credentials)
   - Implements JWT authentication on all endpoints
   - Follows patterns in backend/src/api/v1/users.py

3. After API implementation, delegate to testing-qa-expert:
   - Write integration tests in backend/tests/test_api/test_ai_osce.py
   - Target: ≥70% coverage, 100% pass rate
   - Security tests in backend/tests/test_security/test_ai_osce_security.py

CRITICAL: Report back when PRD_001 is COMPLETE (APIs + tests passing).

BEGIN IMMEDIATELY.
ENDPROMPT
)

echo "$PROMPT" | claude -p --model claude-sonnet-4-5-20250929 | tee -a "$LOG_FILE"

echo ""
echo "==================================================================="
echo "Ralph Week 2 Loop - Monitoring Progress"
echo "==================================================================="
echo "Log file: $LOG_FILE"
echo "Tmux session: ralph-week2"
echo ""
echo "To monitor: tmux attach -t ralph-week2"
echo "To check logs: tail -f $LOG_FILE"
