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
from datetime import datetime, timedelta
import time

from src.db.models import (
    StudyCard,
    StudyCardReview,
    MedicalSpecialty,
    DifficultyLevel,
)
from src.services.sm2_algorithm import SM2Algorithm


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
# PYTEST FIXTURES (use global conftest fixtures)
# ============================================================================


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
# API ENDPOINT TESTS
# ============================================================================


def test_get_due_cards_success(client, auth_headers, sample_study_cards):
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


def test_get_due_cards_with_specialty_filter(client, auth_headers, sample_study_cards):
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


def test_get_due_cards_with_difficulty_filter(client, auth_headers, sample_study_cards):
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


def test_get_due_cards_with_limit(client, auth_headers, sample_study_cards):
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


def test_get_due_cards_unauthenticated(client):
    """Test GET /study-cards/due-cards requires authentication"""
    response = client.get("/api/v1/study-cards/due-cards")
    assert response.status_code == 401


def test_submit_review_quality_5(client, auth_headers, sample_study_cards):
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


def test_submit_review_quality_3(client, auth_headers, sample_study_cards, db_session):
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


def test_submit_review_quality_0_reset(client, auth_headers, sample_study_cards):
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


def test_submit_review_invalid_quality(client, auth_headers, sample_study_cards):
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


def test_submit_review_nonexistent_card(client, auth_headers):
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


def test_submit_review_unauthenticated(client, sample_study_cards):
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


def test_get_statistics_success(client, auth_headers, sample_study_cards):
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


def test_get_statistics_no_reviews(client, auth_headers, sample_study_cards):
    """Test GET /study-cards/statistics with no reviews yet"""
    response = client.get("/api/v1/study-cards/statistics", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    assert data["total_cards"] == 3  # Active cards
    assert data["total_reviews"] == 0
    assert data["reviews_today"] == 0
    assert data["average_quality"] == 0.0
    assert data["retention_rate"] == 0.0


def test_get_statistics_unauthenticated(client):
    """Test GET /study-cards/statistics requires authentication"""
    response = client.get("/api/v1/study-cards/statistics")
    assert response.status_code == 401


def test_australian_medical_context_validation(client, auth_headers, sample_study_cards):
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


def test_performance_get_due_cards(client, auth_headers, sample_study_cards):
    """Test GET /study-cards/due-cards response time < 200ms"""
    start_time = time.time()
    response = client.get("/api/v1/study-cards/due-cards", headers=auth_headers)
    elapsed_time = (time.time() - start_time) * 1000  # Convert to ms

    assert response.status_code == 200
    assert elapsed_time < 200, f"Response time {elapsed_time:.2f}ms exceeds 200ms target"


def test_performance_submit_review(client, auth_headers, sample_study_cards):
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


def test_performance_get_statistics(client, auth_headers, sample_study_cards):
    """Test GET /study-cards/statistics response time < 200ms"""
    start_time = time.time()
    response = client.get("/api/v1/study-cards/statistics", headers=auth_headers)
    elapsed_time = (time.time() - start_time) * 1000  # Convert to ms

    assert response.status_code == 200
    assert elapsed_time < 200, f"Response time {elapsed_time:.2f}ms exceeds 200ms target"


# ============================================================================
# GENERATE FROM OSCE SESSION TESTS (PRD-P1-005 Phase 4)
# ============================================================================


@pytest.fixture
def sample_osce_session(db_session, test_user):
    """Create sample OSCE session with feedback for testing"""
    from src.db.models import OSCEAttemptAI, PatientPersona
    from uuid import uuid4

    # First, create a PatientPersona
    persona_id = str(uuid4())
    persona = PatientPersona(
        persona_id=persona_id,
        persona_code="CARD-001",
        name="John Smith",
        age=52,
        gender="Male",
        specialty="cardiology",
        chief_complaint="Chest pain",
        opening_statement="I've been having chest pain for the last hour",
        symptoms={
            "layer_1": [{"symptom": "chest pain", "severity": "severe"}]
        },
        medical_history={"conditions": []},
        emotional_profile={"baseline": "anxious"},
        rag_query_hints=["chest pain", "MI"],
        key_differentials=["Acute coronary syndrome"],
        difficulty_level="intermediate",
        amc_blueprint_area="Cardiology"
    )
    db_session.add(persona)
    db_session.commit()

    # Now create OSCE session referencing the persona
    session_id = str(uuid4())
    osce_session = OSCEAttemptAI(
        attempt_id=session_id,
        user_id=str(test_user.id),  # Convert to string
        persona_id=persona_id,
        session_type="individual",
        conversation_history=[],
        emotional_state_transitions=[],
        student_actions=[],
        was_completed=True,
        session_state="complete"
    )

    db_session.add(osce_session)
    db_session.commit()
    db_session.refresh(osce_session)

    # Add ai_feedback as dynamic attribute (not a DB column in new schema)
    osce_session.ai_feedback = {
        "overall_score": 75,
        "feedback_text": (
            "Good history taking. You used SOCRATES framework effectively for chest pain assessment. "
            "Red flags were identified appropriately (sudden onset, radiation to jaw). "
            "Consider asking about risk factors more systematically."
        ),
        "strengths": [
            "Used SOCRATES framework for pain assessment",
            "Identified cardiac red flags (radiation, diaphoresis)",
        ],
        "areas_for_improvement": [
            "Could explore cardiovascular risk factors more thoroughly",
        ],
    }

    return osce_session


def test_generate_cards_from_osce_session_success(
    client, auth_headers, sample_osce_session, monkeypatch
):
    """Test POST /study-cards/generate-from-osce - Happy path (201 Created)"""
    from src.ai.study_card_generator import StudyCardGenerator
    from src.db.models import StudyCard

    # Mock the generator to avoid actual Claude API calls in tests
    async def mock_generate_cards(self, session_id, user_id, db):
        """Mock implementation that creates study cards without API calls"""
        # Create 3 sample study cards
        cards = [
            StudyCard(
                user_id=user_id,
                session_id=session_id,
                card_id=f"CARD-TEST-{i:04d}",
                specialty="cardiology",
                topic="History Taking",
                subtopic="SOCRATES Framework",
                question=f"Test question {i}",
                answer=f"Test answer {i}",
                explanation="Test explanation",
                citations=[{"title": "eTG - Chest Pain", "confidence": 0.85}],
                difficulty="medium",
                tags=["history-taking", "socrates"],
                card_type="concept",
                ease_factor=2.5,
                interval_days=1,
                repetitions=0,
                next_review_date=datetime.utcnow(),
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            for i in range(1, 4)
        ]

        # Save to database
        for card in cards:
            db.add(card)
        db.commit()

        for card in cards:
            db.refresh(card)

        return cards

    # Apply mock
    monkeypatch.setattr(
        StudyCardGenerator,
        "generate_cards_from_session",
        mock_generate_cards
    )

    # Act: Call API endpoint
    response = client.post(
        "/api/v1/study-cards/generate-from-osce",
        headers=auth_headers,
        json={"session_id": sample_osce_session.attempt_id},
    )

    # Assert: Verify response
    assert response.status_code == 201
    data = response.json()

    assert data["count"] == 3
    assert data["session_id"] == sample_osce_session.attempt_id
    assert "successfully" in data["message"].lower()
    assert len(data["cards"]) == 3

    # Verify SM-2 initialization
    for card in data["cards"]:
        assert card["ease_factor"] == 2.5
        assert card["interval_days"] == 1
        assert card["repetitions"] == 0
        assert "next_review_date" in card


def test_generate_cards_idempotency_returns_409(
    client, auth_headers, sample_osce_session, monkeypatch
):
    """Test idempotency: calling generate twice returns 409 Conflict on second call"""
    from src.ai.study_card_generator import StudyCardGenerator
    from src.db.models import StudyCard

    # Mock generator (same as above)
    async def mock_generate_cards(self, session_id, user_id, db):
        cards = [
            StudyCard(
                user_id=user_id,
                session_id=session_id,
                card_id=f"CARD-TEST-{i:04d}",
                specialty="cardiology",
                topic="Test",
                question=f"Q{i}",
                answer=f"A{i}",
                citations=[{"title": "Test"}],
                difficulty="medium",
                ease_factor=2.5,
                interval_days=1,
                repetitions=0,
                next_review_date=datetime.utcnow(),
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            for i in range(3)
        ]
        for card in cards:
            db.add(card)
        db.commit()
        return cards

    monkeypatch.setattr(
        StudyCardGenerator,
        "generate_cards_from_session",
        mock_generate_cards
    )

    # Act: Call API twice
    response1 = client.post(
        "/api/v1/study-cards/generate-from-osce",
        headers=auth_headers,
        json={"session_id": sample_osce_session.attempt_id},
    )
    response2 = client.post(
        "/api/v1/study-cards/generate-from-osce",
        headers=auth_headers,
        json={"session_id": sample_osce_session.attempt_id},
    )

    # Assert: First call succeeds, second returns 409
    assert response1.status_code == 201
    assert response2.status_code == 409

    data2 = response2.json()
    assert "already exist" in data2["detail"]["message"]
    assert data2["detail"]["existing_count"] == 3


def test_generate_cards_requires_authentication(client, sample_osce_session):
    """Test POST /study-cards/generate-from-osce requires JWT authentication"""
    # Act: Call without authentication
    response = client.post(
        "/api/v1/study-cards/generate-from-osce",
        json={"session_id": sample_osce_session.attempt_id},
    )

    # Assert: Returns 401 Unauthorized
    assert response.status_code == 401


def test_generate_cards_session_not_found(client, auth_headers, monkeypatch):
    """Test POST /study-cards/generate-from-osce with non-existent session returns 404"""
    from src.ai.study_card_generator import StudyCardGenerator
    from uuid import uuid4

    # Mock generator to raise ValueError for session not found
    async def mock_generate_cards(self, session_id, user_id, db):
        raise ValueError(f"OSCE session {session_id} does not exist")

    monkeypatch.setattr(
        StudyCardGenerator,
        "generate_cards_from_session",
        mock_generate_cards
    )

    fake_session_id = str(uuid4())

    # Act
    response = client.post(
        "/api/v1/study-cards/generate-from-osce",
        headers=auth_headers,
        json={"session_id": fake_session_id},
    )

    # Assert: Returns 404
    assert response.status_code == 404
    assert "does not exist" in response.json()["detail"]


def test_generate_cards_requires_session_ownership(
    client, auth_headers, sample_osce_session, monkeypatch
):
    """Test POST /study-cards/generate-from-osce validates user owns the session (403)"""
    from src.ai.study_card_generator import StudyCardGenerator

    # Mock generator to raise ValueError for ownership issue
    async def mock_generate_cards(self, session_id, user_id, db):
        raise ValueError(f"User {user_id} does not own session {session_id}")

    monkeypatch.setattr(
        StudyCardGenerator,
        "generate_cards_from_session",
        mock_generate_cards
    )

    # Act
    response = client.post(
        "/api/v1/study-cards/generate-from-osce",
        headers=auth_headers,
        json={"session_id": sample_osce_session.attempt_id},
    )

    # Assert: Returns 403 Forbidden
    assert response.status_code == 403
    assert "does not own" in response.json()["detail"]


def test_generate_cards_invalid_uuid_format(client, auth_headers):
    """Test POST /study-cards/generate-from-osce with malformed UUID returns 422"""
    # Act: Send invalid UUID format
    response = client.post(
        "/api/v1/study-cards/generate-from-osce",
        headers=auth_headers,
        json={"session_id": "not-a-valid-uuid"},
    )

    # Assert: Returns 422 Unprocessable Entity
    assert response.status_code == 422
    # Pydantic validation error for invalid UUID format


def test_generate_cards_internal_error_returns_500(
    client, auth_headers, sample_osce_session, monkeypatch
):
    """Test POST /study-cards/generate-from-osce handles unexpected errors (500)"""
    from src.ai.study_card_generator import StudyCardGenerator

    # Mock generator to raise unexpected exception
    async def mock_generate_cards(self, session_id, user_id, db):
        raise RuntimeError("Unexpected database error")

    monkeypatch.setattr(
        StudyCardGenerator,
        "generate_cards_from_session",
        mock_generate_cards
    )

    # Act
    response = client.post(
        "/api/v1/study-cards/generate-from-osce",
        headers=auth_headers,
        json={"session_id": sample_osce_session.attempt_id},
    )

    # Assert: Returns 500 with generic error message
    assert response.status_code == 500
    assert "unexpected error" in response.json()["detail"].lower()
    # Should NOT expose internal error details (security)
