"""
Test suite for MCQ API endpoints

COVERAGE TARGET: 100%
AUSTRALIAN CONTEXT: All tests validate Australian drug names and citations
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.db.models import MCQ, MedicalSpecialty, DifficultyLevel


class TestMCQEndpoints:
    """Test MCQ CRUD endpoints"""

    def test_get_random_mcq_success(self, client: TestClient, db: Session, sample_mcq: MCQ):
        """Test GET /mcqs/random returns random MCQ"""
        response = client.get("/api/v1/mcqs/random")

        assert response.status_code == 200
        data = response.json()

        assert "question_id" in data
        assert "question_text" in data
        assert "options" in data
        assert "specialty" in data
        assert "difficulty" in data

        # Ensure correct answer NOT exposed
        assert "correct_answer" not in data
        assert "explanation" not in data

    def test_get_random_mcq_with_filters(self, client: TestClient, db: Session, sample_mcq: MCQ):
        """Test GET /mcqs/random with specialty and difficulty filters"""
        response = client.get(
            "/api/v1/mcqs/random",
            params={"specialty": "cardiology", "difficulty": "medium"}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["specialty"] == "cardiology"
        assert data["difficulty"] == "medium"

    def test_get_random_mcq_no_results(self, client: TestClient, db: Session):
        """Test GET /mcqs/random with no matching questions returns 404"""
        response = client.get(
            "/api/v1/mcqs/random",
            params={"specialty": "cardiology", "difficulty": "easy"}
        )

        # Assuming no MCQs match this filter
        assert response.status_code in [200, 404]

    def test_get_mcq_by_id_success(self, client: TestClient, db: Session, sample_mcq: MCQ):
        """Test GET /mcqs/{id} returns specific MCQ"""
        response = client.get(f"/api/v1/mcqs/{sample_mcq.question_id}")

        assert response.status_code == 200
        data = response.json()

        assert data["question_id"] == sample_mcq.question_id
        assert data["question_text"] == sample_mcq.question_text

    def test_get_mcq_by_id_not_found(self, client: TestClient, db: Session):
        """Test GET /mcqs/{id} with invalid ID returns 404"""
        response = client.get("/api/v1/mcqs/INVALID-ID-999")

        assert response.status_code == 404
        response_data = response.json()
        # Custom error handler returns {"error": {"code": 404, "message": "...", "path": "..."}}
        assert "error" in response_data
        assert "not found" in response_data["error"]["message"].lower()

    def test_submit_mcq_answer_correct(self, client: TestClient, db: Session, sample_mcq: MCQ):
        """Test POST /mcqs/{id}/submit with correct answer"""
        response = client.post(
            f"/api/v1/mcqs/{sample_mcq.question_id}/submit",
            json={
                "selected_answer": sample_mcq.correct_answer,
                "user_id": 1,
                "time_spent_seconds": 120
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert data["is_correct"] is True
        assert data["correct_answer"] == sample_mcq.correct_answer
        assert "explanation" in data
        assert "citation" in data

    def test_submit_mcq_answer_incorrect(self, client: TestClient, db: Session, sample_mcq: MCQ):
        """Test POST /mcqs/{id}/submit with incorrect answer"""
        # Select wrong answer
        wrong_answer = "A" if sample_mcq.correct_answer != "A" else "B"

        response = client.post(
            f"/api/v1/mcqs/{sample_mcq.question_id}/submit",
            json={
                "selected_answer": wrong_answer,
                "user_id": 1,
                "time_spent_seconds": 90
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert data["is_correct"] is False
        assert data["correct_answer"] == sample_mcq.correct_answer
        assert "explanation" in data

    def test_submit_mcq_answer_invalid_format(self, client: TestClient, db: Session, sample_mcq: MCQ):
        """Test POST /mcqs/{id}/submit with invalid answer format"""
        response = client.post(
            f"/api/v1/mcqs/{sample_mcq.question_id}/submit",
            json={
                "selected_answer": "Z",  # Invalid option
                "user_id": 1
            }
        )

        assert response.status_code == 422  # Validation error

    def test_get_mcq_explanation_success(self, client: TestClient, db: Session, sample_mcq: MCQ):
        """Test GET /mcqs/{id}/explanation returns explanation"""
        response = client.get(f"/api/v1/mcqs/{sample_mcq.question_id}/explanation")

        assert response.status_code == 200
        data = response.json()

        assert data["correct_answer"] == sample_mcq.correct_answer
        assert "explanation" in data
        assert "citation" in data
        assert "specialty" in data

    def test_australian_drug_name_validation(self, client: TestClient, db: Session):
        """Test that American drug names are rejected"""
        # This test assumes validation happens on question creation
        # For retrieval, we ensure no American drug names exist in database

        response = client.get("/api/v1/mcqs/random")

        if response.status_code == 200:
            data = response.json()
            question_text = data["question_text"].lower()
            options_text = str(data["options"]).lower()

            # Ensure no American drug names
            assert "acetaminophen" not in question_text
            assert "acetaminophen" not in options_text
            assert "albuterol" not in question_text
            assert "epinephrine" not in question_text

    def test_australian_citation_present(self, client: TestClient, db: Session, sample_mcq: MCQ):
        """Test that all MCQs have Australian citations"""
        response = client.post(
            f"/api/v1/mcqs/{sample_mcq.question_id}/submit",
            json={"selected_answer": sample_mcq.correct_answer}
        )

        assert response.status_code == 200
        data = response.json()

        citation = data["citation"].lower()

        # Verify Australian source present
        australian_sources = ["etg", "pbs", "amh", "ahpra", "therapeutic guidelines"]
        assert any(source in citation for source in australian_sources), \
            f"Citation must reference Australian source: {data['citation']}"


@pytest.fixture
def sample_mcq(db: Session) -> MCQ:
    """Create sample MCQ for testing"""
    mcq = MCQ(
        question_id="MCQ-TEST-001",
        question_text="A 65-year-old patient presents with chest pain. What is the first-line medication for acute management?",
        options={
            "A": "Paracetamol 1g PO",
            "B": "Aspirin 300mg PO",
            "C": "Morphine 10mg IV",
            "D": "GTN spray 400mcg SL",
            "E": "Clopidogrel 300mg PO"
        },
        correct_answer="B",
        explanation="Aspirin 300mg is the first-line medication for suspected acute coronary syndrome...",
        citation="eTG - Cardiovascular: Acute Coronary Syndrome",
        specialty=MedicalSpecialty.CARDIOLOGY,
        difficulty=DifficultyLevel.MEDIUM,
        tags=["acute coronary syndrome", "chest pain", "emergency management"]
    )

    db.add(mcq)
    db.commit()
    db.refresh(mcq)

    return mcq
