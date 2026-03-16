"""
Conftest for AI OSCE tests (tests/test_ai/).

Ensures PYTHONPATH is set correctly so imports like:
  from src.ai.ai_patient import AIPatientService
work correctly in tests.

This follows the same pattern as tests/test_api/conftest.py.
"""
import sys
import os
from pathlib import Path

# Add backend directory to Python path
# This allows: from src.ai.ai_patient import AIPatientService
backend_dir = Path(__file__).parent.parent.parent  # backend/tests/test_ai -> backend
sys.path.insert(0, str(backend_dir))

# Verify path was added correctly
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info(f"✅ Added {backend_dir} to PYTHONPATH for AI OSCE tests")
