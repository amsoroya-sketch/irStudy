# PRD-WEEK1-002: Database Insertion - Load 207 Personas

**Priority**: P0 (Critical)
**Estimated Time**: 2 hours
**Status**: Ready for Implementation
**Dependencies**: None (can run in parallel with PRD-WEEK1-001)
**Blocks**: Frontend integration, API access, production deployment

---

## Executive Summary

Load all 207 RAG-verified patient personas from JSON files into PostgreSQL database, making them accessible via REST API for frontend consumption. This is a **critical blocker** for production deployment.

---

## Problem Statement

### Current State
- ✅ 207 personas exist as JSON files in `batch1_personas/`
- ❌ No personas in PostgreSQL database
- ❌ Frontend cannot access personas via API
- ❌ No filtering by specialty/difficulty
- ❌ Users cannot select personas for OSCE practice

### Business Impact
- **User Impact**: Cannot use any of the 207 new personas
- **Revenue Impact**: Feature incomplete, cannot launch
- **Timeline Impact**: Blocks Week 1 deployment target

---

## Success Criteria

### Must Have
1. ✅ All 207 personas inserted into `patient_personas` table
2. ✅ Database schema supports full persona JSON storage
3. ✅ API endpoint returns personas with filters
4. ✅ Zero data loss (all fields preserved)
5. ✅ Insertion script is idempotent (can re-run safely)

### Nice to Have
1. Bulk insert performance (<30 seconds for 207 personas)
2. Transaction rollback on any error
3. Duplicate detection (prevent re-inserting existing personas)
4. Audit trail (created_at, updated_at timestamps)

---

## Technical Specification

### Database Schema

**Check if table exists**:
```bash
psql -U postgres -d irstudy_medical -c "\d patient_personas"
```

**If table doesn't exist, create it**:
```sql
CREATE TABLE IF NOT EXISTS patient_personas (
    id SERIAL PRIMARY KEY,
    persona_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    age INTEGER NOT NULL,
    gender VARCHAR(20) NOT NULL,
    specialty VARCHAR(100) NOT NULL,
    diagnosis TEXT NOT NULL,
    difficulty VARCHAR(20) NOT NULL CHECK (difficulty IN ('Easy', 'Medium', 'Hard')),
    persona_data JSONB NOT NULL,  -- Full persona JSON
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    -- Indexes for performance
    CONSTRAINT valid_age CHECK (age >= 0 AND age <= 120),
    CONSTRAINT valid_gender CHECK (gender IN ('Male', 'Female', 'Non-binary', 'Other'))
);

-- Indexes
CREATE INDEX idx_specialty ON patient_personas(specialty);
CREATE INDEX idx_difficulty ON patient_personas(difficulty);
CREATE INDEX idx_active ON patient_personas(is_active);
CREATE INDEX idx_persona_data_gin ON patient_personas USING GIN (persona_data);

-- Full-text search index
CREATE INDEX idx_diagnosis_fts ON patient_personas USING GIN (to_tsvector('english', diagnosis));
```

### Insertion Script

**File**: `scripts/insert_batch1_personas.py`

```python
#!/usr/bin/env python3
"""
Insert Batch 1 Personas into PostgreSQL Database
=================================================

Loads all 207 RAG-verified personas from JSON files into the database.

Usage:
    python3 scripts/insert_batch1_personas.py
    python3 scripts/insert_batch1_personas.py --dry-run
    python3 scripts/insert_batch1_personas.py --force  # Delete existing first
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime
import psycopg2
from psycopg2.extras import Json
from typing import Dict, List

# Configuration
DATABASE_CONFIG = {
    'host': 'localhost',
    'port': 5433,
    'database': 'irstudy_medical',
    'user': 'postgres',
    'password': '3K4cnsyxYOOHGzCcxmOesU7PExXHCMaH'  # From .env
}

PERSONA_DIR = Path('clinical-content-prds/validation-system/batch1_personas')


def connect_db():
    """Connect to PostgreSQL database"""
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        return conn
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        sys.exit(1)


def create_table_if_not_exists(conn):
    """Create patient_personas table if it doesn't exist"""
    create_sql = """
    CREATE TABLE IF NOT EXISTS patient_personas (
        id SERIAL PRIMARY KEY,
        persona_id VARCHAR(100) UNIQUE NOT NULL,
        name VARCHAR(200) NOT NULL,
        age INTEGER NOT NULL,
        gender VARCHAR(20) NOT NULL,
        specialty VARCHAR(100) NOT NULL,
        diagnosis TEXT NOT NULL,
        difficulty VARCHAR(20) NOT NULL,
        persona_data JSONB NOT NULL,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
    );

    CREATE INDEX IF NOT EXISTS idx_specialty ON patient_personas(specialty);
    CREATE INDEX IF NOT EXISTS idx_difficulty ON patient_personas(difficulty);
    CREATE INDEX IF NOT EXISTS idx_active ON patient_personas(is_active);
    CREATE INDEX IF NOT EXISTS idx_persona_data_gin ON patient_personas USING GIN (persona_data);
    """

    with conn.cursor() as cursor:
        cursor.execute(create_sql)
        conn.commit()

    print("✅ Table created/verified")


def insert_persona(conn, persona_data: Dict) -> bool:
    """Insert single persona into database"""
    insert_sql = """
    INSERT INTO patient_personas (
        persona_id, name, age, gender, specialty, diagnosis, difficulty, persona_data
    ) VALUES (
        %(persona_id)s, %(name)s, %(age)s, %(gender)s, %(specialty)s, %(diagnosis)s, %(difficulty)s, %(persona_data)s
    )
    ON CONFLICT (persona_id) DO UPDATE SET
        name = EXCLUDED.name,
        age = EXCLUDED.age,
        gender = EXCLUDED.gender,
        specialty = EXCLUDED.specialty,
        diagnosis = EXCLUDED.diagnosis,
        difficulty = EXCLUDED.difficulty,
        persona_data = EXCLUDED.persona_data,
        updated_at = NOW()
    """

    try:
        with conn.cursor() as cursor:
            cursor.execute(insert_sql, {
                'persona_id': persona_data['id'],
                'name': persona_data['name'],
                'age': persona_data['age'],
                'gender': persona_data['gender'],
                'specialty': persona_data['specialty'],
                'diagnosis': persona_data['diagnosis'],
                'difficulty': persona_data['difficulty'],
                'persona_data': Json(persona_data)
            })
            conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"  Error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Insert Batch 1 personas into database")
    parser.add_argument('--dry-run', action='store_true', help="Show what would be inserted without inserting")
    parser.add_argument('--force', action='store_true', help="Delete existing personas before inserting")
    args = parser.parse_args()

    # Connect to database
    print("=== Batch 1 Persona Database Insertion ===\n")
    conn = connect_db()

    # Create table
    create_table_if_not_exists(conn)

    # Delete existing if force flag
    if args.force:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM patient_personas WHERE persona_id LIKE 'cardiology_%' OR persona_id LIKE 'emergency_%' OR persona_id LIKE 'general_practice_%' OR persona_id LIKE 'pediatrics_%' OR persona_id LIKE 'respiratory_%'")
            deleted = cursor.rowcount
            conn.commit()
        print(f"🗑️  Deleted {deleted} existing personas\n")

    # Load persona files
    persona_files = sorted(PERSONA_DIR.glob('*.json'))
    total = len(persona_files)

    if args.dry_run:
        print(f"📋 DRY RUN: Would insert {total} personas")
        for pfile in persona_files[:5]:
            with open(pfile) as f:
                data = json.load(f)
            print(f"  - {data['id']}: {data['name']} ({data['specialty']}/{data['diagnosis']})")
        print(f"  ... and {total - 5} more")
        return

    # Insert personas
    print(f"📥 Inserting {total} personas...\n")

    inserted = 0
    updated = 0
    failed = 0

    for i, pfile in enumerate(persona_files, 1):
        try:
            with open(pfile) as f:
                persona_data = json.load(f)

            # Check if exists
            with conn.cursor() as cursor:
                cursor.execute("SELECT id FROM patient_personas WHERE persona_id = %s", (persona_data['id'],))
                exists = cursor.fetchone() is not None

            if insert_persona(conn, persona_data):
                if exists:
                    updated += 1
                    print(f"[{i}/{total}] ♻️  Updated: {persona_data['id']}")
                else:
                    inserted += 1
                    print(f"[{i}/{total}] ✅ Inserted: {persona_data['id']}")
            else:
                failed += 1
                print(f"[{i}/{total}] ❌ Failed: {pfile.name}")

        except Exception as e:
            failed += 1
            print(f"[{i}/{total}] ❌ Error loading {pfile.name}: {e}")

    # Summary
    print(f"\n=== Summary ===")
    print(f"Total files: {total}")
    print(f"Inserted: {inserted}")
    print(f"Updated: {updated}")
    print(f"Failed: {failed}")
    print(f"Success rate: {(inserted + updated) / total * 100:.1f}%")

    # Verify insertion
    with conn.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM patient_personas")
        db_count = cursor.fetchone()[0]
    print(f"\nDatabase count: {db_count} personas")

    conn.close()

if __name__ == "__main__":
    main()
```

---

## Implementation Steps

### Step 1: Check Database Connection
```bash
psql -U postgres -h localhost -p 5433 -d irstudy_medical -c "SELECT version();"
```

### Step 2: Create Insertion Script
```bash
# Script created above - save to scripts/insert_batch1_personas.py
chmod +x scripts/insert_batch1_personas.py
```

### Step 3: Dry Run Test
```bash
cd /home/dev/Development/irStudy
source backend/venv/bin/activate
python3 scripts/insert_batch1_personas.py --dry-run
```

### Step 4: Insert Personas
```bash
python3 scripts/insert_batch1_personas.py
```

### Step 5: Verify Insertion
```bash
psql -U postgres -h localhost -p 5433 -d irstudy_medical -c "
SELECT
    specialty,
    difficulty,
    COUNT(*) as count
FROM patient_personas
GROUP BY specialty, difficulty
ORDER BY specialty, difficulty;
"
```

**Expected Output**:
```
     specialty      | difficulty | count
--------------------+------------+-------
 Cardiology         | Easy       |    15
 Cardiology         | Medium     |    25
 Cardiology         | Hard       |     5
 Emergency          | Easy       |    15
 Emergency          | Medium     |    25
 Emergency          | Hard       |     5
 General Practice   | Easy       |    18
 General Practice   | Medium     |    30
 General Practice   | Hard       |     6
 Pediatrics         | Easy       |    12
 Pediatrics         | Medium     |    20
 Pediatrics         | Hard       |     4
 Respiratory        | Easy       |     9
 Respiratory        | Medium     |    15
 Respiratory        | Hard       |     3
(15 rows)
```

---

## API Endpoint Creation

**File**: `backend/src/api/v1/personas.py`

```python
from fastapi import APIRouter, Query
from typing import Optional, List
from pydantic import BaseModel

router = APIRouter(prefix="/personas", tags=["personas"])

class PersonaListItem(BaseModel):
    id: int
    persona_id: str
    name: str
    age: int
    gender: str
    specialty: str
    diagnosis: str
    difficulty: str

@router.get("/", response_model=List[PersonaListItem])
async def get_personas(
    specialty: Optional[str] = None,
    difficulty: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200)
):
    """Get list of patient personas with optional filters"""

    query = "SELECT id, persona_id, name, age, gender, specialty, diagnosis, difficulty FROM patient_personas WHERE is_active = TRUE"
    params = []

    if specialty:
        query += " AND specialty = %s"
        params.append(specialty)

    if difficulty:
        query += " AND difficulty = %s"
        params.append(difficulty)

    if search:
        query += " AND (name ILIKE %s OR diagnosis ILIKE %s)"
        params.extend([f"%{search}%", f"%{search}%"])

    query += " ORDER BY specialty, difficulty, name"
    query += " OFFSET %s LIMIT %s"
    params.extend([skip, limit])

    # Execute query and return results
    # (Implementation depends on your DB connection setup)

    return personas


@router.get("/{persona_id}", response_model=dict)
async def get_persona_detail(persona_id: str):
    """Get full persona data including all fields"""

    query = "SELECT persona_data FROM patient_personas WHERE persona_id = %s AND is_active = TRUE"

    # Execute query and return persona_data JSONB field

    return persona_data
```

---

## Testing & Validation

### Test 1: Database Count
```bash
psql -U postgres -h localhost -p 5433 -d irstudy_medical -c "SELECT COUNT(*) FROM patient_personas;"
# Expected: 207
```

### Test 2: Specialty Distribution
```bash
psql -U postgres -h localhost -p 5433 -d irstudy_medical -c "
SELECT specialty, COUNT(*) FROM patient_personas GROUP BY specialty ORDER BY COUNT(*) DESC;
"
```

### Test 3: Sample Persona Retrieval
```bash
psql -U postgres -h localhost -p 5433 -d irstudy_medical -c "
SELECT persona_id, name, specialty, diagnosis FROM patient_personas WHERE persona_id = 'cardiology_001_stemi_male_65';
"
```

### Test 4: JSON Data Integrity
```bash
psql -U postgres -h localhost -p 5433 -d irstudy_medical -c "
SELECT
    persona_id,
    jsonb_array_length(persona_data->'symptoms') as symptom_count,
    jsonb_array_length(persona_data->'management_plan') as management_count
FROM patient_personas
WHERE persona_id = 'cardiology_001_stemi_male_65';
"
```

---

## Rollback Plan

If insertion fails:

```bash
# Drop all inserted personas
psql -U postgres -h localhost -p 5433 -d irstudy_medical -c "
DELETE FROM patient_personas
WHERE persona_id LIKE 'cardiology_%'
   OR persona_id LIKE 'emergency_%'
   OR persona_id LIKE 'general_practice_%'
   OR persona_id LIKE 'pediatrics_%'
   OR persona_id LIKE 'respiratory_%';
"

# Verify deletion
psql -U postgres -h localhost -p 5433 -d irstudy_medical -c "SELECT COUNT(*) FROM patient_personas;"
# Expected: 0 (or previous count if other personas existed)
```

---

## Performance Targets

| Metric | Target | Actual |
|--------|--------|--------|
| Insertion time | <30 seconds | TBD |
| Queries per second | >100 QPS | TBD |
| p95 query latency | <50ms | TBD |
| Database size | <10 MB | TBD |

---

## Acceptance Criteria

- [ ] All 207 personas inserted
- [ ] Zero data loss (all JSON fields preserved)
- [ ] Database indexes created
- [ ] API endpoint returns personas
- [ ] Filtering works (specialty, difficulty, search)
- [ ] Insertion script is idempotent

---

## Estimated Timeline

| Task | Time |
|------|------|
| Create database schema | 15 min |
| Write insertion script | 30 min |
| Test dry run | 5 min |
| Execute insertion | 5 min |
| Verify data integrity | 10 min |
| Create API endpoint | 30 min |
| Test API | 15 min |
| Documentation | 10 min |
| **TOTAL** | **2 hours** |

---

**Created**: 2026-03-16
**Owner**: Backend Team
**Reviewer**: Database Team
**Status**: Ready for Ralph Loop Execution
