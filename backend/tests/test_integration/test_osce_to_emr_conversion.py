"""
Integration Test: OSCE to EMR Conversion

Tests the integration between AI OSCE module and EMR Practice module.

PRD: PRD-MVP-004-INTEGRATION-TESTING.md
User Story: As a student, I want to convert my completed AI OSCE session
            into an EMR case for documentation practice.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime, timezone
from unittest.mock import patch


@pytest.mark.integration
class TestOSCEToEMRConversion:
    """Test AI OSCE session conversion to EMR cases"""

    def _create_patient_persona(self, db: Session):
        """Helper to create a patient persona for OSCE sessions"""
        from src.db.models import PatientPersona

        persona = PatientPersona(
            persona_id=str(uuid4()),
            persona_code="CARD-001-CHEST-PAIN",
            name="John Smith",
            age=55,
            gender="male",
            occupation="Builder",
            cultural_background="Australian",
            preferred_language="English",
            specialty="cardiology",
            chief_complaint="Chest pain",
            opening_statement="Doctor, I've been having this terrible chest pain...",
            symptoms={},
            medical_history={},
            emotional_profile={},
            rag_query_hints=[],
            key_differentials=[],
            critical_actions=[],
            difficulty_level="intermediate",
            amc_blueprint_area="cardiovascular",
            is_active=True,
        )
        db.add(persona)
        db.commit()
        db.refresh(persona)
        return persona

    def _create_completed_osce_attempt(self, db: Session, user_id: str, persona_id: str):
        """Helper to create a completed AI OSCE attempt"""
        from src.db.models import OSCEAttemptAI

        attempt_id = str(uuid4())
        osce_attempt = OSCEAttemptAI(
            attempt_id=attempt_id,
            user_id=str(user_id),
            persona_id=persona_id,
            session_type="individual",
            started_at=datetime.now(timezone.utc),
            ended_at=datetime.now(timezone.utc),
            duration_seconds=480,
            conversation_history=[
                {
                    "role": "patient",
                    "content": "I've been having this terrible chest pain for the last 2 hours.",
                    "timestamp": "2026-04-05T10:00:00Z",
                },
                {
                    "role": "student",
                    "content": "Can you describe the pain for me?",
                    "timestamp": "2026-04-05T10:00:15Z",
                },
                {
                    "role": "patient",
                    "content": "It's right in the middle of my chest, like someone is squeezing it.",
                    "timestamp": "2026-04-05T10:00:30Z",
                },
            ],
            emotional_state_transitions=[],
            student_actions=[],
            was_completed=True,
            session_state="complete",
        )
        db.add(osce_attempt)
        db.commit()
        db.refresh(osce_attempt)
        return osce_attempt

    def _mock_conversion_result(self):
        """Helper to create a mocked ConversionResult"""
        from src.schemas.integration import ConversionResult, SOAPNoteDraft, ConversionMetadata

        return ConversionResult(
            soap_note_draft=SOAPNoteDraft(
                subjective="55-year-old male presents with 2-hour history of central chest pain. Pain described as crushing and heavy. Associated with diaphoresis. Risk factors include hypertension, hyperlipidaemia, and smoking.",
                objective="Physical examination not performed during OSCE station.",
                assessment="Acute Coronary Syndrome (ACS) - most likely unstable angina or NSTEMI. Differential: GORD, musculoskeletal chest pain, pulmonary embolism.",
                plan="Urgent ECG and troponin. Aspirin 300mg PO stat. GTN spray sublingual PRN. Urgent cardiology review.",
            ),
            metadata=ConversionMetadata(
                pre_fill_percentage=0.78,
                extraction_confidence=0.85,
                tokens_used=1300,
                api_response_time_ms=420,
                missing_elements=["Vital signs", "Allergies", "Family history"],
                australian_terminology_compliance=True,
            ),
        )

    def test_conversion_01_complete_osce_session_and_convert(
        self, client: TestClient, db: Session, auth_headers: dict
    ):
        """
        Test 1: Create completed AI OSCE session and convert to EMR

        Steps:
        1. Create patient persona in database
        2. Create completed OSCEAttemptAI in database
        3. POST /api/v1/integration/osce-to-emr with attempt_id
        4. Verify EMR session created with 201 status

        Expected:
        - Conversion endpoint returns 201
        - Response contains emr_session_id, pre_fill_percentage, redirect_url
        - Pre-fill percentage meets ≥70% target
        """
        from src.db.models import User

        user = db.query(User).filter(User.email == "test@test.com").first()
        persona = self._create_patient_persona(db)
        osce_attempt = self._create_completed_osce_attempt(db, user.id, persona.persona_id)

        mock_result = self._mock_conversion_result()

        with patch(
            "src.api.v1.integration.converter.OSCEToEMRConverter.convert",
            return_value=mock_result,
        ):
            response = client.post(
                "/api/v1/integration/osce-to-emr",
                json={"osceAttemptId": osce_attempt.attempt_id},
                headers=auth_headers,
            )

        assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
        data = response.json()

        assert "emrSessionId" in data
        assert "preFillPercentage" in data
        assert "extractionConfidence" in data
        assert "redirectUrl" in data
        assert "message" in data

        # Pre-fill accuracy ≥70%
        assert data["preFillPercentage"] >= 0.70

        # Extraction confidence ≥65%
        assert data["extractionConfidence"] >= 0.65

        # Redirect URL points to a real EMR route (the old /emr/session/{id}
        # route never existed; the converter now targets /emr/select/{id}).
        assert "/emr/select/" in data["redirectUrl"]

    def test_conversion_02_verify_emr_session_content(
        self, client: TestClient, db: Session, auth_headers: dict
    ):
        """
        Test 2: Verify converted EMR session references a real MockPatient and
        stores the pre-filled SOAP note as an editable draft.

        Steps:
        1. Create completed OSCE attempt
        2. Convert via API endpoint
        3. Inspect the created EMRSession, MockPatient and draft EMRSOAPNote
        4. GET /api/v1/emr/sessions/{session_id} loads the draft SOAP note

        Expected (MockPatient design):
        - EMR session references a real MockPatient (patient_id NOT NULL)
        - specialty/difficulty populated (migration-008 NOT NULL columns)
        - status == "in_progress", source_osce_attempt_id linked
        - SOAP note stored as an EMRSOAPNote DRAFT (is_final_submission False),
          NOT in an un-migrated session_data JSON blob
        - conversion_metadata tracked
        """
        from src.db.models import User, EMRSession, MockPatient, EMRSOAPNote

        user = db.query(User).filter(User.email == "test@test.com").first()
        persona = self._create_patient_persona(db)
        osce_attempt = self._create_completed_osce_attempt(db, user.id, persona.persona_id)

        mock_result = self._mock_conversion_result()

        # Convert OSCE to EMR
        with patch(
            "src.api.v1.integration.converter.OSCEToEMRConverter.convert",
            return_value=mock_result,
        ):
            conversion_response = client.post(
                "/api/v1/integration/osce-to-emr",
                json={"osceAttemptId": osce_attempt.attempt_id},
                headers=auth_headers,
            )

        assert conversion_response.status_code == 201, conversion_response.text
        emr_session_id = conversion_response.json()["emrSessionId"]

        # Verify EMR session in database
        emr_session = (
            db.query(EMRSession)
            .filter(EMRSession.id == emr_session_id)
            .first()
        )
        assert emr_session is not None
        assert emr_session.source_osce_attempt_id == osce_attempt.attempt_id
        assert emr_session.user_id == user.id
        assert emr_session.status == "in_progress"

        # NOT-NULL migration-008 columns must be populated
        assert emr_session.patient_id is not None
        assert emr_session.specialty == persona.specialty
        assert emr_session.difficulty  # non-empty

        # The un-migrated JSON columns must not exist on the model at all.
        assert not hasattr(emr_session, "session_data")
        assert not hasattr(emr_session, "patient_data")

        # A real MockPatient was materialised from the OSCE persona
        mock_patient = (
            db.query(MockPatient)
            .filter(MockPatient.id == emr_session.patient_id)
            .first()
        )
        assert mock_patient is not None
        assert mock_patient.name == persona.name
        assert mock_patient.age == persona.age
        assert mock_patient.gender == persona.gender
        assert mock_patient.specialty == persona.specialty
        assert mock_patient.presenting_complaint == persona.chief_complaint
        assert mock_patient.demographics is not None
        assert mock_patient.demographics.get("source_osce_attempt_id") == osce_attempt.attempt_id

        # The pre-filled SOAP note is stored as an editable DRAFT
        draft = (
            db.query(EMRSOAPNote)
            .filter(
                EMRSOAPNote.session_id == emr_session.id,
                EMRSOAPNote.is_final_submission == False,  # noqa: E712
            )
            .first()
        )
        assert draft is not None
        assert draft.subjective == mock_result.soap_note_draft.subjective
        assert draft.objective == mock_result.soap_note_draft.objective
        assert draft.assessment == mock_result.soap_note_draft.assessment
        assert draft.plan == mock_result.soap_note_draft.plan

        # The editor loads the draft via the normal GET session path
        get_response = client.get(
            f"/api/v1/emr/sessions/{emr_session_id}",
            headers=auth_headers,
        )
        assert get_response.status_code == 200, get_response.text
        soap_note = get_response.json()["soap_note"]
        assert soap_note is not None
        assert soap_note["subjective"] == mock_result.soap_note_draft.subjective
        assert soap_note["plan"] == mock_result.soap_note_draft.plan

        # Verify conversion metadata
        meta = emr_session.conversion_metadata or {}
        assert "pre_fill_percentage" in meta
        assert "extraction_confidence" in meta
        assert "tokens_used" in meta

    def test_conversion_03_unauthorized_conversion_rejected(
        self, client: TestClient, db: Session, auth_headers: dict
    ):
        """
        Test 3: Verify user cannot convert another user's OSCE attempt

        Steps:
        1. Create OSCE attempt for user A
        2. Attempt conversion as user B (different auth)
        3. Verify 403 Forbidden response

        Expected:
        - Conversion rejected with 403 status
        - Error code 'UNAUTHORIZED'
        - No EMR session created
        """
        from src.db.models import User, EMRSession
        from src.auth.security import create_access_token

        # Create a second user
        user_b = User(
            email="otheruser@test.com",
            password_hash="$2b$12$dummyhashforusertest",
            full_name="Other User",
            role="student",
            is_verified=True,
            is_active=True,
        )
        db.add(user_b)
        db.commit()
        db.refresh(user_b)

        # Create OSCE attempt for the original test user (user A)
        persona = self._create_patient_persona(db)
        user_a = db.query(User).filter(User.email == "test@test.com").first()
        osce_attempt = self._create_completed_osce_attempt(db, user_a.id, persona.persona_id)

        # Auth headers for user B
        access_token_b = create_access_token(
            data={"sub": user_b.email, "user_id": str(user_b.id)}
        )
        auth_headers_b = {"Authorization": f"Bearer {access_token_b}"}

        # Attempt conversion as user B
        response = client.post(
            "/api/v1/integration/osce-to-emr",
            json={"osceAttemptId": osce_attempt.attempt_id},
            headers=auth_headers_b,
        )

        assert response.status_code == 403, f"Expected 403, got {response.status_code}: {response.text}"
        data = response.json()
        error = data.get("detail", data)
        assert error.get("error_code") == "UNAUTHORIZED" or "UNAUTHORIZED" in str(error)

        # Verify no EMR session was created for this OSCE attempt
        emr_count = (
            db.query(EMRSession)
            .filter(EMRSession.source_osce_attempt_id == osce_attempt.attempt_id)
            .count()
        )
        assert emr_count == 0
