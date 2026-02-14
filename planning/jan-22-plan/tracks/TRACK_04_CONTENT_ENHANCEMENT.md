# Track 4: Content Enhancement
**Duration:** Weeks 5-15
**Goal:** Add RAG-verified citations to 46 existing OSCE modules + 750 flashcards
**Status:** 📋 PLANNED (Starts Week 5)

---

## Overview

This track enhances existing educational content by adding:
- **RAG-verified citations** with page numbers
- **Evidence summaries** for clinical claims
- **Picture integration** from source textbooks
- **Quality improvements** based on QA validation

**Why Week 5 Start:**
- QA-003 RAG validation ready (Week 2 complete)
- Initial content generation established (Weeks 1-4)
- Can run in parallel with new content generation

---

## Content Inventory

### Existing Content Requiring Enhancement

#### 1. OSCE Modules (46 modules)
**Current State:**
- 46 OSCE modules exist (history, examination, communication)
- **Citation Status:** 0/46 have citations (0%)
- **Quality:** Good clinical content, but lacks evidence references
- **Format:** Consistent 8-minute stations with marking rubrics

**Target State:**
- **Citation Coverage:** 46/46 with RAG citations (100%)
- **Minimum citations per module:** 3-5 references
- **Evidence summaries:** 1-2 paragraphs per module
- **Picture integration:** 20-30 modules with relevant images

#### 2. Flashcards (750 cards)
**Current State:**
- 750 Anki-style flashcards across specialties
- **Citation Status:** ~50/750 have citations (7%)
- **Quality:** Varies; some outdated, some lack references

**Target State:**
- **Citation Coverage:** 750/750 with citations (100%)
- **Minimum citations per card:** 1 reference
- **Updated content:** 100% aligned with current guidelines
- **Picture integration:** 150 cards with diagrams/images

---

## Week-by-Week Enhancement Schedule

### Weeks 5-7: OSCE Modules Enhancement (30 modules)

#### Week 5: First 10 OSCE Modules
**Target:** Cardiology + Respiratory (high-priority modules)
**Status:** ⏳ PENDING

**Modules to Enhance:**
1. Chest Pain History (Cardiology)
2. Cardiovascular Examination (Cardiology)
3. ECG Interpretation (Cardiology)
4. Dyspnea History (Respiratory)
5. Respiratory Examination (Respiratory)
6. Spirometry Interpretation (Respiratory)
7. Acute Asthma Management (Respiratory)
8. COPD Exacerbation (Respiratory)
9. Pleural Effusion Assessment (Respiratory)
10. Pulmonary Embolism Diagnosis (Respiratory)

**Enhancement Process:**

**Step 1: Content Audit (4 hours)**
- [ ] Read all 10 OSCE modules
- [ ] Identify clinical claims requiring evidence
  - Example: "First-line treatment for STEMI is primary PCI"
  - Example: "Spirometry FEV1/FVC <70% indicates airflow obstruction"
- [ ] Mark citation insertion points in text
- [ ] Prioritize by importance (critical vs. supportive)

**Step 2: RAG Citation Retrieval (8 hours)**
```python
# For each clinical claim:
claim = "Primary PCI is superior to thrombolysis for STEMI within 90 minutes"

# Query RAG
rag_results = rag.query(claim, top_k=5)

# Expected sources:
# 1. NHFA/CSANZ ACS Guidelines 2023, p.45-47 (0.94 confidence)
# 2. Therapeutic Guidelines: Cardiovascular, p.123 (0.92 confidence)
# 3. ESC STEMI Guidelines 2017, p.119 (0.89 confidence)

# Select top 2 Australian sources
selected_citations = rag_results[:2]  # Top 2 matches
```

**Step 3: Citation Integration (8 hours)**
- [ ] Insert citations into OSCE modules
- [ ] Format: "Reference: [Title], [Page], [Year]"
- [ ] Ensure citation placement after relevant claim
- [ ] Validate page numbers exist (QA-003)

**Example Before:**
```
Station: Chest Pain History

Task: Take a focused history from a patient with chest pain.

Marking Criteria:
- Characterize chest pain (SOCRATES) - 4 points
- Identify red flags for ACS - 4 points
- Risk stratification (HEART score) - 4 points
- Appropriate disposition - 4 points
- Communication skills - 4 points
```

**Example After:**
```
Station: Chest Pain History

Task: Take a focused history from a patient with chest pain to identify
features of acute coronary syndrome (ACS).

Background:
Acute coronary syndrome (ACS) includes STEMI, NSTEMI, and unstable angina.
Early recognition is critical as primary PCI within 90 minutes improves
outcomes compared to thrombolysis (NHFA/CSANZ ACS Guidelines 2023, p.45-47).

Marking Criteria:
- Characterize chest pain (SOCRATES) - 4 points
  - Severity, Onset, Character, Radiation, Associated symptoms
  - Reference: UpToDate: Chest Pain Evaluation, Section 2.1, p.12 (2024)

- Identify red flags for ACS - 4 points
  - Central/left-sided chest pain, radiation to jaw/arm
  - Diaphoresis, nausea, dyspnea
  - Duration >20 minutes, not relieved by rest
  - Reference: Therapeutic Guidelines: Cardiovascular, p.112-114 (2024)

- Risk stratification (HEART score) - 4 points
  - History, ECG, Age, Risk factors, Troponin
  - Score ≥4: High risk, requires admission
  - Reference: NHFA/CSANZ ACS Guidelines, p.52 (2023)

- Appropriate disposition - 4 points
  - High risk: Emergency Department, ECG, troponin
  - Low risk: Outpatient cardiology follow-up
- Communication skills - 4 points

Evidence Summary:
The HEART score is validated for risk stratification in chest pain presentations,
with scores ≥4 indicating >30% risk of major adverse cardiac events within 6
weeks (Six AJ et al. Neth Heart J. 2008;16(6):191-196). Australian guidelines
recommend using HEART score to guide disposition decisions for patients with
suspected ACS (NHFA/CSANZ ACS Guidelines 2023, p.52-54).
```

**Step 4: Quality Validation (4 hours)**
- [ ] Run QA-003 validation on enhanced modules
- [ ] Check citation confidence scores (target >0.90)
- [ ] Manual review of 2 modules (20% sample)
- [ ] Fix any citation errors

**Deliverables:**
- [ ] 10 OSCE modules enhanced with 3-5 citations each
- [ ] Evidence summaries added (1-2 paragraphs per module)
- [ ] QA-003 validation results (>90% confidence)

**Week 5 Target:**
- ✅ 10/46 OSCE modules enhanced (22%)
- ✅ ~40 citations added
- ✅ 2 modules manually reviewed (quality 4.5/5.0)

---

#### Week 6: Next 10 OSCE Modules
**Target:** Emergency Medicine + Neurology
**Status:** ⏳ PENDING

**Modules to Enhance:**
11. Anaphylaxis Management (Emergency)
12. Trauma Assessment (Emergency)
13. Sepsis Recognition (Emergency)
14. Headache Assessment (Neurology)
15. Stroke Examination (Neurology)
16. Seizure Management (Neurology)
17. Peripheral Neuropathy Exam (Neurology)
18. Parkinson's Disease Assessment (Neurology)
19. Multiple Sclerosis History (Neurology)
20. Dementia Assessment (Neurology)

**Process:** Same as Week 5 (Audit → RAG → Integration → Validation)

**Week 6 Target:**
- ✅ 20/46 OSCE modules enhanced (43%)
- ✅ ~80 citations total
- ✅ 200 flashcards enhanced with citations

---

#### Week 7: Next 10 OSCE Modules + Flashcard Start
**Target:** Gastroenterology + Endocrinology + Flashcards
**Status:** ⏳ PENDING

**Modules to Enhance:**
21-30: GI and Endocrine OSCE modules

**Flashcard Enhancement Begins:**
- [ ] Start enhancing 200 flashcards (Week 7)
- [ ] Continue 200 flashcards per week (Weeks 8-10)
- [ ] Priority: High-yield topics (cardiology, respiratory, emergency)

**Flashcard Enhancement Process:**

**Example Before:**
```
Front: What is the first-line treatment for STEMI?
Back: Primary PCI (percutaneous coronary intervention)
```

**Example After:**
```
Front: What is the first-line treatment for STEMI within 90 minutes of presentation?

Back: Primary PCI (percutaneous coronary intervention)

Evidence:
Primary PCI is superior to thrombolysis when performed within 90 minutes
(door-to-balloon time), with lower mortality and reduced rebleeding risk.

Reference:
- NHFA/CSANZ ACS Guidelines 2023, Section 4.2, p.45-47
- Therapeutic Guidelines: Cardiovascular, Chapter 3, p.123 (2024)

Clinical Pearl:
If PCI not available within 90 minutes, consider thrombolysis (tenecteplase)
as second-line option, especially within first 2 hours of symptom onset.
```

**Week 7 Target:**
- ✅ 30/46 OSCE modules enhanced (65%)
- ✅ ~120 citations total in OSCE
- ✅ 200/750 flashcards enhanced (27%)

---

### Weeks 8-10: Complete OSCE + Scale Flashcard Enhancement

#### Week 8: Final 16 OSCE Modules + 200 Flashcards
**Target:** Complete all 46 OSCE modules ✅
**Status:** ⏳ PENDING

**Modules to Enhance:**
31-46: Psychiatry, ObGyn, Paediatrics, General Practice

**Week 8 Target:**
- ✅ **46/46 OSCE modules enhanced (100%)** ✅
- ✅ ~200 citations in OSCE modules
- ✅ 400/750 flashcards enhanced (53%)

---

#### Weeks 9-10: Complete Flashcard Enhancement
**Target:** Finish all 750 flashcards ✅
**Status:** ⏳ PENDING

**Week 9:**
- [ ] Enhance 200 flashcards (600/750 total, 80%)
- [ ] Focus on medium-yield topics

**Week 10:**
- [ ] Enhance final 150 flashcards (750/750 total, 100%) ✅
- [ ] Quality review of all enhanced content
- [ ] Generate before/after comparison report

**Week 10 Target:**
- ✅ **750/750 flashcards enhanced (100%)** ✅
- ✅ ~750 citations added to flashcards
- ✅ All content enhancement complete

---

### Weeks 11-15: Picture Integration

#### Week 11-12: Extract 200 Pictures from Source Books
**Status:** ⏳ PENDING

**Picture Sources:**
1. **Textbooks (Physical/PDF):**
   - Talley & O'Connor's Clinical Examination
   - Davidson's Principles & Practice of Medicine
   - Harrison's Principles of Internal Medicine
   - Kumar & Clark's Clinical Medicine

2. **Medical Atlases:**
   - Color Atlas of Clinical Dermatology
   - ECG Made Easy (Hampton)
   - Chest X-Ray Made Easy (Corne)

3. **Online Resources (Attribution Required):**
   - Wikimedia Commons (public domain medical images)
   - OpenStax Anatomy (CC-BY license)
   - NEJM Image Challenge (fair use for education)

**Picture Categories:**
- ECGs (50 images): STEMI, arrhythmias, heart blocks
- Chest X-Rays (30 images): Pneumonia, pneumothorax, heart failure
- Dermatology (50 images): Rashes, lesions, skin cancers
- Anatomy diagrams (30 images): Heart, lungs, GI system
- Clinical photos (40 images): Physical exam findings

**Extraction Process:**
1. **Scan/Extract from textbooks** (manual or OCR)
2. **Crop and enhance** (remove backgrounds, resize)
3. **Add attribution** (book title, page, publisher)
4. **Store in organized folders** (`data/images/ecg/`, `data/images/cxr/`)
5. **Create metadata file** (image_database.json)

**Week 11-12 Target:**
- ✅ 200 pictures extracted and organized
- ✅ Attribution metadata complete
- ✅ Ready for integration into content

---

#### Week 13-14: Integrate 200 Pictures into MCQs/OSCE
**Status:** ⏳ PENDING

**Integration Examples:**

**MCQ with ECG:**
```
Question:
A 65-year-old man presents with chest pain. His ECG is shown below.

[ECG IMAGE: ST elevation in leads II, III, aVF]

What is the most likely diagnosis?
A. Anterior STEMI
B. Inferior STEMI ✓
C. Posterior STEMI
D. NSTEMI
E. Pericarditis

Explanation:
The ECG shows ST elevation in the inferior leads (II, III, aVF),
consistent with inferior STEMI. This typically results from occlusion
of the right coronary artery (RCA).

Reference:
- Therapeutic Guidelines: Cardiovascular, p.123 (2024)
- Hampton JR. ECG Made Easy, 9th edition, p.87 (2019)

Image Attribution:
ECG adapted from Hampton JR. ECG Made Easy, 9th edition, p.87
(Elsevier 2019). Used for educational purposes.
```

**OSCE with Clinical Photo:**
```
Station: Dermatology Assessment

Task: Examine this skin lesion and provide a diagnosis.

[IMAGE: Irregular pigmented lesion with asymmetry, border irregularity]

Expected Findings:
- ABCDE criteria for melanoma:
  - Asymmetry ✓
  - Border irregularity ✓
  - Color variation ✓
  - Diameter >6mm ✓
  - Evolution/changing ✓

Diagnosis: Suspicious for malignant melanoma

Management:
- Urgent referral to dermatology (within 2 weeks)
- Excision biopsy for histopathology
- Do NOT perform shave biopsy (contraindicated for melanoma)

Reference:
- Australian Cancer Council: Melanoma Guidelines, p.23-25 (2023)
- Therapeutic Guidelines: Dermatology, p.156 (2024)

Image Attribution:
Clinical photo from Color Atlas of Clinical Dermatology, 4th edition,
p.234 (Elsevier 2020). Used for educational purposes.
```

**Week 13-14 Target:**
- ✅ 200 pictures integrated into content
- ✅ 50 MCQs with images
- ✅ 30 OSCE modules with images

---

#### Week 15: Final 100 Pictures + Advanced Integration
**Status:** ⏳ PENDING

**Advanced Picture Features:**
- [ ] Annotated images (arrows, labels)
- [ ] Side-by-side comparisons (normal vs. abnormal)
- [ ] Progressive disclosure (click to reveal diagnosis)

**Example Annotated ECG:**
```
[ECG with annotations]
→ ST elevation in V1-V4 (anterior leads)
→ Q waves indicating prior MI
→ T wave inversion (ischemia)

Diagnosis: Anterior STEMI with prior infarction
```

**Week 15 Target:**
- ✅ **300 total pictures integrated** ✅
- ✅ 50 annotated images
- ✅ All picture attributions verified

---

## Content Enhancement Quality Standards

### Citation Standards
- **Minimum citations per OSCE:** 3 references
- **Minimum citations per flashcard:** 1 reference
- **Citation confidence:** >0.90 (RAG validation)
- **Page number accuracy:** 100% verified
- **Australian guidelines:** Primary source for all citations

### Evidence Summary Standards
- **Length:** 1-2 paragraphs (100-200 words)
- **Content:**
  - Key recommendation or finding
  - Evidence level (if applicable)
  - Clinical relevance
- **Readability:** Grade 10-12 reading level
- **Citations:** 2-3 references per summary

### Picture Standards
- **Attribution:** 100% of images have source attribution
- **Quality:** Minimum 1024x768 resolution
- **File format:** JPEG for photos, PNG for diagrams
- **File size:** <500KB per image (optimized)
- **Licensing:** Fair use for education or Creative Commons

---

## Success Metrics

| Metric | Target | Week 7 | Week 10 | Week 15 | Status |
|--------|--------|--------|---------|---------|--------|
| **OSCE Modules Enhanced** | 46 | 30 (65%) | 46 (100%) ✅ | 46 ✅ | 🟡 0/46 |
| **OSCE Citations** | 150+ | 120 | 200 | 200 | 🟡 0 |
| **Flashcards Enhanced** | 750 | 200 (27%) | 750 (100%) ✅ | 750 ✅ | 🟡 0/750 |
| **Flashcard Citations** | 750+ | 200 | 750 | 750 | 🟡 0 |
| **Pictures Integrated** | 300 | 0 | 0 | 300 ✅ | 🟡 0/300 |
| **Citation Confidence** | >0.90 | 0.92 | 0.93 | 0.94 | 🟡 - |
| **Quality Score** | 4.5/5.0 | 4.3 | 4.5 | 4.7 | 🟡 - |

---

## Before/After Comparison Report

### Example OSCE Module Comparison

**Before Enhancement:**
- Title: Chest Pain History
- Length: 1 page
- Citations: 0
- Evidence summary: None
- Pictures: None
- Quality score: 3.5/5.0

**After Enhancement:**
- Title: Chest Pain History - Acute Coronary Syndrome Recognition
- Length: 2 pages
- Citations: 4 (NHFA/CSANZ Guidelines, eTG Cardiovascular, UpToDate, HEART score paper)
- Evidence summary: 150 words (ACS epidemiology, HEART score validation)
- Pictures: 1 (ECG showing STEMI)
- Quality score: 4.7/5.0

**Improvement:** 34% quality increase

---

## Risk Management

### Risk 1: Picture Copyright Issues (MEDIUM)
**Issue:** Pictures from textbooks may have copyright restrictions
**Mitigation:**
- Fair use for education (transformative, non-commercial)
- Full attribution with source book details
- Use public domain images where possible (Wikimedia Commons)
**Contingency:** Replace copyrighted images with open-source alternatives

### Risk 2: Citation Retrieval Accuracy (LOW)
**Issue:** RAG may not find exact citations for all claims
**Mitigation:**
- Three-tier validation (auto-approve, LLM verify, reject)
- Manual review of 10% sample
- QA-003 automated validation
**Contingency:** Manual citation search for problematic claims

### Risk 3: Timeline Compression (LOW)
**Issue:** 46 modules + 750 flashcards + 300 pictures in 11 weeks
**Mitigation:**
- Automated RAG citation retrieval
- Template-based enhancement
- Parallel processing
**Contingency:** Extend to Week 17 if needed (within Phase C buffer)

---

## Related Documents
- [QA-003 Upgrade Plan](../QA_003_UPGRADE_PLAN.md)
- [Week 5 Execution Plan](../weekly/WEEK_05_EXECUTION.md)
- [Expansion Roadmap](../EXPANSION_ROADMAP.md)

---

**Last Updated:** 2026-01-24
**Status:** 📋 PLANNED (Starts Week 5)
**Owner:** Content Enhancement Team
**Start Date:** 2026-02-22 (Week 5)
**Completion Date:** 2026-04-25 (Week 15)
