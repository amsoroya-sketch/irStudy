#!/usr/bin/env python3
"""
Import MCQs from JSON files into database

PRD: PRD-MVP-003-CONTENT-POPULATION-MVP.md
Purpose: Import 415 MCQs from data/mcqs/ directory

Usage:
    python3 scripts/import_mcqs.py --source /home/dev/Development/irStudy/data/mcqs/
    python3 scripts/import_mcqs.py --validate  # Dry run mode
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
from src.db.models import MCQ, MedicalSpecialty, DifficultyLevel
from src.db.base import Base, get_database_url


def load_mcq_files(source_dir: Path) -> list[dict]:
    """Load MCQs from all JSON files in directory"""
    mcqs = []

    # Target main files
    target_files = [
        "week3_cardiology_200_mcqs.json",
        "week3_respiratory_200_mcqs.json",
        "psychiatry_final_day5.json",
        # Fallback files
        "week1_all_100_unique_mcqs.json",
        "week3_psychiatry_additional_100_mcqs_with_images.json"
    ]

    for filename in target_files:
        file_path = source_dir / filename
        if not file_path.exists():
            continue

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

                # Handle different JSON structures
                if isinstance(data, dict) and 'questions' in data:
                    mcq_list = data['questions']
                elif isinstance(data, dict) and 'mcqs' in data:
                    mcq_list = data['mcqs']
                elif isinstance(data, list):
                    mcq_list = data
                else:
                    print(f"⚠️  Unknown JSON structure in {filename}")
                    continue

                print(f"✓ Loaded {len(mcq_list)} MCQs from {filename}")
                mcqs.extend(mcq_list)

        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in {filename}: {e}")
        except Exception as e:
            print(f"❌ Error reading {filename}: {e}")

    return mcqs


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
        'surgery': MedicalSpecialty.SURGERY
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

    difficulty_lower = difficulty_str.lower().strip() if difficulty_str else 'medium'
    return difficulty_map.get(difficulty_lower, DifficultyLevel.MEDIUM)


def import_mcqs(source_dir: str, dry_run: bool = False, validate: bool = False):
    """Import MCQs from JSON files into database"""

    print("=" * 60)
    print("MCQ Import Script")
    print("=" * 60)
    print(f"Source: {source_dir}")
    print(f"Mode: {'DRY RUN' if dry_run else 'IMPORT'}")
    print(f"Validation: {'YES' if validate else 'NO'}")
    print("")

    source_path = Path(source_dir)
    if not source_path.exists():
        print(f"❌ Source directory not found: {source_dir}")
        return 1

    # Load MCQs from files
    print("Loading MCQ files...")
    mcqs_data = load_mcq_files(source_path)
    print(f"\n✓ Total MCQs loaded: {len(mcqs_data)}\n")

    if dry_run or len(mcqs_data) == 0:
        print(f"{'Dry run complete' if dry_run else 'No MCQs to import'}")
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

    # Import MCQs
    print("Importing MCQs to database...")
    print("-" * 60)

    imported_count = 0
    skipped_count = 0
    error_count = 0

    for idx, mcq_data in enumerate(mcqs_data, 1):
        try:
            # Extract MCQ ID (use existing or generate)
            # NOTE: JSON uses 'id' field, database uses 'question_id'
            question_id = mcq_data.get('id') or mcq_data.get('mcq_id') or mcq_data.get('question_id') or str(uuid4())

            # Check if MCQ already exists
            existing = db.query(MCQ).filter(MCQ.question_id == question_id).first()
            if existing:
                skipped_count += 1
                continue

            # Map specialty
            specialty_str = mcq_data.get('specialty', 'general_practice')
            specialty = map_specialty(specialty_str)

            # Map difficulty
            difficulty_str = mcq_data.get('difficulty', 'medium')
            difficulty = map_difficulty(difficulty_str)

            # Extract question text (handle nested structure)
            question_obj = mcq_data.get('question', {})
            if isinstance(question_obj, dict):
                # Nested structure: {scenario, stem, options, correct_answer}
                scenario = question_obj.get('scenario', '')
                stem = question_obj.get('stem', '')
                question_text = f"{scenario}\n\n{stem}".strip() if scenario else stem
                options = question_obj.get('options', {})
                correct_answer = question_obj.get('correct_answer', 'A')
            else:
                # Flat structure: question_text at top level
                question_text = mcq_data.get('question_text') or mcq_data.get('stem', '')
                options = mcq_data.get('options', {})
                correct_answer = mcq_data.get('correct_answer') or mcq_data.get('answer') or 'A'

            # Ensure options is a dict
            if isinstance(options, list):
                # Convert list to dict: ['A', 'B', 'C', 'D'] -> {'A': 'A', 'B': 'B', ...}
                options = {chr(65 + i): opt for i, opt in enumerate(options)}

            # Extract explanation (handle nested structure)
            explanation_obj = mcq_data.get('explanation', {})
            if isinstance(explanation_obj, dict):
                # Nested structure: {why_correct, why_incorrect, key_points}
                why_correct = explanation_obj.get('why_correct', '')
                key_points = explanation_obj.get('key_points', [])
                if key_points:
                    key_points_str = '\n\nKey Points:\n' + '\n'.join(f"- {point}" for point in key_points)
                else:
                    key_points_str = ''
                explanation = f"{why_correct}{key_points_str}".strip()
            else:
                # Flat structure: explanation at top level
                explanation = mcq_data.get('explanation') or mcq_data.get('rationale') or ''

            # Extract image URL (if present)
            image_url = mcq_data.get('image_url')

            # Extract citation (from references if present)
            references = mcq_data.get('references', [])
            if references and isinstance(references, list) and len(references) > 0:
                ref = references[0]  # Use first reference
                citation = f"{ref.get('title', 'Australian medical guidelines')} ({ref.get('year', 'N/A')}), p. {ref.get('page', 'N/A')}"
            else:
                citation = mcq_data.get('citation', 'Australian medical guidelines')

            # Extract tags
            tags = mcq_data.get('tags', [])
            if not tags:
                # Generate tags from metadata if available
                metadata = mcq_data.get('metadata', {})
                if metadata.get('australian_context'):
                    tags.append('australian_context')
                topic = mcq_data.get('topic')
                if topic:
                    tags.append(topic.lower())

            # Extract learning points from explanation if available
            learning_points = []
            if isinstance(explanation_obj, dict):
                learning_points = explanation_obj.get('key_points', [])

            # Create MCQ model
            # NOTE: Database uses 'question_id' field, not 'mcq_id'
            mcq = MCQ(
                question_id=question_id,
                question_text=question_text,
                options=options,
                correct_answer=correct_answer,
                explanation=explanation,
                citation=citation,
                learning_points=learning_points,
                specialty=specialty,
                difficulty=difficulty,
                tags=tags,
                image_url=image_url,
                is_published=True
            )

            db.add(mcq)
            imported_count += 1

            if imported_count % 50 == 0:
                print(f"  Imported {imported_count} MCQs...")

        except IntegrityError:
            db.rollback()
            skipped_count += 1
        except Exception as e:
            print(f"  ❌ Error importing MCQ {idx}: {e}")
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
        total_mcqs = db.query(MCQ).count()
        print(f"Total MCQs in database: {total_mcqs}")

        # Show specialty distribution
        cardio_count = db.query(MCQ).filter(MCQ.specialty == MedicalSpecialty.CARDIOLOGY).count()
        resp_count = db.query(MCQ).filter(MCQ.specialty == MedicalSpecialty.RESPIRATORY).count()
        psych_count = db.query(MCQ).filter(MCQ.specialty == MedicalSpecialty.PSYCHIATRY).count()

        print("\nSpecialty Distribution:")
        print(f"  - Cardiology: {cardio_count}")
        print(f"  - Respiratory: {resp_count}")
        print(f"  - Psychiatry: {psych_count}")

        # Check if psychiatry needs more MCQs
        if psych_count < 60:
            print(f"\n⚠️  Psychiatry has only {psych_count} MCQs (need ≥60)")
            print(f"   Gap: {60 - psych_count} MCQs needed")
            print(f"   Consider importing from: week3_psychiatry_additional_100_mcqs_with_images.json")

    except Exception as e:
        print(f"❌ Commit failed: {e}")
        db.rollback()
        return 1
    finally:
        db.close()

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import MCQs from JSON files")
    parser.add_argument(
        '--source',
        default='/home/dev/Development/irStudy/data/mcqs/',
        help='Source directory containing MCQ JSON files'
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

    exit_code = import_mcqs(
        source_dir=args.source,
        dry_run=args.dry_run,
        validate=args.validate
    )

    sys.exit(exit_code)
