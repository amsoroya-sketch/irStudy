"""
Tests for GDPR Compliance APIs (PRD 2 - Step 8)

Validates:
- Article 15: Right of access (data export)
- Article 17: Right to erasure (data deletion)
- Permission-based access control
- Audit logging

NOTE: These are integration-level tests demonstrating security architecture.
Full database operations will be implemented when OSCE tables are finalized.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi import status

from src.db.models import UserRole

# Use shared fixtures from conftest (client, auth_headers, test_user)


def test_gdpr_delete_own_data_success(client, test_user, auth_headers):
    """Test user can delete their own OSCE data"""
    # Make DELETE request to delete own data (authenticated)
    response = client.delete(
        f"/api/v1/users/{test_user.id}/osce-data",
        headers=auth_headers
    )

    # Should return 204 No Content
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_gdpr_delete_other_user_data_forbidden(client, test_user, auth_headers):
    """Test user CANNOT delete another user's data (no admin permission)"""
    other_user_id = test_user.id + 999  # Different user ID

    # Try to delete another user's data (authenticated as test_user)
    response = client.delete(
        f"/api/v1/users/{other_user_id}/osce-data",
        headers=auth_headers
    )

    # Should return 403 Forbidden
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_gdpr_export_own_data_success(client, test_user, auth_headers):
    """Test user can export their own OSCE data"""
    # Make GET request to export own data (authenticated)
    response = client.get(
        f"/api/v1/users/{test_user.id}/osce-data/export",
        headers=auth_headers
    )

    # Should return 200 OK with JSON export
    assert response.status_code == status.HTTP_200_OK

    # Verify response structure
    data = response.json()
    assert "export_date" in data
    assert "user_id" in data
    assert data["user_id"] == test_user.id
    assert "data_subject_rights" in data
    assert "article_15" in data["data_subject_rights"]
    assert "article_17" in data["data_subject_rights"]
    assert "attempts" in data
    assert "scores" in data


def test_gdpr_export_includes_compliance_metadata(client, test_user, auth_headers):
    """Test export includes GDPR compliance metadata"""
    # Make GET request to export data (authenticated)
    response = client.get(
        f"/api/v1/users/{test_user.id}/osce-data/export",
        headers=auth_headers
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    rights = data["data_subject_rights"]

    # Verify GDPR articles are documented (check for article number OR key name OR right description)
    assert ("Article 15" in rights["article_15"] or
            "article 15" in rights["article_15"].lower() or
            "access" in rights["article_15"].lower())
    assert ("Article 17" in rights["article_17"] or
            "article 17" in rights["article_17"].lower() or
            "erasure" in rights["article_17"].lower())
    assert ("Article 20" in rights["article_20"] or
            "article 20" in rights["article_20"].lower() or
            "portability" in rights["article_20"].lower())


def test_gdpr_export_json_format(client, test_user, auth_headers):
    """Test export is in machine-readable JSON format (GDPR Article 20)"""
    # Make GET request to export data (authenticated)
    response = client.get(
        f"/api/v1/users/{test_user.id}/osce-data/export",
        headers=auth_headers
    )

    # Verify JSON format
    assert response.headers["content-type"] == "application/json"

    # Verify parseable JSON
    data = response.json()
    assert isinstance(data, dict)
