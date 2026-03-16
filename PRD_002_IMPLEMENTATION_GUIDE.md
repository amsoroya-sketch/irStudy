# PRD_002 AI Integration - Implementation Guide

**Status**: Ready to implement
**PRD Location**: `/home/dev/Development/irStudy/ai-osce-ralph-prds/PRD_AI_OSCE_002_AI_INTEGRATION.md`
**Dependencies**: ✅ PRD_001 COMPLETE (31/31 tests passing)

---

## Executive Summary

Implement AI Patient and AI Examiner services using Claude 3.5 Sonnet for realistic OSCE simulation:
- **AI Patient**: Progressive disclosure, emotional intelligence, RAG integration
- **AI Examiner**: AMC 15-mark rubric scoring with critical error detection
- **RAG Integration**: Qdrant vector DB for clinical guideline retrieval
- **Session State**: Redis-based emotional state tracking

**Estimated Effort**: 22 hours (5 sequential phases)
**Test Coverage Target**: ≥70%
**Performance Target**: AI Patient response <3s

---

## Implementation Plan - Sequential Phases

### Phase 1: AI Patient Foundation (8 hours)

**Objective**: Claude API integration with progressive disclosure

**Files to Create**:
1. `backend/src/ai/__init__.py`
2. `backend/src/ai/prompts/__init__.py`
3. `backend/src/ai/prompts/patient_system_prompt.py` - SYSTEM_PROMPT builder
4. `backend/src/ai/ai_patient.py` - Main AI Patient service
5. `backend/tests/test_ai/__init__.py`
6. `backend/tests/test_ai/test_ai_patient.py` - TDD tests (write FIRST)

**Key Implementation Details**:

```python
# Vault Integration (MANDATORY - no hardcoded keys)
from src.core.vault import get_vault_secret

claude_api_key = get_vault_secret("secret/ai-osce/claude-api-key", "value")
client = Anthropic(api_key=claude_api_key)

# Claude API Call
response = client.messages.create(
    model="claude-3-5-sonnet-20250219",
    max_tokens=500,
    temperature=0.7,  # Creative for patient role
    system=system_prompt,
    messages=[{"role": "user", "content": student_message}]
)
```

**Progressive Disclosure Logic**:
```python
# Read persona's symptoms JSONB
symptoms = {
    "immediate": ["chest pain for 2 hours", "pain radiates to left arm"],
    "when_asked_onset": "Started after climbing stairs at work",
    "when_asked_severity": "8 out of 10, feels like crushing pressure"
}

# Map question to disclosure
if "when did it start" in student_message.lower():
    context += symptoms["when_asked_onset"]
```

**Validation Checklist**:
- [ ] TDD: Tests written FIRST (must fail initially)
- [ ] All tests passing (100%)
- [ ] No hardcoded credentials: `grep -r "sk-ant-" backend/src/ai/` = empty
- [ ] Vault integration working
- [ ] Response time <3s (with mock API)
- [ ] Progressive disclosure tested

**Test Command**:
```bash
cd backend
source ../venv/bin/activate
export SECRET_KEY="test_key_123456789012345678901234567890"
export DATABASE_URL="sqlite:///:memory:"
pytest tests/test_ai/test_ai_patient.py -v --tb=short
```

---

### Phase 2: Emotional State Machine (4 hours)

**Objective**: 5-state emotional progression with empathy tracking

**Files to Create**:
1. `backend/src/ai/emotional_state.py` - State machine logic
2. `backend/tests/test_ai/test_emotional_state.py` - TDD tests

**5 States**:
1. `ANXIOUS_GUARDED` - Initial state, hesitant to share
2. `CAUTIOUSLY_OPEN` - Starting to trust, shares when asked
3. `TRUSTING` - Cooperative, shares willingly
4. `DEFENSIVE` - Feels judged, resistant
5. `WITHDRAWN` - Lost trust, minimal responses

**State Transition Logic**:
```python
class EmotionalStateMachine:
    STATES = ["ANXIOUS_GUARDED", "CAUTIOUSLY_OPEN", "TRUSTING", "DEFENSIVE", "WITHDRAWN"]

    def __init__(self, baseline_state: str = "ANXIOUS_GUARDED"):
        self.current_state = baseline_state
        self.empathy_points = 0

    def process_student_message(self, message: str) -> str:
        # Detect empathy markers
        empathy_phrases = ["I understand", "must be frightening", "sounds difficult"]
        if any(phrase in message.lower() for phrase in empathy_phrases):
            self.empathy_points += 1

        # State transitions based on empathy
        if self.current_state == "ANXIOUS_GUARDED" and self.empathy_points >= 2:
            self.current_state = "CAUTIOUSLY_OPEN"
        elif self.current_state == "CAUTIOUSLY_OPEN" and self.empathy_points >= 4:
            self.current_state = "TRUSTING"

        return self.current_state
```

**Redis Integration**:
```python
from src.core.redis_client import get_redis_client

redis = get_redis_client()
session_key = f"osce:session:{session_id}:emotional_state"

# Store state (TTL 30 minutes)
redis.setex(session_key, 1800, current_state)
```

**Validation Checklist**:
- [ ] All 5 states implemented
- [ ] Empathy detection working
- [ ] State transitions deterministic
- [ ] Redis persistence working
- [ ] Tests passing (100%)

---

### Phase 3: RAG Integration (4 hours)

**Objective**: Qdrant integration for clinical guideline retrieval

**Files to Create**:
1. `backend/src/ai/rag_service.py` - RAG retrieval logic
2. `backend/tests/test_ai/test_rag_service.py` - TDD tests

**Qdrant Integration**:
```python
from qdrant_client import QdrantClient

class RAGService:
    def __init__(self):
        # Check existing Qdrant setup in codebase
        self.qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        self.client = QdrantClient(url=self.qdrant_url)
        self.collection_name = "medical_guidelines"

    def retrieve_context(self, query: str, top_k: int = 5) -> list:
        """
        Retrieve top-K clinical guideline chunks.

        Returns:
            [{"text": "...", "source": "eTG", "page_ref": "p.123"}, ...]
        """
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=self._embed_query(query),
            limit=top_k
        )

        return [
            {
                "text": hit.payload["text"],
                "source": hit.payload["source"],
                "page_ref": hit.payload.get("page_ref", "N/A")
            }
            for hit in results
        ]
```

**Validation Checklist**:
- [ ] Qdrant client working
- [ ] Top-5 retrieval tested
- [ ] Citation formatting correct
- [ ] Response time <500ms
- [ ] Tests passing (100%)

---

### Phase 4: AI Examiner (4 hours)

**Objective**: AMC 15-mark rubric scoring with Claude API

**Files to Create**:
1. `backend/src/ai/ai_examiner.py` - Main examiner service
2. `backend/src/ai/prompts/examiner_system_prompt.py` - Rubric prompt
3. `backend/tests/test_ai/test_ai_examiner.py` - TDD tests

**AMC 15-Mark Rubric**:
- Communication: 0-3 marks
- Clinical Reasoning: 0-4 marks
- Information Gathering: 0-4 marks
- Management: 0-2 marks
- Professionalism: 0-2 marks
- **Total**: 15 marks (PASS ≥9/15)

**Examiner SYSTEM_PROMPT**:
```python
def build_examiner_system_prompt(persona: PatientPersona, transcript: list) -> str:
    return f"""You are an AI Examiner scoring an OSCE session using the AMC 15-mark rubric.

**Patient Scenario**: {persona.chief_complaint}
**Expected Differentials**: {', '.join(persona.key_differentials)}
**Critical Actions**: {', '.join(persona.critical_actions)}

**Conversation Transcript**:
{format_transcript(transcript)}

**Your Task**:
Score the student's performance on a 15-mark scale:

1. Communication (0-3): Empathy, listening, rapport
2. Clinical Reasoning (0-4): Differential diagnosis, red flags
3. Information Gathering (0-4): Systematic history, relevant questions
4. Management (0-2): Appropriate next steps, safety netting
5. Professionalism (0-2): Respect, confidentiality, cultural sensitivity

**Output Format** (JSON):
{{
  "communication_score": 2,
  "clinical_reasoning_score": 3,
  "information_gathering_score": 3,
  "management_score": 1,
  "professionalism_score": 2,
  "total_score": 11,
  "pass_fail": "PASS",
  "critical_errors": [],
  "feedback": "Student demonstrated good empathy and systematic approach..."
}}

Be strict but fair. Auto-fail if critical red flags missed.
"""
```

**Claude API Call**:
```python
response = self.client.messages.create(
    model="claude-3-5-sonnet-20250219",
    max_tokens=2000,
    temperature=0.1,  # Consistent scoring
    system=examiner_prompt,
    messages=[{"role": "user", "content": "Please score this OSCE session."}]
)

# Parse JSON response
scores = json.loads(response.content[0].text)
```

**Validation Checklist**:
- [ ] All 5 scoring domains implemented
- [ ] JSON parsing working
- [ ] Critical error detection tested
- [ ] Pass/fail threshold correct (≥9/15)
- [ ] Tests passing (100%)

---

### Phase 5: Integration Testing (2 hours)

**Objective**: End-to-end workflow tests

**Files to Create**:
1. `backend/tests/test_ai/test_ai_integration.py` - E2E tests

**E2E Test Workflow**:
```python
@pytest.mark.asyncio
async def test_full_osce_session():
    """Test complete AI OSCE workflow"""
    # 1. Load persona
    persona = await get_test_persona()

    # 2. AI Patient responds to student
    ai_patient = AIPatientService()
    response1 = ai_patient.generate_response(
        persona=persona,
        student_message="Hello, I'm Dr. Smith. How can I help you today?",
        emotional_state="ANXIOUS_GUARDED"
    )
    assert len(response1) > 0

    # 3. Update emotional state
    state_machine = EmotionalStateMachine()
    new_state = state_machine.process_student_message(
        "I understand this must be very frightening for you."
    )
    assert new_state in ["CAUTIOUSLY_OPEN", "TRUSTING"]

    # 4. AI Examiner scores session
    ai_examiner = AIExaminerService()
    scores = ai_examiner.score_session(
        persona=persona,
        transcript=[
            {"role": "student", "message": "Hello, I'm Dr. Smith..."},
            {"role": "patient", "message": response1}
        ]
    )

    # 5. Validate scoring
    assert scores["total_score"] >= 0 and scores["total_score"] <= 15
    assert scores["pass_fail"] in ["PASS", "FAIL"]
```

**Performance Tests**:
```python
def test_ai_patient_response_time():
    """Test AI Patient responds in <3 seconds"""
    import time
    start = time.time()
    response = ai_patient.generate_response(...)
    elapsed = time.time() - start
    assert elapsed < 3.0
```

**Validation Checklist**:
- [ ] E2E workflow tested
- [ ] AI Patient + Examiner integration working
- [ ] Performance targets met
- [ ] All tests passing (100%)
- [ ] Coverage ≥70%

---

## Quality Gates (Run After All Phases)

```bash
cd /home/dev/Development/irStudy/backend

# 1. Type checking
python -m mypy src/ai/ --strict

# 2. Test suite
pytest tests/test_ai/ -v --cov=src/ai --cov-report=term-missing

# 3. Security scan (NO hardcoded credentials)
grep -r "sk-ant-" backend/src/ai/
grep -r "ANTHROPIC_API_KEY.*=" backend/src/ai/

# 4. Integration test
pytest tests/test_ai/test_ai_integration.py -v

# 5. Performance test
pytest tests/test_ai/test_ai_patient.py::test_response_time_under_3s -v
```

**Pass Criteria**:
- ✅ 0 mypy errors
- ✅ 100% test pass rate (≥70% coverage)
- ✅ 0 hardcoded credentials
- ✅ Response time <3s (p95)
- ✅ Integration tests pass

---

## Existing Infrastructure to Reuse

**Vault Integration**:
- File: `backend/src/core/vault.py`
- Function: `get_vault_secret("secret/ai-osce/claude-api-key", "value")`

**Redis Client**:
- File: `backend/src/core/redis_client.py`
- Namespace: `osce:*` (NOT `emr:*`)

**Database Models** (Already Created):
- `PatientPersona` - AI patient profiles
- `OSCEAttemptAI` - Session tracking
- `OSCEScoreAI` - Scoring storage

**Dependencies** (Already Installed):
- `anthropic==0.17.0` - Claude API SDK
- `qdrant-client==1.7.3` - Vector DB client
- `redis>=4.5.0` - Redis client

---

## Next Steps

When ready to implement:

1. **Start with Phase 1** (AI Patient Foundation)
   - Follow TDD: Write tests FIRST
   - Use Vault for Claude API key
   - Implement progressive disclosure
   - Validate with checklist

2. **Sequential Validation**
   - Complete Phase 1 → Validate → Phase 2 → Validate → etc.
   - Don't proceed to next phase until current phase passes all checks

3. **Quality Gates**
   - Run full test suite after all phases
   - Verify 0 hardcoded credentials
   - Check performance targets

4. **Mark PRD_002 Complete**
   - Update `.ralph-loop-state.json`
   - Commit changes
   - Proceed to PRD_003 (WebSocket Infrastructure)

---

**Created**: 2026-02-24
**Last Updated**: 2026-02-24
**Status**: Ready for implementation
