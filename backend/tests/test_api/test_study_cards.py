"""
Comprehensive test suite for Study Card endpoints (TASK_003)

Tests:
- GET /api/v1/study-cards/due-cards - Get cards due for review
- POST /api/v1/study-cards/review - Submit review with SM-2 algorithm
- GET /api/v1/study-cards/statistics - Get study statistics
- SM-2 algorithm correctness (quality 0, 3, 5)
- Ease factor clamping (1.3-2.5)
- Interval calculation
- Australian medical context validation
- Response time < 200ms

AUSTRALIAN MEDICAL CONTEXT:
- Tests validate Australian medical terminology
- Tests verify Australian citations (eTG, AMH, AHPRA)
- Tests ensure content aligns with AMC Clinical Exam preparation
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import time

from src.main import app
from src.db.base import Base, get_db
from src.db.models import (
    User,
    StudyCard,
    StudyCardReview,
    MedicalSpecialty,
    DifficultyLevel,
    UserRole,
)
from src.auth.security import hash_password
from src.services.sm2_algorithm import SM2Algorithm


# ============================================================================
# TEST DATABASE SETUP
# ============================================================================

# Use in-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for tests"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


# ============================================================================
# PYTEST FIXTURES
# ============================================================================


@pytest.fixture(scope="function")
def db_session():
    """Create fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(db_session):
    """Create test user"""
    user = User(
        email="test@example.com",
        password_hash=hash_password("testpass123"),
        full_name="Test User",
        role=UserRole.STUDENT,
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user):
    """Get authentication headers"""
    # Login to get access token
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "testpass123"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_study_cards(db_session, test_user):
    """Create sample study cards for testing"""
    cards = []

    # Card 1: Due today (cardiology)
    card1 = StudyCard(
        user_id=test_user.id,
        card_id="CARDI-CARD-0001",
        specialty=MedicalSpecialty.CARDIOLOGY,
        topic="ECG Interpretation",
        subtopic="STEMI patterns",
        question="What ECG changes indicate an acute anterior STEMI?",
        answer="ST elevation in leads V1-V4, reciprocal ST depression in inferior leads",
        explanation="Anterior STEMI is caused by LAD occlusion. Look for ST elevation ≥2mm in V1-V4.",
        citations=[
            {
                "title": "Australian Cardiovascular Guidelines",
                "author": "National Heart Foundation",
                "year": "2023",
                "source_type": "guideline"
            }
        ],
        difficulty=DifficultyLevel.MEDIUM,
        tags=["ecg", "stemi", "cardiology"],
        card_type="concept",
        next_review_date=datetime.utcnow() - timedelta(days=1),  # Due yesterday
        interval_days=1,
        ease_factor=2.5,
        repetitions=0,
        is_active=True,
    )
    cards.append(card1)

    # Card 2: Due today (respiratory)
    card2 = StudyCard(
        user_id=test_user.id,
        card_id="RESP-CARD-0001",
        specialty=MedicalSpecialty.RESPIRATORY,
        topic="Asthma Management",
        subtopic="First-line treatment",
        question="What is the first-line inhaled therapy for mild persistent asthma in Australia?",
        answer="Low-dose inhaled corticosteroid (ICS) - beclometasone or budesonide",
        explanation="Australian guidelines recommend regular ICS for mild persistent asthma. SABA alone is insufficient.",
        citations=[
            {
                "title": "Australian Asthma Handbook",
                "author": "National Asthma Council Australia",
                "year": "2024",
                "source_type": "guideline"
            }
        ],
        difficulty=DifficultyLevel.EASY,
        tags=["asthma", "respiratory", "pharmacology"],
        card_type="concept",
        next_review_date=datetime.utcnow(),  # Due today
        interval_days=1,
        ease_factor=2.5,
        repetitions=0,
        is_active=True,
    )
    cards.append(card2)

    # Card 3: Not due yet (reviewed yesterday, next review in 5 days)
    card3 = StudyCard(
        user_id=test_user.id,
        card_id="NEURO-CARD-0001",
        specialty=MedicalSpecialty.NEUROLOGY,
        topic="Stroke Management",
        subtopic="Thrombolysis criteria",
        question="What is the time window for IV thrombolysis in acute ischaemic stroke?",
        answer="Within 4.5 hours of symptom onset (or last known well)",
        explanation="Australian stroke guidelines follow international standards: tPA within 4.5 hours if no contraindications.",
        citations=[
            {
                "title": "Australian Stroke Guidelines",
                "author": "Stroke Foundation Australia",
                "year": "2023",
                "source_type": "guideline"
            }
        ],
        difficulty=DifficultyLevel.HARD,
        tags=["stroke", "neurology", "emergency"],
        card_type="clinical_pearl",
        next_review_date=datetime.utcnow() + timedelta(days=5),  # Not due yet
        interval_days=6,
        ease_factor=2.6,
        repetitions=2,
        is_active=True,
    )
    cards.append(card3)

    # Card 4: Inactive card (should not appear in due cards)
    card4 = StudyCard(
        user_id=test_user.id,
        card_id="PSYCH-CARD-0001",
        specialty=MedicalSpecialty.PSYCHIATRY,
        topic="Depression",
        subtopic="First-line treatment",
        question="What is the first-line pharmacological treatment for moderate depression?",
        answer="SSRI (e.g., sertraline, escitalopram)",
        explanation="Australian eTG recommends SSRIs as first-line antidepressants due to better tolerability.",
        citations=[
            {
                "title": "eTG Complete",
                "author": "Therapeutic Guidelines",
                "year": "2024",
                "source_type": "guideline"
            }
        ],
        difficulty=DifficultyLevel.MEDIUM,
        tags=["depression", "psychiatry", "pharmacology"],
        card_type="concept",
        next_review_date=datetime.utcnow(),  # Due today but inactive
        interval_days=1,
        ease_factor=2.5,
        repetitions=0,
        is_active=False,  # INACTIVE
    )
    cards.append(card4)

    db_session.add_all(cards)
    db_session.commit()

    for card in cards:
        db_session.refresh(card)

    return cards


# ============================================================================
# SM-2 ALGORITHM TESTS (Unit Tests)
# ============================================================================


def test_sm2_algorithm_quality_5_perfect():
    """Test SM-2 algorithm with quality 5 (perfect response)"""
    # First review, perfect response
    next_date, interval, ease_factor, reps = SM2Algorithm.calculate_next_review(
        quality=5,
        current_ease_factor=2.5,
        current_interval=1,
        repetitions=0
    )

    assert interval == 1  # First review always 1 day
    assert reps == 1  # Incremented
    assert ease_factor > 2.5  # Should increase
    assert ease_factor <= SM2Algorithm.MAX_EASE_FACTOR  # Clamped to max


def test_sm2_algorithm_quality_3_difficult():
    """Test SM-2 algorithm with quality 3 (correct but difficult)"""
    # Second review, correct but difficult
    next_date, interval, ease_factor, reps = SM2Algorithm.calculate_next_review(
        quality=3,
        current_ease_factor=2.5,
        current_interval=1,
        repetitions=1
    )

    assert interval == 6  # Second review is 6 days
    assert reps == 2  # Incremented
    assert ease_factor < 2.5  # Should decrease for quality 3


def test_sm2_algorithm_quality_0_blackout():
    """Test SM-2 algorithm with quality 0 (complete blackout)"""
    # Failed review - should reset
    next_date, interval, ease_factor, reps = SM2Algorithm.calculate_next_review(
        quality=0,
        current_ease_factor=2.6,
        current_interval=6,
        repetitions=2
    )

    assert interval == 1  # Reset to 1 day
    assert reps == 0  # Reset to 0
    assert ease_factor >= SM2Algorithm.MIN_EASE_FACTOR  # Should not go below min
    assert ease_factor < 2.6  # Should decrease


def test_sm2_algorithm_ease_factor_clamping():
    """Test that ease factor is clamped to 1.3-2.5 range"""
    # Very poor quality should clamp at MIN_EASE_FACTOR
    _, _, ease_factor, _ = SM2Algorithm.calculate_next_review(
        quality=0,
        current_ease_factor=1.4,
        current_interval=1,
        repetitions=0
    )
    assert ease_factor >= SM2Algorithm.MIN_EASE_FACTOR
    assert ease_factor <= SM2Algorithm.MAX_EASE_FACTOR

    # Perfect quality should clamp at MAX_EASE_FACTOR
    _, _, ease_factor, _ = SM2Algorithm.calculate_next_review(
        quality=5,
        current_ease_factor=2.4,
        current_interval=1,
        repetitions=0
    )
    assert ease_factor <= SM2Algorithm.MAX_EASE_FACTOR


def test_sm2_algorithm_third_review():
    """Test SM-2 algorithm for third+ review (interval = previous × EF)"""
    next_date, interval, ease_factor, reps = SM2Algorithm.calculate_next_review(
        quality=4,
        current_ease_factor=2.5,
        current_interval=6,
        repetitions=2
    )

    assert reps == 3  # Third review
    # Interval should be approximately 6 × ease_factor
    assert interval > 6  # Should be greater than previous interval
    assert interval <= 20  # Reasonable upper bound


def test_sm2_algorithm_validate_quality():
    """Test quality validation"""
    assert SM2Algorithm.validate_quality(0) is True
    assert SM2Algorithm.validate_quality(5) is True
    assert SM2Algorithm.validate_quality(3) is True
    assert SM2Algorithm.validate_quality(-1) is False
    assert SM2Algorithm.validate_quality(6) is False


def test_sm2_algorithm_quality_descriptions():
    """Test quality descriptions"""
    assert SM2Algorithm.get_quality_description(0) == "Complete blackout"
    assert SM2Algorithm.get_quality_description(5) == "Perfect response"
    assert SM2Algorithm.get_quality_description(3) == "Correct, but difficult"


# ============================================================================
# API ENDPOINT TESTS
# ============================================================================


def test_get_due_cards_success(db_session, auth_headers, sample_study_cards):
    """Test GET /study-cards/due-cards returns cards due today"""
    start_time = time.time()
    response = client.get("/api/v1/study-cards/due-cards", headers=auth_headers)
    elapsed_time = (time.time() - start_time) * 1000  # Convert to ms

    assert response.status_code == 200
    assert elapsed_time < 200  # Performance check

    data = response.json()
    assert "total_due" in data
    assert "cards" in data

    # Should have 2 due cards (card1 and card2)
    assert data["total_due"] == 2
    assert len(data["cards"]) == 2

    # Verify cards are ordered by next_review_date (oldest first)
    cards = data["cards"]
    assert cards[0]["card_id"] == "CARDI-CARD-0001"  # Due yesterday (oldest)
    assert cards[1]["card_id"] == "RESP-CARD-0001"  # Due today


def test_get_due_cards_with_specialty_filter(db_session, auth_headers, sample_study_cards):
    """Test GET /study-cards/due-cards with specialty filter"""
    response = client.get(
        "/api/v1/study-cards/due-cards?specialty=cardiology",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Should only return cardiology card
    assert data["total_due"] == 1
    assert len(data["cards"]) == 1
    assert data["cards"][0]["specialty"] == "cardiology"


def test_get_due_cards_with_difficulty_filter(db_session, auth_headers, sample_study_cards):
    """Test GET /study-cards/due-cards with difficulty filter"""
    response = client.get(
        "/api/v1/study-cards/due-cards?difficulty=easy",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Should only return easy cards
    assert data["total_due"] == 1
    assert data["cards"][0]["difficulty"] == "easy"


def test_get_due_cards_with_limit(db_session, auth_headers, sample_study_cards):
    """Test GET /study-cards/due-cards with limit parameter"""
    response = client.get(
        "/api/v1/study-cards/due-cards?limit=1",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    # Should return total_due=2 but only 1 card due to limit
    assert data["total_due"] == 2
    assert len(data["cards"]) == 1


def test_get_due_cards_unauthenticated():
    """Test GET /study-cards/due-cards requires authentication"""
    response = client.get("/api/v1/study-cards/due-cards")
    assert response.status_code == 401


def test_submit_review_quality_5(db_session, auth_headers, sample_study_cards):
    """Test POST /study-cards/review with quality 5 (perfect)"""
    card = sample_study_cards[0]  # CARDI-CARD-0001

    start_time = time.time()
    response = client.post(
        "/api/v1/study-cards/review",
        headers=auth_headers,
        json={
            "card_id": card.id,
            "quality": 5,
            "time_taken_seconds": 30
        }
    )
    elapsed_time = (time.time() - start_time) * 1000  # Convert to ms

    assert response.status_code == 200
    assert elapsed_time < 200  # Performance check

    data = response.json()

    # Verify response structure
    assert data["card_id"] == card.id
    assert data["quality"] == 5
    assert data["interval_days"] == 1  # First review
    assert data["repetitions"] == 1
    assert data["ease_factor"] > 2.5  # Should increase
    assert data["ease_factor"] <= SM2Algorithm.MAX_EASE_FACTOR
    assert "message" in data
    assert "quality_description" in data
    assert data["quality_description"] == "Perfect response"

    # Verify review was recorded in database
    db_session.expire_all()
    review = db_session.query(StudyCardReview).filter(
        StudyCardReview.card_id == card.id
    ).first()
    assert review is not None
    assert review.quality == 5
    assert review.time_taken_seconds == 30
    assert review.ease_factor_after > 2.5


def test_submit_review_quality_3(db_session, auth_headers, sample_study_cards):
    """Test POST /study-cards/review with quality 3 (correct but difficult)"""
    card = sample_study_cards[1]  # RESP-CARD-0001

    response = client.post(
        "/api/v1/study-cards/review",
        headers=auth_headers,
        json={
            "card_id": card.id,
            "quality": 3,
            "time_taken_seconds": 60
        }
    )

    assert response.status_code == 200
    data = response.json()

    assert data["quality"] == 3
    assert data["interval_days"] == 1  # First review
    assert data["repetitions"] == 1
    assert data["ease_factor"] < 2.5  # Should decrease for quality 3


def test_submit_review_quality_0_reset(db_session, auth_headers, sample_study_cards):
    """Test POST /study-cards/review with quality 0 (complete blackout) - should reset"""
    card = sample_study_cards[2]  # NEURO-CARD-0001 (already at rep 2)

    response = client.post(
        "/api/v1/study-cards/review",
        headers=auth_headers,
        json={
            "card_id": card.id,
            "quality": 0,
            "time_taken_seconds": 120
        }
    )

    assert response.status_code == 200
    data = response.json()

    # Failed review should reset
    assert data["quality"] == 0
    assert data["interval_days"] == 1  # Reset to 1 day
    assert data["repetitions"] == 0  # Reset to 0
    assert data["ease_factor"] >= SM2Algorithm.MIN_EASE_FACTOR
    assert "Keep practicing" in data["message"]


def test_submit_review_invalid_quality(db_session, auth_headers, sample_study_cards):
    """Test POST /study-cards/review with invalid quality rating"""
    card = sample_study_cards[0]

    # Quality too high
    response = client.post(
        "/api/v1/study-cards/review",
        headers=auth_headers,
        json={
            "card_id": card.id,
            "quality": 6,
            "time_taken_seconds": 30
        }
    )
    assert response.status_code == 422  # Validation error

    # Quality too low
    response = client.post(
        "/api/v1/study-cards/review",
        headers=auth_headers,
        json={
            "card_id": card.id,
            "quality": -1,
            "time_taken_seconds": 30
        }
    )
    assert response.status_code == 422  # Validation error


def test_submit_review_nonexistent_card(db_session, auth_headers):
    """Test POST /study-cards/review with non-existent card"""
    response = client.post(
        "/api/v1/study-cards/review",
        headers=auth_headers,
        json={
            "card_id": 99999,
            "quality": 5,
            "time_taken_seconds": 30
        }
    )
    assert response.status_code == 404


def test_submit_review_unauthenticated(db_session, sample_study_cards):
    """Test POST /study-cards/review requires authentication"""
    card = sample_study_cards[0]

    response = client.post(
        "/api/v1/study-cards/review",
        json={
            "card_id": card.id,
            "quality": 5,
            "time_taken_seconds": 30
        }
    )
    assert response.status_code == 401


def test_get_statistics_success(db_session, auth_headers, sample_study_cards, test_user):
    """Test GET /study-cards/statistics returns correct statistics"""
    # Submit some reviews first
    card1 = sample_study_cards[0]
    card2 = sample_study_cards[1]

    client.post(
        "/api/v1/study-cards/review",
        headers=auth_headers,
        json={"card_id": card1.id, "quality": 5, "time_taken_seconds": 30}
    )
    client.post(
        "/api/v1/study-cards/review",
        headers=auth_headers,
        json={"card_id": card2.id, "quality": 3, "time_taken_seconds": 45}
    )

    start_time = time.time()
    response = client.get("/api/v1/study-cards/statistics", headers=auth_headers)
    elapsed_time = (time.time() - start_time) * 1000  # Convert to ms

    assert response.status_code == 200
    assert elapsed_time < 200  # Performance check

    data = response.json()

    # Verify statistics structure
    assert "total_cards" in data
    assert "by_specialty" in data
    assert "by_difficulty" in data
    assert "cards_due_today" in data
    assert "cards_mastered" in data
    assert "average_ease_factor" in data
    assert "total_reviews" in data
    assert "reviews_today" in data
    assert "average_quality" in data
    assert "retention_rate" in data

    # Verify values
    assert data["total_cards"] == 3  # Active cards only (card4 is inactive)
    assert data["total_reviews"] == 2  # We submitted 2 reviews
    assert data["reviews_today"] == 2
    assert data["average_quality"] == 4.0  # (5 + 3) / 2
    assert data["retention_rate"] == 100.0  # Both reviews had quality >= 3


def test_get_statistics_no_reviews(db_session, auth_headers, sample_study_cards):
    """Test GET /study-cards/statistics with no reviews yet"""
    response = client.get("/api/v1/study-cards/statistics", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    assert data["total_cards"] == 3  # Active cards
    assert data["total_reviews"] == 0
    assert data["reviews_today"] == 0
    assert data["average_quality"] == 0.0
    assert data["retention_rate"] == 0.0


def test_get_statistics_unauthenticated():
    """Test GET /study-cards/statistics requires authentication"""
    response = client.get("/api/v1/study-cards/statistics")
    assert response.status_code == 401


def test_australian_medical_context_validation(db_session, auth_headers, sample_study_cards):
    """Test that study cards maintain Australian medical context"""
    response = client.get("/api/v1/study-cards/due-cards", headers=auth_headers)

    assert response.status_code == 200
    cards = response.json()["cards"]

    # Verify Australian citations
    for card in cards:
        assert len(card["citations"]) > 0
        # At least one citation should reference Australian sources
        citation_titles = [c["title"].lower() for c in card["citations"]]
        has_australian_citation = any(
            "australian" in title or "etg" in title or "ahpra" in title
            for title in citation_titles
        )
        assert has_australian_citation, f"Card {card['card_id']} missing Australian citation"


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================


def test_performance_get_due_cards(db_session, auth_headers, sample_study_cards):
    """Test GET /study-cards/due-cards response time < 200ms"""
    start_time = time.time()
    response = client.get("/api/v1/study-cards/due-cards", headers=auth_headers)
    elapsed_time = (time.time() - start_time) * 1000  # Convert to ms

    assert response.status_code == 200
    assert elapsed_time < 200, f"Response time {elapsed_time:.2f}ms exceeds 200ms target"


def test_performance_submit_review(db_session, auth_headers, sample_study_cards):
    """Test POST /study-cards/review response time < 200ms"""
    card = sample_study_cards[0]

    start_time = time.time()
    response = client.post(
        "/api/v1/study-cards/review",
        headers=auth_headers,
        json={"card_id": card.id, "quality": 5, "time_taken_seconds": 30}
    )
    elapsed_time = (time.time() - start_time) * 1000  # Convert to ms

    assert response.status_code == 200
    assert elapsed_time < 200, f"Response time {elapsed_time:.2f}ms exceeds 200ms target"


def test_performance_get_statistics(db_session, auth_headers, sample_study_cards):
    """Test GET /study-cards/statistics response time < 200ms"""
    start_time = time.time()
    response = client.get("/api/v1/study-cards/statistics", headers=auth_headers)
    elapsed_time = (time.time() - start_time) * 1000  # Convert to ms

    assert response.status_code == 200
    assert elapsed_time < 200, f"Response time {elapsed_time:.2f}ms exceeds 200ms target"
