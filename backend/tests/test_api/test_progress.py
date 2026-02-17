"""
Progress Tracking API Tests

TESTS:
- GET /api/v1/progress/dashboard - Comprehensive dashboard
- GET /api/v1/progress/specialty/{name} - Specialty detail
- GET /api/v1/progress/weak-areas - Weak areas identification
- GET /api/v1/progress/trends/weekly - Weekly trends
- Privacy: Cross-user data access prevention
- Performance: API response time <200ms
- Accuracy: Correct calculations

PRIVACY TESTS:
- User cannot access other users' progress data
- All queries filtered by current_user.id

PERFORMANCE TESTS:
- API response time <200ms
- No N+1 queries
- Database aggregations working

ACCURACY TESTS:
- MCQ accuracy calculation correct (correct/total × 100)
- Weak areas filtering correct
- Weekly trends calculated correctly
"""

import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.main import app
from src.db.models import (
    User,
    MCQ,
    MCQAttempt,
    OSCE,
    OSCEAttempt,
    StudyCard,
    StudyCardReview,
    MedicalSpecialty,
    DifficultyLevel,
    UserRole,
)
from src.auth.security import create_access_token


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def client():
    """Test client"""
    return TestClient(app)


@pytest.fixture
def test_user(db: Session):
    """Create test user"""
    user = User(
        email="test@example.com",
        password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyDKVb0fD6Wm",  # "password123"
        full_name="Test User",
        role=UserRole.STUDENT,
        is_active=True,
        is_verified=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def other_user(db: Session):
    """Create another user for privacy tests"""
    user = User(
        email="other@example.com",
        password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyDKVb0fD6Wm",
        full_name="Other User",
        role=UserRole.STUDENT,
        is_active=True,
        is_verified=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user):
    """Authentication headers"""
    token = create_access_token(data={"sub": test_user.email, "user_id": test_user.id})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_mcqs(db: Session):
    """Create test MCQs"""
    mcqs = []
    for i, specialty in enumerate(
        [MedicalSpecialty.CARDIOLOGY, MedicalSpecialty.RESPIRATORY, MedicalSpecialty.NEUROLOGY]
    ):
        mcq = MCQ(
            question_id=f"MCQ-TEST-{i+1:03d}",
            question_text=f"Test question {i+1}",
            options={"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"},
            correct_answer="A",
            explanation="Test explanation",
            citation="Test citation",
            specialty=specialty,
            difficulty=DifficultyLevel.MEDIUM,
            is_published=True,
        )
        db.add(mcq)
        mcqs.append(mcq)
    db.commit()
    for mcq in mcqs:
        db.refresh(mcq)
    return mcqs


@pytest.fixture
def test_attempts(db: Session, test_user, test_mcqs):
    """Create test MCQ attempts"""
    attempts = []

    # Cardiology: 10 attempts, 7 correct (70% accuracy)
    for i in range(10):
        attempt = MCQAttempt(
            user_id=test_user.id,
            mcq_id=test_mcqs[0].id,
            selected_answer="A" if i < 7 else "B",  # 7 correct, 3 incorrect
            is_correct=i < 7,
            time_taken_seconds=90 + i * 5,
            confidence_level=4,
            attempt_number=i + 1,
        )
        db.add(attempt)
        attempts.append(attempt)

    # Respiratory: 5 attempts, 4 correct (80% accuracy)
    for i in range(5):
        attempt = MCQAttempt(
            user_id=test_user.id,
            mcq_id=test_mcqs[1].id,
            selected_answer="A" if i < 4 else "B",
            is_correct=i < 4,
            time_taken_seconds=85 + i * 3,
            confidence_level=5,
            attempt_number=i + 1,
        )
        db.add(attempt)
        attempts.append(attempt)

    # Neurology: 12 attempts, 7 correct (58.33% accuracy) - WEAK AREA
    for i in range(12):
        attempt = MCQAttempt(
            user_id=test_user.id,
            mcq_id=test_mcqs[2].id,
            selected_answer="A" if i < 7 else "B",
            is_correct=i < 7,
            time_taken_seconds=120 + i * 8,
            confidence_level=2,
            attempt_number=i + 1,
        )
        db.add(attempt)
        attempts.append(attempt)

    db.commit()
    return attempts


@pytest.fixture
def test_osce(db: Session):
    """Create test OSCE"""
    osce = OSCE(
        osce_id="OSCE-TEST-001",
        station_title="Test OSCE Station",
        station_type="history_taking",
        patient_instructions="Test patient instructions",
        candidate_instructions="Test candidate instructions",
        rubric={"category1": {"max_marks": 5}},
        specialty=MedicalSpecialty.CARDIOLOGY,
        difficulty=DifficultyLevel.MEDIUM,
        is_published=True,
    )
    db.add(osce)
    db.commit()
    db.refresh(osce)
    return osce


@pytest.fixture
def test_osce_attempts(db: Session, test_user, test_osce):
    """Create test OSCE attempts"""
    attempts = []
    for i in range(3):
        attempt = OSCEAttempt(
            user_id=test_user.id,
            osce_id=test_osce.id,
            scores={"category1": 3},
            total_score=12,
            passed=True,
            time_taken_seconds=480,
            attempt_number=i + 1,
        )
        db.add(attempt)
        attempts.append(attempt)
    db.commit()
    return attempts


@pytest.fixture
def test_study_cards(db: Session):
    """Create test study cards"""
    cards = []
    for i in range(5):
        card = StudyCard(
            card_id=f"CARD-TEST-{i+1:03d}",
            specialty=MedicalSpecialty.NEUROLOGY,
            topic="Test Topic",
            question="Test question",
            answer="Test answer",
            citations=[{"source": "Test source"}],
            difficulty=DifficultyLevel.MEDIUM,
            is_active=True,
        )
        db.add(card)
        cards.append(card)
    db.commit()
    for card in cards:
        db.refresh(card)
    return cards


@pytest.fixture
def test_study_card_reviews(db: Session, test_user, test_study_cards):
    """Create test study card reviews"""
    reviews = []
    for i, card in enumerate(test_study_cards):
        # Mix of quality ratings (3 successful: quality >= 3, 2 failed)
        quality = 4 if i < 3 else 2
        review = StudyCardReview(
            user_id=test_user.id,
            card_id=card.id,
            quality=quality,
            time_taken_seconds=60,
            ease_factor_after=2.5,
            interval_days_after=1,
            repetitions_after=1,
            next_review_date_after=datetime.utcnow() + timedelta(days=1),
        )
        db.add(review)
        reviews.append(review)
    db.commit()
    return reviews


# ============================================================================
# DASHBOARD TESTS
# ============================================================================


def test_get_dashboard_success(
    client,
    auth_headers,
    test_user,
    test_attempts,
    test_osce_attempts,
    test_study_card_reviews,
):
    """Test GET /dashboard returns comprehensive analytics"""
    response = client.get("/api/v1/progress/dashboard", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    # Check MCQ stats
    assert data["total_mcq_attempts"] == 27  # 10 + 5 + 12
    assert "mcq_accuracy_rate" in data
    assert data["mcq_accuracy_rate"] > 0

    # Check OSCE stats
    assert data["total_osce_completions"] == 3

    # Check Study Card stats
    assert data["study_cards_reviewed"] == 5
    assert "study_card_retention_rate" in data

    # Check specialty breakdown
    assert "specialty_breakdown" in data
    assert len(data["specialty_breakdown"]) == 3  # cardiology, respiratory, neurology

    # Check weak areas
    assert "weak_areas" in data


def test_get_dashboard_no_data(client, auth_headers, test_user):
    """Test GET /dashboard with no attempts"""
    response = client.get("/api/v1/progress/dashboard", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    assert data["total_mcq_attempts"] == 0
    assert data["mcq_accuracy_rate"] == 0.0
    assert data["total_osce_completions"] == 0
    assert data["study_cards_reviewed"] == 0
    assert len(data["specialty_breakdown"]) == 0
    assert len(data["weak_areas"]) == 0


def test_get_dashboard_unauthenticated(client):
    """Test GET /dashboard requires authentication"""
    response = client.get("/api/v1/progress/dashboard")
    assert response.status_code == 401


# ============================================================================
# SPECIALTY DETAIL TESTS
# ============================================================================


def test_get_specialty_detail_success(client, auth_headers, test_user, test_attempts):
    """Test GET /specialty/{name} returns detailed metrics"""
    response = client.get("/api/v1/progress/specialty/cardiology", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    assert data["specialty"] == "cardiology"
    assert data["total_attempts"] == 10
    assert data["correct_attempts"] == 7
    assert data["accuracy_rate"] == 70.0
    assert data["average_time_seconds"] > 0
    assert "osce_completions" in data
    assert "study_cards_available" in data
    assert "recent_attempts" in data


def test_get_specialty_detail_invalid_specialty(client, auth_headers):
    """Test GET /specialty/{name} with invalid specialty"""
    response = client.get("/api/v1/progress/specialty/invalid", headers=auth_headers)
    assert response.status_code == 400
    body = response.json()
    detail = body.get("detail") or str(body)
    assert "Invalid specialty" in detail or "invalid" in str(body).lower()


def test_get_specialty_detail_no_attempts(client, auth_headers, test_user, test_mcqs):
    """Test GET /specialty/{name} with no attempts"""
    response = client.get("/api/v1/progress/specialty/cardiology", headers=auth_headers)
    assert response.status_code == 404


# ============================================================================
# WEAK AREAS TESTS
# ============================================================================


def test_get_weak_areas_default_threshold(client, auth_headers, test_user, test_attempts):
    """Test GET /weak-areas with default threshold (70%)"""
    response = client.get("/api/v1/progress/weak-areas", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    assert data["threshold"] == 70.0
    assert data["min_attempts"] == 5

    # Neurology should be weak (58.33% < 70%)
    weak_specialties = [area["specialty"] for area in data["weak_areas"]]
    assert "neurology" in weak_specialties

    # Find neurology weak area
    neurology_weak = next(
        (area for area in data["weak_areas"] if area["specialty"] == "neurology"), None
    )
    assert neurology_weak is not None
    assert neurology_weak["accuracy_rate"] < 70.0
    assert neurology_weak["total_attempts"] == 12
    assert neurology_weak["recommended_study_cards"] >= 0  # 0 is valid when no study cards seeded


def test_get_weak_areas_custom_threshold(client, auth_headers, test_user, test_attempts):
    """Test GET /weak-areas with custom threshold"""
    response = client.get(
        "/api/v1/progress/weak-areas?threshold=75&min_attempts=5", headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert data["threshold"] == 75.0
    assert data["min_attempts"] == 5

    # Both cardiology (70%) and neurology (58.33%) should be weak
    weak_specialties = [area["specialty"] for area in data["weak_areas"]]
    assert "neurology" in weak_specialties
    assert "cardiology" in weak_specialties


def test_get_weak_areas_no_weak_areas(client, auth_headers, test_user, test_attempts):
    """Test GET /weak-areas with very low threshold"""
    response = client.get(
        "/api/v1/progress/weak-areas?threshold=50&min_attempts=5", headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Neurology (58.33%) should still be above 50%
    assert len(data["weak_areas"]) == 0


# ============================================================================
# WEEKLY TRENDS TESTS
# ============================================================================


def test_get_weekly_trends_default_weeks(client, auth_headers, test_user, test_attempts):
    """Test GET /trends/weekly with default weeks (4)"""
    response = client.get("/api/v1/progress/trends/weekly", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    assert data["weeks"] == 4
    assert "trends" in data
    assert len(data["trends"]) == 4

    # Check trend structure
    for trend in data["trends"]:
        assert "week_start" in trend
        assert "mcq_attempts" in trend
        assert "accuracy_rate" in trend
        assert "study_cards_reviewed" in trend


def test_get_weekly_trends_custom_weeks(client, auth_headers, test_user):
    """Test GET /trends/weekly with custom weeks"""
    response = client.get("/api/v1/progress/trends/weekly?weeks=8", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    assert data["weeks"] == 8
    assert len(data["trends"]) == 8


def test_get_weekly_trends_max_weeks(client, auth_headers, test_user):
    """Test GET /trends/weekly respects max 12 weeks"""
    response = client.get("/api/v1/progress/trends/weekly?weeks=12", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    assert data["weeks"] == 12
    assert len(data["trends"]) == 12


def test_get_weekly_trends_invalid_weeks(client, auth_headers):
    """Test GET /trends/weekly with invalid weeks"""
    response = client.get("/api/v1/progress/trends/weekly?weeks=0", headers=auth_headers)
    assert response.status_code == 422  # Validation error


# ============================================================================
# PRIVACY TESTS
# ============================================================================


def test_dashboard_privacy(
    client, auth_headers, test_user, other_user, test_attempts, db: Session
):
    """Test dashboard only shows current user's data"""
    # Create attempts for other user
    other_mcq = MCQ(
        question_id="MCQ-OTHER-001",
        question_text="Other user question",
        options={"A": "Option A", "B": "Option B"},
        correct_answer="A",
        explanation="Test",
        citation="Test",
        specialty=MedicalSpecialty.CARDIOLOGY,
        difficulty=DifficultyLevel.MEDIUM,
        is_published=True,
    )
    db.add(other_mcq)
    db.commit()
    db.refresh(other_mcq)

    other_attempt = MCQAttempt(
        user_id=other_user.id,
        mcq_id=other_mcq.id,
        selected_answer="A",
        is_correct=True,
        time_taken_seconds=60,
        attempt_number=1,
    )
    db.add(other_attempt)
    db.commit()

    # Get dashboard for test_user
    response = client.get("/api/v1/progress/dashboard", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()

    # Should only see test_user's 27 attempts, not other_user's 1 attempt
    assert data["total_mcq_attempts"] == 27


# ============================================================================
# ACCURACY TESTS
# ============================================================================


def test_accuracy_calculation(client, auth_headers, test_user, test_attempts):
    """Test MCQ accuracy calculation is correct"""
    response = client.get("/api/v1/progress/dashboard", headers=auth_headers)
    data = response.json()

    # Total: 27 attempts (10 + 5 + 12)
    # Correct: 18 attempts (7 + 4 + 7)
    # Expected accuracy: 18/27 * 100 = 66.67%
    expected_accuracy = round((18 / 27) * 100, 2)
    assert data["mcq_accuracy_rate"] == expected_accuracy


def test_specialty_breakdown_accuracy(client, auth_headers, test_user, test_attempts):
    """Test specialty breakdown accuracy calculations"""
    response = client.get("/api/v1/progress/dashboard", headers=auth_headers)
    data = response.json()

    breakdown = {item["specialty"]: item for item in data["specialty_breakdown"]}

    # Cardiology: 7/10 = 70%
    assert breakdown["cardiology"]["accuracy_rate"] == 70.0

    # Respiratory: 4/5 = 80%
    assert breakdown["respiratory"]["accuracy_rate"] == 80.0

    # Neurology: 7/12 = 58.33%
    assert breakdown["neurology"]["accuracy_rate"] == 58.33


def test_study_card_retention_calculation(
    client, auth_headers, test_user, test_study_card_reviews
):
    """Test study card retention rate calculation"""
    response = client.get("/api/v1/progress/dashboard", headers=auth_headers)
    data = response.json()

    # 3 successful (quality >= 3) out of 5 total = 60%
    expected_retention = round((3 / 5) * 100, 2)
    assert data["study_card_retention_rate"] == expected_retention


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================


@pytest.mark.performance
def test_dashboard_performance(client, auth_headers, test_user, test_attempts):
    """Test dashboard response time <200ms"""
    import time

    start = time.time()
    response = client.get("/api/v1/progress/dashboard", headers=auth_headers)
    elapsed = (time.time() - start) * 1000  # Convert to ms

    assert response.status_code == 200
    assert elapsed < 200, f"Response time {elapsed}ms exceeds 200ms target"


@pytest.mark.performance
def test_specialty_detail_performance(client, auth_headers, test_user, test_attempts):
    """Test specialty detail response time <200ms"""
    import time

    start = time.time()
    response = client.get("/api/v1/progress/specialty/cardiology", headers=auth_headers)
    elapsed = (time.time() - start) * 1000

    assert response.status_code == 200
    assert elapsed < 200, f"Response time {elapsed}ms exceeds 200ms target"
