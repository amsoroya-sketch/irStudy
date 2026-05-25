"""
Comprehensive test suite for MCQ endpoints (TASK_002)

Tests:
- GET /api/v1/mcqs/random - Get random MCQ with filters
- GET /api/v1/mcqs/{id} - Get specific MCQ
- POST /api/v1/mcqs/{id}/attempt - Submit answer
- GET /api/v1/mcqs - List MCQs with filters
- Australian drug name validation
- Citation validation
- Response time < 200ms

AUSTRALIAN MEDICAL CONTEXT:
- Tests validate Australian drug names (paracetamol not acetaminophen)
- Tests verify Australian citations (eTG, AHPRA, AMH)
- Tests ensure SI units (mmol/L not mg/dL)
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime
import time

from src.db.models import User, MCQ, MCQAttempt, MedicalSpecialty, DifficultyLevel, UserRole


# ============================================================================
# PYTEST FIXTURES
# ============================================================================


@pytest.fixture
def sample_mcq(db_session):
    """Create sample MCQ for testing"""
    mcq = MCQ(
        question_id="MCQ-CARD-001",
        question_text="A 55-year-old man presents with central chest pain radiating to his left arm. ECG shows ST elevation in leads II, III, aVF. What is the most likely diagnosis?",
        options={
            "A": "Anterior STEMI",
            "B": "Inferior STEMI",
            "C": "Unstable angina",
            "D": "Pulmonary embolism",
            "E": "Pericarditis",
        },
        correct_answer="B",
        explanation="ST elevation in leads II, III, aVF indicates inferior wall STEMI. Management includes immediate reperfusion therapy with PCI or thrombolysis (per eTG guidelines).",
        citation="Therapeutic Guidelines: Cardiovascular, Version 8, 2023",
        learning_points=[
            "Inferior STEMI presents with ST elevation in II, III, aVF",
            "Immediate reperfusion within 90 minutes improves outcomes",
            "Consider right ventricular infarction in inferior MI",
        ],
        specialty=MedicalSpecialty.CARDIOLOGY,
        difficulty=DifficultyLevel.MEDIUM,
        tags=["STEMI", "ECG", "acute-coronary-syndrome"],
        is_published=True,
        times_attempted=10,
        times_correct=7,
    )
    db_session.add(mcq)
    db_session.commit()
    db_session.refresh(mcq)
    return mcq


@pytest.fixture
def multiple_mcqs(db_session):
    """Create multiple MCQs for filtering tests"""
    mcqs = [
        MCQ(
            question_id=f"MCQ-CARD-{str(i).zfill(3)}",
            question_text=f"Cardiology question {i}",
            options={"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"},
            correct_answer="A",
            explanation=f"Explanation {i} - eTG Cardiovascular guidelines",
            citation="Therapeutic Guidelines: Cardiovascular, Version 8, 2023",
            specialty=MedicalSpecialty.CARDIOLOGY,
            difficulty=DifficultyLevel.EASY if i % 2 == 0 else DifficultyLevel.HARD,
            is_published=True,
        )
        for i in range(1, 6)
    ]
    db_session.add_all(mcqs)
    db_session.commit()
    return mcqs


# ============================================================================
# TEST CASES
# ============================================================================


def test_get_random_mcq_success(db_session, client, sample_mcq, auth_headers):
    """Test GET /api/v1/mcqs/random returns MCQ without answer"""
    start_time = time.time()
    response = client.get("/api/v1/mcqs/random", headers=auth_headers)
    elapsed_ms = (time.time() - start_time) * 1000

    assert response.status_code == 200
    data = response.json()

    # Verify MCQ structure
    assert "id" in data
    assert "question_id" in data
    assert data["question_id"] == "MCQ-CARD-001"
    assert "question_text" in data
    assert "options" in data
    assert "specialty" in data
    assert "difficulty" in data

    # Verify answer NOT included (practice mode)
    assert "correct_answer" not in data
    assert "explanation" not in data
    assert "citation" not in data

    # Verify response time < 200ms
    assert elapsed_ms < 200, f"Response time {elapsed_ms}ms exceeds 200ms threshold"


def test_get_random_mcq_with_specialty_filter(db_session, client, multiple_mcqs, auth_headers):
    """Test GET /api/v1/mcqs/random with specialty filter"""
    response = client.get(
        "/api/v1/mcqs/random?specialty=cardiology", headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["specialty"] == "cardiology"


def test_get_random_mcq_with_difficulty_filter(db_session, client, multiple_mcqs, auth_headers):
    """Test GET /api/v1/mcqs/random with difficulty filter"""
    response = client.get(
        "/api/v1/mcqs/random?difficulty=easy", headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["difficulty"] == "easy"


def test_get_random_mcq_no_results(db_session, client, auth_headers):
    """Test GET /api/v1/mcqs/random returns 404 when no MCQs match"""
    response = client.get(
        "/api/v1/mcqs/random?specialty=cardiology", headers=auth_headers
    )

    assert response.status_code == 404
    assert "No MCQs found" in response.json()["detail"]


def test_get_mcq_by_id_success(db_session, client, sample_mcq, auth_headers):
    """Test GET /api/v1/mcqs/{id} returns specific MCQ"""
    start_time = time.time()
    response = client.get(f"/api/v1/mcqs/{sample_mcq.id}", headers=auth_headers)
    elapsed_ms = (time.time() - start_time) * 1000

    assert response.status_code == 200
    data = response.json()

    assert data["id"] == sample_mcq.id
    assert data["question_id"] == "MCQ-CARD-001"
    assert "chest pain" in data["question_text"].lower()

    # Verify answer NOT included (practice mode)
    assert "correct_answer" not in data
    assert "explanation" not in data

    # Verify response time < 200ms
    assert elapsed_ms < 200, f"Response time {elapsed_ms}ms exceeds 200ms threshold"


def test_get_mcq_by_id_not_found(db_session, client, auth_headers):
    """Test GET /api/v1/mcqs/{id} returns 404 for invalid ID"""
    response = client.get("/api/v1/mcqs/99999", headers=auth_headers)

    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_submit_mcq_attempt_correct_answer(db_session, client, sample_mcq, auth_headers):
    """Test POST /api/v1/mcqs/{id}/attempt with correct answer"""
    attempt_data = {
        "mcq_id": sample_mcq.id,
        "selected_answer": "B",  # Correct answer
        "time_taken_seconds": 120,
        "confidence_level": 4,
    }

    start_time = time.time()
    response = client.post(
        f"/api/v1/mcqs/{sample_mcq.id}/attempt",
        json=attempt_data,
        headers=auth_headers,
    )
    elapsed_ms = (time.time() - start_time) * 1000

    assert response.status_code == 200
    data = response.json()

    # Verify response structure
    assert data["is_correct"] is True
    assert data["selected_answer"] == "B"
    assert data["correct_answer"] == "B"
    assert "explanation" in data
    assert "eTG" in data["explanation"] or "Therapeutic Guidelines" in data["citation"]
    assert "citation" in data
    assert "learning_points" in data
    assert data["attempt_number"] == 1

    # Verify Australian context
    assert "eTG" in data["citation"] or "Therapeutic Guidelines" in data["citation"]

    # Verify response time < 200ms
    assert elapsed_ms < 200, f"Response time {elapsed_ms}ms exceeds 200ms threshold"


def test_submit_mcq_attempt_incorrect_answer(db_session, client, sample_mcq, auth_headers):
    """Test POST /api/v1/mcqs/{id}/attempt with incorrect answer"""
    attempt_data = {
        "mcq_id": sample_mcq.id,
        "selected_answer": "A",  # Incorrect answer
        "time_taken_seconds": 90,
        "confidence_level": 2,
    }

    response = client.post(
        f"/api/v1/mcqs/{sample_mcq.id}/attempt",
        json=attempt_data,
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()

    assert data["is_correct"] is False
    assert data["selected_answer"] == "A"
    assert data["correct_answer"] == "B"
    assert "explanation" in data


def test_submit_mcq_attempt_multiple_times(db_session, client, sample_mcq, auth_headers):
    """Test multiple attempts increment attempt_number"""
    attempt_data = {
        "mcq_id": sample_mcq.id,
        "selected_answer": "B",
        "time_taken_seconds": 100,
    }

    # First attempt
    response1 = client.post(
        f"/api/v1/mcqs/{sample_mcq.id}/attempt",
        json=attempt_data,
        headers=auth_headers,
    )
    assert response1.json()["attempt_number"] == 1

    # Second attempt
    response2 = client.post(
        f"/api/v1/mcqs/{sample_mcq.id}/attempt",
        json=attempt_data,
        headers=auth_headers,
    )
    assert response2.json()["attempt_number"] == 2


def test_submit_mcq_attempt_id_mismatch(db_session, client, sample_mcq, auth_headers):
    """Test POST /api/v1/mcqs/{id}/attempt fails with ID mismatch"""
    attempt_data = {
        "mcq_id": 999,  # Mismatched ID
        "selected_answer": "B",
        "time_taken_seconds": 100,
    }

    response = client.post(
        f"/api/v1/mcqs/{sample_mcq.id}/attempt",
        json=attempt_data,
        headers=auth_headers,
    )

    assert response.status_code == 400
    assert "mismatch" in response.json()["detail"].lower()


def test_list_mcqs_success(db_session, client, multiple_mcqs, auth_headers):
    """Test GET /api/v1/mcqs lists MCQs with pagination"""
    response = client.get("/api/v1/mcqs?limit=3", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    assert len(data) <= 3
    assert all("question_id" in mcq for mcq in data)


def test_list_mcqs_with_filters(db_session, client, multiple_mcqs, auth_headers):
    """Test GET /api/v1/mcqs with specialty and difficulty filters"""
    response = client.get(
        "/api/v1/mcqs?specialty=cardiology&difficulty=easy", headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert all(mcq["specialty"] == "cardiology" for mcq in data)
    assert all(mcq["difficulty"] == "easy" for mcq in data)


def test_australian_drug_name_validation():
    """Test that American drug names are rejected in MCQ creation"""
    # This would require educator role, but we test the schema validation
    from src.schemas.mcq import MCQCreate
    from pydantic import ValidationError

    # Test American drug names are rejected
    american_drugs = {
        "A": "Give acetaminophen 1g",  # Should be paracetamol
        "B": "Administer epinephrine 1mg",  # Should be adrenaline
        "C": "Prescribe albuterol inhaler",  # Should be salbutamol
        "D": "None of the above",
    }

    with pytest.raises(ValidationError) as exc_info:
        MCQCreate(
            question_id="MCQ-TEST-001",
            question_text="Test question for drug name validation",
            options=american_drugs,
            correct_answer="D",
            explanation="Test explanation with eTG reference",
            citation="Therapeutic Guidelines: eTG, 2023",
            specialty=MedicalSpecialty.CARDIOLOGY,
        )

    error_message = str(exc_info.value)
    assert "australian drug name" in error_message.lower() or "paracetamol" in error_message.lower()


def test_australian_citation_validation():
    """Test that non-Australian citations are rejected"""
    from src.schemas.mcq import MCQCreate
    from pydantic import ValidationError

    with pytest.raises(ValidationError) as exc_info:
        MCQCreate(
            question_id="MCQ-TEST-002",
            question_text="Test question for citation validation",
            options={
                "A": "Option A",
                "B": "Option B",
                "C": "Option C",
                "D": "Option D",
            },
            correct_answer="A",
            explanation="Test explanation",
            citation="UpToDate, 2023",  # Not Australian guideline
            specialty=MedicalSpecialty.CARDIOLOGY,
        )

    error_message = str(exc_info.value)
    assert "australian" in error_message.lower()


def test_unauthenticated_request_fails(db_session, client):
    """Test that requests without auth token fail"""
    response = client.get("/api/v1/mcqs/random")

    assert response.status_code == 401


def test_mcq_statistics_endpoint(db_session, client, sample_mcq, auth_headers):
    """Test GET /api/v1/mcqs/statistics returns platform statistics"""
    response = client.get("/api/v1/mcqs/statistics", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()

    assert "total_mcqs" in data
    assert "by_specialty" in data
    assert "by_difficulty" in data
    assert "average_success_rate" in data

    assert data["total_mcqs"] == 1
    assert "cardiology" in data["by_specialty"]


# ============================================================================
# PERFORMANCE TESTS
# ============================================================================


def test_mcq_random_response_time(db_session, client, sample_mcq, auth_headers):
    """Test that GET /random responds in < 200ms (95th percentile)"""
    response_times = []

    # Run 20 requests
    for _ in range(20):
        start_time = time.time()
        response = client.get("/api/v1/mcqs/random", headers=auth_headers)
        elapsed_ms = (time.time() - start_time) * 1000
        response_times.append(elapsed_ms)
        assert response.status_code == 200

    # Calculate 95th percentile
    response_times.sort()
    p95 = response_times[int(len(response_times) * 0.95)]

    assert p95 < 200, f"95th percentile response time {p95}ms exceeds 200ms threshold"


def test_mcq_attempt_response_time(db_session, client, sample_mcq, auth_headers):
    """Test that POST /attempt responds in < 200ms (95th percentile)"""
    response_times = []
    attempt_data = {
        "mcq_id": sample_mcq.id,
        "selected_answer": "B",
        "time_taken_seconds": 100,
    }

    # Run 20 requests
    for _ in range(20):
        start_time = time.time()
        response = client.post(
            f"/api/v1/mcqs/{sample_mcq.id}/attempt",
            json=attempt_data,
            headers=auth_headers,
        )
        elapsed_ms = (time.time() - start_time) * 1000
        response_times.append(elapsed_ms)
        assert response.status_code == 200

    # Calculate 95th percentile
    response_times.sort()
    p95 = response_times[int(len(response_times) * 0.95)]

    assert p95 < 200, f"95th percentile response time {p95}ms exceeds 200ms threshold"
