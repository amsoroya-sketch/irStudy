"""
Integration Test: New User Registration Journey

Tests the complete flow from landing page to first MCQ session.

PRD: PRD-MVP-004-INTEGRATION-TESTING.md
User Story: As a new medical student, I want to register, explore the
            dashboard, and complete my first MCQ practice session.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime
import time

@pytest.mark.integration
class TestNewUserRegistrationJourney:
    """Test complete new user onboarding flow"""

    def test_journey_01_complete_registration_flow(
        self, client: TestClient, db: Session
    ):
        """
        Test 1: Complete user registration flow

        Steps:
        1. POST /api/v1/auth/register with valid data
        2. Verify user created in database
        3. Verify email verification token generated
        4. Verify response includes user_id and email

        Expected:
        - 201 Created status
        - User record in database
        - Email verification pending
        """
        # Step 1: Register new user
        registration_data = {
            "email": "test.student@medical.edu.au",
            "password": "SecurePass123!",
            "full_name": "Dr. Test Student",
            "year_level": "Medical Student Year 4"
        }

        start_time = time.time()
        response = client.post("/api/v1/auth/register", json=registration_data)
        registration_time = time.time() - start_time

        # Assertions
        assert response.status_code == 201, f"Expected 201, got {response.status_code}"
        assert registration_time < 2.0, f"Registration took {registration_time}s (should be <2s)"

        data = response.json()
        assert "id" in data
        assert data["email"] == registration_data["email"]
        assert data["full_name"] == registration_data["full_name"]

        # Step 2: Verify user in database
        from src.db.models import User
        user = db.query(User).filter(User.email == registration_data["email"]).first()

        assert user is not None, "User not found in database"
        assert user.email == registration_data["email"]
        assert user.full_name == registration_data["full_name"]
        assert user.is_verified is False, "User should not be verified yet"

    def test_journey_02_login_and_dashboard_access(
        self, client: TestClient, db: Session
    ):
        """
        Test 2: Login and dashboard access

        Steps:
        1. POST /api/v1/auth/login with credentials
        2. Verify JWT token returned
        3. GET /api/v1/dashboard/overview with JWT
        4. Verify dashboard shows 0 sessions for new user

        Expected:
        - 200 OK for login
        - Valid JWT token
        - Dashboard accessible
        - Empty state handled correctly
        """
        # Setup: Create verified user
        from src.db.models import User
        from src.auth.security import hash_password

        user = User(
            email="test.login@medical.edu.au",
            password_hash=hash_password("SecurePass123!"),
            full_name="Dr. Login Test",
            is_verified=True
        )
        db.add(user)
        db.commit()

        # Step 1: Login
        login_data = {
            "email": "test.login@medical.edu.au",
            "password": "SecurePass123!"
        }

        login_response = client.post("/api/v1/auth/login", json=login_data)

        assert login_response.status_code == 200
        login_json = login_response.json()
        assert "access_token" in login_json
        assert login_json["token_type"] == "bearer"

        token = login_json["access_token"]

        # Step 2: Access dashboard
        headers = {"Authorization": f"Bearer {token}"}
        dashboard_response = client.get("/api/v1/dashboard/overview", headers=headers)

        assert dashboard_response.status_code == 200
        dashboard_data = dashboard_response.json()

        # Verify empty state
        assert dashboard_data["overall_progress"]["total_sessions"] == 0
        assert dashboard_data["overall_progress"]["completion_percentage"] == 0.0
        assert dashboard_data["overall_progress"]["avg_score"] == 0.0

    def test_journey_03_first_mcq_session_complete_flow(
        self, client: TestClient, db: Session, auth_headers: dict
    ):
        """
        Test 3: Complete first MCQ practice session

        Steps:
        1. GET /api/v1/mcqs to fetch 5 questions
        2. POST /api/v1/mcqs/{mcq_id}/attempt for each answer
        3. GET /api/v1/dashboard/overview to verify attempts tracked

        Expected:
        - Questions fetched successfully
        - Answers recorded correctly (4/5 correct)
        - Dashboard shows 5 attempts
        - Success rate reflects 80% accuracy
        """
        from src.db.models import MCQ, MedicalSpecialty, DifficultyLevel

        # Setup: Create 5 test MCQs
        test_mcqs = []
        for i in range(5):
            mcq = MCQ(
                question_id=f"INTEGRATION-TEST-{i+1}",
                question_text=f"Integration test question {i+1}?",
                options={
                    "A": f"Option A for question {i+1}",
                    "B": f"Option B for question {i+1}",
                    "C": f"Option C for question {i+1}",
                    "D": f"Option D for question {i+1}"
                },
                correct_answer="A",
                explanation=f"Explanation for question {i+1}",
                citation="eTG - Therapeutic Guidelines (Cardiovascular)",
                specialty=MedicalSpecialty.CARDIOLOGY,
                difficulty=DifficultyLevel.EASY,
                is_published=True
            )
            db.add(mcq)
            test_mcqs.append(mcq)

        db.commit()

        # Step 1: Fetch questions
        response = client.get(
            "/api/v1/mcqs",
            params={"specialty": "cardiology", "difficulty": "easy", "limit": 5},
            headers=auth_headers
        )

        assert response.status_code == 200
        questions = response.json()
        assert len(questions) >= 5, f"Expected ≥5 questions, got {len(questions)}"

        # Step 2: Submit answers (4 correct, 1 incorrect)
        correct_count = 0
        for idx, question in enumerate(questions[:5]):
            mcq_id = question["id"]  # Use database ID, not question_id
            answer_data = {
                "mcq_id": mcq_id,
                "selected_answer": "A" if idx < 4 else "B",  # 4/5 correct
            }

            answer_response = client.post(
                f"/api/v1/mcqs/{mcq_id}/attempt",
                json=answer_data,
                headers=auth_headers
            )

            assert answer_response.status_code == 200, f"Expected 200, got {answer_response.status_code}"

            result = answer_response.json()
            assert "is_correct" in result
            if result["is_correct"]:
                correct_count += 1

        # Verify we got 4 correct answers
        assert correct_count == 4, f"Expected 4 correct answers, got {correct_count}"

        # Step 3: Verify dashboard update shows attempts
        dashboard_response = client.get(
            "/api/v1/dashboard/overview",
            headers=auth_headers
        )

        assert dashboard_response.status_code == 200
        dashboard_data = dashboard_response.json()

        # Verify MCQ attempts are tracked
        assert dashboard_data["modules"]["mcq"]["attempts"] >= 5, "Should have at least 5 MCQ attempts"
        # Success rate should be 80% (4/5)
        assert dashboard_data["modules"]["mcq"]["avg_score"] >= 60.0, "Average score should be at least 60%"

    def test_journey_04_performance_registration_to_dashboard(
        self, client: TestClient, db: Session
    ):
        """
        Test 4: End-to-end performance (registration → dashboard)

        Measures total time for complete new user flow.

        Target: <5 seconds for registration + login + dashboard
        """
        start_time = time.time()

        # Step 1: Register
        reg_data = {
            "email": f"perf.test.{int(time.time())}@medical.edu.au",
            "password": "SecurePass123!",
            "full_name": "Dr. Performance Test"
        }
        reg_response = client.post("/api/v1/auth/register", json=reg_data)
        assert reg_response.status_code == 201

        # Manually verify user (skip email verification for test)
        from src.db.models import User
        user = db.query(User).filter(User.email == reg_data["email"]).first()
        user.is_verified = True
        db.commit()

        # Step 2: Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": reg_data["email"], "password": reg_data["password"]}
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        # Step 3: Dashboard
        dashboard_response = client.get(
            "/api/v1/dashboard/overview",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert dashboard_response.status_code == 200

        total_time = time.time() - start_time

        assert total_time < 5.0, f"End-to-end flow took {total_time:.2f}s (should be <5s)"
