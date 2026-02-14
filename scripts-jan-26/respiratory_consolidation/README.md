# Week 3 Respiratory MCQ Consolidation Scripts

**Purpose**: Consolidate all Week 3 Respiratory MCQ batch files into the main `week3_respiratory_200_mcqs.json` file.

**Total Batches**: 8 batches covering MCQs 001-200

---

## Batch Structure

**Batch 1 (001-025)**: Asthma & Early COPD
- Script: `consolidate_batch_001_025.py`
- Source: WEEK3_RESP_001_025_ASTHMA_COPD.py

**Batch 2 (026-050)**: COPD Management & Bronchiectasis
- Script: `consolidate_batch_026_050.py`
- Sources: 2 files (026-038, 039-050)

**Batch 3 (051-075)**: Pneumonia & TB
- Script: `consolidate_batch_051_075.py`
- Sources: 2 files (051-063, 064-075)

**Batch 4 (076-100)**: TB Complications, Vaccinations & PE Diagnosis
- Script: `consolidate_batch_076_100.py`
- Sources: 2 files (076-088, 089-100)

**Batch 5 (101-125)**: PE/DVT Management & ILD Introduction
- Script: `consolidate_batch_101_125.py`
- Sources: Multiple files covering all 25 MCQs

**Batch 6 (126-150)**: Advanced ILD & Respiratory Failure
- Script: `consolidate_batch_126_150.py`
- Sources: 2 files (126-138, 139-150)

**Batch 7 (151-175)**: Ventilation & Pleural Disease
- Script: `consolidate_batch_151_175.py`
- Sources: 2 files (151-163, 164-175)

**Batch 8 (176-200)**: Lung Cancer & Pulmonary Diagnostics
- Script: `consolidate_batch_176_200.py`
- Sources: 2 files (176-188, 189-200)

---

## Execution Order

Run scripts sequentially:

```bash
cd /home/dev/Development/irStudy/scripts-jan-26/respiratory_consolidation

python3 consolidate_batch_001_025.py  # Batch 1
python3 consolidate_batch_026_050.py  # Batch 2
python3 consolidate_batch_051_075.py  # Batch 3
python3 consolidate_batch_076_100.py  # Batch 4
python3 consolidate_batch_101_125.py  # Batch 5
python3 consolidate_batch_126_150.py  # Batch 6
python3 consolidate_batch_151_175.py  # Batch 7
python3 consolidate_batch_176_200.py  # Batch 8 (FINAL)
```

---

## Features

- Automatic backup before each batch
- Validation of MCQ IDs
- Progress tracking
- Error detection and reporting
- Marks all MCQs as "regenerated: true"
- Updates metadata with timestamps

---

**Status**: Batch 1-2 scripts created, remaining batches to be created
