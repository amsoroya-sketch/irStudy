"""Local fixtures for the conditions-spine DB tests (PRD-CONDITIONS-SPINE-001).

These tests run entirely on the in-memory SQLite `db_session` fixture and pure
model metadata. They do NOT touch HashiCorp Vault, so this override replaces the
global session-scoped `setup_vault` gate (which skips the suite when the shared
Vault on localhost:8200 isn't the project's dev instance) with a no-op for THIS
package only. It weakens no assertion.
"""
import os
import pytest


@pytest.fixture(scope="session", autouse=True)
def setup_vault():
    os.environ.setdefault("VAULT_ADDR", "http://localhost:8200")
    os.environ.setdefault("VAULT_TOKEN", "dev-only-token-change-in-prod")
    os.environ.setdefault("VAULT_ROOT_TOKEN", "dev-only-token-change-in-prod")
    yield
