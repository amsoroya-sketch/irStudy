#!/usr/bin/env python3
"""
Import patient personas from Batch 1 into database for AI OSCE system

PRD: PRD-MVP-003-CONTENT-POPULATION-MVP.md
Purpose: Import 207 patient personas into patient_personas table for AI OSCE simulation

Imports from: clinical-content-prds/validation-system/batch1_personas/

Usage:
    python3 scripts/import_patient_personas.py --source /home/dev/Development/irStudy/clinical-content-prds/validation-system/batch1_personas/
    python3 scripts/import_patient_personas.py --validate  # Dry run mode
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
from src.db.models import PatientPersona
from src.db.base import Base, get_database_url


def load_persona_files(personas_dir: Path) -> list[dict]:
    """Load all persona JSON files from directory"""
    personas = []

    for json_file in sorted(personas_dir.glob("*_persona.json")):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                persona = json.load(f)
                personas.append(persona)
        except json.JSONDecodeError as e:
            print(f"⚠️  Skipping invalid JSON: {json_file.name} - {e}")
        except Exception as e:
            print(f"⚠️  Error reading {json_file.name}: {e}")

    return personas


def map_specialty(specialty_str: str) -> str:
    """Normalize specialty string"""
    specialty_map = {
        'general practice': 'general_practice',
        'emergency': 'emergency_medicine',
        'emergency medicine': 'emergency_medicine',
        'cardiology': 'cardiology',
        'respiratory': 'respiratory',
        'psychiatry': 'psychiatry',
        'pediatrics': 'pediatrics',
        'obstetrics': 'obstetrics_gynaecology',
        'gynaecology': 'obstetrics_gynaecology',
        'neurology': 'neurology',
        'gastroenterology': 'gastroenterology'
    }

    specialty_lower = specialty_str.lower().strip()
    return specialty_map.get(specialty_lower, specialty_str.lower())


def map_difficulty(difficulty_str: str) -> str:
    """Normalize difficulty level"""
    difficulty_map = {
        'easy': 'foundation',
        'medium': 'intermediate',
        'hard': 'advanced',
        'foundation': 'foundation',
        'intermediate': 'intermediate',
        'advanced': 'advanced'
    }

    difficulty_lower = difficulty_str.lower().strip()
    return difficulty_map.get(difficulty_lower, 'intermediate')


def import_personas(source_dir: str, dry_run: bool = False, validate: bool = False, limit: int = None):
    """Import patient personas from JSON files into database"""

    print("=" * 60)
    print("Patient Persona Import Script (AI OSCE)")
    print("=" * 60)
    print(f"Source: {source_dir}")
    print(f"Mode: {'DRY RUN' if dry_run else 'IMPORT'}")
    print(f"Validation: {'YES' if validate else 'NO'}")
    if limit:
        print(f"Limit: {limit} personas")
    print("")

    source_path = Path(source_dir)
    if not source_path.exists():
        print(f"❌ Source directory not found: {source_dir}")
        return 1

    # Load persona files
    print("Loading persona files...")
    personas_data = load_persona_files(source_path)

    if limit:
        personas_data = personas_data[:limit]

    print(f"\n✓ Total personas loaded: {len(personas_data)}\n")

    if dry_run or len(personas_data) == 0:
        print(f"{'Dry run complete' if dry_run else 'No personas to import'}")
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

    # Import personas
    print("Importing personas to database...")
    print("-" * 60)

    imported_count = 0
    skipped_count = 0
    error_count = 0

    for idx, persona_data in enumerate(personas_data, 1):
        try:
            # Extract persona ID (use existing or generate)
            persona_id = persona_data.get('id') or str(uuid4())
            persona_code = persona_data.get('persona_code') or persona_id

            # Check if persona already exists
            existing = db.query(PatientPersona).filter(PatientPersona.persona_code == persona_code).first()
            if existing:
                skipped_count += 1
                continue

            # Map specialty and difficulty
            specialty = map_specialty(persona_data.get('specialty', 'general_practice'))
            difficulty_level = map_difficulty(persona_data.get('difficulty', 'medium'))

            # Extract demographics
            name = persona_data.get('name', f'Patient {idx}')
            age = persona_data.get('age', 0)
            gender = persona_data.get('gender', 'Unknown')
            occupation = persona_data.get('occupation')
            cultural_background = persona_data.get('cultural_background')
            preferred_language = persona_data.get('preferred_language', 'English')

            # Extract clinical presentation
            chief_complaint = persona_data.get('chief_complaint', '')
            opening_statement = persona_data.get('opening_statement', '')

            # Extract progressive disclosure data
            symptoms = persona_data.get('symptoms', [])
            medical_history = persona_data.get('medical_history', {})
            emotional_profile = persona_data.get('emotional_profile', {})
            if not emotional_profile:
                emotional_profile = {
                    'baseline': persona_data.get('emotional_baseline', 'Calm, cooperative'),
                    'triggers': [],
                    'responses': {}
                }

            # Extract RAG integration data
            rag_query_hints = persona_data.get('rag_query_hints', [])
            key_differentials = persona_data.get('differential_diagnoses', [])
            critical_actions = persona_data.get('critical_actions', [])

            # Extract metadata
            amc_blueprint_area = persona_data.get('amc_blueprint_area')
            amc_competencies = persona_data.get('amc_competencies', [])
            estimated_pass_rate = persona_data.get('estimated_pass_rate')

            # Create PatientPersona model
            # NOTE: Database uses 'persona_id' as primary key (String), 'persona_code' as unique identifier
            persona = PatientPersona(
                persona_id=str(uuid4()),  # Generate new UUID for primary key
                persona_code=persona_code,
                name=name,
                age=age,
                gender=gender,
                occupation=occupation,
                cultural_background=cultural_background,
                preferred_language=preferred_language,
                specialty=specialty,
                chief_complaint=chief_complaint,
                opening_statement=opening_statement,
                symptoms=symptoms,
                medical_history=medical_history,
                emotional_profile=emotional_profile,
                rag_query_hints=rag_query_hints,
                key_differentials=key_differentials,
                critical_actions=critical_actions,
                difficulty_level=difficulty_level,
                estimated_pass_rate=estimated_pass_rate,
                amc_blueprint_area=amc_blueprint_area,
                amc_competencies=amc_competencies,
                is_active=True,
                version=1
            )

            db.add(persona)
            imported_count += 1

            if imported_count % 20 == 0:
                print(f"  Imported {imported_count} personas...")
                db.commit()  # Commit in batches

        except IntegrityError as e:
            db.rollback()
            skipped_count += 1
            print(f"  ⚠️  Skipped duplicate persona: {persona_code}")
        except Exception as e:
            print(f"  ❌ Error importing persona {idx}: {e}")
            error_count += 1
            db.rollback()

    # Final commit
    try:
        db.commit()
        print("")
        print("=" * 60)
        print("Import Summary")
        print("=" * 60)
        print(f"✓ Imported: {imported_count} personas")
        print(f"⚠ Skipped (duplicates): {skipped_count} personas")
        print(f"✗ Errors: {error_count} personas")
        print("")

    except Exception as e:
        print(f"❌ Final commit failed: {e}")
        db.rollback()
        return 1
    finally:
        db.close()

    return 0 if error_count == 0 else 1


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Import patient personas for AI OSCE system")
    parser.add_argument(
        '--source',
        type=str,
        default='/home/dev/Development/irStudy/clinical-content-prds/validation-system/batch1_personas/',
        help='Source directory containing persona JSON files'
    )
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Dry run mode (validate without importing)'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='Limit number of personas to import (for testing)'
    )

    args = parser.parse_args()

    return import_personas(
        source_dir=args.source,
        dry_run=args.validate,
        validate=args.validate,
        limit=args.limit
    )


if __name__ == "__main__":
    sys.exit(main())
