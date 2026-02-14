# Study Cards - Quick Start Guide

This guide helps you get started with the Study Cards feature that has been added to the irStudy platform.

---

## What's Been Implemented

The complete database infrastructure for Study Cards including:

1. **Database Model** (`StudyCard`) with SM-2 spaced repetition algorithm
2. **Pydantic Schemas** for API validation
3. **Alembic Migration** to create the `study_cards` table
4. **Seed Script** to import study cards from JSON files

---

## Quick Start (5 minutes)

### 1. Run the Migration

```bash
cd backend
docker-compose exec backend alembic upgrade head
```

**Expected output:**
```
INFO  [alembic.runtime.migration] Running upgrade 001 -> 002, Add study cards table
```

### 2. Import Study Cards

```bash
# From the project root directory
python3 scripts/seed_database.py --study-cards
```

**Expected output:**
```
Study Card Database Seeding
======================================================================
Found 5 JSON files
...
Study Cards:
  Total cards found: 125
  Loaded (new): 125
✓✓ Done!
```

### 3. Verify Import

```bash
docker-compose exec postgres psql -U postgres -d irstudy -c "SELECT COUNT(*) FROM study_cards;"
```

**Expected output:**
```
 count
-------
   125
```

---

## View Sample Cards

```bash
docker-compose exec postgres psql -U postgres -d irstudy -c "
SELECT
    card_id,
    specialty,
    topic,
    difficulty,
    LEFT(question, 60) as question_preview
FROM study_cards
ORDER BY specialty, topic
LIMIT 10;
"
```

---

## Study Card Statistics

```bash
docker-compose exec postgres psql -U postgres -d irstudy -c "
SELECT
    specialty,
    difficulty,
    COUNT(*) as card_count
FROM study_cards
GROUP BY specialty, difficulty
ORDER BY specialty, difficulty;
"
```

---

## Spaced Repetition Algorithm (SM-2)

Study cards use the SM-2 algorithm to optimize review scheduling:

**Quality Ratings:**
- 0: Complete blackout (forgot completely)
- 1: Incorrect, but familiar
- 2: Incorrect, easy to recall
- 3: Correct, difficult recall
- 4: Correct, hesitation
- 5: Perfect recall

**Review Schedule Example:**
- 1st review (quality 4): Next review in **1 day**
- 2nd review (quality 5): Next review in **6 days**
- 3rd review (quality 4): Next review in **15 days**
- 4th review (quality 5): Next review in **37 days**
- 5th review (quality 3): Next review in **93 days**

---

## Data Structure

Study cards are stored in `/data/study_cards/*.json`:

```
data/study_cards/
├── cardiology_study_cards.json (25 cards)
├── respiratory_study_cards.json (25 cards)
├── psychiatry_study_cards.json (25 cards)
├── missing_psychiatry_13_cards.json (13 cards)
└── missing_topics_comprehensive_cards.json (37 cards)

Total: 125 study cards
```

---

## Next Steps: API Development

### Create API Router

**File:** `backend/src/api/v1/study_cards.py`

**Endpoints needed:**

1. `GET /study-cards` - List all cards (with filters)
2. `GET /study-cards/{card_id}` - Get single card
3. `POST /study-cards/{card_id}/review` - Submit review
4. `GET /study-cards/due` - Get cards due today
5. `GET /study-cards/statistics` - User stats

### Create Frontend Components

**Components needed:**

1. `StudyCardDeck.tsx` - Main card interface
2. `StudyCardFlip.tsx` - Flip animation
3. `StudyCardReview.tsx` - Quality rating buttons
4. `StudyCardProgress.tsx` - Progress dashboard

---

## Troubleshooting

### Migration fails

```bash
# Check current migration version
docker-compose exec backend alembic current

# Check pending migrations
docker-compose exec backend alembic heads

# Downgrade if needed
docker-compose exec backend alembic downgrade -1
```

### Import fails

```bash
# Run with --dry-run to validate without inserting
python3 scripts/seed_database.py --study-cards --dry-run

# Force update existing cards
python3 scripts/seed_database.py --study-cards --force
```

### Database connection issues

```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check DATABASE_URL environment variable
echo $DATABASE_URL

# Restart PostgreSQL
docker-compose restart postgres
```

---

## Study Card Schema

```sql
CREATE TABLE study_cards (
    id                SERIAL PRIMARY KEY,
    user_id           INTEGER REFERENCES users(id),
    card_id           VARCHAR(50) UNIQUE NOT NULL,
    specialty         medicalspecialty NOT NULL,
    topic             VARCHAR(255) NOT NULL,
    subtopic          VARCHAR(255),
    question          TEXT NOT NULL,
    answer            TEXT NOT NULL,
    explanation       TEXT,
    citations         JSON NOT NULL,
    difficulty        difficultylevel DEFAULT 'medium',
    tags              JSON,
    card_type         VARCHAR(50) DEFAULT 'concept',
    next_review_date  TIMESTAMP WITH TIME ZONE DEFAULT now(),
    interval_days     INTEGER DEFAULT 1,
    ease_factor       FLOAT DEFAULT 2.5,
    repetitions       INTEGER DEFAULT 0,
    is_active         BOOLEAN DEFAULT true,
    created_at        TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at        TIMESTAMP WITH TIME ZONE DEFAULT now(),
    deleted_at        TIMESTAMP WITH TIME ZONE
);
```

---

## Additional Resources

- **Full Documentation:** `STUDY_CARD_IMPLEMENTATION_SUMMARY.md`
- **Database Models:** `backend/src/db/models.py` (line 545+)
- **Pydantic Schemas:** `backend/src/schemas/study_card.py`
- **Migration:** `backend/alembic/versions/20260207_0805_002_add_study_cards_table.py`

---

**Last Updated:** 2026-02-07
**Status:** Database infrastructure complete, ready for API development
