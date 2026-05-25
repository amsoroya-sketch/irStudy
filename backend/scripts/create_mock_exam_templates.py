#!/usr/bin/env python3
"""
Create Mock Exam Templates for MVP

PRD: PRD-MVP-003-CONTENT-POPULATION-MVP.md
Purpose: Create 3 mock exam templates (16-station format)

Templates:
1. General Practice (balanced specialties)
2. Specialty-Focused (cardiology/respiratory)
3. Communication-Heavy (psychiatry/ethics)

Usage:
    python3 scripts/create_mock_exam_templates.py
    python3 scripts/create_mock_exam_templates.py --validate  # Dry run mode
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


def get_osces_for_template(db, specialty_filter=None, station_type_filter=None, limit=16):
    """
    Get OSCEs from database for a template

    Args:
        db: Database session
        specialty_filter: List of MedicalSpecialty enums (or None for all)
        station_type_filter: List of OSCEType enums (or None for all)
        limit: Number of OSCEs to select

    Returns:
        List of OSCE IDs
    """
    query = db.query(OSCE).filter(OSCE.is_published == True)

    if specialty_filter:
        query = query.filter(OSCE.specialty.in_(specialty_filter))

    if station_type_filter:
        query = query.filter(OSCE.station_type.in_(station_type_filter))

    osces = query.limit(limit).all()
    return [osce.osce_id for osce in osces]


def create_templates(dry_run: bool = False, validate: bool = False):
    """Create 3 mock exam templates"""

    print("=" * 60)
    print("Mock Exam Template Creation Script")
    print("=" * 60)
    print(f"Mode: {'DRY RUN' if dry_run else 'CREATE'}")
    print(f"Validation: {'YES' if validate else 'NO'}")
    print("")

    # Connect to database
    try:
        DATABASE_URL = get_database_url()
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return 1

    # Check if OSCEs are available
    total_osces = db.query(OSCE).count()
    print(f"Total OSCEs in database: {total_osces}")

    if total_osces < 50:
        print(f"⚠️  Insufficient OSCEs ({total_osces} < 50)")
        print("   Run scripts/import_osces.py first")
        db.close()
        return 1

    print("")

    # Template definitions
    templates = [
        {
            "template_id": str(uuid4()),
            "name": "General Practice Mock Exam",
            "description": "Balanced 16-station exam covering cardiology, respiratory, and psychiatry",
            "station_count": 16,
            "time_per_station": 8,  # minutes
            "specialty_filter": [
                MedicalSpecialty.CARDIOLOGY,
                MedicalSpecialty.RESPIRATORY,
                MedicalSpecialty.PSYCHIATRY,
                MedicalSpecialty.GENERAL_PRACTICE
            ],
            "station_type_filter": None,  # All types
        },
        {
            "template_id": str(uuid4()),
            "name": "Specialty-Focused Mock Exam",
            "description": "16-station exam focused on cardiology and respiratory medicine",
            "station_count": 16,
            "time_per_station": 8,
            "specialty_filter": [
                MedicalSpecialty.CARDIOLOGY,
                MedicalSpecialty.RESPIRATORY
            ],
            "station_type_filter": None,
        },
        {
            "template_id": str(uuid4()),
            "name": "Communication Skills Mock Exam",
            "description": "16-station exam emphasizing history-taking and communication (psychiatry/ethics focus)",
            "station_count": 16,
            "time_per_station": 8,
            "specialty_filter": [
                MedicalSpecialty.PSYCHIATRY,
                MedicalSpecialty.GENERAL_PRACTICE
            ],
            "station_type_filter": [
                OSCEType.HISTORY_TAKING,
                OSCEType.COMMUNICATION_SKILLS
            ],
        }
    ]

    created_count = 0

    for template_def in templates:
        try:
            print(f"Creating: {template_def['name']}")
            print(f"  - Stations: {template_def['station_count']}")
            print(f"  - Time per station: {template_def['time_per_station']} min")

            # Get OSCEs for this template
            osce_ids = get_osces_for_template(
                db,
                specialty_filter=template_def['specialty_filter'],
                station_type_filter=template_def['station_type_filter'],
                limit=template_def['station_count']
            )

            if len(osce_ids) < template_def['station_count']:
                print(f"  ⚠️  Only {len(osce_ids)} OSCEs available (need {template_def['station_count']})")

            print(f"  - Selected {len(osce_ids)} OSCEs")

            # Create template data structure
            template_data = {
                "template_id": template_def['template_id'],
                "name": template_def['name'],
                "description": template_def['description'],
                "station_count": len(osce_ids),
                "time_per_station_minutes": template_def['time_per_station'],
                "total_time_minutes": len(osce_ids) * template_def['time_per_station'],
                "osce_ids": osce_ids,
                "created_at": datetime.utcnow().isoformat()
            }

            if not dry_run:
                # NOTE: Since MockExamTemplate model may not exist, store as JSON file
                # This can be imported later when the model is created
                templates_dir = backend_dir / "data" / "mock_exam_templates"
                templates_dir.mkdir(parents=True, exist_ok=True)

                template_file = templates_dir / f"{template_def['template_id']}.json"
                with open(template_file, 'w', encoding='utf-8') as f:
                    json.dump(template_data, f, indent=2, default=str)

                print(f"  ✓ Template saved: {template_file.name}")
                created_count += 1
            else:
                print(f"  [DRY RUN] Would create template: {template_def['name']}")

            print("")

        except Exception as e:
            print(f"  ❌ Error creating template: {e}")
            continue

    db.close()

    print("=" * 60)
    if not dry_run:
        print(f"✅ Created {created_count} mock exam templates")
        print(f"\nTemplates saved to: backend/data/mock_exam_templates/")
        print("\nNOTE: Templates are stored as JSON files.")
        print("When MockExamTemplate model is created, run:")
        print("  python3 scripts/import_mock_exam_templates.py")
    else:
        print("Dry run complete - no templates created")

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create mock exam templates")
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Plan templates but do not create files'
    )
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate OSCE availability without creating'
    )

    args = parser.parse_args()

    exit_code = create_templates(
        dry_run=args.dry_run,
        validate=args.validate
    )

    sys.exit(exit_code)
