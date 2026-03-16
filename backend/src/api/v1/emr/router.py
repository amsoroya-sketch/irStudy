"""
EMR API Router

Aggregates all EMR endpoints:
- Session management (sessions.py)
- Dashboard analytics (dashboard.py)
"""

from fastapi import APIRouter
from .sessions import router as sessions_router
from .dashboard import router as dashboard_router

router = APIRouter(prefix="/emr", tags=["EMR Practice"])

# Include sub-routers
router.include_router(sessions_router)
router.include_router(dashboard_router)
