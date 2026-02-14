# MCQ & OSCE Data Flow - irStudy Platform

**Created:** 2026-02-03
**Status:** Current data flow analysis

---

## Overview

The irStudy platform generates MCQs and OSCEs using AI (Claude/Ollama), stores them as JSON files, and serves them via PostgreSQL database through FastAPI endpoints.

---

## Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│ 1. CONTENT GENERATION (Python scripts)                               │
│                                                                       │
│    RAG System (Qdrant) ──> Claude/Ollama ──> JSON Files             │
│    - Medical text chunks      - Generate MCQs    - data/mcqs/*.json  │
│    - Australian guidelines    - Generate OSCEs   - data/osces/*.json │
│    - Citations required       - Validate quality                     │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 2. FILE STORAGE (JSON format)                                        │
│                                                                       │
│    data/mcqs/                                                         │
│    ├── week1_regenerated_100_mcqs.json                              │
│    ├── week2_regenerated_100_mcqs.json                              │
│    ├── week3_cardiology_200_mcqs.json                               │
│    ├── week3_respiratory_200_mcqs.json                              │
│    └── psychiatry_*.json                                             │
│                                                                       │
│    data/osces/                                                        │
│    ├── cardiology_50_osces.json                                     │
│    ├── respiratory_50_osces.json                                    │
│    └── psychiatry_40_osces.json                                     │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 3. DATABASE LOADING (PostgreSQL)                                     │
│                                                                       │
│    ⚠️  MISSING COMPONENT ⚠️                                          │
│                                                                       │
│    Need: Database seed script to load JSON → PostgreSQL              │
│    - Read JSON files from data/mcqs/, data/osces/                   │
│    - Parse and validate content                                      │
│    - Insert into mcqs and osces tables                              │
│    - Handle duplicates (upsert based on question_id/osce_id)        │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 4. DATABASE SCHEMA (PostgreSQL tables)                               │
│                                                                       │
│    mcqs table (backend/src/db/models.py:188-276)                    │
│    ├── id (primary key)                                             │
│    ├── question_id (unique, e.g., "MCQ-CARD-001")                  │
│    ├── question_text                                                 │
│    ├── options (JSON: {"A": "...", "B": "...", ...})               │
│    ├── correct_answer (A, B, C, D, or E)                           │
│    ├── explanation                                                   │
│    ├── citation (Australian guidelines required)                    │
│    ├── specialty (enum: cardiology, respiratory, etc.)             │
│    ├── difficulty (enum: easy, medium, hard)                       │
│    ├── tags (JSON array)                                            │
│    ├── image_url (optional)                                         │
│    └── statistics (times_attempted, times_correct, etc.)           │
│                                                                       │
│    osces table (backend/src/db/models.py:284-384)                  │
│    ├── id (primary key)                                             │
│    ├── osce_id (unique, e.g., "OSCE-CARD-001")                    │
│    ├── station_title                                                 │
│    ├── station_type (enum: history, examination, etc.)             │
│    ├── patient_instructions                                         │
│    ├── candidate_instructions                                       │
│    ├── examiner_instructions                                        │
│    ├── rubric (JSON: 15-mark AMC format)                           │
│    ├── specialty                                                     │
│    ├── difficulty                                                    │
│    ├── time_limit_minutes (default: 8)                             │
│    └── learning_objectives (JSON)                                   │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 5. API ENDPOINTS (FastAPI)                                           │
│                                                                       │
│    GET /api/v1/mcqs                                                  │
│    - List MCQs (filterable by specialty, difficulty, tags)          │
│    - Paginated (skip/limit)                                          │
│    - Returns MCQPublic (without answers)                             │
│                                                                       │
│    GET /api/v1/mcqs/{mcq_id}                                        │
│    - Get single MCQ (without answer)                                 │
│                                                                       │
│    POST /api/v1/mcqs/{mcq_id}/attempt                               │
│    - Submit answer attempt                                           │
│    - Updates statistics (times_attempted, times_correct)             │
│    - Creates MCQAttempt record                                       │
│                                                                       │
│    GET /api/v1/mcqs/{mcq_id}/explanation                            │
│    - Get explanation after attempt                                   │
│    - Shows correct answer and reasoning                              │
│                                                                       │
│    GET /api/v1/osces                                                 │
│    - List OSCE stations                                              │
│                                                                       │
│    GET /api/v1/osces/{osce_id}                                      │
│    - Get single OSCE station                                         │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 6. FRONTEND (React + TanStack Query)                                 │
│                                                                       │
│    frontend/src/api/mcqsApi.ts                                      │
│    - fetchMCQs()                                                     │
│    - fetchMCQById()                                                  │
│    - submitMCQAttempt()                                             │
│    - fetchMCQExplanation()                                          │
│                                                                       │
│    frontend/src/pages/MCQsPage.tsx                                  │
│    - Display MCQ list with filters                                   │
│    - Answer submission interface                                     │
│    - Explanation display after attempt                               │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Current Status

### ✅ What's Working

1. **Content Generation:**
   - ✅ Python scripts generate MCQs/OSCEs using RAG + AI
   - ✅ Output stored as JSON files in `data/mcqs/` and `data/osces/`
   - ✅ Citations validated against Australian guidelines
   - ✅ QA validation (100% pass rate, citation checks)

2. **Database Schema:**
   - ✅ PostgreSQL tables defined (`mcqs`, `osces`)
   - ✅ Australian medical context fields (citations, specialty, etc.)
   - ✅ AMC exam format (15-mark OSCE rubric, 8-minute stations)
   - ✅ User progress tracking (`mcq_attempts`, `user_progress`)

3. **API Endpoints:**
   - ✅ FastAPI routes implemented (`backend/src/api/v1/mcqs.py`, `osces.py`)
   - ✅ Authentication with JWT tokens
   - ✅ Role-based access control (student, educator, admin)
   - ✅ Filtering by specialty, difficulty, tags

4. **Frontend:**
   - ✅ React components for MCQ/OSCE display
   - ✅ TanStack Query for API integration
   - ✅ Answer submission and explanation display

### ⚠️ Missing Component

**Database Seed Script** - No automated way to load JSON → PostgreSQL

**What's needed:**
```python
# scripts/seed_database.py (DOES NOT EXIST YET)

import json
from pathlib import Path
from sqlalchemy.orm import Session

def seed_mcqs(db: Session):
    """Load all MCQ JSON files into database"""
    mcq_dir = Path("data/mcqs/")

    for json_file in mcq_dir.glob("*.json"):
        with open(json_file) as f:
            mcqs_data = json.load(f)

        for mcq_data in mcqs_data:
            # Parse JSON structure
            mcq = MCQ(
                question_id=mcq_data["question_id"],
                question_text=mcq_data["question"],
                options=mcq_data["options"],
                correct_answer=mcq_data["correct_answer"],
                explanation=mcq_data["explanation"],
                citation=mcq_data["citation"],
                specialty=mcq_data["specialty"],
                difficulty=mcq_data["difficulty"],
                tags=mcq_data.get("tags", []),
                image_url=mcq_data.get("image_url"),
            )

            # Upsert (insert or update if exists)
            db.merge(mcq)

        db.commit()
```

---

## JSON File Locations

### MCQs

```
data/mcqs/
├── week1_regenerated_100_mcqs.json              (100 MCQs, Week 1 content)
├── week1_regenerated_100_mcqs_with_images.json  (with HEAL images)
├── week2_regenerated_100_mcqs.json              (100 MCQs, Week 2 content)
├── week2_regenerated_100_mcqs_with_images.json  (with HEAL images)
├── week3_cardiology_200_mcqs.json               (200 MCQs, Cardiology)
├── week3_cardiology_200_mcqs_with_images.json   (with HEAL images)
├── week3_respiratory_200_mcqs.json              (200 MCQs, Respiratory)
├── week3_respiratory_200_mcqs_with_images.json  (with HEAL images)
├── week3_psychiatry_additional_100_mcqs.json    (100 MCQs, Psychiatry)
├── psychiatry_anxiety_bipolar_day2.json
├── psychiatry_depression_day1.json
├── psychiatry_psychosis_day3.json
├── psychiatry_suicide_mha_day4.json
└── psychiatry_final_day5.json

Total: ~1,000+ MCQs across all specialties
```

### OSCEs

```
data/osces/
├── cardiology_50_osces.json       (50 OSCE stations, Cardiology)
├── respiratory_50_osces.json      (50 OSCE stations, Respiratory)
├── psychiatry_40_osces.json       (40 OSCE stations, Psychiatry)
└── psychiatry_week1_osces.json

Total: ~140+ OSCE stations
```

---

## JSON File Structure

### MCQ JSON Format

```json
{
  "question_id": "MCQ-CARD-001",
  "question": "A 65-year-old man presents with acute chest pain...",
  "options": {
    "A": "GTN spray 400 mcg sublingually",
    "B": "Aspirin 300 mg orally (dispersible)",
    "C": "Morphine 5-10 mg IV",
    "D": "Oxygen if SpO2 <94%",
    "E": "Immediate ECG"
  },
  "correct_answer": "E",
  "explanation": "In suspected acute coronary syndrome (ACS), an ECG should be performed immediately (within 10 minutes of presentation) to guide further management. The ECG can reveal ST elevation MI (STEMI), which requires immediate reperfusion therapy...",
  "citation": "Acute Coronary Syndromes (eTG complete, accessed 2024)",
  "specialty": "cardiology",
  "difficulty": "medium",
  "tags": ["amc", "acute-coronary-syndrome", "emergency", "ecg"],
  "image_url": "https://cdn.irstudy.com/heal_872345.jpg",
  "learning_points": [
    "ECG is first-line investigation in suspected ACS",
    "STEMI requires immediate reperfusion (PCI or thrombolysis)",
    "Aspirin 300 mg should be given early unless contraindicated"
  ]
}
```

### OSCE JSON Format

```json
{
  "osce_id": "OSCE-CARD-001",
  "station_title": "Chest Pain History Taking",
  "station_type": "history_taking",
  "patient_instructions": "You are a 55-year-old man presenting to ED with chest pain that started 2 hours ago while mowing the lawn. The pain is central, crushing, radiating to your left arm and jaw. You feel sweaty and nauseous. You have a history of hypertension and high cholesterol. You smoke 20 cigarettes per day for 30 years. Your father had a heart attack at age 60.",
  "candidate_instructions": "This is a 55-year-old man presenting to the emergency department with chest pain. Take a focused history to determine the likely cause and identify red flag features. You have 8 minutes for this station.",
  "examiner_instructions": "Candidate should perform systematic cardiovascular history focusing on: SOCRATES for pain, cardiovascular risk factors, red flags for acute coronary syndrome.",
  "rubric": {
    "introduction": {
      "max_marks": 1,
      "criteria": "Introduces self, confirms patient identity, establishes rapport"
    },
    "history_pain": {
      "max_marks": 5,
      "criteria": "SOCRATES: Site, Onset, Character, Radiation, Associations, Time course, Exacerbating/relieving factors, Severity"
    },
    "risk_factors": {
      "max_marks": 3,
      "criteria": "Identifies cardiovascular risk factors: hypertension, hyperlipidaemia, smoking, family history, diabetes"
    },
    "red_flags": {
      "max_marks": 3,
      "criteria": "Identifies red flags: sudden onset, radiation, diaphoresis, nausea/vomiting"
    },
    "differential": {
      "max_marks": 2,
      "criteria": "Considers appropriate differential diagnoses (ACS, aortic dissection, PE)"
    },
    "summary": {
      "max_marks": 1,
      "criteria": "Summarizes findings and suggests next steps (ECG, bloods, imaging)"
    }
  },
  "specialty": "cardiology",
  "difficulty": "medium",
  "time_limit_minutes": 8,
  "learning_objectives": [
    "Perform systematic cardiovascular history using SOCRATES",
    "Identify cardiovascular risk factors",
    "Recognize red flags for acute coronary syndrome",
    "Generate appropriate differential diagnoses"
  ],
  "key_points": [
    "Central crushing chest pain radiating to arm/jaw suggests ACS",
    "Diaphoresis + nausea are red flags for MI",
    "Multiple cardiovascular risk factors present",
    "Immediate ECG and troponin required"
  ],
  "red_flags": [
    "Sudden onset chest pain",
    "Radiation to arm/jaw",
    "Diaphoresis",
    "Nausea/vomiting",
    "Multiple CV risk factors"
  ],
  "australian_guidelines": {
    "etg": "Acute Coronary Syndromes (eTG complete)",
    "ahpra": "AHPRA Clinical Competency Standards Section 2.1.3",
    "nhmrc": "NHMRC Cardiovascular Disease Guidelines 2023"
  }
}
```

---

## How to Load Data into Database

### Option 1: Manual Database Seed Script (Recommended)

Create `scripts/seed_database.py`:

```python
#!/usr/bin/env python3
"""
Seed PostgreSQL database with MCQs and OSCEs from JSON files.

Usage:
    python3 scripts/seed_database.py --mcqs --osces
    python3 scripts/seed_database.py --mcqs-only
    python3 scripts/seed_database.py --osces-only
"""

import json
import argparse
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.src.db.models import MCQ, OSCE
from backend.src.db.base import Base

def load_mcqs(db: Session, force=False):
    """Load all MCQ JSON files into database"""
    mcq_dir = Path("data/mcqs/")
    json_files = list(mcq_dir.glob("*.json"))

    print(f"Found {len(json_files)} MCQ JSON files")

    total_loaded = 0
    total_updated = 0
    total_skipped = 0

    for json_file in json_files:
        print(f"\nProcessing: {json_file.name}")

        with open(json_file) as f:
            mcqs_data = json.load(f)

        for mcq_data in mcqs_data:
            question_id = mcq_data.get("question_id")

            if not question_id:
                print(f"  ⚠ Skipping MCQ without question_id")
                total_skipped += 1
                continue

            # Check if exists
            existing = db.query(MCQ).filter(MCQ.question_id == question_id).first()

            if existing and not force:
                print(f"  ⏭ Skipping {question_id} (already exists)")
                total_skipped += 1
                continue

            # Create or update MCQ
            mcq = MCQ(
                question_id=mcq_data["question_id"],
                question_text=mcq_data["question"],
                options=mcq_data["options"],
                correct_answer=mcq_data["correct_answer"],
                explanation=mcq_data["explanation"],
                citation=mcq_data["citation"],
                specialty=mcq_data["specialty"],
                difficulty=mcq_data.get("difficulty", "medium"),
                tags=mcq_data.get("tags", []),
                image_url=mcq_data.get("image_url"),
                image_caption=mcq_data.get("image_caption"),
                learning_points=mcq_data.get("learning_points"),
            )

            if existing:
                # Update existing
                db.merge(mcq)
                total_updated += 1
                print(f"  ✓ Updated {question_id}")
            else:
                # Insert new
                db.add(mcq)
                total_loaded += 1
                print(f"  ✓ Loaded {question_id}")

        db.commit()

    print(f"\n{'='*60}")
    print(f"MCQ Loading Complete")
    print(f"{'='*60}")
    print(f"Loaded: {total_loaded}")
    print(f"Updated: {total_updated}")
    print(f"Skipped: {total_skipped}")
    print(f"Total processed: {total_loaded + total_updated + total_skipped}")

def load_osces(db: Session, force=False):
    """Load all OSCE JSON files into database"""
    # Similar implementation for OSCEs
    pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mcqs", action="store_true", help="Load MCQs")
    parser.add_argument("--osces", action="store_true", help="Load OSCEs")
    parser.add_argument("--force", action="store_true", help="Update existing records")
    args = parser.parse_args()

    # Database connection
    DATABASE_URL = "postgresql://user:password@localhost/irstudy"
    engine = create_engine(DATABASE_URL)

    with Session(engine) as db:
        if args.mcqs:
            load_mcqs(db, force=args.force)
        if args.osces:
            load_osces(db, force=args.force)
```

### Option 2: Alembic Migration with Data Seed

Add data seeding to Alembic migration:

```python
# backend/alembic/versions/xxxx_seed_initial_data.py

def upgrade():
    # Load MCQs
    conn = op.get_bind()

    mcq_dir = Path("data/mcqs/")
    for json_file in mcq_dir.glob("*.json"):
        with open(json_file) as f:
            mcqs = json.load(f)

        for mcq in mcqs:
            conn.execute(
                text("""
                    INSERT INTO mcqs (question_id, question_text, options, correct_answer, ...)
                    VALUES (:question_id, :question_text, :options, :correct_answer, ...)
                    ON CONFLICT (question_id) DO NOTHING
                """),
                mcq
            )
```

### Option 3: Django-Style Fixtures

Create fixtures directory:

```
backend/fixtures/
├── mcqs.json (all MCQs combined)
└── osces.json (all OSCEs combined)
```

Load with:
```bash
python3 scripts/load_fixtures.py --fixture backend/fixtures/mcqs.json
```

---

## Recommended Next Steps

### 1. Create Database Seed Script

```bash
# Create seed script
touch scripts/seed_database.py
chmod +x scripts/seed_database.py

# Implement loading logic (see Option 1 above)
```

### 2. Run Database Seed

```bash
# Activate backend virtual environment
cd backend
source venv/bin/activate

# Run seed script
python3 ../scripts/seed_database.py --mcqs --osces

# Verify data loaded
psql -d irstudy -c "SELECT COUNT(*) FROM mcqs;"
psql -d irstudy -c "SELECT COUNT(*) FROM osces;"
```

### 3. Test API Endpoints

```bash
# Start backend
cd backend
uvicorn src.main:app --reload

# Test MCQ endpoints
curl http://localhost:8000/api/v1/mcqs
curl http://localhost:8000/api/v1/mcqs?specialty=cardiology
curl http://localhost:8000/api/v1/osces
```

### 4. Automate in CI/CD

Add to deployment pipeline:

```yaml
# .github/workflows/deploy.yml

- name: Seed Database
  run: |
    python3 scripts/seed_database.py --mcqs --osces --force
```

---

## Summary

### Current State
- ✅ MCQs/OSCEs generated and stored as JSON files
- ✅ Database schema defined in SQLAlchemy models
- ✅ API endpoints implemented in FastAPI
- ✅ Frontend components ready to consume API
- ⚠️ **Missing: Database seed script to load JSON → PostgreSQL**

### To Complete Data Flow
1. Create `scripts/seed_database.py`
2. Load all JSON files into PostgreSQL
3. Verify API endpoints return data
4. Test frontend integration

---

**Next Action:** Create database seed script to load `data/mcqs/*.json` and `data/osces/*.json` into PostgreSQL tables.
