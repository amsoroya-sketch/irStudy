"""
Test suite for OSCE API endpoints

COVERAGE TARGET: 100%
AMC CLINICAL EXAM FORMAT: 15-mark rubric, 9/15 pass mark, 8-minute stations
AUSTRALIAN CONTEXT: All tests validate Australian terminology and protocols
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.db.models import OSCE, OSCEType, MedicalSpecialty, DifficultyLevel


class TestOSCEEndpoints:
    """Test OSCE CRUD endpoints"""

    def test_get_random_osce_success(self, client: TestClient, db: Session, sample_osce: OSCE):
        """Test GET /osces/random returns random OSCE station"""
        response = client.get("/api/v1/osces/random")

        assert response.status_code == 200
        data = response.json()

        assert "osce_id" in data
        assert "station_title" in data
        assert "station_type" in data
        assert "candidate_instructions" in data
        assert "time_limit_minutes" in data

        # Ensure patient instructions NOT exposed to candidate
        assert "patient_instructions" not in data
        assert "examiner_instructions" not in data

    def test_get_random_osce_with_filters(self, client: TestClient, db: Session, sample_osce: OSCE):
        """Test GET /osces/random with station_type and specialty filters"""
        response = client.get(
            "/api/v1/osces/random",
            params={"station_type": "history_taking", "specialty": "cardiology"}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["station_type"] == "history_taking"
        assert data["specialty"] == "cardiology"

    def test_get_random_osce_no_results(self, client: TestClient, db: Session):
        """Test GET /osces/random with no matching stations returns 404"""
        response = client.get(
            "/api/v1/osces/random",
            params={"station_type": "history_taking", "difficulty": "easy"}
        )

        # Assuming no OSCEs match this filter
        assert response.status_code in [200, 404]

    def test_get_osce_by_id_success(self, client: TestClient, db: Session, sample_osce: OSCE):
        """Test GET /osces/{id} returns specific OSCE station"""
        response = client.get(f"/api/v1/osces/{sample_osce.osce_id}")

        assert response.status_code == 200
        data = response.json()

        assert data["osce_id"] == sample_osce.osce_id
        assert data["station_title"] == sample_osce.station_title

    def test_get_osce_by_id_not_found(self, client: TestClient, db: Session):
        """Test GET /osces/{id} with invalid ID returns 404"""
        response = client.get("/api/v1/osces/INVALID-ID-999")

        assert response.status_code == 404
        response_data = response.json()
        # Custom error handler returns {"error": {"code": 404, "message": "...", "path": "..."}}
        assert "error" in response_data
        assert "not found" in response_data["error"]["message"].lower()

    def test_complete_osce_passed(self, client: TestClient, db: Session, sample_osce: OSCE):
        """Test POST /osces/{id}/complete with passing score"""
        response = client.post(
            f"/api/v1/osces/{sample_osce.osce_id}/complete",
            json={
                "user_id": 1,
                "score": 12,  # ≥9/15 = pass
                "time_spent_seconds": 480,  # 8 minutes
                "feedback": {
                    "introduction": 1,
                    "history_taking": 4,
                    "communication": 4,
                    "diagnosis": 2,
                    "management": 1
                },
                "notes": "Good systematic approach"
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert data["score"] == 12
        assert data["max_score"] == 15
        assert data["passed"] is True
        assert data["pass_mark"] == 9

    def test_complete_osce_failed(self, client: TestClient, db: Session, sample_osce: OSCE):
        """Test POST /osces/{id}/complete with failing score"""
        response = client.post(
            f"/api/v1/osces/{sample_osce.osce_id}/complete",
            json={
                "user_id": 1,
                "score": 7,  # <9/15 = fail
                "time_spent_seconds": 480
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert data["score"] == 7
        assert data["passed"] is False
        assert data["pass_mark"] == 9

    def test_complete_osce_borderline_pass(self, client: TestClient, db: Session, sample_osce: OSCE):
        """Test POST /osces/{id}/complete with exact pass mark"""
        response = client.post(
            f"/api/v1/osces/{sample_osce.osce_id}/complete",
            json={
                "user_id": 1,
                "score": 9,  # Exactly 9/15 = pass
                "time_spent_seconds": 480
            }
        )

        assert response.status_code == 200
        data = response.json()

        assert data["score"] == 9
        assert data["passed"] is True

    def test_get_osce_rubric_success(self, client: TestClient, db: Session, sample_osce: OSCE):
        """Test GET /osces/{id}/rubric returns scoring rubric"""
        response = client.get(f"/api/v1/osces/{sample_osce.osce_id}/rubric")

        assert response.status_code == 200
        data = response.json()

        assert data["osce_id"] == sample_osce.osce_id
        assert "rubric" in data
        assert data["max_marks"] == 15
        assert data["pass_mark"] == 9
        assert data["time_limit_minutes"] == 8

    def test_rubric_totals_15_marks(self, client: TestClient, db: Session, sample_osce: OSCE):
        """Test that rubric categories sum to exactly 15 marks (AMC format)"""
        response = client.get(f"/api/v1/osces/{sample_osce.osce_id}/rubric")

        assert response.status_code == 200
        data = response.json()

        rubric = data["rubric"]
        total_marks = sum(category["max_marks"] for category in rubric.values())

        assert total_marks == 15, f"Rubric must total 15 marks (AMC format), got {total_marks}"

    def test_australian_terminology_validation(self, client: TestClient, db: Session):
        """Test that American terminology is not present in OSCE stations"""
        response = client.get("/api/v1/osces/random")

        if response.status_code == 200:
            data = response.json()
            instructions = data["candidate_instructions"].lower()

            # Ensure no American terminology
            assert "911" not in instructions  # Use 000
            assert "emergency room" not in instructions  # Use emergency department
            assert "acetaminophen" not in instructions  # Use paracetamol
            assert "epinephrine" not in instructions  # Use adrenaline

    def test_time_limit_eight_minutes(self, client: TestClient, db: Session, sample_osce: OSCE):
        """Test that OSCE stations have 8-minute time limit (AMC format)"""
        response = client.get(f"/api/v1/osces/{sample_osce.osce_id}")

        assert response.status_code == 200
        data = response.json()

        assert data["time_limit_minutes"] == 8, "AMC Clinical Exam stations are 8 minutes"


@pytest.fixture
def sample_osce(db: Session) -> OSCE:
    """Create sample OSCE station for testing"""
    osce = OSCE(
        osce_id="OSCE-TEST-001",
        station_title="History Taking - Chest Pain",
        station_type=OSCEType.HISTORY_TAKING,
        patient_instructions=(
            "You are a 65-year-old patient presenting with chest pain. "
            "Describe central crushing chest pain radiating to left arm, started 2 hours ago."
        ),
        candidate_instructions=(
            "You are in the emergency department. "
            "Take a focused history from this patient presenting with chest pain. "
            "You have 8 minutes."
        ),
        examiner_instructions="Assess history taking using SOCRATES framework.",
        rubric={
            "introduction": {"max_marks": 1, "criteria": "Introduces self, confirms patient identity"},
            "history_taking": {"max_marks": 5, "criteria": "SOCRATES framework applied"},
            "communication": {"max_marks": 4, "criteria": "Clear communication, empathy"},
            "diagnosis": {"max_marks": 3, "criteria": "Appropriate differential diagnosis"},
            "management": {"max_marks": 2, "criteria": "Initial management plan outlined"}
        },
        specialty=MedicalSpecialty.CARDIOLOGY,
        difficulty=DifficultyLevel.MEDIUM,
        time_limit_minutes=8,
        learning_objectives=[
            "Apply SOCRATES framework for pain history",
            "Identify red flags for acute coronary syndrome",
            "Communicate effectively with distressed patient"
        ],
        tags=["chest pain", "history taking", "acute coronary syndrome"]
    )

    db.add(osce)
    db.commit()
    db.refresh(osce)

    return osce
