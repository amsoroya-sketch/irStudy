"""
Tests for GDPR Compliance Permissions (PRD 2 - Step 8)

Unit tests validating GDPR permission architecture without database dependencies.

Validates:
- GDPR permissions exist in Permission enum
- Students have GDPR rights for own data
- Admins have GDPR rights for any user's data
- Permission hierarchy is correct

NOTE: Full integration tests require database setup (pending OSCE table finalization).
These unit tests demonstrate the security architecture is in place.
"""

import pytest
from src.auth.permissions import (
    Permission,
    UserRole,
    get_role_permissions,
    has_permission,
)


def test_gdpr_permissions_exist():
    """Test GDPR permissions are defined in Permission enum"""
    # Verify all 4 GDPR permissions exist
    assert hasattr(Permission, "GDPR_DELETE_OWN")
    assert hasattr(Permission, "GDPR_DELETE_ANY")
    assert hasattr(Permission, "GDPR_EXPORT_OWN")
    assert hasattr(Permission, "GDPR_EXPORT_ANY")

    # Verify permission values follow naming convention
    assert Permission.GDPR_DELETE_OWN.value == "gdpr.delete.own"
    assert Permission.GDPR_DELETE_ANY.value == "gdpr.delete.any"
    assert Permission.GDPR_EXPORT_OWN.value == "gdpr.export.own"
    assert Permission.GDPR_EXPORT_ANY.value == "gdpr.export.any"


def test_student_gdpr_permissions():
    """Test students have GDPR rights for their own data (Articles 15 & 17)"""
    student_permissions = get_role_permissions(UserRole.STUDENT)

    # Students can delete own data (Article 17: Right to Erasure)
    assert Permission.GDPR_DELETE_OWN in student_permissions

    # Students can export own data (Article 15: Right of Access)
    assert Permission.GDPR_EXPORT_OWN in student_permissions

    # Students CANNOT delete/export other users' data
    assert Permission.GDPR_DELETE_ANY not in student_permissions
    assert Permission.GDPR_EXPORT_ANY not in student_permissions


def test_educator_gdpr_permissions():
    """Test educators have GDPR rights for their own data"""
    educator_permissions = get_role_permissions(UserRole.EDUCATOR)

    # Educators can delete own data
    assert Permission.GDPR_DELETE_OWN in educator_permissions

    # Educators can export own data
    assert Permission.GDPR_EXPORT_OWN in educator_permissions

    # Educators CANNOT delete/export other users' data (not admins)
    assert Permission.GDPR_DELETE_ANY not in educator_permissions
    assert Permission.GDPR_EXPORT_ANY not in educator_permissions


def test_admin_gdpr_permissions():
    """Test admins have GDPR rights for any user's data"""
    admin_permissions = get_role_permissions(UserRole.ADMIN)

    # Admins can delete own data
    assert Permission.GDPR_DELETE_OWN in admin_permissions

    # Admins can export own data
    assert Permission.GDPR_EXPORT_OWN in admin_permissions

    # Admins can delete ANY user's data
    assert Permission.GDPR_DELETE_ANY in admin_permissions

    # Admins can export ANY user's data
    assert Permission.GDPR_EXPORT_ANY in admin_permissions


def test_has_permission_student_gdpr():
    """Test has_permission function for student GDPR rights"""
    # Student can delete own data
    assert has_permission(UserRole.STUDENT, Permission.GDPR_DELETE_OWN) is True

    # Student can export own data
    assert has_permission(UserRole.STUDENT, Permission.GDPR_EXPORT_OWN) is True

    # Student CANNOT delete any user's data
    assert has_permission(UserRole.STUDENT, Permission.GDPR_DELETE_ANY) is False

    # Student CANNOT export any user's data
    assert has_permission(UserRole.STUDENT, Permission.GDPR_EXPORT_ANY) is False


def test_has_permission_admin_gdpr():
    """Test has_permission function for admin GDPR rights"""
    # Admin has all GDPR permissions
    assert has_permission(UserRole.ADMIN, Permission.GDPR_DELETE_OWN) is True
    assert has_permission(UserRole.ADMIN, Permission.GDPR_DELETE_ANY) is True
    assert has_permission(UserRole.ADMIN, Permission.GDPR_EXPORT_OWN) is True
    assert has_permission(UserRole.ADMIN, Permission.GDPR_EXPORT_ANY) is True


def test_gdpr_compliance_articles():
    """Test GDPR compliance mapping to EU regulations"""
    # Article 15: Right of Access → GDPR_EXPORT_OWN/ANY
    # Article 17: Right to Erasure → GDPR_DELETE_OWN/ANY
    # Article 20: Right to Data Portability → GDPR_EXPORT_OWN/ANY (JSON format)

    # Verify permission names map to GDPR articles
    assert "export" in Permission.GDPR_EXPORT_OWN.value  # Article 15
    assert "delete" in Permission.GDPR_DELETE_OWN.value  # Article 17

    # Verify permissions are string enums (for API serialization)
    assert isinstance(Permission.GDPR_DELETE_OWN.value, str)
    assert isinstance(Permission.GDPR_EXPORT_OWN.value, str)
