"""
EMR Practice System Services

Business logic layer for EMR functionality:
- Session management
- Patient assignment
- Validation
- Progress tracking
"""

from .session_service import SessionService
from .patient_service import PatientService

__all__ = ["SessionService", "PatientService"]
