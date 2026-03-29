# PRD OUTLINE: Auto Study Card Generation from OSCE Feedback

**PRD ID**: PRD-P1-005-AUTO-STUDY-CARD-GENERATION
**Category**: Backend AI Integration
**Priority**: P0-Critical (Highest Business Value - Automatic Learning)
**Estimated Effort**: 12-16 hours
**Dependencies**: PRD-P1-004 (Scoring Integration - must complete first)
**Status**: Outline for Review
**Assigned Agent**: `python-backend-developer` + `security-compliance-expert`

**NOTE**: This is a condensed outline (400-500 lines). Full PRD will be 2,400+ lines with complete code implementations.

---

## R - REQUEST (What & Why)

### Executive Summary

Create an **intelligent study card generation system** that automatically extracts 3-5 key learning points from completed OSCE sessions and converts them into spaced-repetition flashcards with RAG-backed citations. When a student finishes an OSCE session and receives AI Examiner feedback, the system will:

1. **Analyze feedback** - Parse "areas for improvement" and "strengths" from AI Examiner scores
2. **Extract learning points** - Identify 2-3 improvement areas + 1-2 strength reinforcements
3. **Generate Q&A cards** - Create question/answer pairs with clinical context
4. **Add RAG citations** - Query Qdrant vector DB for evidence-based references (confidence ≥0.65)
5. **Initialize SM-2** - Set spaced repetition parameters (ease_factor=2.5, interval=1 day)
6. **Link to session** - Store `session_id` for progress tracking

**Business Impact**:
- **Automatic learning reinforcement** - No manual card creation needed
- **Evidence-based content** - All cards backed by Australian medical guidelines (eTG, AHPRA, AMH)
- **Personalized to errors** - Cards target actual student weaknesses
- **Zero hallucinations** - 100% traceable to source documents via `qdrant_point_id`
- **Cost effective**: ~$0.02 per card generation vs. manual creation time

**Current State**: Students receive OSCE feedback but must manually create study materials. No automated learning reinforcement loop exists.

**Desired State**: Instant generation of 3-5 high-quality flashcards after every OSCE session, ready for spaced repetition review.

### User Story

**As a** medical student who just completed an OSCE session
**I want** the system to automatically generate study cards from my feedback
**So that** I can reinforce my learning through spaced repetition without spending time manually creating flashcards, and ensure I'm studying evidence-based content from Australian medical guidelines

### Success Criteria

#### Must Have (100% Required)
- [ ] **Learning Point Extraction**: Generates 3-5 cards per session (2-3 from improvements, 1-2 from strengths)
- [ ] **RAG Citations**: Every card has ≥1 citation with `qdrant_point_id`, source, page reference
- [ ] **Citation Quality**: Confidence threshold ≥0.65, NO "Unknown" titles
- [ ] **Australian Terminology**: Uses paracetamol (not acetaminophen), eTG references, SI units
- [ ] **SM-2 Initialization**: Sets ease_factor=2.5, interval_days=1, repetitions=0, next_review_date=NOW
- [ ] **Session Linking**: Stores `session_id` to track which OSCE generated each card
- [ ] **Database Migration**: Adds `session_id` column to `study_cards` table with foreign key
- [ ] **API Endpoint**: `POST /api/v1/study-cards/generate-from-osce` returns generated cards
- [ ] **Security**: NO hardcoded credentials, all secrets from Vault
- [ ] **Testing**: 100% test pass rate (12+ unit tests, 5+ integration tests)

#### Should Have (90% Priority)
- [ ] **Idempotency**: Calling endpoint twice for same session returns cached cards (no duplicate generation)
- [ ] **Error Handling**: Graceful degradation if RAG service unavailable
- [ ] **Context Enrichment**: Includes patient persona details in card explanations
- [ ] **Duplicate Prevention**: Doesn't create cards for topics student already knows well

#### Nice to Have (Optional)
- [ ] **Difficulty Estimation**: Assigns initial difficulty based on OSCE performance
- [ ] **Image Generation**: Creates visual aids for anatomical/diagnostic cards
- [ ] **Multi-language**: Supports cards in other languages for international students

---

## A - ARCHITECTURE (How)

### Technical Approach

**Core Module**: `backend/src/ai/study_card_generator.py` (~690 lines - designed by Ralph)

**Workflow**:
1. Receive `attempt_id` via API endpoint
2. Load OSCE scores from `ai_osce_scores` table (feedback, strengths, improvements)
3. Load patient persona from `patient_personas` table (chief_complaint, specialty)
4. Extract learning points using Claude 3.5 Sonnet with educational prompt
5. For each learning point:
   - Generate question/answer pair
   - Query Qdrant RAG for supporting citations
   - Validate citation quality (confidence ≥0.65, title NOT "Unknown")
   - Initialize SM-2 parameters
6. Insert cards into `study_cards` table with `session_id` link
7. Return generated cards to user

### System Design Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                  FRONTEND (Optional Trigger)                │
│  - User clicks "Generate Study Cards" after viewing results │
│  - Or: Auto-trigger on session finalization                 │
└────────────────────┬────────────────────────────────────────┘
                     │ POST /api/v1/study-cards/generate-from-osce
                     │ {attempt_id}
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              BACKEND API (FastAPI)                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ POST /api/v1/study-cards/generate-from-osce          │   │
│  │ - Validate JWT (user owns session)                   │   │
│  │ - Check if cards already generated (idempotency)     │   │
│  │ - Call StudyCardGenerator.generate_from_osce()       │   │
│  └────────────────────┬─────────────────────────────────┘   │
│                       │                                      │
│  ┌────────────────────▼─────────────────────────────────┐   │
│  │ StudyCardGenerator (src/ai/study_card_generator.py)  │   │
│  │ - Load OSCE scores + feedback                        │   │
│  │ - Load patient persona                               │   │
│  │ - Extract 3-5 learning points                        │   │
│  │ - Generate Q&A pairs with Claude                     │   │
│  │ - For each card: Query RAG for citations            │   │
│  │ - Validate citations                                 │   │
│  │ - Initialize SM-2 parameters                         │   │
│  └────────────────────┬─────────────────────────────────┘   │
│                       │                                      │
│  ┌────────────────────▼─────────────────────────────────┐   │
│  │ RAG Service (Qdrant)                                 │   │
│  │ - Query: "diabetes management guidelines australia"  │   │
│  │ - Return: Top 3 results with confidence scores       │   │
│  │ - Filter: confidence ≥ 0.65, title NOT "Unknown"     │   │
│  └────────────────────┬─────────────────────────────────┘   │
│                       │                                      │
│  ┌────────────────────▼─────────────────────────────────┐   │
│  │ Database (PostgreSQL)                                │   │
│  │ INSERT INTO study_cards (                            │   │
│  │   card_id, user_id, session_id,                      │   │
│  │   question, answer, explanation,                     │   │
│  │   citations, ease_factor, interval_days,             │   │
│  │   repetitions, next_review_date                      │   │
│  │ )                                                    │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Database Schema Changes

**Migration**: Add `session_id` column to `study_cards` table

```sql
-- Alembic migration: YYYYMMDD_HHMM_add_session_id_to_study_cards.py

ALTER TABLE study_cards
ADD COLUMN session_id VARCHAR REFERENCES ai_osce_attempts(attempt_id) ON DELETE SET NULL;

CREATE INDEX idx_study_cards_session_id ON study_cards(session_id);

COMMENT ON COLUMN study_cards.session_id IS 'Links study card to OSCE session that generated it. Null for manually created cards.';
```

### API Endpoint Specification

**POST /api/v1/study-cards/generate-from-osce**

**Request**:
```json
{
  "attempt_id": "9d76cd2a-5ad0-4e01-835a-3ce995023367"
}
```

**Response 201 Created**:
```json
{
  "cards": [
    {
      "card_id": "550e8400-e29b-41d4-a716-446655440001",
      "question": "What is the recommended approach for history taking in a patient presenting with Type 2 Diabetes (HbA1c 8.5%)?",
      "answer": "Use a systematic framework covering:\n- Duration of diabetes diagnosis\n- Current medication adherence\n- Dietary patterns (carbohydrate intake, meal frequency)\n- Exercise routine\n- Home glucose monitoring results\n- Symptoms of complications (vision changes, numbness, polyuria)\n- Cardiovascular risk factors (smoking, family history)",
      "explanation": "This learning point was identified as an area for improvement in your OSCE session with Emma Wilson. You demonstrated good communication but could have explored dietary patterns and medication adherence in more depth.",
      "citations": [
        {
          "source": "Therapeutic Guidelines (eTG) - Diabetes Management",
          "qdrant_point_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
          "page": "p. 45-47",
          "confidence": 0.87
        },
        {
          "source": "RACGP Red Book - Diabetes Assessment",
          "qdrant_point_id": "b2c3d4e5-f6g7-8901-bcde-fg2345678901",
          "page": "p. 112",
          "confidence": 0.72
        }
      ],
      "session_id": "9d76cd2a-5ad0-4e01-835a-3ce995023367",
      "specialty": "General Practice",
      "difficulty_level": "intermediate",
      "sm2_params": {
        "ease_factor": 2.5,
        "interval_days": 1,
        "repetitions": 0,
        "next_review_date": "2026-03-22T21:06:15Z"
      }
    }
  ],
  "total": 3,
  "generated_at": "2026-03-21T21:06:15Z"
}
```

**Response 400** (Session not scored):
```json
{
  "error": {
    "code": 400,
    "message": "Cannot generate study cards - session has not been scored yet. Please finalize the session first.",
    "path": "/api/v1/study-cards/generate-from-osce"
  }
}
```

### Key Components

**1. Study Card Generator** (`src/ai/study_card_generator.py` - 690 lines)
- `StudyCardGenerator` class
- `generate_from_osce(attempt_id, user_id)` - Main generation method
- `_extract_learning_points(scores, persona)` - LLM-based extraction
- `_generate_qa_pair(learning_point, persona)` - Q&A generation
- `_query_rag_citations(question, answer)` - RAG integration
- `_validate_citations(citations)` - Quality checks
- `_create_study_card(...)` - Database insertion

**2. RAG Integration** (Qdrant Client)
- Query vector DB with semantic search
- Filter by confidence threshold (≥0.65)
- Validate metadata (title, source, page)
- Return top 3 most relevant citations

**3. Database Models** (Extend existing `StudyCard` model)
- Add `session_id` field (VARCHAR, FK to ai_osce_attempts)
- Add `citations` field (JSONB array)
- Keep existing SM-2 fields (ease_factor, interval_days, repetitions, next_review_date)

---

## L - LOOP (Iterative Development)

### Phase 1: Database Migration + Core Generator (4 hours)

**Deliverables**:
- Alembic migration: Add `session_id` column to `study_cards`
- `StudyCardGenerator` class with learning point extraction
- Unit tests for extraction logic

**Validation**:
- [ ] Migration runs successfully (upgrade + downgrade)
- [ ] Extracts 3-5 learning points from sample feedback
- [ ] Points prioritize "areas for improvement" over "strengths"

### Phase 2: RAG Integration (3 hours)

**Deliverables**:
- Qdrant query integration
- Citation validation logic
- Error handling for RAG service failures

**Validation**:
- [ ] Citations have confidence ≥0.65
- [ ] NO "Unknown" titles in results
- [ ] Handles Qdrant downtime gracefully (logs warning, continues without citations)

### Phase 3: Q&A Generation + API Endpoint (3 hours)

**Deliverables**:
- Claude prompt for Q&A generation
- API endpoint implementation
- Idempotency checks
- Database insertion

**Validation**:
- [ ] Generates Australian medical terminology (paracetamol, eTG)
- [ ] Calling endpoint twice returns cached result
- [ ] Cards inserted with correct SM-2 initialization

### Phase 4: Testing + Documentation (2 hours)

**Deliverables**:
- 12+ unit tests (pytest)
- 5+ integration tests
- API documentation

**Validation**:
- [ ] 100% test pass rate
- [ ] ≥85% code coverage
- [ ] Security scan passes (no hardcoded credentials)

---

## P - PLAN (Detailed Implementation)

### Files to Create

**1. `backend/src/ai/study_card_generator.py` (690 lines)**
- Purpose: Core generation logic
- Key Classes: `StudyCardGenerator`
- Dependencies: anthropic, qdrant-client, sqlalchemy
- Full implementation in expanded PRD

**2. `backend/alembic/versions/YYYYMMDD_HHMM_add_session_id_to_study_cards.py` (80 lines)**
- Purpose: Database migration
- Changes: Add session_id column, index
- Rollback: Remove column

**3. `backend/tests/test_ai/test_study_card_generator.py` (300 lines)**
- Purpose: Unit tests for generator
- Coverage: Learning extraction, Q&A generation, RAG integration
- Tests: 12+ test cases

**4. `backend/tests/test_api/test_study_card_auto_generation.py` (200 lines)**
- Purpose: Integration tests for API endpoint
- Coverage: End-to-end workflow, error cases
- Tests: 5+ test scenarios

### Files to Modify

**1. `backend/src/api/v1/study_cards.py` (+120 lines)**
- Add: `generate_from_osce()` endpoint
- Modify: Import StudyCardGenerator
- Add: Error handling for missing scores

**2. `backend/src/db/models.py` (+8 lines)**
- Modify: `StudyCard` model
- Add: `session_id` field
- Add: Relationship to `OSCEAttemptAI`

**3. `backend/src/api/v1/router.py` (no change - already includes study_cards router)**
- Verify: study_cards router included

### Key Function Signatures (Full Code in Expanded PRD)

```python
# study_card_generator.py

class StudyCardGenerator:
    def generate_from_osce(
        self,
        attempt_id: str,
        user_id: str,
        db: Session
    ) -> List[StudyCard]:
        """Generate 3-5 study cards from OSCE feedback"""
        pass

    def _extract_learning_points(
        self,
        scores: OSCEScoreAI,
        persona: PatientPersona
    ) -> List[Dict[str, str]]:
        """Extract learning points using Claude"""
        pass

    def _generate_qa_pair(
        self,
        learning_point: Dict[str, str],
        persona: PatientPersona
    ) -> Tuple[str, str, str]:
        """Generate question, answer, explanation"""
        pass

    def _query_rag_citations(
        self,
        question: str,
        answer: str
    ) -> List[Dict[str, Any]]:
        """Query Qdrant for citations"""
        pass

    def _validate_citations(
        self,
        citations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Filter citations by quality threshold"""
        pass
```

---

## H - HANDOFF (Delivery & Validation)

### Acceptance Criteria Checklist

#### Functionality
- [ ] **Endpoint Created**: `POST /api/v1/study-cards/generate-from-osce` returns 201 with cards
- [ ] **Card Generation**: Produces 3-5 cards per session (2-3 improvements, 1-2 strengths)
- [ ] **RAG Citations**: Every card has ≥1 citation with qdrant_point_id, source, page
- [ ] **Citation Quality**: All citations have confidence ≥0.65, NO "Unknown" titles
- [ ] **Australian Standards**: Uses paracetamol, eTG references, SI units (mmol/L not mg/dL)
- [ ] **SM-2 Init**: All cards have ease_factor=2.5, interval_days=1, repetitions=0, next_review_date set
- [ ] **Session Linking**: study_cards.session_id links to ai_osce_attempts.attempt_id
- [ ] **Idempotency**: Calling generate twice returns same cached cards (no duplicate API calls)
- [ ] **Authorization**: Only session owner can generate cards (403 for unauthorized)
- [ ] **Error Handling**: Graceful messages for not found (404), not scored (400), RAG failure

#### Database
- [ ] **Migration**: Alembic migration adds session_id column successfully
- [ ] **Foreign Key**: session_id references ai_osce_attempts(attempt_id)
- [ ] **Index**: idx_study_cards_session_id created
- [ ] **Rollback**: Migration downgrade removes column cleanly

#### Security
- [ ] **No Hardcoded Credentials**: grep check passes for API keys
- [ ] **Vault Integration**: ANTHROPIC_API_KEY loaded from Vault
- [ ] **SQL Injection Prevention**: Parameterized queries only
- [ ] **Input Validation**: Pydantic schemas validate all inputs

#### Testing
- [ ] **Unit Tests**: 12/12 tests passing in test_study_card_generator.py
- [ ] **Integration Tests**: 5/5 tests passing in test_study_card_auto_generation.py
- [ ] **Test Coverage**: ≥85% for new code
- [ ] **E2E Test**: Complete OSCE → Finalize → Generate Cards workflow passes

### Testing Requirements Summary

**Unit Tests** (Full code in expanded PRD):
- `test_extract_learning_points_from_feedback()`
- `test_generate_qa_pair_with_clinical_context()`
- `test_query_rag_citations_with_confidence_threshold()`
- `test_validate_citations_filters_low_quality()`
- `test_create_study_card_with_sm2_initialization()`
- ... 7 more tests

**Integration Tests** (Full code in expanded PRD):
- `test_generate_from_osce_success()`
- `test_generate_from_osce_idempotency()`
- `test_generate_from_osce_no_score_error()`
- `test_generate_from_osce_unauthorized()`
- `test_generate_from_osce_rag_failure_graceful()`

**E2E Test** (Playwright - full code in expanded PRD):
- Complete OSCE session → View results → Click "Generate Study Cards" → Cards appear in study deck

### Validation Commands Summary

```bash
# Database migration
cd /home/dev/Development/irStudy/backend
alembic upgrade head
# Expected: Migration runs successfully

# Unit tests
pytest tests/test_ai/test_study_card_generator.py -v
# Expected: 12/12 tests passed

# Integration tests
pytest tests/test_api/test_study_card_auto_generation.py -v
# Expected: 5/5 tests passed

# Security scan
grep -r "sk-ant-\|ANTHROPIC_API_KEY.*=" src/ai/study_card_generator.py
# Expected: 0 matches

# Test coverage
pytest tests/test_ai/test_study_card_generator.py --cov=src.ai.study_card_generator --cov-report=term
# Expected: ≥85% coverage
```

### Performance Requirements

- **Generation Time**: <8 seconds for 3 cards (Claude API: ~2s per card + RAG: ~1s per card)
- **Database Insert**: <100ms for batch insert
- **RAG Query**: <500ms per query

---

## Agent OS Expert Constraints

### Agent: python-backend-developer

**CRITICAL - Read Before Starting**:

**1. Existing Code Integration**:
- Use existing `QdrantClient` from `src/ai/rag_service.py`
- Use existing `StudyCard` model from `src/db/models.py`
- Use existing `OSCEScoreAI`, `OSCEAttemptAI`, `PatientPersona` models
- Follow existing API patterns from `src/api/v1/patient_personas.py`

**2. Australian Medical Standards**:
- MUST use "paracetamol" (not "acetaminophen")
- MUST reference eTG, AHPRA, AMH in explanations
- MUST use SI units (mmol/L not mg/dL)
- Emergency number: 000 (not 911)

**3. RAG Citation Requirements**:
- MUST query Qdrant for every card
- MUST filter confidence ≥0.65
- MUST reject citations with title="Unknown"
- MUST include qdrant_point_id for traceability

**4. Security Requirements**:
- NO hardcoded API keys
- Use Vault for ANTHROPIC_API_KEY
- Parameterized SQL queries only
- JWT validation on endpoint

**5. Validation Checklist (Complete Before Returning)**:
- [ ] pytest tests/ → 100% pass
- [ ] grep -r "sk-ant-" src/ → 0 matches
- [ ] All cards have ≥1 citation
- [ ] All citations have confidence ≥0.65
- [ ] Australian terminology check passes

### Agent: security-compliance-expert

**CRITICAL - Review Before Approval**:

**1. Credential Scanning**:
- Scan for hardcoded API keys
- Verify Vault integration
- Check environment variable usage

**2. SQL Injection Prevention**:
- Verify parameterized queries
- Check ORM usage (SQLAlchemy)
- No string concatenation in queries

**3. Data Validation**:
- Pydantic schemas for all inputs
- UUID validation for attempt_id
- JWT token validation

**4. Audit Trail**:
- Log all card generation requests
- Include user_id, attempt_id, timestamp
- Store in Redis for monitoring

---

## Dependencies

### Python Packages (Add to requirements.txt)
- `anthropic>=0.21.0` - Claude API client
- `qdrant-client>=1.7.0` - RAG vector database
- Existing: `sqlalchemy`, `fastapi`, `pydantic`

### External Services
- Qdrant vector database (already running)
- HashiCorp Vault (already configured)
- PostgreSQL database (study_cards table exists)

---

## Related PRDs

**Depends On**:
- PRD-P1-004-AI-EXAMINER-SCORING-INTEGRATION (must complete first - provides feedback to analyze)

**Blocks**:
- PRD-P1-006-FLASHCARD-REVIEW-INTERFACE (needs cards to display)
- PRD-P1-007-SM2-REVIEW-LOGIC (needs cards with SM-2 params)

**Integrates With**:
- PRD_AI_OSCE_001_DATABASE_AND_APIS (uses ai_osce_attempts, ai_osce_scores tables)
- RAG system (Qdrant vector database)

---

**End of PRD-P1-005 OUTLINE**

**Total Lines**: 465 lines (outline format)
**Full PRD Expansion**: Will be 2,400+ lines with complete code implementations (50-100 line functions)

**Next Steps**:
1. User reviews this outline
2. User provides feedback/approval
3. Expand to full PRD with maximum code detail
4. Create PRD-P1-006 outline (Flashcard UI)
5. Create PRD-P1-007 outline (SM-2 Logic)
