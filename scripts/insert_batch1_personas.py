#!/usr/bin/env python3
import json
import sys
import argparse
import os
from pathlib import Path
import psycopg2
from psycopg2.extras import Json
from typing import Dict

# Configuration - SECURITY: Use environment variables
DATABASE_CONFIG = {
    "host": os.getenv("DATABASE_HOST", "localhost"),
    "port": int(os.getenv("DATABASE_PORT", "5433")),
    "database": os.getenv("DATABASE_NAME", "irstudy_medical"),
    "user": os.getenv("DATABASE_USER", "postgres"),
    "password": os.getenv("DATABASE_PASSWORD", "")
}

PERSONA_DIR = Path("clinical-content-prds/validation-system/batch1_personas")

def connect_db():
    # SECURITY: Validate that credentials are set
    if not DATABASE_CONFIG["password"]:
        print("ERROR: DATABASE_PASSWORD environment variable is not set!")
        print("Please set it using one of these methods:")
        print("  export DATABASE_PASSWORD='your-password'")
        print("  or source backend/.env")
        sys.exit(1)

    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        return conn
    except Exception as e:
        print(f"Database connection failed: {e}")
        sys.exit(1)

def insert_persona(conn, persona_data: Dict) -> bool:
    insert_sql = """
    INSERT INTO patient_personas (
        persona_code, name, age, gender, specialty, chief_complaint,
        opening_statement, symptoms, medical_history, emotional_profile,
        difficulty_level, is_active
    ) VALUES (
        %(persona_code)s, %(name)s, %(age)s, %(gender)s, %(specialty)s,
        %(chief_complaint)s, %(opening_statement)s, %(symptoms)s,
        %(medical_history)s, %(emotional_profile)s, %(difficulty)s, TRUE
    )
    ON CONFLICT (persona_code) DO UPDATE SET
        name = EXCLUDED.name,
        age = EXCLUDED.age,
        gender = EXCLUDED.gender,
        specialty = EXCLUDED.specialty,
        chief_complaint = EXCLUDED.chief_complaint,
        opening_statement = EXCLUDED.opening_statement,
        symptoms = EXCLUDED.symptoms,
        medical_history = EXCLUDED.medical_history,
        emotional_profile = EXCLUDED.emotional_profile,
        difficulty_level = EXCLUDED.difficulty_level
    """

    try:
        difficulty_map = {"Easy": "foundation", "Medium": "intermediate", "Hard": "advanced"}
        difficulty_level = difficulty_map.get(persona_data.get("difficulty", "Medium"), "intermediate")

        with conn.cursor() as cursor:
            cursor.execute(insert_sql, {
                "persona_code": persona_data["id"],
                "name": persona_data["name"],
                "age": persona_data["age"],
                "gender": persona_data["gender"],
                "specialty": persona_data["specialty"],
                "chief_complaint": persona_data.get("chief_complaint", ""),
                "opening_statement": persona_data.get("opening_statement", ""),
                "symptoms": Json(persona_data.get("symptoms", [])),
                "medical_history": Json(persona_data.get("medical_history", [])),
                "emotional_profile": Json({
                    "baseline": persona_data.get("emotional_baseline", ""),
                    "personality_traits": persona_data.get("personality_traits", []),
                    "response_patterns": persona_data.get("response_patterns", {})
                }),
                "difficulty": difficulty_level
            })
            conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"  Error: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Insert Batch 1 personas into database")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    print("=== Batch 1 Persona Database Insertion ===\n")
    conn = connect_db()
    print("Using existing table schema")

    if args.force:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM patient_personas WHERE persona_code LIKE 'cardiology_%' OR persona_code LIKE 'emergency_%' OR persona_code LIKE 'general_practice_%' OR persona_code LIKE 'pediatrics_%' OR persona_code LIKE 'respiratory_%'")
            deleted = cursor.rowcount
            conn.commit()
        print(f"Deleted {deleted} existing personas\n")

    # Exclude QA report files (only load persona JSON files)
    persona_files = sorted([f for f in PERSONA_DIR.glob("*.json") if not f.name.endswith("_qa_report.json")])
    total = len(persona_files)

    if args.dry_run:
        print(f"DRY RUN: Would insert {total} personas")
        for pfile in persona_files[:5]:
            with open(pfile) as f:
                data = json.load(f)
            print(f"  - {data['id']}:  {data['name']} ({data['specialty']}/{data['diagnosis']})")
        if total > 5:
            print(f"  ... and {total - 5} more")
        conn.close()
        return

    print(f"Inserting {total} personas...\n")

    inserted = 0
    updated = 0
    failed = 0

    for i, pfile in enumerate(persona_files, 1):
        try:
            with open(pfile) as f:
                persona_data = json.load(f)

            with conn.cursor() as cursor:
                cursor.execute("SELECT persona_id FROM patient_personas WHERE persona_code = %s", (persona_data['id'],))
                exists = cursor.fetchone() is not None

            if insert_persona(conn, persona_data):
                if exists:
                    updated += 1
                    print(f"[{i}/{total}] Updated: {persona_data['id']}")
                else:
                    inserted += 1
                    print(f"[{i}/{total}] Inserted: {persona_data['id']}")
            else:
                failed += 1
                print(f"[{i}/{total}] Failed: {pfile.name}")

        except Exception as e:
            failed += 1
            print(f"[{i}/{total}] Error loading {pfile.name}: {e}")

    print(f"\n=== Summary ===")
    print(f"Total files: {total}")
    print(f"Inserted: {inserted}")
    print(f"Updated: {updated}")
    print(f"Failed: {failed}")
    if total > 0:
        print(f"Success rate: {(inserted + updated) / total * 100:.1f}%")

    with conn.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM patient_personas")
        db_count = cursor.fetchone()[0]
    print(f"\nDatabase count: {db_count} personas")

    conn.close()

if __name__ == "__main__":
    main()
