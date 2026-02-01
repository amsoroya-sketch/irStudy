"""
Main API v1 router aggregation

Combines all v1 endpoint routers:
- /api/v1/auth - Authentication (register, login, refresh)
- /api/v1/users - User management
- /api/v1/mcqs - MCQ CRUD and attempts
- /api/v1/osces - OSCE CRUD and practice
"""

from fastapi import APIRouter

from api.v1 import auth, users, mcqs, osces


# Create main v1 router
api_router = APIRouter(prefix="/v1")

# Include all sub-routers
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(mcqs.router)
api_router.include_router(osces.router)
