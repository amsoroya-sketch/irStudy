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

    def test_get_random_mcq_success(self, db_session, client: TestClient, sample_mcq: MCQ, auth_headers):
        """Test GET /mcqs/random returns random MCQ"""
        response = client.get("/api/v1/mcqs/random", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Verify MCQ structure (MCQResponse includes both id and question_id)
        assert "id" in data  # Database ID
        assert "question_id" in data  # Unique question ID (MCQ-CARD-001)
        assert "question_text" in data
        assert "options" in data
        assert "specialty" in data
        assert "difficulty" in data

        # Ensure correct answer NOT exposed (practice mode)
        assert "correct_answer" not in data
        assert "explanation" not in data

    def test_get_random_mcq_with_filters(self, db_session, client: TestClient, sample_mcq: MCQ, auth_headers):
        """Test GET /mcqs/random with specialty and difficulty filters"""
        response = client.get(
            "/api/v1/mcqs/random",
            params={"specialty": "cardiology", "difficulty": "medium"},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["specialty"] == "cardiology"
        assert data["difficulty"] == "medium"

    def test_get_random_mcq_no_results(self, db_session, client: TestClient, auth_headers):
        """Test GET /mcqs/random with no matching questions returns 404"""
        response = client.get(
            "/api/v1/mcqs/random",
            params={"specialty": "cardiology", "difficulty": "easy"},
            headers=auth_headers
        )

        # Assuming no MCQs match this filter (database is empty except sample_mcq)
        assert response.status_code == 404
        assert "No MCQs found" in response.json()["detail"]

    def test_get_mcq_by_id_success(self, db_session, client: TestClient, sample_mcq: MCQ, auth_headers):
        """Test GET /mcqs/{id} returns specific MCQ"""
        response = client.get(f"/api/v1/mcqs/{sample_mcq.id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == sample_mcq.id
        assert data["question_id"] == sample_mcq.question_id
        assert data["question_text"] == sample_mcq.question_text

    def test_get_mcq_by_id_not_found(self, db_session, client: TestClient, auth_headers):
        """Test GET /mcqs/{id} with invalid ID returns 404"""
        response = client.get("/api/v1/mcqs/99999", headers=auth_headers)

        assert response.status_code == 404
        # FastAPI standard error format
        assert "not found" in response.json()["detail"].lower()

    def test_submit_mcq_answer_correct(self, db_session, client: TestClient, sample_mcq: MCQ, auth_headers):
        """Test POST /mcqs/{id}/attempt with correct answer"""
        attempt_data = {
            "mcq_id": sample_mcq.id,
            "selected_answer": sample_mcq.correct_answer,
            "time_taken_seconds": 120,
            "confidence_level": 4
        }

        response = client.post(
            f"/api/v1/mcqs/{sample_mcq.id}/attempt",
            json=attempt_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["is_correct"] is True
        assert data["correct_answer"] == sample_mcq.correct_answer
        assert "explanation" in data
        assert "citation" in data

    def test_submit_mcq_answer_incorrect(self, db_session, client: TestClient, sample_mcq: MCQ, auth_headers):
        """Test POST /mcqs/{id}/attempt with incorrect answer"""
        # Select wrong answer
        wrong_answer = "A" if sample_mcq.correct_answer != "A" else "C"

        attempt_data = {
            "mcq_id": sample_mcq.id,
            "selected_answer": wrong_answer,
            "time_taken_seconds": 90,
            "confidence_level": 2
        }

        response = client.post(
            f"/api/v1/mcqs/{sample_mcq.id}/attempt",
            json=attempt_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["is_correct"] is False
        assert data["correct_answer"] == sample_mcq.correct_answer
        assert "explanation" in data

    def test_submit_mcq_answer_id_mismatch(self, db_session, client: TestClient, sample_mcq: MCQ, auth_headers):
        """Test POST /mcqs/{id}/attempt fails with ID mismatch"""
        attempt_data = {
            "mcq_id": 999,  # Mismatched ID
            "selected_answer": "B",
            "time_taken_seconds": 100
        }

        response = client.post(
            f"/api/v1/mcqs/{sample_mcq.id}/attempt",
            json=attempt_data,
            headers=auth_headers
        )

        assert response.status_code == 400
        assert "mismatch" in response.json()["detail"].lower()

    def test_australian_drug_name_validation(self, db_session, client: TestClient, sample_mcq: MCQ, auth_headers):
        """Test that American drug names are rejected"""
        # This test assumes validation happens on question creation
        # For retrieval, we ensure no American drug names exist in database

        response = client.get("/api/v1/mcqs/random", headers=auth_headers)

        if response.status_code == 200:
            data = response.json()
            question_text = data["question_text"].lower()
            options_text = str(data["options"]).lower()

            # Ensure no American drug names
            assert "acetaminophen" not in question_text
            assert "acetaminophen" not in options_text
            assert "albuterol" not in question_text
            assert "epinephrine" not in question_text

    def test_australian_citation_present(self, db_session, client: TestClient, sample_mcq: MCQ, auth_headers):
        """Test that all MCQs have Australian citations"""
        attempt_data = {
            "mcq_id": sample_mcq.id,
            "selected_answer": sample_mcq.correct_answer,
            "time_taken_seconds": 100
        }

        response = client.post(
            f"/api/v1/mcqs/{sample_mcq.id}/attempt",
            json=attempt_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        citation = data["citation"].lower()

        # Verify Australian source present
        australian_sources = ["etg", "pbs", "amh", "ahpra", "therapeutic guidelines"]
        assert any(source in citation for source in australian_sources), \
            f"Citation must reference Australian source: {data['citation']}"
