#!/usr/bin/env python3
"""
Import patient personas from Batch 1 into database

Imports 207 patient personas from clinical-content-prds/validation-system/batch1_personas/
into the mock_patients table for use in EMR practice sessions and OSCE integration tests.

Usage:
    python scripts/import_patient_personas.py [--env test|dev|prod]
"""

import sys
import json
from pathlib import Path
from uuid import uuid4
from datetime import datetime
import argparse

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.db.models import MockPatient
from src.db.base import Base


def load_persona_files(personas_dir: Path) -> list[dict]:
    """Load all persona JSON files from directory"""
    personas = []

    for json_file in sorted(personas_dir.glob("*.json")):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                persona = json.load(f)
                personas.append(persona)
        except json.JSONDecodeError as e:
            print(f"⚠️  Skipping invalid JSON: {json_file.name} - {e}")
        except Exception as e:
            print(f"⚠️  Error reading {json_file.name}: {e}")

    return personas


def map_persona_to_mock_patient(persona: dict) -> MockPatient:
    """Map persona JSON to MockPatient database model"""

    # Generate unique MRN from persona ID
    mrn = f"MOCK-{persona['id']}"

    # Map gender (handle case variations)
    gender_map = {
        'male': 'Male',
        'female': 'Female',
        'other': 'Other',
        'unknown': 'Unknown'
    }
    gender = gender_map.get(persona.get('gender', '').lower(), persona.get('gender', 'Unknown'))

    # Map difficulty (handle case variations)
    difficulty_map = {
        'easy': 'Easy',
        'medium': 'Medium',
        'hard': 'Hard',
        'intermediate': 'Medium'  # Map intermediate to Medium
    }
    difficulty = difficulty_map.get(persona.get('difficulty', '').lower(), persona.get('difficulty', 'Medium'))

    # Extract medical history from persona data
    medical_history = {
        'diagnosis': persona.get('diagnosis', 'Unknown'),
        'symptoms': [
            {
                'symptom': s.get('symptom', 'Unspecified'),
                'onset': s.get('onset', 'Unknown'),
                'duration': s.get('duration', 'Unknown'),
                'severity': s.get('severity', 'Unknown')
            }
            for s in persona.get('symptoms', [])[:3]  # Limit to first 3 symptoms
        ],
        'differential_diagnoses': persona.get('differential_diagnoses', []),
        'opening_statement': persona.get('opening_statement', ''),
        'emotional_baseline': persona.get('emotional_baseline', '')
    }

    # Extract vital signs if available (most personas don't have explicit vital signs)
    vital_signs = persona.get('vital_signs', None)

    # Create MockPatient instance
    mock_patient = MockPatient(
        id=uuid4(),  # Generate new UUID
        mrn=mrn,
        name=persona.get('name', 'Unknown Patient'),
        age=persona.get('age', 0),
        gender=gender,
        presenting_complaint=persona.get('chief_complaint', 'Unknown complaint'),
        vital_signs=vital_signs,
        medical_history=medical_history,
        specialty=persona.get('specialty', 'General').lower(),
        difficulty=difficulty.lower(),
        created_at=datetime.utcnow()
    )

    return mock_patient


def import_personas(database_url: str, personas_dir: Path, batch_size: int = 50) -> tuple[int, int]:
    """
    Import patient personas into database

    Returns:
        (successful_imports, failed_imports)
    """
    # Create database engine and session
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    # Load persona files
    print(f"📂 Loading personas from {personas_dir}")
    personas = load_persona_files(personas_dir)
    print(f"✅ Loaded {len(personas)} persona files")

    # Import personas in batches
    successful = 0
    failed = 0

    try:
        for i, persona in enumerate(personas, 1):
            try:
                mock_patient = map_persona_to_mock_patient(persona)
                session.add(mock_patient)
                successful += 1

                # Commit in batches
                if i % batch_size == 0:
                    session.commit()
                    print(f"✅ Imported {i}/{len(personas)} personas...")

            except Exception as e:
                print(f"⚠️  Failed to import persona {persona.get('id', 'unknown')}: {e}")
                failed += 1
                session.rollback()

        # Commit remaining personas
        session.commit()
        print(f"✅ Final commit complete")

    except Exception as e:
        print(f"❌ Database error: {e}")
        session.rollback()
        raise
    finally:
        session.close()

    return successful, failed


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Import patient personas into database")
    parser.add_argument(
        '--env',
        choices=['test', 'dev', 'prod'],
        default='test',
        help='Target environment (default: test)'
    )
    parser.add_argument(
        '--personas-dir',
        type=Path,
        default=None,
        help='Path to personas directory (default: clinical-content-prds/validation-system/batch1_personas/)'
    )
    parser.add_argument(
        '--database-url',
        type=str,
        default=None,
        help='Database URL (overrides --env)'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=50,
        help='Commit batch size (default: 50)'
    )

    args = parser.parse_args()

    # Determine personas directory
    if args.personas_dir:
        personas_dir = args.personas_dir
    else:
        # Default: clinical-content-prds/validation-system/batch1_personas/
        project_root = backend_dir.parent
        personas_dir = project_root / "clinical-content-prds" / "validation-system" / "batch1_personas"

    if not personas_dir.exists():
        print(f"❌ Personas directory not found: {personas_dir}")
        sys.exit(1)

    # Determine database URL
    if args.database_url:
        database_url = args.database_url
    elif args.env == 'test':
        # Test environment (in-memory SQLite for fast testing)
        database_url = "sqlite:///:memory:"
        print("⚠️  Using in-memory SQLite - data will be lost after script exits")
        print("⚠️  For pytest tests, use conftest.py fixtures instead")
    elif args.env == 'dev':
        # Dev environment (local PostgreSQL)
        database_url = "postgresql://postgres:3K4cnsyxYOOHGzCcxmOesU7PExXHCMaH@localhost:5433/irstudy_medical"
    elif args.env == 'prod':
        print("❌ Production import not implemented (requires encrypted credentials)")
        sys.exit(1)
    else:
        print(f"❌ Invalid environment: {args.env}")
        sys.exit(1)

    # Display configuration
    print("=" * 60)
    print("Patient Persona Import")
    print("=" * 60)
    print(f"Environment: {args.env}")
    print(f"Database URL: {database_url[:50]}...")
    print(f"Personas directory: {personas_dir}")
    print(f"Batch size: {args.batch_size}")
    print("=" * 60)
    print()

    # Import personas
    try:
        successful, failed = import_personas(database_url, personas_dir, args.batch_size)

        print()
        print("=" * 60)
        print("Import Summary")
        print("=" * 60)
        print(f"✅ Successfully imported: {successful}")
        print(f"⚠️  Failed imports: {failed}")
        print(f"📊 Total personas: {successful + failed}")
        print("=" * 60)

        if failed > 0:
            sys.exit(1)

    except Exception as e:
        print()
        print("=" * 60)
        print("❌ Import Failed")
        print("=" * 60)
        print(f"Error: {e}")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
