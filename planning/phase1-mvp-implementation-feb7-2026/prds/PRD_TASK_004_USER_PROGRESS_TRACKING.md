# AUTONOMOUS EXECUTION MODE - NO QUESTIONS

**CURRENT TASK**: TASK_004 - User Progress Tracking (4-5 hours)

**EXECUTE NOW**:

```bash
cd /home/dev/Development/irStudy/backend

# Create User Progress API endpoints
mkdir -p src/api/v1/progress tests/api/v1

# Verify database models exist
python -c "from src.db.models.user_progress import UserProgress; print('✅ UserProgress model exists')"
python -c "from src.db.models.mcq_attempt import MCQAttempt; print('✅ MCQAttempt model exists')"
```

**DO NOT**:
- ❌ Ask "Would you like me to create the dashboard endpoint?"
- ❌ Ask "Should I calculate weekly trends first?"
- ❌ Wait for approval before implementing analytics
- ❌ Ask "Which metrics should I prioritize?"

**START IMMEDIATELY. NO QUESTIONS.**

---

## 📋 Metadata

- **Week:** 1
- **Day:** 4-5 (Feb 10-11, 2026)
- **Duration:** 4-5 hours
- **Priority:** P1-High
- **Dependencies:** TASK_002 (Question CRUD), TASK_003 (Study Cards)
- **Owner:** general-purpose agent (Python/FastAPI)
- **Status:** 🟡 Not Started
- **Blocks:** TASK_008 (Performance Dashboard frontend)

---

## 🎯 Objectives

1. **Implement progress tracking endpoints** (GET /dashboard, GET /specialty/{name}, GET /weak-areas)
2. **Calculate MCQ performance metrics** (accuracy rate, average time, attempts by specialty)
3. **Track OSCE completion** with performance scores
4. **Generate Study Card statistics** (cards reviewed, retention rate, mastery level)
5. **Compute weekly/monthly trends** for progress visualization
6. **Achieve 100% test coverage** on all progress endpoints

---

## 🚨 Constraints (READ FIRST)

❌ **NEVER:**
- Expose other users' progress data (privacy violation)
- Skip input validation on date ranges
- Return raw user IDs or sensitive data
- Calculate metrics incorrectly (accuracy formula: correct/total × 100)

✅ **ALWAYS:**
- Filter all queries by current_user.id (never allow cross-user data access)
- Validate date ranges (start_date <= end_date, not in future)
- Use database-level aggregations (efficient SQL queries)
- Return percentages rounded to 2 decimal places

---

## 📝 Implementation Guide

### Step 1: Create Progress Schemas (30 minutes)

```bash
cd /home/dev/Development/irStudy/backend

cat > src/api/v1/schemas/progress.py <<'EOF'
from pydantic import BaseModel, Field
from typing import List, Dict
from datetime import datetime

class SpecialtyPerformance(BaseModel):
    specialty: str
    total_attempts: int
    correct_attempts: int
    accuracy_rate: float = Field(..., ge=0.0, le=100.0)
    average_time_seconds: int

class DashboardResponse(BaseModel):
    total_mcq_attempts: int
    mcq_accuracy_rate: float
    total_osce_completions: int
    study_cards_reviewed: int
    study_card_retention_rate: float
    specialty_breakdown: List[SpecialtyPerformance]
    weak_areas: List[str]  # Specialties with <70% accuracy

class WeeklyTrend(BaseModel):
    week_start: datetime
    mcq_attempts: int
    accuracy_rate: float
    study_cards_reviewed: int

class MonthlyTrend(BaseModel):
    month: str  # YYYY-MM format
    mcq_attempts: int
    accuracy_rate: float
    osce_completions: int

class WeakArea(BaseModel):
    specialty: str
    accuracy_rate: float
    total_attempts: int
    recommended_study_cards: int
EOF

echo "✅ Progress schemas created"
```

---

### Step 2: Create Progress Analytics Service (1.5 hours)

```bash
cat > src/services/progress_analytics.py <<'EOF'
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.db.models.mcq_attempt import MCQAttempt
from src.db.models.osce_attempt import OSCEAttempt
from src.db.models.study_card_review import StudyCardReview
from src.db.models.mcq import MCQ
from typing import List, Dict
from datetime import datetime, timedelta

class ProgressAnalytics:
    """Service for calculating user progress metrics"""

    @staticmethod
    def get_mcq_accuracy(db: Session, user_id: int) -> float:
        """Calculate overall MCQ accuracy rate"""
        total = db.query(MCQAttempt).filter(MCQAttempt.user_id == user_id).count()
        if total == 0:
            return 0.0

        correct = db.query(MCQAttempt).filter(
            MCQAttempt.user_id == user_id,
            MCQAttempt.is_correct == True
        ).count()

        return round((correct / total) * 100, 2)

    @staticmethod
    def get_specialty_breakdown(db: Session, user_id: int) -> List[Dict]:
        """Get performance breakdown by specialty"""
        results = db.query(
            MCQ.specialty,
            func.count(MCQAttempt.id).label("total_attempts"),
            func.sum(func.cast(MCQAttempt.is_correct, Integer)).label("correct_attempts"),
            func.avg(MCQAttempt.time_taken_seconds).label("avg_time")
        ).join(
            MCQ, MCQAttempt.mcq_id == MCQ.id
        ).filter(
            MCQAttempt.user_id == user_id
        ).group_by(
            MCQ.specialty
        ).all()

        breakdown = []
        for row in results:
            accuracy = (row.correct_attempts / row.total_attempts * 100) if row.total_attempts > 0 else 0.0
            breakdown.append({
                "specialty": row.specialty,
                "total_attempts": row.total_attempts,
                "correct_attempts": row.correct_attempts or 0,
                "accuracy_rate": round(accuracy, 2),
                "average_time_seconds": int(row.avg_time or 0)
            })

        return breakdown

    @staticmethod
    def get_weak_areas(db: Session, user_id: int, threshold: float = 70.0) -> List[str]:
        """Identify specialties with accuracy below threshold"""
        breakdown = ProgressAnalytics.get_specialty_breakdown(db, user_id)
        weak = [item["specialty"] for item in breakdown if item["accuracy_rate"] < threshold and item["total_attempts"] >= 5]
        return weak

    @staticmethod
    def get_study_card_retention(db: Session, user_id: int) -> float:
        """Calculate Study Card retention rate (quality >= 3)"""
        total = db.query(StudyCardReview).filter(
            StudyCardReview.user_id == user_id,
            StudyCardReview.quality.isnot(None)
        ).count()

        if total == 0:
            return 0.0

        successful = db.query(StudyCardReview).filter(
            StudyCardReview.user_id == user_id,
            StudyCardReview.quality >= 3
        ).count()

        return round((successful / total) * 100, 2)

    @staticmethod
    def get_weekly_trends(db: Session, user_id: int, weeks: int = 4) -> List[Dict]:
        """Calculate weekly trends for last N weeks"""
        trends = []
        today = datetime.utcnow()

        for i in range(weeks):
            week_start = today - timedelta(days=(i+1)*7)
            week_end = today - timedelta(days=i*7)

            mcq_count = db.query(MCQAttempt).filter(
                MCQAttempt.user_id == user_id,
                MCQAttempt.created_at >= week_start,
                MCQAttempt.created_at < week_end
            ).count()

            correct_count = db.query(MCQAttempt).filter(
                MCQAttempt.user_id == user_id,
                MCQAttempt.created_at >= week_start,
                MCQAttempt.created_at < week_end,
                MCQAttempt.is_correct == True
            ).count()

            accuracy = (correct_count / mcq_count * 100) if mcq_count > 0 else 0.0

            cards_reviewed = db.query(StudyCardReview).filter(
                StudyCardReview.user_id == user_id,
                StudyCardReview.last_review_date >= week_start,
                StudyCardReview.last_review_date < week_end
            ).count()

            trends.append({
                "week_start": week_start,
                "mcq_attempts": mcq_count,
                "accuracy_rate": round(accuracy, 2),
                "study_cards_reviewed": cards_reviewed
            })

        return list(reversed(trends))  # Oldest to newest
EOF

echo "✅ Progress analytics service created"
```

---

### Step 3: Create Progress Endpoints (1.5 hours)

```bash
cat > src/api/v1/progress/router.py <<'EOF'
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from src.db.session import get_db
from src.api.v1.schemas.progress import (
    DashboardResponse,
    SpecialtyPerformance,
    WeakArea,
    WeeklyTrend
)
from src.auth.dependencies import get_current_user
from src.db.models.user import User
from src.services.progress_analytics import ProgressAnalytics
from src.db.models.mcq_attempt import MCQAttempt
from src.db.models.osce_attempt import OSCEAttempt
from src.db.models.study_card_review import StudyCardReview
from typing import List
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter(prefix="/api/v1/progress", tags=["Progress"])
limiter = Limiter(key_func=get_remote_address)

@router.get("/dashboard", response_model=DashboardResponse)
@limiter.limit("60/minute")
async def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive dashboard with all progress metrics.

    Returns: MCQ accuracy, OSCE completions, Study Card stats, specialty breakdown
    """
    # MCQ stats
    total_mcq = db.query(MCQAttempt).filter(MCQAttempt.user_id == current_user.id).count()
    mcq_accuracy = ProgressAnalytics.get_mcq_accuracy(db, current_user.id)

    # OSCE stats
    total_osce = db.query(OSCEAttempt).filter(OSCEAttempt.user_id == current_user.id).count()

    # Study Card stats
    cards_reviewed = db.query(StudyCardReview).filter(StudyCardReview.user_id == current_user.id).count()
    card_retention = ProgressAnalytics.get_study_card_retention(db, current_user.id)

    # Specialty breakdown
    specialty_breakdown = ProgressAnalytics.get_specialty_breakdown(db, current_user.id)

    # Weak areas
    weak_areas = ProgressAnalytics.get_weak_areas(db, current_user.id)

    return DashboardResponse(
        total_mcq_attempts=total_mcq,
        mcq_accuracy_rate=mcq_accuracy,
        total_osce_completions=total_osce,
        study_cards_reviewed=cards_reviewed,
        study_card_retention_rate=card_retention,
        specialty_breakdown=specialty_breakdown,
        weak_areas=weak_areas
    )

@router.get("/specialty/{specialty_name}", response_model=SpecialtyPerformance)
@limiter.limit("60/minute")
async def get_specialty_performance(
    specialty_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed performance for a specific specialty"""
    breakdown = ProgressAnalytics.get_specialty_breakdown(db, current_user.id)

    specialty_data = next((item for item in breakdown if item["specialty"] == specialty_name), None)

    if not specialty_data:
        return SpecialtyPerformance(
            specialty=specialty_name,
            total_attempts=0,
            correct_attempts=0,
            accuracy_rate=0.0,
            average_time_seconds=0
        )

    return SpecialtyPerformance(**specialty_data)

@router.get("/weak-areas", response_model=List[WeakArea])
@limiter.limit("60/minute")
async def get_weak_areas(
    threshold: float = Query(70.0, ge=0.0, le=100.0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get specialties where user performance is below threshold.

    Default threshold: 70% accuracy
    """
    breakdown = ProgressAnalytics.get_specialty_breakdown(db, current_user.id)

    weak_areas = [
        WeakArea(
            specialty=item["specialty"],
            accuracy_rate=item["accuracy_rate"],
            total_attempts=item["total_attempts"],
            recommended_study_cards=max(10, int(50 - item["accuracy_rate"]))  # More study for lower accuracy
        )
        for item in breakdown
        if item["accuracy_rate"] < threshold and item["total_attempts"] >= 5
    ]

    return weak_areas

@router.get("/trends/weekly", response_model=List[WeeklyTrend])
@limiter.limit("60/minute")
async def get_weekly_trends(
    weeks: int = Query(4, ge=1, le=12),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get weekly progress trends for last N weeks"""
    trends = ProgressAnalytics.get_weekly_trends(db, current_user.id, weeks)
    return [WeeklyTrend(**trend) for trend in trends]
EOF

echo "✅ Progress endpoints created"
```

---

### Step 4: Register Router & Create Tests (1 hour)

```bash
# Register router
python <<'EOF'
import re
with open("src/main.py", "r") as f:
    content = f.read()
if "progress" not in content:
    content = re.sub(r"(from fastapi import FastAPI)", "\\1\nfrom src.api.v1.progress import router as progress_router\n", content)
    content = re.sub(r"(app = FastAPI\(\))", "\\1\n\napp.include_router(progress_router)\n", content)
    with open("src/main.py", "w") as f:
        f.write(content)
    print("✅ Progress router registered")
else:
    print("✅ Progress router already registered")
EOF

# Create tests
cat > tests/api/v1/test_progress.py <<'EOF'
import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.auth.security import create_access_token

client = TestClient(app)

@pytest.fixture
def auth_headers():
    token = create_access_token(data={"sub": "test_user@example.com"})
    return {"Authorization": f"Bearer {token}"}

def test_get_dashboard(auth_headers):
    """Test GET /api/v1/progress/dashboard"""
    response = client.get("/api/v1/progress/dashboard", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_mcq_attempts" in data
    assert "mcq_accuracy_rate" in data
    assert "specialty_breakdown" in data
    assert isinstance(data["specialty_breakdown"], list)

def test_get_specialty_performance(auth_headers):
    """Test GET /api/v1/progress/specialty/{name}"""
    response = client.get("/api/v1/progress/specialty/Cardiology", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "accuracy_rate" in data
    assert data["accuracy_rate"] >= 0.0
    assert data["accuracy_rate"] <= 100.0

def test_get_weak_areas(auth_headers):
    """Test GET /api/v1/progress/weak-areas"""
    response = client.get("/api/v1/progress/weak-areas", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_weekly_trends(auth_headers):
    """Test GET /api/v1/progress/trends/weekly"""
    response = client.get("/api/v1/progress/trends/weekly?weeks=4", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 4
EOF

pytest tests/api/v1/test_progress.py -v
```

---

## ✅ Validation Checklist

```bash
cd /home/dev/Development/irStudy/backend

[ -f src/api/v1/progress/router.py ] && echo "✅ Progress endpoints: EXISTS" || echo "❌ MISSING"
[ -f src/services/progress_analytics.py ] && echo "✅ Analytics service: EXISTS" || echo "❌ MISSING"
[ -f src/api/v1/schemas/progress.py ] && echo "✅ Schemas: EXISTS" || echo "❌ MISSING"
grep -q "progress_router" src/main.py && echo "✅ Router: REGISTERED" || echo "❌ NOT REGISTERED"
pytest tests/api/v1/test_progress.py -v && echo "✅ Tests: 100% PASS" || echo "❌ Tests: FAILED"
```

---

## 🎯 Success Criteria

1. ✅ Progress endpoints implemented: GET /dashboard, GET /specialty/{name}, GET /weak-areas, GET /trends/weekly
2. ✅ MCQ performance metrics calculated correctly (accuracy rate, average time)
3. ✅ OSCE completion tracking operational
4. ✅ Study Card statistics integrated
5. ✅ Weekly/monthly trends functional
6. ✅ Test suite: 100% pass rate

---

## 🔄 When Complete

```bash
cd /home/dev/Development/irStudy

sed -i 's/TASK_004.*TODO/TASK_004: ✅ DONE/' @fix_plan.md

git add .
git commit -m "feat(api): Complete TASK_004 User Progress Tracking - Analytics dashboard

- Progress endpoints: /dashboard, /specialty/{name}, /weak-areas, /trends/weekly
- MCQ performance metrics with accuracy calculation
- OSCE completion tracking
- Study Card retention statistics
- Weekly trends analysis
- Test suite: 100% pass rate

Deliverables:
- backend/src/api/v1/progress/router.py
- backend/src/services/progress_analytics.py
- backend/tests/api/v1/test_progress.py

Quality Gates: 6/6 passed ✅
Blocks: TASK_008 now unblocked

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

echo "✅ TASK_004 complete. Starting TASK_005..."
```

---

**Last Updated:** 2026-02-07
**Status:** 🟡 Not Started
**Depends On:** TASK_002, TASK_003
**Blocks:** TASK_008
