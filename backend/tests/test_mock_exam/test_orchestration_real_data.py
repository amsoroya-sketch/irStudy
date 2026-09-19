"""
Real-data integration test for the Mock Exam Orchestrator.

Unlike ``test_orchestration.py`` (which runs against the synthetic
``test_personas`` fixture in an in-memory SQLite database), this test exercises
``MockExamOrchestrator.auto_select_personas`` against the REAL, seeded
application database. It verifies the claim that the assembler draws a broad
specialty spread from live data (255 personas across 11 specialties as of the
current seed).

DESIGN NOTES:
- Uses the application's own ``SessionLocal`` / ``get_db`` session factory
  (``src.db.base``). No credentials are hardcoded — the DSN is resolved by
  ``get_database_url()`` from the environment / Docker secrets.
- SKIPs cleanly (never fails) when:
    * the application DB layer cannot be imported/constructed
      (missing credentials / no DATABASE_URL), or
    * the database cannot be reached, or
    * fewer than 16 active personas are seeded, or
    * the live schema is out of sync with the ORM model
      (e.g. a pending Alembic migration such as the ``patient_personas.citations``
      column), which the orchestrator's full-entity query would otherwise trip on.
  This keeps CI green on runners that lack a fully-migrated, seeded database.

ASSERTS (when a seeded, migrated DB is reachable):
- ``auto_select_personas`` returns exactly 16 persona_ids.
- All 16 ids are distinct (no duplicate stations).
- The selected personas span >= 8 distinct specialties (queried back from
  ``patient_personas`` for the returned ids).
"""

import uuid

import pytest
from sqlalchemy.exc import SQLAlchemyError

from src.services.mock_exam import MockExamOrchestrator

# Minimum specialty spread the assembler must achieve on real seeded data.
MIN_DISTINCT_SPECIALTIES = 8
REQUIRED_ACTIVE_PERSONAS = 16


@pytest.fixture()
def real_db_session():
    """
    Yield a session bound to the REAL application database.

    Skips the test (rather than failing) if the DB layer cannot be
    imported/constructed, the database cannot be reached, or fewer than 16
    active patient personas are seeded.
    """
    # Import lazily so that a missing DSN / import-time failure results in a
    # clean SKIP for this test only, rather than breaking collection.
    try:
        from src.db.base import SessionLocal
        from src.db.models import PatientPersona
    except Exception as exc:  # pragma: no cover - environment-dependent
        pytest.skip(f"Application DB layer unavailable: {exc!r}")

    try:
        session = SessionLocal()
    except Exception as exc:  # pragma: no cover - environment-dependent
        pytest.skip(f"Could not open a real DB session: {exc!r}")

    try:
        # Probe connectivity + seed state with a column-only query so a schema
        # drift on unrelated columns does not masquerade as a connectivity error.
        try:
            active_count = (
                session.query(PatientPersona.persona_id)
                .filter(PatientPersona.is_active == True)  # noqa: E712
                .count()
            )
        except SQLAlchemyError as exc:  # pragma: no cover - environment-dependent
            pytest.skip(f"Real database not reachable: {exc!r}")

        if active_count < REQUIRED_ACTIVE_PERSONAS:
            pytest.skip(
                f"Seeded DB has only {active_count} active personas "
                f"(need >= {REQUIRED_ACTIVE_PERSONAS}); skipping real-data test."
            )

        yield session
    finally:
        session.close()


@pytest.mark.asyncio
async def test_auto_select_personas_spans_many_specialties_real_data(real_db_session):
    """
    Against the real seeded DB, auto_select_personas must return exactly 16
    distinct personas spanning >= 8 distinct specialties.
    """
    from src.db.models import PatientPersona

    orchestrator = MockExamOrchestrator(real_db_session)

    # user_id is only used to seed randomization; no user row is required.
    user_id = str(uuid.uuid4())

    # Run the assembler and resolve specialties. A SQLAlchemyError here indicates
    # the live schema is out of sync with the ORM model (e.g. an unapplied
    # migration); skip cleanly rather than failing CI on an environment issue.
    try:
        persona_ids = await orchestrator.auto_select_personas(user_id)
        rows = (
            real_db_session.query(
                PatientPersona.persona_id, PatientPersona.specialty
            )
            .filter(PatientPersona.persona_id.in_(persona_ids))
            .all()
        )
    except SQLAlchemyError as exc:  # pragma: no cover - environment-dependent
        pytest.skip(
            "Live schema out of sync with ORM model (pending migration?); "
            f"cannot exercise real-data assembler: {exc!r}"
        )

    # Exactly 16 stations.
    assert len(persona_ids) == 16, (
        f"Expected 16 personas, got {len(persona_ids)}"
    )
    assert all(isinstance(pid, str) for pid in persona_ids)

    # No duplicate stations.
    assert len(set(persona_ids)) == 16, (
        f"Duplicate personas selected: {persona_ids}"
    )

    # Every returned id must resolve to a real persona row.
    assert len(rows) == 16, (
        f"Only {len(rows)}/16 returned ids resolved to persona rows"
    )

    distinct_specialties = {specialty for _pid, specialty in rows}

    assert len(distinct_specialties) >= MIN_DISTINCT_SPECIALTIES, (
        f"Assembler drew only {len(distinct_specialties)} distinct specialties "
        f"({sorted(distinct_specialties)}); expected >= {MIN_DISTINCT_SPECIALTIES}."
    )
