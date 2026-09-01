# OSCE Content Inventory - Quick Reference Guide

**Generated:** 2026-05-28  
**For:** UI Developers, Content Managers, Students  
**Status:** Complete and Production Ready  

---

## Quick Stats

| Category | Count | Location | Status |
|----------|-------|----------|--------|
| **OSCE JSON Files** | 40+ | `/data/osces/` | ✅ Ready |
| **Study Notes Files** | 106 | `/ICRP_OSCE_Preparation/` | ✅ Ready |
| **Pipeline Outputs** | 35 | `/osce-pipeline/output/` | ✅ Ready |
| **Database OSCEs** | 226 | PostgreSQL | ✅ Imported |
| **Database MCQs** | 1,221 | PostgreSQL | ✅ Imported |
| **Video Transcripts** | 2 | `/archive/old-data/processed_window_*/` | ✅ Available |
| **Import Scripts** | 3 | `/backend/scripts/` | ✅ Production |

---

## OSCE Distribution (Database)

```
Cardiology ........................... 64 OSCEs (28%)
Respiratory .......................... 52 OSCEs (23%)
Psychiatry ........................... 46 OSCEs (20%)
General Practice ..................... 33 OSCEs (15%)
Gastroenterology ..................... 18 OSCEs (8%)
  ├─ GI-PUD-001 (Dr. Amir) .......... 1 OSCE (Comprehensive 724 lines)
Neurology ............................ 8 OSCEs (4%)
Other (Surgery, ObGyn, Peds) ........ 5 OSCEs (2%)
────────────────────────────────────────────────
TOTAL ............................... 226 OSCEs (100%)
```

---

## By Source Type

### Dr. Amir Methodology Content ✅

**Comprehensive Format (724+ lines):**
- `gastroenterology_peptic_ulcer_osce.json` (GI-PUD-001)
- Database ID: 308
- Title: Upper Abdominal Pain - Peptic Ulcer Disease Assessment
- Includes: Patient scenario, 8 marking criteria, learning objectives, clinical pearls, red flags, Australian guidelines

**Study Enhancement Document:**
- `AMC_PEPTIC_ULCER_DISEASE_ENHANCEMENT.md`
- 13,000+ words
- 5 major sections + 8 reference tables

**Study Notes (106 files):**
- `/ICRP_OSCE_Preparation/` - All specialties
- Based on Dr. Amir's 5 Ps Framework

**OSCE Pipeline Clinical Notes (35 folders):**
- `/osce-pipeline/output/`
- 31 `clinical_notes.md` files (20-40KB each)

### Standard Format Content

**Batch Files:**
- `cardiology_50_osces.json` (561KB)
- `respiratory_50_osces.json` (640KB)
- `psychiatry_40_osces.json` (298KB)

**Segmented Files (25+ files):**
- `cardiology_osces_21-25.json`
- `respiratory_osces_1_5.json`
- `psychiatry_osces_11-20.json`
- etc.

---

## Video Conversion Status

### Video 1: Dr. Amir Peptic Ulcer Disease
- **Status:** ✅ FULLY CONVERTED
- **Duration:** 20 minutes
- **Output:**
  - OSCE: `gastroenterology_peptic_ulcer_osce.json` (724 lines)
  - Enhancement: `AMC_PEPTIC_ULCER_DISEASE_ENHANCEMENT.md` (13K words)
  - Database: ID 308 (imported and verified)
  - Documentation: `VIDEO_TRANSCRIPT_CONVERSION_COMPLETE_REPORT.md`

### Video 2: Recorded Session
- **Status:** ✅ TRANSCRIBED (conversion pending)
- **Location:** `/archive/old-data/processed_window_20260217_121553/`
- **Output:** Transcript available, awaiting processing

---

## Key Files for UI Implementation

### Master Documentation
- **`MASTER_OSCE_CONTENT_INVENTORY.md`** - Complete detailed inventory
- **`OSCE_INVENTORY_QUICK_REFERENCE.md`** - This file
- **`OSCE_NOTES_LOCATION_GUIDE.md`** - Study materials guide
- **`DR_AMIR_OSCE_COMPLETE_SYSTEM_SUMMARY.md`** - System overview

### OSCE Data Sources
- **Primary:** `/data/osces/cardiology_50_osces.json` (561KB)
- **Primary:** `/data/osces/respiratory_50_osces.json` (640KB)
- **Primary:** `/data/osces/psychiatry_40_osces.json` (298KB)
- **New:** `/data/osces/gastroenterology_peptic_ulcer_osce.json` (35KB)

### Study Materials
- **Folder:** `/ICRP_OSCE_Preparation/`
- **Index:** `00_MASTER_INDEX_AMC_CLINICAL_OSCE.md`
- **Videos:** `00_VIDEO_RESOURCES_MASTER_LIST.md`
- **Specialties:** 27+ medicine files + psychiatry + surgery + peds + obs/gyn + ethics

---

## Data Structure Example

### OSCE JSON Format (Comprehensive)

```json
{
  "osce_id": "GI-PUD-001",
  "station_title": "Upper Abdominal Pain - Peptic Ulcer Disease Assessment",
  "specialty": "gastroenterology",
  "duration_minutes": 8,
  "total_marks": 15,
  
  "patient_scenario": {
    "demographics": { ... },
    "chief_complaint": "...",
    "history_presenting_illness": "..."
  },
  
  "marking_criteria": [
    {
      "criterion": "History taking structure",
      "marks": 3,
      "sub_criteria": [ ... ]
    },
    { ... more criteria ... }
  ],
  
  "learning_objectives": [ ... ],
  "red_flags": [ ... ],
  "clinical_pearls": [ ... ],
  "management_plan": { ... },
  "references": [ ... ]
}
```

### Database Query Examples

```sql
-- All OSCEs by specialty
SELECT specialty, COUNT(*) FROM osces GROUP BY specialty;

-- GI content
SELECT * FROM osces WHERE specialty = 'gastroenterology';

-- Dr. Amir OSCE specifically
SELECT * FROM osces WHERE osce_id = 'GI-PUD-001';

-- Count by type
SELECT osce_type, COUNT(*) FROM osces GROUP BY osce_type;
```

### API Endpoints

```bash
# Get all OSCEs
curl http://localhost:8001/api/v1/osces

# Filter by specialty
curl "http://localhost:8001/api/v1/osces?specialty=cardiology"

# Get specific OSCE
curl http://localhost:8001/api/v1/osces/308

# Search by OSCE ID
curl "http://localhost:8001/api/v1/osces?osce_id=GI-PUD-001"
```

---

## Recommended UI Filter Options

### By Specialty (9 options)
- Cardiology (64)
- Respiratory (52)
- Psychiatry (46)
- General Practice (33)
- Gastroenterology (18)
- Neurology (8)
- Surgery (2)
- Obstetrics/Gynaecology (2)
- Paediatrics (1)

### By Type
- History Taking
- Examination
- Communication Skills
- Other

### By Difficulty
- Easy
- Medium
- Hard

### By Source
- Dr. Amir (Special badge)
- OSCE Pipeline
- Standard

---

## Import & Maintenance

### Active Scripts
- **`backend/scripts/import_osces.py`** - Main batch importer
- **`backend/scripts/import_peptic_ulcer_osce_v2.py`** - GI-PUD-001 (production)

### Running Imports

```bash
# Dry run (validate without importing)
python3 backend/scripts/import_osces.py --validate

# Import from directory
python3 backend/scripts/import_osces.py --source /home/dev/Development/irStudy/data/osces/

# Import specific OSCE
python3 backend/scripts/import_peptic_ulcer_osce_v2.py --dry-run
python3 backend/scripts/import_peptic_ulcer_osce_v2.py --execute
```

---

## Accessing Content

### Via Frontend
```
http://localhost:5173
→ OSCE Practice
→ Filter by specialty/difficulty
→ Select and practice
```

### Via API
```bash
curl http://localhost:8001/api/v1/osces?specialty=gastroenterology
```

### Via Study Notes
```
/ICRP_OSCE_Preparation/
├── START_HERE.md
├── 00_MASTER_INDEX_AMC_CLINICAL_OSCE.md
├── 00_VIDEO_RESOURCES_MASTER_LIST.md
└── [Specialty folders...]
```

---

## Quality Checklist

- ✅ All JSON files valid and well-formed
- ✅ All 226 OSCEs imported successfully
- ✅ Database queries verified and tested
- ✅ API endpoints working
- ✅ Australian medical context throughout
- ✅ AMC exam format compliant
- ✅ Dr. Amir methodology preserved
- ✅ 100% content accuracy verified
- ✅ All import scripts tested
- ✅ Documentation complete

---

## Next Steps

### For UI Implementation
1. Use `/data/osces/` JSON files as primary data source
2. Implement filters: specialty, difficulty, type, source
3. Add special badge/indicator for Dr. Amir content
4. Link to study notes in `/ICRP_OSCE_Preparation/`

### For Content Expansion
1. Convert Video 2 using same methodology as GI-PUD-001
2. Import additional respiratory MCQs from backup files
3. Consider video-linked study materials

### For User Experience
1. Show learning objectives before practice
2. Display red flags checklist during session
3. Provide detailed feedback post-session
4. Track attempt statistics and trends

---

## Support & Troubleshooting

### Common Queries
- **"Where is the OSCE data?"** → `/data/osces/`
- **"How many OSCEs are imported?"** → 226 (9 specialties)
- **"What's the Dr. Amir OSCE?"** → GI-PUD-001 (ID: 308, 724 lines)
- **"Where are study notes?"** → `/ICRP_OSCE_Preparation/` (106 files)

### Database Issues
- Query count: `SELECT COUNT(*) FROM osces;`
- Check imports: `SELECT osce_id, specialty FROM osces LIMIT 10;`
- Verify GI content: `SELECT * FROM osces WHERE specialty='gastroenterology';`

### API Issues
- Test endpoint: `curl http://localhost:8001/api/v1/osces`
- Check backend logs: `tail -f backend.log`
- Verify database connection: Check DATABASE_URL in .env

---

**Last Updated:** 2026-05-28  
**Full Inventory:** See `MASTER_OSCE_CONTENT_INVENTORY.md`  
**Status:** Production Ready  

