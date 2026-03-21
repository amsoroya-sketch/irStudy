# PRD Standards Summary - Ralph Claude Code Loop

**Date**: 2026-03-17
**Source**: `/home/dev/Development/ralph-claude-code/`
**Purpose**: Standards for creating PRDs compatible with Ralph autonomous execution loop

---

## Critical Finding: PRD Length & Depth

**WRONG**: 500-line PRDs with basic structure
**CORRECT**: 2,000-2,200+ line PRDs with comprehensive R-A-L-P-H structure

**Evidence**:
- `ai-osce-ralph-prds/PRD_AI_OSCE_001_DATABASE_AND_APIS.md` = 2,201 lines
- `year9-platform/specs/MASTER_PRD.md` = comprehensive master spec

---

## Required PRD Structure: R-A-L-P-H Template

### R - REQUEST (User Story & Business Context)

**Sections Required**:
1. **Executive Summary** (3-5 paragraphs)
   - What is being built
   - Why it's critical (business impact)
   - Who it serves (target users)
   - Success metrics (quantifiable)

2. **User Story**
   ```
   As a [role]
   I want [capability]
   So that [benefit]
   ```

3. **Problem Statement**
   - Current state (pain points)
   - Desired state (solution)
   - Impact metrics (time saved, users affected)

4. **Success Criteria**
   - Must Have (100% required)
   - Should Have (90% priority)
   - Nice to Have (optional)

**Example**:
```markdown
## Executive Summary

Create a real-time WebSocket chat interface that allows medical students to conduct 8-minute OSCE practice sessions with AI Patient personas. The interface must support bidirectional communication, display message history, handle WebSocket reconnection, and integrate with the existing Material-UI design system.

**Impact**: Unlocks 207 RAG-verified patient personas for actual practice (currently students can only browse, not interact).
```

---

### A - ARCHITECTURE (Technical Approach)

**Sections Required**:
1. **System Design** (architecture diagram in text)
2. **Database Schema** (complete SQL with indexes)
3. **API Endpoints** (full FastAPI/Express implementation)
4. **Data Models** (Pydantic/Zod schemas)
5. **Technology Stack** (specific versions)
6. **Integration Points** (external systems)

**Example Database Schema**:
```sql
CREATE TABLE ai_osce_attempts (
    attempt_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    persona_id UUID NOT NULL REFERENCES patient_personas(persona_id),
    session_type VARCHAR(20) NOT NULL CHECK (session_type IN ('practice', 'mock_exam')),
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ended_at TIMESTAMP WITH TIME ZONE,
    duration_seconds INT,
    session_state VARCHAR(20) NOT NULL DEFAULT 'initialized',

    -- Indexing for performance
    INDEX idx_user_attempts (user_id, started_at DESC),
    INDEX idx_persona_attempts (persona_id)
);
```

**Example API Endpoint**:
```python
@router.post("/osce-sessions", response_model=CreateSessionResponse)
async def create_osce_session(
    request: CreateSessionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create new OSCE practice session

    Args:
        request: Session creation parameters
        db: Database session
        current_user: Authenticated user

    Returns:
        CreateSessionResponse with session_id and WebSocket URL

    Raises:
        HTTPException 404: Patient persona not found
        HTTPException 403: User does not have access to persona
    """
    # Implementation details...
```

---

### L - LOOP (Iterative Development)

**Sections Required**:
1. **Phase Breakdown** (3-5 phases)
2. **Validation Checkpoints** (after each phase)
3. **Rollback Strategy** (if phase fails)
4. **Incremental Testing** (per-phase tests)

**Example**:
```markdown
## Loop: Iterative Development

### Phase 1: Database Schema & Models (2 hours)
**Deliverables**:
- Alembic migration for ai_osce_attempts table
- SQLAlchemy models
- Pydantic schemas

**Validation**:
- [ ] Migration runs successfully (upgrade + downgrade)
- [ ] 0 SQLAlchemy warnings
- [ ] Pydantic schema validation passes

### Phase 2: API Endpoints (3 hours)
**Deliverables**:
- POST /osce-sessions (create session)
- GET /osce-sessions/{session_id} (retrieve session)
- PATCH /osce-sessions/{session_id} (update session)

**Validation**:
- [ ] All endpoints return correct status codes
- [ ] API integration tests pass (100%)
- [ ] OpenAPI schema validates

### Phase 3: Frontend Integration (3 hours)
**Deliverables**:
- React Query hooks for API calls
- Session management component

**Validation**:
- [ ] 0 TypeScript errors
- [ ] Component renders without warnings
- [ ] E2E test: Create session → Display chat
```

---

### P - PLAN (Detailed Implementation)

**Sections Required**:
1. **File-by-File Implementation** (with line counts)
2. **Code Examples** (full function implementations)
3. **Dependencies** (explicit package versions)
4. **Configuration** (environment variables, settings)
5. **Migration Steps** (database, schema changes)

**Example**:
```markdown
## Plan: Detailed Implementation

### File 1: `backend/src/db/models.py` (+150 lines)

```python
from sqlalchemy import Column, String, Integer, UUID, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import JSONB
from .base import Base
import uuid
from datetime import datetime

class OSCEAttempt(Base):
    """
    OSCE practice session attempt record

    Australian Medical Context:
    - AMC Clinical Examination format (8-minute stations)
    - Tracks student performance across patient persona interactions
    - Links to scoring rubric (15-mark scale)
    """
    __tablename__ = 'ai_osce_attempts'

    attempt_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    persona_id = Column(UUID(as_uuid=True), ForeignKey('patient_personas.persona_id'), nullable=False)
    session_type = Column(String(20), CheckConstraint("session_type IN ('practice', 'mock_exam')"), nullable=False)
    started_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    ended_at = Column(DateTime(timezone=True))
    duration_seconds = Column(Integer)
    session_state = Column(String(20), default='initialized')

    # Relationships
    user = relationship("User", back_populates="osce_attempts")
    persona = relationship("PatientPersona", back_populates="attempts")
```
```

---

### H - HANDOFF (Delivery & Validation)

**Sections Required**:
1. **Acceptance Criteria Checklist** (explicit checkboxes)
2. **Testing Requirements** (unit, integration, E2E)
3. **Validation Commands** (exact bash commands)
4. **Security Scan Requirements** (grep patterns)
5. **Performance Benchmarks** (targets)
6. **Documentation Updates** (README, API docs)

**Example**:
```markdown
## Handoff: Acceptance Criteria

### Code Quality
- [ ] Run `cd frontend && npx tsc --noEmit` → 0 errors
- [ ] Run `npm run lint` → 0 errors
- [ ] Run `npm run build` → Build succeeds

### Functionality
- [ ] WebSocket connection establishes successfully
- [ ] Student can send messages (input field works)
- [ ] AI Patient responses appear in chat (backend integration works)
- [ ] Auto-scroll to latest message works
- [ ] Typing indicator shows when AI is "thinking"
- [ ] Session ends gracefully after 8 minutes
- [ ] Reconnection works if connection drops

### Testing Requirements

#### Unit Tests (≥80% coverage target)

```python
def test_patient_persona_creation():
    """Test valid persona creation with JSONB fields"""
    persona = PatientPersona(
        persona_code="CARD-001",
        name="Test Patient",
        age=52,
        gender="Male",
        specialty="cardiology",
        chief_complaint="Chest pain",
        opening_statement="I have chest pain",
        symptoms={"immediate": ["chest pain"]},
        medical_history={"volunteer": ["diabetes"]},
        emotional_profile={"baseline_state": "ANXIOUS_GUARDED"},
    )
    db.add(persona)
    db.commit()

    assert persona.persona_id is not None
    assert persona.symptoms["immediate"] == ["chest pain"]
```

#### Integration Tests

```python
@pytest.mark.integration
def test_create_osce_session_api():
    """Test full session creation flow via API"""
    # Setup
    client = TestClient(app)
    token = create_test_jwt(user_id="test-user-123")

    # Execute
    response = client.post(
        "/api/v1/osce-sessions",
        json={"persona_id": "CARD-001", "session_type": "practice"},
        headers={"Authorization": f"Bearer {token}"}
    )

    # Verify
    assert response.status_code == 201
    assert "session_id" in response.json()
    assert "ws_url" in response.json()
```

#### E2E Tests (Playwright)

```typescript
test('Student can start OSCE session and send message', async ({ page }) => {
  // Login
  await page.goto('/login');
  await page.fill('[name="email"]', 'student@test.com');
  await page.fill('[name="password"]', 'password123');
  await page.click('button[type="submit"]');

  // Navigate to OSCE Practice
  await page.goto('/osce-practice');
  await page.click('[data-testid="persona-CARD-001"]');
  await page.click('button:has-text("Start Session")');

  // Send message
  await page.fill('[aria-label="Chat message input"]', 'Hello, how are you feeling?');
  await page.click('[aria-label="Send message"]');

  // Verify AI response appears
  await expect(page.locator('[data-testid="ai-message"]')).toBeVisible();
});
```

### Security Validation

```bash
# Check for hardcoded credentials
grep -r "hardcoded\|localhost:8001\|ws://" frontend/src/components/osce/ frontend/src/hooks/
# Expected: 0 matches

# Check for API keys in code
grep -r "ANTHROPIC_API_KEY\|CLAUDE_API_KEY" backend/src/
# Expected: 0 matches (should use environment variables)

# Check for SQL injection vulnerabilities
grep -r "execute(.*f\"" backend/src/
# Expected: 0 matches (should use parameterized queries)
```

### Performance Benchmarks

```bash
# API response time test
curl -w "@curl-format.txt" -o /dev/null -s "http://localhost:8001/api/v1/patient-personas"
# Expected: <200ms (p95)

# WebSocket latency test
# Send message → Receive response latency
# Expected: <500ms (p95)

# Database query performance
EXPLAIN ANALYZE SELECT * FROM patient_personas WHERE specialty = 'cardiology' LIMIT 10;
# Expected: <50ms
```
```

---

## Agent Specification Format

**Required Fields**:
1. **Agent Type** (from Agent OS expert list)
2. **Constraints** (what agent MUST/MUST NOT do)
3. **Validation Checklist** (agent self-validates before returning)
4. **Examples** (code patterns to follow)

**Example**:
```markdown
## Agent OS Expert Constraints

### Agent: flutter-desktop-expert

**CRITICAL**: Read these constraints before starting:

1. **Existing Code Patterns** (MUST FOLLOW):
   - Use Material-UI components (already in project: `@mui/material`)
   - Follow existing page structure: See `frontend/src/pages/MCQBrowser.tsx` for layout patterns
   - Use React Query for data fetching: See `frontend/src/api/mcqs.ts` for API patterns
   - TypeScript strict mode: NO `any` types allowed
   - Component file naming: PascalCase (e.g., `OSCEChatInterface.tsx`)

2. **WebSocket Integration** (MUST IMPLEMENT):
   - Backend endpoint: `ws://localhost:8001/ws/osce-session/{persona_id}`
   - JWT authentication: Pass token in query params (backend already validates)
   - Message format: See WebSocketMessage interface in spec above
   - Reconnection logic: Auto-reconnect every 3 seconds on disconnect
   - Error handling: Display connection status to user

3. **Accessibility Requirements** (MUST MEET):
   - All interactive elements have `aria-label`
   - Keyboard navigation works (Tab, Enter, Shift+Enter)
   - Screen reader announces new messages
   - High contrast mode supported
   - Touch targets ≥56px for mobile

4. **Performance Requirements** (MUST ACHIEVE):
   - Message render time: <100ms
   - WebSocket latency: <500ms (send → receive)
   - Smooth scrolling: 60fps
   - Memory: <50MB for 8-minute session (~50 messages)

5. **Security Requirements** (MUST ENFORCE):
   - NO hardcoded tokens or credentials
   - Sanitize all user input (prevent XSS)
   - Use HTTPS for WebSocket in production (wss://)
   - Clear sensitive data on session end
```

---

## Validation Checklist Template

**Must Include**:
1. Compilation checks
2. Test execution commands
3. Security scans
4. Accessibility audits
5. Performance benchmarks

**Example**:
```markdown
## Validation Checklist (Complete Before Returning!)

### Code Quality
- [ ] Run `cd frontend && npx tsc --noEmit` → 0 errors
- [ ] Run `npm run lint` → 0 errors
- [ ] Run `npm run build` → Build succeeds

### Testing
- [ ] Run `npm test` → All tests pass
- [ ] Run `pytest backend/tests/` → 100% pass rate
- [ ] Coverage report → ≥70% for new code

### Security
- [ ] Run `grep -r "hardcoded" src/` → 0 matches
- [ ] Run `npm audit` → 0 high/critical vulnerabilities
- [ ] XSS test: Send `<script>alert('xss')</script>` → Displays as text, not executed

### Accessibility
- [ ] Keyboard navigation: Tab through all elements
- [ ] Screen reader: VoiceOver/NVDA announces messages
- [ ] High contrast mode: All text readable
- [ ] Touch targets: All buttons ≥56px

### Performance
- [ ] Send message → Response latency: <500ms
- [ ] Scroll performance: 60fps (use Chrome DevTools)
- [ ] Memory leak check: No continuous growth over 8 minutes
```

---

## Reference Verification (RAG Content)

**When PRD Includes Content Generation**:
1. All facts MUST have `qdrant_point_id` (UUID)
2. Citations link to source documents
3. No hallucinations (100% traceable)
4. Australian medical sources prioritized (≥60%)

**Example**:
```markdown
## Reference Verification

**RAG Requirements**:
- All patient persona clinical facts must cite source
- Citations format: `qdrant_point_id: UUID`
- Australian medical sources: ≥60% (Murtagh, Talley, eTG)

**Quality Assurance**:
- Run QA validator: `python clinical-content-prds/validation-system/qa_validator.py batch1_personas/`
- Expected: 97%+ quality score, 0 hallucinations

**Example Citation**:
```json
{
  "red_flags": [
    {
      "flag": "Sudden-onset severe headache ('thunderclap')",
      "implication": "Subarachnoid hemorrhage until proven otherwise",
      "citation": {
        "source": "Talley & O'Connor Clinical Examination 9th Ed",
        "qdrant_point_id": "550e8400-e29b-41d4-a716-446655440000",
        "page": "p. 412"
      }
    }
  ]
}
```
```

---

## Test Commands Section

**Required**:
- Exact bash commands to validate implementation
- Expected outputs
- Performance benchmarks

**Example**:
```markdown
## Test Commands

```bash
# TypeScript validation
cd /home/dev/Development/irStudy/frontend
npx tsc --noEmit
# Expected: 0 errors

# Build test
npm run build
# Expected: Build succeeded

# Lint check
npm run lint
# Expected: 0 errors

# Unit tests
npm test
# Expected: All tests passed

# Integration tests
cd /home/dev/Development/irStudy/backend
pytest tests/test_api/test_osce_sessions.py -v
# Expected: 10/10 tests passed

# Security scan
grep -r "hardcoded\|localhost\|ws://" src/components/osce/OSCEChatInterface.tsx src/hooks/useWebSocket.ts
# Expected: 0 matches

# Accessibility audit (manual)
# 1. Open http://localhost:5173/osce-practice
# 2. Start session
# 3. Use only keyboard (no mouse)
# 4. Verify all actions possible via Tab/Enter

# Performance test
# 1. Open Chrome DevTools → Performance tab
# 2. Start recording
# 3. Send 20 messages
# 4. Check FPS (should be 60fps during scrolling)
```
```

---

## Files Created/Modified Section

**Required**:
- Exact file paths
- Line counts
- Purpose of each file

**Example**:
```markdown
## Files to Create/Modify

### Created (3 files)
- `frontend/src/components/osce/OSCEChatInterface.tsx` (~300 lines)
  - WebSocket chat UI component
  - Material-UI layout
  - Auto-scroll, typing indicators

- `frontend/src/hooks/useWebSocket.ts` (~150 lines)
  - WebSocket connection management
  - Auto-reconnect logic
  - JWT authentication

- `backend/alembic/versions/20260317_1200_add_osce_sessions.py` (~80 lines)
  - Database migration for ai_osce_attempts table
  - Indexes for performance

### Modified (2 files)
- `frontend/src/App.tsx` (+8 lines)
  - Add /osce-practice route

- `frontend/src/routes.tsx` (+1 line)
  - Lazy load OSCEPractice component
```

---

## Appendices (Optional but Recommended)

1. **Sample Data Structures** (JSON examples)
2. **Error Codes** (comprehensive list)
3. **Migration Rollback** (SQL for downgrade)
4. **Performance Profiling** (flamegraphs, traces)
5. **Related PRDs** (dependencies, blockers)

---

## Best Practices from ralph-claude-code

1. **Specification Workshops** (Three Amigos approach)
   - Developer, Tester, Product Owner perspectives
   - Given/When/Then scenarios
   - Edge case identification before coding

2. **Template Variables** (for reusable PRDs)
   ```json
   {
     "$variables": {
       "feature_name": "",
       "agent": "flutter-desktop-expert"
     },
     "title": "Implement {{feature_name}} feature"
   }
   ```

3. **JSON Schema Validation**
   ```bash
   ajv validate -s .ralph/schemas/prd-schema.json -d prds/TASK-001.json
   ```

4. **Agent OS Integration**
   - Explicit agent assignments (flutter-desktop-expert, rust-ffi-expert, etc.)
   - Agent-specific constraints and patterns
   - Validation checklists agents must complete

---

## Common Mistakes to Avoid

❌ **Vague acceptance criteria** ("Feature works")
✅ **Specific criteria** ("0 TypeScript errors, <500ms latency, 100% test pass")

❌ **Missing test examples** (just "write tests")
✅ **Concrete test code** (full pytest/jest examples)

❌ **No security validation** (assume code is secure)
✅ **Explicit security scans** (grep for hardcoded credentials, XSS tests)

❌ **Generic agent assignment** ("general-purpose agent")
✅ **Expert agent with constraints** ("flutter-desktop-expert with MUST FOLLOW patterns")

❌ **Short PRDs** (500 lines)
✅ **Comprehensive PRDs** (2,000+ lines with full R-A-L-P-H structure)

---

## Ralph Loop Execution

**State File**: `.ralph-production-state.json`

```json
{
  "started_at": "2026-03-17T10:00:00Z",
  "current_prd": "PRD-PHASE1-001",
  "completed_prds": [],
  "failed_prds": [],
  "total_prds": 21,
  "completed_count": 0
}
```

**Execution Script**: `scripts/ralph-production-loop.sh`

```bash
#!/usr/bin/env bash
execute_prd() {
  local prd_file="$1"
  echo "Executing PRD: $prd_file"

  # Read PRD content
  claude_read "$prd_file"

  # Execute PRD (agent follows R-A-L-P-H structure)
  # Agent self-validates using Handoff checklist
  # PM validates acceptance criteria
  # Mark complete if all criteria pass
}
```

---

**Last Updated**: 2026-03-17
**Source**: ralph-claude-code/ folder analysis
**Next Step**: Update PRD-PHASE1-001 to follow these standards
