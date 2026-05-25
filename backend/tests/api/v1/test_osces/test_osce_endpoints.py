"""
Test suite for OSCE API endpoints

COVERAGE TARGET: 100%
AMC CLINICAL EXAM FORMAT: 15-mark rubric, 9/15 pass mark, 8-minute stations
AUSTRALIAN CONTEXT: All tests validate Australian terminology and protocols

NOTE: These tests use fixtures from:
- tests/conftest.py (db_session, client, auth_headers, test_user)
- tests/api/v1/test_osces/conftest.py (sample_osce)
"""

import pytest
from fastapi.testclient import TestClient

from src.db.models import OSCE


class TestOSCEEndpoints:
    """Test OSCE CRUD endpoints"""

    def test_get_random_osce_success(self, client: TestClient, sample_osce: OSCE, auth_headers: dict):
        """Test GET /osces/random returns random OSCE station"""
        response = client.get("/api/v1/osces/random", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Verify OSCE structure (current API response fields)
        assert "id" in data  # Database ID
        assert "osce_id" in data  # Station ID (e.g., OSCE-CARD-001)
        assert "station_title" in data
        assert "station_type" in data
        assert "candidate_instructions" in data
        assert "time_limit_minutes" in data
        assert "specialty" in data
        assert "difficulty" in data

        # Verify patient_instructions ARE included (candidate needs to know scenario)
        assert "patient_instructions" in data

        # Verify rubric NOT included in random OSCE (practice mode)
        assert "rubric" not in data
        assert "examiner_instructions" not in data

    def test_get_random_osce_with_filters(self, client: TestClient, sample_osce: OSCE, auth_headers: dict):
        """Test GET /osces/random with station_type and specialty filters"""
        response = client.get(
            "/api/v1/osces/random",
            params={"station_type": "history_taking", "specialty": "cardiology"},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["station_type"] == "history_taking"
        assert data["specialty"] == "cardiology"

    def test_get_random_osce_no_results(self, client: TestClient, auth_headers: dict):
        """Test GET /osces/random with no matching stations returns 404"""
        # Filter by specialty that has no published OSCEs
        response = client.get(
            "/api/v1/osces/random",
            params={"specialty": "neurology"},  # No neurology OSCEs in fixture
            headers=auth_headers
        )

        # Should return 404 when no matching OSCEs
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "No OSCE" in data["detail"]

    def test_get_osce_by_id_success(self, client: TestClient, sample_osce: OSCE, auth_headers: dict):
        """Test GET /osces/{id} returns specific OSCE station"""
        # Use database ID (integer), not osce_id (string)
        response = client.get(f"/api/v1/osces/{sample_osce.id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert data["id"] == sample_osce.id
        assert data["osce_id"] == sample_osce.osce_id
        assert data["station_title"] == sample_osce.station_title

    def test_get_osce_by_id_not_found(self, client: TestClient, auth_headers: dict):
        """Test GET /osces/{id} with invalid ID returns 404"""
        response = client.get("/api/v1/osces/99999", headers=auth_headers)

        assert response.status_code == 404
        response_data = response.json()
        # FastAPI standard error format
        assert "detail" in response_data
        assert "not found" in response_data["detail"].lower()

    def test_complete_osce_passed(self, client: TestClient, sample_osce: OSCE, auth_headers: dict):
        """Test POST /osces/{id}/complete-station with passing score"""
        # AMC 15-mark rubric: 5 categories × 3 marks each
        completion_data = {
            "osce_id": sample_osce.id,  # Database ID
            "scores": {
                "history_examination": 3,  # Current rubric categories
                "clinical_reasoning": 3,
                "communication": 2,
                "safety": 2,
                "professionalism": 2,
            },  # Total: 12/15 = pass
            "time_taken_seconds": 480,  # 8 minutes
            "self_reflection": "Good systematic approach using SOCRATES framework",
        }

        response = client.post(
            f"/api/v1/osces/{sample_osce.id}/complete-station",  # Correct endpoint
            json=completion_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        # Check actual response fields (OSCEAttemptResponse)
        assert data["total_score"] == 12
        assert data["passed"] is True
        assert data["attempt_number"] == 1
        assert "rubric" in data  # Rubric included for self-review
        assert "areas_for_improvement" in data

    def test_complete_osce_failed(self, client: TestClient, sample_osce: OSCE, auth_headers: dict):
        """Test POST /osces/{id}/complete-station with failing score"""
        # Scores totaling 7/15 (47% - fail)
        completion_data = {
            "osce_id": sample_osce.id,
            "scores": {
                "history_examination": 1,
                "clinical_reasoning": 1,
                "communication": 2,
                "safety": 2,
                "professionalism": 1,
            },  # Total: 7/15 = fail
            "time_taken_seconds": 480,
            "self_reflection": "Struggled with systematic approach",
        }

        response = client.post(
            f"/api/v1/osces/{sample_osce.id}/complete-station",
            json=completion_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["total_score"] == 7
        assert data["passed"] is False
        # areas_for_improvement should list weak categories (score < 2)
        assert len(data["areas_for_improvement"]) > 0

    def test_complete_osce_borderline_pass(self, client: TestClient, sample_osce: OSCE, auth_headers: dict):
        """Test POST /osces/{id}/complete-station with exact pass mark"""
        # Scores totaling exactly 9/15 (borderline pass)
        completion_data = {
            "osce_id": sample_osce.id,
            "scores": {
                "history_examination": 2,
                "clinical_reasoning": 2,
                "communication": 2,
                "safety": 2,
                "professionalism": 1,
            },  # Total: 9/15 = pass
            "time_taken_seconds": 480,
        }

        response = client.post(
            f"/api/v1/osces/{sample_osce.id}/complete-station",
            json=completion_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["total_score"] == 9
        assert data["passed"] is True

    def test_get_osce_rubric_success(self, client: TestClient, sample_osce: OSCE, auth_headers: dict):
        """Test GET /osces/{id}/rubric returns scoring rubric"""
        response = client.get(f"/api/v1/osces/{sample_osce.id}/rubric", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Verify rubric response structure (OSCERubric schema)
        assert data["osce_id"] == sample_osce.osce_id
        assert data["station_title"] == sample_osce.station_title
        assert data["station_type"] == sample_osce.station_type.value
        assert "rubric" in data
        assert data["max_marks"] == 15
        assert data["pass_mark"] == 9
        assert data["time_limit_minutes"] == 8

        # Verify rubric has 5 AMC categories
        rubric = data["rubric"]
        assert "history_examination" in rubric
        assert "clinical_reasoning" in rubric
        assert "communication" in rubric
        assert "safety" in rubric
        assert "professionalism" in rubric

    def test_rubric_totals_15_marks(self, client: TestClient, sample_osce: OSCE, auth_headers: dict):
        """Test that rubric categories sum to exactly 15 marks (AMC format)"""
        response = client.get(f"/api/v1/osces/{sample_osce.id}/rubric", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        rubric = data["rubric"]
        total_marks = sum(category["max_marks"] for category in rubric.values())

        assert total_marks == 15, f"Rubric must total 15 marks (AMC format), got {total_marks}"

    def test_australian_terminology_validation(self, client: TestClient, sample_osce: OSCE, auth_headers: dict):
        """Test that American terminology is not present in OSCE stations"""
        response = client.get("/api/v1/osces/random", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        instructions = data["candidate_instructions"].lower()

        # Ensure no American terminology
        assert "911" not in instructions  # Use 000
        assert "emergency room" not in instructions  # Use emergency department
        assert "acetaminophen" not in instructions  # Use paracetamol
        # Note: "epinephrine" check removed - some Australian contexts use both terms

    def test_time_limit_eight_minutes(self, client: TestClient, sample_osce: OSCE, auth_headers: dict):
        """Test that OSCE stations have 8-minute time limit (AMC format)"""
        response = client.get(f"/api/v1/osces/{sample_osce.id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        assert data["time_limit_minutes"] == 8, "AMC Clinical Exam stations are 8 minutes"
