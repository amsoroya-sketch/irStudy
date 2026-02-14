# Complete Scope: Agent OS Content Generation Plan (Jan 26, 2026)

**Date**: 2026-01-26
**Purpose**: FULL content generation with Agent OS medical experts
**Status**: Planning Phase (awaiting user approval)

---

## Executive Summary

**Previous Attempt**: 600 MCQ proof-of-concept (too narrow)
**Corrected Scope**: 1,508 MCQs + 210 OSCEs + Images + Summaries (complete)

---

## Full Scope Breakdown

### Phase 1: MCQ Generation (1,508 MCQs)

#### A. Comprehensive Topics (658 MCQs) - Priority HIGH
**Source**: `missing_topics_comprehensive_mcqs.json`
**Categories**: 5 major categories, 52 topics

| Category | Topics | Est. MCQs | Agent Routing |
|----------|--------|-----------|---------------|
| **Endocrine & Metabolic** | Hyperthyroidism, Hypothyroidism, Diabetes, Hypoglycemia, Hypercalcemia, Hyponatremia, Hyperkalemia, Hypokalemia, Addison's, Cushing's | ~150 | MED-004 Endocrinology |
| **Syncope & Falls** | Vasovagal syncope, Orthostatic hypotension, Cardiac syncope, Seizure vs syncope, Falls risk assessment, Polypharmacy, Delirium | ~130 | MED-010 GP + MED-005 Neuro |
| **General Medicine** | Anemia, DVT, Cellulitis, UTI, Sepsis, Shock, Fever workup, Weight loss, Fatigue | ~150 | MED-010 GP + MED-006 Emergency |
| **GI & Electrolytes** | GORD, PUD, IBD, IBS, Acute abdomen, Hepatitis, Cirrhosis, Pancreatitis, Diarrhea, Constipation | ~120 | MED-003 Gastroenterology |
| **Neurology** | Stroke, TIA, Headache, Migraine, Seizure, Meningitis, Encephalitis, Peripheral neuropathy, MS, Parkinson's | ~108 | MED-005 Neurology |

#### B. Specialty-Specific MCQs (850 MCQs)

| Specialty | MCQs | Source Files | Agent | Tools |
|-----------|------|--------------|-------|-------|
| **Respiratory** | 200 | week3_respiratory_200_mcqs.json | MED-002 | Spirometry, CXR, Wells PE, CURB-65 |
| **Cardiology** | 200 | week3_cardiology_200_mcqs.json | MED-001 | ECG, GRACE, TIMI, CHA₂DS₂-VASc |
| **Psychiatry** | 250 | week3_psychiatry + missing_psychiatry | MED-009 | PHQ-9, GAD-7, MSE, BPRS, Y-BOCS |
| **Week 1 Mixed** | 100 | week1_regenerated_100_mcqs.json | Route by topic | Multiple agents |
| **Week 2 Mixed** | 100 | week2_regenerated_100_mcqs.json | Route by topic | Multiple agents |

**Total MCQs**: 658 + 850 = **1,508 MCQs**

---

### Phase 2: OSCE Review & Enhancement (210 OSCEs)

**Current Status**: ✅ ALL 210 OSCEs PASSED validation

| File | OSCEs | Status | Action Required |
|------|-------|--------|-----------------|
| `cardiology_50_osces.json` | 50 | ✅ VALID | Add summaries only |
| `respiratory_50_osces.json` | 50 | ✅ VALID | Add summaries only |
| `psychiatry_40_osces.json` | 40 | ✅ VALID | Add summaries only |
| `psychiatry_week1_osces.json` | 5 | ✅ VALID | Add summaries only |
| `missing_topics_comprehensive_osces.json` | 52 | ✅ VALID | Add summaries only |
| `missing_psychiatry_13_osces.json` | 13 | ✅ VALID | Add summaries only |

**Action**: Lightweight update (add summary field, 1-2 sentences per OSCE)
**Estimated Time**: 2-3 hours (0.5-1 min per OSCE)
**Agent**: Use LLM to generate summaries from existing content

---

### Phase 3: Image Integration (1,508 MCQs)

**Image Types by Specialty**:

#### Cardiology (200 MCQs → ~80 with images):
- ECG tracings (STEMI, NSTEMI, AF, VT, RBBB, LBBB)
- Chest X-rays (cardiomegaly, pulmonary edema)
- Echocardiogram findings (EF, valve disease)

#### Respiratory (200 MCQs → ~70 with images):
- Chest X-rays (pneumonia, pneumothorax, effusion, fibrosis)
- Spirometry graphs (obstructive vs restrictive patterns)
- CT chest (PE, ILD patterns)

#### Endocrinology (~150 MCQs → ~40 with images):
- Thyroid function test tables
- Glucose tolerance test graphs
- Hormone level tables

#### Neurology (~108 MCQs → ~50 with images):
- CT brain (stroke, hemorrhage, tumors)
- MRI brain (MS plaques, infarcts)
- EEG traces (seizure patterns)

#### GI & Emergency (~270 MCQs → ~60 with images):
- Abdominal X-rays (obstruction, perforation)
- Endoscopy images (ulcers, varices, polyps)
- Lab result tables

**Image Strategy**:
1. **Priority 1**: Generate text-based MCQs first (Phase 1)
2. **Priority 2**: Add image placeholders with descriptions
3. **Priority 3**: Source/create actual images (external task)

**Image Fields** (already in structure):
```json
"medical_images": [
  {
    "type": "ECG",
    "description": "12-lead ECG showing ST elevation in leads II, III, aVF",
    "file_path": "data-jan-26/images/cardiology/inferior_stemi_ecg.jpg",
    "format": "JPEG",
    "alt_text": "ECG with inferior STEMI pattern"
  }
]
```

---

### Phase 4: Summary Field Addition (1,508 MCQs + 210 OSCEs)

**MCQs**: Summary generated DURING MCQ creation by LLM
**OSCEs**: Summary generated POST-generation (lightweight update)

**Summary Requirements**:
- Length: 50-200 characters (1-2 sentences)
- Content: Key learning point for AMC exam
- Format: Concise, actionable, evidence-based

**Examples**:
```json
// MCQ Summary
"summary": "Inferior STEMI diagnosed by ST elevation in leads II, III, aVF. Immediate PCI is first-line; thrombolysis if PCI unavailable within 90 minutes."

// OSCE Summary
"summary": "MSE assesses appearance, behavior, speech, mood, thought (form/content), perception, cognition, insight. Essential for psychiatric diagnosis and risk assessment."
```

---

## Agent OS Routing Map (10 Medical Experts)

| Agent ID | Specialty | MCQ Count | Tools | Priority |
|----------|-----------|-----------|-------|----------|
| **MED-001** | Cardiology | 200 | ECG, GRACE, TIMI, CHA₂DS₂-VASc | HIGH |
| **MED-002** | Respiratory | 200 | Spirometry, CXR, Wells PE, CURB-65 | HIGH |
| **MED-003** | Gastroenterology | 120 | Endoscopy interpretation, liver function | MEDIUM |
| **MED-004** | Endocrinology | 150 | Hormone panels, glucose tolerance | MEDIUM |
| **MED-005** | Neurology | 108 | CT/MRI interpretation, seizure Dx | MEDIUM |
| **MED-006** | Emergency | 150 | Trauma scoring, sepsis bundles, shock | MEDIUM |
| **MED-007** | OBGYN | 80 | Fetal monitoring, screening tests | LOW |
| **MED-008** | Paediatrics | 100 | Growth charts, developmental milestones | LOW |
| **MED-009** | Psychiatry | 250 | PHQ-9, GAD-7, MSE, risk assessment | HIGH |
| **MED-010** | General Practice | 150 | Preventive care, chronic disease mgmt | MEDIUM |

**Total**: 1,508 MCQs

---

## Execution Timeline (Revised)

### Week 1: High-Priority Specialties (650 MCQs)
- **Day 1-2**: Cardiology 200 MCQs (MED-001) - 10-12 hours
- **Day 2-3**: Respiratory 200 MCQs (MED-002) - 10-12 hours
- **Day 3-4**: Psychiatry 250 MCQs (MED-009) - 12-15 hours

### Week 2: Medium-Priority Specialties (558 MCQs)
- **Day 5-6**: Endocrinology 150 MCQs (MED-004) - 8-10 hours
- **Day 6-7**: Emergency 150 MCQs (MED-006) - 8-10 hours
- **Day 7-8**: Syncope/Falls 130 MCQs (MED-010 + MED-005) - 6-8 hours
- **Day 8-9**: GI 120 MCQs (MED-003) - 6-8 hours

### Week 3: Remaining Topics (300 MCQs)
- **Day 10**: Neurology 108 MCQs (MED-005) - 5-6 hours
- **Day 11**: Week 1-2 Mixed 200 MCQs (multi-agent routing) - 8-10 hours

### Week 3: OSCEs & Images (210 OSCEs + images)
- **Day 12**: Add summaries to 210 OSCEs - 2-3 hours
- **Day 13-14**: Image integration (descriptions, placeholders) - 8-10 hours

### Week 4: Validation & Polish
- **Day 15-16**: Final QA-003 validation, Australian compliance - 6-8 hours
- **Day 17**: Documentation, tracking update, PR creation - 4-6 hours

**Total Timeline**: 3-4 weeks (15-17 working days)

---

## Constraints & Requirements (Enforced at Every Step)

### Constraint 11: Citations (BLOCKING)
- **Requirement**: Exactly 3 RAG-verified citations per MCQ
- **Minimum Confidence**: >0.70
- **Australian Priority**: eTG > RANZCP > AMH > International guidelines
- **Fail-Fast**: If <3 citations available, regenerate RAG query

### Constraint 12: LLM-Powered (BLOCKING)
- **Requirement**: 100% LLM-generated content (NO templates)
- **Forbidden Patterns**:
  - "Clinical scenario for {topic}"
  - "Question about {topic}"
  - "Option A/B/C/D" without context
  - "Explanation for {topic}"
- **Fail-Fast**: If placeholder detected, regenerate with different LLM prompt

### Summary Field (REQUIRED)
- **Length**: 50-200 characters
- **Content**: 1-2 sentences capturing key learning point
- **Generation**: LLM-powered (not template)
- **Fail-Fast**: If missing or <50 chars, regenerate

### Australian Compliance (BLOCKING)
- **Spelling**: Australian English (e.g., "favour" not "favor")
- **Drug Names**: Generic names per Australian Medicines Handbook
- **Guidelines**: eTG, RANZCP, RACGP prioritized
- **Emergency Number**: 000 (not 911)
- **Fail-Fast**: QA-001 Australian compliance validator

### Images (REQUIRED for appropriate MCQs)
- **Integration**: medical_images field populated
- **Description**: Clear alt-text for accessibility
- **Placeholder**: If actual image unavailable, detailed description provided
- **Priority**: ECG, CXR, CT/MRI, lab results, spirometry

---

## Quality Gates (4 Stages)

### Gate 1: Pre-Generation (BLOCKING)
- [ ] RAG system operational (Qdrant localhost:6333)
- [ ] LLM operational (Ollama localhost:11434)
- [ ] All 10 medical expert agents loaded (MED-001 through MED-010)
- [ ] Embedding model loaded (S-PubMedBert)
- [ ] Output directory exists (data-jan-26/)
- [ ] Pre-commit hook installed

### Gate 2: Incremental (Per-MCQ BLOCKING)
- [ ] 3 RAG citations fetched (confidence >0.70)
- [ ] Citation content extracted (non-empty)
- [ ] LLM generated clinical scenario (no placeholders)
- [ ] Patient demographics present (age, gender)
- [ ] Summary field generated (50-200 chars)
- [ ] No placeholder patterns detected

### Gate 3: Post-Generation (Per-File BLOCKING)
- [ ] Content substance validation passed
- [ ] QA-003 RAG validator: >70% Tier 1 auto-approval
- [ ] QA-001 Australian compliance: 100% pass
- [ ] QA-002 Clinical accuracy: No critical errors
- [ ] Citation validation: 100% have 3 citations
- [ ] Summary validation: 100% have summaries

### Gate 4: Pre-Commit (BLOCKING)
- [ ] Pre-commit hook runs automatically
- [ ] No placeholder patterns detected (6 patterns checked)
- [ ] Minimum content lengths met
- [ ] Australian context markers present
- [ ] Exit code 0 (PASS) required to commit

---

## Success Metrics

### Quantitative (Must Achieve 100%)
1. **1,508 MCQs** generated with Agent OS medical experts
2. **4,524 citations** validated (1,508 × 3)
3. **0 placeholder patterns** across all content
4. **1,508 summaries** generated (1 per MCQ)
5. **210 OSCE summaries** added (lightweight update)
6. **~400 images** integrated (descriptions + placeholders)

### Qualitative (Target >90%)
1. **QA-003 Tier 1 auto-approval**: >70% (stretch: >90%)
2. **Australian compliance**: 100%
3. **Clinical accuracy**: No critical errors
4. **Specialty tool usage**: Evidence of ECG/spirometry/MSE tools applied
5. **Educational value**: Suitable for AMC exam preparation

### Performance
1. **Generation rate**: 0.3-0.5 MCQs/second (accounting for LLM + validation)
2. **Citation accuracy**: >85% average RAG confidence
3. **Validation pass rate**: >95% first-time (minimal rework)
4. **Zero rework MCQs**: <5% require regeneration

---

## Deliverables (data-jan-26/)

### MCQs (1,508 files organized by specialty)
```
data-jan-26/mcqs/
├── cardiology_200_mcqs.json (MED-001)
├── respiratory_200_mcqs.json (MED-002)
├── psychiatry_250_mcqs.json (MED-009)
├── endocrinology_150_mcqs.json (MED-004)
├── emergency_150_mcqs.json (MED-006)
├── gastroenterology_120_mcqs.json (MED-003)
├── neurology_108_mcqs.json (MED-005)
├── syncope_falls_130_mcqs.json (MED-010 + MED-005)
├── general_medicine_150_mcqs.json (MED-010 + MED-006)
└── week1_week2_mixed_200_mcqs.json (Multi-agent routing)
```

### OSCEs (210 with summaries)
```
data-jan-26/osces/
├── cardiology_50_osces_with_summaries.json
├── respiratory_50_osces_with_summaries.json
├── psychiatry_40_osces_with_summaries.json
├── psychiatry_week1_osces_with_summaries.json
├── comprehensive_52_osces_with_summaries.json
└── missing_psychiatry_13_osces_with_summaries.json
```

### Images (Descriptions + Placeholders)
```
data-jan-26/images/
├── cardiology/ (~80 ECG/CXR descriptions)
├── respiratory/ (~70 CXR/spirometry descriptions)
├── neurology/ (~50 CT/MRI descriptions)
├── endocrinology/ (~40 lab result tables)
└── emergency/ (~60 trauma imaging descriptions)
```

### Validation Reports
```
data-jan-26/validation/
├── qa003_validation_report.json
├── australian_compliance_report.json
├── citation_validation_report.json
├── content_substance_report.json
└── final_audit_report.json
```

---

## Rollback Plan

### If >5% Placeholder Rate After 100 MCQs
1. **STOP immediately** (fail-fast)
2. **Diagnose root cause**:
   - Is RAG citation content being passed to LLM?
   - Is LLM prompt correct (using citation content)?
   - Is Agent OS routing working (specialty-specific tools)?
3. **Fix prompts/logic**
4. **Delete invalid MCQs** (start fresh)
5. **Retry with validation**

### If QA-003 Tier 1 Approval <70% After 200 MCQs
1. **Analyze rejection reasons** (QA-003 logs)
2. **Improve RAG query specificity** (better keywords)
3. **Enhance LLM prompts** (more detailed instructions)
4. **Extend timeline** (Week 2: 50-60%, Week 3: 70-80%, Week 4: 90%+)

### If Agent OS Medical Experts Not Available
1. **Fallback to generic LLM** (OllamaClient) - LAST RESORT
2. **Increase validation rigor** (manual QA reviews)
3. **Accept longer timeline** (4-6 weeks instead of 3-4)

---

## Next Steps (Awaiting Approval)

1. **User Approval**: Review this complete scope plan
2. **Confirm Priorities**:
   - Start with high-priority specialties (Cardiology, Respiratory, Psychiatry)?
   - Or comprehensive topics first (658 MCQs across all specialties)?
3. **Confirm Image Strategy**:
   - Descriptions only (fast)?
   - Or actual image sourcing (slower, requires external resources)?
4. **Begin Execution**: Once approved, start with Week 1 Day 1 (Cardiology 200 MCQs)

---

**Document Status**: Draft - Awaiting User Approval
**Created**: 2026-01-26
**Next Review**: After user feedback on scope/priorities
**Estimated Total Time**: 3-4 weeks (15-17 working days)
