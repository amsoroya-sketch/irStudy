"""
EMR Case Catalog Endpoint (Phase 1a - "pick a case and practice")

ENDPOINTS:
- GET /cases - List selectable EMR practice cases for the picker

SECURITY:
- JWT authentication required (any authenticated user may list cases)
- validation_criteria (the per-case answer key) is NEVER returned to the client

AUSTRALIAN MEDICAL CONTEXT:
- Cases are authored against Australian standards (eTG, PBS, MBS, AHPRA)
"""

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.db.base import get_db
from src.db.models import User, MockPatient
from src.auth.dependencies import get_current_user

from .schemas import EMRCaseListItem, EMRCaseListResponse


router = APIRouter()


# ============================================================================
# GET /cases - LIST SELECTABLE EMR PRACTICE CASES
# ============================================================================


@router.get("/cases", response_model=EMRCaseListResponse)
async def list_cases(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    specialty: Optional[str] = Query(None, description="Filter by medical specialty"),
    difficulty: Optional[str] = Query(
        None, description="Filter by difficulty (easy, medium, hard)"
    ),
):
    """
    Return the catalog of selectable EMR practice cases for the "pick a case"
    picker.

    The catalog is small (~24 authored cases) so no pagination is applied.

    AUTHORIZATION:
    - Any authenticated user may list cases.

    FILTERS (optional):
    - specialty: exact-match medical specialty
    - difficulty: exact-match difficulty level

    ORDERING:
    - Deterministic: (specialty, difficulty, mrn) so the picker is stable.

    SECURITY:
    - ``validation_criteria`` (the answer key) is intentionally excluded — the
      response schema only surfaces non-sensitive selection fields.
    """
    # Select only the non-sensitive columns needed for the picker. This avoids
    # ever loading validation_criteria into a serialisable object.
    query = db.query(
        MockPatient.id,
        MockPatient.mrn,
        MockPatient.name,
        MockPatient.age,
        MockPatient.gender,
        MockPatient.presenting_complaint,
        MockPatient.specialty,
        MockPatient.difficulty,
    )

    if specialty:
        query = query.filter(MockPatient.specialty == specialty)

    if difficulty:
        query = query.filter(MockPatient.difficulty == difficulty)

    query = query.order_by(
        MockPatient.specialty.asc(),
        MockPatient.difficulty.asc(),
        MockPatient.mrn.asc(),
    )

    rows = query.all()

    cases = [
        EMRCaseListItem(
            id=row.id,
            mrn=row.mrn,
            name=row.name,
            age=row.age,
            gender=row.gender,
            presenting_complaint=row.presenting_complaint,
            specialty=row.specialty,
            difficulty=row.difficulty,
        )
        for row in rows
    ]

    return EMRCaseListResponse(total=len(cases), cases=cases)
