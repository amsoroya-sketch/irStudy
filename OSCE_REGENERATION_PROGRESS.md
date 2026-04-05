# OSCE Regeneration Progress Tracker

**Date Started:** 2026-03-28
**Status:** IN PROGRESS
**Agent Coordination:** Agent OS expert agents with quality control

---

## Overview

Regenerating 205 placeholder OSCEs across 3 specialties using Agent OS expert agents with comprehensive quality control.

**Root Cause:** Generation failure - OSCEs created as placeholder templates but never filled with actual clinical content (98.6% placeholder rate discovered).

**Solution:** Complete regeneration using expert agents with mandatory quality gates.

---

## Phase 1: Psychiatry OSCEs (40 items)

**Status:** 🔄 IN PROGRESS

**Agent:** mental-health-crisis-expert
**Start Time:** 2026-03-28 [timestamp when agent started]
**Estimated Completion:** 80-120 minutes

### Input File
- `data/osces/psychiatry_40_osces.json` (40 placeholder OSCEs)

### Output File
- `data/osces/psychiatry_40_osces_regenerated.json`

### Backup Created
- `data/osces/backups/[timestamp]/psychiatry_40_osces.json`

### Mandatory Quality Gates

| Gate | Requirement | Status |
|------|-------------|--------|
| **Gate 1: SAFE-T Protocol** | All 40 OSCEs include SAFE-T (Specific plan, Access, Feelings, Earlier attempts, Threat) | ⏳ Pending |
| **Gate 2: Australian Crisis Contacts** | Lifeline 13 11 14, Beyond Blue 1300 224 636 in all OSCEs | ⏳ Pending |
| **Gate 3: Mental Health Act** | NSW 2007 criteria specified for high-risk scenarios | ⏳ Pending |
| **Gate 4: Zero Placeholders** | 0% placeholder rate (was 100%) | ⏳ Pending |
| **Gate 5: Specific Medications** | All medications have doses + PBS codes | ⏳ Pending |
| **Gate 6: Complete Marking Criteria** | 10-15 marking criteria items per OSCE | ⏳ Pending |
| **Gate 7: Clinical Specificity** | No generic phrases ("A patient presents...") | ⏳ Pending |

### Topic Distribution (40 OSCEs)

From metadata analysis:
- Mental Status Examination: 8 OSCEs
- Mood Disorders: 8 OSCEs
- Psychotic Disorders: 6 OSCEs
- Anxiety/Trauma: 6 OSCEs
- Risk Assessment: 6 OSCEs
- Other Psychiatry: 6 OSCEs

### Constraints Applied
- ✅ Constraint 15: Psychiatry MCQ Requirements (SAFE-T mandatory)
- ✅ Gold standard template: `data/osces/psychiatry_week1_osces.json`
- ✅ CONTENT_REGENERATION_PLAN.md requirements

### Expected Improvements

| Metric | Before | After (Target) |
|--------|--------|----------------|
| **Placeholder Rate** | 100% (40/40) | 0% (0/40) |
| **SAFE-T Coverage** | 0% | 100% |
| **Evaluation Score** | 0.36/10 | >8.0/10 |
| **Clinical Content** | Generic templates | Specific demographics, symptoms, medications |
| **Australian Context** | Missing | Crisis contacts, MHA, PBS codes |

### Validation Commands

```bash
# Placeholder detection
python3 scripts/detect_placeholder_content.py data/osces/psychiatry_40_osces_regenerated.json

# Expected output:
# ✅ 0/40 placeholders (0%)
# ✅ Status: OK

# Spot check 3 random OSCEs
jq '.osces[0,10,20] | {topic, has_safet: (.sample_answer.immediate_management | tostring | contains("SAFE-T")), has_crisis_contacts: (.learning_points | tostring | contains("Lifeline"))}' data/osces/psychiatry_40_osces_regenerated.json
```

---

## Phase 2: Cardiology OSCEs (50 items)

**Status:** 📋 PLANNED

**Agent:** medication-management-expert + physical-examination-expert
**Estimated Time:** 100-150 minutes

### Input File
- `data/osces/cardiology_50_osces.json` (50 placeholder OSCEs)

### Output File
- `data/osces/cardiology_50_osces_regenerated.json`

### Mandatory Quality Gates

| Gate | Requirement | Target |
|------|-------------|--------|
| **Gate 1: ECG Interpretation** | Specific ECG findings (not "ECG changes for...") | 100% |
| **Gate 2: Medications** | Doses + PBS codes (e.g., "Aspirin 300mg PO stat, PBS 1215Y") | 100% |
| **Gate 3: STEMI Protocols** | Door-to-balloon <90 min, dual antiplatelet, PCI vs thrombolysis | All ACS cases |
| **Gate 4: Heart Failure** | NYHA class, BNP levels, fluid restriction, medication titration | All HF cases |
| **Gate 5: Zero Placeholders** | 0% placeholder rate (was 100%) | 100% |

### Topic Focus Areas
- STEMI/NSTEMI management (15 OSCEs)
- Heart failure (acute & chronic) (10 OSCEs)
- Arrhythmias (AF, VT, heart block) (10 OSCEs)
- Valvular disease (AS, MR) (5 OSCEs)
- Hypertension & risk stratification (5 OSCEs)
- Other cardiology (chest pain, syncope) (5 OSCEs)

### Australian Guidelines Required
- National Heart Foundation guidelines
- Cardiac Society of Australia and New Zealand (CSANZ)
- eTG: Cardiovascular
- PBS restrictions for anticoagulants (NOACs, warfarin)

---

## Phase 3: Respiratory OSCEs (50 items)

**Status:** 📋 PLANNED

**Agent:** physical-examination-expert
**Estimated Time:** 100-150 minutes

### Input File
- `data/osces/respiratory_50_osces.json` (50 placeholder OSCEs)

### Output File
- `data/osces/respiratory_50_osces_regenerated.json`

### Mandatory Quality Gates

| Gate | Requirement | Target |
|------|-------------|--------|
| **Gate 1: Spirometry Interpretation** | Specific FEV1/FVC values, obstruction patterns | 100% |
| **Gate 2: Oxygen Targets** | COPD 88-92%, non-COPD 94-98% | 100% |
| **Gate 3: Inhaler Devices** | Specific devices (MDI + spacer, Turbuhaler, HandiHaler) | 100% |
| **Gate 4: Medications** | Doses + PBS codes (e.g., "Salbutamol 200mcg 2 puffs PRN, PBS 8333L") | 100% |
| **Gate 5: Zero Placeholders** | 0% placeholder rate (was 100%) | 100% |

### Topic Focus Areas
- Asthma (acute & chronic) (12 OSCEs)
- COPD (exacerbation & stable) (12 OSCEs)
- Pneumonia (CAP, HAP) (8 OSCEs)
- Pulmonary embolism (8 OSCEs)
- Pleural effusion/pneumothorax (5 OSCEs)
- Other respiratory (ILD, lung cancer) (5 OSCEs)

### Australian Guidelines Required
- National Asthma Council
- COPD-X Guidelines
- Thoracic Society of Australia and New Zealand (TSANZ)
- eTG: Respiratory
- PBS restrictions for inhalers and biologics

---

## Phase 4: Missing Topics OSCEs (65 items)

**Status:** 📋 PLANNED (Lower priority)

**Agents:** Specialty-specific agents
**Estimated Time:** 130-200 minutes

### Files to Regenerate
1. `missing_psychiatry_13_osces.json` (13 OSCEs)
   - Topics: Loneliness, grief, post-partum blues
   - Agent: mental-health-crisis-expert

2. `missing_topics_comprehensive_osces.json` (52 OSCEs)
   - Endocrine: diabetes, thyroid (10 OSCEs)
   - Dermatology: rashes, skin lesions (10 OSCEs)
   - ENT: hearing loss, vertigo (8 OSCEs)
   - Ophthalmology: red eye, vision loss (8 OSCEs)
   - Rheumatology: arthritis, back pain (8 OSCEs)
   - Other: various (8 OSCEs)
   - Agents: Specialty-specific

---

## Overall Progress

### Summary Metrics

| Specialty | Total OSCEs | Status | Placeholder Rate Before | Target After |
|-----------|-------------|--------|------------------------|--------------|
| **Psychiatry** | 40 | 🔄 In Progress | 100% | 0% |
| **Cardiology** | 50 | 📋 Planned | 100% | 0% |
| **Respiratory** | 50 | 📋 Planned | 100% | 0% |
| **Missing Topics** | 65 | 📋 Planned | 100% | 0% |
| **TOTAL** | 205 | - | 97.6% (200/205) | 0% |

### Timeline

**Week 1 (High Priority):**
- ✅ Day 1: Create regeneration scripts and delegate to agents
- 🔄 Day 1-2: Psychiatry OSCEs (40 items) - IN PROGRESS
- 📋 Day 2-3: Cardiology OSCEs (50 items)
- 📋 Day 3-4: Respiratory OSCEs (50 items)

**Week 2 (Lower Priority):**
- 📋 Day 5-7: Missing Topics OSCEs (65 items)

**Estimated Total Time:** 12-18 hours across 2 weeks

---

## Quality Assurance Protocol

### Pre-Generation Checklist
- [x] Constraint files read (Constraint 15 for psychiatry)
- [x] Gold standard template reviewed (psychiatry_week1_osces.json)
- [x] Regeneration plan documented (CONTENT_REGENERATION_PLAN.md)
- [x] Backup directories created
- [x] Placeholder detection script tested

### Post-Generation Validation (Per Specialty)
- [ ] Run placeholder detection script (target: 0%)
- [ ] Spot check 5 random OSCEs for clinical specificity
- [ ] Verify specialty-specific requirements (SAFE-T, ECG, spirometry)
- [ ] Check Australian context (guidelines, PBS codes, crisis contacts)
- [ ] Validate marking criteria completeness (10-15 items)
- [ ] Confirm sample answers have specific management plans

### Quality Gates Before Deployment
- [ ] All placeholder detection: 0% across all files
- [ ] Specialty requirements: 100% compliance
- [ ] Australian guidelines: Referenced in all OSCEs
- [ ] Medications: All have doses + PBS codes
- [ ] No generic phrases: Manual review of 10 random OSCEs

---

## Agent Coordination

### Agent Assignment Strategy

| Specialty | Primary Agent | Support Agent | Rationale |
|-----------|---------------|---------------|-----------|
| **Psychiatry** | mental-health-crisis-expert | history-taking-expert | SAFE-T expertise, Mental Health Act knowledge |
| **Cardiology** | medication-management-expert | physical-examination-expert | Medication dosing (anticoagulants, antiplatelet), examination findings |
| **Respiratory** | physical-examination-expert | medication-management-expert | Spirometry interpretation, respiratory examination, inhaler techniques |
| **Endocrine** | medication-management-expert | - | Diabetes management, insulin dosing |
| **Dermatology** | physical-examination-expert | - | Lesion description, dermatology examination |
| **Other** | Specialty-specific | - | As appropriate per topic |

### Quality Control Checkpoints

Each agent MUST complete before returning:
1. ✅ Read constraint files and templates
2. ✅ Generate all assigned OSCEs
3. ✅ Run placeholder detection (target: 0%)
4. ✅ Spot check 3-5 OSCEs for quality
5. ✅ Verify specialty-specific requirements
6. ✅ Document any failures or issues

---

## Known Issues & Resolutions

### Issue 1: Placeholder Content Root Cause
**Problem:** OSCEs generated as templates but never filled with clinical content
**Evidence:** 98.6% placeholder rate (345/350 items)
**Resolution:** Complete regeneration using expert agents with quality gates

### Issue 2: Metadata Was Misleading
**Problem:** Metadata claimed success (`validation_failures: []`) but content was empty
**Evidence:** All reference content fields empty, generic phrases throughout
**Resolution:** Added placeholder detection script to catch this in future

### Issue 3: Only 1 Good OSCE File
**Problem:** Only `psychiatry_week1_osces.json` (5 OSCEs) had real content
**Opportunity:** Use as gold standard template for all regeneration

---

## Success Criteria

### Immediate (End of Week 1)
- ✅ 140 OSCEs regenerated (3 main specialties)
- ✅ 0% placeholder rate on regenerated files
- ✅ Evaluation scores >8.0/10 (vs 0.36 currently)
- ✅ 100% specialty-specific requirement compliance

### Short-term (End of Week 2)
- ✅ All 205 placeholder OSCEs regenerated
- ✅ 100% content completeness across all files
- ✅ Ready for AMC practice use

### Long-term (Week 3+)
- ✅ Create Constraint 16: OSCE Requirements (prevent future placeholders)
- ✅ Integrate placeholder detection with CI/CD pipeline
- ✅ Update generation workflow to prevent recurrence

---

## Files Created

### Scripts
1. `scripts/regenerate_psychiatry_osces.py` - Psychiatry OSCE regeneration with Claude CLI
2. `scripts/detect_placeholder_content.py` - Placeholder detection (existing)

### Documentation
1. `OSCE_REGENERATION_PROGRESS.md` (this file)
2. `CONTENT_REGENERATION_PLAN.md` (existing)
3. `OSCE_STUDY_CARD_ANALYSIS.md` (existing)

### Backups
- `data/osces/backups/[timestamp]/` - All original files before regeneration

---

## Next Actions

### After Psychiatry Completion
1. Validate all quality gates
2. If PASS: Replace original file, update documentation
3. If FAIL: Debug, fix, re-run
4. Create regeneration script for Cardiology
5. Delegate to medication-management-expert

### After All OSCEs Complete
1. Run full evaluation on all regenerated files
2. Compare scores: Before (0.36/10) vs After (target >8.0/10)
3. Document lessons learned
4. Create Constraint 16 to prevent future placeholders
5. Update generation pipeline

---

**Last Updated:** 2026-03-28
**Next Update:** After psychiatry OSCEs complete (~2 hours)
