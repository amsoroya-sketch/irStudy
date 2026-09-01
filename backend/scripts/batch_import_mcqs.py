#!/usr/bin/env python3
"""
Batch import additional MCQs from multiple JSON files

Purpose: Import 600-800 additional real MCQs from data/mcqs/ directory
Avoids duplicates by checking existing question_ids
"""

import sys
import json
import argparse
from pathlib import Path
from uuid import uuid4

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from src.db.models import MCQ, MedicalSpecialty, DifficultyLevel
from src.db.base import Base, get_database_url


# Priority files to import
TARGET_FILES = [
    "missing_topics_comprehensive_mcqs.json",
    "missing_psychiatry_150_mcqs.json",
    "week1_all_100_unique_mcqs.json",
    "week1_regenerated_100_mcqs.json",
    "week1_additional_65_mcqs.json",
    "week3_psychiatry_additional_100_mcqs.json",
    "week2_day6_psychiatry_80_mcqs.json",
    "psychiatry_depression_day1.json",
    "psychiatry_anxiety_bipolar_day2.json",
    "psychiatry_psychosis_day3.json",
    "psychiatry_suicide_mha_day4.json",
    "psychiatry_final_day5.json",
]


def map_specialty(specialty_str: str) -> MedicalSpecialty:
    """Map specialty string to MedicalSpecialty enum"""
    specialty_map = {
        'cardiology': MedicalSpecialty.CARDIOLOGY,
        'respiratory': MedicalSpecialty.RESPIRATORY,
        'psychiatry': MedicalSpecialty.PSYCHIATRY,
        'general_practice': MedicalSpecialty.GENERAL_PRACTICE,
        'emergency': MedicalSpecialty.EMERGENCY_MEDICINE,
        'emergency_medicine': MedicalSpecialty.EMERGENCY_MEDICINE,
        'pediatrics': MedicalSpecialty.PAEDIATRICS,
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


def load_json_file(file_path: Path) -> list:
    """Load MCQs from a single JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Handle different JSON structures
        if isinstance(data, dict):
            if 'mcqs' in data:
                return data['mcqs']
            elif 'questions' in data:
                return data['questions']
            else:
                # Look for any list in the dict
                for key, value in data.items():
                    if isinstance(value, list) and len(value) > 0:
                        return value
        elif isinstance(data, list):
            return data

        return []
    except Exception as e:
        print(f"  ❌ Error reading file: {e}")
        return []


def process_mcq_data(mcq_data: dict) -> dict:
    """Process MCQ data and extract fields"""

    # Extract question ID
    question_id = (
        mcq_data.get('id') or
        mcq_data.get('mcq_id') or
        mcq_data.get('question_id') or
        f"IMPORTED-{uuid4().hex[:12].upper()}"
    )

    # Extract question text (handle nested structure)
    question_obj = mcq_data.get('question', {})
    if isinstance(question_obj, dict):
        scenario = question_obj.get('scenario', '')
        stem = question_obj.get('stem', '')
        question_text = f"{scenario}\n\n{stem}".strip() if scenario else stem
        options = question_obj.get('options', {})
        correct_answer = question_obj.get('correct_answer', 'A')
    else:
        question_text = mcq_data.get('question_text') or mcq_data.get('stem', '')
        options = mcq_data.get('options', {})
        correct_answer = mcq_data.get('correct_answer') or mcq_data.get('answer') or 'A'

    # Convert options list to dict if needed
    if isinstance(options, list):
        options = {chr(65 + i): opt for i, opt in enumerate(options)}

    # Extract explanation
    explanation_obj = mcq_data.get('explanation', {})
    if isinstance(explanation_obj, dict):
        why_correct = explanation_obj.get('why_correct', '')
        key_points = explanation_obj.get('key_points', [])
        if key_points:
            key_points_str = '\n\nKey Points:\n' + '\n'.join(f"- {point}" for point in key_points)
        else:
            key_points_str = ''
        explanation = f"{why_correct}{key_points_str}".strip()
    else:
        explanation = mcq_data.get('explanation') or mcq_data.get('rationale') or ''

    # Extract other fields
    specialty = map_specialty(mcq_data.get('specialty', 'general_practice'))
    difficulty = map_difficulty(mcq_data.get('difficulty', 'medium'))
    image_url = mcq_data.get('image_url')

    # Extract citation
    references = mcq_data.get('references', [])
    if references and isinstance(references, list) and len(references) > 0:
        ref = references[0]
        citation = f"{ref.get('title', 'Australian guidelines')} ({ref.get('year', 'N/A')})"
    else:
        citation = mcq_data.get('citation', 'Australian medical guidelines')

    # Extract tags
    tags = mcq_data.get('tags', [])
    if not tags:
        topic = mcq_data.get('topic')
        if topic:
            tags.append(topic.lower())

    # Extract learning points
    learning_points = []
    if isinstance(explanation_obj, dict):
        learning_points = explanation_obj.get('key_points', [])

    return {
        'question_id': question_id,
        'question_text': question_text,
        'options': options,
        'correct_answer': correct_answer,
        'explanation': explanation,
        'specialty': specialty,
        'difficulty': difficulty,
        'citation': citation,
        'tags': tags,
        'learning_points': learning_points,
        'image_url': image_url,
        'is_published': True,
        'requires_australian_context': True
    }


def batch_import(source_dir: str, dry_run: bool = False):
    """Import MCQs from multiple files"""

    print("=" * 80)
    print("BATCH MCQ IMPORT - Additional Content")
    print("=" * 80)
    print(f"Source: {source_dir}")
    print(f"Mode: {'DRY RUN' if dry_run else 'IMPORT'}")
    print("=" * 80)
    print()

    source_path = Path(source_dir)
    if not source_path.exists():
        print(f"❌ Source directory not found: {source_dir}")
        return 1

    # Connect to database
    if not dry_run:
        try:
            DATABASE_URL = get_database_url()
            engine = create_engine(DATABASE_URL)
            Base.metadata.create_all(engine)
            SessionLocal = sessionmaker(bind=engine)
            db = SessionLocal()

            # Get existing question IDs
            existing_ids = set(mcq.question_id for mcq in db.query(MCQ.question_id).all())
            print(f"Existing MCQs in database: {len(existing_ids)}\n")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return 1
    else:
        existing_ids = set()

    # Process each file
    total_imported = 0
    total_skipped = 0
    total_errors = 0

    for filename in TARGET_FILES:
        file_path = source_path / filename
        if not file_path.exists():
            print(f"⚠️  File not found: {filename}")
            continue

        print(f"Processing: {filename}")
        mcq_list = load_json_file(file_path)

        if not mcq_list:
            print(f"  ⚠️  No MCQs found\n")
            continue

        imported = 0
        skipped = 0
        errors = 0

        for mcq_data in mcq_list:
            try:
                # Process MCQ data
                processed = process_mcq_data(mcq_data)

                # Check for duplicates
                if processed['question_id'] in existing_ids:
                    skipped += 1
                    continue

                # Check for dummy content
                options_str = str(processed['options'])
                if 'Option A' in options_str and 'Option B' in options_str:
                    skipped += 1
                    continue

                if dry_run:
                    imported += 1
                else:
                    # Create MCQ model
                    mcq = MCQ(**processed)
                    db.add(mcq)
                    existing_ids.add(processed['question_id'])
                    imported += 1

            except Exception as e:
                errors += 1
                print(f"  ❌ Error processing MCQ: {str(e)[:100]}")

        # Commit after each file
        if not dry_run and imported > 0:
            try:
                db.commit()
                print(f"  ✓ Imported: {imported} | Skipped: {skipped} | Errors: {errors}\n")
            except Exception as e:
                db.rollback()
                print(f"  ❌ Database commit failed: {e}\n")
                errors += imported
                imported = 0
        else:
            print(f"  ✓ Would import: {imported} | Skipped: {skipped} | Errors: {errors}\n")

        total_imported += imported
        total_skipped += skipped
        total_errors += errors

    if not dry_run:
        db.close()

    # Summary
    print("=" * 80)
    print("IMPORT SUMMARY")
    print("=" * 80)
    print(f"Total Imported: {total_imported}")
    print(f"Total Skipped: {total_skipped}")
    print(f"Total Errors: {total_errors}")
    print(f"New Total MCQs: {len(existing_ids) if not dry_run else f'{len(existing_ids)} + {total_imported}'}")
    print("=" * 80)

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch import MCQs from JSON files")
    parser.add_argument('--source', default='../data/mcqs', help='Source directory')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode')
    parser.add_argument('--execute', action='store_true', help='Execute import')

    args = parser.parse_args()

    dry_run = not args.execute
    if dry_run:
        print("\n⚠️  DRY RUN MODE - Use --execute to perform actual import\n")

    exit_code = batch_import(args.source, dry_run=dry_run)
    sys.exit(exit_code)
