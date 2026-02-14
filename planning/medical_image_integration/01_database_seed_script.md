# Task 01: Database Seed Script

**Duration:** 4 hours
**Priority:** P0 (Critical Path)
**Dependencies:** None
**Output:** `scripts/seed_database.py`

---

## Objective

Create automated script to load all MCQ and OSCE JSON files into PostgreSQL database with validation, error handling, and progress reporting.

---

## Scope

### In Scope
- Parse all JSON files in `data/mcqs/` and `data/osces/`
- Validate JSON structure
- Insert into PostgreSQL using SQLAlchemy ORM
- Handle duplicates (upsert logic)
- Progress reporting with tqdm
- Error logging and recovery
- Dry-run mode for testing

### Out of Scope
- Image linking (covered in Task 09)
- User progress data (seeded separately)
- Frontend changes

---

## Prerequisites

### Files Needed
- **MCQ JSONs:** `data/mcqs/*.json` (~15 files, 1,000+ MCQs)
- **OSCE JSONs:** `data/osces/*.json` (~4 files, 140+ OSCEs)
- **Database Models:** `backend/src/db/models.py`
- **Database Config:** `backend/src/db/base.py`

### Environment
- PostgreSQL running (local or remote)
- Database `irstudy` created
- Environment variable `DATABASE_URL` set
- Backend virtual environment activated

---

## Implementation Steps

### Step 1: Script Structure (30 min)

**File:** `scripts/seed_database.py`

```python
#!/usr/bin/env python3
"""
Seed PostgreSQL database with MCQs and OSCEs from JSON files.

Usage:
    python3 scripts/seed_database.py --mcqs --osces
    python3 scripts/seed_database.py --mcqs-only
    python3 scripts/seed_database.py --osces-only
    python3 scripts/seed_database.py --dry-run
    python3 scripts/seed_database.py --force  # Update existing
"""

import argparse
import json
from pathlib import Path
from typing import List, Dict, Optional
import sys
from datetime import datetime

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from tqdm import tqdm

from src.db.models import MCQ, OSCE, MedicalSpecialty, DifficultyLevel, OSCEType
from src.db.base import Base

# Configuration
MCQ_DIR = Path("data/mcqs/")
OSCE_DIR = Path("data/osces/")
```

### Step 2: JSON Parsing Functions (1 hour)

```python
def parse_mcq_json(file_path: Path) -> List[Dict]:
    """Parse MCQ JSON file and return list of MCQ dicts"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Handle different JSON structures
    if isinstance(data, dict):
        if 'mcqs' in data:
            return data['mcqs']
        elif 'questions' in data:
            return data['questions']
        else:
            # Single MCQ wrapped in dict
            return [data] if 'id' in data else []
    elif isinstance(data, list):
        return data
    else:
        raise ValueError(f"Unknown JSON structure in {file_path}")

def normalize_specialty(specialty_str: str) -> Optional[MedicalSpecialty]:
    """Normalize specialty string to enum value"""
    specialty_map = {
        'cardiology': MedicalSpecialty.CARDIOLOGY,
        'respiratory': MedicalSpecialty.RESPIRATORY,
        'psychiatry': MedicalSpecialty.PSYCHIATRY,
        'neurology': MedicalSpecialty.NEUROLOGY,
        'emergency': MedicalSpecialty.EMERGENCY_MEDICINE,
        'emergency_medicine': MedicalSpecialty.EMERGENCY_MEDICINE,
        # Add all mappings
    }

    key = specialty_str.lower().replace(' ', '_')
    return specialty_map.get(key)

def normalize_difficulty(diff_str: str) -> DifficultyLevel:
    """Normalize difficulty string to enum value"""
    diff_map = {
        'easy': DifficultyLevel.EASY,
        'medium': DifficultyLevel.MEDIUM,
        'hard': DifficultyLevel.HARD,
    }
    return diff_map.get(diff_str.lower(), DifficultyLevel.MEDIUM)

def validate_mcq(mcq_data: Dict) -> tuple[bool, List[str]]:
    """Validate MCQ data structure"""
    errors = []

    # Required fields
    if 'id' not in mcq_data:
        errors.append("Missing 'id' field")

    # Question structure
    question = mcq_data.get('question', {})
    if not isinstance(question, dict):
        errors.append("'question' must be a dict")
    elif 'scenario' not in question or 'stem' not in question or 'options' not in question:
        errors.append("Question missing required fields")

    # Answer validation
    if 'answer' not in mcq_data:
        errors.append("Missing 'answer' field")

    # Options validation
    options = question.get('options', {})
    if not isinstance(options, dict) or len(options) < 2:
        errors.append("Options must be dict with at least 2 choices")

    return (len(errors) == 0, errors)
```

### Step 3: Database Insertion Logic (1.5 hours)

```python
def load_mcqs(db: Session, dry_run=False, force=False) -> Dict:
    """Load all MCQ JSON files into database"""
    stats = {
        'total_files': 0,
        'total_mcqs': 0,
        'loaded': 0,
        'updated': 0,
        'skipped': 0,
        'failed': 0,
        'errors': []
    }

    json_files = sorted(MCQ_DIR.glob("*.json"))
    stats['total_files'] = len(json_files)

    print(f"\n{'='*70}")
    print(f"MCQ Database Seeding")
    print(f"{'='*70}")
    print(f"Found {len(json_files)} JSON files")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print(f"Force update: {force}")
    print()

    for json_file in json_files:
        print(f"\nProcessing: {json_file.name}")

        try:
            mcqs_data = parse_mcq_json(json_file)
            stats['total_mcqs'] += len(mcqs_data)

            for mcq_data in tqdm(mcqs_data, desc=f"  {json_file.stem}"):
                # Validate
                valid, errors = validate_mcq(mcq_data)
                if not valid:
                    stats['failed'] += 1
                    stats['errors'].append({
                        'file': json_file.name,
                        'mcq_id': mcq_data.get('id', 'UNKNOWN'),
                        'errors': errors
                    })
                    continue

                question_id = mcq_data['id']

                # Check if exists
                existing = db.query(MCQ).filter(MCQ.question_id == question_id).first()

                if existing and not force:
                    stats['skipped'] += 1
                    continue

                # Prepare MCQ object
                question = mcq_data['question']
                mcq = MCQ(
                    question_id=question_id,
                    question_text=f"{question['scenario']}\n\n{question['stem']}",
                    options=question['options'],
                    correct_answer=mcq_data['answer'],
                    explanation=mcq_data.get('explanation', ''),
                    citation=mcq_data.get('citation', mcq_data.get('citations', [''])[0]),
                    specialty=normalize_specialty(mcq_data.get('specialty', 'general_practice')),
                    difficulty=normalize_difficulty(mcq_data.get('difficulty', 'medium')),
                    tags=mcq_data.get('tags', []),
                    image_url=mcq_data.get('image_url'),
                    image_caption=mcq_data.get('image_caption'),
                    learning_points=mcq_data.get('learning_points'),
                )

                if not dry_run:
                    if existing:
                        # Update
                        for key, value in mcq.__dict__.items():
                            if key != '_sa_instance_state' and key != 'id':
                                setattr(existing, key, value)
                        stats['updated'] += 1
                    else:
                        # Insert
                        db.add(mcq)
                        stats['loaded'] += 1

        except Exception as e:
            stats['errors'].append({
                'file': json_file.name,
                'error': str(e)
            })
            print(f"  ✗ Error: {e}")

    if not dry_run:
        db.commit()

    return stats

def load_osces(db: Session, dry_run=False, force=False) -> Dict:
    """Load all OSCE JSON files into database"""
    # Similar implementation as load_mcqs
    # Parse OSCE JSON structure
    # Validate OSCE fields
    # Insert/update OSCE records
    pass
```

### Step 4: CLI Interface (30 min)

```python
def print_stats(mcq_stats: Dict, osce_stats: Dict):
    """Print final statistics"""
    print(f"\n{'='*70}")
    print(f"SEEDING COMPLETE")
    print(f"{'='*70}\n")

    if mcq_stats:
        print(f"MCQs:")
        print(f"  Total JSON files: {mcq_stats['total_files']}")
        print(f"  Total MCQs found: {mcq_stats['total_mcqs']}")
        print(f"  Loaded (new): {mcq_stats['loaded']}")
        print(f"  Updated: {mcq_stats['updated']}")
        print(f"  Skipped: {mcq_stats['skipped']}")
        print(f"  Failed: {mcq_stats['failed']}")

        if mcq_stats['errors']:
            print(f"\n  Errors ({len(mcq_stats['errors'])}):")
            for err in mcq_stats['errors'][:5]:  # Show first 5
                print(f"    - {err}")

    if osce_stats:
        print(f"\nOSCEs:")
        print(f"  Total JSON files: {osce_stats['total_files']}")
        print(f"  Total OSCEs found: {osce_stats['total_osces']}")
        print(f"  Loaded (new): {osce_stats['loaded']}")
        print(f"  Updated: {osce_stats['updated']}")
        print(f"  Skipped: {osce_stats['skipped']}")
        print(f"  Failed: {osce_stats['failed']}")

def main():
    parser = argparse.ArgumentParser(
        description='Seed PostgreSQL database with MCQs and OSCEs from JSON files',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--mcqs', action='store_true', help='Load MCQs')
    parser.add_argument('--osces', action='store_true', help='Load OSCEs')
    parser.add_argument('--all', action='store_true', help='Load both MCQs and OSCEs')
    parser.add_argument('--force', action='store_true', help='Update existing records')
    parser.add_argument('--dry-run', action='store_true', help='Validate without inserting')
    parser.add_argument('--db-url', default=None, help='Database URL (or use DATABASE_URL env)')

    args = parser.parse_args()

    # Determine what to load
    load_mcqs_flag = args.mcqs or args.all
    load_osces_flag = args.osces or args.all

    if not (load_mcqs_flag or load_osces_flag):
        parser.error("Must specify --mcqs, --osces, or --all")

    # Database connection
    db_url = args.db_url or os.getenv('DATABASE_URL')
    if not db_url:
        parser.error("DATABASE_URL not set")

    engine = create_engine(db_url)

    # Run seeding
    with Session(engine) as db:
        mcq_stats = None
        osce_stats = None

        if load_mcqs_flag:
            mcq_stats = load_mcqs(db, dry_run=args.dry_run, force=args.force)

        if load_osces_flag:
            osce_stats = load_osces(db, dry_run=args.dry_run, force=args.force)

        print_stats(mcq_stats, osce_stats)

    print(f"\n{'✓' if args.dry_run else '✓✓'} Done!")

if __name__ == "__main__":
    main()
```

---

## Testing

### Unit Tests

```python
# tests/test_seed_database.py

def test_parse_mcq_json():
    """Test MCQ JSON parsing"""
    sample_json = {
        "mcqs": [{
            "id": "TEST-001",
            "question": {
                "scenario": "A patient presents...",
                "stem": "What is the diagnosis?",
                "options": {"A": "Option A", "B": "Option B"}
            },
            "answer": "A"
        }]
    }

    result = parse_mcq_json_from_dict(sample_json)
    assert len(result) == 1
    assert result[0]['id'] == 'TEST-001'

def test_validate_mcq():
    """Test MCQ validation"""
    valid_mcq = {
        "id": "TEST-001",
        "question": {
            "scenario": "...",
            "stem": "...",
            "options": {"A": "...", "B": "..."}
        },
        "answer": "A"
    }

    is_valid, errors = validate_mcq(valid_mcq)
    assert is_valid
    assert len(errors) == 0
```

### Integration Test

```bash
# Test with dry-run first
python3 scripts/seed_database.py --all --dry-run

# Test with sample data
python3 scripts/seed_database.py --mcqs

# Verify in database
psql -d irstudy -c "SELECT COUNT(*) FROM mcqs;"
psql -d irstudy -c "SELECT specialty, COUNT(*) FROM mcqs GROUP BY specialty;"
```

---

## Success Criteria

- [ ] Script parses all 15+ MCQ JSON files without errors
- [ ] Script parses all 4+ OSCE JSON files without errors
- [ ] 1,000+ MCQs inserted into database
- [ ] 140+ OSCEs inserted into database
- [ ] Duplicate handling works (no duplicate question_ids)
- [ ] Validation catches malformed JSON
- [ ] Dry-run mode works correctly
- [ ] Progress bars display properly
- [ ] Error reporting is comprehensive
- [ ] Database constraints respected (foreign keys, enums)

---

## Rollback Plan

If seeding fails:

```sql
-- Delete all MCQs
DELETE FROM mcq_attempts;
DELETE FROM mcqs;

-- Delete all OSCEs
DELETE FROM osces;

-- Verify clean
SELECT COUNT(*) FROM mcqs;    -- Should be 0
SELECT COUNT(*) FROM osces;   -- Should be 0
```

---

## Next Task

After completion, proceed to **Task 02: API Endpoint Verification**

File: `02_api_endpoint_verification.md`
