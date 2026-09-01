# Phase 2 hardening tests (EMR assessment): surface the authoritative pass/fail +
# missing_elements to the client, and never fabricate a graded FAIL on an AI outage.
#
# These tests drive the fix that:
#   1. Adds pass_fail / missing_elements / captured / completeness / ai_unavailable
#      to the ValidationResult contract on BOTH the submit and GET read paths.
#   2. Leaves an AI-outage submission un-graded (re-submittable) instead of writing
#      a permanent 0.0 FAIL.
import json
from unittest.mock import patch

import pytest

from src.services.emr.assessment_engine import assess_submission
from src.db.models import EMRSession, EMRValidationResult


# STEMI answer-key mirrored from tests/test_emr/conftest.py::seeded_hard_case.
#   must_not_miss = ["aortic dissection considered"]
#   critical_errors = ["nitrates given despite ... recent sildenafil"]
GOOD_SOAP = {
    "subjective": "SOCRATES of pain documented, cardiac risk factors, denies sildenafil use",
    "objective": "BP both arms, ECG done <10min showing STEMI, obs recorded",
    "assessment": "STEMI primary; aortic dissection considered and excluded",
    "plan": "aspirin 300mg chewed, serial troponin, STEMI pathway / cardiology, analgesia",
}


def _claude_json(**over):
    """Claude-shaped grading payload (what ClaudeValidator.validate returns)."""
    base = {
        "overall_score": 12.0,
        "completeness": {"subjective": 80, "objective": 80, "assessment": 80, "plan": 80},
        "captured": ["SOCRATES of pain", "aortic dissection considered"],
        "missing_elements": [],
        "critical_errors_committed": [],
        "accuracy_notes": [],
        "category_scores": {
            "History_Taking": 3, "Clinical_Reasoning": 3, "Documentation_Quality": 2,
            "Patient_Safety": 2, "Professional_Communication": 2,
        },
        "strengths": ["structured"],
        "improvements": ["more detail"],
    }
    base.update(over)
    return base


def _fallback_json():
    """Outage-shaped payload: matches ClaudeValidator._fallback_response()."""
    return {
        "overall_score": 0.0,
        "completeness": {"subjective": 0, "objective": 0, "assessment": 0, "plan": 0},
        "captured": [],
        "missing_elements": [],
        "critical_errors_committed": [],
        "accuracy_notes": ["Claude AI validation unavailable - fallback used"],
        "category_scores": {},
        "strengths": [],
        "improvements": [],
        "ai_unavailable": True,
    }


def _submit(client, headers, sid, soap=GOOD_SOAP):
    return client.post(
        f"/api/v1/emr/sessions/{sid}/submit",
        json={"final_soap_note": soap},
        headers=headers,
    )


def _patch_claude(payload):
    """Patch the async ClaudeValidator.validate so the REAL engine (decide_pass_fail)
    runs end-to-end through the endpoint."""
    async def _fake_validate(*args, **kwargs):
        return payload
    return patch(
        "src.services.emr.validators.claude_validator.ClaudeValidator.validate",
        new=_fake_validate,
    )


# ---------------------------------------------------------------------------
# Bug 1: authoritative pass_fail + missing_elements reach the client
# ---------------------------------------------------------------------------
def test_get_validation_surfaces_authoritative_fail_below_threshold(
    client, db_session, seeded_hard_case, auth_headers
):
    """8 <= overall_score < 9 must read back as pass_fail == False on the GET path."""
    sid = seeded_hard_case.session_id
    with _patch_claude(_claude_json(overall_score=8.5)):
        assert _submit(client, auth_headers, sid).status_code == 200

    r = client.get(f"/api/v1/emr/validation/{sid}", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "graded"
    vr = data["validation_results"]
    assert vr is not None
    assert vr["overall_score"] == 8.5
    # Authoritative decision must be present AND False (frontend must not recompute).
    assert vr["pass_fail"] is False


def test_get_validation_surfaces_fail_on_critical_error_high_score(
    client, db_session, seeded_hard_case, auth_headers
):
    """A committed critical error is an automatic FAIL even at a high score."""
    sid = seeded_hard_case.session_id
    with _patch_claude(_claude_json(
        overall_score=13.0,
        critical_errors_committed=["nitrates given despite recent sildenafil"],
    )):
        assert _submit(client, auth_headers, sid).status_code == 200

    r = client.get(f"/api/v1/emr/validation/{sid}", headers=auth_headers)
    data = r.json()
    vr = data["validation_results"]
    assert vr["overall_score"] == 13.0
    assert vr["pass_fail"] is False


def test_missing_elements_surfaced_when_must_not_miss_omitted(
    client, db_session, seeded_hard_case, auth_headers
):
    """The omitted must_not_miss element appears in missing_elements on submit AND GET,
    and forces a FAIL."""
    sid = seeded_hard_case.session_id
    omitted = "aortic dissection considered"  # in the case must_not_miss list
    with _patch_claude(_claude_json(
        overall_score=12.0, captured=["SOCRATES of pain"], missing_elements=[omitted],
    )):
        submit = _submit(client, auth_headers, sid)
    assert submit.status_code == 200
    sub_vr = submit.json()["validation_results"]
    assert omitted in sub_vr["missing_elements"]
    assert sub_vr["pass_fail"] is False

    r = client.get(f"/api/v1/emr/validation/{sid}", headers=auth_headers)
    get_vr = r.json()["validation_results"]
    assert omitted in get_vr["missing_elements"]
    assert get_vr["pass_fail"] is False


# ---------------------------------------------------------------------------
# Rubric sanity: category_scores stay on the 0-3 AMC scale (do NOT change scale)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_category_scores_within_0_3_range(seeded_hard_case):
    criteria = seeded_hard_case.patient.validation_criteria
    with _patch_claude(_claude_json()):
        out = await assess_submission(GOOD_SOAP, criteria, layers_1_2={"score": 10})
    cs = out["category_scores"]
    assert cs, "category_scores should not be empty"
    assert all(0 <= float(v) <= 3 for v in cs.values())


# ---------------------------------------------------------------------------
# Bug 2: AI outage must NOT fabricate a graded FAIL; must be re-submittable
# ---------------------------------------------------------------------------
def test_ai_unavailable_does_not_grade_and_allows_resubmit(
    client, db_session, seeded_hard_case, auth_headers
):
    sid = seeded_hard_case.session_id

    # 1) First submit hits an AI outage -> not graded, no fail row, flagged.
    with patch(
        "src.api.v1.emr.sessions.assess_submission_sync", return_value=_fallback_json()
    ):
        outage = _submit(client, auth_headers, sid)
    assert outage.status_code == 200
    body = outage.json()
    assert body["status"] == "in_progress"          # NOT graded
    assert body["validation_score"] is None
    assert body["validation_results"]["ai_unavailable"] is True
    assert body["validation_results"]["pass_fail"] is None
    assert body["message"]                            # surfaces temporary-unavailable message

    # DB: session left un-graded, NO EMRValidationResult fabricated FAIL row.
    db_session.expire_all()
    s = db_session.query(EMRSession).filter_by(id=sid).first()
    assert s.status == "in_progress"
    assert s.validation_score is None
    assert db_session.query(EMRValidationResult).filter_by(session_id=sid).count() == 0

    # GET read path must not read back a graded PASS/FAIL for the outage session.
    r = client.get(f"/api/v1/emr/validation/{sid}", headers=auth_headers)
    gdata = r.json()
    assert gdata["status"] == "in_progress"
    gvr = gdata["validation_results"]
    if gvr is not None:
        assert gvr["pass_fail"] is None
        assert gvr["ai_unavailable"] is True

    # 2) Re-submit once Claude is back -> the assessment actually runs and grades.
    with patch(
        "src.api.v1.emr.sessions.assess_submission_sync",
        return_value=_claude_json(overall_score=12.0, pass_fail=True),
    ):
        rerun = _submit(client, auth_headers, sid)
    assert rerun.status_code == 200
    rbody = rerun.json()
    assert rbody["status"] == "graded"
    assert rbody["validation_score"] == 12.0
    assert rbody["validation_results"]["pass_fail"] is True

    db_session.expire_all()
    s2 = db_session.query(EMRSession).filter_by(id=sid).first()
    assert s2.status == "graded"
    # Exactly one validation-result row after the successful re-run.
    assert db_session.query(EMRValidationResult).filter_by(session_id=sid).count() == 1
    # Only one final-submission SOAP note (re-submit must not duplicate).
    from src.db.models import EMRSOAPNote
    finals = db_session.query(EMRSOAPNote).filter_by(
        session_id=sid, is_final_submission=True
    ).count()
    assert finals == 1
