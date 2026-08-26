#!/usr/bin/env python3
"""
Import OSCE scenarios from JSON files into database

PRD: PRD-MVP-003-CONTENT-POPULATION-MVP.md
Purpose: Import 140 OSCEs from data/osces/ directory

Usage:
    python3 scripts/import_osces.py --source /home/dev/Development/irStudy/data/osces/
    python3 scripts/import_osces.py --validate  # Dry run mode
"""

import sys
import json
import argparse
from pathlib import Path
from uuid import uuid4
from datetime import datetime

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from src.db.models import OSCE, MedicalSpecialty, DifficultyLevel, OSCEType
from src.db.base import Base, get_database_url


def load_osce_files(source_dir: Path) -> list[dict]:
    """Load OSCE scenarios from all JSON files in directory"""
    osces = []

    # Target main files
    target_files = [
        "cardiology_50_osces.json",
        "respiratory_50_osces.json",
        "psychiatry_40_osces.json"
    ]

    for filename in target_files:
        file_path = source_dir / filename
        if not file_path.exists():
            print(f"⚠️  File not found: {filename}")
            continue

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

                # Handle different JSON structures
                if isinstance(data, dict) and 'osces' in data:
                    osce_list = data['osces']
                elif isinstance(data, dict) and 'scenarios' in data:
                    osce_list = data['scenarios']
                elif isinstance(data, list):
                    osce_list = data
                else:
                    print(f"⚠️  Unknown JSON structure in {filename}")
                    continue

                print(f"✓ Loaded {len(osce_list)} OSCEs from {filename}")
                osces.extend(osce_list)

        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in {filename}: {e}")
        except Exception as e:
            print(f"❌ Error reading {filename}: {e}")

    # Also load any per-station *.osce.json files (Phase 6 workshop stations)
    for file_path in sorted(source_dir.glob("*.osce.json")):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            items = data if isinstance(data, list) else [data]
            osces.extend(items)
        except Exception as e:
            print(f"❌ Error reading {file_path.name}: {e}")
    if source_dir.glob("*.osce.json"):
        n = sum(1 for _ in source_dir.glob("*.osce.json"))
        if n:
            print(f"✓ Loaded {n} workshop station file(s) (*.osce.json)")

    return osces


def map_specialty(specialty_str: str) -> MedicalSpecialty:
    """Map specialty string to MedicalSpecialty enum"""
    specialty_map = {
        'cardiology': MedicalSpecialty.CARDIOLOGY,
        'respiratory': MedicalSpecialty.RESPIRATORY,
        'psychiatry': MedicalSpecialty.PSYCHIATRY,
        'general_practice': MedicalSpecialty.GENERAL_PRACTICE,
        'emergency': MedicalSpecialty.EMERGENCY_MEDICINE,
        'emergency_medicine': MedicalSpecialty.EMERGENCY_MEDICINE,
        'pediatrics': MedicalSpecialty.PAEDIATRICS,  # Australian spelling
        'paediatrics': MedicalSpecialty.PAEDIATRICS,
        'gastroenterology': MedicalSpecialty.GASTROENTEROLOGY,
        'neurology': MedicalSpecialty.NEUROLOGY,
        'endocrinology': MedicalSpecialty.ENDOCRINOLOGY,
        'obstetrics': MedicalSpecialty.OBSTETRICS_GYNAECOLOGY,
        'gynaecology': MedicalSpecialty.OBSTETRICS_GYNAECOLOGY,
        'obstetrics_gynaecology': MedicalSpecialty.OBSTETRICS_GYNAECOLOGY,
        'surgery': MedicalSpecialty.SURGERY,
        'ophthalmology': MedicalSpecialty.OPHTHALMOLOGY,
        'urology': MedicalSpecialty.UROLOGY,
        'musculoskeletal': MedicalSpecialty.MUSCULOSKELETAL,
    }

    specialty_lower = specialty_str.lower().strip()
    return specialty_map.get(specialty_lower, MedicalSpecialty.GENERAL_PRACTICE)


def map_difficulty(difficulty_str: str) -> DifficultyLevel:
    """Map difficulty string to DifficultyLevel enum"""
    difficulty_map = {
        'easy': DifficultyLevel.EASY,
        'medium': DifficultyLevel.MEDIUM,
        'hard': DifficultyLevel.HARD,
        'moderate': DifficultyLevel.MEDIUM
    }

    difficulty_lower = difficulty_str.lower().strip()
    return difficulty_map.get(difficulty_lower, DifficultyLevel.MEDIUM)


def map_osce_type(type_str: str) -> OSCEType:
    """Map OSCE type string to OSCEType enum"""
    type_map = {
        'history_taking': OSCEType.HISTORY_TAKING,
        'physical_examination': OSCEType.PHYSICAL_EXAMINATION,
        'counselling': OSCEType.COUNSELLING,
        'communication': OSCEType.COMMUNICATION,
        'diagnosis_management': OSCEType.DIAGNOSIS_MANAGEMENT,
        'emergency_scenario': OSCEType.EMERGENCY_SCENARIO,
        # legacy aliases
        'communication_skills': OSCEType.COMMUNICATION,
        'procedural': OSCEType.PHYSICAL_EXAMINATION,
    }

    type_lower = type_str.lower().strip() if type_str else 'history_taking'
    return type_map.get(type_lower, OSCEType.HISTORY_TAKING)


def import_osces(source_dir: str, dry_run: bool = False, validate: bool = False):
    """Import OSCE scenarios from JSON files into database"""

    print("=" * 60)
    print("OSCE Import Script")
    print("=" * 60)
    print(f"Source: {source_dir}")
    print(f"Mode: {'DRY RUN' if dry_run else 'IMPORT'}")
    print(f"Validation: {'YES' if validate else 'NO'}")
    print("")

    source_path = Path(source_dir)
    if not source_path.exists():
        print(f"❌ Source directory not found: {source_dir}")
        return 1

    # Load OSCEs from files
    print("Loading OSCE files...")
    osces_data = load_osce_files(source_path)
    print(f"\n✓ Total OSCEs loaded: {len(osces_data)}\n")

    if dry_run or len(osces_data) == 0:
        print(f"{'Dry run complete' if dry_run else 'No OSCEs to import'}")
        return 0

    # Connect to database
    try:
        DATABASE_URL = get_database_url()
        engine = create_engine(DATABASE_URL)

        # Create tables if they don't exist
        Base.metadata.create_all(engine)

        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return 1

    # Import OSCEs
    print("Importing OSCEs to database...")
    print("-" * 60)

    imported_count = 0
    skipped_count = 0
    error_count = 0

    for idx, osce_data in enumerate(osces_data, 1):
        try:
            # Extract OSCE ID (use existing or generate)
            osce_id = osce_data.get('id') or osce_data.get('osce_id') or str(uuid4())
            # osce_id column is VARCHAR(50); bound long IDs deterministically
            if len(osce_id) > 50:
                import hashlib
                suffix = hashlib.md5(osce_id.encode()).hexdigest()[:8]
                osce_id = osce_id[:41] + "-" + suffix

            # Check if OSCE already exists
            existing = db.query(OSCE).filter(OSCE.osce_id == osce_id).first()
            if existing:
                skipped_count += 1
                continue

            # Map specialty
            specialty_str = osce_data.get('specialty', 'general_practice')
            specialty = map_specialty(specialty_str)

            # Map difficulty
            difficulty_str = osce_data.get('difficulty', 'medium')
            difficulty = map_difficulty(difficulty_str)

            # Map OSCE type
            osce_type_str = osce_data.get('station_type') or osce_data.get('type', 'history_taking')
            osce_type = map_osce_type(osce_type_str)

            # Extract fields
            station_title = osce_data.get('title') or osce_data.get('station_title', f'OSCE {idx}')

            patient_instructions = (
                osce_data.get('patient_instructions') or
                osce_data.get('patient_presentation') or
                osce_data.get('scenario', '')
            )

            candidate_instructions = (
                osce_data.get('candidate_instructions') or
                osce_data.get('instructions', '')
            )

            rubric = (
                osce_data.get('rubric') or
                osce_data.get('marking_rubric') or
                osce_data.get('assessment_criteria', {})
            )

            # Extract optional fields
            learning_objectives = osce_data.get('learning_objectives', [])
            key_points = osce_data.get('key_points', [])
            red_flags = osce_data.get('red_flags', [])
            tags = osce_data.get('tags', [])
            time_limit = osce_data.get('time_limit_minutes', 8)
            examiner_instructions = osce_data.get('examiner_instructions')
            australian_guidelines = osce_data.get('australian_guidelines', [])

            # Create OSCE model
            osce = OSCE(
                osce_id=osce_id,
                station_title=station_title,
                station_type=osce_type,
                specialty=specialty,
                difficulty=difficulty,
                patient_instructions=patient_instructions,
                candidate_instructions=candidate_instructions,
                examiner_instructions=examiner_instructions,
                rubric=rubric,
                time_limit_minutes=time_limit,
                learning_objectives=learning_objectives,
                key_points=key_points,
                red_flags=red_flags,
                australian_guidelines=australian_guidelines,
                tags=tags,
                is_published=True
            )

            db.add(osce)
            imported_count += 1

            if imported_count % 10 == 0:
                print(f"  Imported {imported_count} OSCEs...")

        except IntegrityError:
            db.rollback()
            skipped_count += 1
        except Exception as e:
            print(f"  ❌ Error importing OSCE {idx}: {e}")
            db.rollback()
            error_count += 1

    # Commit all changes
    try:
        db.commit()
        print("-" * 60)
        print(f"\n✅ Import complete!")
        print(f"  - Imported: {imported_count}")
        print(f"  - Skipped (duplicates): {skipped_count}")
        print(f"  - Errors: {error_count}")
        print("")

        # Verify final count
        total_osces = db.query(OSCE).count()
        print(f"Total OSCEs in database: {total_osces}")

        # Show specialty distribution
        cardio_count = db.query(OSCE).filter(OSCE.specialty == MedicalSpecialty.CARDIOLOGY).count()
        resp_count = db.query(OSCE).filter(OSCE.specialty == MedicalSpecialty.RESPIRATORY).count()
        psych_count = db.query(OSCE).filter(OSCE.specialty == MedicalSpecialty.PSYCHIATRY).count()

        print("\nSpecialty Distribution:")
        print(f"  - Cardiology: {cardio_count}")
        print(f"  - Respiratory: {resp_count}")
        print(f"  - Psychiatry: {psych_count}")

    except Exception as e:
        print(f"❌ Commit failed: {e}")
        db.rollback()
        return 1
    finally:
        db.close()

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import OSCEs from JSON files")
    parser.add_argument(
        '--source',
        default='/home/dev/Development/irStudy/data/osces/',
        help='Source directory containing OSCE JSON files'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Load files but do not import to database'
    )
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate data structure without importing'
    )

    args = parser.parse_args()

    exit_code = import_osces(
        source_dir=args.source,
        dry_run=args.dry_run,
        validate=args.validate
    )

    sys.exit(exit_code)
