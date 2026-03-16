#!/bin/bash
#
# Ralph Loop - PRD_004 Scoring System Implementation
# Implements AMC 15-mark rubric, critical error detection, confidence calculation
#

set -euo pipefail

PROJECT_ROOT="/home/dev/Development/irStudy"
STATE_FILE="$PROJECT_ROOT/.ralph-loop-state.json"
LOG_FILE="$PROJECT_ROOT/ralph-prd004.log"
BACKEND_DIR="$PROJECT_ROOT/backend"

cd "$PROJECT_ROOT"

echo "==================================================================="
echo "RALPH LOOP - PRD_004 Scoring System Implementation"
echo "==================================================================="
echo "Started: $(date)"
echo ""

# Update state file - mark PRD_003 complete, start PRD_004
jq '.completed_prds += ["ai-osce-ralph-prds/PRD_AI_OSCE_003_WEBSOCKET_INFRASTRUCTURE.md (COMPLETE - 100%)"] |
    .current_prd = "ai-osce-ralph-prds/PRD_AI_OSCE_004_SCORING_SYSTEM.md" |
    .current_task = "START PRD_004: Scoring System with AMC 15-mark rubric" |
    .current_cycle = 3 |
    .prd_003_completion = {
      "websocket_handler": "completed",
      "jwt_authentication": "completed",
      "session_timer": "completed",
      "session_state_manager": "completed",
      "fastapi_router": "completed",
      "main_app_integration": "completed",
      "integration_tests": "completed (8/8 passing)",
      "test_pass_rate": "100%",
      "code_coverage": "100%",
      "completion_date": "'$(date -Iseconds)'"
    }' "$STATE_FILE" > "$STATE_FILE.tmp" && mv "$STATE_FILE.tmp" "$STATE_FILE"

echo "State updated - PRD_004 now active"
echo ""

# PRD_004 Implementation Prompt
PROMPT=$(cat <<'ENDPROMPT'
You are implementing PRD_004 Scoring System for the AI OSCE platform.

**CONTEXT:**
- PRD_001 (Database & APIs): ✅ COMPLETE (31/31 tests, 75% coverage)
- PRD_002 (AI Integration): ✅ COMPLETE (60/60 tests, 82% coverage)
- PRD_003 (WebSocket): ✅ COMPLETE (8/8 tests, 100% coverage)
- **Current**: PRD_004 (Scoring System) - NOT STARTED

**CRITICAL READING:**
1. Read: `/home/dev/Development/irStudy/ai-osce-ralph-prds/PRD_AI_OSCE_004_SCORING_SYSTEM.md` (complete specification)
2. Check existing: `backend/src/ai/ai_examiner.py` (from PRD_002 - already has basic scoring)
3. Check existing: `backend/src/db/models.py` (OSCEScoreAI table already exists)

**OBJECTIVE:**
Enhance the existing AI Examiner with:
1. **AMC 15-Mark Rubric** (5 domains: Communication 0-3, Clinical Reasoning 0-4, Information Gathering 0-4, Management 0-2, Professionalism 0-2)
2. **Critical Error Detection** (20+ rules, auto-fail logic)
3. **Scoring Confidence** (0.0-1.0 calculation)
4. **Feedback Generation** (strengths, improvements, narrative)
5. **Golden Dataset** (20 sample scenarios for testing)

**IMPLEMENTATION APPROACH (Sequential TDD Phases):**

### Phase 1: Enhance AI Examiner Rubric (6 hours)

**Read existing code first:**
```bash
cd /home/dev/Development/irStudy/backend
cat src/ai/ai_examiner.py
cat src/ai/prompts/examiner_system_prompt.py
```

**Then enhance with:**
1. Update `examiner_system_prompt.py` with detailed AMC 15-mark rubric
2. Update `ai_examiner.py` to return structured JSON:
   ```python
   {
     "communication_score": 0-3,
     "clinical_reasoning_score": 0-4,
     "information_gathering_score": 0-4,
     "management_score": 0-2,
     "professionalism_score": 0-2,
     "total_score": 0-15,
     "pass_fail": "PASS|BORDERLINE|FAIL",
     "communication_feedback": "...",
     "clinical_reasoning_feedback": "...",
     "information_gathering_feedback": "...",
     "management_feedback": "...",
     "professionalism_feedback": "...",
     "strengths": [...],
     "areas_for_improvement": [...],
     "overall_feedback": "..."
   }
   ```
3. Set temperature = 0.1 (deterministic scoring)

**Write tests FIRST (TDD):**
```bash
# Create: backend/tests/test_ai/test_ai_examiner_rubric.py
```

Test cases:
- test_score_perfect_session (15/15, PASS)
- test_score_passing_session (9-14/15, PASS)
- test_score_borderline_session (8/15, BORDERLINE)
- test_score_failing_session (0-7/15, FAIL)
- test_json_output_validation (all fields present)
- test_temperature_consistency (same input → same score)

**Run tests and confirm they FAIL first, then implement.**

---

### Phase 2: Critical Error Detection (8 hours)

**Create new module:**
```bash
mkdir -p backend/src/ai/scoring
touch backend/src/ai/scoring/__init__.py
```

**Files to create:**
1. `backend/src/ai/scoring/critical_errors.py` - Rules engine
2. `backend/src/ai/scoring/error_rules.py` - 20+ rule definitions

**Critical Error Rules (minimum 20):**
```python
CRITICAL_ERROR_RULES = [
    {
        "id": "CE001",
        "name": "Missed acute red flag",
        "description": "Failed to order ECG for chest pain",
        "pattern": lambda t, p: "chest pain" in t.lower() and "ecg" not in t.lower(),
        "severity": "auto_fail"
    },
    {
        "id": "CE002",
        "name": "Unsafe medication",
        "description": "Prescribed contraindicated medication",
        "keywords": ["contraindicated", "wrong dose", "allergy"],
        "severity": "auto_fail"
    },
    # ... 18 more rules covering:
    # - Missed anaphylaxis signs
    # - Incorrect vital sign interpretation
    # - Failed to escalate emergency
    # - Inadequate pain management
    # - Medication allergy not checked
    # - Infection control violations
    # - No resuscitation in cardiac arrest
    # - Dismissive of serious symptoms
    # - Inappropriate intimate examination
    # - Failed to obtain informed consent
    # - Severe communication breakdown
    # ... etc
]
```

**Write tests FIRST:**
```bash
# Create: backend/tests/test_ai/test_critical_errors.py
```

Test cases:
- test_detect_missed_red_flag (chest pain + no ECG → CE001)
- test_detect_unsafe_medication (contraindicated drug → CE002)
- test_auto_fail_on_critical_error (any CE → FAIL)
- test_no_false_positives (good session → no CEs)
- test_all_20_rules (validate each rule individually)

---

### Phase 3: Confidence Calculation (4 hours)

**Create:**
```bash
# File: backend/src/ai/scoring/confidence.py
```

**Confidence Formula:**
```python
def calculate_confidence(transcript: str, scores: Dict, persona: Dict) -> float:
    """
    Calculate scoring confidence (0.0-1.0).

    confidence = (evidence_clarity × 0.5) + (score_consistency × 0.4) - (edge_case_penalty × 0.1)
    """
    evidence_clarity = calculate_transcript_completeness(transcript)  # 0.0-1.0
    score_consistency = validate_score_consistency(scores)  # 0.0-1.0
    edge_case_penalty = detect_ambiguous_situations(transcript, persona)  # 0.0-1.0

    confidence = (evidence_clarity * 0.5) + (score_consistency * 0.4) - (edge_case_penalty * 0.1)
    return max(0.0, min(1.0, confidence))
```

**Write tests FIRST:**
```bash
# Create: backend/tests/test_ai/test_confidence.py
```

Test cases:
- test_high_confidence_clear_session (complete transcript → 0.9+)
- test_low_confidence_incomplete_session (missing data → <0.7)
- test_confidence_range (always 0.0-1.0)
- test_edge_case_detection (ambiguous → penalty)

---

### Phase 4: Feedback Generation (4 hours)

**Create:**
```bash
# File: backend/src/ai/scoring/feedback_generator.py
```

**Feedback Components:**
```python
class FeedbackGenerator:
    def generate_strengths(self, transcript: str, scores: Dict) -> List[str]:
        """Extract 3-5 specific achievements from transcript."""
        # Analyze high-scoring domains
        # Find evidence in transcript
        # Return specific, actionable strengths

    def generate_improvements(self, transcript: str, scores: Dict) -> List[str]:
        """Identify 2-4 actionable gaps."""
        # Analyze low-scoring domains
        # Find missed opportunities
        # Return constructive, specific improvements

    def generate_narrative(self, strengths: List, improvements: List,
                          scores: Dict) -> str:
        """Generate 100-150 word constructive narrative."""
        # Combine strengths and improvements
        # Constructive, growth-oriented tone
        # AMC Clinical Examination context
```

**Write tests FIRST:**
```bash
# Create: backend/tests/test_ai/test_feedback.py
```

Test cases:
- test_generate_strengths (3-5 items, specific)
- test_generate_improvements (2-4 items, actionable)
- test_generate_narrative (100-150 words, constructive)
- test_evidence_based_feedback (references transcript)

---

### Phase 5: Golden Dataset (2 hours)

**Create:**
```bash
# File: backend/data/golden_dataset_scoring.json
```

**Structure (20 sample scenarios):**
```json
[
  {
    "scenario_id": "GD_SCORE_001",
    "persona_name": "Robert Chen - Chest Pain (STEMI)",
    "specialty": "cardiology",
    "difficulty": "intermediate",
    "transcript": "Full 8-minute conversation...",
    "human_expert_score": {
      "communication": 3,
      "clinical_reasoning": 4,
      "information_gathering": 4,
      "management": 2,
      "professionalism": 2,
      "total": 15,
      "pass_fail": "PASS"
    },
    "expected_ai_score_range": {"min": 13, "max": 15},
    "critical_errors_expected": [],
    "confidence_expected": "high"
  },
  // ... 19 more scenarios covering:
  // - Perfect sessions (15/15)
  // - Passing sessions (9-14/15)
  // - Borderline sessions (8/15)
  // - Failing sessions (0-7/15)
  // - Critical error scenarios
  // - Various specialties
]
```

**Write tests FIRST:**
```bash
# Create: backend/tests/test_ai/test_golden_dataset.py
```

Test cases:
- test_golden_dataset_validation (AI vs human ±2 marks, ≥90% accuracy)
- test_pass_fail_agreement (≥95% agreement)
- test_confidence_on_dataset (low confidence → human review)

---

### Phase 6: Integration (2 hours)

**Update existing:**
```bash
# Modify: backend/src/websocket/session_manager.py
```

Add scoring trigger at session end:
```python
async def finalize_session(self, attempt_id: str):
    # Existing finalization logic...

    # NEW: Trigger scoring
    from src.ai.ai_examiner import AIExaminerService
    from src.ai.scoring.critical_errors import CriticalErrorDetector
    from src.ai.scoring.confidence import calculate_confidence

    examiner = AIExaminerService()
    transcript = self._get_full_transcript(attempt_id)
    persona = self._get_persona(attempt_id)

    # Score session
    scores = await examiner.score_session(persona, transcript)

    # Detect critical errors
    detector = CriticalErrorDetector()
    critical_errors = detector.detect_errors(transcript, persona)

    # Calculate confidence
    confidence = calculate_confidence(transcript, scores, persona)

    # Apply critical error auto-fail logic
    if critical_errors:
        scores["pass_fail"] = "FAIL"
        scores["critical_errors"] = critical_errors

    # Save to database
    self._save_score(attempt_id, scores, confidence)

    # Broadcast results via WebSocket
    await self._broadcast_results(scores)
```

**Write tests:**
```bash
# Create: backend/tests/test_ai/test_scoring_integration.py
```

Test cases:
- test_end_to_end_scoring_flow (session → scoring → results)
- test_score_saved_to_database (OSCEScoreAI table)
- test_critical_error_overrides_score (15/15 but CE → FAIL)
- test_performance_target (scoring <5s)

---

**VALIDATION CHECKLIST:**

Before reporting completion, run:
```bash
cd /home/dev/Development/irStudy/backend
source venv/bin/activate

# 1. All tests pass
pytest tests/test_ai/test_*scoring*.py tests/test_ai/test_critical_errors.py tests/test_ai/test_confidence.py tests/test_ai/test_feedback.py tests/test_ai/test_golden_dataset.py -v --tb=short

# 2. Coverage ≥70%
pytest tests/test_ai/test_*scoring*.py --cov=src/ai/scoring --cov-report=term

# 3. Existing tests still pass
pytest tests/test_ai/test_ai_examiner.py -v  # PRD_002 tests

# 4. No security violations
grep -r "sk-ant-" src/ai/scoring/ || echo "✓ No hardcoded credentials"
grep -r "hardcoded" src/ai/scoring/ || echo "✓ No hardcoded values"

# 5. Integration test
pytest tests/test_ai/test_scoring_integration.py -v

# 6. Full test suite
pytest tests/test_ai/ -v --tb=short

echo "==================================================================="
echo "PRD_004 VALIDATION RESULTS"
echo "==================================================================="
echo "Expected:"
echo "- All new tests passing (≥25 tests)"
echo "- Code coverage ≥70%"
echo "- 0 hardcoded credentials"
echo "- Golden Dataset accuracy ≥90%"
echo "- Scoring completes <5s"
echo "- PRD_002 tests still pass (60/60)"
echo "==================================================================="
```

**CONSTRAINTS:**

1. **TDD MANDATORY**: Write tests FIRST, confirm FAIL, then implement
2. **Zero hardcoded credentials**: Use Vault via `get_vault_secret()`
3. **Australian Medical Context**: AMC rubric (not USMLE), "paracetamol" (not "acetaminophen"), emergency 000
4. **Leverage existing code**: Enhance `ai_examiner.py` (don't recreate)
5. **Temperature = 0.1**: Deterministic scoring
6. **Integration**: Update `session_manager.py` to trigger scoring at session end

**RETURN FORMAT:**

Report when complete with:
1. Summary of files created/modified
2. Test results (all passing)
3. Coverage report (≥70%)
4. Security scan (zero violations)
5. Integration validation (PRD_002 tests still pass)
6. Performance metrics (scoring <5s)

BEGIN Phase 1: Enhance AI Examiner Rubric.
Write tests FIRST, confirm they FAIL, then implement.
ENDPROMPT
)

echo "$PROMPT"
echo ""
echo "==================================================================="
echo "Execute Ralph Prompt?"
echo "==================================================================="
echo "This will pipe the prompt to Claude Code."
echo "Press Enter to continue, Ctrl+C to abort..."
read -r

echo "$PROMPT" | claude -p --model claude-sonnet-4-5-20250929 | tee -a "$LOG_FILE"

echo ""
echo "==================================================================="
echo "Ralph PRD_004 Loop - Complete"
echo "==================================================================="
echo "Log file: $LOG_FILE"
echo "Check progress: tail -f $LOG_FILE"
echo ""
