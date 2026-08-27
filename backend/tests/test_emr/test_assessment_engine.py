# EMR Documentation Assessment Engine tests (PRD-EMR-PRACTICE-001)
import json
from unittest.mock import patch, MagicMock
import pytest

from src.services.emr.validators.claude_validator import ClaudeValidator
from src.services.emr.assessment_engine import assess_submission, decide_pass_fail

# ---- fixtures -------------------------------------------------------------
STEMI_CRITERIA = {
    "presenting_scenario": "58yo male, central crushing chest pain 40 min, diaphoretic.",
    "task": "Document assessment and initial management as admitting RMO.",
    "expected": {
        "subjective": ["SOCRATES of pain", "cardiac risk factors", "sildenafil/erectile-drug use"],
        "objective": ["BP in both arms", "ECG within 10 minutes"],
        "assessment": ["ACS/STEMI primary", "aortic dissection considered"],
        "plan": ["aspirin 300 mg chewed", "serial troponin", "STEMI pathway / cardiology", "analgesia"],
    },
    "critical_errors": ["nitrates given despite hypotension / inferior-RV infarct / recent sildenafil"],
    "must_not_miss": ["aortic dissection considered"],
}

def _claude_json(**over):
    base = {
        "overall_score": 12.0, "completeness": {"subjective": 80, "objective": 80,
        "assessment": 80, "plan": 80}, "captured": ["SOCRATES of pain"], "missing_elements": [],
        "critical_errors_committed": [], "accuracy_notes": [],
        "category_scores": {"History_Taking": 3, "Clinical_Reasoning": 3, "Documentation_Quality": 2,
                            "Patient_Safety": 2, "Professional_Communication": 2},
        "strengths": ["structured"], "improvements": ["more detail"],
    }
    base.update(over)
    return base

def _mock_anthropic(payload):
    """Return a MagicMock Anthropic client whose messages.create -> text=json.dumps(payload)."""
    client = MagicMock()
    msg = MagicMock()
    msg.content = [MagicMock(text=json.dumps(payload))]
    client.messages.create.return_value = msg
    return client

GOOD_SOAP = {"subjective": "SOCRATES pain, risk factors, denies sildenafil",
             "objective": "BP both arms, ECG done <10min, STEMI",
             "assessment": "STEMI; consider aortic dissection",
             "plan": "aspirin 300mg chewed, troponin, cardiology, analgesia"}

# ---- Test 1: critical error committed -> FAIL -----------------------------
def test_critical_error_forces_fail():
    result = _claude_json(overall_score=13.0,
        critical_errors_committed=["nitrates given despite recent sildenafil"])
    assert decide_pass_fail(result, STEMI_CRITERIA) is False

# ---- Test 2: must-not-miss omitted -> FAIL --------------------------------
def test_must_not_miss_omission_fails():
    result = _claude_json(overall_score=12.0,
        missing_elements=["aortic dissection considered"])
    assert decide_pass_fail(result, STEMI_CRITERIA) is False

# ---- Test 3: clean high score -> PASS -------------------------------------
def test_complete_note_passes():
    result = _claude_json(overall_score=12.0, critical_errors_committed=[], missing_elements=[])
    assert decide_pass_fail(result, STEMI_CRITERIA) is True

# ---- Test 4: below threshold -> FAIL --------------------------------------
def test_below_threshold_fails():
    result = _claude_json(overall_score=8.5, critical_errors_committed=[], missing_elements=[])
    assert decide_pass_fail(result, STEMI_CRITERIA) is False

# ---- Test 5: engine calls Claude with the answer-key in patient_context ---
@pytest.mark.asyncio
async def test_answer_key_threaded_into_prompt():
    with patch("src.services.emr.validators.claude_validator.anthropic.Anthropic",
               return_value=_mock_anthropic(_claude_json())), \
         patch("src.services.emr.validators.claude_validator.VaultClient") as V:
        V.return_value.get_secret.return_value = {"value": "sk-test"}
        captured = {}
        orig = ClaudeValidator._build_validation_prompt.__func__
        def spy(cls, soap, patient, rb):
            p = orig(cls, soap, patient, rb); captured["prompt"] = p; return p
        with patch.object(ClaudeValidator, "_build_validation_prompt", classmethod(spy)):
            await ClaudeValidator.validate(GOOD_SOAP, {"validation_criteria": STEMI_CRITERIA}, {})
        assert "critical_errors" in captured["prompt"] or "must_not_miss" in captured["prompt"]
        assert "aortic dissection" in captured["prompt"]

# ---- Test 6: completeness reflects captured vs missing --------------------
def test_completeness_present_in_result():
    result = _claude_json(completeness={"subjective": 50, "objective": 40, "assessment": 60, "plan": 70})
    assert set(result["completeness"]) == {"subjective", "objective", "assessment", "plan"}
    assert all(0 <= v <= 100 for v in result["completeness"].values())

# ---- Test 7: PHI anonymised before Claude call ----------------------------
@pytest.mark.asyncio
async def test_phi_anonymised_before_call():
    client = _mock_anthropic(_claude_json())
    with patch("src.services.emr.validators.claude_validator.anthropic.Anthropic", return_value=client), \
         patch("src.services.emr.validators.claude_validator.VaultClient") as V:
        V.return_value.get_secret.return_value = {"value": "sk-test"}
        await ClaudeValidator.validate(
            {"subjective": "John Smith, MRN 1234567, chest pain", "objective": "", "assessment": "", "plan": ""},
            {"validation_criteria": STEMI_CRITERIA}, {})
        sent = client.messages.create.call_args.kwargs["messages"][0]["content"]
        assert "John Smith" not in sent and "1234567" not in sent

# ---- Test 8: vault key missing -> fallback (no crash) ---------------------
@pytest.mark.asyncio
async def test_missing_vault_key_falls_back():
    with patch("src.services.emr.validators.claude_validator.VaultClient") as V:
        V.return_value.get_secret.return_value = None
        out = await ClaudeValidator.validate(GOOD_SOAP, {"validation_criteria": STEMI_CRITERIA}, {})
        assert "overall_score" in out  # fallback response shape

# ---- Test 9: assess_submission returns the full result contract ----------
@pytest.mark.asyncio
async def test_assess_submission_contract():
    with patch("src.services.emr.validators.claude_validator.anthropic.Anthropic",
               return_value=_mock_anthropic(_claude_json())), \
         patch("src.services.emr.validators.claude_validator.VaultClient") as V:
        V.return_value.get_secret.return_value = {"value": "sk-test"}
        out = await assess_submission(GOOD_SOAP, STEMI_CRITERIA, layers_1_2={"score": 10})
        for k in ("overall_score", "pass_fail", "completeness", "missing_elements",
                  "critical_errors_committed", "category_scores"):
            assert k in out

# ---- Test 10: submit persists real score + EMRValidationResult row --------
def test_submit_persists_validation_result(client, db_session, seeded_hard_case, auth_headers):
    # seeded_hard_case = a MockPatient with STEMI_CRITERIA + an in_progress EMRSession
    sid = seeded_hard_case.session_id
    with patch("src.api.v1.emr.sessions.assess_submission_sync",
               return_value=_claude_json(overall_score=6.0,
               critical_errors_committed=["nitrates given"])):
        r = client.post(f"/api/v1/emr/sessions/{sid}/submit",
                        json={"final_soap_note": GOOD_SOAP}, headers=auth_headers)
    assert r.status_code == 200
    from src.db.models import EMRSession, EMRValidationResult
    s = db_session.query(EMRSession).filter_by(id=sid).first()
    assert s.validation_score == 6.0 and s.status == "graded"
    vr = db_session.query(EMRValidationResult).filter_by(session_id=sid).first()
    assert vr is not None and vr.pass_fail is False

# ---- Test 11: MockPatient ORM now maps validation_criteria ----------------
def test_mockpatient_maps_validation_criteria(db_session):
    from src.db.models import MockPatient
    cols = MockPatient.__table__.columns.keys()
    for c in ("validation_criteria", "source_osce_id", "physical_exam_findings",
              "investigation_results", "medications", "allergies", "demographics"):
        assert c in cols

# ---- Test 12: no critical error + all must-not-miss present + >=9 -> PASS --
def test_borderline_pass():
    result = _claude_json(overall_score=9.0, missing_elements=["cardiac risk factors"],
                          critical_errors_committed=[])
    # 'cardiac risk factors' is NOT in must_not_miss -> still a PASS at >=9
    assert decide_pass_fail(result, STEMI_CRITERIA) is True
