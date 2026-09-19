# PRD-MCQ-CITATION-001: MCQ Citation Remediation (RAG-Grounded, qdrant_point_id)

**PRD ID**: PRD-MCQ-CITATION-001
**Project**: irStudy Platform (EMR + AI OSCE)
**Project Location**: /home/dev/Development/irStudy
**Working Directory**: /home/dev/Development/irStudy
**Technology Stack**: FastAPI (Python 3.12) + SQLAlchemy + PostgreSQL + Qdrant (RAG)
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
./scripts/ralph_loop.sh --calls 40 --prompt /home/dev/Development/irStudy/PRD-MCQ-CITATION-001.md
```

**Runtime prerequisite**: Qdrant reachable at `$QDRANT_URL` (default `http://localhost:6333`) with the `medical_knowledge` collection populated, and `$DATABASE_PASSWORD` set (from `backend/.env`).

---

## 0 - DISCOVERY (verified against the repo at planning time)

### 0.1 Search evidence
- `grep -rn "search_similar\|qdrant_point_id\|confidence_threshold" backend/src/ai/`
- `grep -n "citation" backend/src/db/models.py backend/scripts/import_mcqs.py`
- Offline scan of `data/mcqs/*.json` (18 non-backup files): **1,934 MCQ items, 4,947 references, 0 with `qdrant_point_id`, 2,154 (43%) author "Unknown/blank"**; Australian-source hits: Murtagh 1,723 / eTG 242 / Talley 111.

### 0.2 Discovery Results (REUSE — verified file:line)
| Capability | Location | Reuse verdict |
|---|---|---|
| Ground text → `{source, qdrant_point_id, score, title, author, year, page}` | `backend/src/ai/rag_service.py:146-227` `RAGService.search_similar(query_text, limit=5, confidence_threshold=0.65)` | REUSE verbatim |
| ≥0.65 filter + drop-missing-point-id + Australian-ratio warn | `backend/src/ai/study_card_generator.py:574-636` `_enrich_with_citations` | MIRROR |
| Fail-fast per-citation metadata validation | `backend/src/agents/qa/incremental_citation_validator.py` | REUSE |
| Pre-flight RAG quality gate | `scripts/test_rag_citation_quality.py` | REUSE (Phase 0 gate) |
| Structured multi-citation JSON persistence (shape to copy) | `backend/src/db/models.py:1243` `StudyCard.citations = Column(JSON, nullable=False)` | MIRROR onto MCQ |
| MCQ importer entrypoints | `backend/scripts/import_mcqs.py:215` `transform_mcq`, `:165` `_coerce_citation` | EXTEND |

### 0.3 Gap Analysis (BUILD-NEW — the real work)
1. **MCQ cannot store structured citations.** `models.py:303` `MCQ.citation = Column(String(500))`. → Add `MCQ.citations = Column(JSON, nullable=True)` via Alembic; keep `citation` as a derived summary.
2. **Importer discards point-ids.** `import_mcqs.py:165-189` collapses `references[]` into one `[:500]` string. → Preserve the structured array into `citations`.
3. **No MCQ remediation engine.** → New `backend/src/ai/mcq_citation_remediator.py` reusing `search_similar` and mirroring `_enrich_with_citations`.

### 0.4 Risks to resolve in Phase 0 (verified, blocking)
- **Embedding-model mismatch**: `rag_service.py` embeds with `microsoft/BiomedNLP-PubMedBERT`, but `scripts/generate_mcqs_from_rag.py` uses `pritamdeka/S-PubMedBert-MS-MARCO`. Confirm which model indexed `medical_knowledge` before trusting `search_similar` scores.
- **Stale test**: `backend/tests/test_ai/test_rag_service.py:42,223,229` assert `collection_name == "medical_guidelines"` vs source default `medical_knowledge` (`rag_service.py:31`). Fix in Phase 0.
- **Sentinel point-id policy**: treat `qdrant_point_id="00000000-0000-0000-0000-000000000000"` (`study_card_generator.py:624-636`) as NOT grounded → flag for regeneration, never a real citation.

### 0.5 Reference Implementations
None required — all structure comes from verified in-repo code above (0.2).

---

## T - TESTS

### Test Inventory
- Total Tests: 9 (backend pytest, under `backend/tests/`)
- Phase 1 (schema & importer): Tests 1–3
- Phase 2 (remediation engine): Tests 4–8
- Phase 3 (corpus validator): Test 9
- All tests mock `RAGService.search_similar` (never hit live Qdrant) — mirror `backend/tests/test_ai/test_study_card_generator.py:427-579`.

### TDD Workflow (MANDATORY)
Every phase follows **RED → GREEN → REFACTOR**:
1. **RED Phase**: write all 9 tests below; run them; confirm they FAIL (modules/columns don't exist yet).
2. **GREEN Phase**: implement minimal code until all 9 PASS.
3. **REFACTOR Phase**: improve code; re-run; confirm 9/9 STILL PASS.
**Agent Constraint**: DO NOT write implementation code before the tests exist and are confirmed failing.

#### Test 1: MCQ maps a structured `citations` JSON column
```python
# FILE: backend/tests/test_db/test_mcq_citations_column.py
from src.db.models import MCQ

def test_mcq_has_structured_citations_column():
    assert hasattr(MCQ, "citations")
    col = MCQ.__table__.columns["citations"]
    assert col.type.__class__.__name__ == "JSON"
```

#### Test 2: a citation list round-trips through the DB
```python
def test_mcq_persists_citation_list(db_session):
    cites = [{"source": "eTG", "qdrant_point_id": "550e8400-e29b-41d4-a716-446655440000",
              "confidence": 0.81, "is_australian": True, "title": "Therapeutic Guidelines",
              "author": "eTG", "year": "2024", "page": "p.12"}]
    m = MCQ(question_id="MCQ-T-001", question_text="q", options={"A": "a", "B": "b"},
            correct_answer="A", explanation="e", citation="eTG (2024)", citations=cites,
            specialty="respiratory", difficulty="medium")
    db_session.add(m); db_session.commit(); db_session.refresh(m)
    assert m.citations[0]["qdrant_point_id"] == "550e8400-e29b-41d4-a716-446655440000"
```

#### Test 3: importer preserves structured citations (not just a flat String)
```python
# FILE: backend/tests/test_scripts/test_import_preserves_citations.py
from scripts.import_mcqs import transform_mcq

def test_import_preserves_structured_citations():
    raw = {"id": "MCQ-T-002", "specialty": "respiratory", "correct_answer": "A",
           "question": {"stem": "q", "options": {"A": "a", "B": "b"}}, "explanation": "e",
           "references": [{"title": "eTG", "year": "2024", "page": "p.1",
                           "qdrant_point_id": "550e8400-e29b-41d4-a716-446655440000"}]}
    rec = transform_mcq(raw)
    assert isinstance(rec["citations"], list)
    assert rec["citations"][0]["qdrant_point_id"] == "550e8400-e29b-41d4-a716-446655440000"
    assert isinstance(rec["citation"], str) and len(rec["citation"]) <= 500
```

#### Test 4: engine grounds an MCQ with point-ids
```python
# FILE: backend/tests/test_ai/test_mcq_citation_remediator.py
from unittest.mock import MagicMock
from src.ai.mcq_citation_remediator import MCQCitationRemediator

def _hit(pid, score, author="eTG", title="Therapeutic Guidelines", au=True):
    return {"source": title, "qdrant_point_id": pid, "score": score, "content": "…",
            "page": "p.1", "title": title, "author": author, "year": "2024", "is_australian": au}

def _remediator(hits):
    rag = MagicMock(); rag.search_similar.return_value = hits
    return MCQCitationRemediator(rag_service=rag)

def test_grounds_mcq_with_point_ids():
    r = _remediator([_hit("550e8400-e29b-41d4-a716-446655440000", 0.82)])
    out = r.remediate({"question": {"stem": "q"}, "explanation": "e", "correct_answer": "A"})
    assert out["citations"] and all(c["qdrant_point_id"] for c in out["citations"])
    assert out["citations"][0]["confidence"] >= 0.65
```

#### Test 5: drops results without a point-id (mirror _enrich_with_citations:586)
```python
def test_drops_results_without_point_id():
    bad = _hit("", 0.9); bad["qdrant_point_id"] = ""
    r = _remediator([bad])
    out = r.remediate({"question": {"stem": "q"}, "explanation": "e", "correct_answer": "A"})
    assert out["citations"] == [] and out["needs_regeneration"] is True
```

#### Test 6: drops results below the 0.65 confidence threshold
```python
def test_drops_below_confidence_threshold():
    r = _remediator([_hit("550e8400-e29b-41d4-a716-446655440000", 0.40)])
    out = r.remediate({"question": {"stem": "q"}, "explanation": "e", "correct_answer": "A"})
    assert out["citations"] == [] and out["needs_regeneration"] is True
```

#### Test 7: no "Unknown Author" survives into output
```python
def test_no_unknown_author_in_output():
    r = _remediator([_hit("550e8400-e29b-41d4-a716-446655440000", 0.8, author="Unknown Author")])
    out = r.remediate({"question": {"stem": "q"}, "explanation": "e", "correct_answer": "A"})
    assert all((c.get("author") or "").lower() not in ("unknown author", "unknown", "")
               for c in out["citations"])
```

#### Test 8: flags low Australian-source ratio (mirror :613-622)
```python
def test_flags_low_australian_ratio():
    r = _remediator([_hit("id1", 0.8, title="StatPearls", au=False)])
    out = r.remediate({"question": {"stem": "q"}, "explanation": "e", "correct_answer": "A"})
    assert out["australian_ratio"] < 0.60
```

#### Test 9: corpus validator flags missing point-ids and Unknown Author
```python
# FILE: backend/tests/test_scripts/test_mcq_citation_report.py
from scripts.remediate_mcq_citations import validate_corpus

def test_report_flags_zero_pointid_and_unknown_author():
    sample = [{"id": "M1", "citations": [{"qdrant_point_id": "", "author": "Unknown Author"}]},
              {"id": "M2", "citations": [{"qdrant_point_id": "550e8400-e29b-41d4-a716-446655440000",
                                          "author": "eTG"}]}]
    rep = validate_corpus(sample)
    assert rep["missing_point_id"] == 1 and rep["unknown_author"] == 1
    assert "M1" in rep["needs_regeneration"] and "M2" not in rep["needs_regeneration"]
```

### Test Execution Commands
```bash
cd backend && pytest tests/test_db/test_mcq_citations_column.py \
  tests/test_scripts/test_import_preserves_citations.py \
  tests/test_ai/test_mcq_citation_remediator.py \
  tests/test_scripts/test_mcq_citation_report.py -v
```

---

## R - REQUEST

**User story**: As an AMC candidate, I trust that every MCQ explanation is grounded in a verifiable Australian source, so I can follow a citation to confirm the answer and study the primary reference.

**Business context**: The platform promises Australian-sourced, traceable content (every citation needs a `qdrant_point_id`; ≥60% Australian). Today **0 of 4,947 MCQ references carry a `qdrant_point_id`** and 43% have no author. Study cards already do this correctly; this PRD brings MCQs to parity.

**Out of scope**: OSCE/markdown prose citations; regenerating the 39 optionless/empty MCQs (tracked separately).

---

## A - ARCHITECTURE

**Flow (reuse-first):**
```
For each MCQ (question.stem + explanation as query_text)
  → RAGService.search_similar(query_text, limit=5, confidence_threshold=0.65)   [REUSE rag_service.py:146]
  → drop hits without qdrant_point_id; drop score<0.65                          [MIRROR study_card_generator:586-593]
  → drop "Unknown/blank" author; compute australian_ratio; warn if <0.60        [MIRROR :613-622]
  → if ≥1 valid citation: write structured list to MCQ.citations (JSON);
      set MCQ.citation = human-readable summary of primary (<=500 chars)
  → else: needs_regeneration=True; append id to mcq_citation_report.json        [do NOT fabricate]
```

**New/changed files:**
- `backend/src/db/models.py` — add `MCQ.citations = Column(JSON, nullable=True)` (mirror `StudyCard.citations`, models.py:1243).
- `backend/alembic/versions/<rev>_add_mcq_citations_json.py` — additive, reversible.
- `backend/scripts/import_mcqs.py` — preserve `references[]`/`citations[]` structured array into `citations`; keep deriving the flat `citation` summary.
- `backend/src/ai/mcq_citation_remediator.py` (NEW) — `MCQCitationRemediator(rag_service).remediate(mcq_dict)`; injectable `rag_service` for tests.
- `scripts/remediate_mcq_citations.py` (NEW CLI) — iterate `data/mcqs/*.json` (reuse `import_mcqs` ignore-list), call the remediator, write structured citations back, emit `data/mcqs/_reports/mcq_citation_report.json` (`validate_corpus`). `--dry-run` = no writes; `--limit N` smoke.

**Reuse policy**: do NOT reimplement grounding, confidence filtering, or point-id extraction — import and call existing code. Only MCQ storage, importer preservation, iteration CLI, and report are new.

---

## L - LOOP

### Loop Execution Strategy
**CRITICAL**: 4-phase sequential workflow with TDD enforcement. No parallel phases (Phase 2 depends on Phase 1 schema; Phase 3 depends on Phase 2 engine).

**Phase Dependency Chain**:
```
Phase 0 (RAG trust established)
  ↓ (confirmed embedder + green RAG quality gate)
Phase 1 (MCQ.citations column + importer preservation)
  ↓ (structured citation storage)
Phase 2 (MCQCitationRemediator)
  ↓ (per-MCQ grounding)
Phase 3 (remediate_mcq_citations.py + report)
  ↓ COMPLETE (9/9 tests; report emitted)
```
**Blocking conditions**: embedding-model mismatch unresolved · any test failing · `alembic upgrade`/`downgrade` not clean · hardcoded secret · migration not reversible.

**Recovery Protocol**: if a phase is blocked, fix the issue in the CURRENT phase before advancing; never proceed to the next phase with a failing test, an unreversible migration, or an unresolved embedding-model mismatch. Revert a refactor that breaks green. Document any blocker resolution in the H section.

### Phase 0: Pre-flight — establish RAG trust (blocking gate)
**TDD Workflow (MANDATORY)**: this phase is a gate, not new tests. RED/GREEN/REFACTOR resumes in Phase 1.
- Confirm the embedding model that indexed `medical_knowledge` matches `RAGService`'s embedder (risk 0.4).
- Run `scripts/test_rag_citation_quality.py` → must exit 0.
- Fix the stale `medical_guidelines` assertions in `test_rag_service.py`.
- **Blocker**: if the model mismatch cannot be resolved, BLOCK and report — remediation scores would be invalid.

### Phase 1: Schema & importer (Tests 1–3)
**TDD Workflow (MANDATORY)**: RED (write Tests 1–3, confirm fail) → GREEN (add `MCQ.citations` column + migration; preserve structured citations in `transform_mcq`) → REFACTOR (stays green).
- **Blocker**: `alembic upgrade head && alembic downgrade -1` not clean.

### Phase 2: Remediation engine (Tests 4–8)
**TDD Workflow (MANDATORY)**: RED (write Tests 4–8) → GREEN (`MCQCitationRemediator` reusing `search_similar`, mirroring `_enrich_with_citations`) → REFACTOR.
- **Blocker**: any grounded citation lacking a `qdrant_point_id`.

### Phase 3: Corpus CLI + report (Test 9)
**TDD Workflow (MANDATORY)**: RED (write Test 9) → GREEN (`remediate_mcq_citations.py` + `validate_corpus`; iterate all MCQ JSON; write citations; emit report) → REFACTOR.
- **Blocker**: an ungrounded MCQ receiving a fabricated/sentinel citation instead of being flagged.

---

## P - PLAN

- **Migration**: additive `citations JSON NULL`; `downgrade()` drops it. No backfill in the migration — backfill is the CLI's job (Phase 3).
- **Remediator query_text**: `f"{stem}\n{explanation}"`; use the correct option's text if explanation is thin.
- **australian_ratio**: reuse the `is_australian` flag from `search_similar` results.
- **Idempotency**: the CLI skips MCQs already carrying valid point-id citations unless `--force`.
- **Never fabricate**: an MCQ with no ≥0.65 point-id hit gets `needs_regeneration=True` and is listed in the report — no synthetic/sentinel citation.
- **Secrets**: RAG/DB endpoints from env only (`QDRANT_URL`, `DATABASE_PASSWORD`); never hardcode. No local LLM (project rule).

---

## H - HANDOFF

### Test Results Summary
```
[TO BE FILLED BY RALPH AFTER EXECUTION — pytest output, 9/9 passing]
```

### TDD Compliance Verification
- [ ] All 9 tests written BEFORE implementation (RED confirmed failing)
- [ ] All 9 tests passing after implementation (GREEN)
- [ ] All 9 tests still passing after refactor
- [ ] 0 tests skipped

### Corpus remediation results (from mcq_citation_report.json)
- MCQs processed: `[TO BE FILLED]`
- MCQs with ≥1 valid point-id citation after remediation: `[TO BE FILLED]`
- MCQs flagged needs_regeneration: `[TO BE FILLED]`
- References with `qdrant_point_id` before → after: `0 → [TO BE FILLED]`
- "Unknown Author" references before → after: `2154 → [TO BE FILLED]`
- Australian-source ratio after: `[TO BE FILLED]` (target ≥0.60)

### Migration evidence
```
[TO BE FILLED — alembic upgrade head && alembic downgrade -1 && alembic upgrade head output]
```

### Success Criteria
- [ ] 9/9 tests passing (100%)
- [ ] Every MCQ citation written by the remediator has a non-empty `qdrant_point_id`
- [ ] 0 "Unknown Author" in remediated citations
- [ ] Australian-source ratio ≥0.60 across remediated citations (or documented shortfall + regeneration list)
- [ ] MCQs lacking grounding are listed in `mcq_citation_report.json`, not given fake citations
- [ ] Migration reversible; embedding-model risk (0.4) resolved and documented

### Deliverables Checklist
- [ ] `MCQ.citations` JSON column + Alembic migration (reversible)
- [ ] `backend/scripts/import_mcqs.py` preserves structured citations
- [ ] `backend/src/ai/mcq_citation_remediator.py` (`MCQCitationRemediator`)
- [ ] `scripts/remediate_mcq_citations.py` CLI + `validate_corpus`
- [ ] `data/mcqs/_reports/mcq_citation_report.json` emitted
- [ ] Stale `test_rag_service.py` collection-name assertions fixed

---

## Permissions (Ralph Autonomous Execution)

<!-- RALPH-PERMISSIONS:BEGIN -->
allow:
  - Bash(cd backend && pytest:*)
  - Bash(cd backend && alembic upgrade:*)
  - Bash(cd backend && alembic downgrade:*)
  - Bash(python scripts/remediate_mcq_citations.py:*)
  - Bash(python scripts/test_rag_citation_quality.py:*)
add-dir:
  - /home/dev/Development/irStudy
<!-- RALPH-PERMISSIONS:END -->

---

### Quality Gates

**Tests (this PRD's surface only):**
- [ ] `cd backend && pytest tests/test_ai/test_mcq_citation_remediator.py tests/test_db/test_mcq_citations_column.py tests/test_scripts/test_import_preserves_citations.py tests/test_scripts/test_mcq_citation_report.py` → passing
- [ ] `cd backend && python -m py_compile src/ai/mcq_citation_remediator.py` → exit code 0

**Migration reversibility:**
- [ ] `cd backend && alembic upgrade head && alembic downgrade -1 && alembic upgrade head` → exit code 0

**RAG pre-flight (Phase 0):**
- [ ] `python scripts/test_rag_citation_quality.py` → exit code 0

**Security (passes only when no secret is found):**
- [ ] `! grep -rEn "sk-ant-|DATABASE_PASSWORD\s*=\s*['\"]|QDRANT_API_KEY\s*=\s*['\"]" backend/src backend/scripts scripts` → exit code 0

**Commit — final gate:**
- [ ] `git log -1 --pretty=%s | grep -q 'PRD-MCQ-CITATION-001'` → exit code 0

### Commit as the final gate (MANDATORY)
After every Quality Gate passes, commit the work:
`git add -A && git commit -m "feat(content): PRD-MCQ-CITATION-001 — RAG-grounded MCQ citations with qdrant_point_id"`.
Never commit `.env`, generated reports under `_reports/`, or scratch files.
