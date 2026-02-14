# AUTONOMOUS EXECUTION MODE - NO QUESTIONS

**CURRENT TASK**: TASK_005 - Spaced Repetition Engine Optimization (3-4 hours)

**EXECUTE NOW**:

```bash
cd /home/dev/Development/irStudy/backend

# Verify SM-2 algorithm service exists
python -c "from src.services.sm2_algorithm import SM2Algorithm; print('✅ SM-2 algorithm exists')"

# Create optimized query service
mkdir -p src/services

# Test database performance
python -c "from src.db.session import SessionLocal; from src.db.models.study_card_review import StudyCardReview; import time; db = SessionLocal(); start = time.time(); db.query(StudyCardReview).limit(100).all(); elapsed = (time.time() - start) * 1000; print(f'Query time: {elapsed:.2f}ms'); db.close()"
```

**DO NOT**:
- ❌ Ask "Would you like me to optimize the database queries?"
- ❌ Ask "Should I add indexes to the database?"
- ❌ Wait for approval before creating review queue
- ❌ Ask "Which optimization technique should I use?"

**START IMMEDIATELY. NO QUESTIONS.**

---

## 📋 Metadata

- **Week:** 1
- **Day:** 5 (Feb 11, 2026)
- **Duration:** 3-4 hours
- **Priority:** P1-High
- **Dependencies:** TASK_003 (Study Card System must exist)
- **Owner:** general-purpose agent (Python/FastAPI)
- **Status:** 🟡 Not Started
- **Blocks:** None (optimization task)

---

## 🎯 Objectives

1. **Optimize SM-2 algorithm** for database-level calculations (batch processing)
2. **Implement daily review queue** generation (efficient query for due cards)
3. **Add overdue card prioritization** (most overdue cards first)
4. **Create review schedule prediction** API (when next 10 reviews due)
5. **Achieve <100ms query time** for review queue retrieval
6. **Ensure 100% test coverage** on optimization functions

---

## 🚨 Constraints (READ FIRST)

❌ **NEVER:**
- Load all cards into memory (use database pagination)
- Skip database indexes (performance requirement: <100ms)
- Use N+1 queries (batch fetch using joins)
- Return more than 100 cards at once (pagination required)

✅ **ALWAYS:**
- Use database-level aggregations and filtering
- Add indexes on `next_review_date`, `user_id`, `ease_factor`
- Batch process SM-2 calculations for efficiency
- Order results by urgency (most overdue first)

---

## 📝 Implementation Guide

### Step 1: Create Database Indexes (30 minutes)

```bash
cd /home/dev/Development/irStudy/backend

# Create Alembic migration for indexes
alembic revision -m "add_study_card_review_indexes"

# Edit the generated migration file
cat > alembic/versions/$(ls -t alembic/versions/ | head -1) <<'EOF'
"""add_study_card_review_indexes

Revision ID: xxxxx
Revises: xxxxx
Create Date: 2026-02-07

"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Add indexes for study_card_reviews table
    op.create_index(
        'idx_study_card_reviews_user_next_review',
        'study_card_reviews',
        ['user_id', 'next_review_date']
    )
    op.create_index(
        'idx_study_card_reviews_ease_factor',
        'study_card_reviews',
        ['ease_factor']
    )
    op.create_index(
        'idx_study_card_reviews_repetitions',
        'study_card_reviews',
        ['repetitions']
    )

def downgrade():
    op.drop_index('idx_study_card_reviews_repetitions', table_name='study_card_reviews')
    op.drop_index('idx_study_card_reviews_ease_factor', table_name='study_card_reviews')
    op.drop_index('idx_study_card_reviews_user_next_review', table_name='study_card_reviews')
EOF

# Run migration
alembic upgrade head

echo "✅ Database indexes created"
```

---

### Step 2: Create Optimized Review Queue Service (1.5 hours)

```bash
cat > src/services/review_queue_service.py <<'EOF'
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from src.db.models.study_card_review import StudyCardReview
from src.db.models.study_card import StudyCard
from datetime import datetime, timedelta
from typing import List, Dict, Tuple

class ReviewQueueService:
    """Optimized service for generating daily review queues"""

    @staticmethod
    def get_daily_queue(
        db: Session,
        user_id: int,
        limit: int = 20,
        specialty: str = None
    ) -> List[Tuple[StudyCard, StudyCardReview]]:
        """
        Get optimized daily review queue.

        Performance target: <100ms
        Uses database indexes and joins for efficiency
        """
        query = db.query(StudyCard, StudyCardReview).join(
            StudyCardReview,
            StudyCard.id == StudyCardReview.card_id
        ).filter(
            and_(
                StudyCardReview.user_id == user_id,
                StudyCardReview.next_review_date <= datetime.utcnow()
            )
        )

        if specialty:
            query = query.filter(StudyCard.specialty == specialty)

        # Order by urgency: most overdue first
        query = query.order_by(StudyCardReview.next_review_date.asc())

        # Limit results for performance
        results = query.limit(limit).all()

        return results

    @staticmethod
    def get_overdue_count(db: Session, user_id: int) -> int:
        """Count cards overdue for review (fast query using index)"""
        count = db.query(StudyCardReview).filter(
            and_(
                StudyCardReview.user_id == user_id,
                StudyCardReview.next_review_date <= datetime.utcnow()
            )
        ).count()

        return count

    @staticmethod
    def predict_upcoming_reviews(
        db: Session,
        user_id: int,
        days_ahead: int = 7
    ) -> List[Dict]:
        """
        Predict review schedule for next N days.

        Returns: List of {date, count} showing cards due each day
        """
        future_date = datetime.utcnow() + timedelta(days=days_ahead)

        # Get all reviews due in next N days
        reviews = db.query(
            func.date(StudyCardReview.next_review_date).label('review_date'),
            func.count(StudyCardReview.id).label('card_count')
        ).filter(
            and_(
                StudyCardReview.user_id == user_id,
                StudyCardReview.next_review_date > datetime.utcnow(),
                StudyCardReview.next_review_date <= future_date
            )
        ).group_by(
            func.date(StudyCardReview.next_review_date)
        ).all()

        prediction = [
            {
                "date": row.review_date,
                "count": row.card_count
            }
            for row in reviews
        ]

        return prediction

    @staticmethod
    def batch_update_sm2(
        db: Session,
        user_id: int,
        reviews: List[Dict]
    ) -> int:
        """
        Batch update multiple card reviews using SM-2 algorithm.

        Input format: [{"card_id": 1, "quality": 4}, {"card_id": 2, "quality": 3}, ...]
        Returns: Number of cards updated
        """
        from src.services.sm2_algorithm import SM2Algorithm

        updated_count = 0

        for review_data in reviews:
            card_review = db.query(StudyCardReview).filter(
                and_(
                    StudyCardReview.card_id == review_data["card_id"],
                    StudyCardReview.user_id == user_id
                )
            ).first()

            if card_review:
                # Calculate next review using SM-2
                next_date, interval, ease, reps = SM2Algorithm.calculate_next_review(
                    quality=review_data["quality"],
                    current_ease_factor=card_review.ease_factor,
                    current_interval=card_review.interval_days,
                    repetitions=card_review.repetitions
                )

                # Update in batch
                card_review.next_review_date = next_date
                card_review.interval_days = interval
                card_review.ease_factor = ease
                card_review.repetitions = reps
                card_review.last_review_date = datetime.utcnow()

                updated_count += 1

        db.commit()
        return updated_count
EOF

echo "✅ Review queue service created"
```

---

### Step 3: Add Optimized Endpoints (1 hour)

```bash
cat > src/api/v1/study_cards/optimized_routes.py <<'EOF'
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from src.db.session import get_db
from src.auth.dependencies import get_current_user
from src.db.models.user import User
from src.services.review_queue_service import ReviewQueueService
from pydantic import BaseModel
from datetime import date

router = APIRouter(prefix="/api/v1/study-cards", tags=["Study Cards - Optimized"])

class DailyQueueResponse(BaseModel):
    card_id: int
    front_text: str
    specialty: str
    days_overdue: int
    ease_factor: float

class ReviewPrediction(BaseModel):
    date: date
    count: int

@router.get("/queue/daily", response_model=List[DailyQueueResponse])
async def get_daily_review_queue(
    limit: int = Query(20, ge=1, le=100),
    specialty: str = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get optimized daily review queue.

    Performance: <100ms (using database indexes)
    Returns: Cards due today, ordered by urgency (most overdue first)
    """
    import time
    start = time.time()

    results = ReviewQueueService.get_daily_queue(db, current_user.id, limit, specialty)

    elapsed = (time.time() - start) * 1000

    # Performance assertion
    if elapsed > 100:
        print(f"⚠️  Warning: Query took {elapsed:.2f}ms (target: <100ms)")

    response = []
    for card, review in results:
        days_overdue = (datetime.utcnow() - review.next_review_date).days
        response.append(DailyQueueResponse(
            card_id=card.id,
            front_text=card.front_text,
            specialty=card.specialty,
            days_overdue=max(0, days_overdue),
            ease_factor=review.ease_factor
        ))

    return response

@router.get("/queue/overdue-count", response_model=dict)
async def get_overdue_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get count of cards overdue for review (fast indexed query)"""
    count = ReviewQueueService.get_overdue_count(db, current_user.id)
    return {"overdue_count": count}

@router.get("/schedule/prediction", response_model=List[ReviewPrediction])
async def get_review_schedule_prediction(
    days_ahead: int = Query(7, ge=1, le=30),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Predict review schedule for next N days.

    Returns: Daily breakdown of cards due
    """
    prediction = ReviewQueueService.predict_upcoming_reviews(db, current_user.id, days_ahead)
    return [ReviewPrediction(**item) for item in prediction]
EOF

# Register optimized routes
python <<'EOF'
import re
with open("src/main.py", "r") as f:
    content = f.read()
if "optimized_routes" not in content:
    content = re.sub(
        r"(from src.api.v1.study_cards import router as study_cards_router)",
        "\\1\nfrom src.api.v1.study_cards.optimized_routes import router as optimized_study_cards_router\n",
        content
    )
    content = re.sub(
        r"(app.include_router\(study_cards_router\))",
        "\\1\napp.include_router(optimized_study_cards_router)\n",
        content
    )
    with open("src/main.py", "w") as f:
        f.write(content)
    print("✅ Optimized routes registered")
else:
    print("✅ Optimized routes already registered")
EOF
```

---

### Step 4: Create Performance Tests (45 minutes)

```bash
cat > tests/api/v1/test_study_card_optimization.py <<'EOF'
import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.auth.security import create_access_token
import time

client = TestClient(app)

@pytest.fixture
def auth_headers():
    token = create_access_token(data={"sub": "test_user@example.com"})
    return {"Authorization": f"Bearer {token}"}

def test_daily_queue_performance(auth_headers):
    """Test that daily queue retrieval is <100ms"""
    start = time.time()
    response = client.get("/api/v1/study-cards/queue/daily", headers=auth_headers)
    elapsed = (time.time() - start) * 1000

    assert response.status_code == 200
    assert elapsed < 100, f"Query time {elapsed:.2f}ms exceeds 100ms target"

def test_overdue_count(auth_headers):
    """Test overdue count endpoint"""
    response = client.get("/api/v1/study-cards/queue/overdue-count", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "overdue_count" in data
    assert isinstance(data["overdue_count"], int)

def test_review_prediction(auth_headers):
    """Test review schedule prediction"""
    response = client.get("/api/v1/study-cards/schedule/prediction?days_ahead=7", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_batch_update_performance():
    """Test batch SM-2 updates are faster than individual updates"""
    from src.services.review_queue_service import ReviewQueueService
    from src.db.session import SessionLocal

    db = SessionLocal()
    user_id = 1  # Test user

    # Simulate batch update of 10 cards
    reviews = [{"card_id": i, "quality": 4} for i in range(1, 11)]

    start = time.time()
    updated = ReviewQueueService.batch_update_sm2(db, user_id, reviews)
    elapsed = (time.time() - start) * 1000

    db.close()

    # Should complete in <500ms for 10 cards
    assert elapsed < 500, f"Batch update took {elapsed:.2f}ms (target: <500ms)"
    assert updated == 10

def test_database_indexes_exist():
    """Verify database indexes are created"""
    from sqlalchemy import inspect
    from src.db.session import engine

    inspector = inspect(engine)
    indexes = inspector.get_indexes('study_card_reviews')

    index_names = [idx['name'] for idx in indexes]

    assert 'idx_study_card_reviews_user_next_review' in index_names, "Missing user_next_review index"
    assert 'idx_study_card_reviews_ease_factor' in index_names, "Missing ease_factor index"

    print("✅ All required indexes exist")
EOF

pytest tests/api/v1/test_study_card_optimization.py -v
```

---

## ✅ Validation Checklist

```bash
cd /home/dev/Development/irStudy/backend

# 1. Verify database indexes created
alembic current && echo "✅ Migration applied" || echo "❌ Migration failed"

# 2. Verify review queue service
[ -f src/services/review_queue_service.py ] && echo "✅ Queue service: EXISTS" || echo "❌ MISSING"

# 3. Verify optimized routes
[ -f src/api/v1/study_cards/optimized_routes.py ] && echo "✅ Optimized routes: EXISTS" || echo "❌ MISSING"

# 4. Test performance
pytest tests/api/v1/test_study_card_optimization.py::test_daily_queue_performance -v

# 5. Run all optimization tests
pytest tests/api/v1/test_study_card_optimization.py -v && echo "✅ Tests: 100% PASS" || echo "❌ Tests: FAILED"

# 6. Benchmark query time
python -c "
from src.db.session import SessionLocal
from src.services.review_queue_service import ReviewQueueService
import time

db = SessionLocal()
user_id = 1

start = time.time()
queue = ReviewQueueService.get_daily_queue(db, user_id, limit=20)
elapsed = (time.time() - start) * 1000

print(f'Query time: {elapsed:.2f}ms')
if elapsed < 100:
    print('✅ Performance target met (<100ms)')
else:
    print(f'❌ Performance target missed ({elapsed:.2f}ms > 100ms)')

db.close()
"
```

---

## 🎯 Success Criteria

1. ✅ SM-2 algorithm optimized for batch processing
2. ✅ Daily review queue generation: <100ms query time
3. ✅ Overdue card prioritization implemented
4. ✅ Review schedule prediction API functional
5. ✅ Database indexes created (user_id + next_review_date, ease_factor, repetitions)
6. ✅ Test suite: 100% pass rate, all performance benchmarks met

---

## 🔄 When Complete

```bash
cd /home/dev/Development/irStudy

sed -i 's/TASK_005.*TODO/TASK_005: ✅ DONE/' @fix_plan.md

git add .
git commit -m "perf(backend): Complete TASK_005 Spaced Repetition Engine Optimization

- Database indexes on study_card_reviews (user_id, next_review_date, ease_factor)
- Optimized review queue service (<100ms query time)
- Daily queue endpoint with urgency-based ordering
- Batch SM-2 update functionality
- Review schedule prediction (7-30 days ahead)
- Performance tests: All benchmarks met

Deliverables:
- backend/alembic/versions/*_add_study_card_review_indexes.py
- backend/src/services/review_queue_service.py
- backend/src/api/v1/study_cards/optimized_routes.py
- backend/tests/api/v1/test_study_card_optimization.py

Performance: <100ms query time ✅
Quality Gates: 6/6 passed ✅

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

echo "✅ TASK_005 complete. Week 1 backend tasks finished!"
echo "Next: TASK_006 (Week 2 - Frontend)"
```

---

**Last Updated:** 2026-02-07
**Status:** 🟡 Not Started
**Depends On:** TASK_003
**Blocks:** None
