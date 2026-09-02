# PRD-PERSONA-BREADTH-001: Patient Persona Breadth Expansion (unlock full-blueprint mock exams)

**PRD ID**: PRD-PERSONA-BREADTH-001
**Project**: irStudy Platform (EMR + AI OSCE)
**Project Location**: /home/dev/Development/irStudy
**Working Directory**: /home/dev/Development/irStudy
**Technology Stack**: FastAPI (Python 3.12) + SQLAlchemy + PostgreSQL + Qdrant (RAG) + Claude API
**Status**: Ready for Implementation
**Created**: 2026-09-01
**Standards**: T-RALPH V2.6
**Prescription**: low
**Depends on**: PRD-CONDITIONS-SPINE-001 (uses its coverage-by-blueprint report to target gaps). Can run standalone against the known missing-specialty list if the spine isn't done yet.

---

## Project Context (CRITICAL for Ralph Execution)

**IMPORTANT**: This PRD is for the **irStudy Platform** project.
**Project Constraints File**: `/home/dev/Development/irStudy/PROJECT_CONSTRAINTS.md`
**Project CLAUDE.md File**: `/home/dev/Development/irStudy/.claude/CLAUDE.md`
**Ralph Execution Command**:
```bash
cd /home/dev/Development/ralph-dashboard
./scripts/ralph_loop.sh --calls 50 --prompt /home/dev/Development/irStudy/PRD-PERSONA-BREADTH-001.md
```
**Runtime prerequisites**: `$DATABASE_PASSWORD` (backend/.env); Qdrant at `$QDRANT_URL` with `medical_knowledge`; **Claude-based generation only — NEVER a local/ollama LLM** (project rule).

---

## 0 - DISCOVERY (verified)

### 0.1 The gap (measured)
The 207 imported personas cover only **5 specialties** — Cardiology 45, Emergency 42, Respiratory 40, Paediatrics 40, General Practice 40. **Zero** Neurology, Gastroenterology, Psychiatry, Obstetrics & Gynaecology, Endocrinology, Surgery. The mock-exam engine (already built: `backend/src/services/mock_exam/orchestrator.py`) can never assemble a full-breadth AMC paper; its "balanced 2×8" test only passes on a synthetic fixture.

### 0.2 Discovery Results (REUSE — verified)
| Capability | Location | Use |
|---|---|---|
| Persona JSON schema (target format) | `archive/prds/clinical-content-prds/validation-system/batch1_personas/*_persona.json` (keys: id,name,age,gender,specialty,difficulty,chief_complaint,opening_statement,symptoms,past_medical_history,medications,allergies,examination_findings,expected_diagnosis,expected_management,critical_errors,learning_objectives) | Generate identical shape |
| Persona importer | `backend/scripts/import_patient_personas.py` (globs `*_persona.json`; `map_specialty`/`map_difficulty`) | Import generated personas. **Fix**: default `--source` path is wrong — run with explicit `--source` |
| Claude-API generation pattern | `backend/scripts/generate_mcqs_claude.py` | Mirror Claude client + prompt/validate loop |
| RAG grounding (qdrant_point_id + Australian source) | `RAGService.search_similar()` `backend/src/ai/rag_service.py:146` | Ground `expected_diagnosis`/`expected_management` |
| QA report shape | `batch1_personas/*_persona_qa_report.json` | Emit equivalent QA per persona |
| PatientPersona model | `backend/src/db/models.py:672` (specialty:719, difficulty_level:734, amc_blueprint_area:736) | Persist target |

### 0.3 Gap Analysis (BUILD-NEW)
A `scripts/generate_personas.py` that, per target (specialty × condition × difficulty), generates a schema-valid, RAG-grounded persona via Claude, validates it, writes `*_persona.json`, then imports. Targets come from the conditions-spine coverage report (or the fallback missing-specialty list in 0.1).

### 0.4 Risks
- Persona clinical validity — route first N per specialty through the matching expert agent before bulk generation.
- Embedding/RAG availability — if `medical_knowledge` returns nothing ≥0.65 for a condition, persona is flagged needs_review, not imported.

### 0.5 Reference Implementations
None required — structure comes from verified in-repo code (0.2).

---

## T - TESTS

### Test Inventory
- Total Tests: 6 (backend pytest, under `backend/tests/`)
- Phase 1 (generator/validator, mocked Claude+RAG): Tests 1–6
- All tests mock the Claude client and `RAGService` — no live API calls (mirror `tests/test_ai/test_study_card_generator.py`).

### TDD Workflow (MANDATORY)
Every phase follows **RED → GREEN → REFACTOR**:
1. **RED Phase**: write all 6 tests; confirm they FAIL (module absent).
2. **GREEN Phase**: implement minimal code until they PASS.
3. **REFACTOR Phase**: improve; re-run; stay green.
**Agent Constraint**: no implementation before tests exist and are confirmed failing.

#### Test 1: generated persona has all required fields
```python
# FILE: backend/tests/test_scripts/test_generate_personas.py
from unittest.mock import MagicMock
from scripts.generate_personas import PersonaGenerator, validate_persona, REQUIRED_FIELDS

VALID = {"name": "Jane", "age": 54, "gender": "female", "specialty": "neurology",
         "difficulty": "medium", "chief_complaint": "sudden weakness",
         "opening_statement": "...", "symptoms": {}, "past_medical_history": [],
         "medications": [], "allergies": [], "examination_findings": {},
         "expected_diagnosis": "Ischaemic stroke", "expected_management": "...",
         "critical_errors": ["missed thrombolysis window"], "learning_objectives": ["..."]}

def _gen(claude_json, rag_hits):
    claude = MagicMock(); claude.generate.return_value = claude_json
    rag = MagicMock(); rag.search_similar.return_value = rag_hits
    return PersonaGenerator(claude_client=claude, rag_service=rag)

def test_generated_persona_has_required_fields():
    g = _gen(VALID, [{"qdrant_point_id": "550e8400-e29b-41d4-a716-446655440000", "score": 0.8,
                      "is_australian": True, "source": "eTG"}])
    p = g.generate(specialty="neurology", condition="Ischaemic stroke", difficulty="medium")
    assert all(f in p for f in REQUIRED_FIELDS)
```

#### Test 2: specialty and difficulty are honoured
```python
def test_specialty_and_difficulty_honoured():
    g = _gen(VALID, [{"qdrant_point_id": "id", "score": 0.8, "is_australian": True, "source": "eTG"}])
    p = g.generate(specialty="neurology", condition="Stroke", difficulty="medium")
    assert p["specialty"] == "neurology" and p["difficulty"] == "medium"
```

#### Test 3: persona grounded with citation point-ids
```python
def test_persona_grounded_with_citation_pointid():
    g = _gen(VALID, [{"qdrant_point_id": "550e8400-e29b-41d4-a716-446655440000", "score": 0.82,
                      "is_australian": True, "source": "eTG"}])
    p = g.generate(specialty="neurology", condition="Stroke", difficulty="medium")
    assert p["citations"] and all(c["qdrant_point_id"] for c in p["citations"])
```

#### Test 4: ungrounded persona is flagged, not imported
```python
def test_ungrounded_persona_rejected():
    g = _gen(VALID, [])
    p = g.generate(specialty="neurology", condition="Stroke", difficulty="medium")
    assert p["needs_review"] is True and p["citations"] == []
```

#### Test 5: validator rejects missing required fields
```python
def test_validate_persona_rejects_missing_fields():
    bad = dict(VALID); del bad["expected_diagnosis"]
    errs = validate_persona(bad)
    assert any("expected_diagnosis" in e for e in errs)
```

#### Test 6: never uses a local LLM (guard the project rule)
```python
def test_never_uses_local_llm():
    import inspect, scripts.generate_personas as m
    src = inspect.getsource(m)
    assert "ollama" not in src.lower() and "localhost:11434" not in src
```

### Test Execution Commands
```bash
cd backend && pytest tests/test_scripts/test_generate_personas.py -v
```

---

## R - REQUEST

**User story**: As an AMC candidate, I want mock exams that span the full AMC blueprint (not just 5 specialties), so a practice paper reflects the real exam. As the content team, I want persona coverage to fill the measured gaps.

**Business context**: The mock-exam engine is built but starved — only 5 of the needed specialties have personas. This PRD generates the missing personas, RAG-grounded and Australian-sourced, so the existing engine can assemble true 8-domain papers.

**Scope**: generate ≥8 personas each for the top missing specialties (Neurology, Gastroenterology, Psychiatry, Obstetrics & Gynaecology, Endocrinology, Surgery) with an easy/medium/hard spread; import them. **Out of scope**: changing the mock-exam engine (works already).

---

## A - ARCHITECTURE

```
targets (from conditions-spine coverage report, or fallback 0.1 list)
  → PersonaGenerator.generate(specialty, condition, difficulty):
        RAGService.search_similar(condition + "Australian management")   [REUSE rag_service.py:146]
          → drop hits w/o qdrant_point_id / score<0.65                    [MIRROR study_card_generator]
        Claude prompt (schema + grounded facts) → persona JSON            [MIRROR generate_mcqs_claude.py]
        validate_persona(): REQUIRED_FIELDS present, difficulty∈{easy,medium,hard}, ≥1 critical_error
        if no grounding: needs_review=True (write to _reports, do not import)
  → write archive/.../batch1_personas/<specialty>_<n>_<condition>_persona.json
  → import via import_patient_personas.py --source <dir>
```
- New: `scripts/generate_personas.py` (injectable `claude_client`, `rag_service`).
- **Claude only** — `claude_client` wraps the project's Claude API path (see `generate_mcqs_claude.py`); no ollama/local-LLM references (Test 6).
- Reuse importer, RAG, persona schema, QA-report shape.

---

## L - LOOP

### Loop Execution Strategy
**CRITICAL**: 3-phase sequential, TDD-enforced (**RED → GREEN → REFACTOR** each). Phase 2 depends on Phase 1 (generator); Phase 3 on Phase 2 (generated files).

**Phase Dependency Chain**:
```
Phase 1 (generator, unit-tested) → Phase 2 (grounded generation + clinical review) → Phase 3 (import + mock-exam balance verified) → COMPLETE
```
**Blocking conditions**: any unit test failing · a generated persona lacking grounding gets imported · any local-LLM reference · clinical reviewer rejects a batch.

**Recovery Protocol**: if a phase is blocked, fix it in the CURRENT phase before advancing; never import an ungrounded persona; revert refactors that break green; document resolution in H.

### Phase 1: PersonaGenerator + validator (Tests 1–6)
**TDD Workflow (MANDATORY)**: RED (write Tests 1–6 with mocked Claude/RAG) → GREEN (`PersonaGenerator` + `validate_persona`) → REFACTOR. GREEN before any real generation.
**Blocker**: any of Tests 1–6 failing, or a local-LLM reference detected → phase BLOCKED (no real generation until green).

### Phase 2: grounded generation + clinical review
**TDD Workflow (MANDATORY)**: unit tests stay green. Small batch first (`--limit`), route the first 3 per specialty through the matching expert agent for clinical validity, then full batch; write `*_persona.json` + QA reports.

### Phase 3: import + mock-exam balance verified
**TDD Workflow (MANDATORY)**: import via `import_patient_personas.py --source <dir>`; verify persona counts per specialty rise; re-run the mock-exam balanced-distribution test against real data.

---

## P - PLAN

- Reuse the exact `*_persona.json` field set (0.2); `amc_blueprint_area` from specialty.
- Ground every clinical claim; personas with no ≥0.65 point-id hit go to `_reports/personas_needs_review.json`, NOT imported.
- Clinical validity: first N per specialty through the matching expert agent (e.g. `mental-health-crisis-expert` for psychiatry).
- Idempotent: skip existing `persona_code`.
- Australian context mandatory (drugs, guidelines, 000); enforce ≥60% Australian citations per persona.

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

### Generation results
- Personas generated / imported per specialty: `[FILL]`
- Personas sent to needs_review (ungrounded): `[FILL]`
- Australian-source ratio (avg): `[FILL]`
- Persona specialty count before → after: `5 → [FILL]`

### Mock-exam balance re-check (real data)
```
[TO BE FILLED — tests/test_mock_exam balanced-distribution result against imported personas]
```

### Success Criteria
- [ ] 6/6 tests pass
- [ ] ≥8 personas each for the targeted missing specialties, all schema-valid
- [ ] Every imported persona has ≥1 qdrant_point_id citation; ungrounded ones NOT imported
- [ ] No local-LLM code path (Test 6 green)
- [ ] Mock-exam engine can assemble a paper spanning ≥8 specialties

### Deliverables Checklist
- [ ] `scripts/generate_personas.py` (`PersonaGenerator`, `validate_persona`, `REQUIRED_FIELDS`)
- [ ] `*_persona.json` files for the missing specialties
- [ ] `_reports/personas_needs_review.json` for ungrounded personas
- [ ] Imported personas (counts per specialty verified)
- [ ] Mock-exam balanced-distribution test re-run against real data

---

## Permissions (Ralph Autonomous Execution)

<!-- RALPH-PERMISSIONS:BEGIN -->
allow:
  - Bash(cd backend && pytest:*)
  - Bash(python scripts/generate_personas.py:*)
  - Bash(python backend/scripts/import_patient_personas.py:*)
add-dir:
  - /home/dev/Development/irStudy
<!-- RALPH-PERMISSIONS:END -->

---

### Quality Gates

**Tests:**
- [ ] `cd backend && pytest tests/test_scripts/test_generate_personas.py` → passing
- [ ] `cd backend && pytest tests/test_mock_exam/test_orchestration.py` → passing

**No local LLM (project rule):**
- [ ] `! grep -rEni "ollama|localhost:11434" scripts/generate_personas.py` → exit code 0

**Compile:**
- [ ] `cd backend && python -m py_compile ../scripts/generate_personas.py` → exit code 0

**Security (passes only when no secret is found):**
- [ ] `! grep -rEn "sk-ant-|ANTHROPIC_API_KEY\s*=\s*['\"]|DATABASE_PASSWORD\s*=\s*['\"]" scripts backend/src` → exit code 0

**Commit — final gate:**
- [ ] `git log -1 --pretty=%s | grep -q 'PRD-PERSONA-BREADTH-001'` → exit code 0

### Commit as the final gate (MANDATORY)
After all gates pass: `git add -A && git commit -m "feat(content): PRD-PERSONA-BREADTH-001 — RAG-grounded personas for missing AMC specialties"`. Never commit `.env`, API keys, or `_reports/`.
