"""
Conftest for Mock Exam tests

Provides test database fixtures and authentication helpers.
Pattern: SQLite in-memory database, fresh per test.

Fixtures:
- db_session: SQLAlchemy session with clean database
- client: FastAPI TestClient
- auth_headers: JWT Authorization header
- test_user: Authenticated test user
- test_personas: 32 sample personas (2 per specialty × 8 specialties × 2 difficulties)
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import datetime, timezone
from uuid import uuid4

from src.main import app
from src.db.base import Base, get_db
from src.db.models import User, UserRole, PatientPersona

# SQLite in-memory database for tests (CHANGED: :memory: for isolation)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool  # ADDED: Prevent connection pool issues
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Fresh database session for each test"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    """FastAPI test client with test database"""
    # FIXED: Move dependency override into fixture to prevent pollution
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app)

    yield test_client

    # CRITICAL: Clear overrides after each test
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """Create authenticated test user"""
    from src.auth.security import hash_password
    
    user = User(
        email="mock_exam_test@example.com",
        password_hash=hash_password("TestPassword123!"),
        full_name="Mock Exam Test User",
        is_active=True,
        role=UserRole.STUDENT,
        is_verified=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user, db_session):
    """
    Create Authorization header with valid JWT

    Returns:
        dict: {"Authorization": "Bearer <token>"}
    """
    from src.auth.security import create_access_token

    token = create_access_token(
        data={
            "user_id": str(test_user.id),
            "email": test_user.email,
            "sub": test_user.email
        }
    )

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_personas(db_session):
    """
    Create 32 test personas for mock exams

    Distribution:
    - 8 specialties: Cardiology, Respiratory, Neurology, Gastroenterology,
                     Psychiatry, Paediatrics, Obstetrics, Emergency Medicine
    - 2 difficulty levels per specialty: intermediate, advanced
    - 2 personas per difficulty level = 4 personas per specialty
    - Total: 8 × 4 = 32 personas

    Ensures sufficient personas for 16-station mock exam (requires 16 total).
    """
    specialties = [
        'Cardiology',
        'Respiratory',
        'Neurology',
        'Gastroenterology',
        'Psychiatry',
        'Paediatrics',
        'Obstetrics & Gynaecology',
        'Emergency Medicine'
    ]

    personas = []

    for specialty in specialties:
        # Create 2 intermediate personas
        for i in range(2):
            persona = PatientPersona(
                persona_id=str(uuid4()),
                persona_code=f"{specialty[:4].upper()}-{i+1:03d}-TEST-INT",
                name=f"Test {specialty} Intermediate {i+1}",
                age=40 + i * 10,
                gender="male" if i % 2 == 0 else "female",
                specialty=specialty,
                chief_complaint=f"Test complaint for {specialty} (intermediate)",
                opening_statement=f"I've been having this problem for a few weeks now.",
                symptoms={},
                medical_history={},
                emotional_profile={},
                difficulty_level="intermediate"
            )
            personas.append(persona)
            db_session.add(persona)

        # Create 2 advanced personas
        for i in range(2):
            persona = PatientPersona(
                persona_id=str(uuid4()),
                persona_code=f"{specialty[:4].upper()}-{i+100:03d}-TEST-ADV",
                name=f"Test {specialty} Advanced {i+1}",
                age=50 + i * 10,
                gender="female" if i % 2 == 0 else "male",
                specialty=specialty,
                chief_complaint=f"Complex complaint for {specialty} (advanced)",
                opening_statement=f"I'm very concerned about my symptoms.",
                symptoms={},
                medical_history={},
                emotional_profile={},
                difficulty_level="advanced"
            )
            personas.append(persona)
            db_session.add(persona)

    db_session.commit()

    # Refresh all personas to get database-assigned values
    for persona in personas:
        db_session.refresh(persona)

    return personas


@pytest.fixture
def sample_mock_exam(db_session, test_user, test_personas):
    """
    Create a sample mock exam for testing

    Returns:
        MockExam: Pre-created exam with 16 stations configured
    """
    from src.db.models import MockExam

    # Select first 16 personas
    persona_ids = [str(p.persona_id) for p in test_personas[:16]]

    exam = MockExam(
        exam_id=str(uuid4()),
        user_id=test_user.id,
        stations_config={'persona_ids': persona_ids},
        exam_name="Sample Mock Exam",
        exam_state='IN_PROGRESS',
        current_station_number=1,
        total_score=0,
        stations_passed=0,
        started_at=datetime.now(timezone.utc)
    )

    db_session.add(exam)
    db_session.commit()
    db_session.refresh(exam)

    return exam
