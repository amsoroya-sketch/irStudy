# PRD-CONDITIONS-SPINE-001: AMC Conditions/Blueprint Spine (content coverage backbone)

**PRD ID**: PRD-CONDITIONS-SPINE-001
**Project**: irStudy Platform (EMR + AI OSCE)
**Project Location**: /home/dev/Development/irStudy
**Working Directory**: /home/dev/Development/irStudy
**Technology Stack**: FastAPI (Python 3.12) + SQLAlchemy + PostgreSQL (Alembic)
**Status**: Ready for Implementation
**Created**: 2026-09-01
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
./scripts/ralph_loop.sh --calls 45 --prompt /home/dev/Development/irStudy/PRD-CONDITIONS-SPINE-001.md
```
**Runtime prerequisite**: `$DATABASE_PASSWORD` set (from `backend/.env`).

---

## 0 - DISCOVERY (verified at planning time)

### 0.1 Search evidence
- `grep -niE "class (Condition|Blueprint)" backend/src/db/models.py` → **none** (no conditions/blueprint table exists).
- `grep -nA20 "class MedicalSpecialty" backend/src/db/models.py` → 14-value controlled enum (cardiology…musculoskeletal, models.py:125-138).
- Content tables carry `specialty` but no cross-content link: MCQ (`models.py:308` enum), OSCE (enum), PatientPersona (`:719` free-text), MockPatient (free-text). MCQ↔OSCE have no FK; nothing links to a condition.

### 0.2 Discovery Results (REUSE)
| Thing | Location | Use |
|---|---|---|
| Controlled specialty vocabulary | `MedicalSpecialty` enum, `models.py:125-138` | Condition.specialty column type |
| Content topic data to seed conditions | `data/mcqs/*.json` (`topic`/`subtopic`), `data/osces/*.json` (`title`), persona `expected_diagnosis` | Deterministic, data-grounded seed |
| Migration pattern | `backend/alembic/versions/*` (additive + reversible) | New table + nullable FKs |
| Reconciliation report to extend | `scripts/content_reconciliation.py` | Add per-blueprint coverage |

### 0.3 Gap Analysis (BUILD-NEW)
No spine linking content to AMC conditions/blueprint areas → coverage is only coarse specialty, and MCQ/OSCE/persona/EMR are siloed. Add a `conditions` table, nullable `condition_id` FKs on the four content tables, a data-grounded seed + backfill, and a coverage query.

### 0.4 Source-data caveat (verified)
`data/processed/AMC Anthology of Medical Conditions.json` and `AMC Handbook of Clinical Assessment.json` are **page-extracted documents, not per-condition records**. The conditions list is seeded deterministically from existing content topics (0.2), NOT parsed from these books. No LLM generation in this PRD (avoids hallucinated conditions).

### 0.5 Reference Implementations
None required — all structure comes from verified in-repo code (0.2).

---

## T - TESTS

### Test Inventory
- Total Tests: 7 (backend pytest, under `backend/tests/`)
- Phase 1 (model/table): Tests 1, 3
- Phase 2 (FKs): Test 2
- Phase 3 (seed/backfill): Tests 4, 5, 6
- Phase 4 (coverage): Test 7

### TDD Workflow (MANDATORY)
Every phase follows **RED → GREEN → REFACTOR**:
1. **RED Phase**: write the phase's tests; confirm they FAIL (table/column/function absent).
2. **GREEN Phase**: implement minimal code until they PASS.
3. **REFACTOR Phase**: improve; re-run; stay green.
**Agent Constraint**: no implementation before tests exist and are confirmed failing.

#### Test 1: conditions table exists with required columns
```python
# FILE: backend/tests/test_db/test_condition_model.py
from src.db.models import Condition, MCQ, OSCE, PatientPersona, MockPatient

def test_condition_table_exists():
    assert Condition.__tablename__ == "conditions"
    cols = Condition.__table__.columns
    for c in ("id", "condition_code", "name", "specialty", "amc_blueprint_area"):
        assert c in cols
```

#### Test 2: content tables carry a nullable condition_id FK
```python
def test_content_tables_have_condition_fk():
    for model in (MCQ, OSCE, PatientPersona, MockPatient):
        assert "condition_id" in model.__table__.columns
        assert model.__table__.columns["condition_id"].nullable is True
```

#### Test 3: a condition persists and links an MCQ
```python
def test_condition_persists_and_links_mcq(db_session):
    c = Condition(condition_code="RESP-ASTHMA", name="Asthma",
                  specialty="respiratory", amc_blueprint_area="Respiratory Medicine")
    db_session.add(c); db_session.commit(); db_session.refresh(c)
    m = MCQ(question_id="MCQ-C-1", question_text="q", options={"A": "a", "B": "b"},
            correct_answer="A", explanation="e", citation="x",
            specialty="respiratory", difficulty="medium", condition_id=c.id)
    db_session.add(m); db_session.commit(); db_session.refresh(m)
    assert m.condition_id == c.id
```

#### Test 4: derive_conditions dedups and normalizes from content
```python
# FILE: backend/tests/test_scripts/test_seed_conditions.py
from scripts.seed_conditions import derive_conditions

def test_derive_conditions_from_content():
    mcqs = [{"specialty": "respiratory", "topic": "Asthma"},
            {"specialty": "respiratory", "topic": "asthma"},   # dupe (case)
            {"specialty": "cardiology", "topic": "STEMI"}]
    conds = derive_conditions(mcqs=mcqs, osces=[], personas=[])
    names = {(c["specialty"], c["name"].lower()) for c in conds}
    assert ("respiratory", "asthma") in names and ("cardiology", "stemi") in names
    assert len(conds) == 2
```

#### Test 5: every derived condition maps to a valid specialty
```python
def test_every_condition_maps_to_valid_specialty():
    from src.db.models import MedicalSpecialty
    valid = {e.value for e in MedicalSpecialty}
    conds = derive_conditions(mcqs=[{"specialty": "cardiology", "topic": "AF"}], osces=[], personas=[])
    assert all(c["specialty"] in valid for c in conds)
```

#### Test 6: backfill matches by specialty + topic, guarded by specialty
```python
# FILE: backend/tests/test_scripts/test_backfill_and_coverage.py
from scripts.backfill_condition_links import match_condition

def test_match_condition_by_specialty_and_topic():
    conds = [{"id": 1, "specialty": "respiratory", "name": "Asthma"}]
    assert match_condition({"specialty": "respiratory", "topic": "Asthma exacerbation"}, conds) == 1
    assert match_condition({"specialty": "cardiology", "topic": "Asthma"}, conds) is None
```

#### Test 7: coverage report counts per blueprint area
```python
from scripts.content_reconciliation import coverage_by_blueprint

def test_coverage_report_counts_per_blueprint_area():
    rows = coverage_by_blueprint(
        conditions=[{"id": 1, "amc_blueprint_area": "Respiratory Medicine"}],
        content={"mcq": [{"condition_id": 1}], "osce": [], "persona": [], "emr_case": []})
    assert rows["Respiratory Medicine"]["mcq"] == 1
```

### Test Execution Commands
```bash
cd backend && pytest tests/test_db/test_condition_model.py \
  tests/test_scripts/test_seed_conditions.py \
  tests/test_scripts/test_backfill_and_coverage.py -v
```

---

## R - REQUEST

**User story**: As the content team, I need every MCQ, OSCE, persona, and EMR case anchored to an AMC condition/blueprint area, so I can see true coverage per blueprint area (not just coarse specialty) and target gaps quantitatively.

**Business context**: Gaps are currently invisible — content is a flat pool filtered by inconsistent specialty strings. A conditions spine turns it into a joinable graph and makes "what's missing per AMC blueprint area" answerable with a query. Prereq for data-driven content expansion (PRD-PERSONA-BREADTH-001).

---

## A - ARCHITECTURE

- **`Condition` model** (new table `conditions`): `id` PK, `condition_code` String unique, `name` String, `specialty` (`MedicalSpecialty` enum), `amc_blueprint_area` String, `aliases` JSON null, `system` String null. Mirror existing model style.
- **Nullable `condition_id` FK** on `mcqs`, `osces`, `patient_personas`, `mock_patients` (→ conditions.id, ON DELETE SET NULL). Additive, reversible migration.
- **`scripts/seed_conditions.py`**: `derive_conditions(mcqs, osces, personas)` — distinct `(specialty, normalized topic/title/diagnosis)` pairs, normalize case/whitespace, map specialty via `MedicalSpecialty` (skip unmappable → logged report), assign `amc_blueprint_area` from a specialty→blueprint dict. Writes `data/amc_blueprints/conditions.json` + inserts. Deterministic, no LLM.
- **`scripts/backfill_condition_links.py`**: `match_condition(item, conditions)` — link each row by exact/normalized topic match guarded by specialty; unmatched left null and listed in `data/amc_blueprints/_reports/unlinked.json`.
- **`scripts/content_reconciliation.py`** extended: `coverage_by_blueprint(...)` → items per blueprint area per content type; surfaced in `--json`.

**Reuse-first**: no new grounding/LLM; the seed is pure data transformation over existing files.

---

## L - LOOP

### Loop Execution Strategy
**CRITICAL**: 4-phase sequential, TDD-enforced (**RED → GREEN → REFACTOR** each). Phase 2 depends on Phase 1; Phase 3 on Phase 2; Phase 4 on Phase 3.

**Phase Dependency Chain**:
```
Phase 1 (conditions table) → Phase 2 (condition_id FKs) → Phase 3 (seed + backfill) → Phase 4 (coverage report) → COMPLETE (7/7)
```
**Blocking conditions**: any test failing · migration not reversible · unmapped-specialty rate not reported · hardcoded secret.

**Recovery Protocol**: if a phase is blocked, fix it in the CURRENT phase before advancing; never proceed with a failing test or an unreversible migration; revert refactors that break green; document resolution in H.

### Phase 1: Condition model + table (Tests 1, 3)
**TDD Workflow (MANDATORY)**: RED (write Tests 1,3) → GREEN (`Condition` model + migration) → REFACTOR.
**Blocker**: Tests 1/3 failing, or `alembic upgrade head && alembic downgrade -1` not clean → phase BLOCKED.

### Phase 2: condition_id FKs on content tables (Test 2)
**TDD Workflow (MANDATORY)**: RED (Test 2) → GREEN (nullable FKs on the 4 tables + migration) → REFACTOR.

### Phase 3: seed + backfill (Tests 4, 5, 6)
**TDD Workflow (MANDATORY)**: RED (Tests 4–6) → GREEN (`seed_conditions.py` + `backfill_condition_links.py`; run against DB; emit `unlinked.json`) → REFACTOR.

### Phase 4: coverage report (Test 7)
**TDD Workflow (MANDATORY)**: RED (Test 7) → GREEN (`coverage_by_blueprint` in reconciliation; emit per-blueprint coverage) → REFACTOR.

---

## P - PLAN

- Migrations (table, then FKs) must `downgrade` cleanly.
- `amc_blueprint_area` map: 14 specialties → AMC domains (internal-medicine specialties → their sub-areas; obstetrics_gynaecology → Women's Health; paediatrics → Child Health; psychiatry → Mental Health; surgery/urology/ophthalmology/musculoskeletal → Surgery & Procedures; general_practice / emergency_medicine as their own). One documented dict.
- Idempotent seed/backfill (`condition_code` unique dedups).
- Never fabricate conditions — only derive from existing content topics.

---

## H - HANDOFF

### Test Results Summary
```
[TO BE FILLED BY RALPH — pytest 7/7 passing]
```

### TDD Compliance Verification
- [ ] All 7 tests written BEFORE implementation (RED confirmed failing)
- [ ] All 7 passing after implementation (GREEN); still passing after refactor
- [ ] 0 tests skipped

### Seed & backfill results
- Conditions seeded (by specialty): `[FILL]`
- Content rows linked / unlinked: mcq `[FILL]`, osce `[FILL]`, persona `[FILL]`, emr_case `[FILL]`
- Unmapped-specialty rows (logged): `[FILL]`

### Coverage-by-blueprint (top gaps)
```
[TO BE FILLED — blueprint areas with 0 or few items across content types]
```

### Migration evidence
```
[TO BE FILLED — alembic upgrade head && downgrade -N && upgrade head]
```

### Success Criteria
- [ ] 7/7 tests pass
- [ ] `conditions` seeded from real content; every condition maps to a valid `MedicalSpecialty`
- [ ] `condition_id` FKs present & nullable on the 4 tables; migration reversible
- [ ] Coverage-by-blueprint report emitted; unlinked content listed, not force-matched

### Deliverables Checklist
- [ ] `Condition` model + `conditions` table (migration)
- [ ] Nullable `condition_id` FK on mcqs/osces/patient_personas/mock_patients (migration)
- [ ] `scripts/seed_conditions.py` + `data/amc_blueprints/conditions.json`
- [ ] `scripts/backfill_condition_links.py` + `_reports/unlinked.json`
- [ ] `coverage_by_blueprint` in `scripts/content_reconciliation.py`

---

## Permissions (Ralph Autonomous Execution)

<!-- RALPH-PERMISSIONS:BEGIN -->
allow:
  - Bash(cd backend && pytest:*)
  - Bash(cd backend && alembic upgrade:*)
  - Bash(cd backend && alembic downgrade:*)
  - Bash(python scripts/seed_conditions.py:*)
  - Bash(python scripts/backfill_condition_links.py:*)
  - Bash(python scripts/content_reconciliation.py:*)
add-dir:
  - /home/dev/Development/irStudy
<!-- RALPH-PERMISSIONS:END -->

---

### Quality Gates

**Tests:**
- [ ] `cd backend && pytest tests/test_db/test_condition_model.py tests/test_scripts/test_seed_conditions.py tests/test_scripts/test_backfill_and_coverage.py` → passing

**Migration reversibility:**
- [ ] `cd backend && alembic upgrade head && alembic downgrade -2 && alembic upgrade head` → exit code 0

**Compile:**
- [ ] `cd backend && python -m py_compile ../scripts/seed_conditions.py ../scripts/backfill_condition_links.py` → exit code 0

**Security (passes only when no secret is found):**
- [ ] `! grep -rEn "sk-ant-|DATABASE_PASSWORD\s*=\s*['\"]" backend/src scripts` → exit code 0

**Commit — final gate:**
- [ ] `git log -1 --pretty=%s | grep -q 'PRD-CONDITIONS-SPINE-001'` → exit code 0

### Commit as the final gate (MANDATORY)
After all gates pass: `git add -A && git commit -m "feat(content): PRD-CONDITIONS-SPINE-001 — AMC conditions/blueprint spine + coverage"`. Never commit `.env` or generated `_reports/`.
