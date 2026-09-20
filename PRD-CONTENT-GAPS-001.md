# PRD-CONTENT-GAPS-001: Net-New Content for Empty/Thin Specialties (RAG-Grounded, Claude)

**PRD ID**: PRD-CONTENT-GAPS-001
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
./scripts/ralph_loop.sh --calls 80 --prompt /home/dev/Development/irStudy/PRD-CONTENT-GAPS-001.md
```
**Runtime prerequisites**: `$DATABASE_PASSWORD` (backend/.env); Qdrant at `$QDRANT_URL` with `medical_knowledge`; **Claude API only — NEVER local/ollama LLM** (`python-llm-integration` skill). Large run — high `--calls`.

---

## 0 - DISCOVERY (verified at planning time, live DB)

### 0.1 Search evidence — the gaps (from COVERAGE.md + live queries)
- **MCQ-empty specialties (0 MCQs each)**: surgery, obstetrics_gynaecology, ophthalmology, urology, musculoskeletal; emergency_medicine has 1. → need MCQs.
- **OSCE-thin/empty**: paediatrics 1, surgery 2, endocrinology 0 OSCEs. → need OSCEs.
- Conditions already exist for surgery/O&G/ophthal/urology/MSK (OSCE-derived, seeded in PRD-CONDITIONS-SPINE) so generated content can link.

### 0.2 Discovery Results (REUSE — verified)
| Capability | Location | Reuse verdict |
|---|---|---|
| Claude MCQ generation | `scripts/generate_mcqs_claude.py` | REUSE |
| RAG-grounded MCQ scaffold | `scripts/generate_mcqs_from_rag.py` | REUSE |
| OSCE generation pattern | `scripts/generate_respiratory_osces_with_images.py` (+ cardiology/psychiatry variants) | REUSE as template |
| Persona generation | `scripts/generate_personas.py` (`PersonaGenerator`, RAG-grounded, Claude-only) | REUSE |
| Ground text → point-id citations | `backend/src/ai/rag_service.py:146` `search_similar` | REUSE |
| Citation attach + Australian ratio | `backend/src/ai/mcq_citation_remediator.py` | REUSE |
| MCQ import + validate | `backend/scripts/import_mcqs.py` (`transform_mcq`, `validate_record`, importer) | REUSE |
| OSCE import | `backend/scripts/import_osces.py` (`import_osces`, line 146) | REUSE |
| Seed + link to conditions | `scripts/seed_conditions.py`, `scripts/backfill_condition_links.py` | REUSE |
| Coverage report | `scripts/content_reconciliation.py` | REUSE (verify) |

### 0.3 Gap Analysis (BUILD-NEW)
A `scripts/generate_specialty_content.py` orchestrating per-specialty generation of MCQs (and OSCEs where thin) using the reuse targets above — RAG-grounded, Claude-only, validated, imported, linked. Nothing about the generation primitives is new; the orchestration + per-specialty topic lists are.

### 0.4 Risks
- **Never fabricate**: content without ≥0.65 RAG grounding is flagged `needs_review`, not shipped.
- **Clinical accuracy**: each specialty's first batch is clinically validated before bulk (surgery→`surgical-skills-expert`; MSK/procedures→`procedural-skills-expert`; O&G→human RANZCOG SME flag; ophthalmology/urology→`general-purpose`+RAG+human SME flag).
- **Topic sourcing**: derive topics from existing seeded conditions for that specialty + AMC blueprint, not model memory.

### 0.5 Reference Implementations
None required — all structure from verified in-repo code (0.2).

---

## T - TESTS

### Test Inventory
- Total Tests: 5 (backend pytest). Mock Claude + `RAGService` — no live API in unit tests.

### TDD Workflow (MANDATORY)
Every phase follows **RED → GREEN → REFACTOR**:
1. **RED**: write all 5 tests; confirm FAIL (module absent).
2. **GREEN**: implement minimal code to pass.
3. **REFACTOR**: improve; stay green.
**Agent Constraint**: no implementation before tests exist and are confirmed failing.

#### Test 1: generated MCQ is schema-valid for the target specialty
```python
# FILE: backend/tests/test_scripts/test_generate_specialty_content.py
from unittest.mock import MagicMock
from scripts.generate_specialty_content import SpecialtyContentGenerator

VALID_MCQ = {"question": {"scenario": "A 55F...", "stem": "Next step?",
             "options": {"A": "a", "B": "b", "C": "c", "D": "d"}},
             "correct_answer": "B", "explanation": "...", "specialty": "surgery"}

def _gen(hits, mcq=VALID_MCQ):
    claude = MagicMock(); claude.generate.return_value = mcq
    rag = MagicMock(); rag.search_similar.return_value = hits
    return SpecialtyContentGenerator(claude_client=claude, rag_service=rag)

def test_generated_mcq_valid():
    g = _gen([{"qdrant_point_id": "550e8400-e29b-41d4-a716-446655440000", "score": 0.8,
               "is_australian": True, "source": "Murtagh"}])
    mcq = g.generate_mcq(topic="Acute appendicitis", specialty="surgery")
    from scripts.import_mcqs import transform_mcq, validate_record
    assert validate_record(transform_mcq(mcq)) is None
```

#### Test 2: generated MCQ carries point-id citations
```python
def test_generated_mcq_grounded():
    g = _gen([{"qdrant_point_id": "550e8400-e29b-41d4-a716-446655440000", "score": 0.82,
               "is_australian": True, "source": "Murtagh"}])
    mcq = g.generate_mcq(topic="Acute appendicitis", specialty="surgery")
    assert mcq["citations"] and all(c["qdrant_point_id"] for c in mcq["citations"])
```

#### Test 3: ungrounded topic is flagged, not shipped
```python
def test_ungrounded_flagged():
    g = _gen([])
    out = g.generate_mcq(topic="Nonexistent", specialty="surgery")
    assert out.get("needs_review") is True and not out.get("citations")
```

#### Test 4: topics are derived from seeded conditions, not invented
```python
def test_topics_from_conditions():
    g = _gen([{"qdrant_point_id": "id", "score": 0.8, "is_australian": True, "source": "Murtagh"}])
    topics = g.topics_for_specialty("surgery", conditions=[{"specialty": "surgery", "name": "Acute Appendicitis"},
                                                           {"specialty": "cardiology", "name": "STEMI"}])
    assert "Acute Appendicitis" in topics and "STEMI" not in topics  # specialty-scoped
```

#### Test 5: never references a local LLM
```python
def test_no_local_llm():
    import inspect, scripts.generate_specialty_content as m
    src = inspect.getsource(m)
    assert "ollama" not in src.lower() and "localhost:11434" not in src
```

### Test Execution Commands
```bash
cd backend && pytest tests/test_scripts/test_generate_specialty_content.py -v
```

---

## R - REQUEST

**User story**: As an AMC candidate, I can practise across the full blueprint — surgery, O&G, emergency, ophthalmology, urology, MSK MCQs and paediatric/endocrine OSCEs — not just the currently-covered specialties.

**Business context**: 6 specialties have zero MCQs and several have no OSCEs. Mock exams and topic practice are lopsided. This PRD fills the measured gaps to a defined minimum, grounded and Australian-sourced, so coverage-by-blueprint is non-zero everywhere.

**Out of scope**: persona quality remediation (backlog); MCQ regeneration (PRD-MCQ-REGEN-001).

---

## A - ARCHITECTURE

```
for each target specialty (topics from seeded conditions of that specialty):
  → RAGService.search_similar(topic + "Australian management")   [REUSE]
      → drop no-point-id / score<0.65
  → Claude generate MCQ / OSCE / persona (schema)                 [REUSE generate_mcqs_claude / osce template / personas]
  → validate (transform_mcq+validate_record for MCQ; import_osces validation for OSCE); attach citations (≥60% AU)
  → ungrounded/invalid → needs_review, not shipped
  → write to data/mcqs/<specialty>_generated.json / data/osces/<specialty>_generated.json
  → import (import_mcqs / import_osces) + re-seed + backfill_condition_links --apply
  → content_reconciliation → coverage rises for that specialty
```
- New: `scripts/generate_specialty_content.py` (`SpecialtyContentGenerator`; injectable claude_client + rag_service).
- **Targets & minimums**: MCQs ≥30 each for surgery, obstetrics_gynaecology, ophthalmology, urology, musculoskeletal, emergency_medicine; OSCEs ≥5 each for paediatrics, surgery, endocrinology. Claude-only.

---

## L - LOOP

### Loop Execution Strategy
**CRITICAL**: sequential, TDD-enforced (**RED → GREEN → REFACTOR**). Phase 1 builds+tests the generator; Phases 2A–2C generate per specialty group (each: generate → clinical review → import → link → verify coverage); Phase 3 final coverage verify. Per-specialty phases are independent and MAY be delegated in parallel by capable models.

**Phase Dependency Chain**:
```
Phase 1 (generator, unit-tested) → Phase 2A (MCQ-empty specialties) + Phase 2B (thin-OSCE specialties) → Phase 3 (coverage verify) → COMPLETE
```
**Blocking conditions**: any unit test failing · ungrounded content shipped · any local-LLM reference · clinical reviewer rejects a specialty batch · a target specialty below its minimum with no documented reason.

**Recovery Protocol**: fix the current phase before advancing; never ship ungrounded/unvalidated content; O&G and ophthalmology/urology batches that need human SME sign-off are marked pending-SME (not auto-accepted); document blockers in H.

### Phase 1: SpecialtyContentGenerator + validator (Tests 1–5)
**TDD Workflow (MANDATORY)**: RED (write Tests 1–5) → GREEN (`SpecialtyContentGenerator`) → REFACTOR.
**Blocker**: any test failing or a local-LLM reference → phase BLOCKED.

### Phase 2A: MCQs for MCQ-empty specialties
**TDD Workflow (MANDATORY)**: unit tests stay green. Per specialty (surgery, O&G, ophthalmology, urology, MSK, emergency): topics from seeded conditions → generate ≥30 grounded MCQs → clinical-expert sample review → import + link. O&G/ophthalmology/urology: mark pending human SME.
**Blocker**: below-minimum without reason, ungrounded shipped, or reviewer rejection.

### Phase 2B: OSCEs for thin specialties
**TDD Workflow (MANDATORY)**: paediatrics, surgery, endocrinology → generate ≥5 grounded OSCE stations each (reuse the osces_with_images template) → clinical review → import + link.
**Blocker**: as above.

### Phase 3: coverage verify
**TDD Workflow (MANDATORY)**: run `content_reconciliation.py`; confirm every target specialty now non-zero and at/above minimum (or documented). Re-run mock-exam real-data test.
**Blocker**: a target specialty still zero without documented reason.

---

## P - PLAN
- Topic lists come from `conditions` rows for each specialty (query DB) + AMC blueprint — never model memory.
- Reuse `import_mcqs.validate_record` + `import_osces` validation as the acceptance guard; reuse `mcq_citation_remediator` for citations.
- Idempotent: skip ids already present unless `--force`; `--limit`/`--specialty` flags for incremental runs.
- Australian context mandatory; ≥60% Australian citations.
- Never fabricate: ungrounded → `_reports/content_gaps_needs_review.json`, not shipped.
- Human-SME specialties (O&G, ophthalmology, urology) shipped as `pending_sme=true` until signed off.

---

## H - HANDOFF

### Test Results Summary
```
[TO BE FILLED BY RALPH — pytest 5/5 passing]
```

### TDD Compliance Verification
- [ ] All 5 tests written BEFORE implementation (RED confirmed failing)
- [ ] All 5 passing after implementation (GREEN); still passing after refactor
- [ ] 0 tests skipped

### Generation results (per specialty)
- MCQs generated/imported: surgery `[FILL]`, O&G `[FILL]`, ophthalmology `[FILL]`, urology `[FILL]`, MSK `[FILL]`, emergency `[FILL]`
- OSCEs generated/imported: paediatrics `[FILL]`, surgery `[FILL]`, endocrinology `[FILL]`
- needs_review (ungrounded): `[FILL]`; pending_sme: `[FILL]`
- Australian-source ratio: `[FILL]` (≥0.60)

### Coverage after (from content_reconciliation.py)
```
[TO BE FILLED — coverage-by-blueprint; every target specialty non-zero]
```

### Success Criteria
- [ ] 5/5 tests passing
- [ ] Each MCQ-empty specialty ≥30 MCQs; each thin-OSCE specialty ≥5 OSCEs (or documented shortfall)
- [ ] Every shipped item schema-valid with ≥1 qdrant_point_id citation; ungrounded flagged not fabricated
- [ ] O&G/ophthalmology/urology batches marked pending_sme for human sign-off
- [ ] coverage-by-blueprint non-zero for all target specialties; mock-exam real-data test still passes
- [ ] No local-LLM code path (Test 5 green)

### Deliverables Checklist
- [ ] `scripts/generate_specialty_content.py` (`SpecialtyContentGenerator`)
- [ ] `data/mcqs/<specialty>_generated.json` + `data/osces/<specialty>_generated.json`
- [ ] `_reports/content_gaps_needs_review.json`
- [ ] Imported + linked; coverage report updated

---

## Permissions (Ralph Autonomous Execution)

<!-- RALPH-PERMISSIONS:BEGIN -->
allow:
  - Bash(cd backend && pytest:*)
  - Bash(python scripts/generate_specialty_content.py:*)
  - Bash(python backend/scripts/import_mcqs.py:*)
  - Bash(python backend/scripts/import_osces.py:*)
  - Bash(python scripts/seed_conditions.py:*)
  - Bash(python scripts/backfill_condition_links.py:*)
  - Bash(python scripts/content_reconciliation.py:*)
add-dir:
  - /home/dev/Development/irStudy
<!-- RALPH-PERMISSIONS:END -->

---

### Quality Gates

**Tests:**
- [ ] `cd backend && pytest tests/test_scripts/test_generate_specialty_content.py` → passing

**No local LLM (project rule):**
- [ ] `! grep -rEni "ollama|localhost:11434" scripts/generate_specialty_content.py` → exit code 0

**Compile:**
- [ ] `cd backend && python -m py_compile ../scripts/generate_specialty_content.py` → exit code 0

**Security (passes only when no secret is found):**
- [ ] `! grep -rEn "sk-ant-|ANTHROPIC_API_KEY\s*=\s*['\"]|DATABASE_PASSWORD\s*=\s*['\"]" scripts backend/src` → exit code 0

**Commit — final gate:**
- [ ] `git log -1 --pretty=%s | grep -q 'PRD-CONTENT-GAPS-001'` → exit code 0

### Commit as the final gate (MANDATORY)
After every Quality Gate passes, commit the work:
`git add -A && git commit -m "feat(content): PRD-CONTENT-GAPS-001 — net-new MCQs/OSCEs for empty specialties"`.
Never commit `.env`, API keys, or generated `_reports/`.
