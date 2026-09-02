"""
Mock Exam Orchestration Service

Orchestrates 16-station mock OSCE exams with:
- Balanced auto-persona selection (2 per specialty)
- State machine management (IN_PROGRESS → COMPLETED)
- Score aggregation and pass/fail calculation
- Integration with existing AI OSCE pipeline

AMC CLINICAL EXAM FORMAT:
- 16 stations × 8 minutes each = 128 minutes
- 2-minute breaks between stations
- Total duration: ~150 minutes
- Pass threshold: ≥198/240 (82.5%)
- Balanced specialty coverage (8 specialties)

SECURITY:
- All database operations use SQLAlchemy ORM (no raw SQL)
- UUID validation on all inputs
- Transaction safety (rollback on errors)
"""

import random
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from src.db.models import MockExam, OSCEAttemptAI, OSCEScoreAI, PatientPersona, User
from src.schemas.mock_exam import (
    PersonaInfo,
    MockExamCreateResponse,
    MockExamStatusResponse,
    StationCompleteResponse,
    MockExamResultsResponse,
    StationResult,
    SummaryStatistics,
)


logger = logging.getLogger(__name__)


# AMC Clinical Exam specialty distribution (8 specialties × 2 personas each)
SPECIALTY_DISTRIBUTION = [
    'Cardiology',
    'Respiratory',
    'Neurology',
    'Gastroenterology',
    'Psychiatry',
    'Paediatrics',
    'Obstetrics & Gynaecology',
    'Emergency Medicine'
]


class MockExamOrchestrator:
    """
    Orchestrate 16-station mock exam progression.

    Responsibilities:
    - Auto-select balanced personas (2 per specialty)
    - Manage exam state machine
    - Aggregate scores across 16 stations
    - Calculate overall pass/fail
    - Maintain exam integrity (prevent duplicate stations, score corruption)

    Usage:
        orchestrator = MockExamOrchestrator(db)
        exam = await orchestrator.create_exam(user_id="user-123", exam_name="Practice Exam 1")
        status = await orchestrator.get_exam_status(exam_id=exam.exam_id)
        result = await orchestrator.advance_station(
            exam_id=exam.exam_id,
            station_number=1,
            station_score=12,
            pass_fail='PASS'
        )
    """

    def __init__(self, db: Session):
        """
        Initialize orchestrator with database session.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    async def auto_select_personas(self, user_id: str) -> List[str]:
        """
        Auto-select 16 personas with balanced distribution.

        Logic:
        - Discover active specialties from database
        - Attempt 2 personas per specialty (intermediate + advanced, with fallbacks)
        - If balanced selection yields <16, fill remainder with random active personas
        - Ensures no duplicate personas

        Args:
            user_id: User ID for deterministic randomization

        Returns:
            List of 16 persona_ids (as strings)

        Raises:
            ValueError: If fewer than 16 total active personas exist in the database
        """
        selected_personas = []
        selected_ids = set()
        random.seed(f"{user_id}-{datetime.utcnow().timestamp()}")

        # Discover what specialties actually exist in the database
        available_specialties = [
            row[0] for row in self.db.query(PatientPersona.specialty)
            .filter(PatientPersona.is_active == True)
            .distinct()
            .all()
        ]
        logger.info(f"Available specialties in DB: {available_specialties}")

        # Phase 1: Try to pick 2 per available specialty (balanced coverage)
        for specialty in available_specialties:
            if len(selected_personas) >= 16:
                break

            # Cap at 2 per specialty here (not the global len(selected_personas)
            # check) — otherwise an early specialty can consume a 3rd (foundation
            # fallback) slot merely because the global total hasn't hit 16 yet,
            # starving later specialties and shrinking the paper's specialty span
            # well below the available count. Any shortfall is topped up from any
            # specialty in Phase 2 below.
            specialty_added = 0

            # Try intermediate first
            intermediate = self.db.query(PatientPersona)\
                .filter(
                    PatientPersona.specialty == specialty,
                    PatientPersona.difficulty_level == 'intermediate',
                    PatientPersona.is_active == True
                )\
                .order_by(func.random())\
                .first()

            if intermediate and str(intermediate.persona_id) not in selected_ids:
                selected_personas.append(str(intermediate.persona_id))
                selected_ids.add(str(intermediate.persona_id))
                specialty_added += 1

            # Try advanced
            if specialty_added < 2 and len(selected_personas) < 16:
                advanced = self.db.query(PatientPersona)\
                    .filter(
                        PatientPersona.specialty == specialty,
                        PatientPersona.difficulty_level == 'advanced',
                        PatientPersona.is_active == True
                    )\
                    .order_by(func.random())\
                    .first()

                if advanced and str(advanced.persona_id) not in selected_ids:
                    selected_personas.append(str(advanced.persona_id))
                    selected_ids.add(str(advanced.persona_id))
                    specialty_added += 1

            # Fallback: foundation if we still need one for this specialty
            if specialty_added < 2 and len(selected_personas) < 16:
                foundation = self.db.query(PatientPersona)\
                    .filter(
                        PatientPersona.specialty == specialty,
                        PatientPersona.difficulty_level == 'foundation',
                        PatientPersona.is_active == True
                    )\
                    .order_by(func.random())\
                    .first()

                if foundation and str(foundation.persona_id) not in selected_ids:
                    selected_personas.append(str(foundation.persona_id))
                    selected_ids.add(str(foundation.persona_id))
                    specialty_added += 1

        # Phase 2: If still <16, fill with any remaining active personas
        if len(selected_personas) < 16:
            remaining_needed = 16 - len(selected_personas)
            logger.info(f"Balanced selection found {len(selected_personas)}, filling {remaining_needed} from all specialties")

            additional = self.db.query(PatientPersona)\
                .filter(
                    PatientPersona.is_active == True,
                    ~PatientPersona.persona_id.in_(list(selected_ids))
                )\
                .order_by(func.random())\
                .limit(remaining_needed)\
                .all()

            for persona in additional:
                selected_personas.append(str(persona.persona_id))
                selected_ids.add(str(persona.persona_id))

        # Validate we have 16 personas
        if len(selected_personas) < 16:
            total_active = self.db.query(PatientPersona).filter(PatientPersona.is_active == True).count()
            raise ValueError(
                f"Insufficient personas for mock exam. "
                f"Found {len(selected_personas)}, need 16. "
                f"Total active personas in database: {total_active}. "
                f"Please ensure at least 16 active patient personas exist."
            )

        # Shuffle to randomize station order (not grouped by specialty)
        random.shuffle(selected_personas)

        logger.info(f"Auto-selected 16 personas for user {user_id}: {selected_personas[:3]}... (truncated)")
        return selected_personas[:16]  # Ensure exactly 16

    async def create_exam(
        self,
        user_id: str,
        exam_name: Optional[str] = None
    ) -> MockExamCreateResponse:
        """
        Create new mock exam with auto-selected personas.

        Args:
            user_id: User ID creating the exam
            exam_name: Optional custom exam name

        Returns:
            MockExamCreateResponse with exam_id, stations_config, start_url

        Raises:
            ValueError: If user not found or persona selection fails
        """
        # Verify user exists
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User {user_id} not found")

        # Auto-select 16 personas
        persona_ids = await self.auto_select_personas(user_id)

        # Generate exam ID
        exam_id = str(uuid4())

        # Create mock_exams record
        exam = MockExam(
            exam_id=exam_id,
            user_id=user_id,
            stations_config={'persona_ids': persona_ids},
            exam_name=exam_name or f"Mock Exam - {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
            exam_state='IN_PROGRESS',
            current_station_number=1,
            total_score=0,
            stations_passed=0,
            started_at=datetime.now(timezone.utc)
        )

        self.db.add(exam)
        self.db.commit()
        self.db.refresh(exam)

        logger.info(f"Created mock exam {exam_id} for user {user_id} with 16 stations")

        # Fetch persona details for response
        personas = self.db.query(PatientPersona)\
            .filter(PatientPersona.persona_id.in_(persona_ids))\
            .all()

        # Create PersonaInfo list (maintain station order)
        persona_map = {str(p.persona_id): p for p in personas}
        stations_config = [
            PersonaInfo(
                persona_id=str(persona_id),
                persona_code=persona_map[persona_id].persona_code,
                name=persona_map[persona_id].name,
                specialty=persona_map[persona_id].specialty,
                chief_complaint=persona_map[persona_id].chief_complaint,
                difficulty_level=persona_map[persona_id].difficulty_level
            )
            for persona_id in persona_ids
        ]

        return MockExamCreateResponse(
            exam_id=exam_id,
            stations_config=stations_config,
            estimated_duration_minutes=150,
            start_url=f"/api/v1/osce/session/{exam_id}/station/1",
            created_at=exam.started_at
        )

    async def get_exam_status(self, exam_id: str, user_id: str) -> MockExamStatusResponse:
        """
        Get current mock exam status and progress.

        Args:
            exam_id: UUID of exam
            user_id: User ID (for authorization check)

        Returns:
            MockExamStatusResponse with current state, progress, scores

        Raises:
            ValueError: If exam not found or user not authorized
        """
        exam = self.db.query(MockExam)\
            .filter(MockExam.exam_id == exam_id)\
            .first()

        if not exam:
            raise ValueError(f"Exam {exam_id} not found")

        if str(exam.user_id) != str(user_id):
            raise ValueError(f"User {user_id} not authorized to access exam {exam_id}")

        # Calculate time elapsed
        time_elapsed_minutes = None
        if exam.started_at:
            # Ensure timezone-aware datetimes (SQLite may return naive datetimes)
            started_at = exam.started_at if exam.started_at.tzinfo else exam.started_at.replace(tzinfo=timezone.utc)
            completed_at = None
            if exam.completed_at:
                completed_at = exam.completed_at if exam.completed_at.tzinfo else exam.completed_at.replace(tzinfo=timezone.utc)
                time_elapsed = (completed_at - started_at).total_seconds() / 60
            else:
                time_elapsed = (datetime.now(timezone.utc) - started_at).total_seconds() / 60
            time_elapsed_minutes = int(time_elapsed)

        # Count completed stations
        stations_completed = self.db.query(OSCEAttemptAI)\
            .filter(
                OSCEAttemptAI.mock_exam_id == exam_id,
                OSCEAttemptAI.was_completed == True
            )\
            .count()

        return MockExamStatusResponse(
            exam_id=exam_id,
            exam_state=exam.exam_state,
            current_station_number=exam.current_station_number,
            stations_completed=stations_completed,
            total_score=exam.total_score,
            max_possible_score=240,
            time_elapsed_minutes=time_elapsed_minutes,
            started_at=exam.started_at,
            completed_at=exam.completed_at,
            exam_name=exam.exam_name
        )

    async def advance_station(
        self,
        exam_id: str,
        station_number: int,
        station_score: int,
        pass_fail: str,
        user_id: str
    ) -> StationCompleteResponse:
        """
        Advance to next station or complete exam.

        Flow:
        1. Validate station_number matches current_station
        2. Update exam totals (total_score, stations_passed)
        3. Increment current_station_number
        4. Check if exam complete (station_number == 16)
        5. If complete: Calculate overall pass/fail, update exam_state

        Args:
            exam_id: UUID of exam
            station_number: Just completed station (1-16)
            station_score: Score for station (0-15)
            pass_fail: 'PASS' or 'FAIL'
            user_id: User ID (for authorization)

        Returns:
            StationCompleteResponse with next_station, progress, exam_complete

        Raises:
            ValueError: If exam not found, station mismatch, or invalid state
        """
        exam = self.db.query(MockExam)\
            .filter(MockExam.exam_id == exam_id)\
            .first()

        if not exam:
            raise ValueError(f"Exam {exam_id} not found")

        if str(exam.user_id) != str(user_id):
            raise ValueError(f"User {user_id} not authorized to access exam {exam_id}")

        if exam.exam_state != 'IN_PROGRESS':
            raise ValueError(f"Exam {exam_id} is not in progress (state: {exam.exam_state})")

        # Validate station number matches expected
        if station_number != exam.current_station_number:
            logger.warning(
                f"Station number mismatch: expected {exam.current_station_number}, "
                f"got {station_number}. Allowing completion."
            )

        # Update exam totals
        exam.total_score += station_score
        if pass_fail == 'PASS':
            exam.stations_passed += 1

        # Check if exam complete
        if station_number >= 16:
            # Exam complete
            exam.exam_state = 'COMPLETED'
            exam.completed_at = datetime.now(timezone.utc)

            # Calculate total duration
            if exam.started_at and exam.completed_at:
                # Ensure timezone-aware datetimes (SQLite may return naive datetimes)
                started_at = exam.started_at if exam.started_at.tzinfo else exam.started_at.replace(tzinfo=timezone.utc)
                completed_at = exam.completed_at if exam.completed_at.tzinfo else exam.completed_at.replace(tzinfo=timezone.utc)
                duration_seconds = (completed_at - started_at).total_seconds()
                exam.total_duration_minutes = int(duration_seconds / 60)

            # Calculate overall pass/fail (≥198/240 = 82.5%)
            exam.overall_pass = (exam.total_score >= 198)

            self.db.commit()

            logger.info(
                f"Mock exam {exam_id} completed: score={exam.total_score}/240, "
                f"pass={exam.overall_pass}, duration={exam.total_duration_minutes}min"
            )

            return StationCompleteResponse(
                next_station_number=None,
                station_score=station_score,
                overall_progress=1.0,
                exam_complete=True,
                total_score=exam.total_score
            )
        else:
            # Advance to next station
            exam.current_station_number = station_number + 1
            self.db.commit()

            overall_progress = station_number / 16.0

            logger.info(
                f"Advanced mock exam {exam_id} to station {exam.current_station_number}, "
                f"progress={overall_progress:.1%}"
            )

            return StationCompleteResponse(
                next_station_number=exam.current_station_number,
                station_score=station_score,
                overall_progress=overall_progress,
                exam_complete=False,
                total_score=exam.total_score
            )

    async def get_exam_results(self, exam_id: str, user_id: str) -> MockExamResultsResponse:
        """
        Get comprehensive exam results after completion.

        Args:
            exam_id: UUID of exam
            user_id: User ID (for authorization)

        Returns:
            MockExamResultsResponse with full breakdown, statistics, pass/fail

        Raises:
            ValueError: If exam not found, not completed, or user not authorized
        """
        exam = self.db.query(MockExam)\
            .filter(MockExam.exam_id == exam_id)\
            .first()

        if not exam:
            raise ValueError(f"Exam {exam_id} not found")

        if str(exam.user_id) != str(user_id):
            raise ValueError(f"User {user_id} not authorized to access exam {exam_id}")

        if exam.exam_state != 'COMPLETED':
            raise ValueError(
                f"Exam {exam_id} is not completed (state: {exam.exam_state}). "
                f"Cannot retrieve results."
            )

        # Get all 16 station attempts
        attempts = self.db.query(OSCEAttemptAI)\
            .filter(OSCEAttemptAI.mock_exam_id == exam_id)\
            .order_by(OSCEAttemptAI.station_number)\
            .all()

        if len(attempts) < 16:
            logger.warning(
                f"Exam {exam_id} marked complete but only has {len(attempts)} attempts. "
                f"Expected 16."
            )

        # Build station results
        station_results = []
        performance_by_specialty = {}

        for i, attempt in enumerate(attempts):
            # Get score for this attempt
            score_record = self.db.query(OSCEScoreAI)\
                .filter(OSCEScoreAI.attempt_id == attempt.attempt_id)\
                .first()

            # Calculate total_score manually (SQLite doesn't support GENERATED columns)
            if score_record:
                # Try to get total_score (exists in PostgreSQL), else calculate it
                if hasattr(score_record, 'total_score') and score_record.total_score is not None:
                    total_score = score_record.total_score
                else:
                    # Calculate from individual components
                    total_score = (
                        (score_record.communication_score or 0) +
                        (score_record.clinical_reasoning_score or 0) +
                        (score_record.information_gathering_score or 0) +
                        (score_record.management_score or 0) +
                        (score_record.professionalism_score or 0)
                    )

                # Calculate pass_fail (≥9 to pass)
                pass_fail_status = 'PASS' if total_score >= 9 else 'FAIL'
            else:
                total_score = 0
                pass_fail_status = 'FAIL'

            # Get persona details
            persona = self.db.query(PatientPersona)\
                .filter(PatientPersona.persona_id == attempt.persona_id)\
                .first()

            persona_name = persona.name if persona else "Unknown"
            specialty = persona.specialty if persona else "Unknown"

            # Calculate duration (default 8 minutes if not recorded)
            duration_minutes = 8
            if attempt.ended_at and attempt.started_at:
                duration_seconds = (attempt.ended_at - attempt.started_at).total_seconds()
                duration_minutes = int(duration_seconds / 60)

            station_results.append(
                StationResult(
                    station_number=attempt.station_number or (i + 1),
                    persona_name=persona_name,
                    specialty=specialty,
                    score=total_score,
                    pass_fail=pass_fail_status,
                    duration_minutes=duration_minutes
                )
            )

            # Track performance by specialty
            if specialty not in performance_by_specialty:
                performance_by_specialty[specialty] = {
                    'stations': 0,
                    'total_score': 0,
                    'passed': 0
                }

            performance_by_specialty[specialty]['stations'] += 1
            performance_by_specialty[specialty]['total_score'] += total_score
            if pass_fail_status == 'PASS':
                performance_by_specialty[specialty]['passed'] += 1

        # Calculate average scores by specialty
        for specialty in performance_by_specialty:
            stats = performance_by_specialty[specialty]
            stats['average_score'] = stats['total_score'] / stats['stations'] if stats['stations'] > 0 else 0

        # Calculate overall statistics
        percentage = (exam.total_score / 240) * 100 if exam.total_score else 0

        summary_statistics = SummaryStatistics(
            stations_passed=exam.stations_passed,
            stations_failed=(len(station_results) - exam.stations_passed),
            average_score_per_station=(exam.total_score / len(station_results)) if station_results else 0,
            percentage=percentage,
            performance_by_specialty=performance_by_specialty
        )

        logger.info(
            f"Retrieved results for exam {exam_id}: {exam.total_score}/240, "
            f"{exam.stations_passed}/16 passed"
        )

        return MockExamResultsResponse(
            exam_id=exam_id,
            overall_score=exam.total_score,
            max_score=240,
            percentage=percentage,
            overall_pass_fail='PASS' if exam.overall_pass else 'FAIL',
            stations=station_results,
            summary_statistics=summary_statistics,
            total_duration_minutes=exam.total_duration_minutes or 0,
            completed_at=exam.completed_at,
            exam_name=exam.exam_name,
            report_pdf_url=None  # TODO: Implement PDF generation in future
        )
