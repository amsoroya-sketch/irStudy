# EMR Practice — Target Case List (v1)

**Date:** 2026-08-26
**Purpose:** Curated "top + variety" challenging scenarios for EMR documentation practice, where
students document in the Epic/Cerner simulator and Claude assesses how completely/accurately they
captured the case — with a defined **make-or-break** criterion per case (the "difference between
success and failure").

**Source pool:** 79 RMO Case Bank cases (each has an explicit *TRAP = the mistake that loses the
case*), the 60 new AMC OSCE stations, and the 193 expert-reviewed workshop notes.

**How each case is scored (see the feature plan):** every case carries a `validation_criteria`
answer-key — required Subjective / Objective / Assessment / Plan items + required orders/meds +
**critical errors (auto-fail)**. Claude compares the student's EMR note to it → per-domain
completeness %, accuracy, critical items captured vs missed, critical errors committed →
**overall score + PASS/FAIL**. A case **fails** if a critical error is committed OR a must-not-miss
element is omitted, regardless of prose quality.

Difficulty tiers: 🔴 resuscitation/time-critical · 🟠 red-flag subacute · 🟡 ward/prescribing.

---

## Tier A — Time-critical resuscitation (8) 🔴
Documentation challenge: capture the *right first action* + avoid the drug/sequence that kills.

| # | Case | System | Make-or-break (critical error → FAIL) |
|---|------|--------|----------------------------------------|
| 1 | Central chest pain, 58M — ?STEMI | Cardiology | ECG within 10 min documented; **no nitrates if hypotensive / inferior-RV infarct / sildenafil** |
| 2 | Tearing chest pain, unequal arm BP — aortic dissection | Cardiology/Vascular | **No aspirin/antiplatelet/anticoagulant until dissection excluded**; CT aortogram + BP/HR control |
| 3 | Anaphylaxis | Emergency/Immunol | **IM adrenaline 0.5 mg (1:1000) documented first; patient flat not sitting up**; not antihistamine-led |
| 4 | Breathless, hypotensive, tracheal shift — tension pneumothorax | Respiratory | **Needle decompression before any CXR**; clinical diagnosis documented |
| 5 | Haematemesis + hypotension — upper GI bleed | Gastroenterology | 2 large cannulas, crossmatch, MTP; **variceal pathway (terlipressin+abx) ≠ peptic**; restrictive transfusion |
| 6 | Suspected meningitis with sepsis | ID/Emergency | **Antibiotics NOT delayed for CT/LP**; ceftriaxone + dexamethasone; notifiable-disease action |
| 7 | Diabetic ketoacidosis | Endocrine | **Fluids before insulin; potassium checked/replaced**; euglycaemic-DKA (SGLT2) considered |
| 8 | Abdo/back pain + hypotension, 74M smoker — ruptured AAA | Vascular/Emergency | **Unstable patient does NOT go to CT**; permissive hypotension, vascular + theatre now |

## Tier B — Red-flag / must-not-miss, subacute (6) 🟠
Documentation challenge: document the exclusion of the dangerous cause before the benign label.

| # | Case | System | Make-or-break |
|---|------|--------|--------------|
| 9 | RIF pain, 22F | Surgery/O&G | **Pregnancy test (β-hCG) documented BEFORE imaging**; ectopic/torsion in DDx |
| 10 | Acute testicular pain, 16M | Urology | Torsion until proven otherwise; **urology called — do not wait for US**; 6-hour window |
| 11 | Worst-ever sudden headache — SAH | Neurology | **A normal CT after 6 h does NOT exclude SAH** → LP for xanthochromia; red-flag screen |
| 12 | Visible haematuria + LUTS, older man | Urology | **Not attributed to BPH** — cystoscopy + CT urography regardless of benign DRE |
| 13 | Code Stroke | Neurology | Time-last-known-well + glucose documented; **no aggressive BP drop / no aspirin before bleed excluded** |
| 14 | Acute red eye / sudden vision loss | Ophthalmology | Vision-threatening cause excluded (GCA/CRAO/acute glaucoma/orbital cellulitis); urgent referral + timing |

## Tier C — Undifferentiated / broad-workup (3) 🔴🟠
Documentation challenge: completeness — the systematic net, not a premature single diagnosis.

| # | Case | System | Make-or-break |
|---|------|--------|--------------|
| 15 | Undifferentiated shock | Emergency | **Four shock categories worked through** (hypovol/distributive/cardiogenic/obstructive); VBG+lactate, catheter |
| 16 | Drowsy patient, no history | Emergency/Neuro | Airway/GCS first; **reversibles documented (glucose, opioids/naloxone, CO2)**; collateral history chased |
| 17 | Syncope — the workup | Cardiology/GP | Cardiac vs neuro vs orthostatic; ECG; **driving advice + safety-netting documented** |

## Tier D — Ward / prescribing / metabolic (4) 🟡
Documentation challenge: the order set, the drug chart, and the monitoring plan.

| # | Case | System | Make-or-break |
|---|------|--------|--------------|
| 18 | Hyperkalaemia with ECG changes | Renal/Emergency | **Calcium gluconate = cardioprotection, does NOT lower K⁺** (documents both protect + shift + remove); ECG |
| 19 | Inpatient hyperglycaemia + insulin prescribing | Endocrine | Basal-bolus-correction documented; **SGLT2 inhibitor withheld during acute illness** |
| 20 | AKI on the ward | Renal | Cause sought; **drug chart re-dosed for AKI / nephrotoxics stopped** (not left at pre-AKI doses) |
| 21 | New AF with fast ventricular rate | Cardiology | Rate control + anticoag decision; **no cardioversion of AF >48 h / unknown onset without anticoag or TOE** |

## Tier E — O&G acute (3) 🔴🟠
| # | Case | System | Make-or-break |
|---|------|--------|--------------|
| 22 | Severe pre-eclampsia / postpartum hypertension | Obstetrics | **BP ≥160/110 treated + magnesium for seizure prophylaxis**; proteinuria not required for diagnosis |
| 23 | Early pregnancy bleeding — ?ectopic | Obstetrics/Gynae | β-hCG + TVS; **anti-D for Rh-negative documented**; PUL/ectopic pathway not benign-miscarriage default |
| 24 | Delirium in an inpatient | Geriatrics/Psych | Cause screen (DIMSTOP); **no antipsychotic in Parkinson's/Lewy body**; documented as delirium not "dementia" |

---

## Coverage summary (variety check)
- **Systems:** cardiology ×4, respiratory ×2, GI ×2, neurology ×3, urology ×2, renal ×2, endocrine ×2,
  O&G ×3, vascular ×2, emergency/undifferentiated ×3, ophthalmology ×1, geriatrics ×1.
- **Acuity:** 11 resuscitation, 7 red-flag subacute, 6 ward/prescribing.
- **Documentation-challenge archetypes:** right-first-action, don't-give-the-lethal-drug,
  exclude-before-you-label, completeness-of-the-net, order-set/drug-chart, monitoring/safety-netting.
- **Difficulty:** all "hard" or "medium" — these are deliberately challenging (the user's ask).

## Expansion path
This v1 = 24. The pool supports **~60+** (all 40 RMO ED + 39 RMO ward + 19 doc-rich OSCE stations)
without new authoring. Add Tier F (tox/psych: paracetamol OD, mixed OD, agitated patient,
self-harm risk, alcohol withdrawal/DTs) and Tier G (paediatric: febrile child, febrile
neutropenia) in v2.
