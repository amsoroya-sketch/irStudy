"""
Unit tests for Mock Exam Orchestrator

Tests:
- Auto-persona selection (16 personas, balanced distribution)
- Exam creation
- Station progression (advance_station)
- Exam completion detection
- Score aggregation
- Pass/fail calculation
- Error handling (insufficient personas, invalid states)

Coverage Target: ≥70%
"""

import pytest
import asyncio
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy.orm import Session

from src.db.models import MockExam, PatientPersona, User, OSCEAttemptAI, OSCEScoreAI
from src.services.mock_exam import MockExamOrchestrator
from src.schemas.mock_exam import MockExamCreateResponse, MockExamStatusResponse


@pytest.fixture
def orchestrator(db_session: Session):
    """Create MockExamOrchestrator instance"""
    return MockExamOrchestrator(db_session)


# ============================================================================
# TESTS: AUTO-PERSONA SELECTION
# ============================================================================


@pytest.mark.asyncio
async def test_auto_select_personas_returns_16(orchestrator, test_user, test_personas):
    """Test that auto_select_personas returns exactly 16 personas"""
    persona_ids = await orchestrator.auto_select_personas(str(test_user.id))

    assert len(persona_ids) == 16
    assert all(isinstance(pid, str) for pid in persona_ids)


@pytest.mark.asyncio
async def test_auto_select_personas_balanced_distribution(orchestrator, test_user, test_personas):
    """Test that personas are balanced across specialties"""
    persona_ids = await orchestrator.auto_select_personas(str(test_user.id))

    # Get specialties of selected personas
    personas = orchestrator.db.query(PatientPersona)\
        .filter(PatientPersona.persona_id.in_(persona_ids))\
        .all()

    specialty_counts = {}
    for persona in personas:
        specialty_counts[persona.specialty] = specialty_counts.get(persona.specialty, 0) + 1

    # Each specialty should have exactly 2 personas
    for specialty in [
        'Cardiology', 'Respiratory', 'Neurology', 'Gastroenterology',
        'Psychiatry', 'Paediatrics', 'Obstetrics & Gynaecology', 'Emergency Medicine'
    ]:
        assert specialty in specialty_counts
        assert specialty_counts[specialty] == 2, f"{specialty} should have 2 personas, got {specialty_counts[specialty]}"


@pytest.mark.asyncio
async def test_auto_select_personas_difficulty_mix(orchestrator, test_user, test_personas):
    """Test that personas include both intermediate and advanced difficulty"""
    persona_ids = await orchestrator.auto_select_personas(str(test_user.id))

    personas = orchestrator.db.query(PatientPersona)\
        .filter(PatientPersona.persona_id.in_(persona_ids))\
        .all()

    difficulty_counts = {}
    for persona in personas:
        difficulty_counts[persona.difficulty_level] = difficulty_counts.get(persona.difficulty_level, 0) + 1

    # Should have mix of intermediate and advanced
    assert 'intermediate' in difficulty_counts
    assert 'advanced' in difficulty_counts

    # Should be roughly balanced (8 of each)
    assert difficulty_counts['intermediate'] >= 6  # Allow some variance
    assert difficulty_counts['advanced'] >= 6


@pytest.mark.asyncio
async def test_auto_select_personas_no_duplicates(orchestrator, test_user, test_personas):
    """Test that no duplicate personas are selected"""
    persona_ids = await orchestrator.auto_select_personas(str(test_user.id))

    assert len(persona_ids) == len(set(persona_ids)), "Duplicate personas found"


@pytest.mark.asyncio
async def test_auto_select_personas_insufficient_personas(orchestrator, test_user, db_session):
    """Test error handling when insufficient personas available"""
    # Create only 10 personas (not enough for 16)
    for i in range(10):
        persona = PatientPersona(
            persona_id=str(uuid4()),
            persona_code=f"TEST-{i:03d}-INSUFFICIENT",
            name=f"Test Insufficient {i}",
            age=50,
            gender="male",
            specialty="Cardiology",
            chief_complaint="Test complaint",
            opening_statement="I have a problem",
            symptoms={},
            medical_history={},
            emotional_profile={},
            difficulty_level="intermediate",
            is_active=True
        )
        db_session.add(persona)

    db_session.commit()

    # Should raise ValueError
    with pytest.raises(ValueError, match="Insufficient personas"):
        await orchestrator.auto_select_personas(str(test_user.id))


# ============================================================================
# TESTS: EXAM CREATION
# ============================================================================


@pytest.mark.asyncio
async def test_create_exam_success(orchestrator, test_user, test_personas):
    """Test successful exam creation"""
    exam = await orchestrator.create_exam(
        user_id=str(test_user.id),
        exam_name="Test Mock Exam"
    )

    assert isinstance(exam, MockExamCreateResponse)
    assert exam.exam_id is not None
    assert len(exam.stations_config) == 16
    assert exam.estimated_duration_minutes == 150
    assert "/station/1" in exam.start_url

    # Verify database record created
    db_exam = orchestrator.db.query(MockExam)\
        .filter(MockExam.exam_id == exam.exam_id)\
        .first()

    assert db_exam is not None
    assert db_exam.user_id == str(test_user.id)
    assert db_exam.exam_state == 'IN_PROGRESS'
    assert db_exam.current_station_number == 1
    assert db_exam.total_score == 0


@pytest.mark.asyncio
async def test_create_exam_custom_name(orchestrator, test_user, test_personas):
    """Test exam creation with custom name"""
    custom_name = "AMC Practice Exam #1"

    exam = await orchestrator.create_exam(
        user_id=str(test_user.id),
        exam_name=custom_name
    )

    db_exam = orchestrator.db.query(MockExam)\
        .filter(MockExam.exam_id == exam.exam_id)\
        .first()

    assert db_exam.exam_name == custom_name


@pytest.mark.asyncio
async def test_create_exam_invalid_user(orchestrator, test_personas):
    """Test exam creation with invalid user ID"""
    # Use valid UUID format but non-existent user
    invalid_user_id = str(uuid4())

    with pytest.raises(ValueError, match="User.*not found"):
        await orchestrator.create_exam(
            user_id=invalid_user_id,
            exam_name="Test"
        )


# ============================================================================
# TESTS: EXAM STATUS
# ============================================================================


@pytest.mark.asyncio
async def test_get_exam_status_in_progress(orchestrator, test_user, test_personas):
    """Test getting status of in-progress exam"""
    # Create exam
    exam = await orchestrator.create_exam(str(test_user.id))

    # Get status
    status = await orchestrator.get_exam_status(exam.exam_id, str(test_user.id))

    assert isinstance(status, MockExamStatusResponse)
    assert status.exam_id == exam.exam_id
    assert status.exam_state == 'IN_PROGRESS'
    assert status.current_station_number == 1
    assert status.stations_completed == 0
    assert status.total_score == 0
    assert status.time_elapsed_minutes is not None
    assert status.started_at is not None
    assert status.completed_at is None


@pytest.mark.asyncio
async def test_get_exam_status_not_found(orchestrator, test_user):
    """Test getting status of non-existent exam"""
    with pytest.raises(ValueError, match="not found"):
        await orchestrator.get_exam_status("invalid-exam-id", str(test_user.id))


@pytest.mark.asyncio
async def test_get_exam_status_unauthorized(orchestrator, test_user, test_personas, db_session):
    """Test getting status with different user (authorization check)"""
    from src.auth.security import hash_password

    # Create exam with test_user
    exam = await orchestrator.create_exam(str(test_user.id))

    # Create another user
    other_user = User(
        email="other_user@example.com",
        password_hash=hash_password("TestPassword123!"),
        full_name="Other User",
        is_active=True,
        is_verified=True
    )
    db_session.add(other_user)
    db_session.commit()
    db_session.refresh(other_user)

    # Try to access exam with other user
    with pytest.raises(ValueError, match="not authorized"):
        await orchestrator.get_exam_status(exam.exam_id, str(other_user.id))


# ============================================================================
# TESTS: STATION PROGRESSION
# ============================================================================


@pytest.mark.asyncio
async def test_advance_station_success(orchestrator, test_user, test_personas):
    """Test advancing from station 1 to station 2"""
    # Create exam
    exam = await orchestrator.create_exam(str(test_user.id))

    # Complete station 1
    result = await orchestrator.advance_station(
        exam_id=exam.exam_id,
        station_number=1,
        station_score=12,
        pass_fail='PASS',
        user_id=str(test_user.id)
    )

    assert result.next_station_number == 2
    assert result.station_score == 12
    assert result.overall_progress == 1/16
    assert result.exam_complete is False
    assert result.total_score == 12

    # Verify database updated
    db_exam = orchestrator.db.query(MockExam)\
        .filter(MockExam.exam_id == exam.exam_id)\
        .first()

    assert db_exam.current_station_number == 2
    assert db_exam.total_score == 12
    assert db_exam.stations_passed == 1


@pytest.mark.asyncio
async def test_advance_station_fail(orchestrator, test_user, test_personas):
    """Test advancing station with FAIL status"""
    exam = await orchestrator.create_exam(str(test_user.id))

    result = await orchestrator.advance_station(
        exam_id=exam.exam_id,
        station_number=1,
        station_score=6,
        pass_fail='FAIL',
        user_id=str(test_user.id)
    )

    assert result.next_station_number == 2
    assert result.station_score == 6
    assert result.total_score == 6

    # Verify stations_passed not incremented
    db_exam = orchestrator.db.query(MockExam)\
        .filter(MockExam.exam_id == exam.exam_id)\
        .first()

    assert db_exam.stations_passed == 0


@pytest.mark.asyncio
async def test_advance_station_complete_exam(orchestrator, test_user, test_personas):
    """Test completing station 16 (exam completion)"""
    # Create exam
    exam = await orchestrator.create_exam(str(test_user.id))

    # Fast-forward to station 16
    db_exam = orchestrator.db.query(MockExam)\
        .filter(MockExam.exam_id == exam.exam_id)\
        .first()
    db_exam.current_station_number = 16
    db_exam.total_score = 186  # 15 stations × 12 points (below pass threshold)
    db_exam.stations_passed = 15
    orchestrator.db.commit()

    # Complete station 16
    result = await orchestrator.advance_station(
        exam_id=exam.exam_id,
        station_number=16,
        station_score=12,
        pass_fail='PASS',
        user_id=str(test_user.id)
    )

    assert result.next_station_number is None
    assert result.exam_complete is True
    assert result.total_score == 198  # 186 + 12 = 198 (exactly at pass threshold)
    assert result.overall_progress == 1.0

    # Verify exam marked complete
    db_exam = orchestrator.db.query(MockExam)\
        .filter(MockExam.exam_id == exam.exam_id)\
        .first()

    assert db_exam.exam_state == 'COMPLETED'
    assert db_exam.completed_at is not None
    assert db_exam.total_duration_minutes is not None
    assert db_exam.overall_pass is True  # 198/240 = 82.5% (pass)


@pytest.mark.asyncio
async def test_advance_station_exam_fail(orchestrator, test_user, test_personas):
    """Test exam completion with failing score"""
    exam = await orchestrator.create_exam(str(test_user.id))

    # Fast-forward to station 16 with low score
    db_exam = orchestrator.db.query(MockExam)\
        .filter(MockExam.exam_id == exam.exam_id)\
        .first()
    db_exam.current_station_number = 16
    db_exam.total_score = 160  # Low score
    db_exam.stations_passed = 10
    orchestrator.db.commit()

    # Complete station 16
    result = await orchestrator.advance_station(
        exam_id=exam.exam_id,
        station_number=16,
        station_score=10,
        pass_fail='PASS',
        user_id=str(test_user.id)
    )

    assert result.exam_complete is True
    assert result.total_score == 170  # 160 + 10 = 170 (below pass threshold of 198)

    # Verify exam failed
    db_exam = orchestrator.db.query(MockExam)\
        .filter(MockExam.exam_id == exam.exam_id)\
        .first()

    assert db_exam.overall_pass is False  # 170/240 = 70.8% (fail)


@pytest.mark.asyncio
async def test_advance_station_wrong_state(orchestrator, test_user, test_personas):
    """Test advancing station on completed exam (invalid state)"""
    exam = await orchestrator.create_exam(str(test_user.id))

    # Mark exam as completed
    db_exam = orchestrator.db.query(MockExam)\
        .filter(MockExam.exam_id == exam.exam_id)\
        .first()
    db_exam.exam_state = 'COMPLETED'
    orchestrator.db.commit()

    # Try to advance station
    with pytest.raises(ValueError, match="not in progress"):
        await orchestrator.advance_station(
            exam_id=exam.exam_id,
            station_number=1,
            station_score=12,
            pass_fail='PASS',
            user_id=str(test_user.id)
        )


# ============================================================================
# TESTS: EXAM RESULTS
# ============================================================================


@pytest.mark.asyncio
async def test_get_exam_results_not_completed(orchestrator, test_user, test_personas):
    """Test getting results of incomplete exam"""
    exam = await orchestrator.create_exam(str(test_user.id))

    with pytest.raises(ValueError, match="not completed"):
        await orchestrator.get_exam_results(exam.exam_id, str(test_user.id))


@pytest.mark.asyncio
async def test_get_exam_results_success(orchestrator, test_user, test_personas, db_session):
    """Test getting comprehensive exam results after completion"""
    # Create exam
    exam = await orchestrator.create_exam(str(test_user.id))

    # Create 16 mock attempts and scores
    persona_ids = exam.stations_config
    total_score = 0

    for i in range(16):
        attempt = OSCEAttemptAI(
            attempt_id=str(uuid4()),
            user_id=str(test_user.id),
            persona_id=persona_ids[i].persona_id,
            mock_exam_id=exam.exam_id,
            session_type='mock_exam',
            station_number=i + 1,
            started_at=datetime.now(timezone.utc),
            ended_at=datetime.now(timezone.utc),
            was_completed=True
        )
        db_session.add(attempt)
        db_session.flush()

        # Create score (alternating PASS/FAIL for variety)
        # Station score should be 12 or 10 - distribute across 5 domains
        if i % 2 == 0:
            # 12 total: 3+3+3+2+1 = 12
            comm, clin, info, mgmt, prof = 3, 3, 3, 2, 1
            station_score = 12
        else:
            # 10 total: 3+3+2+1+1 = 10
            comm, clin, info, mgmt, prof = 3, 3, 2, 1, 1
            station_score = 10

        total_score += station_score

        score = OSCEScoreAI(
            score_id=str(uuid4()),
            attempt_id=attempt.attempt_id,
            communication_score=comm,
            clinical_reasoning_score=clin,
            information_gathering_score=info,
            management_score=mgmt,
            professionalism_score=prof
            # total_score and pass_fail are GENERATED columns
        )
        db_session.add(score)

    # Mark exam as completed
    db_exam = orchestrator.db.query(MockExam)\
        .filter(MockExam.exam_id == exam.exam_id)\
        .first()
    db_exam.exam_state = 'COMPLETED'
    db_exam.total_score = total_score
    db_exam.stations_passed = 16
    db_exam.completed_at = datetime.now(timezone.utc)
    db_exam.total_duration_minutes = 148
    db_exam.overall_pass = (total_score >= 198)

    db_session.commit()

    # Get results
    results = await orchestrator.get_exam_results(exam.exam_id, str(test_user.id))

    assert results.exam_id == exam.exam_id
    assert results.overall_score == total_score
    assert results.max_score == 240
    assert len(results.stations) == 16
    assert results.summary_statistics.stations_passed == 16
    assert results.total_duration_minutes == 148
    assert results.completed_at is not None


# ============================================================================
# TESTS: SCORE AGGREGATION
# ============================================================================


@pytest.mark.asyncio
async def test_score_aggregation_multiple_stations(orchestrator, test_user, test_personas):
    """Test that scores aggregate correctly across multiple stations"""
    exam = await orchestrator.create_exam(str(test_user.id))

    # Complete 5 stations with different scores
    scores = [12, 10, 13, 9, 14]

    for i, score in enumerate(scores):
        await orchestrator.advance_station(
            exam_id=exam.exam_id,
            station_number=i + 1,
            station_score=score,
            pass_fail='PASS' if score >= 9 else 'FAIL',
            user_id=str(test_user.id)
        )

    # Verify total score
    db_exam = orchestrator.db.query(MockExam)\
        .filter(MockExam.exam_id == exam.exam_id)\
        .first()

    assert db_exam.total_score == sum(scores)
    assert db_exam.stations_passed == 5  # All passed (≥9)


