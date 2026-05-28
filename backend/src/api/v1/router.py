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
    health,
    mock_exams,
    study_notes,  # Week 3-4: Dr. Amir OSCE study notes
    html_notes,  # Week 3-4: Dr. Amir HTML OSCE notes (65 files)
)
from src.api.v1.emr import router as emr_router
from src.api.v1.integration import converter as integration_converter


# Create main v1 router
api_router = APIRouter(prefix="/v1", redirect_slashes=False)

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
api_router.include_router(mock_exams.router)  # PRD AI OSCE 006: Mock Exam Mode (16-station exams)
api_router.include_router(study_notes.router)  # Week 3-4: Dr. Amir OSCE study notes API
api_router.include_router(html_notes.router)  # Week 3-4: Dr. Amir HTML OSCE notes (65 files)
api_router.include_router(emr_router)  # PRD EMR 001: EMR API Endpoints (comprehensive router)
api_router.include_router(integration_converter.router)  # OSCE-to-EMR conversion endpoints
api_router.include_router(health.router)  # Health check endpoints (Kubernetes probes)
