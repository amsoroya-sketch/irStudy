"""
Admin-only endpoints for RBAC testing
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from src.db.base import get_db
from src.db.models import User, UserRole
from src.auth.dependencies import get_current_user

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/users")
async def list_all_users(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[dict]:
    """Admin-only endpoint - requires EDUCATOR role"""
    if current_user.role != UserRole.EDUCATOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    users = db.query(User).all()
    return [
        {
            "id": str(u.id),
            "email": u.email,
            "role": u.role.value,
        }
        for u in users
    ]
