"""
EMR Practice System API

Provides REST API endpoints for EMR (Electronic Medical Records) practice:
- Session management (create, retrieve, submit)
- Dashboard analytics (progress, specialty breakdown, history)
- SOAP note validation (3-layer validation system)

AUSTRALIAN MEDICAL COMPLIANCE:
- PBS (Pharmaceutical Benefits Scheme) for medications
- MBS (Medicare Benefits Schedule) for pathology
- eTG (Therapeutic Guidelines) terminology
"""

from .router import router

__all__ = ["router"]
