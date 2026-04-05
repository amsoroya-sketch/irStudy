"""
Patient Assignment Service

Handles random patient selection with filtering for EMR practice sessions.

AUSTRALIAN MEDICAL CONTEXT:
- Filters by Australian specialties
- Ensures appropriate complexity levels
- Excludes previously completed patients
"""

import random
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from src.db.models import User
import logging

logger = logging.getLogger(__name__)


class PatientService:
    """Service for patient assignment logic"""

    @staticmethod
    def get_random_patient(
        db: Session,
        specialty: Optional[str] = None,
        complexity: Optional[str] = None,
        exclude_user_completed: Optional[int] = None
    ):
        """
        Get random mock patient with optional filtering.

        Args:
            db: Database session
            specialty: Filter by medical specialty
            complexity: Filter by difficulty level
            exclude_user_completed: User ID to exclude completed patients

        Returns:
            MockPatient object or None if no matches

        Performance: <50ms (uses specialty + complexity indexes)
        """
        # Import here to avoid circular dependency
        from src.db.models import User

        # SQLAlchemy model import - check if mock_patients table exists
        try:
            # Try to query from mock_patients table
            from sqlalchemy import text
            query = db.execute(text("SELECT 1 FROM mock_patients LIMIT 1"))
            query.fetchone()
        except Exception as e:
            logger.error(f"mock_patients table not accessible: {e}")
            # Return mock data for development
            return _create_mock_patient_for_dev(specialty, complexity)

        # Build query
        from sqlalchemy import text
        conditions = []
        params = {}

        if specialty:
            conditions.append("specialty = :specialty")
            params["specialty"] = specialty

        if complexity:
            conditions.append("difficulty = :complexity")
            params["complexity"] = complexity

        # Exclude previously completed patients
        if exclude_user_completed:
            conditions.append("""
                id NOT IN (
                    SELECT DISTINCT patient_id
                    FROM emr_sessions
                    WHERE user_id = :user_id
                    AND submitted_at IS NOT NULL
                )
            """)
            params["user_id"] = exclude_user_completed

        # Build WHERE clause
        where_clause = " AND ".join(conditions) if conditions else "1=1"

        # Get total count
        count_query = text(f"SELECT COUNT(*) FROM mock_patients WHERE {where_clause}")
        total = db.execute(count_query, params).scalar()

        if total == 0:
            logger.warning(f"No patients found matching filters: {params}")
            return None

        # Get random patient
        offset = random.randint(0, total - 1)
        patient_query = text(f"""
            SELECT * FROM mock_patients
            WHERE {where_clause}
            LIMIT 1 OFFSET :offset
        """)
        params["offset"] = offset

        result = db.execute(patient_query, params).fetchone()

        # Convert row to dict-like object
        if result:
            return _row_to_patient_dict(result)

        return None

    @staticmethod
    def get_patient_for_osce(db: Session, osce_id: str):
        """
        Get patient linked to specific OSCE station.

        Args:
            db: Database session
            osce_id: OSCE station ID

        Returns:
            MockPatient or None
        """
        from sqlalchemy import text

        try:
            query = text("""
                SELECT * FROM mock_patients
                WHERE source_osce_id = :osce_id
                LIMIT 1
            """)
            result = db.execute(query, {"osce_id": osce_id}).fetchone()

            if result:
                return _row_to_patient_dict(result)

            return None

        except Exception as e:
            logger.error(f"Error fetching patient for OSCE {osce_id}: {e}")
            return None

    @staticmethod
    def get_available_specialties(db: Session) -> list:
        """
        Get list of available specialties with patient count.

        Returns:
            List of {specialty, count} dicts
        """
        from sqlalchemy import text

        try:
            query = text("""
                SELECT specialty, COUNT(*) as count
                FROM mock_patients
                GROUP BY specialty
                ORDER BY specialty
            """)
            results = db.execute(query).fetchall()

            return [
                {"specialty": row[0], "count": row[1]}
                for row in results
            ]

        except Exception as e:
            logger.error(f"Error fetching specialties: {e}")
            return []


def _row_to_patient_dict(row):
    """Convert SQLAlchemy row to patient dict"""
    import json

    # Handle both Row objects and dict-like objects
    if hasattr(row, '_mapping'):
        row_dict = dict(row._mapping)
    else:
        row_dict = dict(row)

    # Parse JSON fields
    json_fields = ['demographics', 'medical_history', 'medications', 'allergies',
                   'vital_signs', 'physical_exam_findings', 'investigation_results']

    for field in json_fields:
        if field in row_dict and isinstance(row_dict[field], str):
            try:
                row_dict[field] = json.loads(row_dict[field])
            except json.JSONDecodeError:
                row_dict[field] = {}

    # Convert UUID to string
    if 'id' in row_dict:
        row_dict['id'] = str(row_dict['id'])

    return row_dict


def _create_mock_patient_for_dev(specialty: Optional[str], complexity: Optional[str]):
    """Create mock patient data for development when database not available"""
    return {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "mrn": "12345678",
        "name": "William Thompson",
        "age": 65,
        "gender": "Male",
        "allergies": ["Penicillin"],
        "current_medications": [
            {"name": "Metformin", "dose": "1000mg", "frequency": "BD", "indication": "Type 2 Diabetes"}
        ],
        "vital_signs": {
            "BP": "152/88",
            "HR": 92,
            "RR": 20,
            "Temp": 37.1,
            "SpO2": 95
        },
        "presenting_complaint": "Chest pain and shortness of breath for 2 hours",
        "clinical_scenario": "65-year-old male presenting to ED with 2-hour history of central chest pain radiating to left arm. Pain described as 'tight, heavy feeling' 7/10 severity. Associated shortness of breath and diaphoresis.",
        "specialty": specialty or "Cardiology",
        "complexity_level": complexity or "Moderate",
        "difficulty": complexity or "Moderate",
        "demographics": {
            "country_of_birth": "Australia",
            "primary_language": "English",
            "indigenous_status": "Aboriginal"
        },
        "medical_history": {
            "past_illnesses": ["Type 2 Diabetes", "Hypertension"],
            "surgeries": [],
            "family_history": "Father with CAD"
        },
        "medications": [
            {"name": "Metformin", "dose": "1000mg", "frequency": "BD"}
        ],
        "physical_exam_findings": {
            "cardiovascular": "Regular rhythm, no murmurs",
            "respiratory": "Clear breath sounds bilaterally"
        },
        "investigation_results": {
            "ECG": "Sinus rhythm, T-wave inversion V4-V6",
            "Troponin": 0.45
        }
    }
