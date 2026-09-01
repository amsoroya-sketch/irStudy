#!/usr/bin/env python3
"""
Import peptic ulcer OSCE (GI-PUD-001) from video transcript to database

This script properly maps the comprehensive OSCE JSON to the simplified database schema.

Usage:
    python3 scripts/import_peptic_ulcer_osce_v2.py --dry-run  # Preview only
    python3 scripts/import_peptic_ulcer_osce_v2.py --execute  # Actually import
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db.models import OSCE, MedicalSpecialty, DifficultyLevel, OSCEType
from src.db.base import Base, get_database_url


def load_osce_json(file_path: Path) -> dict:
    """Load OSCE data from JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        sys.exit(1)


def convert_rubric_format(marking_criteria: list) -> dict:
    """Convert marking_criteria array to rubric dict format for database"""
    rubric = {}
    for item in marking_criteria:
        criterion_key = item['criterion'].lower().replace(' ', '_').replace('/', '_')
        rubric[criterion_key] = {
            'max_marks': item['max_marks'],
            'criteria': item['criterion'],
            'sub_criteria': item.get('sub_criteria', [])
        }
    return rubric


def create_osce_from_json(osce_data: dict) -> OSCE:
    """Create OSCE model from comprehensive JSON data"""

    # Basic fields
    osce_id = osce_data.get('osce_id')
    station_title = osce_data.get('title')  # Map 'title' to 'station_title'

    # Map station_type (our JSON has "history_taking", database has HISTORY_TAKING enum)
    station_type_str = osce_data.get('station_type', 'history_taking')
    station_type = OSCEType.HISTORY_TAKING  # Default
    if station_type_str == 'history_taking':
        station_type = OSCEType.HISTORY_TAKING
    elif station_type_str == 'physical_examination':
        station_type = OSCEType.PHYSICAL_EXAMINATION
    elif station_type_str == 'communication':
        station_type = OSCEType.COMMUNICATION

    # Map specialty
    specialty_str = osce_data.get('specialty', 'gastroenterology')
    specialty = MedicalSpecialty.GASTROENTEROLOGY
    if specialty_str == 'gastroenterology':
        specialty = MedicalSpecialty.GASTROENTEROLOGY
    elif specialty_str == 'general_practice':
        specialty = MedicalSpecialty.GENERAL_PRACTICE

    # Map difficulty
    difficulty_str = osce_data.get('difficulty', 'intermediate')
    difficulty = DifficultyLevel.MEDIUM
    if difficulty_str in ['intermediate', 'medium']:
        difficulty = DifficultyLevel.MEDIUM
    elif difficulty_str == 'easy':
        difficulty = DifficultyLevel.EASY
    elif difficulty_str == 'hard':
        difficulty = DifficultyLevel.HARD

    # Instructions
    candidate_instructions = osce_data.get('candidate_instructions', '')
    patient_instructions = osce_data.get('patient_instructions', '')
    examiner_instructions = osce_data.get('examiner_instructions', '')

    # Convert marking_criteria to rubric format
    marking_criteria = osce_data.get('marking_criteria', [])
    rubric = convert_rubric_format(marking_criteria)

    # Time limit
    time_limit_minutes = osce_data.get('duration_minutes', 8)

    # Educational content
    learning_objectives = osce_data.get('learning_objectives', [])
    key_points = osce_data.get('key_points', [])
    red_flags = osce_data.get('red_flags', [])
    tags = osce_data.get('tags', [])

    # Australian guidelines
    australian_guidelines = osce_data.get('australian_guidelines', [])

    # Create OSCE object with correct field names
    osce = OSCE(
        osce_id=osce_id,
        station_title=station_title,  # Not 'title'
        station_type=station_type,

        candidate_instructions=candidate_instructions,
        patient_instructions=patient_instructions,
        examiner_instructions=examiner_instructions,

        rubric=rubric,

        specialty=specialty,
        difficulty=difficulty,
        time_limit_minutes=time_limit_minutes,

        learning_objectives=learning_objectives,
        key_points=key_points,
        red_flags=red_flags,
        tags=tags,

        australian_guidelines=australian_guidelines,

        times_practiced=0,
        average_score=0.0,
        is_published=True
    )

    return osce


def import_osce(osce_file: str, dry_run: bool = True):
    """Import OSCE from JSON file to database"""

    print("=" * 80)
    print("PEPTIC ULCER OSCE IMPORT - Video Transcript Conversion (v2)")
    print("=" * 80)
    print(f"Source: {osce_file}")
    print(f"Mode: {'DRY RUN' if dry_run else 'IMPORT'}")
    print("=" * 80)
    print()

    # Load JSON
    osce_path = Path(osce_file)
    if not osce_path.exists():
        print(f"❌ File not found: {osce_file}")
        return 1

    print(f"Loading OSCE data from {osce_path.name}...")
    osce_data = load_osce_json(osce_path)

    # Display OSCE details
    print(f"\nOSCE Details:")
    print(f"  ID: {osce_data.get('osce_id')}")
    print(f"  Title: {osce_data.get('title')}")
    print(f"  Specialty: {osce_data.get('specialty')}")
    print(f"  Difficulty: {osce_data.get('difficulty')}")
    print(f"  Station Type: {osce_data.get('station_type')}")
    print(f"  Duration: {osce_data.get('duration_minutes')} minutes")
    print(f"  Total Marks: {osce_data.get('total_marks')}")
    print(f"  Marking Criteria: {len(osce_data.get('marking_criteria', []))} items")
    print(f"  Learning Objectives: {len(osce_data.get('learning_objectives', []))}")
    print(f"  Key Points: {len(osce_data.get('key_points', []))}")
    print(f"  Red Flags: {len(osce_data.get('red_flags', []))}")
    print(f"  Tags: {len(osce_data.get('tags', []))}")
    print()

    # Create OSCE object
    print("Creating OSCE object...")
    try:
        osce = create_osce_from_json(osce_data)
        print(f"✓ OSCE object created successfully")
        print(f"  - station_title: {osce.station_title}")
        print(f"  - station_type: {osce.station_type}")
        print(f"  - specialty: {osce.specialty}")
        print(f"  - difficulty: {osce.difficulty}")
        print(f"  - rubric keys: {list(osce.rubric.keys())}")
        print()
    except Exception as e:
        print(f"❌ Error creating OSCE object: {e}")
        import traceback
        traceback.print_exc()
        return 1

    if dry_run:
        print("=" * 80)
        print("✅ DRY RUN SUCCESSFUL")
        print("=" * 80)
        print("OSCE data structure is valid and ready for import")
        print("\nTo import to database, run:")
        print("  python3 scripts/import_peptic_ulcer_osce_v2.py --execute")
        print("=" * 80)
        return 0

    # Connect to database
    print("Connecting to database...")
    try:
        DATABASE_URL = get_database_url()
        engine = create_engine(DATABASE_URL)
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        print("✓ Database connection established")
        print()

        # Check if OSCE already exists
        existing = db.query(OSCE).filter(OSCE.osce_id == osce.osce_id).first()
        if existing:
            print(f"⚠️  OSCE {osce.osce_id} already exists in database")
            print(f"    Existing: {existing.station_title}")
            response = input("\nOverwrite existing OSCE? (yes/no): ")
            if response.lower() != 'yes':
                print("❌ Import cancelled by user")
                db.close()
                return 1
            print(f"✓ Deleting existing OSCE...")
            db.delete(existing)
            db.commit()

        # Add to database
        print("Adding OSCE to database...")
        db.add(osce)
        db.commit()
        db.refresh(osce)

        print()
        print("=" * 80)
        print("✅ IMPORT SUCCESSFUL")
        print("=" * 80)
        print(f"OSCE ID: {osce.osce_id}")
        print(f"Database ID: {osce.id}")
        print(f"Station Title: {osce.station_title}")
        print(f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        print("Access via API:")
        print(f"  http://localhost:8001/api/v1/osces/{osce.id}")
        print(f"  http://localhost:8001/api/v1/osces?specialty=gastroenterology")
        print()
        print("Access via Frontend:")
        print(f"  http://localhost:5173")
        print("  → Navigate to OSCE Practice → Filter by Gastroenterology")
        print("=" * 80)

        # Verify import
        print()
        print("Verifying import...")
        count = db.query(OSCE).filter(OSCE.specialty == MedicalSpecialty.GASTROENTEROLOGY).count()
        print(f"✓ Total Gastroenterology OSCEs in database: {count}")

        db.close()
        return 0

    except Exception as e:
        print(f"❌ Database error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Import peptic ulcer OSCE from video transcript (v2 - properly formatted)"
    )
    parser.add_argument(
        '--file',
        default='../data/osces/gastroenterology_peptic_ulcer_osce.json',
        help='Path to OSCE JSON file'
    )
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode (default)')
    parser.add_argument('--execute', action='store_true', help='Execute import')

    args = parser.parse_args()

    dry_run = not args.execute
    if dry_run:
        print("\n⚠️  DRY RUN MODE - Use --execute to perform actual import\n")

    exit_code = import_osce(args.file, dry_run=dry_run)
    sys.exit(exit_code)
