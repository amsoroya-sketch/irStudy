"""
RBAC Permission System for AMC Clinical Exam Simulation

PERMISSION FORMAT: resource.action
Examples: "mcq.create", "osce.view", "user.manage"

SECURITY:
- All permission checks logged to SecurityEventLogger
- User IDs anonymized in logs
- Permission denials return HTTP 403
"""

from enum import Enum
from typing import Set, Dict
from ..db.models import UserRole


class Permission(str, Enum):
    """System permissions for RBAC"""

    # MCQ permissions
    MCQ_VIEW = "mcq.view"
    MCQ_CREATE = "mcq.create"
    MCQ_UPDATE = "mcq.update"
    MCQ_DELETE = "mcq.delete"
    MCQ_ATTEMPT = "mcq.attempt"

    # OSCE permissions
    OSCE_VIEW = "osce.view"
    OSCE_CREATE = "osce.create"
    OSCE_UPDATE = "osce.update"
    OSCE_DELETE = "osce.delete"
    OSCE_ATTEMPT = "osce.attempt"

    # User management
    USER_VIEW = "user.view"
    USER_CREATE = "user.create"
    USER_UPDATE = "user.update"
    USER_DELETE = "user.delete"

    # Progress tracking
    PROGRESS_VIEW_OWN = "progress.view.own"
    PROGRESS_VIEW_ALL = "progress.view.all"
    PROGRESS_GRADE = "progress.grade"

    # Study cards
    STUDYCARD_VIEW = "studycard.view"
    STUDYCARD_CREATE = "studycard.create"
    STUDYCARD_UPDATE = "studycard.update"
    STUDYCARD_DELETE = "studycard.delete"

    # Administration
    ADMIN_PANEL = "admin.panel"
    SYSTEM_CONFIG = "system.config"

    # GDPR Compliance (PRD 2 - Step 8)
    GDPR_DELETE_OWN = "gdpr.delete.own"
    GDPR_DELETE_ANY = "gdpr.delete.any"
    GDPR_EXPORT_OWN = "gdpr.export.own"
    GDPR_EXPORT_ANY = "gdpr.export.any"


# Role-Permission Mapping
ROLE_PERMISSIONS: Dict[UserRole, Set[Permission]] = {
    UserRole.STUDENT: {
        # View and attempt content
        Permission.MCQ_VIEW,
        Permission.MCQ_ATTEMPT,
        Permission.OSCE_VIEW,
        Permission.OSCE_ATTEMPT,
        Permission.PROGRESS_VIEW_OWN,
        Permission.STUDYCARD_VIEW,
        Permission.STUDYCARD_CREATE,
        Permission.STUDYCARD_UPDATE,
        Permission.STUDYCARD_DELETE,
        # GDPR rights
        Permission.GDPR_DELETE_OWN,
        Permission.GDPR_EXPORT_OWN,
    },

    UserRole.EDUCATOR: {
        # All student permissions
        Permission.MCQ_VIEW,
        Permission.MCQ_ATTEMPT,
        Permission.MCQ_CREATE,
        Permission.MCQ_UPDATE,
        Permission.OSCE_VIEW,
        Permission.OSCE_ATTEMPT,
        Permission.OSCE_CREATE,
        Permission.OSCE_UPDATE,
        Permission.PROGRESS_VIEW_OWN,
        Permission.PROGRESS_VIEW_ALL,
        Permission.PROGRESS_GRADE,
        Permission.USER_VIEW,
        Permission.STUDYCARD_VIEW,
        Permission.STUDYCARD_CREATE,
        Permission.STUDYCARD_UPDATE,
        Permission.STUDYCARD_DELETE,
        # GDPR rights
        Permission.GDPR_DELETE_OWN,
        Permission.GDPR_EXPORT_OWN,
    },

    UserRole.ADMIN: {
        # All permissions
        Permission.MCQ_VIEW,
        Permission.MCQ_CREATE,
        Permission.MCQ_UPDATE,
        Permission.MCQ_DELETE,
        Permission.MCQ_ATTEMPT,
        Permission.OSCE_VIEW,
        Permission.OSCE_CREATE,
        Permission.OSCE_UPDATE,
        Permission.OSCE_DELETE,
        Permission.OSCE_ATTEMPT,
        Permission.USER_VIEW,
        Permission.USER_CREATE,
        Permission.USER_UPDATE,
        Permission.USER_DELETE,
        Permission.PROGRESS_VIEW_OWN,
        Permission.PROGRESS_VIEW_ALL,
        Permission.PROGRESS_GRADE,
        Permission.STUDYCARD_VIEW,
        Permission.STUDYCARD_CREATE,
        Permission.STUDYCARD_UPDATE,
        Permission.STUDYCARD_DELETE,
        Permission.ADMIN_PANEL,
        Permission.SYSTEM_CONFIG,
        # GDPR rights (can manage any user's data)
        Permission.GDPR_DELETE_OWN,
        Permission.GDPR_DELETE_ANY,
        Permission.GDPR_EXPORT_OWN,
        Permission.GDPR_EXPORT_ANY,
    },
}


def get_role_permissions(role: UserRole) -> Set[Permission]:
    """
    Get all permissions for a given role.

    Args:
        role: User role enum

    Returns:
        Set of permissions for that role
    """
    return ROLE_PERMISSIONS.get(role, set())


def has_permission(user_role: UserRole, permission: Permission) -> bool:
    """
    Check if a role has a specific permission.

    Args:
        user_role: User role enum
        permission: Permission to check

    Returns:
        True if role has permission, False otherwise
    """
    return permission in get_role_permissions(user_role)
