# Split PDF Files Index

This document indexes all split PDF files for easy reference during content extraction.

## Overview

| Textbook | Original Size | Total Pages | Split Files | Split Directory |
|----------|--------------|-------------|-------------|-----------------|
| Talley & O'Connor Clinical Examination | 18.50 MB | 1,135 | 23 files (50 pages each) | `Clinical_Examination_Split/` |
| Murtagh's General Practice 8th Ed | 40.54 MB | 3,785 | 38 files (100 pages each) | `Murtagh_General_Practice_Split/` |
| Oxford Emergency Medicine 5th Ed | 36.43 MB | 804 | 9 files (100 pages each) | `Oxford_Emergency_Medicine_Split/` |
| AMC Anthology of Medical Conditions | 62.97 MB | 483 | 5 files (100 pages each) | `AMC_Anthology_Split/` |

## Chapter Locations

### Talley & O'Connor Clinical Examination
- **Chapter 8 (Peripheral Vascular):** Parts 004-006 (pages 151-300) ✅ EXTRACTED
- **Chapter 14 (Musculoskeletal):** Parts 007-009 (pages 301-450) ✅ EXTRACTED
- **Chapter 15 (ENT):** Parts 007-009 (pages 301-450) ✅ EXTRACTED
- **Thyroid Examination:** Parts 001-003 (pages 1-150) ✅ EXTRACTED
- **Lymph Nodes:** Parts 001-003 (pages 1-150) ✅ EXTRACTED

### Murtagh's General Practice (For Issue #1 & #3)
**Note:** Chapter 26 (Diabetes) is approximately pages 2500-2600
- **Chapter 26 (Diabetes Management):** Part 026 (pages 2501-2600) - FOR ISSUE #1
- **Common GP Presentations:** Various chapters throughout
  - Chest pain: Part 003-004 (pages 201-400)
  - SOB: Part 004-005 (pages 301-500)
  - Abdominal pain: Part 006-007 (pages 501-700)
  - Headache: Part 008-009 (pages 701-900)
  - Fever: Part 010-011 (pages 901-1100)
  - Mental health: Part 032-034 (pages 3101-3400)

### Oxford Emergency Medicine (For Issue #3)
- **ACS (Acute Coronary Syndrome):** Part 002-003 (pages 101-300)
- **Anaphylaxis:** Part 002 (pages 101-200)
- **Stroke:** Part 005-006 (pages 401-600)
- **GI Bleeding:** Part 003-004 (pages 201-400)
- **Sepsis:** Part 007 (pages 601-700)
- **Trauma:** Part 008-009 (pages 701-804)

### AMC Anthology (For Phase 3 - Issue #4 & #5)
- **Medical Conditions A-Z:** Parts 001-005 (all pages)
- **Case scenarios:** Distributed throughout
- **Specialty cases:** Parts 003-005 (pages 201-483)

## Extraction Status

### ✅ Completed (Issue #2)
- [x] ENT Examination from Talley Ch 15
- [x] Musculoskeletal from Talley Ch 14
- [x] Peripheral Vascular from Talley Ch 8
- [x] Thyroid Examination from Talley
- [x] Lymph Node Examination from Talley

### 📋 Next Up (Issue #1)
- [ ] Diabetes Management Module from Murtagh Ch 26 (Part 026)

### 🎯 Phase 2 (Issue #3)
- [ ] 12 Mock OSCE Stations
  - 6 from Murtagh's (common GP presentations)
  - 6 from Oxford EM (emergency presentations)

### 📊 Phase 3 (Issues #4 & #5)
- [ ] Master Differential Diagnosis Guide
- [ ] 50-100 Clinical Cases with SOAP notes

## Quick Reference Commands

```bash
# List files in a specific split directory
ls -lh Clinical_Examination_Split/
ls -lh Murtagh_General_Practice_Split/
ls -lh Oxford_Emergency_Medicine_Split/
ls -lh AMC_Anthology_Split/

# Find specific page ranges
# Example: Find Murtagh Chapter 26 (Diabetes)
ls Murtagh_General_Practice_Split/Murtagh_GP_part026_pages2501-2600.pdf

# Split additional PDFs
python3 scripts/split_pdf.py <input.pdf> --output-dir <dir> --prefix <name> --pages 100
```

## Notes

- All split PDFs maintain original quality
- Files are named with page ranges for easy identification
- Large image-heavy sections result in larger file sizes
- Encrypted PDFs (like AMC Anthology) require pycryptodome library

---

**Last Updated:** December 16, 2025  
**Total Split Files:** 75 files  
**Total Coverage:** 6,207 pages across 4 major textbooks
