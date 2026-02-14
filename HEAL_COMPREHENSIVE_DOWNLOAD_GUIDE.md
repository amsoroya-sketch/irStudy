# HEAL Comprehensive Download Guide

**Status:** ✅ Ready to Use
**Created:** 2026-02-03
**Based on:** HEAL_TOPIC_ANALYSIS.md (4,572 items analyzed)

---

## Overview

This comprehensive downloader organizes HEAL images by **specialty > topic** with configurable delays and phase-based downloading.

### What's New

1. **Comprehensive Topic Coverage**
   - 250+ specific medical topics identified from HEAL analysis
   - Organized by 9 specialties with priority levels (P0, P1, P2)

2. **Separate Folder Organization**
   - Each topic downloads to its own folder
   - Example: `hematology/acute_myeloid_leukemia/`, `hematology/sickle_cell_anemia/`

3. **Configurable Delays**
   - Image delay: 2s between downloads (respectful to server)
   - Topic delay: 5s between topics
   - Can disable for testing (`--no-delay`)

4. **Phase-Based Downloading**
   - Phase 1 (P0): High-priority (~300-400 images, 1-2 hours)
   - Phase 2 (P1): Medium-priority (~200-300 images, 1-1.5 hours)
   - Phase 3 (P2): Low-priority (~50-100 images, 30 min)

---

## Quick Start

### Phase 1: High-Priority Specialties (Recommended First)

```bash
./download_heal_comprehensive.sh --phase 1
```

**What it downloads:**
- ✅ Hematology: 60 topics (leukemia, anemia, coagulation, bone marrow)
- ✅ Dermatology: 35 topics (skin cancers, dermatitis, infections, acne)
- ✅ Cardiology/ECG: 35 topics (arrhythmias, MI, blocks, hypertrophy)

**Total:** ~300-400 images in 1-2 hours

### Phase 2: Medium-Priority Specialties

```bash
./download_heal_comprehensive.sh --phase 2
```

**What it downloads:**
- ✅ Anatomy: 42 topics (cardiovascular, neuro, musculoskeletal)
- ✅ Bone/Marrow: 14 topics (bone marrow analysis, histology)
- ✅ Respiratory: 10 topics (pneumonia, COPD, ILD)
- ✅ Pediatrics: 10 topics (pediatric conditions)
- ✅ Pathology: 20 topics (tumors, inflammation, organ pathology)

**Total:** ~200-300 images in 1-1.5 hours

### Phase 3: Low-Priority Specialties

```bash
./download_heal_comprehensive.sh --phase 3
```

**What it downloads:**
- ✅ Gastrointestinal: 8 topics (ulcer, IBD, hepatitis)
- ✅ Infectious Disease: 4 topics (mononucleosis, sepsis)

**Total:** ~50-100 images in 30 minutes

### All Phases (Complete Download)

```bash
./download_heal_comprehensive.sh --phase all
```

**Total:** ~550-800 images in 3-4 hours

---

## Detailed Topic Coverage

### Phase 1 Specialties (P0)

#### 1. Hematology (60 topics, 150 images recommended)

**Leukemia (10 topics):**
- acute myeloid leukemia
- acute lymphoblastic leukemia
- chronic myeloid leukemia
- chronic lymphocytic leukemia
- hairy cell leukemia
- acute promyelocytic leukemia
- myelodysplastic syndrome
- myeloproliferative neoplasm
- auer rods leukemia
- blast cells leukemia

**Anemia (8 topics):**
- iron deficiency anemia
- megaloblastic anemia
- sickle cell anemia
- thalassemia
- hemolytic anemia
- aplastic anemia
- anemia chronic disease
- pernicious anemia

**Red Cell Disorders (5 topics):**
- spherocytosis
- elliptocytosis
- target cells
- schistocytes
- rouleaux formation

**White Cell Disorders (5 topics):**
- neutropenia
- leukocytosis
- lymphocytosis
- monocytosis
- eosinophilia

**Coagulation (8 topics):**
- disseminated intravascular coagulation
- thrombocytopenia
- thrombocytosis
- von willebrand disease
- hemophilia
- purpura
- antiphospholipid syndrome
- heparin induced thrombocytopenia

**Bone Marrow (6 topics):**
- bone marrow aspirate
- bone marrow biopsy
- multiple myeloma
- plasma cells
- hemophagocytosis
- bone marrow hypoplasia

**Blood Smear Morphology (8 topics):**
- blood smear normal
- blood smear abnormal
- atypical lymphocytes
- downey cells
- immature granulocytes
- blast differential
- reticulocytes
- platelet morphology

**Total:** 60 topics × 2-3 images = ~150 images

---

#### 2. Dermatology (35 topics, 75 images recommended)

**Skin Cancers (5 topics):**
- melanoma
- basal cell carcinoma
- squamous cell carcinoma
- keratoacanthoma
- kaposi sarcoma

**Inflammatory (8 topics):**
- atopic dermatitis
- contact dermatitis
- seborrheic dermatitis
- nummular dermatitis
- stasis dermatitis
- psoriasis
- lichen planus
- pityriasis rosea

**Infections (6 topics):**
- cellulitis
- erysipelas
- impetigo
- herpes zoster
- herpes simplex
- fungal infection skin

**Allergic (4 topics):**
- urticaria
- angioedema
- drug eruption
- stevens johnson syndrome

**Acne/Rosacea (3 topics):**
- acne vulgaris
- acne rosacea
- perioral dermatitis

**Autoimmune (4 topics):**
- vitiligo
- alopecia areata
- pemphigus
- bullous pemphigoid

**Other (5 topics):**
- scabies
- molluscum contagiosum
- warts
- seborrheic keratosis
- skin tag

**Total:** 35 topics × 2 images = ~75 images

---

#### 3. Cardiology/ECG (35 topics, 75 images recommended)

**Arrhythmias (10 topics):**
- atrial fibrillation ECG
- atrial flutter ECG
- supraventricular tachycardia ECG
- ventricular tachycardia ECG
- ventricular fibrillation ECG
- junctional tachycardia ECG
- sinus tachycardia ECG
- sinus bradycardia ECG
- premature atrial contraction
- premature ventricular contraction

**Conduction Blocks (6 topics):**
- left bundle branch block
- right bundle branch block
- first degree AV block
- second degree AV block
- third degree AV block
- bifascicular block

**Ischemia/MI (8 topics):**
- ST elevation myocardial infarction
- non ST elevation myocardial infarction
- anterior wall MI
- inferior wall MI
- lateral wall MI
- posterior wall MI
- acute coronary syndrome ECG
- angina ECG

**Hypertrophy/Enlargement (5 topics):**
- left ventricular hypertrophy ECG
- right ventricular hypertrophy ECG
- left atrial enlargement ECG
- right atrial enlargement ECG
- biventricular hypertrophy

**Other (6 topics):**
- pacemaker ECG
- pericarditis ECG
- hyperkalemia ECG
- hypokalemia ECG
- long QT syndrome
- brugada syndrome

**Total:** 35 topics × 2 images = ~75 images

---

## Usage Examples

### 1. Quick Test (5 images per topic, no delays)

```bash
./download_heal_comprehensive.sh \
    --phase 1 \
    --images-per-topic 5 \
    --no-delay \
    --show-browser
```

**Time:** 15-20 minutes
**Images:** ~90-100 images
**Use case:** Test the system, verify setup

---

### 2. Production Download (Phase 1 only)

```bash
./download_heal_comprehensive.sh \
    --phase 1 \
    --images-per-topic 10
```

**Time:** 1-2 hours
**Images:** ~300-400 images
**Use case:** Get highest-priority medical images quickly

---

### 3. Complete Download (All phases)

```bash
./download_heal_comprehensive.sh \
    --phase all \
    --images-per-topic 10
```

**Time:** 3-4 hours
**Images:** ~550-800 images
**Use case:** Comprehensive HEAL integration

---

### 4. Custom Specialties Only

```bash
./download_heal_comprehensive.sh \
    --specialties hematology cardiology \
    --images-per-topic 15
```

**Time:** 1 hour
**Images:** ~140 images (60 hematology topics + 35 cardiology topics) × 15
**Use case:** Focus on specific AMC weaknesses

---

### 5. High-Volume Download (More images per topic)

```bash
./download_heal_comprehensive.sh \
    --phase 1 \
    --images-per-topic 20
```

**Time:** 2-3 hours
**Images:** ~600-800 images
**Use case:** Build large image database for hematology/dermatology/cardiology

---

### 6. Fast Download (Minimal delays)

```bash
./download_heal_comprehensive.sh \
    --phase 2 \
    --images-per-topic 10 \
    --image-delay 0.5 \
    --topic-delay 2
```

**Time:** 40 minutes (instead of 1-1.5 hours)
**Images:** ~200-300 images
**Use case:** Faster download with some server respect

---

## Output Structure

```
data/medical_images/heal/
├── hematology/
│   ├── acute_myeloid_leukemia/
│   │   ├── heal_123456.jpg
│   │   ├── heal_123457.jpg
│   │   └── acute_myeloid_leukemia_metadata.json
│   ├── sickle_cell_anemia/
│   │   ├── heal_234567.jpg
│   │   └── sickle_cell_anemia_metadata.json
│   ├── ...
│   └── hematology_summary.json
│
├── dermatology/
│   ├── melanoma/
│   │   ├── heal_345678.jpg
│   │   └── melanoma_metadata.json
│   ├── psoriasis/
│   │   ├── heal_456789.jpg
│   │   └── psoriasis_metadata.json
│   ├── ...
│   └── dermatology_summary.json
│
├── cardiology/
│   ├── atrial_fibrillation_ECG/
│   │   ├── heal_567890.jpg
│   │   └── atrial_fibrillation_ECG_metadata.json
│   ├── ST_elevation_myocardial_infarction/
│   │   ├── heal_678901.jpg
│   │   └── ST_elevation_myocardial_infarction_metadata.json
│   ├── ...
│   └── cardiology_summary.json
│
└── heal_comprehensive_metadata.json (all downloads combined)
```

---

## Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `--phase` | Required | Download phase (1, 2, 3, all) |
| `--specialties` | - | Custom specialty list (overrides phase) |
| `--images-per-topic` | 10 | Max images per topic |
| `--output` | `data/medical_images/heal` | Output directory |
| `--image-delay` | 2.0 | Seconds between images |
| `--topic-delay` | 5.0 | Seconds between topics |
| `--no-delay` | False | Disable all delays (faster) |
| `--show-browser` | False | Show browser window (debugging) |

---

## Time & Resource Estimates

### Phase 1 (P0 - High Priority)

| Metric | Value |
|--------|-------|
| Specialties | 3 (hematology, dermatology, cardiology) |
| Topics | 130 |
| Images (10/topic) | 300-400 |
| Time (2s/image, 5s/topic) | 1-2 hours |
| Storage | ~100-150 MB |

### Phase 2 (P1 - Medium Priority)

| Metric | Value |
|--------|-------|
| Specialties | 5 (anatomy, bone_marrow, respiratory, pediatrics, pathology) |
| Topics | 96 |
| Images (10/topic) | 200-300 |
| Time | 1-1.5 hours |
| Storage | ~60-100 MB |

### Phase 3 (P2 - Low Priority)

| Metric | Value |
|--------|-------|
| Specialties | 2 (gastrointestinal, infectious_disease) |
| Topics | 12 |
| Images (10/topic) | 50-100 |
| Time | 30 minutes |
| Storage | ~20-30 MB |

### Complete Download (All Phases)

| Metric | Value |
|--------|-------|
| Specialties | 10 |
| Topics | 238 |
| Images (10/topic) | 550-800 |
| Time | 3-4 hours |
| Storage | ~180-280 MB |

---

## Integration with Existing System

### 1. After Download Complete

```bash
# View downloaded structure
tree -L 3 data/medical_images/heal/ | head -50

# Count images
find data/medical_images/heal/ -name "*.jpg" | wc -l

# Check metadata
cat data/medical_images/heal/heal_comprehensive_metadata.json | jq '.total_images'
```

### 2. Process Metadata

```bash
python3 scripts/process_image_metadata.py \
    --source data/medical_images/heal \
    --output data/heal_processed_metadata.json
```

### 3. Enrich with Citations

```bash
python3 scripts/enrich_heal_metadata.py \
    --metadata data/heal_processed_metadata.json
```

### 4. Upload to CDN

```bash
# Set credentials
export R2_ENDPOINT_URL="https://<account-id>.r2.cloudflarestorage.com"
export R2_ACCESS_KEY_ID="<your-key>"
export R2_SECRET_ACCESS_KEY="<your-secret>"

# Upload
python3 scripts/upload_to_cdn.py \
    --source data/medical_images/heal \
    --bucket irstudy-medical-images \
    --metadata data/heal_processed_metadata.json
```

### 5. Index in Database

```bash
export DATABASE_URL="postgresql://user:pass@localhost/irstudy"

python3 scripts/index_images.py \
    --metadata data/heal_processed_metadata.json
```

---

## Recommended Strategy

### For Time-Constrained Users (1-2 hours available)

```bash
# Download only Phase 1 (highest-priority)
./download_heal_comprehensive.sh --phase 1
```

This gives you:
- ✅ Exceptional hematology coverage (blood smears, bone marrow)
- ✅ Excellent dermatology coverage (skin lesions)
- ✅ Comprehensive ECG library (arrhythmias, MI, blocks)

---

### For Complete Coverage (3-4 hours available)

```bash
# Download all phases
./download_heal_comprehensive.sh --phase all
```

This gives you:
- ✅ All high-priority content (Phase 1)
- ✅ Anatomy, respiratory, pathology (Phase 2)
- ✅ GI and infectious disease (Phase 3)
- ✅ 550-800 images across 238 medical topics

---

### For Targeted Exam Prep

```bash
# Download only your weak areas
./download_heal_comprehensive.sh \
    --specialties hematology dermatology \
    --images-per-topic 15
```

---

## Troubleshooting

### No results found for specific topics

Some topics may have zero items in HEAL. The script will show:
```
Topic: neurology stroke
  ⚠ No results found
```

This is expected - HEAL has gaps in coverage (see HEAL_TOPIC_ANALYSIS.md).

### Download too slow

Reduce delays:
```bash
./download_heal_comprehensive.sh \
    --phase 1 \
    --image-delay 0.5 \
    --topic-delay 1
```

Or disable completely for testing:
```bash
./download_heal_comprehensive.sh \
    --phase 1 \
    --images-per-topic 5 \
    --no-delay
```

### Browser launch failed

Install system dependencies:
```bash
sudo apt-get install -y libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 \
    libxrandr2 libgbm1 libasound2
```

---

## Next Steps

1. **Run Phase 1** (high-priority, 1-2 hours)
2. **Review downloaded images** (verify quality)
3. **Run Phase 2** (if time allows, 1-1.5 hours)
4. **Process and integrate** (metadata, CDN, database)
5. **Fill gaps** with MedPix/Radiopaedia for missing specialties

---

**Ready to start!** Choose your phase and run the download.

**Recommended first command:**
```bash
./download_heal_comprehensive.sh --phase 1
```

This downloads the most valuable 300-400 images in 1-2 hours.
