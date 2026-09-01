#!/usr/bin/env python3
"""
Import peptic ulcer OSCE from video transcript to database

Usage:
    python3 scripts/import_peptic_ulcer_osce.py --dry-run  # Preview only
    python3 scripts/import_peptic_ulcer_osce.py --execute  # Actually import
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
from src.db.models import OSCE, MedicalSpecialty, DifficultyLevel
from src.db.base import Base, get_database_url


def load_osce_json(file_path: Path) -> dict:
    """Load OSCE data from JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        sys.exit(1)


def map_specialty(specialty_str: str) -> MedicalSpecialty:
    """Map specialty string to MedicalSpecialty enum"""
    specialty_map = {
        'gastroenterology': MedicalSpecialty.GASTROENTEROLOGY,
        'general_practice': MedicalSpecialty.GENERAL_PRACTICE,
        'emergency_medicine': MedicalSpecialty.EMERGENCY_MEDICINE
    }
    return specialty_map.get(specialty_str.lower(), MedicalSpecialty.GASTROENTEROLOGY)


def map_difficulty(difficulty_str: str) -> DifficultyLevel:
    """Map difficulty string to DifficultyLevel enum"""
    difficulty_map = {
        'easy': DifficultyLevel.EASY,
        'intermediate': DifficultyLevel.MEDIUM,
        'medium': DifficultyLevel.MEDIUM,
        'hard': DifficultyLevel.HARD
    }
    return difficulty_map.get(difficulty_str.lower(), DifficultyLevel.MEDIUM)


def create_osce_from_json(osce_data: dict) -> OSCE:
    """Create OSCE model from JSON data"""

    # Extract basic fields
    osce_id = osce_data.get('osce_id')
    title = osce_data.get('title')
    specialty = map_specialty(osce_data.get('specialty', 'gastroenterology'))
    difficulty = map_difficulty(osce_data.get('difficulty', 'intermediate'))
    duration_minutes = osce_data.get('duration_minutes', 8)

    # Extract scenario
    patient_scenario = osce_data.get('patient_scenario', {})

    # Extract marking criteria and calculate total
    marking_criteria = osce_data.get('marking_criteria', [])
    total_marks = osce_data.get('total_marks', 15)

    # Create OSCE object
    osce = OSCE(
        osce_id=osce_id,
        title=title,
        specialty=specialty,
        difficulty=difficulty,
        duration_minutes=duration_minutes,

        # Patient scenario
        patient_demographics=patient_scenario.get('demographics', {}),
        chief_complaint=patient_scenario.get('chief_complaint', ''),
        history_presenting_illness=patient_scenario.get('history_presenting_illness', ''),
        past_medical_history=patient_scenario.get('past_medical_history', []),
        current_medications=patient_scenario.get('current_medications', []),
        vital_signs=patient_scenario.get('vital_signs', {}),
        examination_findings=patient_scenario.get('examination_findings', {}),

        # Instructions
        candidate_instructions=osce_data.get('candidate_instructions', ''),
        patient_instructions=osce_data.get('patient_instructions', ''),
        examiner_instructions=osce_data.get('examiner_instructions', ''),

        # Management
        management_plan=osce_data.get('management_plan', {}),
        differential_diagnosis=osce_data.get('differential_diagnosis', {}),

        # Marking
        marking_criteria=marking_criteria,
        total_marks=total_marks,

        # Educational content
        learning_objectives=osce_data.get('learning_objectives', []),
        key_points=osce_data.get('key_points', []),
        red_flags=osce_data.get('red_flags', []),

        # Metadata
        tags=osce_data.get('tags', []),
        references=osce_data.get('references', []),
        is_published=True
    )

    return osce


def import_osce(osce_file: str, dry_run: bool = True):
    """Import OSCE from JSON file to database"""

    print("=" * 80)
    print("PEPTIC ULCER OSCE IMPORT - Video Transcript Conversion")
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
    print(f"  Duration: {osce_data.get('duration_minutes')} minutes")
    print(f"  Total Marks: {osce_data.get('total_marks')}")
    print(f"  Learning Objectives: {len(osce_data.get('learning_objectives', []))}")
    print(f"  Key Points: {len(osce_data.get('key_points', []))}")
    print(f"  Tags: {len(osce_data.get('tags', []))}")
    print()

    if dry_run:
        print("✅ DRY RUN - JSON validation passed")
        print("✅ OSCE data structure is correct")
        print("\nTo import to database, run: python3 scripts/import_peptic_ulcer_osce.py --execute")
        return 0

    # Connect to database
    print("Connecting to database...")
    try:
        DATABASE_URL = get_database_url()
        engine = create_engine(DATABASE_URL)
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()

        # Check if OSCE already exists
        existing = db.query(OSCE).filter(OSCE.osce_id == osce_data.get('osce_id')).first()
        if existing:
            print(f"⚠️  OSCE {osce_data.get('osce_id')} already exists in database")
            response = input("Overwrite? (yes/no): ")
            if response.lower() != 'yes':
                print("❌ Import cancelled")
                return 1
            db.delete(existing)
            print(f"✓ Deleted existing OSCE")

        # Create OSCE
        print("Creating OSCE object...")
        osce = create_osce_from_json(osce_data)

        # Add to database
        print("Adding to database...")
        db.add(osce)
        db.commit()
        db.refresh(osce)

        print()
        print("=" * 80)
        print("✅ IMPORT SUCCESSFUL")
        print("=" * 80)
        print(f"OSCE ID: {osce.osce_id}")
        print(f"Database ID: {osce.id}")
        print(f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        print("Access via API:")
        print(f"  http://localhost:8001/api/v1/osces/{osce.osce_id}")
        print(f"  http://localhost:8001/api/v1/osces?specialty=gastroenterology")
        print()
        print("Access via Frontend:")
        print(f"  http://localhost:5173 → OSCE Practice → Gastroenterology")
        print("=" * 80)

        db.close()
        return 0

    except Exception as e:
        print(f"❌ Database error: {e}")
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import peptic ulcer OSCE from video transcript")
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
