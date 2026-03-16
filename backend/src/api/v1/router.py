"""
Main API v1 router aggregation

Combines all v1 endpoint routers:
- /api/v1/auth - Authentication (register, login, refresh)
- /api/v1/users - User management
- /api/v1/mcqs - MCQ CRUD and attempts
- /api/v1/osces - OSCE CRUD and practice
- /api/v1/progress - User progress and analytics
- /api/v1/patient-personas - AI OSCE patient personas
- /api/v1/osce-sessions - AI OSCE session management
"""

from fastapi import APIRouter

from src.api.v1 import (
    auth,
    users,
    mcqs,
    osces,
    progress,
    permissions,
    gdpr,
    study_cards,
    study_cards_optimized,
    patient_personas,
    osce_sessions,
)
from src.api.v1.emr import router as emr_router


# Create main v1 router
api_router = APIRouter(prefix="/v1")

# Include all sub-routers
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(mcqs.router)
api_router.include_router(osces.router)
api_router.include_router(progress.router)
api_router.include_router(permissions.router)  # Task 3.2: RBAC permissions API
api_router.include_router(gdpr.router)  # PRD 2 Step 8: GDPR Compliance APIs
api_router.include_router(study_cards.router)  # Task 3: Study Card System with SM-2
api_router.include_router(study_cards_optimized.router)  # Task 5: Spaced Repetition Engine Optimization
api_router.include_router(patient_personas.router)  # PRD AI OSCE 001: Patient Personas API
api_router.include_router(osce_sessions.router)  # PRD AI OSCE 001: OSCE Sessions API
api_router.include_router(emr_router)  # PRD GAP 002: EMR API Endpoints
