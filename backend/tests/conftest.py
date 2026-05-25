"""
Global pytest configuration for backend tests

Provides shared fixtures for all test modules:
- Vault setup (session-scoped, auto-configured)
- Database session (db_session)
- Test users
- Patient personas (mock_patients)
- Python path setup
"""

import sys
import json
import os
import subprocess
from pathlib import Path
from uuid import uuid4
from datetime import datetime
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from src.db.base import Base
# Import all models to ensure they're registered with Base.metadata
from src.db.models import (
    User, MCQ, MCQAttempt, OSCE, OSCEAttempt, StudyCard, StudyCardReview,
    UserProgress, MockPatient, EMRSession, EMRSOAPNote, EMRPrescription,
    EMRPathologyOrder, EMRValidationResult
)


# ============================================================================
# VAULT SETUP FIXTURE (Session-scoped, runs automatically)
# ============================================================================


@pytest.fixture(scope="session", autouse=True)
def setup_vault():
    """
    Ensure Vault is running and initialized for tests (session-scoped).
    
    This fixture:
    1. Checks if Vault is running on port 8200
    2. Starts Vault if not running (via start_vault_dev.sh)
    3. Initializes secrets (via init_vault_secrets.sh)
    4. Sets environment variables for test session
    
    Runs automatically before all tests (autouse=True).
    """
    # Set Vault environment variables for entire test session
    os.environ['VAULT_ADDR'] = 'http://localhost:8200'
    os.environ['VAULT_TOKEN'] = 'dev-only-token-change-in-prod'
    os.environ['VAULT_ROOT_TOKEN'] = 'dev-only-token-change-in-prod'  # Used by SecurityEventLogger
    
    # Get scripts directory
    scripts_dir = backend_dir / "scripts"
    
    # Check if Vault is running
    vault_running = False
    try:
        import urllib.request
        urllib.request.urlopen('http://localhost:8200/v1/sys/health', timeout=1)
        vault_running = True
        print("\n✅ Vault already running at http://localhost:8200")
    except Exception:
        pass
    
    # Start Vault if not running
    if not vault_running:
        print("\n🚀 Starting Vault dev server...")
        try:
            result = subprocess.run(
                ['bash', str(scripts_dir / 'start_vault_dev.sh')],
                check=True,
                capture_output=True,
                text=True,
                timeout=60
            )
            print(result.stdout)
            print("✅ Vault started successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to start Vault: {e.stderr}")
            pytest.skip("Vault dev server not available")
        except subprocess.TimeoutExpired:
            print("❌ Vault startup timed out")
            pytest.skip("Vault startup timed out")
    
    # Initialize secrets
    print("🔑 Initializing Vault secrets...")
    try:
        result = subprocess.run(
            ['bash', str(scripts_dir / 'init_vault_secrets.sh')],
            check=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        # Only print key lines (avoid verbose output)
        for line in result.stdout.split('\n'):
            if any(marker in line for marker in ['✅', '❌', '⚠️', '====', 'Next steps']):
                print(line)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to initialize Vault secrets: {e.stderr}")
        pytest.skip("Vault initialization failed")
    except subprocess.TimeoutExpired:
        print("❌ Vault initialization timed out")
        pytest.skip("Vault initialization timed out")
    
    yield  # Tests run here
    
    # Cleanup not needed - Vault runs in dev mode and auto-unseals
    # Container cleanup happens via stop_vault_dev.sh when needed


# ============================================================================
# TEST DATABASE SETUP
# ============================================================================

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ============================================================================
# DATABASE FIXTURES
# ============================================================================


@pytest.fixture(scope="function")
def db_session():
    """
    Create fresh in-memory SQLite database for each test.

    This fixture:
    1. Creates all tables from Base metadata
    2. Yields a database session
    3. Closes the session and drops all tables after test completes

    Usage:
        def test_something(db_session):
            # Use db_session to interact with database
            user = User(email="test@test.com")
            db_session.add(user)
            db_session.commit()
    """
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


# ============================================================================
# FASTAPI TEST CLIENT FIXTURES
# ============================================================================


@pytest.fixture
def client(db_session):
    """FastAPI test client with database dependency override"""
    from fastapi.testclient import TestClient
    from src.main import app
    from src.db.base import get_db

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """Create authenticated test user"""
    from src.auth.security import hash_password

    user = User(
        email="test@test.com",
        password_hash=hash_password("TestPassword123!"),
        full_name="Test User",
        role="student",
        is_verified=True,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user):
    """Create Authorization header with valid JWT"""
    from src.auth.security import create_access_token

    access_token = create_access_token(
        data={"sub": test_user.email, "user_id": str(test_user.id)}
    )
    return {"Authorization": f"Bearer {access_token}"}


# ============================================================================
# PATIENT PERSONA FIXTURES
# ============================================================================


def _load_persona_files(personas_dir: Path, limit: int = None) -> list[dict]:
    """Load persona JSON files from directory (excludes QA report files)"""
    personas = []

    # Get only persona files (exclude QA reports)
    json_files = [
        f for f in sorted(personas_dir.glob("*_persona.json"))
        if not f.name.endswith("_qa_report.json")
    ]

    if limit:
        json_files = json_files[:limit]

    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                persona = json.load(f)
                personas.append(persona)
        except Exception:
            continue  # Skip invalid files

    return personas


def _map_persona_to_mock_patient(persona: dict) -> MockPatient:
    """Map persona JSON to MockPatient database model"""
    # Generate unique MRN from persona ID
    mrn = f"MOCK-{persona['id']}"

    # Map gender (handle case variations)
    gender_map = {
        'male': 'Male',
        'female': 'Female',
        'other': 'Other',
        'unknown': 'Unknown'
    }
    gender = gender_map.get(persona.get('gender', '').lower(), persona.get('gender', 'Unknown'))

    # Map difficulty (handle case variations)
    difficulty_map = {
        'easy': 'Easy',
        'medium': 'Medium',
        'hard': 'Hard',
        'intermediate': 'Medium'
    }
    difficulty = difficulty_map.get(persona.get('difficulty', '').lower(), persona.get('difficulty', 'Medium'))

    # Extract medical history from persona data
    medical_history = {
        'diagnosis': persona.get('diagnosis', 'Unknown'),
        'symptoms': [
            {
                'symptom': s.get('symptom', 'Unspecified'),
                'onset': s.get('onset', 'Unknown'),
                'duration': s.get('duration', 'Unknown'),
                'severity': s.get('severity', 'Unknown')
            }
            for s in persona.get('symptoms', [])[:3]
        ],
        'differential_diagnoses': persona.get('differential_diagnoses', []),
        'opening_statement': persona.get('opening_statement', ''),
        'emotional_baseline': persona.get('emotional_baseline', '')
    }

    # Create MockPatient instance
    return MockPatient(
        id=uuid4(),
        mrn=mrn,
        name=persona.get('name', 'Unknown Patient'),
        age=persona.get('age', 0),
        gender=gender,
        presenting_complaint=persona.get('chief_complaint', 'Unknown complaint'),
        vital_signs=persona.get('vital_signs', None),
        medical_history=medical_history,
        specialty=persona.get('specialty', 'General').lower(),
        difficulty=difficulty.lower(),
        created_at=datetime.utcnow()
    )


@pytest.fixture(scope="session")
def all_persona_data():
    """
    Load all patient persona files (session-scoped for performance).

    Returns raw persona dictionaries for use by other fixtures.
    """
    project_root = backend_dir.parent
    personas_dir = project_root / "clinical-content-prds" / "validation-system" / "batch1_personas"

    if not personas_dir.exists():
        pytest.skip(f"Patient personas directory not found: {personas_dir}")

    personas = _load_persona_files(personas_dir)

    if not personas:
        pytest.skip("No patient persona files found")

    return personas


@pytest.fixture
def sample_personas(db_session):
    """
    Seed database with 20 sample patient personas (fast for most tests).

    Use this fixture for tests that need patient data but don't require all 207 personas.
    """
    project_root = backend_dir.parent
    personas_dir = project_root / "clinical-content-prds" / "validation-system" / "batch1_personas"

    if not personas_dir.exists():
        pytest.skip(f"Patient personas directory not found: {personas_dir}")

    # Load first 20 personas (mix of specialties)
    personas = _load_persona_files(personas_dir, limit=20)

    if not personas:
        pytest.skip("No patient persona files found")

    # Import personas into database
    for persona in personas:
        try:
            mock_patient = _map_persona_to_mock_patient(persona)
            db_session.add(mock_patient)
        except Exception:
            continue

    db_session.commit()
    return personas


@pytest.fixture
def all_personas(db_session, all_persona_data):
    """
    Seed database with ALL patient personas from Batch 1 (207 personas).

    Use this fixture for tests that specifically require the full dataset
    (e.g., pagination tests, specialty-specific tests).

    WARNING: This is slower (~2-3 seconds) - only use when necessary.
    """
    # Import all personas into database
    for persona in all_persona_data:
        try:
            mock_patient = _map_persona_to_mock_patient(persona)
            db_session.add(mock_patient)
        except Exception:
            continue

    db_session.commit()
    return all_persona_data
