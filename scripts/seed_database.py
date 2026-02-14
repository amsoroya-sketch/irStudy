#!/usr/bin/env python3
"""
Seed PostgreSQL database with MCQs and OSCEs from JSON files.

Usage:
    python3 scripts/seed_database.py --mcqs --osces
    python3 scripts/seed_database.py --mcqs-only
    python3 scripts/seed_database.py --osces-only
    python3 scripts/seed_database.py --all --dry-run
    python3 scripts/seed_database.py --all --force  # Update existing
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

from src.db.models import MCQ, OSCE, StudyCard, MedicalSpecialty, DifficultyLevel, OSCEType
from src.db.base import Base

# Configuration
MCQ_DIR = Path("data/mcqs/")
OSCE_DIR = Path("data/osces/")
STUDY_CARD_DIR = Path("data/study_cards/")


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


def parse_osce_json(file_path: Path) -> List[Dict]:
    """Parse OSCE JSON file and return list of OSCE dicts"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Handle different JSON structures
    if isinstance(data, dict):
        if 'osces' in data:
            return data['osces']
        elif 'stations' in data:
            return data['stations']
        else:
            # Single OSCE wrapped in dict
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
        'gastroenterology': MedicalSpecialty.GASTROENTEROLOGY,
        'neurology': MedicalSpecialty.NEUROLOGY,
        'psychiatry': MedicalSpecialty.PSYCHIATRY,
        'endocrinology': MedicalSpecialty.ENDOCRINOLOGY,
        'emergency': MedicalSpecialty.EMERGENCY_MEDICINE,
        'emergency_medicine': MedicalSpecialty.EMERGENCY_MEDICINE,
        'general_practice': MedicalSpecialty.GENERAL_PRACTICE,
        'paediatrics': MedicalSpecialty.PAEDIATRICS,
        'pediatrics': MedicalSpecialty.PAEDIATRICS,
        'obstetrics': MedicalSpecialty.OBSTETRICS_GYNAECOLOGY,
        'obstetrics_gynaecology': MedicalSpecialty.OBSTETRICS_GYNAECOLOGY,
        'obgyn': MedicalSpecialty.OBSTETRICS_GYNAECOLOGY,
        'surgery': MedicalSpecialty.SURGERY,
    }

    key = specialty_str.lower().replace(' ', '_').replace('-', '_')
    return specialty_map.get(key, MedicalSpecialty.GENERAL_PRACTICE)


def normalize_difficulty(diff_str: str) -> DifficultyLevel:
    """Normalize difficulty string to enum value"""
    diff_map = {
        'easy': DifficultyLevel.EASY,
        'medium': DifficultyLevel.MEDIUM,
        'hard': DifficultyLevel.HARD,
    }
    return diff_map.get(diff_str.lower(), DifficultyLevel.MEDIUM)


def normalize_station_type(type_str: str) -> OSCEType:
    """Normalize OSCE station type to enum value"""
    type_map = {
        'history': OSCEType.HISTORY_TAKING,
        'history_taking': OSCEType.HISTORY_TAKING,
        'examination': OSCEType.PHYSICAL_EXAMINATION,
        'physical_examination': OSCEType.PHYSICAL_EXAMINATION,
        'counselling': OSCEType.COUNSELLING,
        'communication': OSCEType.COMMUNICATION,
        'diagnosis': OSCEType.DIAGNOSIS_MANAGEMENT,
        'management': OSCEType.DIAGNOSIS_MANAGEMENT,
        'diagnosis_management': OSCEType.DIAGNOSIS_MANAGEMENT,
        'emergency': OSCEType.EMERGENCY_SCENARIO,
        'emergency_scenario': OSCEType.EMERGENCY_SCENARIO,
    }
    return type_map.get(type_str.lower(), OSCEType.DIAGNOSIS_MANAGEMENT)


def validate_mcq(mcq_data: Dict) -> tuple[bool, List[str]]:
    """Validate MCQ data structure"""
    errors = []

    # Required fields
    if 'id' not in mcq_data:
        errors.append("Missing 'id' field")

    # Question structure
    if 'question' in mcq_data:
        question = mcq_data.get('question', {})
        if not isinstance(question, dict):
            errors.append("'question' must be a dict")
        elif 'options' not in question:
            errors.append("Question missing 'options' field")
    else:
        errors.append("Missing 'question' field")

    # Answer validation
    if 'correct_answer' not in mcq_data:
        errors.append("Missing 'correct_answer' field")

    return (len(errors) == 0, errors)


def validate_osce(osce_data: Dict) -> tuple[bool, List[str]]:
    """Validate OSCE data structure"""
    errors = []

    # Required fields
    if 'id' not in osce_data:
        errors.append("Missing 'id' field")

    return (len(errors) == 0, errors)


def extract_citation(references: List[Dict]) -> str:
    """Extract citation string from references array"""
    if not references:
        return "No citation available"

    # Take first reference
    ref = references[0]
    title = ref.get('title', 'Unknown')
    author = ref.get('author', 'Unknown Author')
    year = ref.get('year', '')
    page = ref.get('page', '')

    citation = f"{title} by {author}"
    if year:
        citation += f" ({year})"
    if page:
        citation += f", p.{page}"

    return citation


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

                # Extract question parts
                question = mcq_data['question']
                scenario = question.get('scenario', '')
                stem = question.get('stem', '')
                question_text = f"{scenario}\n\n{stem}" if scenario else stem

                # Extract options (ensure dict format)
                options = question.get('options', {})
                if not isinstance(options, dict):
                    # Convert list to dict
                    options = {chr(65+i): opt for i, opt in enumerate(options)}

                # Extract citation
                references = mcq_data.get('references', [])
                citation = extract_citation(references)

                # Extract learning points
                learning_objectives = mcq_data.get('learning_objectives', [])
                learning_points = learning_objectives if learning_objectives else None

                # Extract tags
                tags = []
                if mcq_data.get('topic'):
                    tags.append(mcq_data['topic'])
                if mcq_data.get('subtopic'):
                    tags.append(mcq_data['subtopic'])

                # Prepare MCQ object
                mcq = MCQ(
                    question_id=question_id,
                    question_text=question_text,
                    options=options,
                    correct_answer=mcq_data['correct_answer'],
                    explanation=mcq_data.get('explanation', ''),
                    citation=citation,
                    specialty=normalize_specialty(mcq_data.get('specialty', 'general_practice')),
                    difficulty=normalize_difficulty(mcq_data.get('difficulty', 'medium')),
                    tags=tags if tags else None,
                    learning_points=learning_points,
                    image_url=mcq_data.get('image_url'),
                    image_caption=mcq_data.get('image_caption'),
                )

                if not dry_run:
                    if existing:
                        # Update
                        for key, value in mcq.__dict__.items():
                            if key not in ['_sa_instance_state', 'id', 'created_at', 'times_attempted', 'times_correct', 'average_time_seconds']:
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
        try:
            db.commit()
        except IntegrityError as e:
            db.rollback()
            print(f"  ✗ Integrity error during commit: {e}")

    return stats


def load_osces(db: Session, dry_run=False, force=False) -> Dict:
    """Load all OSCE JSON files into database"""
    stats = {
        'total_files': 0,
        'total_osces': 0,
        'loaded': 0,
        'updated': 0,
        'skipped': 0,
        'failed': 0,
        'errors': []
    }

    json_files = sorted(OSCE_DIR.glob("*.json"))
    stats['total_files'] = len(json_files)

    print(f"\n{'='*70}")
    print(f"OSCE Database Seeding")
    print(f"{'='*70}")
    print(f"Found {len(json_files)} JSON files")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print(f"Force update: {force}")
    print()

    for json_file in json_files:
        print(f"\nProcessing: {json_file.name}")

        try:
            osces_data = parse_osce_json(json_file)
            stats['total_osces'] += len(osces_data)

            for osce_data in tqdm(osces_data, desc=f"  {json_file.stem}"):
                # Validate
                valid, errors = validate_osce(osce_data)
                if not valid:
                    stats['failed'] += 1
                    stats['errors'].append({
                        'file': json_file.name,
                        'osce_id': osce_data.get('id', 'UNKNOWN'),
                        'errors': errors
                    })
                    continue

                osce_id = osce_data['id']

                # Check if exists
                existing = db.query(OSCE).filter(OSCE.osce_id == osce_id).first()

                if existing and not force:
                    stats['skipped'] += 1
                    continue

                # Map JSON structure to DB model
                scenario = osce_data.get('scenario', {})

                # Extract station title
                station_title = osce_data.get('topic', '') or osce_data.get('id', '')

                # Determine station type
                scenario_type = osce_data.get('scenario_type', '').lower()
                station_type = normalize_station_type(scenario_type if scenario_type else 'diagnosis_management')

                # Patient instructions
                patient_presentation = scenario.get('patient_presentation', '')
                vital_signs = scenario.get('vital_signs', {})
                history = scenario.get('history', '')
                examination = scenario.get('examination_findings', '')

                patient_instructions = f"""Patient Presentation:
{patient_presentation}

Vital Signs:
{json.dumps(vital_signs, indent=2) if vital_signs else 'Not specified'}

History:
{history}

Examination Findings:
{examination}
"""

                # Candidate instructions
                tasks = osce_data.get('tasks', [])
                candidate_instructions = f"""Tasks:
"""
                for task in tasks:
                    candidate_instructions += f"\n{task.get('task_number', '')}. {task.get('description', '')} ({task.get('marks', 0)} marks)"

                # Examiner instructions
                expected_answers = osce_data.get('expected_answers', {})
                examiner_instructions = f"""Expected Answers:
{json.dumps(expected_answers, indent=2)}
"""

                # Build rubric
                rubric = {}
                total_marks = osce_data.get('total_marks', 0)
                for task in tasks:
                    task_key = f"task_{task.get('task_number', 1)}"
                    rubric[task_key] = {
                        'max_marks': task.get('marks', 0),
                        'criteria': task.get('description', '')
                    }

                # Extract citation and store in australian_guidelines
                references = osce_data.get('references', [])
                citation = extract_citation(references)

                # Store references in australian_guidelines JSON field
                australian_guidelines = None
                if references:
                    australian_guidelines = {
                        'references': references,
                        'primary_citation': citation
                    }

                # Supporting documents
                images = scenario.get('images', [])
                supporting_documents = {'images': images} if images else None

                # Prepare OSCE object
                osce = OSCE(
                    osce_id=osce_id,
                    station_title=station_title,
                    station_type=station_type,
                    patient_instructions=patient_instructions,
                    candidate_instructions=candidate_instructions,
                    examiner_instructions=examiner_instructions,
                    rubric=rubric,
                    specialty=normalize_specialty(osce_data.get('specialty', 'general_practice')),
                    difficulty=normalize_difficulty(osce_data.get('difficulty', 'medium')),
                    time_limit_minutes=osce_data.get('duration_minutes', 8),  # Use duration_minutes from JSON or default to 8
                    learning_objectives=osce_data.get('learning_objectives', []),
                    tags=[osce_data.get('topic')] if osce_data.get('topic') else None,
                    supporting_documents=supporting_documents,
                    australian_guidelines=australian_guidelines,
                )

                if not dry_run:
                    if existing:
                        # Update
                        for key, value in osce.__dict__.items():
                            if key not in ['_sa_instance_state', 'id', 'created_at', 'times_attempted', 'average_score']:
                                setattr(existing, key, value)
                        stats['updated'] += 1
                    else:
                        # Insert
                        db.add(osce)
                        stats['loaded'] += 1

        except Exception as e:
            stats['errors'].append({
                'file': json_file.name,
                'error': str(e)
            })
            print(f"  ✗ Error: {e}")

    if not dry_run:
        try:
            db.commit()
        except IntegrityError as e:
            db.rollback()
            print(f"  ✗ Integrity error during commit: {e}")

    return stats


def load_study_cards(db: Session, dry_run=False, force=False) -> Dict:
    """Load all Study Card JSON files into database"""
    stats = {
        'total_files': 0,
        'total_cards': 0,
        'loaded': 0,
        'updated': 0,
        'skipped': 0,
        'failed': 0,
        'errors': []
    }

    json_files = sorted(STUDY_CARD_DIR.glob("*.json"))
    stats['total_files'] = len(json_files)

    print(f"\n{'='*70}")
    print(f"Study Card Database Seeding")
    print(f"{'='*70}")
    print(f"Found {len(json_files)} JSON files")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print(f"Force update: {force}")
    print()

    for json_file in json_files:
        print(f"\nProcessing: {json_file.name}")

        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Handle different JSON structures
            if isinstance(data, dict):
                if 'cards' in data:
                    cards_data = data['cards']
                else:
                    # Single card wrapped in dict
                    cards_data = [data] if 'id' in data else []
            elif isinstance(data, list):
                cards_data = data
            else:
                raise ValueError(f"Unknown JSON structure in {json_file}")

            stats['total_cards'] += len(cards_data)

            for card_data in tqdm(cards_data, desc=f"  {json_file.stem}"):
                # Extract card ID
                card_id = card_data.get('id', card_data.get('card_id'))
                if not card_id:
                    stats['failed'] += 1
                    stats['errors'].append({
                        'file': json_file.name,
                        'error': 'Missing card ID'
                    })
                    continue

                # Check if exists
                existing = db.query(StudyCard).filter(StudyCard.card_id == card_id).first()

                if existing and not force:
                    stats['skipped'] += 1
                    continue

                # Extract front and back content
                front = card_data.get('front', {})
                back = card_data.get('back', {})

                # Build question (front of card)
                question = front.get('question', '') if isinstance(front, dict) else str(front)

                # Build answer (back of card)
                if isinstance(back, dict):
                    answer_parts = []
                    if back.get('answer'):
                        answer_parts.append(back['answer'])
                    if back.get('key_facts'):
                        key_facts = back['key_facts']
                        if isinstance(key_facts, list):
                            answer_parts.append("\n\nKey Facts:\n" + "\n".join(f"- {fact}" for fact in key_facts))
                    answer = "\n".join(answer_parts)
                else:
                    answer = str(back)

                # Extract explanation/clinical pearl
                explanation = None
                if isinstance(back, dict):
                    if back.get('clinical_pearl'):
                        explanation = back['clinical_pearl']
                    elif back.get('explanation'):
                        explanation = back['explanation']

                # Map difficulty
                difficulty_str = card_data.get('difficulty', 'medium')
                difficulty_map = {
                    'basic': 'easy',
                    'beginner': 'easy',
                    'easy': 'easy',
                    'intermediate': 'medium',
                    'medium': 'medium',
                    'advanced': 'hard',
                    'hard': 'hard',
                }
                difficulty = normalize_difficulty(difficulty_map.get(difficulty_str.lower(), 'medium'))

                # Extract citations (ensure it's a list of dicts)
                references = card_data.get('references', [])
                if not references:
                    # Create default citation if missing
                    references = [{
                        'title': 'Australian Medical Guidelines',
                        'author': 'Unknown Author',
                        'year': '2020'
                    }]

                # Prepare StudyCard object
                study_card = StudyCard(
                    card_id=card_id,
                    specialty=normalize_specialty(card_data.get('specialty', 'general_practice')),
                    topic=card_data.get('topic', 'General'),
                    subtopic=card_data.get('subtopic'),
                    question=question,
                    answer=answer,
                    explanation=explanation,
                    citations=references,
                    difficulty=difficulty,
                    tags=card_data.get('tags', []),
                    card_type=card_data.get('card_type', 'concept'),
                    user_id=None,  # Shared/public cards (not user-specific)
                )

                if not dry_run:
                    if existing:
                        # Update
                        for key, value in study_card.__dict__.items():
                            if key not in ['_sa_instance_state', 'id', 'created_at', 'next_review_date', 'interval_days', 'ease_factor', 'repetitions']:
                                setattr(existing, key, value)
                        stats['updated'] += 1
                    else:
                        # Insert
                        db.add(study_card)
                        stats['loaded'] += 1

        except Exception as e:
            stats['errors'].append({
                'file': json_file.name,
                'error': str(e)
            })
            print(f"  ✗ Error: {e}")

    if not dry_run:
        try:
            db.commit()
        except IntegrityError as e:
            db.rollback()
            print(f"  ✗ Integrity error during commit: {e}")

    return stats


def print_stats(mcq_stats: Dict, osce_stats: Dict, study_card_stats: Dict = None):
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

        if osce_stats['errors']:
            print(f"\n  Errors ({len(osce_stats['errors'])}):")
            for err in osce_stats['errors'][:5]:
                print(f"    - {err}")

    if study_card_stats:
        print(f"\nStudy Cards:")
        print(f"  Total JSON files: {study_card_stats['total_files']}")
        print(f"  Total cards found: {study_card_stats['total_cards']}")
        print(f"  Loaded (new): {study_card_stats['loaded']}")
        print(f"  Updated: {study_card_stats['updated']}")
        print(f"  Skipped: {study_card_stats['skipped']}")
        print(f"  Failed: {study_card_stats['failed']}")

        if study_card_stats['errors']:
            print(f"\n  Errors ({len(study_card_stats['errors'])}):")
            for err in study_card_stats['errors'][:5]:
                print(f"    - {err}")


def main():
    parser = argparse.ArgumentParser(
        description='Seed PostgreSQL database with MCQs, OSCEs, and Study Cards from JSON files',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--mcqs', action='store_true', help='Load MCQs')
    parser.add_argument('--osces', action='store_true', help='Load OSCEs')
    parser.add_argument('--study-cards', action='store_true', help='Load Study Cards')
    parser.add_argument('--all', action='store_true', help='Load MCQs, OSCEs, and Study Cards')
    parser.add_argument('--force', action='store_true', help='Update existing records')
    parser.add_argument('--dry-run', action='store_true', help='Validate without inserting')
    parser.add_argument('--db-url', default=None, help='Database URL (or use DATABASE_URL env)')

    args = parser.parse_args()

    # Determine what to load
    load_mcqs_flag = args.mcqs or args.all
    load_osces_flag = args.osces or args.all
    load_study_cards_flag = args.study_cards or args.all

    if not (load_mcqs_flag or load_osces_flag or load_study_cards_flag):
        parser.error("Must specify --mcqs, --osces, --study-cards, or --all")

    # Database connection
    import os
    db_url = args.db_url or os.getenv('DATABASE_URL')
    if not db_url:
        parser.error("DATABASE_URL not set")

    engine = create_engine(db_url)

    # Run seeding
    with Session(engine) as db:
        mcq_stats = None
        osce_stats = None
        study_card_stats = None

        if load_mcqs_flag:
            mcq_stats = load_mcqs(db, dry_run=args.dry_run, force=args.force)

        if load_osces_flag:
            osce_stats = load_osces(db, dry_run=args.dry_run, force=args.force)

        if load_study_cards_flag:
            study_card_stats = load_study_cards(db, dry_run=args.dry_run, force=args.force)

        print_stats(mcq_stats, osce_stats, study_card_stats)

    print(f"\n{'✓' if args.dry_run else '✓✓'} Done!")


if __name__ == "__main__":
    main()
