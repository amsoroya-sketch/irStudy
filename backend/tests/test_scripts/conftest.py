"""Local fixtures for the conditions-spine script tests (PRD-CONDITIONS-SPINE-001).

- Makes the repository root importable so `from scripts.seed_conditions import ...`
  and `from scripts.content_reconciliation import ...` resolve (the reconciliation
  and seed/backfill scripts live in the repo-root `scripts/` package, mirroring
  the existing `scripts_emr` shim pattern).
- Overrides the global session-scoped `setup_vault` gate with a no-op for THIS
  package only; these tests exercise pure functions and never touch Vault.
"""
import os
import sys
from pathlib import Path

import pytest

# backend/tests/test_scripts/conftest.py -> repo root is parents[3]
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))


@pytest.fixture(scope="session", autouse=True)
def setup_vault():
    os.environ.setdefault("VAULT_ADDR", "http://localhost:8200")
    os.environ.setdefault("VAULT_TOKEN", "dev-only-token-change-in-prod")
    os.environ.setdefault("VAULT_ROOT_TOKEN", "dev-only-token-change-in-prod")
    yield
