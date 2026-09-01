"""
Tests for the EMR case catalog picker (Phase 1a).

Covers:
- GET /api/v1/emr/cases  (case catalog for the "pick a case and practice" picker)
- start_session specialty-whitelist reconciliation (previously-rejected
  authored specialties like emergency_medicine must now be accepted).

TDD: written BEFORE implementation.

SECURITY:
- validation_criteria (the per-case answer key) MUST NOT leak to the client.
- Auth is required for the catalog.
"""

from uuid import uuid4

import pytest

from src.db.models import MockPatient


CASES_URL = "/api/v1/emr/cases"
START_URL = "/api/v1/emr/sessions/start"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _seed_patient(
    db_session,
    *,
    mrn: str,
    name: str = "Test Patient",
    age: int = 55,
    gender: str = "Male",
    presenting_complaint: str = "Chest pain",
    specialty: str = "cardiology",
    difficulty: str = "medium",
    with_criteria: bool = False,
) -> MockPatient:
    """Insert a MockPatient row and return it (committed)."""
    patient = MockPatient(
        id=uuid4(),
        mrn=mrn,
        name=name,
        age=age,
        gender=gender,
        presenting_complaint=presenting_complaint,
        vital_signs={"hr": 90, "bp": "130/80"},
        medical_history=["hypertension"],
        specialty=specialty,
        difficulty=difficulty,
        validation_criteria=(
            {
                "presenting_scenario": "secret scenario",
                "expected": {"plan": ["aspirin 300mg"]},
                "critical_errors": ["nitrates in RV infarct"],
            }
            if with_criteria
            else None
        ),
    )
    db_session.add(patient)
    db_session.commit()
    db_session.refresh(patient)
    return patient


# ---------------------------------------------------------------------------
# GET /emr/cases
# ---------------------------------------------------------------------------


def test_list_cases_requires_auth(client):
    """The catalog is a protected endpoint (no token -> 401)."""
    response = client.get(CASES_URL)
    assert response.status_code == 401


def test_list_cases_returns_all_with_shape(client, auth_headers, db_session):
    """Returns every selectable case with the {total, cases: [...]} shape."""
    _seed_patient(db_session, mrn="EMRP-A", specialty="cardiology", difficulty="hard")
    _seed_patient(db_session, mrn="EMRP-B", specialty="respiratory", difficulty="medium")
    _seed_patient(db_session, mrn="EMRP-C", specialty="neurology", difficulty="medium")

    response = client.get(CASES_URL, headers=auth_headers)
    assert response.status_code == 200

    data = response.json()
    assert data["total"] == 3
    assert isinstance(data["cases"], list)
    assert len(data["cases"]) == 3

    item = data["cases"][0]
    for field in (
        "id",
        "mrn",
        "name",
        "age",
        "gender",
        "presenting_complaint",
        "specialty",
        "difficulty",
    ):
        assert field in item, f"missing field {field} in case item"


def test_list_cases_does_not_expose_validation_criteria(client, auth_headers, db_session):
    """The answer key (validation_criteria) must never be serialised to the client."""
    _seed_patient(db_session, mrn="EMRP-SECRET", specialty="cardiology", with_criteria=True)

    response = client.get(CASES_URL, headers=auth_headers)
    assert response.status_code == 200

    body_text = response.text
    assert "validation_criteria" not in body_text
    assert "critical_errors" not in body_text
    assert "secret scenario" not in body_text

    for item in response.json()["cases"]:
        assert "validation_criteria" not in item


def test_case_id_is_patient_id(client, auth_headers, db_session):
    """The `id` returned is the mock-patient UUID used to start a session."""
    patient = _seed_patient(db_session, mrn="EMRP-ID", specialty="urology")

    response = client.get(CASES_URL, headers=auth_headers)
    assert response.status_code == 200

    ids = {c["id"] for c in response.json()["cases"]}
    assert str(patient.id) in ids


def test_filter_by_specialty(client, auth_headers, db_session):
    _seed_patient(db_session, mrn="EMRP-CARD", specialty="cardiology")
    _seed_patient(db_session, mrn="EMRP-RESP", specialty="respiratory")

    response = client.get(
        CASES_URL, headers=auth_headers, params={"specialty": "cardiology"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert all(c["specialty"] == "cardiology" for c in data["cases"])


def test_filter_by_difficulty(client, auth_headers, db_session):
    _seed_patient(db_session, mrn="EMRP-HARD", specialty="cardiology", difficulty="hard")
    _seed_patient(db_session, mrn="EMRP-MED", specialty="cardiology", difficulty="medium")

    response = client.get(
        CASES_URL, headers=auth_headers, params={"difficulty": "hard"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert all(c["difficulty"] == "hard" for c in data["cases"])


def test_combined_filter(client, auth_headers, db_session):
    _seed_patient(db_session, mrn="EMRP-1", specialty="cardiology", difficulty="hard")
    _seed_patient(db_session, mrn="EMRP-2", specialty="cardiology", difficulty="medium")
    _seed_patient(db_session, mrn="EMRP-3", specialty="respiratory", difficulty="hard")

    response = client.get(
        CASES_URL,
        headers=auth_headers,
        params={"specialty": "cardiology", "difficulty": "hard"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["cases"][0]["mrn"] == "EMRP-1"


def test_deterministic_ordering(client, auth_headers, db_session):
    """Ordered by (specialty, difficulty, mrn) so the picker is stable."""
    # Seed intentionally out of order.
    _seed_patient(db_session, mrn="EMRP-Z", specialty="respiratory", difficulty="medium")
    _seed_patient(db_session, mrn="EMRP-A", specialty="cardiology", difficulty="medium")
    _seed_patient(db_session, mrn="EMRP-B", specialty="cardiology", difficulty="hard")
    _seed_patient(db_session, mrn="EMRP-C", specialty="cardiology", difficulty="hard")

    response = client.get(CASES_URL, headers=auth_headers)
    assert response.status_code == 200

    cases = response.json()["cases"]
    keys = [(c["specialty"], c["difficulty"], c["mrn"]) for c in cases]
    assert keys == sorted(keys)
    # Explicit expected order.
    assert [c["mrn"] for c in cases] == ["EMRP-B", "EMRP-C", "EMRP-A", "EMRP-Z"]


def test_empty_catalog_returns_zero(client, auth_headers, db_session):
    response = client.get(CASES_URL, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["cases"] == []


# ---------------------------------------------------------------------------
# start_session specialty-whitelist reconciliation
# ---------------------------------------------------------------------------


def test_start_session_accepts_previously_rejected_specialty(
    client, auth_headers, db_session
):
    """
    emergency_medicine is one of the 12 authored specialties but was NOT in the
    old hardcoded whitelist, so it used to 400. It must now be accepted and
    start a session against a real seeded patient.
    """
    _seed_patient(
        db_session,
        mrn="EMRP-EM",
        specialty="emergency_medicine",
        difficulty="hard",
    )

    response = client.post(
        START_URL,
        json={"specialty": "emergency_medicine"},
        headers=auth_headers,
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["specialty"] == "emergency_medicine"
    assert data["status"] == "in_progress"


@pytest.mark.parametrize(
    "specialty",
    [
        "obstetrics_gynaecology",
        "general_practice",
        "ophthalmology",
        "psychiatry",
        "surgery",
        "urology",
    ],
)
def test_start_session_accepts_all_authored_specialties(
    client, auth_headers, db_session, specialty
):
    """Every authored specialty must be accepted by the whitelist."""
    _seed_patient(db_session, mrn=f"EMRP-{specialty}", specialty=specialty)

    response = client.post(
        START_URL,
        json={"specialty": specialty},
        headers=auth_headers,
    )
    assert response.status_code == 201, response.text
    assert response.json()["specialty"] == specialty


def test_start_session_still_rejects_truly_invalid_specialty(client, auth_headers):
    """An unknown specialty must still 400 (existing contract preserved)."""
    response = client.post(
        START_URL,
        json={"specialty": "not_a_specialty"},
        headers=auth_headers,
    )
    assert response.status_code == 400
    assert "validation" in response.json()["detail"].lower()
