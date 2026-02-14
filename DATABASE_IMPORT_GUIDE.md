# Database Import Guide - MCQs & OSCEs

## 📍 Current Location

You are currently importing MCQs and OSCEs from **JSON files** into **PostgreSQL database** for the EMR Practice System and main irStudy platform.

---

## 📂 File Locations

### MCQ Data Files
**Location**: `/home/dev/Development/irStudy/data/mcqs/`

**Available Files** (total ~2.5MB):
```
week3_cardiology_200_mcqs.json       (1.1MB) - 200 cardiology MCQs ✅
week3_respiratory_200_mcqs.json      (1.1MB) - 200 respiratory MCQs ✅
psychiatry_depression_day1.json      (48KB)  - Depression MCQs
psychiatry_anxiety_bipolar_day2.json (53KB)  - Anxiety/Bipolar MCQs
psychiatry_psychosis_day3.json       (73KB)  - Psychosis MCQs
psychiatry_suicide_mha_day4.json     (65KB)  - Suicide/Mental Health Act
psychiatry_final_day5.json           (47KB)  - Final psychiatry MCQs
missing_topics_comprehensive_mcqs.json (1.1MB) - Additional topics
missing_psychiatry_150_mcqs.json     (266KB) - More psychiatry MCQs
```

### OSCE Data Files
**Location**: `/home/dev/Development/irStudy/data/osces/`

**Available Files** (total ~600KB):
```
cardiology_50_osces.json             (163KB) - 50 cardiology OSCEs ✅
respiratory_50_osces.json            (168KB) - 50 respiratory OSCEs ✅
psychiatry_40_osces.json             (137KB) - 40 psychiatry OSCEs
psychiatry_week1_osces.json          (33KB)  - Week 1 psychiatry
missing_topics_comprehensive_osces.json (73KB) - Additional OSCEs
missing_psychiatry_13_osces.json     (20KB)  - More psychiatry OSCEs
```

---

## 🗄️ Database Schema

### Database Models
**File**: `/home/dev/Development/irStudy/backend/src/db/models.py`

**Tables**:
1. **users** - User accounts (authentication, profiles)
2. **mcqs** - Multiple-choice questions
3. **osces** - OSCE scenarios
4. **mcq_attempts** - Student MCQ attempts (audit trail)
5. **user_progress** - Progress tracking per specialty
6. **user_favorite_mcqs** - Favorite MCQs (many-to-many)
7. **user_favorite_osces** - Favorite OSCEs (many-to-many)

### MCQ Table Schema

```python
class MCQ(Base):
    __tablename__ = "mcqs"

    # Primary fields
    id = Column(Integer, primary_key=True)
    question_id = Column(String(50), unique=True)  # e.g., "MCQ-CARD-001"
    question_text = Column(Text)
    options = Column(JSON)  # {"A": "...", "B": "...", ...}
    correct_answer = Column(String(1))  # A, B, C, D, or E

    # Educational content
    explanation = Column(Text)
    citation = Column(String(500))  # Australian guideline reference
    learning_points = Column(JSON)

    # Metadata
    specialty = Column(Enum(MedicalSpecialty))  # cardiology, respiratory, etc.
    difficulty = Column(Enum(DifficultyLevel))  # easy, medium, hard
    tags = Column(JSON)

    # Media
    image_url = Column(String(500))

    # Statistics
    times_attempted = Column(Integer, default=0)
    times_correct = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
```

### OSCE Table Schema

```python
class OSCE(Base):
    __tablename__ = "osces"

    # Primary fields
    id = Column(Integer, primary_key=True)
    osce_id = Column(String(50), unique=True)  # e.g., "OSCE-CARD-001"
    station_title = Column(String(255))
    station_type = Column(Enum(OSCEType))  # history_taking, examination, etc.

    # Instructions
    candidate_instructions = Column(Text)  # What candidate sees
    patient_instructions = Column(Text)    # For simulated patient
    examiner_instructions = Column(Text)   # Marking guide

    # Rubric (15-mark AMC format)
    rubric = Column(JSON)
    """
    {
        "introduction": {"max_marks": 1, "criteria": "..."},
        "history_taking": {"max_marks": 5, "criteria": "..."},
        ...
    }
    """

    # Metadata
    specialty = Column(Enum(MedicalSpecialty))
    difficulty = Column(Enum(DifficultyLevel))
    time_limit_minutes = Column(Integer, default=8)

    # Educational content
    learning_objectives = Column(JSON)
    key_points = Column(JSON)

    # Timestamps
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
```

---

## 🔧 Import Script

### Main Import Script
**File**: `/home/dev/Development/irStudy/scripts/load_sample_data.py`

**What it does**:
1. Reads MCQ/OSCE JSON files
2. Maps fields to database schema
3. Skips placeholder/invalid content
4. Inserts into PostgreSQL
5. Returns statistics

**Key Functions**:
- `load_mcqs_from_file(filepath, limit=None)` - Load MCQs from JSON
- `load_osces_from_file(filepath, limit=None)` - Load OSCEs from JSON
- `_map_specialty(topic)` - Map topic string to MedicalSpecialty enum
- `_map_difficulty(difficulty)` - Map difficulty string to DifficultyLevel enum
- `_format_citation(references)` - Format Australian guideline citations

---

## 🚀 How to Import Data

### Option 1: Import All Data (Recommended)

```bash
cd /home/dev/Development/irStudy

# Import 50 MCQs and 20 OSCEs (default)
python scripts/load_sample_data.py

# Import more data
python scripts/load_sample_data.py --mcqs 200 --osces 50
```

### Option 2: Clear and Reimport

```bash
# Clear existing data and import fresh
python scripts/load_sample_data.py --clear --mcqs 200 --osces 50
```

### Option 3: Import Specific Files

```python
from scripts.load_sample_data import DataLoader

loader = DataLoader()

# Load specific MCQ file
loader.load_mcqs_from_file('data/mcqs/week3_cardiology_200_mcqs.json', limit=100)

# Load specific OSCE file
loader.load_osces_from_file('data/osces/cardiology_50_osces.json', limit=25)

# Get statistics
stats = loader.get_stats()
print(f"MCQs: {stats['mcqs']}, OSCEs: {stats['osces']}")

loader.close()
```

---

## 🔗 EMR Integration

### How EMR Links to MCQ/OSCE Database

**File**: `/home/dev/Development/irStudy/emr-practice-system/integration/DATABASE_INTEGRATION.md`

**Shared Tables**:
1. **users** - Same users across MCQs, OSCEs, and EMR
2. **user_progress** - Extended to include EMR metrics

**New EMR Tables**:
1. **emr_sessions** - EMR practice sessions
   - Links to users via `user_id`
   - Links to OSCEs via `linked_osce_id` (optional)

2. **soap_notes** - SOAP note documentation
   - Links to emr_sessions via `session_id`

3. **prescriptions** - Practice prescriptions
   - Links to emr_sessions via `session_id`

4. **pathology_orders** - Practice pathology orders
   - Links to emr_sessions via `session_id`

**Integration Example**:
```sql
-- User practices OSCE, then documents in EMR
-- 1. User attempts OSCE (osces table)
-- 2. EMR session created with linked_osce_id (emr_sessions table)
-- 3. User documents SOAP note (soap_notes table)
-- 4. Progress tracked across both (user_progress table)

SELECT
    u.full_name,
    o.station_title,
    es.emr_type,
    sn.validation_score
FROM users u
JOIN emr_sessions es ON u.id = es.user_id
LEFT JOIN osces o ON es.linked_osce_id = o.id
LEFT JOIN soap_notes sn ON es.id = sn.session_id
WHERE u.id = 1;
```

---

## 📊 Database Statistics

### Current Data (After Import)

**Query Statistics**:
```python
from scripts.load_sample_data import DataLoader

loader = DataLoader()
stats = loader.get_stats()

print(f"Total MCQs: {stats['mcqs']}")
print(f"Total OSCEs: {stats['osces']}")
loader.close()
```

**Expected After Full Import**:
- MCQs: ~600+ (cardiology, respiratory, psychiatry)
- OSCEs: ~150+ (cardiology, respiratory, psychiatry)

### Query Examples

```python
from backend.src.db.models import MCQ, OSCE, MedicalSpecialty
from backend.src.db.base import get_db

db = next(get_db())

# Get all cardiology MCQs
cardio_mcqs = db.query(MCQ).filter(
    MCQ.specialty == MedicalSpecialty.CARDIOLOGY
).all()

# Get medium difficulty OSCEs
medium_osces = db.query(OSCE).filter(
    OSCE.difficulty == DifficultyLevel.MEDIUM
).all()

# Get MCQs with high success rate
hard_mcqs = db.query(MCQ).filter(
    MCQ.times_attempted > 10,
    (MCQ.times_correct / MCQ.times_attempted) < 0.5
).all()
```

---

## 🔍 Data Quality

### Validation Checks

The import script automatically:
1. ✅ Skips placeholder MCQs (regeneration_failed flag)
2. ✅ Skips invalid options ("Option A", "Option B" placeholders)
3. ✅ Maps specialty from topic strings
4. ✅ Formats Australian citations
5. ✅ Validates enum values
6. ✅ Extracts tags from topics

### Citation Format

**Input** (JSON):
```json
"references": [
    {"title": "eTG Cardiovascular", "page": 142},
    {"title": "AMH Cardiology", "page": 256}
]
```

**Output** (Database):
```
"eTG Cardiovascular p.142, AMH Cardiology p.256"
```

---

## 🛠️ Troubleshooting

### Error: "Database connection refused"

**Solution**:
```bash
# Check PostgreSQL is running
docker-compose ps

# Start database
docker-compose up -d db

# Wait for PostgreSQL to start
sleep 5

# Run import
python scripts/load_sample_data.py
```

### Error: "Enum value not found"

**Cause**: Specialty/difficulty string doesn't map to enum

**Solution**: Check `_map_specialty()` and `_map_difficulty()` mappings in `load_sample_data.py`

### Error: "Duplicate key violation"

**Cause**: MCQ/OSCE with same ID already exists

**Solution**:
```bash
# Clear database and reimport
python scripts/load_sample_data.py --clear
```

### Warning: "Skipped X placeholders"

**Normal**: Script automatically skips invalid/placeholder content

---

## 📈 Next Steps

1. ✅ **Import MCQs/OSCEs** into database
   ```bash
   python scripts/load_sample_data.py --mcqs 200 --osces 50
   ```

2. ✅ **Start Backend API**
   ```bash
   cd backend
   docker-compose up -d
   ```

3. ✅ **Test API Endpoints**
   ```bash
   # Get MCQs
   curl http://localhost:8001/api/v1/mcqs

   # Get OSCEs
   curl http://localhost:8001/api/v1/osces
   ```

4. ✅ **Start EMR Frontend**
   ```bash
   cd emr-frontend
   npm run dev
   ```

5. ✅ **Link EMR to OSCEs**
   - User selects OSCE scenario
   - EMR session created with `linked_osce_id`
   - User practices documenting the OSCE case in EMR

---

## 🔗 Related Files

**Database Models**: `/home/dev/Development/irStudy/backend/src/db/models.py`

**Import Script**: `/home/dev/Development/irStudy/scripts/load_sample_data.py`

**MCQ Data**: `/home/dev/Development/irStudy/data/mcqs/*.json`

**OSCE Data**: `/home/dev/Development/irStudy/data/osces/*.json`

**EMR Integration**: `/home/dev/Development/irStudy/emr-practice-system/integration/DATABASE_INTEGRATION.md`

**Backend API**: `/home/dev/Development/irStudy/backend/src/api/v1/mcqs.py`

---

## 📝 Summary

✅ **MCQs and OSCEs** are stored as **JSON files** in `/data/mcqs/` and `/data/osces/`

✅ **Import script** (`load_sample_data.py`) loads them into **PostgreSQL database**

✅ **Database schema** defined in `backend/src/db/models.py`

✅ **EMR system** links to OSCEs via `linked_osce_id` for integrated practice

✅ **Shared users and progress** across MCQs, OSCEs, and EMR

**Next**: Run import script to populate database, then start backend API! 🚀

---

**Last Updated**: 2026-02-03
**Status**: ✅ Ready to Import
