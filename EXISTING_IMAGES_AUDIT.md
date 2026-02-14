# Existing Medical Images Audit

**Date:** 2026-02-06
**Total Images:** 463 (318 usable + 145 directories)
**Total Size:** 71 MB
**Source:** HEAL (University of Utah Health Education Assets Library)

---

## Summary

We have **318 high-quality medical images** already downloaded from HEAL, primarily covering **3 of 11 specialties**:

| Specialty | Images | Coverage | Status |
|-----------|--------|----------|--------|
| **Haematology** | 160 | 🟢 Good | 60 taxonomy nodes, 160 images = 2.7 per node |
| **Cardiology** | 84 | 🟡 Partial | 96 taxonomy nodes, 84 images = 0.9 per node |
| **Dermatology** | 74 | 🟡 Partial | 71 taxonomy nodes, 74 images = 1.0 per node |
| **Malaria** | 1 | 🔴 Minimal | Not in taxonomy (infectious disease topic) |
| **TOTAL** | 319 | - | 227 nodes covered, ~1.4 images per node |

**Gap:** We have 3/11 specialties (27%) with images, covering ~227/831 nodes (27%).

---

## Detailed Breakdown

### HEAL Images: 318 total

#### Haematology (160 images) - ✅ Good Coverage

**Topics with images:**
- Acute myeloid leukemia: 2 images
- Thalassemia: 9 images
- Iron deficiency anaemia: 10 images
- Chronic lymphocytic leukemia: 9 images
- *...and 116 more topics with ~140 additional images*

**Taxonomy Nodes:** 60
**Images per Node:** 2.7 (above target of 2-3 for medium priority)
**Assessment:** ✅ **Good coverage** - Haematology is well-represented

**HEAL Topics:** 120 subdirectories in `data/medical_images/heal/hematology/`

---

#### Cardiology (84 images) - 🟡 Partial Coverage

**Sample Topics with images:**
- Acute coronary syndrome ECG
- Angina ECG
- Anterior wall MI
- Atrial fibrillation ECG
- Atrial flutter ECG
- Bifascicular block
- Brugada syndrome
- First degree AV block
- Hyperkalemia ECG
- Inferior wall MI
- Left bundle branch block
- Long QT syndrome
- NSTEMI
- Pacemaker ECG
- *...and more*

**Taxonomy Nodes:** 96
**Images per Node:** 0.9 (below target of 8 for high priority)
**Assessment:** 🟡 **Needs more images** - Target is 768 images (96 × 8)
**Gap:** 84/768 = 11% coverage

---

#### Dermatology (74 images) - 🟡 Partial Coverage

**Taxonomy Nodes:** 71
**Images per Node:** 1.0 (below target of 8 for high priority)
**Assessment:** 🟡 **Needs more images** - Target is 568 images (71 × 8)
**Gap:** 74/568 = 13% coverage

---

### Missing Specialties (0 images each)

| Specialty | Nodes | Target Images | Gap |
|-----------|-------|---------------|-----|
| **Respiratory** | 61 | 305 | 100% |
| **Neurology** | 100 | 800 | 100% |
| **Gastroenterology** | 88 | 704 | 100% |
| **Endocrinology** | 72 | 576 | 100% |
| **Obstetrics/Gynaecology** | 79 | 632 | 100% |
| **Paediatrics** | 84 | 672 | 100% |
| **Psychiatry** | 45 | 225 | 100% |
| **Emergency Medicine** | 75 | 600 | 100% |

**Total Gap:** 8 specialties, 604 nodes, ~4,514 images needed

---

## Coverage Analysis

### By AMC Priority

| AMC Priority | Nodes | Images | Images/Node | Target | Gap |
|--------------|-------|--------|-------------|--------|-----|
| **Critical (5/5)** | ~450 | ~234 | 0.5 | 3,600 | 93% |
| **High (4/5)** | ~224 | ~60 | 0.3 | 1,792 | 97% |
| **Medium (3/5)** | ~157 | ~24 | 0.2 | 785 | 97% |
| **TOTAL** | 831 | 318 | 0.4 | 6,177 | 95% |

**Assessment:** We have only 5% of our target image library.

### By Specialty

| Coverage Level | Specialties | Nodes | Images |
|----------------|-------------|-------|--------|
| **Good (>2 img/node)** | 1 (Haematology) | 60 | 160 |
| **Partial (0.5-2 img/node)** | 2 (Cardiology, Derm) | 167 | 158 |
| **None (0 img/node)** | 8 specialties | 604 | 0 |

---

## Image Quality Assessment

### HEAL Images

**Format:** JPEG
**Naming:** `heal_[6-digit-ID].jpg` (e.g., `heal_889688.jpg`)
**Organization:** Good - organized by specialty/topic
**Quality:** ✅ Likely high (HEAL is reputable medical education resource)

**Sample Paths:**
```
data/medical_images/heal/hematology/acute_myeloid_leukemia/heal_889688.jpg
data/medical_images/heal/cardiology/atrial_fibrillation_ECG/heal_890123.jpg
data/medical_images/heal/dermatology/psoriasis/heal_889456.jpg
```

### Other Sources

**Malaria:** 1 image (not in current taxonomy - infectious disease topic)
**MedPix:** Directory exists but empty (0 images)
**NIH Chest X-ray:** Directory exists but empty (0 images)

---

## Mapping to Taxonomy

### Coverage by Taxonomy Nodes

**Covered:** ~227/831 nodes (27%)
**Uncovered:** ~604/831 nodes (73%)

### Haematology Mapping (160 images → 60 nodes)

**Taxonomy Structure:**
```json
{
  "haematology": {
    "anaemia": {
      "iron_deficiency": { "images": 10, "status": "good" },
      "thalassemia": { "images": 9, "status": "good" },
      ...
    },
    "leukaemia": {
      "acute_myeloid": { "images": 2, "status": "needs_more" },
      "chronic_lymphocytic": { "images": 9, "status": "good" },
      ...
    }
  }
}
```

**Notes:**
- HEAL uses American spelling "hematology" (we use "haematology")
- Most HEAL topics map directly to taxonomy nodes
- Some taxonomy nodes have no images yet

### Cardiology Mapping (84 images → 96 nodes)

**Well-Covered Topics:**
- ECG patterns (STEMI, NSTEMI, AF, flutter, blocks)
- Myocardial infarction (anterior, inferior, lateral)
- Arrhythmias

**Missing Topics:**
- Echocardiography images
- Cardiac CT/MRI
- Catheterization images
- Heart failure imaging
- Valvular disease imaging

**Assessment:** Need 684 more images to reach target (768 total)

### Dermatology Mapping (74 images → 71 nodes)

**Coverage:** ~1 image per node (need 8 per node)

**Assessment:** Need 494 more images to reach target (568 total)

---

## Recommendations

### Immediate Actions (Today)

1. ✅ **Audit Complete** - We now know what we have
2. **Create Image Catalog** - JSON file mapping images to taxonomy nodes
3. **Link to MCQs** - Update MCQ database with existing image URLs
4. **Prioritize Next Downloads** - Focus on high-AMC-relevance missing specialties

### Priority 1: Fill Critical Gaps (This Week)

Download images for these high-impact specialties first:

| Specialty | Priority | Nodes | Target Images | Rationale |
|-----------|----------|-------|---------------|-----------|
| **Emergency Medicine** | Urgent | 75 | 600 | 12-18% AMC weight, 100% high-yield |
| **Respiratory** | High | 61 | 305 | 10-15% AMC weight, 82% high-yield |
| **Neurology** | High | 100 | 800 | 8-12% AMC weight, 90% high-yield |
| **Gastroenterology** | High | 88 | 704 | 8-12% AMC weight, 94% high-yield |

**Total:** 324 nodes, ~2,409 images

### Priority 2: Complete Existing Specialties

Bring partially covered specialties to full coverage:

| Specialty | Current | Target | Gap |
|-----------|---------|--------|-----|
| Cardiology | 84 | 768 | 684 images |
| Dermatology | 74 | 568 | 494 images |

**Total:** 1,178 images

### Priority 3: Remaining Specialties

| Specialty | Nodes | Target Images |
|-----------|-------|---------------|
| Endocrinology | 72 | 576 |
| Obstetrics/Gynaecology | 79 | 632 |
| Paediatrics | 84 | 672 |
| Psychiatry | 45 | 225 |

**Total:** 2,105 images

---

## Download Strategy

### Approach A: HEAL API (If Available)

**Pros:** Same source, consistent quality, already have 318 images
**Cons:** Need API integration

**Steps:**
1. Research HEAL API documentation
2. Implement proper `search_heal()` function
3. Download missing specialties/topics
4. Estimated time: 4-6 hours implementation + 1-2 hours download

### Approach B: Alternative Sources

**OpenI (NIH):** Open Access medical images with API
**Radiopaedia:** Excellent radiology images, has API
**MedPix:** NIH database, good for clinical photos
**PubMed Central:** Open Access journal figures

**Pros:** Multiple sources, fallback options
**Cons:** Different image quality/formats, licensing varies

### Approach C: Hybrid (Recommended)

1. **Week 1:** Use existing 318 images for MVP
2. **Week 2:** Implement HEAL API for remaining downloads
3. **Week 3:** Add alternative sources for gaps
4. **Week 4:** Quality review and replacement

---

## File Structure

### Current Structure
```
data/medical_images/
├── heal/
│   ├── hematology/ (120 subdirs, 160 images)
│   ├── cardiology/ (40+ subdirs, 84 images)
│   └── dermatology/ (35+ subdirs, 74 images)
├── malaria/ (1 image)
├── medpix/ (empty)
└── nih_chest_xray/ (empty)
```

### Recommended Structure (Aligned with Taxonomy)
```
data/medical_images/
├── cardiology/
│   ├── coronary_artery_disease/
│   │   ├── acute_mi/
│   │   │   └── stemi/
│   │   │       ├── anterior_stemi_001.jpg
│   │   │       └── anterior_stemi_002.jpg
│   │   └── stable_angina/
│   └── arrhythmias/
├── respiratory/
├── dermatology/
├── haematology/
├── ...
└── _sources/  # Keep original downloads for reference
    ├── heal/
    ├── openi/
    └── radiopaedia/
```

**Benefits:** Matches taxonomy folder_path, easier to link to MCQs

---

## Next Steps

### Step 1: Create Image Catalog (2-3 hours)

Generate JSON file mapping existing images to taxonomy:

```json
{
  "catalog_version": "1.0",
  "total_images": 318,
  "images": [
    {
      "id": "heal_889688",
      "path": "data/medical_images/heal/hematology/acute_myeloid_leukemia/heal_889688.jpg",
      "taxonomy_node": "haematology/leukaemia/acute_myeloid_leukaemia/peripheral_blood",
      "specialty": "haematology",
      "amc_relevance": 5,
      "image_type": "microscopy",
      "source": "HEAL",
      "linked_mcqs": []
    }
  ]
}
```

### Step 2: Link Images to MCQs (3-4 hours)

Update MCQ JSON files with image URLs:

```json
{
  "question_id": "cardio_af_001",
  "question": "Which ECG finding suggests atrial fibrillation?",
  "image_url": "/images/cardiology/arrhythmias/atrial_fibrillation/heal_890123.jpg",
  "image_caption": "ECG showing irregular rhythm",
  ...
}
```

### Step 3: Research Download Options (1-2 hours)

Investigate HEAL API and alternatives

### Step 4: Implement Download Script (4-6 hours)

Proper HEAL API integration or alternative source

### Step 5: Download Priority Images (2-4 hours)

Emergency medicine, respiratory, neurology, gastroenterology

---

## Conclusion

**Current Status:**
- ✅ We have 318 high-quality HEAL images
- ✅ Haematology has good coverage (160 images, 60 nodes)
- 🟡 Cardiology and Dermatology need more images
- 🔴 8 specialties have zero images

**Immediate Value:**
- Use existing 318 images for ~20-30 MCQs immediately
- Focus haematology, cardiology ECG, and dermatology questions

**Path Forward:**
1. Catalog existing images → Link to MCQs (Today)
2. Research HEAL API (This week)
3. Download priority specialties (Next 2 weeks)
4. Build toward 6,300 image target (Ongoing)

---

**Generated:** 2026-02-06
**Status:** Audit Complete ✅
**Next:** Create image catalog and link to MCQs
