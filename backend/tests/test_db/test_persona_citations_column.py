"""TDD tests for PatientPersona.citations structured JSON column
(PRD-PERSONA-CITATION-001).

Mirrors tests/test_db/test_mcq_citations_column.py. Personas generated with
RAG grounding carry a ``citations`` array (each element has a qdrant_point_id
and is_australian flag); the persona table must persist it, and the importer
(scripts/import_patient_personas.py) must write it — previously it dropped
grounding on import.
"""
import importlib.util
import json
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.db.base import Base
from src.db.models import PatientPersona


@pytest.fixture
def mem_engine():
    """Isolated in-memory SQLite engine (StaticPool → one shared connection) so
    the importer and the verification session see the same database."""
    eng = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(eng)
    yield eng
    Base.metadata.drop_all(eng)
    eng.dispose()


SCRIPT_PATH = (
    Path(__file__).resolve().parents[2] / "scripts" / "import_patient_personas.py"
)

SAMPLE_CITATIONS = [
    {
        "qdrant_point_id": "dd6bc5b7-03b5-4b6b-83ba-35759e417012",
        "score": 0.957,
        "is_australian": True,
        "source": "Talley and O'Connor's Clinical Examination (8th edition).pdf",
    },
    {
        "qdrant_point_id": "ca39c0e5-44cf-4582-befb-026d2881776e",
        "score": 0.956,
        "is_australian": True,
        "source": "John Murtagh General Practice, 8th Edition.pdf",
    },
]


def _load_importer():
    spec = importlib.util.spec_from_file_location(
        "import_patient_personas_under_test", SCRIPT_PATH
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_persona_has_structured_citations_column():
    assert hasattr(PatientPersona, "citations")
    col = PatientPersona.__table__.columns["citations"]
    assert col.type.__class__.__name__ == "JSON"
    assert col.nullable is True


def test_persona_persists_citation_list(db_session):
    p = PatientPersona(
        persona_id="test-uuid-001",
        persona_code="TEST-001",
        name="Test Patient",
        age=54,
        gender="Male",
        specialty="cardiology",
        chief_complaint="chest pain",
        opening_statement="I've had chest pain since this morning.",
        symptoms=[],
        medical_history={},
        emotional_profile={"baseline": "calm", "triggers": [], "responses": {}},
        difficulty_level="intermediate",
        citations=SAMPLE_CITATIONS,
    )
    db_session.add(p)
    db_session.commit()
    db_session.refresh(p)
    assert p.citations[0]["qdrant_point_id"] == "dd6bc5b7-03b5-4b6b-83ba-35759e417012"
    assert p.citations[0]["is_australian"] is True


def test_importer_persists_citations(tmp_path, mem_engine, monkeypatch):
    """The importer must read the JSON ``citations`` array and persist it."""
    persona_file = tmp_path / "cardiology_999_test_persona.json"
    persona_file.write_text(
        json.dumps(
            {
                "id": "IMPORT-CIT-001",
                "persona_code": "IMPORT-CIT-001",
                "name": "Imported Patient",
                "age": 60,
                "gender": "Female",
                "specialty": "cardiology",
                "difficulty": "medium",
                "chief_complaint": "shortness of breath",
                "opening_statement": "I can't catch my breath.",
                "symptoms": [],
                "medical_history": {},
                "emotional_profile": {"baseline": "anxious"},
                "citations": SAMPLE_CITATIONS,
            }
        ),
        encoding="utf-8",
    )

    importer = _load_importer()
    # Route the importer at the isolated in-memory engine instead of the live DB.
    monkeypatch.setattr(importer, "get_database_url", lambda: "sqlite:///:memory:")
    monkeypatch.setattr(importer, "create_engine", lambda *a, **k: mem_engine)

    rc = importer.import_personas(source_dir=str(tmp_path))
    assert rc == 0

    Session = sessionmaker(bind=mem_engine)
    verify = Session()
    try:
        row = (
            verify.query(PatientPersona)
            .filter(PatientPersona.persona_code == "IMPORT-CIT-001")
            .first()
        )
        assert row is not None
        assert row.citations is not None
        assert row.citations[0]["qdrant_point_id"] == (
            "dd6bc5b7-03b5-4b6b-83ba-35759e417012"
        )
    finally:
        verify.close()


def test_importer_backfills_null_citations(tmp_path, mem_engine, monkeypatch):
    """Re-running the importer updates citations on an existing row that has
    NULL citations (idempotent backfill), without duplicating the persona."""
    # Seed an existing persona with NULL citations (simulating the 48 already
    # imported before the column existed).
    Seed = sessionmaker(bind=mem_engine)
    seed = Seed()
    try:
        seed.add(
            PatientPersona(
                persona_id="backfill-uuid-001",
                persona_code="BACKFILL-001",
                name="Existing Patient",
                age=45,
                gender="Male",
                specialty="respiratory",
                chief_complaint="cough",
                opening_statement="I've had a cough for weeks.",
                symptoms=[],
                medical_history={},
                emotional_profile={"baseline": "calm"},
                difficulty_level="intermediate",
                citations=None,
            )
        )
        seed.commit()
    finally:
        seed.close()

    persona_file = tmp_path / "respiratory_998_test_persona.json"
    persona_file.write_text(
        json.dumps(
            {
                "id": "BACKFILL-001",
                "persona_code": "BACKFILL-001",
                "name": "Existing Patient",
                "age": 45,
                "gender": "Male",
                "specialty": "respiratory",
                "difficulty": "medium",
                "chief_complaint": "cough",
                "opening_statement": "I've had a cough for weeks.",
                "symptoms": [],
                "medical_history": {},
                "emotional_profile": {"baseline": "calm"},
                "citations": SAMPLE_CITATIONS,
            }
        ),
        encoding="utf-8",
    )

    importer = _load_importer()
    monkeypatch.setattr(importer, "get_database_url", lambda: "sqlite:///:memory:")
    monkeypatch.setattr(importer, "create_engine", lambda *a, **k: mem_engine)

    rc = importer.import_personas(source_dir=str(tmp_path))
    assert rc == 0

    Session = sessionmaker(bind=mem_engine)
    verify = Session()
    try:
        rows = (
            verify.query(PatientPersona)
            .filter(PatientPersona.persona_code == "BACKFILL-001")
            .all()
        )
        assert len(rows) == 1  # no duplicate inserted
        assert rows[0].citations is not None
        assert rows[0].citations[0]["qdrant_point_id"] == (
            "dd6bc5b7-03b5-4b6b-83ba-35759e417012"
        )
    finally:
        verify.close()
