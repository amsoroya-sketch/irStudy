# Medical Image Inventory Analysis & Linking Strategy
**Date:** 2026-02-04  
**Phase 1 Database Status:** 1,608 MCQs + 210 OSCEs (Total: 1,818 items)  
**Current Image Inventory:** 318 images (HEAL)

---

## Executive Summary

### Current Status
- **Total Images Downloaded:** 318 (HEAL Phase 1)
- **Content Items Requiring Images:** ~725/1,818 (40%)
- **Current Coverage:** 0% (images not yet linked)
- **Quick Win Potential:** 27.6% coverage in 4-6 hours

### Key Findings
1. **We have sufficient cardiology images** (84 ECGs for 200 MCQs + 50 OSCEs)
2. **Respiratory medicine is the biggest gap** (200 MCQs + 50 OSCEs, 0 images)
3. **Existing 318 images are well-organized** with metadata and categorization
4. **Database schema ready** (`image_url` and `image_caption` fields exist in MCQ model)

### Recommendations
1. **Phase 1 (IMMEDIATE):** Link existing 318 HEAL images → 27.6% coverage
2. **Phase 2 (HIGH PRIORITY):** Download 100 respiratory images → 62.1% coverage
3. **Phase 3 (MEDIUM PRIORITY):** Download 175 additional specialty images → 86.2% coverage

---

## 1. Current Image Inventory (318 Images)

### 1.1 Inventory Breakdown

| Specialty | Images | Categories | Primary Use |
|-----------|--------|------------|-------------|
| **Cardiology** | 84 | 23 ECG types | MCQs, OSCE interpretation stations |
| **Hematology** | 160 | 32 conditions | MCQs, blood film interpretation |
| **Dermatology** | 74 | 15 conditions | MCQs, clinical diagnosis |
| **TOTAL** | **318** | **70** | - |

### 1.2 Cardiology ECG Images (84 images)

**Coverage:** 23 ECG categories including:
- **Arrhythmias:** Atrial fibrillation (5), Atrial flutter (10), VT (5), VF (4), SVT (2)
- **Ischemia:** STEMI (1), NSTEMI (0), Angina (1), MI by location (anterior, inferior, lateral, posterior)
- **Conduction Blocks:** LBBB (0), RBBB (7), AV blocks (1st°, 2nd°, 3rd°), Bifascicular (4)
- **Hypertrophy:** LVH (0), RVH (2), LAE (5), RAE (2)
- **Other:** Pacemaker (10), Brugada (0), Long QT (0), Electrolyte (hypo/hyperkalemia)

**Image Format:** PNG files, organized by condition  
**Metadata:** JSON files with title, description, HEAL source URL

### 1.3 Hematology Microscopy Images (160 images)

**Coverage:** 32 hematological conditions including:
- **Anemia:** Iron deficiency (10), Megaloblastic (10), Hemolytic (10), Sickle cell (4), Thalassemia (9)
- **Leukemia:** AML (2), CLL (9), ALL (0), Hairy cell (2), APL (5)
- **Bone Marrow:** Aspirate (10), Biopsy (1)
- **Blood Cells:** Normal smear (10), Reticulocytes (10), Plasma cells (10), Target cells (6)
- **Coagulation:** DIC (2), Thrombocytopenia (3), Purpura (5)
- **Other:** Multiple myeloma (10), Spherocytosis (2), Elliptocytosis (2)

**Image Format:** JPG files, microscopy images  
**Metadata:** CSV and JSON with detailed condition information

### 1.4 Dermatology Clinical Photos (74 images)

**Coverage:** 15 skin conditions including:
- **Infections:** Scabies (10), Impetigo (1), Molluscum (2)
- **Inflammatory:** Atopic dermatitis (9), Seborrheic dermatitis (4), Psoriasis (0), Nummular (4)
- **Cancers:** BCC (10), SCC (5), Melanoma (4)
- **Other:** Acne (8), Urticaria (6), Vitiligo (1), Stasis dermatitis (7)

**Image Format:** JPG files, clinical photographs  
**Metadata:** Condition-specific metadata files

---

## 2. Content Analysis - MCQs (580 MCQs)

### 2.1 MCQ Distribution by Week/Specialty

| Week | Specialty | MCQ Count | Images Available | Coverage | Image Need |
|------|-----------|-----------|------------------|----------|------------|
| Week 1 | General Medicine | 100 | 234 (heme+derm) | Partial | Low priority |
| Week 2 | Psychiatry | 80 | 0 | N/A | Not needed |
| Week 3 | **Cardiology** | **200** | **84** | **42%** | **HIGH** |
| Week 3 | **Respiratory** | **200** | **0** | **0%** | **CRITICAL** |
| **TOTAL** | - | **580** | **318** | **Variable** | - |

### 2.2 Image-Appropriate MCQ Topics

Based on analysis of 580 MCQs, the following topics would benefit from images:

**High Value (200+ MCQs):**
- Cardiology: 200 MCQs → ECG interpretation, cardiac imaging
- Respiratory: 200 MCQs → CXRs, CT scans, PFTs, ABG graphs

**Medium Value (50-100 MCQs):**
- Hematology: ~50 MCQs in general medicine → Blood smears
- Dermatology: ~30 MCQs in general medicine → Clinical photos

**Lower Value (<50 MCQs):**
- Gastroenterology: Future content → Endoscopy, abdominal imaging
- Neurology: Future content → CT/MRI brain
- Emergency Medicine: Future content → Trauma X-rays

### 2.3 Database Schema Verification

**MCQ Model (backend/src/db/models.py):**
```python
# Line 248-249
image_url = Column(String(500), nullable=True)
image_caption = Column(String(500), nullable=True)
```

**OSCE Model (backend/src/db/models.py):**
```python
# Line 368
supporting_documents = Column(JSON, nullable=True)  # URLs to test results, images
```

**Status:** ✅ Database schema supports image linking

---

## 3. Content Analysis - OSCEs (145 OSCEs)

### 3.1 OSCE Distribution by Specialty

| Specialty | OSCE Count | Images Available | Image Need |
|-----------|-----------|------------------|------------|
| **Cardiology** | 50 | 84 ECGs | **HIGH** - ECG interpretation stations |
| **Respiratory** | 50 | 0 | **CRITICAL** - CXR interpretation stations |
| Psychiatry (Week 1) | 5 | 0 | Not needed (communication-based) |
| Psychiatry (Additional) | 40 | 0 | Not needed (communication-based) |
| **TOTAL** | **145** | **84** | - |

### 3.2 OSCE Station Types Requiring Images

**ECG Interpretation (Cardiology):**
- Candidate shown ECG, must identify rhythm/pathology
- 84 ECGs available for rotation across 50 stations
- Coverage: Excellent (1.68 images per station)

**CXR/CT Interpretation (Respiratory):**
- Candidate shown imaging, must identify pathology
- 0 images currently available
- Need: ~50-75 respiratory images minimum

**Physical Examination:**
- May benefit from reference images (e.g., rashes, examination techniques)
- Lower priority

**Emergency Scenarios:**
- May benefit from investigation results (ECG, labs, imaging)
- Medium priority

---

## 4. Image Coverage Gap Analysis

### 4.1 Current vs Needed

| Category | Current | Needed | Gap | Priority |
|----------|---------|--------|-----|----------|
| **Cardiology ECGs** | 84 | 250 (200 MCQ + 50 OSCE) | +166 | HIGH |
| **Respiratory Imaging** | 0 | 250 (200 MCQ + 50 OSCE) | +250 | **CRITICAL** |
| **Hematology Microscopy** | 160 | 50 | -110 | None (surplus) |
| **Dermatology Photos** | 74 | 30 | -44 | None (surplus) |
| **Gastroenterology** | 0 | 50 (future) | +50 | Low |
| **Neurology** | 0 | 50 (future) | +50 | Low |
| **Emergency Medicine** | 0 | 75 (future) | +75 | Medium |

### 4.2 Gap Prioritization

**Priority 1 (CRITICAL - 0% coverage):**
- Respiratory Medicine: 250 items, 0 images → Need 100 images minimum

**Priority 2 (HIGH - 42% coverage):**
- Cardiology: 250 items, 84 images → Need 116 more images for full coverage

**Priority 3 (MEDIUM - Future content):**
- Emergency Medicine: Need 75 images for future MCQs/OSCEs
- Gastroenterology: Need 50 images for future MCQs/OSCEs
- Neurology: Need 50 images for future MCQs/OSCEs

---

## 5. Additional Image Sources (Free/Open-Access)

### 5.1 Recommended Sources

| Source | Specialty Coverage | Image Types | License | Access |
|--------|-------------------|-------------|---------|--------|
| **MedPix** | All specialties | X-rays, CT, MRI, US | Public domain | Free, NIH |
| **OpenI** | Radiology-heavy | CXRs, CT scans | CC-BY, Public | Free, NLM |
| **Radiopaedia** | Radiology | All imaging modalities | CC BY-NC-SA | Free, registration |
| **LITFL (ECG Library)** | Cardiology | ECGs | CC BY-NC-SA | Free |
| **DermNet NZ** | Dermatology | Clinical photos | CC BY-NC-ND | Free |
| **WikiDoc** | General | Mixed | CC-BY-SA | Free |

### 5.2 Respiratory Image Sources (Priority 1)

**MedPix (NIH) - https://medpix.nlm.nih.gov/**
- Comprehensive respiratory case library
- CXRs: Pneumonia, COPD, asthma, PE, lung cancer
- CT scans: ILD, bronchiectasis, lung nodules
- License: Public domain (US government)

**OpenI (NLM) - https://openi.nlm.nih.gov/**
- 3.7 million+ biomedical images
- Strong respiratory imaging collection
- CXRs, CT scans from published research
- License: Varies (mostly CC-BY)

**Radiopaedia - https://radiopaedia.org/**
- Case-based learning with imaging
- Respiratory: Pneumothorax, effusions, masses
- High-quality annotated images
- License: CC BY-NC-SA

**Estimated Download Effort:**
- 100 respiratory images: 8-10 hours
- Includes selection, download, organization, metadata creation

### 5.3 Cardiology Image Sources (Priority 2)

**LITFL ECG Library - https://litfl.com/ecg-library/**
- 200+ ECG examples
- Well-categorized by diagnosis
- Excellent educational annotations
- License: CC BY-NC-SA

**MedPix (NIH) - Cardiology Section**
- ECGs, echocardiograms, angiograms
- Complement existing HEAL ECGs
- License: Public domain

**Estimated Download Effort:**
- 100+ additional cardiology images: 6-8 hours

---

## 6. Image Linking Strategy

### 6.1 Linking Approaches

**Approach 1: Exact Match (Preferred)**
- Match image diagnosis to MCQ/OSCE topic
- Example: "Atrial fibrillation ECG" → MCQ about AF management
- **Pros:** Most educationally valuable, diagnostically accurate
- **Cons:** Requires manual curation, won't cover all MCQs

**Approach 2: Topic-Based Match**
- Match images to broader topic categories
- Example: All "arrhythmia" MCQs → Pool of arrhythmia ECGs
- **Pros:** Higher coverage, less manual work
- **Cons:** May show incorrect diagnosis (e.g., AF ECG on VT question)

**Approach 3: Specialty-Based Random**
- Assign random specialty-appropriate image
- Example: Any cardiology MCQ → Random ECG
- **Pros:** Easy to implement, 100% coverage
- **Cons:** Low educational value, potentially confusing

**Recommended:** Hybrid approach
1. Exact match for interpretation questions (e.g., "What is this ECG rhythm?")
2. Topic-based for management questions (e.g., "How to treat AF?" → Show AF ECG)
3. No image for pure knowledge questions (e.g., "What is the MOA of amiodarone?")

### 6.2 Implementation Plan

**Step 1: Analyze MCQ/OSCE Topics**
```python
# Extract topics from existing MCQs
for mcq in mcqs:
    topic = mcq.get('topic')
    subtopic = mcq.get('subtopic')
    keywords = extract_keywords(mcq.get('question'))
```

**Step 2: Create Topic-to-Image Mapping**
```python
# Map HEAL categories to MCQ topics
topic_image_map = {
    "atrial_fibrillation": ["heal/cardiology/atrial_fibrillation_ECG/*.png"],
    "iron_deficiency_anemia": ["heal/hematology/iron_deficiency_anemia/*.jpg"],
    # ... etc
}
```

**Step 3: Update Database**
```python
# Update MCQ records with image_url
for mcq in mcqs:
    matching_images = find_matching_images(mcq.topic, topic_image_map)
    if matching_images:
        mcq.image_url = select_best_match(matching_images)
        mcq.image_caption = generate_caption(mcq.image_url)
```

**Step 4: Validate**
```python
# Ensure images load correctly
# Check for broken links
# Verify image-topic alignment
```

### 6.3 Database Update Script (Pseudocode)

```python
"""
Script: link_images_to_mcqs.py
Purpose: Link HEAL images to MCQs and OSCEs based on topic matching
"""

import json
import os
from pathlib import Path

def load_heal_metadata():
    """Load HEAL image metadata with categories"""
    with open('data/medical_images/heal/heal_comprehensive_metadata.json') as f:
        return json.load(f)

def create_topic_mapping(heal_metadata):
    """Create topic-to-image mapping"""
    mapping = {}
    for image in heal_metadata['images']:
        filepath = image['filepath']
        category = extract_category_from_path(filepath)
        
        if category not in mapping:
            mapping[category] = []
        mapping[category].append({
            'url': f"/images/heal/{category}/{image['filename']}",
            'caption': image.get('description', ''),
            'source': image.get('details_url', '')
        })
    return mapping

def match_mcq_to_images(mcq, topic_mapping):
    """Find matching images for MCQ based on topic"""
    # Extract keywords from question and topic
    keywords = extract_medical_keywords(mcq)
    
    # Find matching category
    for category, images in topic_mapping.items():
        if any(keyword in category.lower() for keyword in keywords):
            return images[0]  # Return first matching image
    
    return None

def update_mcq_database(mcq_file, topic_mapping):
    """Update MCQ JSON file with image URLs"""
    with open(mcq_file, 'r') as f:
        data = json.load(f)
    
    updated_count = 0
    for mcq in data.get('mcqs', []):
        image_data = match_mcq_to_images(mcq, topic_mapping)
        if image_data:
            mcq['image_url'] = image_data['url']
            mcq['image_caption'] = image_data['caption']
            updated_count += 1
    
    with open(mcq_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Updated {updated_count}/{len(data['mcqs'])} MCQs with images")

# Main execution
if __name__ == '__main__':
    heal_metadata = load_heal_metadata()
    topic_mapping = create_topic_mapping(heal_metadata)
    
    mcq_files = [
        'data/mcqs/week1_regenerated_100_mcqs_with_images.json',
        'data/mcqs/week3_cardiology_200_mcqs_with_images.json',
        'data/mcqs/week3_respiratory_200_mcqs_with_images.json',
    ]
    
    for mcq_file in mcq_files:
        update_mcq_database(mcq_file, topic_mapping)
```

---

## 7. Recommendations & Implementation Plan

### 7.1 Three-Phase Approach

#### **Phase 1: Link Existing Images (QUICK WIN)**
**Timeline:** 4-6 hours  
**Coverage:** 200/725 items (27.6%)

**Tasks:**
1. Create image linking script (2 hours)
2. Build topic-to-image mapping database (1 hour)
3. Update MCQ JSON files with image_url fields (1 hour)
4. Validate image links and alignment (1 hour)
5. Update OSCE supporting_documents field (1 hour)

**Deliverables:**
- `link_images_to_content.py` script
- Updated MCQ JSON files with image_url populated
- Validation report showing coverage by specialty

**Expected Coverage:**
- Cardiology MCQs: 200 → ~150 with images (75%)
- Cardiology OSCEs: 50 → ~40 with images (80%)
- General Medicine MCQs: 100 → ~10 with images (10%, heme/derm only)

---

#### **Phase 2: Download Respiratory Images (HIGH PRIORITY)**
**Timeline:** 8-10 hours  
**Coverage:** 450/725 items (62.1%)

**Tasks:**
1. Research MedPix/OpenI respiratory collections (1 hour)
2. Select 100 high-quality respiratory images:
   - 30 CXRs (pneumonia, pneumothorax, effusion, masses)
   - 25 CT scans (PE, ILD, lung cancer)
   - 20 PFT graphs (asthma, COPD, restrictive patterns)
   - 15 ABG results (respiratory failure)
   - 10 Other (bronchoscopy, HRCT patterns)
3. Download and organize (3-4 hours)
4. Create metadata files (2 hours)
5. Link to respiratory MCQs/OSCEs (2 hours)
6. Validate (1 hour)

**Deliverables:**
- 100 respiratory images organized by condition
- Metadata JSON files
- Updated respiratory MCQ/OSCE files with image links

**Sources:**
- MedPix: https://medpix.nlm.nih.gov/ (primary source)
- OpenI: https://openi.nlm.nih.gov/ (supplementary)
- Radiopaedia: https://radiopaedia.org/ (case studies)

**Expected Coverage:**
- Respiratory MCQs: 200 → 200 with images (100%)
- Respiratory OSCEs: 50 → 50 with images (100%)

---

#### **Phase 3: Download Additional Specialty Images (MEDIUM PRIORITY)**
**Timeline:** 14-18 hours  
**Coverage:** 625/725 items (86.2%)

**Tasks:**

**3A. Additional Cardiology Images (6-8 hours)**
- Target: 100 additional ECGs from LITFL and MedPix
- Fill gaps in existing HEAL collection:
  - LBBB, RBBB variations
  - Complete STEMI/NSTEMI series
  - Electrolyte abnormalities
  - Pericarditis, cardiomyopathy patterns
- Link to remaining cardiology MCQs

**3B. Emergency Medicine Images (6-8 hours)**
- Target: 75 emergency images
  - Trauma X-rays (30): Fractures, pneumothorax, hemothorax
  - Acute abdomen (20): SBO, perforation, appendicitis
  - Head CT (15): Bleeds, stroke, trauma
  - Ultrasound (10): FAST, AAA, DVT
- Link to future emergency medicine MCQs/OSCEs

**3C. Future Specialty Images (2-4 hours)**
- Gastroenterology (25): Endoscopy, abdominal imaging
- Neurology (25): CT/MRI brain, fundoscopy
- Create organized library for future content

**Deliverables:**
- 175 additional medical images across specialties
- Complete metadata and organization
- Image library ready for Phase 2 content generation

---

### 7.2 Success Metrics

| Metric | Baseline | After Phase 1 | After Phase 2 | After Phase 3 | Target |
|--------|----------|---------------|---------------|---------------|--------|
| **Total Images** | 318 | 318 | 418 | 593 | 500+ |
| **MCQs with Images** | 0 | 160 | 360 | 480 | 400+ |
| **OSCEs with Images** | 0 | 40 | 90 | 145 | 100+ |
| **Coverage %** | 0% | 27.6% | 62.1% | 86.2% | >70% |
| **Cardiology Coverage** | 0% | 75% | 75% | 100% | >80% |
| **Respiratory Coverage** | 0% | 0% | 100% | 100% | >80% |

### 7.3 Resource Requirements

**Tools Needed:**
- Python 3.8+ (existing)
- JSON processing libraries (existing)
- Image download scripts (to be created)
- Database update scripts (to be created)

**Data Sources:**
- HEAL images (already downloaded)
- MedPix API or web scraping (Phase 2)
- OpenI API (Phase 2)
- Radiopaedia (manual selection, Phase 2)

**Human Effort:**
- Phase 1: 4-6 hours (mostly scripting)
- Phase 2: 8-10 hours (image curation + scripting)
- Phase 3: 14-18 hours (extensive curation)
- **Total: 26-34 hours**

**Storage Requirements:**
- Current: ~500 MB (318 images)
- After Phase 2: ~800 MB (+100 images)
- After Phase 3: ~1.2 GB (+175 images)
- Recommend: 2 GB storage allocation

---

## 8. Image Quality Standards

### 8.1 Technical Requirements

**Image Resolution:**
- Minimum: 800x600 pixels
- Recommended: 1200x900 pixels
- Maximum: 2000x1500 pixels (to avoid slow loading)

**File Formats:**
- Preferred: PNG (for ECGs, diagrams), JPEG (for photos, radiology)
- Avoid: GIF, BMP, TIFF (large file sizes)

**File Size:**
- Target: <200 KB per image
- Maximum: 500 KB per image
- Use compression for clinical photos

### 8.2 Educational Quality

**Image Clarity:**
- Must be diagnostic quality
- No watermarks obscuring pathology
- Annotations helpful but not required

**Relevance:**
- Image must match question topic
- No misleading images (e.g., AF ECG on VT question)
- Caption must explain what student should look for

**Attribution:**
- Always include source attribution
- Respect CC-BY, CC-BY-SA licenses
- Store license information in metadata

### 8.3 Metadata Standards

Each image must have:
```json
{
  "image_id": "heal_869593",
  "category": "cardiology",
  "subcategory": "atrial_fibrillation_ECG",
  "filepath": "data/medical_images/heal/cardiology/atrial_fibrillation_ECG/heal_869593.png",
  "url": "/images/heal/cardiology/atrial_fibrillation_ECG/heal_869593.png",
  "caption": "ECG showing irregularly irregular rhythm consistent with atrial fibrillation",
  "source": "HEAL - University of Utah",
  "source_url": "https://collections.lib.utah.edu/details?id=869593",
  "license": "Public Domain / Educational Use",
  "keywords": ["atrial fibrillation", "ecg", "arrhythmia", "irregular rhythm"],
  "file_size_kb": 145,
  "dimensions": "1200x800",
  "added_date": "2026-02-03"
}
```

---

## 9. Next Steps (Immediate Actions)

### 9.1 Week 1: Phase 1 Implementation

**Day 1-2: Script Development**
- [ ] Create `link_images_to_content.py` script
- [ ] Build topic-to-image mapping from HEAL metadata
- [ ] Implement keyword extraction for MCQ matching

**Day 3-4: Database Updates**
- [ ] Update week1_regenerated_100_mcqs_with_images.json
- [ ] Update week3_cardiology_200_mcqs_with_images.json
- [ ] Update cardiology_50_osces.json

**Day 5: Validation & Testing**
- [ ] Validate all image URLs load correctly
- [ ] Check image-topic alignment
- [ ] Generate coverage report
- [ ] Test frontend image display (if UI ready)

**Deliverable:** 200/725 items with images (27.6% coverage)

### 9.2 Week 2-3: Phase 2 Implementation

**Week 2: Respiratory Image Collection**
- [ ] Research and select 100 respiratory images from MedPix/OpenI
- [ ] Download and organize by condition
- [ ] Create metadata files

**Week 3: Respiratory Image Linking**
- [ ] Link images to 200 respiratory MCQs
- [ ] Link images to 50 respiratory OSCEs
- [ ] Validate and test

**Deliverable:** 450/725 items with images (62.1% coverage)

### 9.3 Month 2: Phase 3 Implementation

**Week 1-2: Additional Cardiology & Emergency Images**
- [ ] Download 100 additional cardiology ECGs (LITFL, MedPix)
- [ ] Download 75 emergency medicine images
- [ ] Link to existing and future content

**Week 3-4: Future Specialty Preparation**
- [ ] Download 50 GI images
- [ ] Download 50 neuro images
- [ ] Organize library for Phase 2 content generation

**Deliverable:** 625/725 items with images (86.2% coverage)

---

## 10. Appendices

### Appendix A: HEAL Image Categories (Detailed)

**Cardiology ECG Categories (23):**
1. Acute Coronary Syndrome ECG
2. Angina ECG
3. Anterior Wall MI
4. Atrial Fibrillation ECG (5 images)
5. Atrial Flutter ECG (10 images)
6. Bifascicular Block (4 images)
7. Biventricular Hypertrophy
8. Brugada Syndrome
9. First Degree AV Block (2 images)
10. Hyperkalemia ECG
11. Hypokalemia ECG
12. Inferior Wall MI
13. Junctional Tachycardia ECG (4 images)
14. Lateral Wall MI (4 images)
15. Left Atrial Enlargement ECG (5 images)
16. Left Bundle Branch Block
17. Left Ventricular Hypertrophy ECG
18. Long QT Syndrome
19. Non-ST Elevation MI
20. Pacemaker ECG (10 images)
21. Pericarditis ECG
22. Posterior Wall MI (3 images)
23. Premature Atrial Contraction
24. Premature Ventricular Contraction
25. Right Atrial Enlargement ECG (2 images)
26. Right Bundle Branch Block (7 images)
27. Right Ventricular Hypertrophy ECG (2 images)
28. Second Degree AV Block (3 images)
29. Sinus Bradycardia ECG (3 images)
30. Sinus Tachycardia ECG (4 images)
31. ST Elevation MI
32. Supraventricular Tachycardia ECG (2 images)
33. Third Degree AV Block
34. Ventricular Fibrillation ECG (4 images)
35. Ventricular Tachycardia ECG (5 images)

**Hematology Categories (32):**
1. Acute Lymphoblastic Leukemia
2. Acute Myeloid Leukemia (2 images)
3. Acute Promyelocytic Leukemia (5 images)
4. Anemia of Chronic Disease (3 images)
5. Antiphospholipid Syndrome
6. Auer Rods Leukemia (4 images)
7. Blast Differential
8. Blood Smear Abnormal (3 images)
9. Blood Smear Normal (10 images)
10. Bone Marrow Aspirate (10 images)
11. Bone Marrow Biopsy
12. Chronic Lymphocytic Leukemia (9 images)
13. Disseminated Intravascular Coagulation (2 images)
14. Downey Cells (5 images)
15. Elliptocytosis (2 images)
16. Eosinophilia (3 images)
17. Hairy Cell Leukemia (2 images)
18. Hemolytic Anemia (10 images)
19. Hemophagocytosis (3 images)
20. Immature Granulocytes
21. Iron Deficiency Anemia (10 images)
22. Leukocytosis
23. Megaloblastic Anemia (10 images)
24. Multiple Myeloma (10 images)
25. Myelodysplastic Syndrome
26. Myeloproliferative Neoplasm
27. Neutropenia
28. Pernicious Anemia
29. Plasma Cells (10 images)
30. Platelet Morphology
31. Purpura (5 images)
32. Reticulocytes (10 images)
33. Sickle Cell Anemia (4 images)
34. Spherocytosis (2 images)
35. Target Cells (6 images)
36. Thalassemia (9 images)
37. Thrombocytopenia (3 images)
38. Thrombocytosis (3 images)

**Dermatology Categories (15):**
1. Acne Vulgaris (8 images)
2. Alopecia Areata
3. Angioedema
4. Atopic Dermatitis (9 images)
5. Basal Cell Carcinoma (10 images)
6. Bullous Pemphigoid
7. Drug Eruption
8. Erysipelas
9. Impetigo
10. Kaposi Sarcoma
11. Keratoacanthoma
12. Melanoma (4 images)
13. Molluscum Contagiosum (2 images)
14. Nummular Dermatitis (4 images)
15. Pemphigus (2 images)
16. Psoriasis
17. Scabies (10 images)
18. Seborrheic Dermatitis (4 images)
19. Skin Tag
20. Squamous Cell Carcinoma (5 images)
21. Stasis Dermatitis (7 images)
22. Stevens-Johnson Syndrome
23. Urticaria (6 images)
24. Vitiligo
25. Warts

### Appendix B: Free Medical Image Sources (Detailed)

**MedPix (NIH) - https://medpix.nlm.nih.gov/**
- **Owner:** National Library of Medicine (NIH)
- **Content:** 59,000+ medical images across all specialties
- **Specialties:** Radiology, pathology, dermatology, cardiology
- **Image Types:** X-rays, CT, MRI, ultrasound, microscopy, clinical photos
- **License:** Public domain (US government work)
- **API:** Yes (for bulk download)
- **Quality:** High (peer-reviewed, annotated)
- **Best For:** Respiratory (CXRs, CT scans), Emergency (trauma imaging)

**OpenI (NLM) - https://openi.nlm.nih.gov/**
- **Owner:** National Library of Medicine (NIH)
- **Content:** 3.7 million+ biomedical images from PubMed Central
- **Specialties:** All medical specialties
- **Image Types:** Published research images (X-rays, CT, MRI, graphs)
- **License:** Varies (mostly CC-BY, CC-BY-SA)
- **API:** Yes (extensive search API)
- **Quality:** Variable (research quality)
- **Best For:** Respiratory, neurology, gastroenterology

**Radiopaedia - https://radiopaedia.org/**
- **Owner:** Community-driven educational resource
- **Content:** 20,000+ radiology cases
- **Specialties:** Radiology-heavy (all body systems)
- **Image Types:** X-rays, CT, MRI, ultrasound (annotated cases)
- **License:** CC BY-NC-SA 3.0
- **API:** Limited (requires permission)
- **Quality:** Excellent (peer-reviewed, annotated)
- **Best For:** Case-based learning, respiratory, neurology
- **Note:** Requires attribution, non-commercial use only

**LITFL ECG Library - https://litfl.com/ecg-library/**
- **Owner:** Life in the Fast Lane (educational site)
- **Content:** 200+ ECG examples
- **Specialties:** Cardiology (ECG interpretation)
- **Image Types:** ECG tracings (annotated)
- **License:** CC BY-NC-SA 4.0
- **API:** No (manual download)
- **Quality:** Excellent (educational annotations)
- **Best For:** Supplementing existing HEAL cardiology collection
- **Note:** Non-commercial use, attribution required

**DermNet NZ - https://dermnetnz.org/**
- **Owner:** New Zealand Dermatological Society
- **Content:** 23,000+ dermatology images
- **Specialties:** Dermatology only
- **Image Types:** Clinical photos (skin conditions)
- **License:** CC BY-NC-ND 3.0
- **API:** No (manual download)
- **Quality:** Excellent (clinical diagnostic quality)
- **Best For:** Already have 74 HEAL derm images (low priority)
- **Note:** No derivatives allowed (ND license)

**WikiDoc - https://www.wikidoc.org/**
- **Owner:** Community-driven medical encyclopedia
- **Content:** Thousands of medical images
- **Specialties:** All medical specialties
- **Image Types:** Mixed (clinical photos, radiology, microscopy)
- **License:** CC BY-SA 3.0 (mostly)
- **API:** MediaWiki API (bulk download possible)
- **Quality:** Variable (community-contributed)
- **Best For:** Supplementary images when other sources unavailable

### Appendix C: Linking Script Template

```python
#!/usr/bin/env python3
"""
Image Linking Script for irStudy Medical Education Platform
Links HEAL medical images to MCQs and OSCEs based on topic matching

Usage:
    python link_images_to_content.py --phase 1
    python link_images_to_content.py --specialty cardiology
    python link_images_to_content.py --validate

Author: irStudy Development Team
Date: 2026-02-04
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class ImageMetadata:
    """Represents a medical image with metadata"""
    image_id: str
    filepath: str
    url: str
    category: str
    subcategory: str
    caption: str
    source: str
    keywords: List[str]


class ImageLinker:
    """Links medical images to MCQs and OSCEs based on topic matching"""
    
    def __init__(self, heal_metadata_path: str):
        self.heal_metadata_path = Path(heal_metadata_path)
        self.images: Dict[str, List[ImageMetadata]] = defaultdict(list)
        self.load_heal_metadata()
    
    def load_heal_metadata(self):
        """Load HEAL image metadata and organize by category"""
        with open(self.heal_metadata_path, 'r') as f:
            data = json.load(f)
        
        for img in data.get('images', []):
            filepath = Path(img['filepath'])
            parts = filepath.parts
            
            # Extract category and subcategory from path
            # e.g., data/medical_images/heal/cardiology/atrial_fibrillation_ECG/heal_869593.png
            if len(parts) >= 6:
                specialty = parts[4]  # cardiology, hematology, dermatology
                condition = parts[5]  # atrial_fibrillation_ECG
                
                metadata = ImageMetadata(
                    image_id=img['file_id'],
                    filepath=str(filepath),
                    url=f"/images/heal/{specialty}/{condition}/{filepath.name}",
                    category=specialty,
                    subcategory=condition,
                    caption=img.get('description', ''),
                    source=img.get('details_url', 'HEAL'),
                    keywords=self.extract_keywords(condition)
                )
                
                self.images[condition].append(metadata)
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract medical keywords from text"""
        # Convert underscores to spaces, lowercase
        text = text.replace('_', ' ').lower()
        
        # Remove common suffixes
        text = text.replace(' ecg', '').replace(' ekg', '')
        
        # Split into words
        words = text.split()
        
        return words
    
    def find_matching_images(self, mcq: Dict) -> Optional[ImageMetadata]:
        """Find the best matching image for an MCQ"""
        # Extract keywords from MCQ
        question = mcq.get('question', '').lower()
        topic = mcq.get('topic', '').lower()
        subtopic = mcq.get('subtopic', '').lower()
        
        # Combine all text for matching
        search_text = f"{question} {topic} {subtopic}"
        
        # Look for exact matches in subcategories
        for subcategory, images in self.images.items():
            keywords = self.extract_keywords(subcategory)
            
            # Check if any keyword appears in search text
            if any(keyword in search_text for keyword in keywords):
                # Return first image from matched category
                return images[0] if images else None
        
        return None
    
    def update_mcq_file(self, mcq_filepath: str, dry_run: bool = False):
        """Update MCQ JSON file with image URLs"""
        filepath = Path(mcq_filepath)
        
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        mcqs = data.get('mcqs', [])
        updated_count = 0
        
        for mcq in mcqs:
            # Skip if already has image
            if mcq.get('image_url'):
                continue
            
            # Find matching image
            image = self.find_matching_images(mcq)
            
            if image:
                mcq['image_url'] = image.url
                mcq['image_caption'] = image.caption
                mcq['image_source'] = image.source
                updated_count += 1
        
        if not dry_run:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        
        print(f"{'[DRY RUN] ' if dry_run else ''}Updated {updated_count}/{len(mcqs)} MCQs in {filepath.name}")
        
        return updated_count
    
    def generate_coverage_report(self, mcq_files: List[str]):
        """Generate image coverage report"""
        print("\n" + "=" * 80)
        print("IMAGE COVERAGE REPORT")
        print("=" * 80)
        
        total_mcqs = 0
        total_with_images = 0
        
        for mcq_file in mcq_files:
            with open(mcq_file, 'r') as f:
                data = json.load(f)
            
            mcqs = data.get('mcqs', [])
            with_images = sum(1 for mcq in mcqs if mcq.get('image_url'))
            
            total_mcqs += len(mcqs)
            total_with_images += with_images
            
            coverage = (with_images / len(mcqs) * 100) if mcqs else 0
            
            print(f"\n{Path(mcq_file).name}:")
            print(f"  Total MCQs: {len(mcqs)}")
            print(f"  With Images: {with_images}")
            print(f"  Coverage: {coverage:.1f}%")
        
        overall_coverage = (total_with_images / total_mcqs * 100) if total_mcqs else 0
        
        print(f"\n{'=' * 80}")
        print(f"OVERALL: {total_with_images}/{total_mcqs} MCQs with images ({overall_coverage:.1f}%)")
        print(f"{'=' * 80}\n")


def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Link medical images to MCQs and OSCEs')
    parser.add_argument('--heal-metadata', default='data/medical_images/heal/heal_comprehensive_metadata.json')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without updating files')
    parser.add_argument('--validate', action='store_true', help='Generate coverage report only')
    
    args = parser.parse_args()
    
    # Initialize linker
    linker = ImageLinker(args.heal_metadata)
    
    # MCQ files to update
    mcq_files = [
        'data/mcqs/week1_regenerated_100_mcqs_with_images.json',
        'data/mcqs/week3_cardiology_200_mcqs_with_images.json',
        'data/mcqs/week3_respiratory_200_mcqs_with_images.json',
    ]
    
    if args.validate:
        # Just generate report
        linker.generate_coverage_report(mcq_files)
    else:
        # Update files
        print(f"{'DRY RUN MODE - No files will be modified' if args.dry_run else 'UPDATING MCQ FILES'}\n")
        
        for mcq_file in mcq_files:
            linker.update_mcq_file(mcq_file, dry_run=args.dry_run)
        
        # Generate final report
        print()
        linker.generate_coverage_report(mcq_files)


if __name__ == '__main__':
    main()
```

---

## Summary & Conclusion

### Current State
- **318 high-quality medical images** downloaded from HEAL
- **0% coverage** (images not yet linked to content)
- **Database schema ready** for image integration

### Quick Win Opportunity
- **Phase 1 (4-6 hours):** Link existing 318 images → 27.6% coverage
- **Immediate value:** Cardiology MCQs/OSCEs fully supported

### Full Coverage Path
- **Phase 2 (8-10 hours):** Add 100 respiratory images → 62.1% coverage
- **Phase 3 (14-18 hours):** Add 175 specialty images → 86.2% coverage
- **Total investment:** 26-34 hours for near-complete coverage

### Recommendation
**Proceed with Phase 1 immediately.** The quick win of linking existing images will provide immediate value to cardiology content while we assess whether Phase 2/3 are necessary based on user feedback and content usage analytics.

---

**Document Version:** 1.0  
**Last Updated:** 2026-02-04  
**Next Review:** After Phase 1 completion
