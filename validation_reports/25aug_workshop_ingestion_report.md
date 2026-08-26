# 25-August Workshop Content Ingestion — Validation Report

**Date:** 2026-08-25
**Scope:** Dr. Amir AMC workshop drop (`25-august-docs/`) → expert-reviewed HTML study notes + RMO study cards
**Pipeline:** extract → RAG-enrich → expert-agent assessment → validation gate → render → import

---

## 1. Volume

| Stage | Count |
|---|---|
| Source files (deduped) | 193 case files + 1 RMO Case Bank PDF |
| Extracted (DOCX + PDF, 0 failures) | 193 |
| RAG-enriched (Qdrant medical_knowledge) | 193 |
| Expert-assessed (`.assessed.json`) | **193 / 193** |
| Passed validation gate | **193 / 193 (100%)** |
| HTML notes rendered | 193 |
| RMO study cards imported | 79 |

By target specialty: obstetrics_gynaecology 70, gastroenterology 43, musculoskeletal 27,
neurology 18, general_practice 18, urology 11, ophthalmology 6.

## 2. Expert review output

Across 193 cases (each reviewed by a matched Australian clinical expert agent — history-taking,
clinical-documentation/O&G, surgical-skills/MSK, physical-examination/ophthalmology — fact-checked
against the 12-textbook Qdrant RAG index):

- **444 corrections** (avg 2.3/case) — genuine clinical errors / outdated guidance
- **814 enhancement suggestions** (avg 4.2/case)
- **612 RAG citations** (avg 3.2/case) — every ID verified present in that case's own retrieved context

Station types: history_taking 74, diagnosis_management 66, counselling 22, physical_examination 14,
emergency_scenario 11, communication 6. Difficulty: medium 111, hard 74, easy 8.

## 3. Notable clinical corrections surfaced (sample)

The expert agents caught real errors in the source teaching material, including:
- **Drug safety:** SGLT2-inhibitor vs GLP-1-agonist pancreatitis attribution; flucloxacillin/dicloxacillin
  wrongly cleared in penicillin allergy (mastitis); nitrate + PDE5-inhibitor contraindication understated;
  Hiprex mis-taught as an alkalinising analgesic; ranitidine (withdrawn 2020) still listed.
- **Emergencies reframed:** cauda equina / metastatic cord compression as time-critical; tension
  pneumothorax needle decompression before imaging; septic arthritis not excluded by normal temperature
  (aspirate before diagnosing gout).
- **Australian-standard updates:** cervical screening 5-yearly HPV + self-collection accuracy; GDM cut-off
  fasting ≥5.1 mmol/L (ADIPS); pre-eclampsia no longer requires proteinuria (SOMANZ); NAFLD/NASH → MASLD/MASH;
  C. difficile first-line oral vancomycin/fidaxomicin (eTG); placenta praevia grading retired (RANZCOG).
- **Diagnostic traps:** visible haematuria in older men needs cystoscopy + CT urography regardless of BPH;
  postmenopausal IDA mandates scope-first workup; CN VI supplies lateral rectus; cherry-red spot = CRAO not CRVO.

## 4. KNOWN ISSUE — RAG index coverage gap (action required)

**~20% of citations (122/612) were flagged by agents as "tangential / best-available."** Multiple
independent agents reported that the Qdrant `medical_knowledge` index returns weak/off-topic matches
for specific domains, because the 12 indexed textbooks are GP/medicine-weighted and lack dedicated
O&G, MSK, ophthalmology and urology sources.

Worst-affected topics (agent-reported): foot/ankle/leg pain, PPH/APH/DFM/labour-arrest, pelvic organ
prolapse, urinary incontinence, several urology stations, headache bundle, ophthalmology cases 1 & 4.
Strong retrieval: breast triple-test, cirrhosis/CKD/jaundice, KEMH antenatal (anaemia, GDM), gout distribution.

**Recommendation:** ingest RANZCOG/SOMANZ/KEMH (O&G), an MSK/orthopaedics text, an ophthalmology reference,
and a urology source into `medical_knowledge`, then re-run `scripts/enrich_with_rag.py --force` and refresh
citations. This is the single highest-value follow-up for citation quality (ties directly to the pre-existing
2.45%-citation-coverage gap noted in the platform assessment).

## 5. Validation gate

`scripts/validate_workshop_assessments.py` enforced per case: valid JSON, ≥3 citations with
qdrant_point_ids that exist in the case's rag_context (fabricated IDs rejected), ≥2 enhancements,
station_type/difficulty from the DB enums, no placeholder patterns, PDF cases have structured sections.
One fabricated citation ID (gynae_4_vulvar_lump) was caught and re-mapped to a real chunk. Final: **193/193 pass.**

## 6. Phase 6 — OSCE station generation (added)

From the assessed notes, **60 full AMC OSCE stations** were generated (8 expert agents),
validated (rubric sums to 15, ≥2 red_flags, ≥2 australian_guidelines, ≥2 verified citations,
role-appropriate patient/candidate/examiner instructions), and imported → **osces table 226 → 286**.

By specialty: obstetrics_gynaecology 14, musculoskeletal 10, gastroenterology 9, neurology 8,
urology 8, general_practice 6, ophthalmology 5. **All 60 populate red_flags,
australian_guidelines AND examiner_instructions** — fields left empty on 225/226 pre-existing
platform OSCEs, so this set also establishes the richer schema going forward.

Two importer bugs fixed en route:
- `map_osce_type` referenced non-existent enum members (`COMMUNICATION_SKILLS`,
  `PROCEDURAL_SKILLS`, `DATA_INTERPRETATION`) — the SAME enum-mismatch class as the May 2026
  OSCE-import incident; remapped to the real OSCEType members.
- `osce_id` VARCHAR(50) overflow on long case names → now bounded (prefix + md5 suffix).
- import_osces.py extended to load `*.osce.json`, persist examiner_instructions +
  australian_guidelines, and know the 3 new specialties.

Also fixed a real API read-path bug found during verification: `OSCEResponse`'s
Australian-terminology validator (`backend/src/api/v1/osces/schemas.py`) matched `"er "`
as a substring, 500-ing the list/detail endpoints on any text containing words like
"after/her/consider". Changed to whole-word matching → endpoints now serve the stations
(list + detail verified HTTP 200; new specialties served with populated red_flags).

PRE-EXISTING bug NOT fixed (out of scope, affects all OSCEs not just new ones): the
`GET /osces/{id}/rubric` endpoint 500s for every station — `OSCERubric.rubric` is typed
`Dict[str, Dict[str, Any]]` but no OSCE (old or new) stores that shape. Rubric data is fully
accessible via `GET /osces/{id}`. Worth a separate fix (decide canonical rubric schema).

Artifacts: 25-august-docs/osce_generated/*.osce.json,
scripts/validate_osce_stations.py, 25-august-docs/OSCE_GENERATION_INSTRUCTIONS.md.

## 7. Artifacts

- Notes: `ICRP_OSCE_Preparation/{Medicine,ObGyn,Musculoskeletal,Urology,Ophthalmology}/WS_*.html`
- Staging + assessments: `25-august-docs/staging/<Specialty>/*.json` + `*.assessed.json`
- Scripts: `scripts/{extract_workshop_cases,enrich_with_rag,rag_query_cli,render_workshop_note,validate_workshop_assessments,convert_rmo_casebank}.py`
- RMO cards: `data/study_cards/rmo_case_bank_cards.json`
