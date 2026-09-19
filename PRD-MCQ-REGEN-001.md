# PRD-MCQ-REGEN-001: Regenerate Ungrounded & Unimportable MCQs (RAG-Grounded, Claude)

**PRD ID**: PRD-MCQ-REGEN-001
**Project**: irStudy Platform (EMR + AI OSCE)
**Project Location**: /home/dev/Development/irStudy
**Working Directory**: /home/dev/Development/irStudy
**Technology Stack**: FastAPI (Python 3.12) + SQLAlchemy + PostgreSQL + Qdrant (RAG) + Claude API
**Status**: Ready for Implementation
**Created**: 2026-09-02
**Standards**: T-RALPH V2.6
**Prescription**: low

---

## Project Context (CRITICAL for Ralph Execution)

**IMPORTANT**: This PRD is for the **irStudy Platform** project.
**Project Constraints File**: `/home/dev/Development/irStudy/PROJECT_CONSTRAINTS.md`
**Project CLAUDE.md File**: `/home/dev/Development/irStudy/.claude/CLAUDE.md`
**Ralph Execution Command**:
```bash
cd /home/dev/Development/ralph-dashboard
./scripts/ralph_loop.sh --calls 50 --prompt /home/dev/Development/irStudy/PRD-MCQ-REGEN-001.md
```
**Runtime prerequisites**: `$DATABASE_PASSWORD` (backend/.env); Qdrant at `$QDRANT_URL` with `medical_knowledge`; **Claude API only — NEVER local/ollama LLM** (`python-llm-integration` skill).

---

## 0 - DISCOVERY (verified at planning time)

### 0.1 Search evidence
- `data/mcqs/_reports/mcq_citation_report.json`: **150 `needs_regeneration`** MCQs (no RAG citation ≥0.65). By prefix: CARD 46, GAST 39, GENE 22, NEUR 20, ENDO 14, WEEK3 8, WEEK1 1. Sample ids: `ENDO-MCQ-0002`, `ENDO-MCQ-0011`.
- `data/mcqs/_reports/respiratory_unimportable.json`: **39 unimportable** MCQs, reason `empty_question_text` (bare-string `question`, no options); e.g. from `missing_topics_comprehensive_mcqs.json`.

### 0.2 Discovery Results (REUSE — verified file:line)
| Capability | Location | Reuse verdict |
|---|---|---|
| Claude-based MCQ generation | `scripts/generate_mcqs_claude.py` | REUSE (Claude client + prompt/validate loop) |
| RAG-grounded MCQ generation scaffold | `scripts/generate_mcqs_from_rag.py` | REUSE |
| Ground text → `{qdrant_point_id, score, source, is_australian}` | `backend/src/ai/rag_service.py:146` `search_similar` | REUSE |
| Structured-citation attach + ≥0.65 + drop-no-point-id + Australian ratio | `backend/src/ai/mcq_citation_remediator.py` (`MCQCitationRemediator`, `is_australian_source`) | REUSE |
| MCQ transform + validation guard + importer | `backend/scripts/import_mcqs.py` `transform_mcq`, `validate_record`, per-row SAVEPOINT importer | REUSE |
| Corpus report | `scripts/remediate_mcq_citations.py` `validate_corpus` | REUSE (confirm needs_regeneration → 0 after) |

### 0.3 Gap Analysis (BUILD-NEW)
A regenerator `scripts/regenerate_mcqs.py` that, for each flagged MCQ, RAG-grounds the topic, generates a full valid MCQ via Claude, validates, attaches point-id citations (≥60% Australian), writes back to the source JSON, then re-imports + re-links to conditions. Two input sets: the 150 ungrounded ids and the 39 unimportable stubs.

### 0.4 Risks
- **Never fabricate**: an MCQ with no ≥0.65 point-id-bearing RAG hit stays flagged (do not ship a fake citation).
- **Clinical accuracy**: regenerated MCQs must be clinically validated (sample per specialty via clinical experts) before bulk accept.
- **Answer integrity**: `correct_answer` must be a real key in `options`; use `import_mcqs.validate_record` as the guard.

### 0.5 Reference Implementations
None required — all structure from verified in-repo code (0.2).

---

## T - TESTS

### Test Inventory
- Total Tests: 6 (backend pytest, under `backend/tests/`). Mock the Claude client and `RAGService` — no live API in unit tests (mirror `tests/test_ai/test_mcq_citation_remediator.py`).

### TDD Workflow (MANDATORY)
Every phase follows **RED → GREEN → REFACTOR**:
1. **RED**: write all 6 tests; confirm they FAIL (module absent).
2. **GREEN**: implement minimal code to pass.
3. **REFACTOR**: improve; re-run; stay green.
**Agent Constraint**: no implementation before tests exist and are confirmed failing.

#### Test 1: regenerator produces a schema-valid MCQ
```python
# FILE: backend/tests/test_scripts/test_regenerate_mcqs.py
from unittest.mock import MagicMock
from scripts.regenerate_mcqs import MCQRegenerator

VALID_CLAUDE = {"question": {"scenario": "A 60M...", "stem": "Most appropriate next step?",
                "options": {"A": "a", "B": "b", "C": "c", "D": "d"}},
                "correct_answer": "C", "explanation": "because...", "specialty": "endocrinology"}

def _regen(hits):
    claude = MagicMock(); claude.generate.return_value = VALID_CLAUDE
    rag = MagicMock(); rag.search_similar.return_value = hits
    return MCQRegenerator(claude_client=claude, rag_service=rag)

def test_regenerated_mcq_is_schema_valid():
    r = _regen([{"qdrant_point_id": "550e8400-e29b-41d4-a716-446655440000", "score": 0.8,
                 "is_australian": True, "source": "eTG"}])
    mcq = r.regenerate(topic="Hyperthyroidism", specialty="endocrinology")
    from scripts.import_mcqs import transform_mcq, validate_record
    rec = transform_mcq(mcq)
    assert validate_record(rec) is None  # None == valid
```

#### Test 2: regenerated MCQ carries point-id citations (≥1)
```python
def test_regenerated_mcq_has_pointid_citations():
    r = _regen([{"qdrant_point_id": "550e8400-e29b-41d4-a716-446655440000", "score": 0.82,
                 "is_australian": True, "source": "eTG"}])
    mcq = r.regenerate(topic="Hyperthyroidism", specialty="endocrinology")
    assert mcq["citations"] and all(c["qdrant_point_id"] for c in mcq["citations"])
```

#### Test 3: ungrounded topic is NOT shipped (flagged, not fabricated)
```python
def test_ungrounded_topic_flagged_not_fabricated():
    r = _regen([])  # no RAG hit ≥0.65
    out = r.regenerate(topic="Nonexistent", specialty="endocrinology")
    assert out.get("needs_review") is True and not out.get("citations")
```

#### Test 4: correct_answer resolves into options
```python
def test_correct_answer_in_options():
    r = _regen([{"qdrant_point_id": "id", "score": 0.8, "is_australian": True, "source": "eTG"}])
    mcq = r.regenerate(topic="Graves", specialty="endocrinology")
    q = mcq["question"]; assert mcq["correct_answer"] in q["options"]
```

#### Test 5: unimportable stub is rebuilt into full question form
```python
def test_unimportable_stub_rebuilt():
    r = _regen([{"qdrant_point_id": "id", "score": 0.8, "is_australian": True, "source": "eTG"}])
    stub = {"id": "IMPORTED-X", "question": "bare string, no options", "specialty": "respiratory"}
    mcq = r.rebuild(stub)
    assert isinstance(mcq["question"], dict) and len(mcq["question"]["options"]) >= 2
```

#### Test 6: never references a local LLM (project rule)
```python
def test_no_local_llm():
    import inspect, scripts.regenerate_mcqs as m
    src = inspect.getsource(m)
    assert "ollama" not in src.lower() and "localhost:11434" not in src
```

### Test Execution Commands
```bash
cd backend && pytest tests/test_scripts/test_regenerate_mcqs.py -v
```

---

## R - REQUEST

**User story**: As an AMC candidate, every MCQ I attempt is a complete, answerable question backed by a verifiable Australian source — no blank stems, no ungrounded claims.

**Business context**: 150 MCQs have no RAG grounding and 39 are structurally broken (blank question/options) — they either can't be served or fail the citation-integrity promise. This PRD regenerates them to the same standard as the remediated corpus.

**Out of scope**: net-new specialty content (PRD-CONTENT-*); persona quality debt (separate backlog).

---

## A - ARCHITECTURE

```
input: 150 ungrounded ids (mcq_citation_report.json) + 39 unimportable stubs (respiratory_unimportable.json)
  → for each: RAGService.search_similar(topic + "Australian management")   [REUSE rag_service.py:146]
      → drop hits w/o qdrant_point_id / score<0.65                          [MIRROR mcq_citation_remediator]
      → Claude prompt (grounded facts + schema) → full MCQ                  [REUSE generate_mcqs_claude.py]
      → transform_mcq + validate_record must pass; correct_answer ∈ options [REUSE import_mcqs]
      → attach citations (≥60% Australian); if no grounding → needs_review, skip
  → write back into the source data/mcqs/*.json (replace the flagged item by id)
  → re-import (import_mcqs.py) + re-link (backfill_condition_links.py)
  → re-run remediate_mcq_citations validate_corpus → needs_regeneration ≈ 0
```
- New: `scripts/regenerate_mcqs.py` (`MCQRegenerator`, injectable `claude_client` + `rag_service`).
- Claude-only; no ollama/local refs (Test 6).

---

## L - LOOP

### Loop Execution Strategy
**CRITICAL**: 3-phase sequential, TDD-enforced (**RED → GREEN → REFACTOR** each). Phase 2 depends on Phase 1 (regenerator); Phase 3 on Phase 2 (regenerated data).

**Phase Dependency Chain**:
```
Phase 1 (MCQRegenerator, unit-tested) → Phase 2 (grounded regen + clinical review) → Phase 3 (re-import + re-link + corpus verify) → COMPLETE
```
**Blocking conditions**: any unit test failing · an ungrounded MCQ shipped with a citation · any local-LLM reference · clinical reviewer rejects a batch.

**Recovery Protocol**: fix the current phase before advancing; never ship an ungrounded/unvalidated MCQ; revert refactors that break green; document blockers in H.

### Phase 1: MCQRegenerator + validator (Tests 1–6)
**TDD Workflow (MANDATORY)**: RED (write Tests 1–6, mocked Claude/RAG) → GREEN (`MCQRegenerator.regenerate` + `.rebuild`) → REFACTOR.
**Blocker**: any test failing or a local-LLM reference → phase BLOCKED (no real generation).

### Phase 2: grounded regeneration + clinical review
**TDD Workflow (MANDATORY)**: unit tests stay green. Small batch first (`--limit`), route a sample per specialty through the matching clinical expert (e.g. `medication-management-expert`, `pathology-interpretation-expert`) before bulk; write regenerated items back to source JSON; ungrounded → `_reports/mcq_regen_needs_review.json`, not shipped.
**Blocker**: clinical reviewer rejects a batch, or a shipped MCQ lacks a point-id citation.

### Phase 3: re-import + re-link + corpus verify
**TDD Workflow (MANDATORY)**: re-run `import_mcqs.py`, `backfill_condition_links.py --apply`, and `remediate_mcq_citations.py`; confirm `needs_regeneration` ≈ 0 and the 39 stubs are now importable.
**Blocker**: needs_regeneration not materially reduced, or new invalid rows introduced.

---

## P - PLAN
- Regenerate in place by `id` (replace the flagged item in its source `data/mcqs/*.json`); keep a pre-image backup under a gitignored `_reports/` path.
- Reuse `import_mcqs.validate_record` as the single acceptance guard; reuse `mcq_citation_remediator` for citation attachment.
- Idempotent: skip ids already grounded/valid unless `--force`.
- Australian context mandatory (drugs/PBS/000/guidelines); ≥60% Australian citations per MCQ.
- Never fabricate: no ≥0.65 grounding → `needs_review`, not shipped.

---

## H - HANDOFF

### Test Results Summary
```
[TO BE FILLED BY RALPH — pytest 6/6 passing]
```

### TDD Compliance Verification
- [ ] All 6 tests written BEFORE implementation (RED confirmed failing)
- [ ] All 6 passing after implementation (GREEN); still passing after refactor
- [ ] 0 tests skipped

### Regeneration results
- Ungrounded regenerated / still needs_review: `[FILL]` / `[FILL]` (of 150)
- Unimportable rebuilt / still invalid: `[FILL]` / `[FILL]` (of 39)
- needs_regeneration before → after: `150 → [FILL]`
- Australian-source ratio of regenerated: `[FILL]` (≥0.60)
- Re-import delta + newly-linked to conditions: `[FILL]`

### Success Criteria
- [ ] 6/6 tests passing
- [ ] Every shipped regenerated MCQ is schema-valid (transform_mcq/validate_record) with correct_answer ∈ options
- [ ] Every shipped regenerated MCQ has ≥1 qdrant_point_id citation; ungrounded ones flagged not fabricated
- [ ] needs_regeneration ≈ 0; the 39 stubs importable
- [ ] Clinical-expert sample sign-off recorded per specialty
- [ ] No local-LLM code path (Test 6 green)

### Deliverables Checklist
- [ ] `scripts/regenerate_mcqs.py` (`MCQRegenerator.regenerate` + `.rebuild`)
- [ ] Regenerated items written back into `data/mcqs/*.json`
- [ ] `_reports/mcq_regen_needs_review.json` for anything ungrounded
- [ ] Re-import + re-link applied; corpus report shows needs_regeneration ≈ 0

---

## Permissions (Ralph Autonomous Execution)

<!-- RALPH-PERMISSIONS:BEGIN -->
allow:
  - Bash(cd backend && pytest:*)
  - Bash(python scripts/regenerate_mcqs.py:*)
  - Bash(python backend/scripts/import_mcqs.py:*)
  - Bash(python scripts/backfill_condition_links.py:*)
  - Bash(python scripts/remediate_mcq_citations.py:*)
add-dir:
  - /home/dev/Development/irStudy
<!-- RALPH-PERMISSIONS:END -->

---

### Quality Gates

**Tests:**
- [ ] `cd backend && pytest tests/test_scripts/test_regenerate_mcqs.py` → passing

**No local LLM (project rule):**
- [ ] `! grep -rEni "ollama|localhost:11434" scripts/regenerate_mcqs.py` → exit code 0

**Compile:**
- [ ] `cd backend && python -m py_compile ../scripts/regenerate_mcqs.py` → exit code 0

**Security (passes only when no secret is found):**
- [ ] `! grep -rEn "sk-ant-|ANTHROPIC_API_KEY\s*=\s*['\"]|DATABASE_PASSWORD\s*=\s*['\"]" scripts backend/src` → exit code 0

**Commit — final gate:**
- [ ] `git log -1 --pretty=%s | grep -q 'PRD-MCQ-REGEN-001'` → exit code 0

### Commit as the final gate (MANDATORY)
After every Quality Gate passes, commit the work:
`git add -A && git commit -m "feat(content): PRD-MCQ-REGEN-001 — regenerate ungrounded & unimportable MCQs"`.
Never commit `.env`, API keys, or generated `_reports/`.
