"""
Integration Test: OSCE to EMR Conversion

Tests the integration between OSCE module and EMR module.

PRD: PRD-MVP-004-INTEGRATION-TESTING.md
User Story: As a student, I want to convert my completed OSCE session
            into an EMR case for documentation practice.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import json

@pytest.mark.integration
class TestOSCEToEMRConversion:
    """Test OSCE session conversion to EMR cases"""

    def test_conversion_01_complete_osce_session_first(
        self, client: TestClient, db: Session, auth_headers: dict
    ):
        """
        Test 5: Complete OSCE session before conversion

        Steps:
        1. Create OSCE scenario in database
        2. POST /api/v1/osces/sessions with responses
        3. Verify OSCE session created with completed status
        4. Verify session includes patient context

        Expected:
        - OSCE session created successfully
        - Status is "completed"
        - Patient demographics captured
        """
        from src.db.models import OSCE, MedicalSpecialty

        # Setup: Create OSCE scenario
        osce = OSCE(
            osce_id="INTEGRATION-OSCE-CHEST-PAIN-001",
            title="Chest Pain Assessment",
            specialty=MedicalSpecialty.CARDIOLOGY,
            scenario_text="Patient presents with chest pain...",
            patient_demographics={
                "age": 55,
                "gender": "Male",
                "presenting_complaint": "Chest pain"
            },
            history_taking_rubric=[
                {"item": "Onset", "weight": 1.0},
                {"item": "Character", "weight": 1.0},
                {"item": "Radiation", "weight": 1.0}
            ],
            is_published=True
        )
        db.add(osce)
        db.commit()

        # Create OSCE session
        session_data = {
            "osce_id": "INTEGRATION-OSCE-CHEST-PAIN-001",
            "responses": {
                "history_taking": ["Onset", "Character", "Radiation"],
                "physical_exam": ["Vital signs", "Cardiovascular exam"]
            }
        }

        response = client.post(
            "/api/v1/osces/sessions",
            json=session_data,
            headers=auth_headers
        )

        assert response.status_code == 201
        session = response.json()

        assert "session_id" in session
        assert session["status"] == "completed"
        assert session["osce_id"] == "INTEGRATION-OSCE-CHEST-PAIN-001"

        return session["session_id"]

    def test_conversion_02_convert_osce_to_emr_case(
        self, client: TestClient, db: Session, auth_headers: dict
    ):
        """
        Test 6: Convert OSCE session to EMR case

        Steps:
        1. Create and complete OSCE session (from Test 5)
        2. POST /api/v1/emr/convert-from-osce with session_id
        3. Verify EMR case created
        4. Verify patient context transferred correctly
        5. Verify history items mapped

        Expected:
        - EMR case created successfully
        - All OSCE data transferred
        - Source OSCE session linked
        """
        from src.db.models import OSCE, OSCESession, MedicalSpecialty
        from src.core.auth import create_access_token

        # Setup: Create OSCE and session
        osce = OSCE(
            osce_id="INTEGRATION-OSCE-CONVERSION-TEST",
            title="Conversion Test OSCE",
            specialty=MedicalSpecialty.CARDIOLOGY,
            scenario_text="Test scenario for conversion",
            patient_demographics={
                "age": 45,
                "gender": "Female",
                "presenting_complaint": "Shortness of breath"
            },
            history_taking_rubric=[
                {"item": "Onset", "weight": 1.0},
                {"item": "Duration", "weight": 1.0}
            ],
            is_published=True
        )
        db.add(osce)
        db.flush()

        # Extract user_id from auth_headers
        token = auth_headers["Authorization"].replace("Bearer ", "")
        # Decode token to get user_id (simplified for test)
        from src.db.models import User
        user = db.query(User).first()

        osce_session = OSCESession(
            osce_id=osce.osce_id,
            user_id=user.id,
            responses={
                "history_taking": ["Onset", "Duration"],
                "physical_exam": ["Vital signs"]
            },
            score=8.5,
            status="completed"
        )
        db.add(osce_session)
        db.commit()

        # Convert to EMR
        conversion_data = {
            "osce_session_id": str(osce_session.id)
        }

        response = client.post(
            "/api/v1/emr/convert-from-osce",
            json=conversion_data,
            headers=auth_headers
        )

        assert response.status_code == 201
        emr_case = response.json()

        assert "case_id" in emr_case
        assert emr_case["status"] == "active"
        assert emr_case["source_osce_session_id"] == str(osce_session.id)

        # Verify patient context transferred
        patient_context = emr_case["patient_context"]
        assert patient_context["demographics"]["age"] == 45
        assert patient_context["demographics"]["gender"] == "Female"
        assert patient_context["presenting_complaint"] == "Shortness of breath"

        # Verify history items
        assert len(patient_context["history"]) == 2
        history_items = [item["item"] for item in patient_context["history"]]
        assert "Onset" in history_items
        assert "Duration" in history_items

    def test_conversion_03_verify_bidirectional_link(
        self, client: TestClient, db: Session, auth_headers: dict
    ):
        """
        Test 7: Verify OSCE ↔ EMR bidirectional linking

        Steps:
        1. Create OSCE session
        2. Convert to EMR case
        3. GET /api/v1/osces/sessions/{id} - verify emr_case_id present
        4. GET /api/v1/emr/cases/{id} - verify osce_session_id present

        Expected:
        - OSCE session has emr_case_id reference
        - EMR case has osce_session_id reference
        - Can navigate between both
        """
        from src.db.models import OSCE, OSCESession, User, MedicalSpecialty

        # Setup
        user = db.query(User).first()

        osce = OSCE(
            osce_id="INTEGRATION-BIDIRECTIONAL-TEST",
            title="Bidirectional Link Test",
            specialty=MedicalSpecialty.GENERAL_PRACTICE,
            scenario_text="Test",
            patient_demographics={"age": 30, "gender": "Male"},
            history_taking_rubric=[{"item": "Test", "weight": 1.0}],
            is_published=True
        )
        db.add(osce)
        db.flush()

        osce_session = OSCESession(
            osce_id=osce.osce_id,
            user_id=user.id,
            responses={"history_taking": ["Test"]},
            score=9.0,
            status="completed"
        )
        db.add(osce_session)
        db.commit()

        # Convert
        conversion_response = client.post(
            "/api/v1/emr/convert-from-osce",
            json={"osce_session_id": str(osce_session.id)},
            headers=auth_headers
        )

        assert conversion_response.status_code == 201
        emr_case_id = conversion_response.json()["case_id"]

        # Verify OSCE → EMR link
        osce_response = client.get(
            f"/api/v1/osces/sessions/{osce_session.id}",
            headers=auth_headers
        )

        assert osce_response.status_code == 200
        osce_data = osce_response.json()
        assert osce_data.get("emr_case_id") == emr_case_id

        # Verify EMR → OSCE link
        emr_response = client.get(
            f"/api/v1/emr/cases/{emr_case_id}",
            headers=auth_headers
        )

        assert emr_response.status_code == 200
        emr_data = emr_response.json()
        assert emr_data["source_osce_session_id"] == str(osce_session.id)
