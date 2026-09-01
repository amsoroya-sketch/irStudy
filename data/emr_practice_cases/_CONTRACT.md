# EMR Practice Case — Authoring Contract (READ FIRST)

You are authoring **EMR documentation practice cases** for the irStudy platform. Each case is one
JSON file. Students will read the scenario, document a SOAP note + orders + meds in an EMR simulator,
and Claude will grade their note **against your answer-key** → PASS/FAIL. Your answer-key IS the
ground truth. Accuracy of the `critical_errors` (auto-fail traps) is the single most important thing.

## Where to write
One file per case: `data/emr_practice_cases/EMRP-<NNNN>-<slug>.json` (e.g. `EMRP-0001-stemi.json`).
Use the exact `mrn` / number you are assigned. Do NOT touch other cases' files.

## Exact JSON schema (the PRD-002 gate enforces this — off-schema = rejected)
```jsonc
{
  "mrn": "EMRP-0001",                    // exactly as assigned, unique
  "name": "Full Name",                   // realistic AU name (fictional)
  "age": 58,
  "gender": "male",                      // "male" | "female"
  "specialty": "cardiology",             // MUST be one of the enum values below
  "difficulty": "hard",                  // "easy" | "medium" | "hard" (as assigned)
  "presenting_complaint": "short triage-line complaint",
  "vital_signs": {                       // realistic, CONSISTENT with the scenario (e.g. hypotensive if shocked)
    "bp": "88/54", "hr": 118, "rr": 24, "spo2": 94, "temp": 36.8, "gcs": 15, "bgl": 6.1
  },
  "medical_history": {                   // JSON object; include what's clinically relevant
    "conditions": ["..."], "medications": ["..."], "allergies": ["..."],
    "social": "...", "family": "..."
  },
  "validation_criteria": {
    "presenting_scenario": "2-4 sentence vignette the student sees: age/sex, complaint, key obs, context.",
    "task": "Document your assessment and initial management as the admitting RMO.",
    "expected": {
      "subjective": ["specific history items the note MUST contain — SOCRATES, risk factors, red-flag screen, key negatives"],
      "objective": ["specific exam/obs/bedside-test items — e.g. 'ECG within 10 min', 'BP in both arms'"],
      "assessment": ["primary Dx + must-consider DDx phrased as documentation expects"],
      "plan": ["ordered management items: drugs w/ dose+route, investigations, referrals, monitoring, disposition"]
    },
    "critical_errors": ["the trap(s) that LOSE the case — committing ANY = automatic FAIL"],  // >=1 REQUIRED
    "must_not_miss": ["diagnoses/actions whose OMISSION = FAIL, e.g. 'aortic dissection considered'"]
  }
}
```

### Rules the gate checks (all must hold)
- All top-level keys present; `validation_criteria` complete.
- `critical_errors` has **≥1** entry.
- Each `expected.{subjective,objective,assessment,plan}` is **non-empty**.
- `specialty` ∈ enum; `difficulty` ∈ enum.
- `presenting_scenario` and `task` non-empty.
- `mrn` unique.

## Enum values (use these EXACT strings)
**specialty:** cardiology, respiratory, gastroenterology, neurology, psychiatry, endocrinology,
emergency_medicine, general_practice, paediatrics, obstetrics_gynaecology, surgery, ophthalmology,
urology, musculoskeletal
**difficulty:** easy, medium, hard

## Source material — REUSE, don't invent clinical content
Most cases have a matching **RMO Case Bank card** in `data/study_cards/rmo_case_bank_cards.json`
(key `cards`, match by `subtopic`). Each card's `answer`/`explanation` encodes:
- **FIRST** → the first, time-critical `expected.plan` item
- **THEN** (numbered) → further `expected.plan` items + orders/meds
- **TRAP ("the mistake that loses the case")** → this becomes a `critical_errors` entry (verbatim intent)
- **SAY** → an `expected.subjective` or `plan` communication item
Cases without an RMO match: find the matching station in `25-august-docs/osce_generated/*.osce.json`
(grep by topic) and/or use your own Australian clinical expertise + guidelines.

## Quality bar
- Australian standards (AMH, eTG, ANZCOR, RACGP/College guidelines). Doses realistic and correct.
- 4–8 items per expected section — specific and checkable, not vague ("consider sepsis" → "give
  ceftriaxone 2g IV within 1 hour; do NOT delay antibiotics for CT/LP").
- `critical_errors` must be the genuinely dangerous action (the target-list "make-or-break").
- `vital_signs` must be internally consistent with the scenario's severity.
- Fictional patient identity; no real PHI.

## Self-validate before returning
For each file you write, confirm: it parses as JSON, all keys present, `critical_errors` ≥1, no empty
expected section, specialty/difficulty spelled exactly from the enum. Report the list of files you wrote.
