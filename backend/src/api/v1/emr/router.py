"""
EMR API Router

Aggregates all EMR endpoints:
- Case catalog / picker (cases.py)
- Session management (sessions.py)
- Dashboard analytics (dashboard.py)
- Validation endpoints (validation.py)
"""

from fastapi import APIRouter
from .cases import router as cases_router
from .sessions import router as sessions_router
from .dashboard import router as dashboard_router
from .validation import router as validation_router

router = APIRouter(prefix="/emr", tags=["EMR Practice"])

# Include sub-routers
router.include_router(cases_router)
router.include_router(sessions_router)
router.include_router(dashboard_router)
router.include_router(validation_router)
