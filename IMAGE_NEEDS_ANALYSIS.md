# Medical Image Needs Analysis Report
Generated: 2026-02-05 11:21:05

## Executive Summary

**Current State:**
- Total images in library: **318**
- Images by source:
  - HEAL: 318
- Images by specialty:
  - Hematology: 160 (microscopy)
  - Cardiology: 84 (mostly ECGs)
  - Dermatology: 74 (clinical photos)

**Target:**
- Coverage goal: **35%** of all MCQs and OSCEs
- Additional images needed: **515**
- New total: **833** images

**Estimated Effort:**
- Download time: **0.3 hours** (with 2s rate limiting)
- Using existing `download_heal_comprehensive.py` script

---

## Current Coverage by Specialty (MCQs)

| Specialty | Total MCQs | Current Images | Coverage % | Target Images | **Images Needed** | Priority |
|-----------|------------|----------------|------------|---------------|-------------------|----------|
| general_practice | 766 | 15 | 1.96% | 268 | **253** | HIGH |
| cardiology | 232 | 17 | 7.33% | 81 | **64** | MEDIUM |
| psychiatry | 196 | 0 | 0.00% | 68 | **68** | HIGH |
| gastroenterology | 184 | 12 | 6.52% | 64 | **52** | MEDIUM |
| endocrinology | 108 | 0 | 0.00% | 37 | **37** | HIGH |
| neurology | 84 | 0 | 0.00% | 29 | **29** | HIGH |
| respiratory | 38 | 1 | 2.63% | 13 | **12** | HIGH |

**Total MCQs:** 1608
**Current coverage:** 45 images (2.8%)

---

## Current Coverage by Specialty (OSCEs)

| Specialty | Total OSCEs | Current Images | Coverage % | Target Images | **Images Needed** | Priority |
|-----------|-------------|----------------|------------|---------------|-------------------|----------|
| cardiology | 61 | 32 | 52.46% | 21 | **0** | LOW |
| respiratory | 50 | 9 | 18.00% | 17 | **8** | MEDIUM |
| psychiatry | 45 | 5 | 11.11% | 15 | **10** | MEDIUM |
| general_practice | 33 | 7 | 21.21% | 11 | **4** | LOW |
| gastroenterology | 15 | 4 | 26.67% | 5 | **1** | LOW |
| neurology | 6 | 0 | 0.00% | 2 | **2** | HIGH |

---

## Priority Breakdown

### HIGH Priority (< 5% coverage)
Specialties with critical image shortage:

**GENERAL_PRACTICE**
- Current: 15 images (1.96%)
- Target: 268 images (35%)
- **Need: 253 new images**

**PSYCHIATRY**
- Current: 0 images (0.00%)
- Target: 68 images (35%)
- **Need: 68 new images**

**ENDOCRINOLOGY**
- Current: 0 images (0.00%)
- Target: 37 images (35%)
- **Need: 37 new images**

**NEUROLOGY**
- Current: 0 images (0.00%)
- Target: 29 images (35%)
- **Need: 29 new images**

**RESPIRATORY**
- Current: 1 images (2.63%)
- Target: 13 images (35%)
- **Need: 12 new images**

### MEDIUM Priority (5-20% coverage)
Specialties needing significant expansion:

**cardiology**: Need 64 images (current: 7.33%)

**gastroenterology**: Need 52 images (current: 6.52%)

---

## Download Strategy

### Option 1: HEAL Comprehensive Download (Recommended)
Use the existing `download_heal_comprehensive.py` script with targeted specialty downloads.

**Phase 1: HIGH Priority Specialties** (~2-3 hours)
```bash
# Download for psychiatry, endocrinology, neurology, respiratory
python3 scripts/download_heal_comprehensive.py \
    --specialties psychiatry endocrinology neurology respiratory \
    --images-per-topic 15
```

**Phase 2: MEDIUM Priority Specialties** (~1-2 hours)
```bash
# Download for general_practice, gastroenterology
python3 scripts/download_heal_comprehensive.py \
    --specialties general_medicine gastroenterology \
    --images-per-topic 20
```

**Phase 3: Cardiology Boost** (~30 min)
```bash
# Get more cardiology images (we have ECGs, need clinical images)
python3 scripts/download_heal_comprehensive.py \
    --specialties cardiology \
    --images-per-topic 10
```

### Option 2: Full Automated Download (~4-5 hours)
```bash
# Download all phases automatically
python3 scripts/download_heal_comprehensive.py --phase all
```

---

## Expected Outcomes

After downloading **{needs['summary']['total_images_needed']}** additional images:

| Metric | Before | After |
|--------|--------|-------|
| Total images | {catalog['total_images']} | {plan['target_total']} |
| MCQ coverage | {sum(s['mcqs_with_images'] for s in mcq_stats)} / {sum(s['total_mcqs'] for s in mcq_stats)} ({sum(s['mcqs_with_images'] for s in mcq_stats) / sum(s['total_mcqs'] for s in mcq_stats) * 100:.1f}%) | {sum(need['target_images'] for need in needs['mcqs'].values())} / {sum(s['total_mcqs'] for s in mcq_stats)} (35%) |
| Specialties at 0% | {sum(1 for s in mcq_stats if s['coverage_percent'] == 0)} | 0 |
| Specialties at >30% | {sum(1 for s in mcq_stats if s['coverage_percent'] >= 30)} | {len(mcq_stats)} |

---

## Image Types Needed

Based on question content analysis, prioritize downloading:

1. **ECGs** - for cardiology (STEMI, arrhythmias, conduction blocks)
2. **Chest X-rays** - for respiratory (pneumonia, pneumothorax, pleural effusion)
3. **Microscopy** - for hematology (blood smears, bone marrow)
4. **Dermatology photos** - for GP/dermatology (rashes, lesions, skin cancers)
5. **CT/MRI scans** - for neurology (stroke, hemorrhage, tumors)
6. **Endoscopy images** - for gastroenterology (GI bleed, IBD)
7. **Ultrasound** - for endocrinology (thyroid nodules)
8. **Fundoscopy** - for diabetes/endocrinology (diabetic retinopathy)

---

## Next Steps

1. **Review this analysis** - Confirm target coverage percentage (currently 35%)
2. **Run image matching** - Execute SQL updates to link existing 318 images
   ```bash
   python3 scripts/match_images_to_questions.py --execute
   ```
3. **Download additional images** - Run HEAL download script (Phase 1 first)
4. **Re-run matching** - Link new images to questions
5. **Manual review** - QA check image appropriateness for questions
6. **Update RAG** - Generate CLIP embeddings for multimodal search

---

## Automation Recommendations

**Weekly maintenance script:**
```bash
#!/bin/bash
# Download new HEAL images (10-20 per specialty per week)
python3 scripts/download_heal_comprehensive.py --images-per-topic 5
# Match to questions
python3 scripts/match_images_to_questions.py --execute
# Update catalog
python3 scripts/catalog_medical_images.py
```

This keeps image library growing incrementally without overwhelming downloads.

---

## Appendix: Detailed Specialty Breakdown

### CARDIOLOGY
- Total questions: 232
- Current images: 17 (7.33%)
- Target: 81 images (35% coverage)
- **Gap: 64 images needed**
- Priority: **MEDIUM**

### ENDOCRINOLOGY
- Total questions: 108
- Current images: 0 (0.00%)
- Target: 37 images (35% coverage)
- **Gap: 37 images needed**
- Priority: **HIGH**

### GASTROENTEROLOGY
- Total questions: 184
- Current images: 12 (6.52%)
- Target: 64 images (35% coverage)
- **Gap: 52 images needed**
- Priority: **MEDIUM**

### GENERAL_PRACTICE
- Total questions: 766
- Current images: 15 (1.96%)
- Target: 268 images (35% coverage)
- **Gap: 253 images needed**
- Priority: **HIGH**

### NEUROLOGY
- Total questions: 84
- Current images: 0 (0.00%)
- Target: 29 images (35% coverage)
- **Gap: 29 images needed**
- Priority: **HIGH**

### PSYCHIATRY
- Total questions: 196
- Current images: 0 (0.00%)
- Target: 68 images (35% coverage)
- **Gap: 68 images needed**
- Priority: **HIGH**

### RESPIRATORY
- Total questions: 38
- Current images: 1 (2.63%)
- Target: 13 images (35% coverage)
- **Gap: 12 images needed**
- Priority: **HIGH**
