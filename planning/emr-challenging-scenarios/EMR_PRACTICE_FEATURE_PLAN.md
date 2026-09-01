# EMR Challenging-Scenario Practice + AI Assessment — Feature Plan

**Date:** 2026-08-26
**Goal:** Students practise documenting **challenging clinical scenarios** in the Epic/Cerner EMR
simulator; the system + Claude assess **how completely and accurately they captured the case**, and
declare **PASS/FAIL** — where the make-or-break is whether the critical details were documented and
no critical error was made.

---

## Context / why now

We just ingested a large body of challenging content (60 AMC OSCE stations, 79 RMO acute-care cases
with explicit "traps," 193 expert-reviewed notes). The EMR practice **system already exists** but is
disconnected: the editor UI is built, the data model is complete, and a real Claude validator exists —
but the live submit path returns a **hardcoded 12.5/15 for every submission**, there are only **3
practice cases**, and the case answer-key column exists in the DB but is unused. This plan connects the
content to the existing machinery and turns on real assessment.

## What already exists (REUSE — do not rebuild)

| Capability | Where | State |
|---|---|---|
| EMR editor UI (SOAP 4-tab, prescriptions, pathology, auto-save, submit) | `frontend/src/pages/emr/*`, `frontend/src/components/emr/{epic,cerner}/*` | ✅ built |
| Session lifecycle (start/get/auto-save/submit/list) | `backend/src/api/v1/emr/sessions.py` | ✅ built |
| Data model: case, session, SOAP, Rx, path, validation-result | `backend/src/db/models.py:1385-1505` | ✅ built |
| **Answer-key + rich clinical columns on the case** (`validation_criteria`, `source_osce_id`, `physical_exam_findings`, `investigation_results`, `medications`, `allergies`, `demographics`) | live DB (migration `20260215_1200_008_add_emr_tables.py`) | ⚠️ **in DB, UNMAPPED in ORM, unused** |
| Real Claude validator (AMC 15-mark, PHI-anonymised, Vault key) | `backend/src/services/emr/validators/claude_validator.py` (`ClaudeValidator.validate`) | ⚠️ orphaned (import only) |
| Real Claude validator wired to a *secondary* endpoint | `backend/src/ai/clinical_validator.py` via `backend/src/services/emr_validation_service.py` → `POST /emr/validation/soap-note` | ⚠️ real but not called by submit |
| Validation display components (score banner, 5-category rubric bars) | `frontend/src/components/emr/validation/{ValidationStatusBanner,AMCRubricVisualization}.tsx` | ⚠️ orphaned (no page) |
| Rich result type (`missing_elements`, `dangerous_medications`, `strengths`, `areas_for_improvement`) | `frontend/src/types/emr.ts` (`ValidationResult`) | ✅ defined |
| Content to seed cases | `data/study_cards/rmo_case_bank_cards.json` (79), `25-august-docs/osce_generated/*.osce.json` (60), `osces` table (286) | ✅ available |

## The gap (BUILD — the real work)

1. **No challenging cases with an answer-key.** Only 3 `mock_patients`; none carry `validation_criteria`.
2. **Assessment is mock.** `sessions.py:617-663` hardcodes the score; the real validators are unwired.
3. **No answer-key-aware prompt.** Existing prompts grade generic rubric, not "captured vs expected."
4. **Frontend:** no scenario/task brief shown to the student (`presenting_complaint` fetched, never
   rendered); submit dead-ends — the validation results page/route was never built.

---

## Design

### The case = scenario + answer-key
Each practice case is a `MockPatient` row carrying a **`validation_criteria`** JSON answer-key:

```jsonc
{
  "presenting_scenario": "58M, central crushing chest pain 40 min, diaphoretic. Triage obs: ...",
  "task": "Document your assessment and initial management as the admitting RMO.",
  "expected": {
    "subjective": ["SOCRATES of pain", "cardiac risk factors", "sildenafil/erectile-drug use", "..."],
    "objective":  ["BP in both arms", "ECG within 10 min", "signs of failure", "..."],
    "assessment": ["ACS/STEMI as primary", "must-not-miss: aortic dissection, PE"],
    "plan":       ["aspirin 300 mg chewed", "serial troponin", "STEMI pathway / cardiology",
                    "analgesia", "monitored bed"]
  },
  "critical_errors": [                       // committing ANY of these = automatic FAIL
    "nitrates given despite hypotension / inferior-RV infarct / recent sildenafil"
  ],
  "must_not_miss": ["aortic dissection considered"]   // omitting = FAIL
}
```

The RMO cases populate this almost directly: **FIRST → first expected plan item, numbered THEN →
plan/orders, TRAP → critical_errors, SAY → expected communication**. OSCE stations map their
`red_flags`→must_not_miss, `australian_guidelines`→expected plan, rubric→domain weights.

### Assessment flow (the "success vs failure" engine)
On `POST /emr/sessions/{id}/submit`, keep Layers 1-2 (real), **replace the Layer-3 mock** with a real
Claude call that receives the student's SOAP+orders+meds AND the case `validation_criteria`, and returns:

```jsonc
{
  "overall_score": 0-15, "pass_fail": true|false,
  "completeness": { "subjective": 0-100, "objective": 0-100, "assessment": 0-100, "plan": 0-100 },
  "captured": [ "...expected items found..." ],
  "missing_elements": [ "...expected items NOT documented..." ],
  "critical_errors_committed": [ "...traps triggered..." ],
  "accuracy_notes": [ "wrong dose/route, wrong Dx, ..." ],
  "strengths": [...], "areas_for_improvement": [...]
}
```

**PASS/FAIL rule:** `pass_fail = false` if any `critical_errors_committed` OR any `must_not_miss`
omitted; else pass at ≥9/15 (existing 60% AMC threshold). This is the user's "difference between
success and failure."

---

## Implementation plan

### Phase 1 — Case model + answer-key (backend, small)
- Map the existing-but-unmapped columns on `MockPatient` (`backend/src/db/models.py:1385`):
  `source_osce_id`, `demographics`, `medications`, `allergies`, `physical_exam_findings`,
  `investigation_results`, `validation_criteria`. (Columns already exist in DB — ORM-only change; a
  no-op/verify Alembic migration to confirm.)

### Phase 2 — Case content (data, the target list)
- New `scripts/build_emr_practice_cases.py`: from the 24 target cases (RMO + OSCE source, see
  `EMR_PRACTICE_TARGET_CASES.md`), generate `mock_patients` rows with demographics, realistic
  `vital_signs`, `presenting_complaint`, and the `validation_criteria` answer-key. Use expert agents
  (history-taking / surgical / clinical-documentation) to author each answer-key from the source
  content + RAG, validated by a gate (must have ≥1 critical_error, non-empty expected S/O/A/P), then
  import. Reuse the pattern of `backend/scripts/import_mock_patients.py`.
- Result: `mock_patients` 3 → ~27, all `difficulty="hard"`/`"medium"`, selectable via the unchanged
  `POST /emr/sessions/start?difficulty=hard&specialty=...`.

### Phase 3 — Wire real assessment (backend, the load-bearing change)
- In `backend/src/api/v1/emr/sessions.py:617-663`, replace the mock `layer_3_result`/`mock_validation`
  with a call to `ClaudeValidator.validate(soap_note, patient_context, rule_based_result)`
  (`services/emr/validators/claude_validator.py`), passing `mock_patient` + its `validation_criteria`
  as `patient_context`. Persist the real result to `validation_score` + `score_breakdown` (existing
  read path at `get_session` lines 232-264 already consumes that shape) and also write the normalized
  `EMRValidationResult` row (currently never populated).
- Extend `ClaudeValidator._build_validation_prompt` to score **captured-vs-expected against the
  answer-key** and emit `missing_elements` / `critical_errors_committed` / `pass_fail` (schema above).
- Pick ONE credential path (Vault `emr/claude-api-key` — already used by this validator). Keep PHI
  anonymisation. Model: current latest Sonnet.

### Phase 4 — Frontend (2 gaps)
- **Scenario brief panel:** render `presenting_complaint` + `validation_criteria.task` at the top of
  `EpicEMRPage.tsx`/`CernerEMRPage.tsx` (beside the existing conversion Alert, ~lines 173-188) so the
  student sees the challenge and the task.
- **Results page:** build `EMRValidationPage` + register `/emr/validation/:sessionId` in
  `frontend/src/App.tsx` (submit already navigates there — currently dead-ends). Compose the orphaned
  `ValidationStatusBanner` + `AMCRubricVisualization`, and render `pass_fail`, `missing_elements`,
  `critical_errors_committed`, `strengths`, `areas_for_improvement` from `ValidationResult`. Fix the
  `sessionId` vs `validation_id` param mismatch.

### Phase 5 — Verify end-to-end
- Seed a case (e.g. #1 STEMI). Start session → document a deliberately incomplete note that gives
  nitrates → submit → confirm **FAIL** with the critical error + missing items surfaced. Then a good
  note → **PASS** with high completeness. Confirm `EMRValidationResult` row written and the results
  page renders. Repeat for a non-emergency case (e.g. #20 AKI).

## Constraints / notes
- Claude API only (Vault key), PHI anonymised before every call — reuse existing `_anonymize_phi`.
- Don't touch the parallel dead code (`services/emr/session_service.py`, `PatientService` is unused by
  the live route) — either wire or leave; do not add a third path.
- Scope guard: v1 = 24 cases + real assessment + results page. Pool supports 60+ later with no new tooling.

## Suggested sequencing for a build
Phase 1 (ORM map) → Phase 3 (wire assessment, testable with the 3 existing patients) → Phase 2
(author the 24 cases) → Phase 4 (frontend) → Phase 5 (verify). Phases 2 and 4 can run in parallel.
