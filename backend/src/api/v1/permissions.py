"""
Permissions API Endpoints for RBAC

Provides endpoints for frontend to query user permissions and check access.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List
from pydantic import BaseModel

from ...auth.dependencies import get_current_active_user
from ...auth.permissions import Permission, get_role_permissions
from ...db.models import User


router = APIRouter(prefix="/permissions", tags=["permissions"])


class UserPermissionsResponse(BaseModel):
    """User permissions response"""
    user_id: int
    role: str
    permissions: List[str]

    class Config:
        from_attributes = True


class PermissionCheckResponse(BaseModel):
    """Permission check response"""
    permission: str
    has_permission: bool
    user_role: str


@router.get("/me", response_model=UserPermissionsResponse)
async def get_my_permissions(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user's permissions.

    Returns all permissions assigned to user's role.
    Used by frontend to show/hide UI elements.

    Returns:
        UserPermissionsResponse with user's role and permissions

    Security:
        - Requires authentication
        - Returns only current user's permissions
    """
    permissions = get_role_permissions(current_user.role)

    return UserPermissionsResponse(
        user_id=current_user.id,
        role=current_user.role.value,
        permissions=[p.value for p in permissions]
    )


@router.get("/check/{permission}", response_model=PermissionCheckResponse)
async def check_permission(
    permission: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    Check if current user has a specific permission.

    Args:
        permission: Permission string to check (e.g., "mcq.create")

    Returns:
        PermissionCheckResponse with result

    Security:
        - Requires authentication
        - Checks only current user's permissions
    """
    try:
        perm_enum = Permission(permission)
        has_perm = perm_enum in get_role_permissions(current_user.role)

        return PermissionCheckResponse(
            permission=permission,
            has_permission=has_perm,
            user_role=current_user.role.value
        )
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid permission: {permission}"
        )


@router.get("/all", response_model=List[str])
async def get_all_permissions(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get list of all available permissions in the system.

    Returns:
        List of all permission strings

    Security:
        - Requires authentication
        - Information disclosure is minimal (just permission names)
    """
    return [p.value for p in Permission]
