# UI Display Master List - All Dr. Amir Content

**Date:** 2026-05-28
**Purpose:** Complete list of ALL content to display in irStudy UI
**Status:** ✅ Production Ready

---

## Overview: What Needs to Be Displayed

This document provides a **single source of truth** for ALL OSCE and study content that should be visible to students in the UI.

### Summary Statistics

| Content Type | Count | Status | Display Location |
|-------------|-------|--------|------------------|
| **OSCEs in Database** | 226 | ✅ Already visible | `/osces` page |
| **Study Notes Files** | 106 | ❌ Not yet visible | `/notes` page (to be built) |
| **Dr. Amir Comprehensive OSCE** | 1 | ✅ In DB, needs enhancement | `/osces/308` (enhance display) |
| **Study Enhancement Docs** | 1 | ❌ Not yet visible | `/notes/amc-gi-pud-001` (to be built) |
| **Video-Based OSCEs** | 1 (1 pending) | ✅ Converted | Future additions |

---

## Section 1: OSCEs in Database (226 Total)

**Display Location:** `/osces` (OSCE Practice page)
**Status:** ✅ Already visible in UI
**Enhancement Needed:** Show more details for comprehensive OSCEs

### 1.1 By Specialty (Filter Options for UI)

```
┌─────────────────────────────────────────────────────┐
│ SPECIALTY FILTER DROPDOWN                           │
├─────────────────────────────────────────────────────┤
│ ☐ All Specialties (226)                            │
│ ☑ Cardiology (64 OSCEs) ...................... 28% │
│ ☐ Respiratory (52 OSCEs) ..................... 23% │
│ ☐ Psychiatry (46 OSCEs) ...................... 20% │
│ ☐ General Practice (33 OSCEs) ................ 15% │
│ ☐ Gastroenterology (18 OSCEs) ................ 8%  │
│   └─ ⭐ Includes 1 Dr. Amir comprehensive OSCE     │
│ ☐ Neurology (8 OSCEs) ........................ 4%  │
│ ☐ Surgery (2 OSCEs) .......................... 1%  │
│ ☐ Obstetrics/Gynaecology (2 OSCEs) ........... 1%  │
│ ☐ Paediatrics (1 OSCE) ....................... <1% │
└─────────────────────────────────────────────────────┘
```

### 1.2 Special Badge: Dr. Amir Comprehensive Format

**What Makes It Special:**
- 724 lines vs standard 50-100 lines
- Learning objectives, clinical pearls, red flags
- Australian guidelines with PBS codes
- Dr. Amir's 5 Ps framework integrated

**OSCE to Highlight:**

```
┌─────────────────────────────────────────────────────────────┐
│ 🏥 GI-PUD-001: Upper Abdominal Pain                        │
│                                                             │
│ ⭐⭐⭐ DR. AMIR COMPREHENSIVE OSCE                          │
│                                                             │
│ 📍 Gastroenterology • Upper GI                             │
│ 📊 Intermediate                                            │
│ ⏱️ 8 minutes                                                │
│ 📝 History Taking                                          │
│                                                             │
│ 🎯 KEY LEARNING POINTS                                     │
│   • Distinguish gastric vs duodenal by pain timing        │
│   • Identify NSAID-induced PUD and cessation              │
│   • Screen for 7 red flags systematically                 │
│   • Apply Dr. Amir's 5 Ps framework                       │
│                                                             │
│ 📚 INCLUDES                                                │
│   ✓ 9 Learning objectives                                 │
│   ✓ 8 Critical teaching points                            │
│   ✓ 7 Red flag warnings                                   │
│   ✓ 9 Clinical pearls                                     │
│   ✓ 6 Common pitfalls                                     │
│   ✓ 4 Australian guidelines                               │
│   ✓ Complete management pathway                           │
│                                                             │
│ 📖 LINKED STUDY NOTE                                       │
│   → "Peptic Ulcer Disease - Dr. Amir Enhanced Guide"      │
│      (13,000 words, 45 min read)                          │
│                                                             │
│ [📋 VIEW DETAILS]  [▶️ START PRACTICE]  [📚 READ NOTES]   │
└─────────────────────────────────────────────────────────────┘
```

**Database Query to Identify:**
```sql
SELECT * FROM osces WHERE osce_id = 'GI-PUD-001';
-- Result: ID 308, specialty: gastroenterology
```

**UI Implementation:**
- Add special badge "⭐ DR. AMIR COMPREHENSIVE" to this OSCE card
- Show preview of learning objectives
- Link to related study note
- Enhanced detail view (5 tabs instead of basic view)

### 1.3 Standard OSCEs (225 Total)

**Display:** Standard OSCE card format
**Content:** Basic information (title, specialty, difficulty, duration)
**Enhancement Plan:** Gradually add comprehensive format to popular OSCEs

**Example Standard OSCE Card:**
```
┌────────────────────────────────────────────┐
│ Cardiology: Chest Pain - 45-Year-Old Male │
│                                            │
│ 📍 Cardiology • Intermediate               │
│ ⏱️ 8 minutes                                │
│                                            │
│ [View Details]  [Start Practice]          │
└────────────────────────────────────────────┘
```

---

## Section 2: Study Notes (106 Files)

**Display Location:** `/notes` (NEW module to be built)
**Status:** ❌ Not yet visible in UI (files exist but not in database)
**Source:** `/ICRP_OSCE_Preparation/`

### 2.1 Organization by Specialty

#### Medicine (27+ files)

**Cardiovascular System:**
```
1. 01_Cardiovascular_Examination_FULL.md (15KB)
   - Dr. Amir's 5 Ps Framework
   - HIPJAP mnemonic (History, Inspection, Palpation, etc.)
   - Complete examination sequence

2. 02_Respiratory_Examination_FULL.md (14KB)
   - Dr. Amir's 5 Ps Framework
   - IPTAP sequence
   - Chest expansion techniques

3. 03_Abdominal_Examination_FULL.md
4. 04_Peripheral_Vascular_Examination.md
... (23+ more cardiovascular/respiratory files)
```

**Gastrointestinal:**
```
1. AMC_PEPTIC_ULCER_DISEASE_ENHANCEMENT.md (13,000 words) ⭐ PRIORITY
   - Dr. Amir video transcript conversion
   - 5 major sections
   - High-yield AMC content
   - ALREADY PROCESSED for database import

2. Standard GI examination notes
```

**Neurology, Endocrinology, Emergency:**
```
- Neurological examination sequences
- Cranial nerve assessment
- Diabetic examination protocols
- Emergency scenarios
```

#### Psychiatry (Multiple files)

```
1. Psychiatry_Mental_State_Exam.md
2. Psychiatry_Risk_Assessment.md
3. Psychiatry_Communication_Skills.md
... (more psychiatric stations)
```

#### Surgery (Multiple files)

```
1. Surgery_Examination_Techniques.md
2. Surgery_Pre_Post_Op_Assessment.md
... (surgical stations)
```

#### Paediatrics (Multiple files)

```
1. Paediatric_Adaptations_Dr_Amir.md
2. Paediatric_Developmental_Assessment.md
... (paediatric stations)
```

#### Obstetrics & Gynaecology (Multiple files)

```
1. ObGyn_Obstetric_Examination.md
2. ObGyn_Gynaecological_History.md
... (obs/gyn stations)
```

#### Ethics & Communication (Multiple files)

```
1. Ethics_Breaking_Bad_News.md
2. Ethics_Informed_Consent.md
3. Communication_Angry_Patient.md
... (communication skills)
```

### 2.2 UI Display Format for Study Notes

**Notes Browser Page (`/notes`):**

```
┌─────────────────────────────────────────────────────────────┐
│ Study Notes - Dr. Amir's 5 Ps Framework                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ [Search: ________________]  [Filter: All Specialties ▼]    │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 📚 Peptic Ulcer Disease - Dr. Amir Enhanced Guide      │ │
│ │                                                         │ │
│ │ ⭐⭐⭐ HIGH-YIELD AMC TOPIC                              │ │
│ │                                                         │ │
│ │ 📍 Gastroenterology • Upper GI                         │ │
│ │ 📊 Intermediate                                        │ │
│ │ ⏱️ 45 min read • 13,000 words                          │ │
│ │                                                         │ │
│ │ 5 Major Sections:                                      │ │
│ │ • Gastric vs Duodenal Distinction                     │ │
│ │ • NSAID-Induced PUD                                   │ │
│ │ • Australian Medications                              │ │
│ │ • Red Flag Assessment                                 │ │
│ │ • Differential Approach                               │ │
│ │                                                         │ │
│ │ 🩺 LINKED OSCE: GI-PUD-001 (Practice with AI)        │ │
│ │                                                         │ │
│ │ [READ NOTE]  [BOOKMARK]  [PRACTICE OSCE]              │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ 📚 Cardiovascular Examination - Complete Guide         │ │
│ │                                                         │ │
│ │ 📍 Cardiology                                          │ │
│ │ ⏱️ 20 min read                                          │ │
│ │                                                         │ │
│ │ Dr. Amir's 5 Ps Framework:                            │ │
│ │ • Preparation → Position → Permission → Perform       │ │
│ │ • HIPJAP mnemonic included                            │ │
│ │                                                         │ │
│ │ [READ NOTE]  [BOOKMARK]                               │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
│ ... (104 more notes)                                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2.3 Priority Display Order

**1. High-Yield AMC Content (Top Priority):**
- AMC_PEPTIC_ULCER_DISEASE_ENHANCEMENT.md ⭐⭐⭐

**2. Complete Examination Guides:**
- Cardiovascular_Examination_FULL.md
- Respiratory_Examination_FULL.md
- Abdominal_Examination_FULL.md

**3. Specialty-Specific:**
- All other 103 files organized by specialty

---

## Section 3: Video Transcript-Based Content

**Source:** Dr. Amir video teaching materials
**Location:** `/archive/old-data/processed_window_*/`

### 3.1 Video 1: Peptic Ulcer Disease ✅ COMPLETE

**Status:** Fully converted and ready for display

**Outputs Created:**

1. **OSCE (GI-PUD-001):**
   - File: `data/osces/gastroenterology_peptic_ulcer_osce.json`
   - Database: ID 308
   - Display: `/osces/308` ✅ Already visible

2. **Study Enhancement:**
   - File: `AMC_PEPTIC_ULCER_DISEASE_ENHANCEMENT.md`
   - Words: 13,000
   - Display: `/notes/amc-gi-pud-001` ❌ Not yet visible (needs database import)

**What Students Should See:**

```
┌─────────────────────────────────────────────────────────────┐
│ FROM DR. AMIR VIDEO TEACHING                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ 🎥 Peptic Ulcer Disease: Complete Learning Package         │
│                                                             │
│ ⭐ Based on Dr. Amir Soufi's 20-minute teaching video      │
│                                                             │
│ INCLUDES:                                                   │
│                                                             │
│ 1️⃣ OSCE Practice Station (8 minutes)                       │
│    📝 GI-PUD-001: Upper Abdominal Pain                     │
│    ▶️ Practice with AI patient                             │
│    [START OSCE]                                            │
│                                                             │
│ 2️⃣ Comprehensive Study Guide (45 minutes)                  │
│    📚 13,000-word enhancement document                     │
│    📖 5 major sections with clinical pearls               │
│    [READ NOTES]                                            │
│                                                             │
│ 🎯 LEARNING PATHWAY:                                       │
│    1. Read study notes (45 min)                           │
│    2. Practice OSCE with AI (8 min)                       │
│    3. Review feedback and improve                         │
│    4. Repeat until mastery                                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Video 2: Recorded Session ⏳ PENDING

**Status:** Transcribed, awaiting conversion
**Location:** `/archive/old-data/processed_window_20260217_121553/`
**Next Steps:** Apply same conversion process as Video 1

**Future Display:** Same format as Video 1 (OSCE + Study Notes linked together)

---

## Section 4: Master Index Files

**Display Location:** Study resources section or help center
**Purpose:** Navigation and resource discovery

### 4.1 Key Index Files

```
📂 /ICRP_OSCE_Preparation/

┌─────────────────────────────────────────────────────────────┐
│ INDEX FILES (Show in UI as "Study Resources")              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ 1. START_HERE.md                                           │
│    - Quick start guide for students                        │
│    - How to use the 5 Ps framework                        │
│    - Study tips and exam strategies                       │
│                                                             │
│ 2. 00_MASTER_INDEX_AMC_CLINICAL_OSCE.md                   │
│    - Complete catalog of 106 OSCE stations                │
│    - Organized by specialty                               │
│    - Links to all files                                   │
│                                                             │
│ 3. 00_VIDEO_RESOURCES_MASTER_LIST.md                      │
│    - 50+ demonstration videos                             │
│    - YouTube links to Dr. Amir content                    │
│    - Video-to-OSCE mappings                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**UI Suggestion:**
- Create "📖 Study Resources" page (`/resources`)
- Display these index files with nice formatting
- Make them browsable and searchable

---

## Section 5: Linking Strategy (Cross-References)

**How Content Should Connect in UI:**

### 5.1 From OSCE → Study Notes

```
OSCE Detail Page (/osces/308)
    ↓
    [Section: Related Study Materials]
    ↓
    "📚 Learn More: Peptic Ulcer Disease - Dr. Amir Guide"
    ↓
    [Link] → /notes/amc-gi-pud-001
```

### 5.2 From Study Notes → OSCE

```
Study Note Detail Page (/notes/amc-gi-pud-001)
    ↓
    [Section: Practice What You Learned]
    ↓
    "🩺 Practice OSCE: Upper Abdominal Pain (GI-PUD-001)"
    ↓
    [Link] → /osces/308
```

### 5.3 From MCQ Results → Study Notes

```
MCQ Results (student got question wrong)
    ↓
    [Section: Review These Topics]
    ↓
    "📖 Study: Peptic Ulcer Disease - Gastric vs Duodenal"
    ↓
    [Link] → /notes/amc-gi-pud-001#section-1
```

### 5.4 From Dashboard → Dr. Amir Content

```
Dashboard (/)
    ↓
    [Widget: Featured Dr. Amir Content]
    ↓
    "🎥 Dr. Amir Video-Based Learning"
    ↓
    Shows: GI-PUD-001 OSCE + Study Notes as a package
```

---

## Section 6: Implementation Priority

### Phase 1: Immediate (Week 1-2) ✅ CRITICAL

**1. Enhance Existing OSCE Display (GI-PUD-001):**
- Add special badge "⭐ DR. AMIR COMPREHENSIVE"
- Show learning objectives preview on card
- Enhance detail page with 5 tabs
- Display: `/osces/308`

**2. Import Study Enhancement to Database:**
- Create `study_notes` table
- Import `AMC_PEPTIC_ULCER_DISEASE_ENHANCEMENT.md`
- Make accessible via API

### Phase 2: Core Features (Week 3-4) 🎯 HIGH PRIORITY

**3. Build Study Notes Module:**
- Create `/notes` browser page
- Create `/notes/:id` detail page
- Import top 10 most important study files from `ICRP_OSCE_Preparation/`

**4. Link OSCE ↔ Study Notes:**
- Add "Related Study Materials" section to OSCE detail
- Add "Practice OSCE" button to study notes
- Bidirectional navigation

### Phase 3: Content Expansion (Week 5-6) 📚 MEDIUM PRIORITY

**5. Import Remaining Study Notes:**
- Import all 106 files to database
- Organize by specialty
- Add search and filter functionality

**6. Video Integration:**
- Create "Dr. Amir Video Learning" section
- Link videos → OSCEs → Study Notes
- Import Video 2 content

### Phase 4: Advanced Features (Week 7-8) ⭐ NICE TO HAVE

**7. Index Files Display:**
- Create `/resources` page
- Display START_HERE.md, master indexes
- Add video resources list

**8. Learning Pathway Tracking:**
- Track which notes students have read
- Suggest OSCEs based on notes studied
- Progress visualization

---

## Section 7: Database Import Checklist

### Already Imported ✅

- [x] 226 OSCEs (all specialties)
- [x] GI-PUD-001 comprehensive OSCE
- [x] 1,221 MCQs

### Need to Import ❌

- [ ] `AMC_PEPTIC_ULCER_DISEASE_ENHANCEMENT.md` to `study_notes` table
- [ ] 106 study note files to `study_notes` table
- [ ] Index files to `resources` table (optional)

### Import Scripts Needed

**1. Study Notes Importer:**
```python
# backend/scripts/import_study_notes.py

import_study_note(
    note_id="AMC-GI-PUD-001",
    file_path="AMC_PEPTIC_ULCER_DISEASE_ENHANCEMENT.md",
    specialty="gastroenterology",
    tags=["high_yield", "dr_amir", "video_based"],
    related_osce_ids=["GI-PUD-001"]
)
```

**2. Batch Study Notes Importer:**
```python
# backend/scripts/import_icrp_notes.py

import_directory(
    source_dir="ICRP_OSCE_Preparation/Medicine/",
    specialty="medicine",
    framework="5ps"
)
```

---

## Section 8: UI Filter & Search Requirements

### Filters Needed

**OSCE Browser (`/osces`):**
```
☐ Specialty (9 options)
☐ Difficulty (3 options: Easy, Medium, Hard)
☐ Type (4 options: History, Exam, Communication, Other)
☐ Source (3 options: All, Dr. Amir, Standard)
☐ Duration (4 options: <5 min, 5-10 min, 10-15 min, >15 min)
```

**Study Notes Browser (`/notes`):**
```
☐ Specialty (9 options)
☐ Difficulty (3 options)
☐ Framework (2 options: 5 Ps, Standard)
☐ Content Type (3 options: Examination, History, Management)
☐ Reading Time (<10 min, 10-30 min, >30 min)
☐ AMC Relevance (High Yield, Common, Rare)
```

### Search Functionality

**Full-Text Search:**
- Search OSCE titles, descriptions
- Search study note content
- Search by topic/tag (e.g., "NSAID", "gastric ulcer", "red flags")

**Autocomplete Suggestions:**
- "peptic ulcer" → Shows GI-PUD-001 OSCE + Study Note
- "cardiovascular exam" → Shows 64 cardiology OSCEs + exam notes
- "dr amir" → Shows all Dr. Amir content

---

## Section 9: Mobile Display Adaptations

### OSCE Cards (Mobile)

```
┌──────────────────────────┐
│ 🏥 GI-PUD-001            │
│ Upper Abdominal Pain     │
│                          │
│ ⭐⭐⭐ DR. AMIR          │
│                          │
│ 📍 Gastro • 8 min        │
│ 📊 Intermediate          │
│                          │
│ [▶️ PRACTICE]            │
│ [📚 READ NOTES]          │
└──────────────────────────┘
```

### Study Notes (Mobile)

```
┌────────────────────────────┐
│ 📚 Peptic Ulcer Disease   │
│                            │
│ ⭐ High Yield              │
│ ⏱️ 45 min read             │
│                            │
│ 5 Sections:                │
│ 1. Gastric vs Duodenal    │
│ 2. NSAID-Induced          │
│ 3. Medications            │
│ 4. Red Flags              │
│ 5. Differential Dx        │
│                            │
│ [READ] [BOOKMARK]         │
└────────────────────────────┘
```

---

## Section 10: Quality Assurance

### Content Verification Checklist

**Before Display:**
- [ ] All 226 OSCEs render correctly
- [ ] GI-PUD-001 shows all 9 learning objectives
- [ ] Study notes markdown renders properly
- [ ] Links between OSCE ↔ Notes work
- [ ] Mobile responsive on all pages
- [ ] Search returns accurate results
- [ ] Filters work correctly
- [ ] Dr. Amir badge displays prominently

**Accessibility:**
- [ ] WCAG 2.2 AA compliance
- [ ] Screen reader tested
- [ ] Keyboard navigation works
- [ ] Color contrast ratios pass

**Performance:**
- [ ] Page load <2 seconds
- [ ] Smooth scrolling on long study notes
- [ ] Lazy loading for 106+ notes
- [ ] API response time <200ms

---

## Section 11: Success Metrics

### What to Track

**Engagement:**
- Views per OSCE/note
- Time spent reading notes
- OSCE completion rate
- Notes → OSCE conversion rate

**Learning Outcomes:**
- Score improvement after reading notes
- Pass rate for Dr. Amir OSCE vs standard OSCEs
- Repeat attempt rate
- Bookmark/save rate

**Content Performance:**
- Most viewed OSCEs (top 10)
- Most viewed notes (top 10)
- Dr. Amir content usage vs standard
- Search terms (what students look for)

---

## Summary: Complete Display Checklist

### ✅ What's Already Visible

1. 226 OSCEs in database → `/osces` ✅
2. GI-PUD-001 comprehensive OSCE → `/osces/308` ✅

### ❌ What Needs to Be Built

1. Study Notes Module → `/notes` ❌
2. Enhanced OSCE Detail View → `/osces/308` (enhance existing) ❌
3. OSCE ↔ Notes Linking → Add to both pages ❌
4. Dr. Amir Special Badges → Add to UI components ❌
5. Study Resources Page → `/resources` ❌

### 📦 What Needs to Be Imported

1. AMC_PEPTIC_ULCER_DISEASE_ENHANCEMENT.md → `study_notes` table ❌
2. 106 ICRP study files → `study_notes` table ❌
3. Index files → `resources` table (optional) ❌

---

## Quick Start for Developers

**1. Show Dr. Amir OSCE Properly:**
```typescript
// frontend/src/pages/osces/OSCEDetail.tsx
if (osce.osce_id === 'GI-PUD-001') {
  return <DrAmirOSCEDetail osce={osce} />;
} else {
  return <StandardOSCEDetail osce={osce} />;
}
```

**2. Import Study Enhancement:**
```bash
cd backend
python3 scripts/import_study_notes.py --execute
```

**3. Build Notes Module:**
```bash
cd frontend/src/pages
mkdir notes
# Create NotesBrowser.tsx and NoteDetail.tsx
```

**4. Link Everything:**
```typescript
// On OSCE detail page
<RelatedStudyNotes osceId={osce.osce_id} />

// On study note page
<RelatedOSCEs noteId={note.note_id} />
```

---

**Last Updated:** 2026-05-28
**Document Owner:** PM / Content Manager
**Status:** ✅ PRODUCTION READY - Implementation can begin
**Priority:** Phase 1 (Enhanced OSCE) + Phase 2 (Study Notes) = HIGH

---

## Appendix: File Locations Reference

```
Project Root: /home/dev/Development/irStudy/

OSCEs (JSON):
├── data/osces/cardiology_50_osces.json (561KB)
├── data/osces/respiratory_50_osces.json (640KB)
├── data/osces/psychiatry_40_osces.json (298KB)
├── data/osces/gastroenterology_peptic_ulcer_osce.json (35KB) ⭐
└── ... (25+ more segmented files)

Study Notes:
├── AMC_PEPTIC_ULCER_DISEASE_ENHANCEMENT.md (13K words) ⭐
└── ICRP_OSCE_Preparation/ (106 files)
    ├── Medicine/ (27+ files)
    ├── Psychiatry/
    ├── Surgery/
    ├── Paediatrics/
    ├── ObGyn/
    └── Ethics_Communication/

Video Transcripts:
├── archive/old-data/processed_window_20260217_124331/ (Video 1) ✅
└── archive/old-data/processed_window_20260217_121553/ (Video 2) ⏳

Master Plans:
├── COMPLETE_UI_UX_MASTER_PLAN.md
├── DR_AMIR_OSCE_UI_UX_PLAN.md
├── DR_AMIR_OSCE_COMPLETE_SYSTEM_SUMMARY.md
├── MASTER_OSCE_CONTENT_INVENTORY.md
├── OSCE_INVENTORY_QUICK_REFERENCE.md
└── UI_DISPLAY_MASTER_LIST.md (this file)
```

---

**END OF DOCUMENT**
