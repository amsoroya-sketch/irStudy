# PRD-EMR-PRACTICE-001: EMR Documentation Assessment Engine

**PRD ID**: PRD-EMR-PRACTICE-001
**Project**: irStudy Medical Education Platform (EMR + AI OSCE)
**Project Location**: /home/dev/Development/irStudy
**Working Directory**: /home/dev/Development/irStudy
**Technology Stack**: FastAPI (Python 3.12) + PostgreSQL/SQLAlchemy + Anthropic Claude + HashiCorp Vault
**Repository**: git@github.com-sketch:amsoroya-sketch/irStudy.git
**Status**: Ready for Implementation
**Created**: 2026-08-26
**Standards**: T-RALPH V2.6
**Prescription**: low
**Estimated Effort**: 5-7 hours

---

## Project Context (CRITICAL for Ralph Execution)

**IMPORTANT**: This PRD is for the **irStudy** project.

**Project Constraints File**: `/home/dev/Development/irStudy/PROJECT_CONSTRAINTS.md`
**Project CLAUDE.md File**: `/home/dev/Development/irStudy/.claude/CLAUDE.md`

**Technology Stack**:
- **Backend**: FastAPI (Python 3.12), SQLAlchemy 2.0
- **Database**: PostgreSQL (`irstudy_medical` @ localhost:5433)
- **AI**: Anthropic Claude (key from HashiCorp Vault `emr/claude-api-key`)
- **Testing**: pytest, pytest-asyncio, pytest-mock

**Ralph Execution Command**:
```bash
cd /home/dev/Development/ralph-dashboard
./scripts/ralph_loop.sh --calls 40 --prompt /home/dev/Development/irStudy/planning/emr-challenging-scenarios/prds/PRD-EMR-PRACTICE-001.md
```

---

## 0 - DISCOVERY

**Ponytail Principle**: This feature is ~75% built and disconnected. Reuse the existing validator,
models, and submit path; the work is wiring + an answer-key prompt, NOT new infrastructure.

### 0.1 Existing Code Search (evidence — verified 2026-08-26)

```bash
# The mock that must be replaced (live student assessment path)
grep -n "MOCK implementation\|mock_validation" backend/src/api/v1/emr/sessions.py
# → 618: "# NOTE: This is a MOCK implementation for testing"
# → 627: mock_validation = { "overall_score": 12.5, ... }  (hardcoded, persisted verbatim)

# The real validator that already exists (orphaned — imported only)
grep -rn "class ClaudeValidator\|async def validate" backend/src/services/emr/validators/claude_validator.py
# → 24: class ClaudeValidator ; 36: async def validate(cls, soap_note, patient_context, rule_based_result)

grep -rn "ClaudeValidator" backend/src --include=*.py | grep -v claude_validator.py
# → only backend/src/services/emr/validators/__init__.py:16 (never called by an endpoint)

# The answer-key column already in the DB but unmapped in the ORM
grep -n "validation_criteria\|source_osce_id\|physical_exam_findings" backend/alembic/versions/20260215_1200_008_add_emr_tables.py
# → columns present in migration 008 (validation_criteria JSON, source_osce_id FK, etc.)
grep -n "validation_criteria" backend/src/db/models.py
# → 0 matches (NOT mapped in MockPatient ORM at models.py:1385)

# The result table that is never written
grep -rn "EMRValidationResult(" backend/src --include=*.py
# → 0 matches (model exists at models.py:1487, never instantiated)
```

### 0.2 Discovery Results (reuse targets — all verified to exist)

| Component | Location | Reuse decision |
|---|---|---|
| Mock Layer-3 block (to replace) | `backend/src/api/v1/emr/sessions.py:617-663` | REPLACE with real call |
| Real Claude validator | `backend/src/services/emr/validators/claude_validator.py:36` (`ClaudeValidator.validate`) | REUSE (wire in) |
| Prompt builder (to extend) | `claude_validator.py` `_build_validation_prompt` (~line 130) | EXTEND for answer-key |
| PHI anonymiser | `claude_validator.py` `_anonymize_phi` (~line 100) | REUSE unchanged |
| Vault key | `emr/claude-api-key` (via `src/core/vault.py` `VaultClient`) | REUSE |
| Layers 1-2 (rule-based, AU terminology) | `sessions.py:563-615` | KEEP (real) |
| MockPatient ORM (to extend) | `backend/src/db/models.py:1385` | MAP unmapped columns |
| EMRValidationResult model | `backend/src/db/models.py:1487` | POPULATE (currently never written) |
| Submit endpoint | `sessions.py:435` `submit_session`; read path `get_session:232-264` | REUSE (score_breakdown shape unchanged) |

### 0.3 Gap Analysis
- `MockPatient` ORM does not map `validation_criteria` (the answer-key) → assessment can't read it.
- Layer-3 is hardcoded → every submission scores 12.5/15 regardless of content.
- `_build_validation_prompt` grades a generic rubric, not "captured vs expected".
- `EMRValidationResult` is never persisted.

### 0.4 Do NOT touch (verified dead relative to the live route)
`backend/src/services/emr/session_service.py` (raw-SQL, not imported by endpoints) and
`PatientService` (unused by `/sessions/start`). Do not add a third validation path
(`src/ai/clinical_validator.py` is wired only to the secondary `/emr/validation/soap-note` endpoint).

### 0.5 Reference Implementations
None external — all patterns are in-repo (this project's own `ClaudeValidator` + submit path).

---

## T - TESTS (Write These FIRST)

### Test Inventory
- Total: 12 tests · file: `backend/tests/test_emr/test_assessment_engine.py`
- All Anthropic API calls are **mocked** (no live key needed in unit tests).

### TDD Workflow (MANDATORY)
1. **RED**: write all 12 tests → confirm they FAIL (feature not wired).
2. **GREEN**: implement minimal wiring → confirm PASS.
3. **REFACTOR**: clean up → tests still PASS.

**Agent Constraint**: write NO implementation before the 12 tests exist and are confirmed failing.

### Answer-key contract (`MockPatient.validation_criteria` JSON)
```jsonc
{
  "presenting_scenario": "str", "task": "str",
  "expected": { "subjective": ["str"], "objective": ["str"], "assessment": ["str"], "plan": ["str"] },
  "critical_errors": ["str"],   // committing ANY → FAIL
  "must_not_miss": ["str"]      // omitting ANY → FAIL
}
```

### Assessment result contract (returned by the engine, persisted to `score_breakdown`)
```jsonc
{
  "overall_score": 0-15, "pass_fail": true|false,
  "completeness": { "subjective": 0-100, "objective": 0-100, "assessment": 0-100, "plan": 0-100 },
  "captured": ["str"], "missing_elements": ["str"],
  "critical_errors_committed": ["str"], "accuracy_notes": ["str"],
  "category_scores": {"History_Taking":0-3, "Clinical_Reasoning":0-3, "Documentation_Quality":0-3,
                       "Patient_Safety":0-3, "Professional_Communication":0-3},
  "strengths": ["str"], "improvements": ["str"]
}
```

### Tests (full code)

Each test below is specified as full code in the single file
`backend/tests/test_emr/test_assessment_engine.py` (shared fixtures at top, then one function per test).

#### Test 1: critical error committed → pass_fail=False
#### Test 2: must-not-miss omitted → pass_fail=False
#### Test 3: complete error-free note ≥9/15 → PASS
#### Test 4: score below 9 threshold → FAIL
#### Test 5: answer-key threaded into the Claude prompt
#### Test 6: completeness returned per S/O/A/P (0-100)
#### Test 7: PHI anonymised before the Claude call
#### Test 8: Vault key missing → fallback (no crash)
#### Test 9: assess_submission returns the full result contract
#### Test 10: submit persists real score + EMRValidationResult row
#### Test 11: MockPatient ORM maps validation_criteria + clinical columns
#### Test 12: non-critical omission but ≥9 → PASS

```python
# FILE: backend/tests/test_emr/test_assessment_engine.py
import json
from unittest.mock import patch, MagicMock
import pytest

from src.services.emr.validators.claude_validator import ClaudeValidator
from src.services.emr.assessment_engine import assess_submission, decide_pass_fail

# ---- fixtures -------------------------------------------------------------
STEMI_CRITERIA = {
    "presenting_scenario": "58yo male, central crushing chest pain 40 min, diaphoretic.",
    "task": "Document assessment and initial management as admitting RMO.",
    "expected": {
        "subjective": ["SOCRATES of pain", "cardiac risk factors", "sildenafil/erectile-drug use"],
        "objective": ["BP in both arms", "ECG within 10 minutes"],
        "assessment": ["ACS/STEMI primary", "aortic dissection considered"],
        "plan": ["aspirin 300 mg chewed", "serial troponin", "STEMI pathway / cardiology", "analgesia"],
    },
    "critical_errors": ["nitrates given despite hypotension / inferior-RV infarct / recent sildenafil"],
    "must_not_miss": ["aortic dissection considered"],
}

def _claude_json(**over):
    base = {
        "overall_score": 12.0, "completeness": {"subjective": 80, "objective": 80,
        "assessment": 80, "plan": 80}, "captured": ["SOCRATES of pain"], "missing_elements": [],
        "critical_errors_committed": [], "accuracy_notes": [],
        "category_scores": {"History_Taking": 3, "Clinical_Reasoning": 3, "Documentation_Quality": 2,
                            "Patient_Safety": 2, "Professional_Communication": 2},
        "strengths": ["structured"], "improvements": ["more detail"],
    }
    base.update(over)
    return base

def _mock_anthropic(payload):
    """Return a MagicMock Anthropic client whose messages.create -> text=json.dumps(payload)."""
    client = MagicMock()
    msg = MagicMock()
    msg.content = [MagicMock(text=json.dumps(payload))]
    client.messages.create.return_value = msg
    return client

GOOD_SOAP = {"subjective": "SOCRATES pain, risk factors, denies sildenafil",
             "objective": "BP both arms, ECG done <10min, STEMI",
             "assessment": "STEMI; consider aortic dissection",
             "plan": "aspirin 300mg chewed, troponin, cardiology, analgesia"}

# ---- Test 1: critical error committed -> FAIL -----------------------------
def test_critical_error_forces_fail():
    result = _claude_json(overall_score=13.0,
        critical_errors_committed=["nitrates given despite recent sildenafil"])
    assert decide_pass_fail(result, STEMI_CRITERIA) is False

# ---- Test 2: must-not-miss omitted -> FAIL --------------------------------
def test_must_not_miss_omission_fails():
    result = _claude_json(overall_score=12.0,
        missing_elements=["aortic dissection considered"])
    assert decide_pass_fail(result, STEMI_CRITERIA) is False

# ---- Test 3: clean high score -> PASS -------------------------------------
def test_complete_note_passes():
    result = _claude_json(overall_score=12.0, critical_errors_committed=[], missing_elements=[])
    assert decide_pass_fail(result, STEMI_CRITERIA) is True

# ---- Test 4: below threshold -> FAIL --------------------------------------
def test_below_threshold_fails():
    result = _claude_json(overall_score=8.5, critical_errors_committed=[], missing_elements=[])
    assert decide_pass_fail(result, STEMI_CRITERIA) is False

# ---- Test 5: engine calls Claude with the answer-key in patient_context ---
@pytest.mark.asyncio
async def test_answer_key_threaded_into_prompt():
    with patch("src.services.emr.validators.claude_validator.anthropic.Anthropic",
               return_value=_mock_anthropic(_claude_json())), \
         patch("src.services.emr.validators.claude_validator.VaultClient") as V:
        V.return_value.get_secret.return_value = {"value": "sk-test"}
        captured = {}
        orig = ClaudeValidator._build_validation_prompt.__func__
        def spy(cls, soap, patient, rb):
            p = orig(cls, soap, patient, rb); captured["prompt"] = p; return p
        with patch.object(ClaudeValidator, "_build_validation_prompt", classmethod(spy)):
            await ClaudeValidator.validate(GOOD_SOAP, {"validation_criteria": STEMI_CRITERIA}, {})
        assert "critical_errors" in captured["prompt"] or "must_not_miss" in captured["prompt"]
        assert "aortic dissection" in captured["prompt"]

# ---- Test 6: completeness reflects captured vs missing --------------------
def test_completeness_present_in_result():
    result = _claude_json(completeness={"subjective": 50, "objective": 40, "assessment": 60, "plan": 70})
    assert set(result["completeness"]) == {"subjective", "objective", "assessment", "plan"}
    assert all(0 <= v <= 100 for v in result["completeness"].values())

# ---- Test 7: PHI anonymised before Claude call ----------------------------
@pytest.mark.asyncio
async def test_phi_anonymised_before_call():
    client = _mock_anthropic(_claude_json())
    with patch("src.services.emr.validators.claude_validator.anthropic.Anthropic", return_value=client), \
         patch("src.services.emr.validators.claude_validator.VaultClient") as V:
        V.return_value.get_secret.return_value = {"value": "sk-test"}
        await ClaudeValidator.validate(
            {"subjective": "John Smith, MRN 1234567, chest pain", "objective": "", "assessment": "", "plan": ""},
            {"validation_criteria": STEMI_CRITERIA}, {})
        sent = client.messages.create.call_args.kwargs["messages"][0]["content"]
        assert "John Smith" not in sent and "1234567" not in sent

# ---- Test 8: vault key missing -> fallback (no crash) ---------------------
@pytest.mark.asyncio
async def test_missing_vault_key_falls_back():
    with patch("src.services.emr.validators.claude_validator.VaultClient") as V:
        V.return_value.get_secret.return_value = None
        out = await ClaudeValidator.validate(GOOD_SOAP, {"validation_criteria": STEMI_CRITERIA}, {})
        assert "overall_score" in out  # fallback response shape

# ---- Test 9: assess_submission returns the full result contract ----------
@pytest.mark.asyncio
async def test_assess_submission_contract():
    with patch("src.services.emr.validators.claude_validator.anthropic.Anthropic",
               return_value=_mock_anthropic(_claude_json())), \
         patch("src.services.emr.validators.claude_validator.VaultClient") as V:
        V.return_value.get_secret.return_value = {"value": "sk-test"}
        out = await assess_submission(GOOD_SOAP, STEMI_CRITERIA, layers_1_2={"score": 10})
        for k in ("overall_score", "pass_fail", "completeness", "missing_elements",
                  "critical_errors_committed", "category_scores"):
            assert k in out

# ---- Test 10: submit persists real score + EMRValidationResult row --------
def test_submit_persists_validation_result(client, db_session, seeded_hard_case, auth_headers):
    # seeded_hard_case = a MockPatient with STEMI_CRITERIA + an in_progress EMRSession
    sid = seeded_hard_case.session_id
    with patch("src.api.v1.emr.sessions.assess_submission_sync",
               return_value=_claude_json(overall_score=6.0,
               critical_errors_committed=["nitrates given"])):
        r = client.post(f"/api/v1/emr/sessions/{sid}/submit",
                        json={"final_soap_note": GOOD_SOAP}, headers=auth_headers)
    assert r.status_code == 200
    from src.db.models import EMRSession, EMRValidationResult
    s = db_session.query(EMRSession).filter_by(id=sid).first()
    assert s.validation_score == 6.0 and s.status == "graded"
    vr = db_session.query(EMRValidationResult).filter_by(session_id=sid).first()
    assert vr is not None and vr.pass_fail is False

# ---- Test 11: MockPatient ORM now maps validation_criteria ----------------
def test_mockpatient_maps_validation_criteria(db_session):
    from src.db.models import MockPatient
    cols = MockPatient.__table__.columns.keys()
    for c in ("validation_criteria", "source_osce_id", "physical_exam_findings",
              "investigation_results", "medications", "allergies", "demographics"):
        assert c in cols

# ---- Test 12: no critical error + all must-not-miss present + >=9 -> PASS --
def test_borderline_pass():
    result = _claude_json(overall_score=9.0, missing_elements=["cardiac risk factors"],
                          critical_errors_committed=[])
    # 'cardiac risk factors' is NOT in must_not_miss -> still a PASS at >=9
    assert decide_pass_fail(result, STEMI_CRITERIA) is True
```

### Test Execution
```bash
cd backend && python -m pytest tests/test_emr/test_assessment_engine.py -q
# RED: 12 failing (assessment_engine module + ORM fields + wiring absent)
# GREEN: 12/12 passing
```

---

## R - REQUEST

**User story**: As a student practising a challenging EMR scenario, when I submit my documentation I
want a **real, case-specific assessment** — did I capture the required details, did I make a critical
error — so my PASS/FAIL reflects my actual clinical documentation, not a fixed score.

**Business context**: The EMR practice loop is unusable for real learning while every submission
returns 12.5/15. This PRD turns on genuine assessment — the load-bearing change that makes the whole
challenging-scenario feature (PRDs 002/003) meaningful.

---

## A - ARCHITECTURE

- **New module** `backend/src/services/emr/assessment_engine.py`:
  - `async assess_submission(soap_note, validation_criteria, layers_1_2) -> dict` — anonymise (reuse
    `ClaudeValidator._anonymize_phi`), call `ClaudeValidator.validate(soap, {"validation_criteria": …}, layers_1_2)`,
    merge Layers 1-2, apply `decide_pass_fail`, return the result contract.
  - `decide_pass_fail(result, criteria) -> bool` — FALSE if `critical_errors_committed` non-empty OR
    any `must_not_miss` ∈ `missing_elements`; else `overall_score >= 9`.
  - `assess_submission_sync(...)` thin wrapper for the sync endpoint (run the coroutine).
- **Extend** `ClaudeValidator._build_validation_prompt` to inject `patient_context["validation_criteria"]`
  and instruct Claude to return the result contract (completeness, captured, missing_elements,
  critical_errors_committed). Keep model + temperature; update `_parse_claude_response` to pass the
  new fields through.
- **ORM** `backend/src/db/models.py` `MockPatient`: add the 7 columns (already in DB) as
  `Column(JSON)` / `Column(...)` mappings. Add a verify Alembic migration (idempotent
  `ADD COLUMN IF NOT EXISTS` — no-op on the dev DB, real on fresh DBs).
- **Wire** `sessions.py:617-663`: replace mock with `assess_submission_sync(final_soap, patient.validation_criteria, {"layer_1": …, "layer_2": …})`; persist to `validation_score`/`score_breakdown` and insert an `EMRValidationResult` row.
- **Credential path**: Vault `emr/claude-api-key` (already used by `ClaudeValidator`).

---

## L - LOOP

### Loop Execution Strategy
**CRITICAL**: 3-phase sequential TDD workflow (RED → GREEN → REFACTOR each phase). Each phase
completes 100% of its tests before the next.

**Phase order**: 1 ORM+migration → 2 Assessment engine + prompt → 3 Wire into submit.

**Sequential requirements**: no phase advances with failing tests / type errors / security findings.
Blocking conditions: pytest failure, import error, secret found → phase BLOCKED.

**Recovery Protocol**: if a phase is blocked, fix the issue in the CURRENT phase; never proceed with
blockers; document the blocker + resolution in the H section.

**Dependency chain**:
```
Phase 1 (MockPatient ORM maps validation_criteria + 6 cols; verify migration)
    ↓ provides: readable answer-key on the case
Phase 2 (assessment_engine.py + decide_pass_fail + prompt extension)
    ↓ provides: real assess_submission() returning the result contract
Phase 3 (replace mock at sessions.py:617-663; persist EMRValidationResult)
    ↓ provides: real graded submissions
COMPLETE (12/12 tests passing)
```

### Phase 1: ORM mapping (GOAL/CONSTRAINTS/RUBRIC — prescription low)
- GOAL: `MockPatient` maps `validation_criteria, source_osce_id, demographics, medications, allergies, physical_exam_findings, investigation_results`; verify migration is idempotent.
- CONSTRAINTS: columns already exist in DB (migration 008) — do NOT recreate; migration uses `ADD COLUMN IF NOT EXISTS`. No data loss.
- RUBRIC: Test 11 passes; `alembic upgrade head` clean; existing EMR tests still pass.

### Phase 2: Assessment engine + prompt (prescription low)
- GOAL: `assess_submission` + `decide_pass_fail` implement the result contract + PASS/FAIL rule; prompt threads the answer-key.
- CONSTRAINTS: reuse `ClaudeValidator` (don't fork it); PHI anonymised; Vault-missing → fallback; Claude call mocked in tests.
- RUBRIC: Tests 1-9, 12 pass.

### Phase 3: Wire into submit (prescription low)
- GOAL: replace the mock block; persist real score + `EMRValidationResult`.
- CONSTRAINTS: keep Layers 1-2; keep `score_breakdown` shape the read path consumes (sessions.py:232-264); do not touch dead code (0.4).
- RUBRIC: Test 10 passes; manual submit on a seeded case returns a non-12.5 score.

---

## P - PLAN
1. `backend/tests/test_emr/test_assessment_engine.py` — 12 tests (RED).
2. `backend/src/db/models.py` — map 7 `MockPatient` columns.
3. `backend/alembic/versions/<ts>_map_mock_patient_answer_key.py` — idempotent verify migration.
4. `backend/src/services/emr/assessment_engine.py` — new module.
5. `backend/src/services/emr/validators/claude_validator.py` — extend prompt + parser.
6. `backend/src/api/v1/emr/sessions.py:617-671` — replace mock, persist EMRValidationResult.

---

## H - HANDOFF

### Agent constraints
**CRITICAL — read FIRST**: `/home/dev/Development/irStudy/PROJECT_CONSTRAINTS.md` (Top-10 constraints,
Section 0 discovery, security: never hardcode keys — use Vault, TDD workflow). Then this PRD's T
section. Then the existing `ClaudeValidator` + submit path. Agent: **python-backend-developer**.

### Test Results Summary
```
[TO BE FILLED BY RALPH AFTER EXECUTION]
cd backend && python -m pytest tests/test_emr/test_assessment_engine.py -q
# Expected: 12 passed
```

### TDD Compliance Verification
- [ ] All 12 tests written first and confirmed FAILING (RED) — [TO BE FILLED BY RALPH]
- [ ] 12/12 passing after implementation (GREEN) — [TO BE FILLED BY RALPH]
- [ ] Tests still passing after refactor — [TO BE FILLED BY RALPH]

### Success Criteria
- [ ] Submitting a note that commits a critical error returns `pass_fail=false`.
- [ ] A complete, error-free note ≥9/15 returns `pass_fail=true`.
- [ ] `EMRValidationResult` row written per graded submission.
- [ ] No hardcoded API keys (Vault only); PHI anonymised before Claude call.

### Deliverables Checklist
- [ ] `backend/tests/test_emr/test_assessment_engine.py` (12 tests)
- [ ] `backend/src/services/emr/assessment_engine.py`
- [ ] `MockPatient` ORM mapping + verify migration
- [ ] Extended `ClaudeValidator._build_validation_prompt` + parser
- [ ] Wired submit path (`sessions.py`) + `EMRValidationResult` persistence

### Quality Gates

**Backend tests & import:**
- [ ] `cd backend && python -m pytest tests/test_emr/test_assessment_engine.py -q` → passing
- [ ] `cd backend && python -c "import src.api.v1.emr.sessions"` → exit code 0
- [ ] `cd backend && alembic upgrade head` → success

**Security (passes only when no secret is found):**
- [ ] `! grep -rEn "sk-ant-|api_key\s*=\s*['\"]" backend/src/services/emr backend/src/api/v1/emr` → exit code 0

**Commit — final gate:**
- [ ] `git log -1 --pretty=%s | grep -q 'PRD-EMR-PRACTICE-001'` → exit code 0

### Commit as the final gate
After every Quality Gate passes, commit:
`git add -A && git commit -m "feat(emr): PRD-EMR-PRACTICE-001 — real documentation assessment engine"`.
Never commit `.env`, generated reports, or scratch files.

---

## Permissions (Ralph Autonomous Execution)

<!-- RALPH-PERMISSIONS:BEGIN -->
allow:
  - Bash(python -m pytest backend/tests/*:*)
  - Bash(cd backend && python -m pytest*:*)
  - Bash(alembic:*)
  - Bash(cd backend && alembic:*)
  - Bash(python -c:*)
add-dir:
  - /home/dev/Development/irStudy
<!-- RALPH-PERMISSIONS:END -->
