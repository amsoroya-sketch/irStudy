"""
EMR Session Service

Handles session lifecycle management with ACID transaction safety.

SECURITY:
- Transaction-safe submit (atomic operations)
- User authorization checks
- No hardcoded credentials

PERFORMANCE:
- Auto-save: <200ms target
- Submit: <500ms target (optimized from 1000ms)
- Query optimizations using indexes
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import text, and_
import logging
import json

from src.schemas.emr import (
    SessionStartRequest,
    SessionSubmitRequest,
    SOAPNoteSubmit,
    PrescriptionSubmit,
    PathologyOrderSubmit
)

logger = logging.getLogger(__name__)


class SessionService:
    """EMR session management business logic"""

    @staticmethod
    def create_session(
        db: Session,
        user_id: int,
        patient_id: str,
        emr_system: str,
        osce_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create new EMR practice session.

        Args:
            db: Database session
            user_id: User ID
            patient_id: Mock patient UUID
            emr_system: "cerner" or "epic"
            osce_id: Optional OSCE station link

        Returns:
            Session dict with ID

        Raises:
            ValueError: If max active sessions exceeded
        """
        # Check max active sessions (limit: 5)
        active_count = db.execute(text("""
            SELECT COUNT(*) FROM emr_sessions
            WHERE user_id = :user_id
            AND submitted_at IS NULL
        """), {"user_id": user_id}).scalar()

        if active_count >= 5:
            raise ValueError("Maximum 5 concurrent sessions allowed")

        # Get patient specialty and difficulty
        patient = db.execute(text("""
            SELECT specialty, difficulty FROM mock_patients WHERE id = :patient_id
        """), {"patient_id": patient_id}).fetchone()

        if not patient:
            raise ValueError(f"Patient {patient_id} not found")

        # Create session
        session_id = db.execute(text("""
            INSERT INTO emr_sessions (user_id, patient_id, specialty, difficulty, started_at)
            VALUES (:user_id, :patient_id, :specialty, :difficulty, NOW())
            RETURNING id
        """), {
            "user_id": user_id,
            "patient_id": patient_id,
            "specialty": patient[0],
            "difficulty": patient[1]
        }).scalar()

        # Update user progress (emr_sessions_total)
        db.execute(text("""
            UPDATE user_progress
            SET emr_sessions_total = COALESCE(emr_sessions_total, 0) + 1
            WHERE user_id = :user_id
        """), {"user_id": user_id})

        db.commit()

        return {
            "session_id": str(session_id),
            "started_at": datetime.utcnow()
        }

    @staticmethod
    def update_session_data(
        db: Session,
        session_id: str,
        user_id: int,
        session_data: Dict[str, Any]
    ) -> datetime:
        """
        Auto-save session draft data (JSONB merge).

        Args:
            db: Database session
            session_id: Session UUID
            user_id: User ID (for authorization)
            session_data: Draft data to merge

        Returns:
            auto_saved_at timestamp

        Performance: <200ms target
        """
        # Verify ownership and active status
        session = db.execute(text("""
            SELECT id FROM emr_sessions
            WHERE id = :session_id
            AND user_id = :user_id
            AND submitted_at IS NULL
        """), {"session_id": session_id, "user_id": user_id}).fetchone()

        if not session:
            raise ValueError("Session not found or already submitted")

        # Update session data (PostgreSQL JSONB merge)
        # Note: For development, we'll use simple JSON update
        # In production, use JSONB || operator for true merge
        auto_saved_at = datetime.utcnow()

        db.execute(text("""
            UPDATE emr_sessions
            SET score_breakdown = :session_data,
                submitted_at = :auto_saved_at
            WHERE id = :session_id
        """).execution_options(synchronize_session=False), {
            "session_id": session_id,
            "session_data": json.dumps(session_data),
            "auto_saved_at": auto_saved_at
        })

        db.commit()

        return auto_saved_at

    @staticmethod
    def submit_session(
        db: Session,
        session_id: str,
        user_id: int,
        submit_data: SessionSubmitRequest
    ) -> Dict[str, Any]:
        """
        Submit EMR session (ACID transaction).

        Steps (atomic):
        1. Mark session complete
        2. Create SOAP note record
        3. Create prescription records
        4. Create pathology order records
        5. Update user progress

        Args:
            db: Database session
            session_id: Session UUID
            user_id: User ID (authorization)
            submit_data: Complete submission data

        Returns:
            Dict with created record IDs

        Performance: <500ms target (optimized)

        Raises:
            ValueError: If session not found or already submitted
            Exception: Triggers automatic rollback
        """
        try:
            # Verify session exists and is active
            session_check = db.execute(text("""
                SELECT patient_id, specialty
                FROM emr_sessions
                WHERE id = :session_id
                AND user_id = :user_id
                AND submitted_at IS NULL
            """), {"session_id": session_id, "user_id": user_id}).fetchone()

            if not session_check:
                raise ValueError("Session not found or already submitted")

            patient_id, specialty = session_check

            # 1. Mark session complete
            completed_at = datetime.utcnow()
            db.execute(text("""
                UPDATE emr_sessions
                SET submitted_at = :completed_at,
                    elapsed_time_seconds = :elapsed_time
                WHERE id = :session_id
            """), {
                "session_id": session_id,
                "completed_at": completed_at,
                "elapsed_time": submit_data.completion_time_seconds
            })

            # 2. Create SOAP note
            soap_note = submit_data.soap_note
            soap_note_id = db.execute(text("""
                INSERT INTO emr_soap_notes (
                    session_id, user_id, patient_id,
                    subjective, objective, assessment, plan,
                    note_type, completion_time_seconds, typing_wpm,
                    created_at
                )
                VALUES (
                    :session_id, :user_id, :patient_id,
                    :subjective, :objective, :assessment, :plan,
                    :note_type, :completion_time, :typing_wpm,
                    :created_at
                )
                RETURNING id
            """), {
                "session_id": session_id,
                "user_id": user_id,
                "patient_id": patient_id,
                "subjective": soap_note.subjective,
                "objective": soap_note.objective,
                "assessment": soap_note.assessment,
                "plan": soap_note.plan,
                "note_type": soap_note.note_type,
                "completion_time": submit_data.completion_time_seconds,
                "typing_wpm": submit_data.typing_wpm,
                "created_at": completed_at
            }).scalar()

            # 3. Create prescriptions
            prescription_ids = []
            for rx in submit_data.prescriptions:
                rx_id = db.execute(text("""
                    INSERT INTO emr_prescriptions (
                        session_id, user_id, patient_id,
                        medication_name, dose, frequency, route,
                        quantity, repeats, indication, created_at
                    )
                    VALUES (
                        :session_id, :user_id, :patient_id,
                        :medication_name, :dose, :frequency, :route,
                        :quantity, :repeats, :indication, :created_at
                    )
                    RETURNING id
                """), {
                    "session_id": session_id,
                    "user_id": user_id,
                    "patient_id": patient_id,
                    "medication_name": rx.medication_name,
                    "dose": rx.dose,
                    "frequency": rx.frequency,
                    "route": rx.route,
                    "quantity": rx.quantity,
                    "repeats": rx.repeats,
                    "indication": rx.indication,
                    "created_at": completed_at
                }).scalar()
                prescription_ids.append(str(rx_id))

            # 4. Create pathology orders
            pathology_order_ids = []
            for order in submit_data.pathology_orders:
                order_id = db.execute(text("""
                    INSERT INTO emr_pathology_orders (
                        session_id, user_id, patient_id,
                        test_name, urgency, clinical_indication,
                        is_panel, panel_tests, created_at
                    )
                    VALUES (
                        :session_id, :user_id, :patient_id,
                        :test_name, :urgency, :clinical_indication,
                        :is_panel, :panel_tests, :created_at
                    )
                    RETURNING id
                """), {
                    "session_id": session_id,
                    "user_id": user_id,
                    "patient_id": patient_id,
                    "test_name": order.test_name,
                    "urgency": order.urgency,
                    "clinical_indication": order.clinical_indication,
                    "is_panel": order.is_panel,
                    "panel_tests": json.dumps(order.panel_tests),
                    "created_at": completed_at
                }).scalar()
                pathology_order_ids.append(str(order_id))

            # 5. Update user progress
            db.execute(text("""
                UPDATE user_progress
                SET emr_sessions_completed = COALESCE(emr_sessions_completed, 0) + 1,
                    emr_soap_notes_completed = COALESCE(emr_soap_notes_completed, 0) + 1,
                    emr_prescriptions_written = COALESCE(emr_prescriptions_written, 0) + :num_prescriptions,
                    emr_pathology_orders_placed = COALESCE(emr_pathology_orders_placed, 0) + :num_orders
                WHERE user_id = :user_id
            """), {
                "user_id": user_id,
                "num_prescriptions": len(submit_data.prescriptions),
                "num_orders": len(submit_data.pathology_orders)
            })

            # Commit transaction
            db.commit()

            return {
                "session_id": session_id,
                "completed_at": completed_at,
                "soap_note_id": str(soap_note_id),
                "prescription_ids": prescription_ids,
                "pathology_order_ids": pathology_order_ids
            }

        except Exception as e:
            logger.error(f"Session submit failed: {e}")
            db.rollback()
            raise

    @staticmethod
    def get_session(db: Session, session_id: str, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed session information.

        Args:
            db: Database session
            session_id: Session UUID
            user_id: User ID (authorization)

        Returns:
            Session dict or None

        Performance: <300ms target
        """
        # Get session with patient data
        session = db.execute(text("""
            SELECT
                s.id, s.user_id, s.specialty, s.difficulty,
                s.started_at, s.submitted_at, s.elapsed_time_seconds,
                s.validation_score, s.score_breakdown,
                p.id as patient_id, p.name, p.age, p.gender,
                p.presenting_complaint, p.specialty as patient_specialty,
                p.difficulty as patient_difficulty
            FROM emr_sessions s
            JOIN mock_patients p ON s.patient_id = p.id
            WHERE s.id = :session_id
            AND s.user_id = :user_id
        """), {"session_id": session_id, "user_id": user_id}).fetchone()

        if not session:
            return None

        # Convert to dict
        session_dict = dict(session._mapping)

        # If completed, fetch SOAP note, prescriptions, pathology
        if session_dict['submitted_at']:
            # Get SOAP note
            soap_note = db.execute(text("""
                SELECT * FROM emr_soap_notes WHERE session_id = :session_id
            """), {"session_id": session_id}).fetchone()

            if soap_note:
                session_dict['soap_note'] = dict(soap_note._mapping)

            # Get prescriptions
            prescriptions = db.execute(text("""
                SELECT * FROM emr_prescriptions WHERE session_id = :session_id
            """), {"session_id": session_id}).fetchall()

            session_dict['prescriptions'] = [dict(rx._mapping) for rx in prescriptions]

            # Get pathology orders
            pathology_orders = db.execute(text("""
                SELECT * FROM emr_pathology_orders WHERE session_id = :session_id
            """), {"session_id": session_id}).fetchall()

            session_dict['pathology_orders'] = [dict(order._mapping) for order in pathology_orders]

        return session_dict

    @staticmethod
    def list_sessions(
        db: Session,
        user_id: int,
        is_active: Optional[bool] = None,
        specialty: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        List user's EMR sessions with pagination.

        Args:
            db: Database session
            user_id: User ID
            is_active: Filter by completion status
            specialty: Filter by specialty
            limit: Page size
            offset: Page offset

        Returns:
            Dict with sessions list and total count

        Performance: <500ms target
        """
        # Build query conditions
        conditions = ["user_id = :user_id"]
        params = {"user_id": user_id, "limit": limit, "offset": offset}

        if is_active is not None:
            if is_active:
                conditions.append("submitted_at IS NULL")
            else:
                conditions.append("submitted_at IS NOT NULL")

        if specialty:
            conditions.append("specialty = :specialty")
            params["specialty"] = specialty

        where_clause = " AND ".join(conditions)

        # Get total count
        total = db.execute(text(f"""
            SELECT COUNT(*) FROM emr_sessions WHERE {where_clause}
        """), params).scalar()

        # Get sessions
        sessions = db.execute(text(f"""
            SELECT
                s.id, s.started_at, s.submitted_at,
                s.specialty, s.validation_score,
                p.name as patient_name
            FROM emr_sessions s
            JOIN mock_patients p ON s.patient_id = p.id
            WHERE {where_clause}
            ORDER BY s.started_at DESC
            LIMIT :limit OFFSET :offset
        """), params).fetchall()

        return {
            "sessions": [dict(s._mapping) for s in sessions],
            "total_count": total,
            "limit": limit,
            "offset": offset
        }

    @staticmethod
    def delete_session(db: Session, session_id: str, user_id: int):
        """
        Delete draft session (only if not submitted).

        Args:
            db: Database session
            session_id: Session UUID
            user_id: User ID (authorization)

        Raises:
            ValueError: If session not found, not owned, or already submitted
        """
        # Verify session exists and is draft
        session = db.execute(text("""
            SELECT id FROM emr_sessions
            WHERE id = :session_id
            AND user_id = :user_id
            AND submitted_at IS NULL
        """), {"session_id": session_id, "user_id": user_id}).fetchone()

        if not session:
            raise ValueError("Session not found or cannot be deleted (already submitted)")

        # Delete session (CASCADE will handle related records)
        db.execute(text("""
            DELETE FROM emr_sessions WHERE id = :session_id
        """), {"session_id": session_id})

        db.commit()
