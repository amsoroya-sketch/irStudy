# PRD-EMR-PRACTICE-002: Challenging Case Content Pipeline (validate + import)

**PRD ID**: PRD-EMR-PRACTICE-002
**Project**: irStudy Medical Education Platform (EMR + AI OSCE)
**Project Location**: /home/dev/Development/irStudy
**Working Directory**: /home/dev/Development/irStudy
**Technology Stack**: Python 3.12 + SQLAlchemy + PostgreSQL
**Repository**: git@github.com-sketch:amsoroya-sketch/irStudy.git
**Status**: Ready for Implementation
**Created**: 2026-08-26
**Standards**: T-RALPH V2.6
**Prescription**: low
**Estimated Effort**: 3-4 hours
**Depends on**: PRD-EMR-PRACTICE-001 (needs `MockPatient.validation_criteria` mapped)

---

## Project Context (CRITICAL for Ralph Execution)

**IMPORTANT**: This PRD is for the **irStudy** project.

**Project Constraints File**: `/home/dev/Development/irStudy/PROJECT_CONSTRAINTS.md`
**Project CLAUDE.md File**: `/home/dev/Development/irStudy/.claude/CLAUDE.md`

**Technology Stack**:
- **Backend**: Python 3.12, SQLAlchemy 2.0
- **Database**: PostgreSQL (`irstudy_medical` @ localhost:5433)
- **Testing**: pytest

**Ralph Execution Command**:
```bash
cd /home/dev/Development/ralph-dashboard
./scripts/ralph_loop.sh --calls 30 --prompt /home/dev/Development/irStudy/planning/emr-challenging-scenarios/prds/PRD-EMR-PRACTICE-002.md
```

---

## 0 - DISCOVERY

**Ponytail Principle**: An idempotent mock-patient importer already exists — reuse its structure;
this PRD adds a **content gate** and an **answer-key-aware importer**, not a new framework.

### 0.1 Existing Code Search (evidence — verified 2026-08-26)

```bash
grep -n "def map_persona_to_mock_patient\|difficulty_map\|def main" backend/scripts/import_mock_patients.py
# → 46 map_persona_to_mock_patient ; 62 difficulty_map ; 161 main  (idempotent importer to reuse)

# The answer-key data this PRD imports (authored separately, Deliverable B of the plan)
ls data/emr_practice_cases/*.json   # 24 authored cases (mock_patient + validation_criteria)

# Enum values the gate must validate against
grep -n "class MedicalSpecialty\|class DifficultyLevel" backend/src/db/models.py
```

### 0.2 Discovery Results (reuse targets)

| Component | Location | Reuse decision |
|---|---|---|
| Idempotent persona importer | `backend/scripts/import_mock_patients.py:46,161` | ADAPT into `import_emr_practice_cases.py` |
| `MockPatient` ORM (+ `validation_criteria`) | `backend/src/db/models.py:1385` (mapped by PRD-001) | TARGET table |
| Enums | `backend/src/db/models.py` `MedicalSpecialty`, `DifficultyLevel` | VALIDATE against |
| Authored case files | `data/emr_practice_cases/*.json` | INPUT (24 cases) |

### 0.3 Gap Analysis
- No content gate exists for the answer-key contract.
- The existing importer maps personas, not EMR practice cases with `validation_criteria`.

### 0.5 Reference Implementations
None external.

---

## T - TESTS (Write These FIRST)

### Test Inventory
- Total: 8 tests · file: `backend/tests/test_emr/test_practice_case_pipeline.py`

### TDD Workflow (MANDATORY)
1. **RED**: write all 8 tests → confirm they FAIL (gate + importer absent).
2. **GREEN**: implement minimal code → confirm PASS.
3. **REFACTOR**: clean up → tests still PASS.
Workflow is **RED → GREEN → REFACTOR**. Write NO implementation before the 8 tests exist and fail.

### Answer-key contract (input `data/emr_practice_cases/*.json`)
```jsonc
{
  "mrn": "EMRP-0001", "name": "str", "age": 58, "gender": "str",
  "specialty": "cardiology", "difficulty": "hard",
  "presenting_complaint": "str", "vital_signs": {...}, "medical_history": {...},
  "validation_criteria": {
    "presenting_scenario": "str", "task": "str",
    "expected": {"subjective": [...], "objective": [...], "assessment": [...], "plan": [...]},
    "critical_errors": ["str"], "must_not_miss": ["str"]
  }
}
```

### Tests (full code)

Full code in `backend/tests/test_emr/test_practice_case_pipeline.py` (shared fixture `VALID` at top).

#### Test 1: valid case passes the gate
#### Test 2: missing critical_errors → reject
#### Test 3: empty expected section → reject
#### Test 4: bad specialty enum → reject
#### Test 5: missing scenario/task → reject
#### Test 6: build_mock_patient maps validation_criteria onto the ORM object
#### Test 7: import is idempotent (re-run adds 0 by mrn)
#### Test 8: all 24 authored cases pass the gate

```python
# FILE: backend/tests/test_emr/test_practice_case_pipeline.py
import json, copy
from pathlib import Path
import pytest

from scripts_emr.validate_practice_cases import validate_case, validate_dir  # thin import shim
from backend.scripts.import_emr_practice_cases import build_mock_patient, import_cases

VALID = {
    "mrn": "EMRP-0001", "name": "Test Case", "age": 58, "gender": "male",
    "specialty": "cardiology", "difficulty": "hard",
    "presenting_complaint": "central chest pain",
    "vital_signs": {"bp": "150/90", "hr": 92, "spo2": 97},
    "medical_history": {"conditions": ["hypertension"]},
    "validation_criteria": {
        "presenting_scenario": "58yo male, central crushing chest pain 40 min.",
        "task": "Document assessment and initial management.",
        "expected": {"subjective": ["SOCRATES"], "objective": ["ECG <10min"],
                     "assessment": ["STEMI"], "plan": ["aspirin 300mg"]},
        "critical_errors": ["nitrates in RV infarct"],
        "must_not_miss": ["aortic dissection considered"],
    },
}

# Test 1: valid case passes the gate
def test_valid_case_passes():
    ok, errors = validate_case(VALID)
    assert ok and errors == []

# Test 2: missing critical_errors -> reject
def test_no_critical_error_rejected():
    c = copy.deepcopy(VALID); c["validation_criteria"]["critical_errors"] = []
    ok, errors = validate_case(c)
    assert not ok and any("critical_error" in e for e in errors)

# Test 3: empty expected section -> reject
def test_empty_expected_section_rejected():
    c = copy.deepcopy(VALID); c["validation_criteria"]["expected"]["plan"] = []
    ok, errors = validate_case(c)
    assert not ok and any("expected.plan" in e for e in errors)

# Test 4: bad specialty enum -> reject
def test_bad_specialty_rejected():
    c = copy.deepcopy(VALID); c["specialty"] = "wizardry"
    ok, errors = validate_case(c)
    assert not ok and any("specialty" in e for e in errors)

# Test 5: missing scenario/task -> reject
def test_missing_scenario_task_rejected():
    c = copy.deepcopy(VALID); c["validation_criteria"]["task"] = ""
    ok, errors = validate_case(c)
    assert not ok

# Test 6: build_mock_patient maps validation_criteria onto the ORM object
def test_build_mock_patient_sets_criteria():
    mp = build_mock_patient(VALID)
    assert mp.validation_criteria["critical_errors"] == ["nitrates in RV infarct"]
    assert mp.specialty == "cardiology" and mp.difficulty == "hard"

# Test 7: import is idempotent (re-run adds 0 by mrn)
def test_import_idempotent(db_session, tmp_path):
    f = tmp_path / "EMRP-0001.json"; f.write_text(json.dumps(VALID))
    n1 = import_cases(str(tmp_path), db_session)
    n2 = import_cases(str(tmp_path), db_session)
    assert n1 == 1 and n2 == 0
    from src.db.models import MockPatient
    rows = db_session.query(MockPatient).filter_by(mrn="EMRP-0001").all()
    assert len(rows) == 1 and rows[0].validation_criteria is not None

# Test 8: all 24 authored cases pass the gate (fixture dir)
def test_authored_cases_all_valid():
    d = Path("data/emr_practice_cases")
    if not d.exists():
        pytest.skip("authored cases not present in this environment")
    ok, report = validate_dir(str(d))
    assert ok, f"invalid cases: {report}"
    assert len(list(d.glob('*.json'))) >= 24
```

### Test Execution
```bash
cd backend && python -m pytest tests/test_emr/test_practice_case_pipeline.py -q
python scripts/validate_emr_practice_cases.py data/emr_practice_cases/
```

---

## R - REQUEST
As the PM, I need the 24 authored challenging cases (with answer-keys) **gated for quality** and
**idempotently imported** into `mock_patients`, so students can select and practise them and the
PRD-001 engine can score against each case's `validation_criteria`.

---

## A - ARCHITECTURE
- `scripts/validate_emr_practice_cases.py` — `validate_case(case) -> (ok, errors)` and
  `validate_dir(path) -> (ok, report)`. Checks: contract keys present; `critical_errors` ≥1;
  each `expected.{subjective,objective,assessment,plan}` non-empty; `specialty`/`difficulty` ∈ enums;
  `presenting_scenario`+`task` non-empty; unique `mrn`.
- `backend/scripts/import_emr_practice_cases.py` — `build_mock_patient(case) -> MockPatient` (reuse
  the mapping style of `import_mock_patients.py:46`, adding the new answer-key/clinical fields) and
  `import_cases(dir, db) -> inserted_count` (skip existing by `mrn`; validate before insert).
- Test shim `scripts_emr/validate_practice_cases.py` re-exports for import convenience (or adjust
  imports to the real script path — keep one canonical implementation).

---

## L - LOOP

### Loop Execution Strategy
**CRITICAL**: 2-phase sequential TDD (RED → GREEN → REFACTOR each phase). Phase 1 (gate) → Phase 2
(importer). No advance on failing tests.

**Recovery Protocol**: if a phase is blocked, fix it in the CURRENT phase; never advance with
blockers; record the blocker + resolution in the H section.

**Dependency chain**:
```
Phase 1 (validate_emr_practice_cases.py — gate)
    ↓ provides: validate_case/validate_dir
Phase 2 (import_emr_practice_cases.py — idempotent importer)
    ↓ provides: mock_patients populated with answer-keys
COMPLETE (8/8 tests passing; 24/24 authored cases valid)
```

### Phase 1: Content gate (prescription low)
- GOAL: reject any case violating the answer-key contract; accept the 24 authored cases.
- CONSTRAINTS: enums from `models.py`; pure function, no DB.
- RUBRIC: Tests 1-5, 8 pass.

### Phase 2: Importer (prescription low)
- GOAL: idempotent import by `mrn`, mapping `validation_criteria` + clinical fields.
- CONSTRAINTS: reuse `import_mock_patients.py` structure; validate before insert; lowercase specialty/difficulty.
- RUBRIC: Tests 6-7 pass; running against `data/emr_practice_cases/` inserts 24 then 0 on re-run.

---

## P - PLAN
1. `backend/tests/test_emr/test_practice_case_pipeline.py` (RED).
2. `scripts/validate_emr_practice_cases.py`.
3. `backend/scripts/import_emr_practice_cases.py`.

---

## H - HANDOFF

### Agent constraints
**CRITICAL — read FIRST**: `/home/dev/Development/irStudy/PROJECT_CONSTRAINTS.md` (Section 0 discovery,
testing). Then this PRD's T section. Then `backend/scripts/import_mock_patients.py`.
Agent: **python-backend-developer**.

### Test Results Summary
```
[TO BE FILLED BY RALPH AFTER EXECUTION]
cd backend && python -m pytest tests/test_emr/test_practice_case_pipeline.py -q
python scripts/validate_emr_practice_cases.py data/emr_practice_cases/
```

### TDD Compliance Verification
- [ ] 8 tests written first, confirmed FAILING — [TO BE FILLED BY RALPH]
- [ ] 8/8 passing — [TO BE FILLED BY RALPH]

### Success Criteria
- [ ] Gate rejects cases with no critical_error / empty expected section / bad enum.
- [ ] Import idempotent (re-run inserts 0).
- [ ] 24 authored cases import; each row has `validation_criteria` populated.

### Deliverables Checklist
- [ ] `backend/tests/test_emr/test_practice_case_pipeline.py` (8 tests)
- [ ] `scripts/validate_emr_practice_cases.py` (content gate)
- [ ] `backend/scripts/import_emr_practice_cases.py` (idempotent importer)

### Quality Gates

**Content & pipeline:**
- [ ] `cd backend && python -m pytest tests/test_emr/test_practice_case_pipeline.py -q` → passing
- [ ] `python scripts/validate_emr_practice_cases.py data/emr_practice_cases/` → exit code 0

**Security (passes only when no secret is found):**
- [ ] `! grep -rEn "sk-ant-|api_key\s*=\s*['\"]" scripts backend/scripts/import_emr_practice_cases.py` → exit code 0

**Commit — final gate:**
- [ ] `git log -1 --pretty=%s | grep -q 'PRD-EMR-PRACTICE-002'` → exit code 0

### Commit as the final gate
After every Quality Gate passes:
`git add -A && git commit -m "feat(emr): PRD-EMR-PRACTICE-002 — challenging case content pipeline"`.
Never commit `.env`, generated reports, or scratch files.

---

## Permissions (Ralph Autonomous Execution)

<!-- RALPH-PERMISSIONS:BEGIN -->
allow:
  - Bash(python scripts/validate_emr_practice_cases.py:*)
  - Bash(python -m pytest backend/tests/*:*)
  - Bash(cd backend && python -m pytest*:*)
  - Bash(python backend/scripts/import_emr_practice_cases.py:*)
add-dir:
  - /home/dev/Development/irStudy
<!-- RALPH-PERMISSIONS:END -->
