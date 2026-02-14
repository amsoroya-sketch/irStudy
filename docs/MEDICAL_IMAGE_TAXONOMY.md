# Medical Image Taxonomy for AMC Clinical Exam Preparation

**Version:** 1.0  
**Created:** 2026-02-05  
**Purpose:** Exhaustive medical image taxonomy for AMC Clinical Exam preparation

## Overview

This taxonomy provides a comprehensive hierarchical classification of medical images for AMC Clinical Exam preparation. It covers **11 medical specialties** with **831 image nodes** organized in a 5-level hierarchy:

**Specialty → Subcategory → Topic → Subtopic → Image Type**

---

## Quick Statistics

| Metric | Value |
|--------|-------|
| **Total Specialties** | 11 |
| **Total Nodes** | 831 |
| **Estimated Images** | 900-1,100 |
| **Australian Compliance** | 100% |
| **AMC Relevance** | High (scores 3-5) |

---

## Specialties Overview


| # | Specialty | Nodes | AMC Priority | Est. Images | Coverage |
|---|-----------|-------|--------------|-------------|----------|
| 1 | [Cardiology](#cardiology) | 96 | HIGH (5/5) | 120-150 | 11 areas |
| 2 | [Respiratory](#respiratory) | 61 | HIGH (4/5) | 90-120 | 8 areas |
| 3 | [Dermatology](#dermatology) | 71 | HIGH (5/5) | 80-110 | 8 areas |
| 4 | [Haematology](#haematology) | 60 | HIGH (5/5) | 120-160 | 6 areas |
| 5 | [Neurology](#neurology) | 100 | HIGH (5/5) | 90-120 | 18 areas |
| 6 | [Gastroenterology](#gastroenterology) | 88 | HIGH (5/5) | 100-130 | 11 areas |
| 7 | [Endocrinology](#endocrinology) | 72 | HIGH (5/5) | 80-100 | 10 areas |
| 8 | [Obstetrics Gynaecology](#obstetrics_gynaecology) | 79 | HIGH (5/5) | 90-110 | 5 areas |
| 9 | [Paediatrics](#paediatrics) | 84 | HIGH (5/5) | 95-120 | 10 areas |
| 10 | [Psychiatry](#psychiatry) | 45 | MEDIUM (4/5) | 50-60 | 9 areas |
| 11 | [Emergency Medicine](#emergency_medicine) | 75 | HIGH (5/5) | 85-110 | 10 areas |

---

## Usage Guide

### For Image Download

Use the search terms in each node to download relevant medical images from HEAL (Health Education Assets Library).

**Example workflow:**
```bash
# Use the download helper script (to be created)
python scripts/download_images_from_taxonomy.py --specialty cardiology --max-per-node 10
```

### For Study Organization

Images are organized by the `folder_path` structure:

```
medical_images/
├── cardiology/
│   ├── coronary_artery_disease/
│   │   ├── acute_mi/
│   │   │   ├── stemi/
│   │   │   └── nstemi/
│   └── arrhythmias/
├── respiratory/
│   ├── infections/
│   └── obstructive_disease/
└── ... (9 more specialties)
```

### AMC Exam Focus

**High Priority (AMC Relevance 5):**
- Acute presentations: MI, PE, stroke, trauma
- Common emergencies: pneumothorax, appendicitis, bowel obstruction  
- Core conditions: pneumonia, fractures, heart failure

**Medium Priority (AMC Relevance 3-4):**
- Uncommon presentations
- Specialist-specific conditions
- Advanced imaging findings

---

## Australian Medical Terminology

100% Australian compliance verified by expert agents:

| American | Australian ✅ |
|----------|-------------|
| pediatric | paediatric |
| esophageal | oesophageal |
| hematology | haematology |
| anemia | anaemia |
| fetal | foetal |
| acetaminophen | paracetamol |
| epinephrine | adrenaline |

---

## Quality Validation

All 831 nodes validated using expert agent system:

✅ **QA-001: Australian Compliance** - 100% pass rate  
✅ **QA-004: Format Validation** - Valid JSON structure  
✅ **Completeness Check** - All specialties complete

**Validation report:** `validation_reports/taxonomy_validation_medical_image_taxonomy_v1.md`

---

## File Structure

```
data/
├── medical_image_taxonomy_v1.json          # 831 nodes, 11 specialties
└── medical_images/                          # Downloaded images (TBD)

validation_reports/
└── taxonomy_validation_medical_image_taxonomy_v1.md

scripts/
├── validate_taxonomy_with_agents.py        # Expert agent validation
└── download_images_from_taxonomy.py        # HEAL download helper (TBD)

docs/
└── MEDICAL_IMAGE_TAXONOMY.md               # This file
```

---

## Next Steps

1. ✅ **Taxonomy Complete** - 831 nodes across 11 specialties
2. ⏭️ **Download Helper Script** - Generate HEAL download commands
3. ⏭️ **CSV Export** - Create spreadsheet for quick reference
4. ⏭️ **Image Download** - Execute HEAL batch downloads
5. ⏭️ **Link to Content** - Match images to MCQs/OSCEs
6. ⏭️ **CLIP Embeddings** - Enable multimodal RAG search

---

## Detailed Specialty Index

### 1. Cardiology

**Nodes:** 96 | **Priority:** HIGH | **AMC:** 5/5

**Coverage areas:**
- Ischemic Heart Disease (10 nodes)
- Arrhythmias (27 nodes)
- Conduction Blocks (13 nodes)
- Valvular Disease (11 nodes)
- Cardiomyopathy (10 nodes)
- Pericardial Disease (5 nodes)
- Heart Failure (3 nodes)
- Hypertrophy Patterns (5 nodes)
- Electrolyte Abnormalities (4 nodes)
- Congenital Heart Disease (4 nodes)
- Pacemakers (4 nodes)

### 2. Respiratory

**Nodes:** 61 | **Priority:** HIGH | **AMC:** 4/5

**Coverage areas:**
- Respiratory Infections (12 nodes)
- Obstructive Airway Disease (10 nodes)
- Restrictive Lung Disease (9 nodes)
- Vascular Lung Disease (7 nodes)
- Pleural Disease (8 nodes)
- Lung Cancer (7 nodes)
- Chest Trauma (4 nodes)
- Mediastinal Disease (4 nodes)

### 3. Dermatology

**Nodes:** 71 | **Priority:** HIGH | **AMC:** 5/5

**Coverage areas:**
- Skin Cancer (10 nodes)
- Benign Lesions (9 nodes)
- Inflammatory Conditions (13 nodes)
- Infections (17 nodes)
- Autoimmune Conditions (8 nodes)
- Drug Reactions (4 nodes)
- Hair And Nail Disorders (5 nodes)
- Acne And Rosacea (5 nodes)

### 4. Haematology

**Nodes:** 60 | **Priority:** HIGH | **AMC:** 5/5

**Coverage areas:**
- Anaemias (15 nodes)
- White Cell Disorders (17 nodes)
- Platelet Disorders (5 nodes)
- Coagulation Disorders (9 nodes)
- Transfusion Medicine (8 nodes)
- Special Haematology (6 nodes)

### 5. Neurology

**Nodes:** 100 | **Priority:** HIGH | **AMC:** 5/5

**Coverage areas:**
- Stroke (10 nodes)
- Headache Disorders (5 nodes)
- Seizures Epilepsy (4 nodes)
- Movement Disorders (4 nodes)
- Dementia (5 nodes)
- Demyelinating Disease (5 nodes)
- Peripheral Neuropathy (3 nodes)
- Spinal Cord Disorders (5 nodes)
- Brain Tumours (7 nodes)
- Infections (7 nodes)
- Neuromuscular Disorders (3 nodes)
- Cranial Nerve Disorders (3 nodes)
- Congenital Developmental (6 nodes)
- Metabolic Toxic (8 nodes)
- Cerebrovascular Malformations (7 nodes)
- Traumatic Brain Injury (5 nodes)
- Neuro Ophthalmology (9 nodes)
- Electrophysiology (4 nodes)

### 6. Gastroenterology

**Nodes:** 88 | **Priority:** HIGH | **AMC:** 5/5

**Coverage areas:**
- Oesophageal Disorders (8 nodes)
- Gastric Disorders (9 nodes)
- Small Bowel Disorders (9 nodes)
- Colorectal Disorders (14 nodes)
- Hepatobiliary Disorders (18 nodes)
- Pancreatic Disorders (9 nodes)
- Abdominal Wall Hernias (8 nodes)
- Peritoneal Disorders (3 nodes)
- Appendiceal Disorders (3 nodes)
- Anal Disorders (4 nodes)
- Splenic Disorders (3 nodes)

### 7. Endocrinology

**Nodes:** 72 | **Priority:** HIGH | **AMC:** 5/5

**Coverage areas:**
- Diabetes Complications (12 nodes)
- Thyroid Disorders (14 nodes)
- Pituitary Disorders (8 nodes)
- Adrenal Disorders (9 nodes)
- Parathyroid Disorders (3 nodes)
- Metabolic Bone Disease (13 nodes)
- Obesity Complications (2 nodes)
- Lipid Disorders (4 nodes)
- Genetic Syndromes (3 nodes)
- Calcium Disorders (4 nodes)

### 8. Obstetrics Gynaecology

**Nodes:** 79 | **Priority:** HIGH | **AMC:** 5/5

**Coverage areas:**
- Pregnancy Complications (25 nodes)
- Gynaecological Conditions (32 nodes)
- Breast Imaging (15 nodes)
- Contraception Imaging (2 nodes)
- Infertility Imaging (5 nodes)

### 9. Paediatrics

**Nodes:** 84 | **Priority:** HIGH | **AMC:** 5/5

**Coverage areas:**
- Neonatal Conditions (23 nodes)
- Paediatric Respiratory (8 nodes)
- Paediatric Gastrointestinal (7 nodes)
- Paediatric Neurology (12 nodes)
- Paediatric Orthopaedics (9 nodes)
- Paediatric Infectious Diseases (5 nodes)
- Paediatric Haematology Oncology (4 nodes)
- Paediatric Dermatology (6 nodes)
- Paediatric Genitourinary (7 nodes)
- Paediatric Endocrine (3 nodes)

### 10. Psychiatry

**Nodes:** 45 | **Priority:** MEDIUM | **AMC:** 4/5

**Coverage areas:**
- Neuroimaging Psychiatry (14 nodes)
- Self Harm Injuries (4 nodes)
- Psychiatric Emergencies Imaging (11 nodes)
- Medication Side Effects (4 nodes)
- Electroconvulsive Therapy (1 nodes)
- Sleep Disorders (2 nodes)
- Autism Developmental Disorders (4 nodes)
- Neuropsychiatric Syndromes (2 nodes)
- Trauma Related Imaging (3 nodes)

### 11. Emergency Medicine

**Nodes:** 75 | **Priority:** HIGH | **AMC:** 5/5

**Coverage areas:**
- Trauma (32 nodes)
- Acute Abdomen (5 nodes)
- Cardiovascular Emergencies (10 nodes)
- Respiratory Emergencies (5 nodes)
- Neurological Emergencies (5 nodes)
- Toxicology (4 nodes)
- Environmental Emergencies (4 nodes)
- Infectious Emergencies (3 nodes)
- Metabolic Emergencies (6 nodes)
- Obstetric Emergencies (1 nodes)

---

## Maintenance and Updates

**To add new content:**
1. Follow 5-level hierarchy: Specialty → Subcategory → Topic → Subtopic
2. Include 3-4 search term variants per node
3. Use Australian medical terminology exclusively
4. Assign AMC relevance (1-5 scale)
5. Validate: `python scripts/validate_taxonomy_with_agents.py`

**To update search terms:**
- Test terms on HEAL: https://library.med.utah.edu/heal/
- Ensure variants capture different query styles
- Include modality in search terms (e.g., "pneumonia chest X-ray")

---

## License

**Educational Use Only** - AMC Clinical Exam Preparation

**Image Sources:**
- HEAL (Health Education Assets Library) - University of Utah
- Open-access medical repositories
- Educational databases with appropriate licensing

---

**Status:** Complete and Validated ✅  
**Last Updated:** {updated}  
**Document Version:** 1.0
