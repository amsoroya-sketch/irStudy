#!/bin/bash
#
# Ralph Loop - Continue PRD_002 through PRD_005
# Runs in tmux session for autonomous implementation
#

set -euo pipefail

PROJECT_ROOT="/home/dev/Development/irStudy"
LOG_FILE="$PROJECT_ROOT/ralph-week2-continue.log"

cd "$PROJECT_ROOT"

echo "==================================================================="
echo "RALPH LOOP - Continue Week 2 PRDs (002-005)"
echo "==================================================================="
echo "Started: $(date)"
echo ""

# Create comprehensive prompt for Claude
RALPH_PROMPT=$(cat <<'ENDPROMPT'
You are the project-manager-coordinator continuing Week 2 AI OSCE implementation.

## COMPLETED
✅ PRD_001: Database & APIs (100% - 31/31 tests passing)

## CURRENT TASK
Implement PRD_002 through PRD_005 sequentially with validation gates.

## IMPLEMENTATION GUIDE LOCATION
Read: /home/dev/Development/irStudy/PRD_002_IMPLEMENTATION_GUIDE.md

## PRD LOCATIONS
- PRD_002: /home/dev/Development/irStudy/ai-osce-ralph-prds/PRD_AI_OSCE_002_AI_INTEGRATION.md
- PRD_003: /home/dev/Development/irStudy/ai-osce-ralph-prds/PRD_AI_OSCE_003_WEBSOCKET_INFRASTRUCTURE.md
- PRD_004: /home/dev/Development/irStudy/ai-osce-ralph-prds/PRD_AI_OSCE_004_SCORING_SYSTEM.md
- PRD_005: /home/dev/Development/irStudy/ai-osce-ralph-prds/PRD_AI_OSCE_005_FRONTEND_IMPLEMENTATION.md

## SEQUENTIAL IMPLEMENTATION PLAN

### PRD_002: AI Integration (22 hours) - START HERE

**Phase 1: AI Patient Foundation (8 hours)**
Delegate to: rust-ffi-expert

Files to create:
- backend/src/ai/__init__.py
- backend/src/ai/prompts/__init__.py
- backend/src/ai/prompts/patient_system_prompt.py
- backend/src/ai/ai_patient.py
- backend/tests/test_ai/__init__.py
- backend/tests/test_ai/test_ai_patient.py (TDD - write FIRST)

Critical constraints:
1. TDD: Write tests FIRST, confirm they fail, then implement
2. Vault integration: secret/ai-osce/claude-api-key (NO hardcoded keys)
3. Claude API: model=claude-3-5-sonnet-20250219, temp=0.7
4. Progressive disclosure from persona.symptoms JSONB
5. Response time <3 seconds target

Validation checklist:
- [ ] Tests written first and initially failing (RED)
- [ ] Implementation complete
- [ ] All tests passing (GREEN)
- [ ] No hardcoded credentials: grep -r "sk-ant-" backend/src/ai/ = empty
- [ ] Vault integration working
- [ ] Response generated successfully

**Phase 2: Emotional State Machine (4 hours)**
Delegate to: rust-ffi-expert

Files to create:
- backend/src/ai/emotional_state.py
- backend/tests/test_ai/test_emotional_state.py

5 states: ANXIOUS_GUARDED → CAUTIOUSLY_OPEN → TRUSTING → DEFENSIVE → WITHDRAWN
Redis namespace: osce:session:{session_id}:emotional_state

**Phase 3: RAG Integration (4 hours)**
Delegate to: rust-ffi-expert

Files to create:
- backend/src/ai/rag_service.py
- backend/tests/test_ai/test_rag_service.py

Qdrant integration, top-5 retrieval, <500ms target

**Phase 4: AI Examiner (4 hours)**
Delegate to: rust-ffi-expert

Files to create:
- backend/src/ai/ai_examiner.py
- backend/src/ai/prompts/examiner_system_prompt.py
- backend/tests/test_ai/test_ai_examiner.py

AMC 15-mark rubric, temp=0.1 for consistency

**Phase 5: Integration Testing (2 hours)**
Delegate to: testing-qa-expert

Files to create:
- backend/tests/test_ai/test_ai_integration.py

E2E workflow, performance tests, golden dataset validation

### PRD_002 QUALITY GATES (Run after all 5 phases)

```bash
cd backend
source ../venv/bin/activate

# 1. Type checking
python -m mypy src/ai/ --strict

# 2. Test suite
pytest tests/test_ai/ -v --cov=src/ai --cov-report=term-missing

# 3. Security scan
grep -r "sk-ant-" backend/src/ai/
grep -r "ANTHROPIC_API_KEY.*=" backend/src/ai/

# 4. Performance test
pytest tests/test_ai/test_ai_patient.py::test_response_time_under_3s -v
```

Pass criteria: 0 errors, 100% tests pass, ≥70% coverage, 0 hardcoded creds

---

### PRD_003: WebSocket Infrastructure (After PRD_002 complete)
### PRD_004: Scoring System (After PRD_003 complete)
### PRD_005: Frontend Implementation (After PRD_004 complete)

## CRITICAL INSTRUCTIONS

1. **Read Implementation Guide First**:
   cat /home/dev/Development/irStudy/PRD_002_IMPLEMENTATION_GUIDE.md

2. **Sequential with Validation Gates**:
   - Complete Phase 1 → Validate → Phase 2 → Validate → etc.
   - Do NOT proceed to next phase until current phase passes ALL checks

3. **TDD Required**:
   - Write tests FIRST for every phase
   - Confirm tests FAIL initially (RED)
   - Implement code
   - Confirm tests PASS (GREEN)

4. **Use Existing Infrastructure**:
   - Vault: backend/src/core/vault.py
   - Redis: backend/src/core/redis_client.py
   - Database models: already exist

5. **Zero Hardcoded Credentials**:
   - Use Vault: get_vault_secret("secret/ai-osce/claude-api-key", "value")
   - Run grep check before completing each phase

6. **Delegation Pattern**:
   - Provide FULL context to rust-ffi-expert
   - Include validation checklist
   - Wait for completion before next delegation
   - Validate results before proceeding

## START IMMEDIATELY

Begin with PRD_002 Phase 1 (AI Patient Foundation).

Delegate to rust-ffi-expert with comprehensive constraints from the implementation guide.

Report progress after each phase completion.
ENDPROMPT
)

echo "==================================================================="
echo "Sending prompt to Claude..."
echo "==================================================================="
echo ""

# Send to Claude and log output
echo "$RALPH_PROMPT" | claude -p --model claude-sonnet-4-5-20250929 | tee -a "$LOG_FILE"

echo ""
echo "==================================================================="
echo "Ralph Loop Execution Complete"
echo "==================================================================="
echo "Log file: $LOG_FILE"
echo "Check log for implementation progress and results"
echo ""
echo "To monitor in real-time: tail -f $LOG_FILE"
