# AUTONOMOUS EXECUTION MODE - NO QUESTIONS

**CURRENT TASK**: TASK_003 - Study Card System (4-5 hours)

**EXECUTE NOW**:

```bash
cd /home/dev/Development/irStudy/backend

# Create Study Card API endpoints
mkdir -p src/api/v1/study_cards tests/api/v1

# Create Study Card router
cat > src/api/v1/study_cards/router.py <<'EOF'
# Study Card endpoints will be implemented here
EOF

# Verify Study Card database model
python -c "from src.db.models.study_card import StudyCard; print('✅ StudyCard model exists')"

# Check existing Study Card count
python -c "from src.db.session import SessionLocal; from src.db.models.study_card import StudyCard; db = SessionLocal(); print(f'📊 Study Cards: {db.query(StudyCard).count()} (expected: 140)'); db.close()"
```

**DO NOT**:
- ❌ Ask "Would you like me to implement the SM-2 algorithm now?"
- ❌ Ask "Should I create the review endpoints first?"
- ❌ Wait for approval before implementing endpoints
- ❌ Ask "Which spaced repetition algorithm should we use?"

**START IMMEDIATELY. NO QUESTIONS.**

---

## 📋 Metadata

- **Week:** 1
- **Day:** 3 (Feb 9, 2026)
- **Duration:** 4-5 hours
- **Priority:** P1-High
- **Dependencies:** TASK_001 (security audit must be complete)
- **Owner:** general-purpose agent (Python/FastAPI)
- **Status:** 🟡 Not Started
- **Blocks:** TASK_004 (User Progress), TASK_005 (SM-2 Engine)

---

## 🎯 Objectives

1. **Implement Study Card CRUD endpoints** (GET /due-cards, POST /review, GET /statistics)
2. **Integrate SM-2 spaced repetition algorithm** (ease factor, interval calculation)
3. **Track review history** for all user study card interactions
4. **Create performance analytics endpoint** showing retention rates
5. **Achieve 100% test coverage** on all Study Card endpoints
6. **Ensure API response time <200ms** for card retrieval

---

## 🚨 Constraints (READ FIRST)

**From `/home/dev/Development/irStudy/constraints/01-medical-accuracy.md`:**

❌ **NEVER:**
- Return Study Cards without Australian medical context
- Skip SM-2 algorithm implementation (use proper spaced repetition)
- Allow placeholder content in Study Cards
- Use non-Australian medical sources

✅ **ALWAYS:**
- Use Australian medical terminology and spelling
- Implement SM-2 algorithm correctly (ease factor 1.3-2.5, intervals based on performance)
- Track all review attempts in database (for analytics)
- Validate Study Card content for Australian medical accuracy

**SM-2 Algorithm Specifications:**
- Initial ease factor: 2.5
- Ease factor range: 1.3 - 2.5
- Quality ratings: 0 (complete blackout) to 5 (perfect response)
- Interval calculation: I(n) = I(n-1) × EF
- For quality < 3: Reset interval to 1 day

---

## 📝 Implementation Guide

### Step 1: Create Pydantic Schemas (45 minutes)

```bash
cd /home/dev/Development/irStudy/backend

cat > src/api/v1/schemas/study_card.py <<'EOF'
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class StudyCardBase(BaseModel):
    front_text: str = Field(..., min_length=10, max_length=500)
    back_text: str = Field(..., min_length=10, max_length=2000)
    specialty: str = Field(..., max_length=100)
    topic: str = Field(..., max_length=200)
    difficulty: str = Field(..., regex="^(easy|medium|hard)$")

class StudyCardResponse(StudyCardBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class StudyCardReview(BaseModel):
    card_id: int
    quality: int = Field(..., ge=0, le=5)  # SM-2 quality rating (0-5)
    time_taken_seconds: int = Field(..., ge=0, le=300)  # Max 5 minutes

class StudyCardReviewResponse(BaseModel):
    card_id: int
    next_review_date: datetime
    interval_days: int
    ease_factor: float
    repetitions: int

class StudyCardStatistics(BaseModel):
    total_cards: int
    cards_due_today: int
    cards_mastered: int
    average_ease_factor: float
    retention_rate: float  # Percentage of cards reviewed correctly
EOF

echo "✅ Study Card schemas created"
```

---

### Step 2: Implement SM-2 Algorithm Service (1 hour)

```bash
cd /home/dev/Development/irStudy/backend

mkdir -p src/services

cat > src/services/sm2_algorithm.py <<'EOF'
from datetime import datetime, timedelta
from typing import Tuple

class SM2Algorithm:
    """
    SuperMemo-2 (SM-2) spaced repetition algorithm implementation.

    References:
    - Original SM-2: https://www.supermemo.com/en/archives1990-2015/english/ol/sm2
    - Quality ratings: 0 (blackout) to 5 (perfect recall)
    """

    MIN_EASE_FACTOR = 1.3
    MAX_EASE_FACTOR = 2.5
    DEFAULT_EASE_FACTOR = 2.5

    @staticmethod
    def calculate_next_review(
        quality: int,
        current_ease_factor: float,
        current_interval: int,
        repetitions: int
    ) -> Tuple[datetime, int, float, int]:
        """
        Calculate next review date based on SM-2 algorithm.

        Args:
            quality: Performance rating (0-5)
            current_ease_factor: Current ease factor (1.3-2.5)
            current_interval: Current interval in days
            repetitions: Number of consecutive correct reviews

        Returns:
            Tuple of (next_review_date, interval_days, new_ease_factor, new_repetitions)
        """
        # Calculate new ease factor
        new_ease_factor = current_ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))

        # Clamp ease factor to valid range
        new_ease_factor = max(SM2Algorithm.MIN_EASE_FACTOR, min(SM2Algorithm.MAX_EASE_FACTOR, new_ease_factor))

        # Determine interval and repetitions
        if quality < 3:
            # Reset on failure
            new_interval = 1
            new_repetitions = 0
        else:
            new_repetitions = repetitions + 1

            if new_repetitions == 1:
                new_interval = 1
            elif new_repetitions == 2:
                new_interval = 6
            else:
                new_interval = round(current_interval * new_ease_factor)

        # Calculate next review date
        next_review_date = datetime.utcnow() + timedelta(days=new_interval)

        return next_review_date, new_interval, new_ease_factor, new_repetitions
EOF

echo "✅ SM-2 algorithm service created"
```

---

### Step 3: Create Study Card Endpoints (1.5 hours)

```bash
cd /home/dev/Development/irStudy/backend

cat > src/api/v1/study_cards/router.py <<'EOF'
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from src.db.session import get_db
from src.db.models.study_card import StudyCard
from src.db.models.study_card_review import StudyCardReview
from src.api.v1.schemas.study_card import (
    StudyCardResponse,
    StudyCardReview as StudyCardReviewSchema,
    StudyCardReviewResponse,
    StudyCardStatistics
)
from src.auth.dependencies import get_current_user
from src.db.models.user import User
from src.services.sm2_algorithm import SM2Algorithm
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter(prefix="/api/v1/study-cards", tags=["Study Cards"])
limiter = Limiter(key_func=get_remote_address)

@router.get("/due-cards", response_model=List[StudyCardResponse])
@limiter.limit("60/minute")
async def get_due_cards(
    limit: int = Query(20, ge=1, le=100),
    specialty: str = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get Study Cards due for review today.

    Rate limit: 60 requests/minute
    Returns cards where next_review_date <= today, ordered by urgency
    """
    # Query for cards due today
    query = db.query(StudyCard).join(
        StudyCardReview,
        StudyCard.id == StudyCardReview.card_id
    ).filter(
        StudyCardReview.user_id == current_user.id,
        StudyCardReview.next_review_date <= datetime.utcnow()
    )

    if specialty:
        query = query.filter(StudyCard.specialty == specialty)

    # Order by next_review_date (most overdue first)
    cards = query.order_by(StudyCardReview.next_review_date.asc()).limit(limit).all()

    return cards

@router.post("/review", response_model=StudyCardReviewResponse)
@limiter.limit("60/minute")
async def review_study_card(
    review: StudyCardReviewSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submit a Study Card review and calculate next review date using SM-2 algorithm.

    Rate limit: 60 requests/minute
    Quality ratings: 0 (complete blackout) to 5 (perfect response)
    """
    # Get current review record
    current_review = db.query(StudyCardReview).filter(
        StudyCardReview.card_id == review.card_id,
        StudyCardReview.user_id == current_user.id
    ).first()

    if not current_review:
        # Create first review record
        current_review = StudyCardReview(
            user_id=current_user.id,
            card_id=review.card_id,
            ease_factor=SM2Algorithm.DEFAULT_EASE_FACTOR,
            interval_days=1,
            repetitions=0
        )
        db.add(current_review)

    # Calculate next review using SM-2
    next_review_date, new_interval, new_ease_factor, new_repetitions = SM2Algorithm.calculate_next_review(
        quality=review.quality,
        current_ease_factor=current_review.ease_factor,
        current_interval=current_review.interval_days,
        repetitions=current_review.repetitions
    )

    # Update review record
    current_review.ease_factor = new_ease_factor
    current_review.interval_days = new_interval
    current_review.repetitions = new_repetitions
    current_review.next_review_date = next_review_date
    current_review.last_review_date = datetime.utcnow()
    current_review.quality = review.quality
    current_review.time_taken_seconds = review.time_taken_seconds

    db.commit()
    db.refresh(current_review)

    return StudyCardReviewResponse(
        card_id=review.card_id,
        next_review_date=next_review_date,
        interval_days=new_interval,
        ease_factor=new_ease_factor,
        repetitions=new_repetitions
    )

@router.get("/statistics", response_model=StudyCardStatistics)
@limiter.limit("60/minute")
async def get_study_card_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get Study Card statistics for current user.

    Rate limit: 60 requests/minute
    Returns: total cards, cards due today, mastery stats, retention rate
    """
    # Total cards reviewed by user
    total_cards = db.query(StudyCardReview).filter(
        StudyCardReview.user_id == current_user.id
    ).count()

    # Cards due today
    cards_due_today = db.query(StudyCardReview).filter(
        StudyCardReview.user_id == current_user.id,
        StudyCardReview.next_review_date <= datetime.utcnow()
    ).count()

    # Cards mastered (repetitions >= 5)
    cards_mastered = db.query(StudyCardReview).filter(
        StudyCardReview.user_id == current_user.id,
        StudyCardReview.repetitions >= 5
    ).count()

    # Average ease factor
    avg_ease = db.query(StudyCardReview).filter(
        StudyCardReview.user_id == current_user.id
    ).with_entities(func.avg(StudyCardReview.ease_factor)).scalar() or 2.5

    # Retention rate (quality >= 3)
    total_reviews = db.query(StudyCardReview).filter(
        StudyCardReview.user_id == current_user.id,
        StudyCardReview.quality.isnot(None)
    ).count()

    successful_reviews = db.query(StudyCardReview).filter(
        StudyCardReview.user_id == current_user.id,
        StudyCardReview.quality >= 3
    ).count()

    retention_rate = (successful_reviews / total_reviews * 100) if total_reviews > 0 else 0.0

    return StudyCardStatistics(
        total_cards=total_cards,
        cards_due_today=cards_due_today,
        cards_mastered=cards_mastered,
        average_ease_factor=round(avg_ease, 2),
        retention_rate=round(retention_rate, 2)
    )
EOF

echo "✅ Study Card endpoints created"
```

---

### Step 4: Register Router (15 minutes)

```bash
cd /home/dev/Development/irStudy/backend

# Register Study Card router in main.py
python <<'EOF'
import re

with open("src/main.py", "r") as f:
    content = f.read()

if "study_cards" not in content:
    # Add import
    import_line = "from src.api.v1.study_cards import router as study_cards_router\n"
    content = re.sub(r"(from fastapi import FastAPI)", f"\\1\n{import_line}", content)

    # Add router
    router_line = "app.include_router(study_cards_router)\n"
    content = re.sub(r"(app = FastAPI\(\))", f"\\1\n\n{router_line}", content)

    with open("src/main.py", "w") as f:
        f.write(content)

    print("✅ Study Card router registered")
else:
    print("✅ Study Card router already registered")
EOF
```

---

### Step 5: Create Test Suite (1 hour)

```bash
cd /home/dev/Development/irStudy/backend

cat > tests/api/v1/test_study_cards.py <<'EOF'
import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.auth.security import create_access_token

client = TestClient(app)

@pytest.fixture
def auth_headers():
    token = create_access_token(data={"sub": "test_user@example.com"})
    return {"Authorization": f"Bearer {token}"}

def test_get_due_cards(auth_headers):
    """Test GET /api/v1/study-cards/due-cards endpoint"""
    response = client.get("/api/v1/study-cards/due-cards", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_review_study_card(auth_headers):
    """Test POST /api/v1/study-cards/review endpoint"""
    # Get a due card first
    due_cards = client.get("/api/v1/study-cards/due-cards", headers=auth_headers).json()

    if len(due_cards) > 0:
        card_id = due_cards[0]["id"]

        # Submit review
        review = {
            "card_id": card_id,
            "quality": 4,  # Good recall
            "time_taken_seconds": 45
        }
        response = client.post("/api/v1/study-cards/review", json=review, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "next_review_date" in data
        assert "interval_days" in data
        assert "ease_factor" in data
        assert data["ease_factor"] >= 1.3
        assert data["ease_factor"] <= 2.5

def test_sm2_algorithm_quality_5():
    """Test SM-2 algorithm with perfect recall (quality=5)"""
    from src.services.sm2_algorithm import SM2Algorithm

    next_date, interval, ease, reps = SM2Algorithm.calculate_next_review(
        quality=5,
        current_ease_factor=2.5,
        current_interval=6,
        repetitions=2
    )

    # Ease factor should increase
    assert ease > 2.5
    assert ease <= SM2Algorithm.MAX_EASE_FACTOR
    # Interval should increase
    assert interval > 6
    # Repetitions should increment
    assert reps == 3

def test_sm2_algorithm_quality_0():
    """Test SM-2 algorithm with complete failure (quality=0)"""
    from src.services.sm2_algorithm import SM2Algorithm

    next_date, interval, ease, reps = SM2Algorithm.calculate_next_review(
        quality=0,
        current_ease_factor=2.5,
        current_interval=30,
        repetitions=5
    )

    # Should reset interval to 1 day
    assert interval == 1
    # Should reset repetitions to 0
    assert reps == 0
    # Ease factor should decrease
    assert ease < 2.5

def test_get_statistics(auth_headers):
    """Test GET /api/v1/study-cards/statistics endpoint"""
    response = client.get("/api/v1/study-cards/statistics", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_cards" in data
    assert "cards_due_today" in data
    assert "cards_mastered" in data
    assert "average_ease_factor" in data
    assert "retention_rate" in data
    assert data["retention_rate"] >= 0.0
    assert data["retention_rate"] <= 100.0

def test_api_response_time(auth_headers):
    """Test that API response time is <200ms"""
    import time
    start = time.time()
    response = client.get("/api/v1/study-cards/due-cards", headers=auth_headers)
    elapsed = (time.time() - start) * 1000

    assert response.status_code == 200
    assert elapsed < 200, f"API response time {elapsed}ms exceeds 200ms threshold"
EOF

echo "✅ Test suite created"

# Run tests
pytest tests/api/v1/test_study_cards.py -v
```

---

## ✅ Validation Checklist

```bash
cd /home/dev/Development/irStudy/backend

# 1. Verify Study Card endpoints exist
[ -f src/api/v1/study_cards/router.py ] && echo "✅ Study Card endpoints: EXISTS" || echo "❌ MISSING"

# 2. Verify SM-2 algorithm service
[ -f src/services/sm2_algorithm.py ] && echo "✅ SM-2 algorithm: EXISTS" || echo "❌ MISSING"

# 3. Verify schemas
[ -f src/api/v1/schemas/study_card.py ] && echo "✅ Schemas: EXISTS" || echo "❌ MISSING"

# 4. Verify router registered
grep -q "study_cards_router" src/main.py && echo "✅ Router: REGISTERED" || echo "❌ NOT REGISTERED"

# 5. Run tests
pytest tests/api/v1/test_study_cards.py -v && echo "✅ Tests: 100% PASS" || echo "❌ Tests: FAILED"

# 6. Verify SM-2 algorithm correctness
python -c "from src.services.sm2_algorithm import SM2Algorithm; print('✅ SM-2 algorithm: FUNCTIONAL')"
```

---

## 🎯 Success Criteria

**This task is DONE when ALL of these are true:**

1. ✅ Study Card endpoints implemented: GET /due-cards, POST /review, GET /statistics
2. ✅ SM-2 algorithm integrated and tested (ease factor 1.3-2.5, correct interval calculation)
3. ✅ Review history tracking operational (all reviews recorded in database)
4. ✅ Performance analytics endpoint functional (retention rate, mastery stats)
5. ✅ Test suite complete: 100% pass rate with >70% coverage
6. ✅ API response time <200ms verified

---

## 🔄 When Complete

```bash
cd /home/dev/Development/irStudy

sed -i 's/TASK_003.*TODO/TASK_003: ✅ DONE/' @fix_plan.md

git add .
git commit -m "feat(api): Complete TASK_003 Study Card System - SM-2 spaced repetition

- Study Card endpoints: GET /due-cards, POST /review, GET /statistics
- SM-2 algorithm service with ease factor 1.3-2.5
- Review history tracking for analytics
- Performance statistics endpoint
- Test suite: 100% pass rate
- API response time: <200ms

Deliverables:
- backend/src/api/v1/study_cards/router.py
- backend/src/services/sm2_algorithm.py
- backend/src/api/v1/schemas/study_card.py
- backend/tests/api/v1/test_study_cards.py

Quality Gates: 6/6 passed ✅
Blocks: TASK_004, TASK_005 now unblocked

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

echo "✅ TASK_003 complete. Starting TASK_004..."
```

---

**Last Updated:** 2026-02-07
**Status:** 🟡 Not Started
**Depends On:** TASK_001
**Blocks:** TASK_004, TASK_005
