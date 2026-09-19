"""On-disk (database-free) tests for condition backfill, seeding helpers and
blueprint coverage reporting.

Note on the disable below: ``backend/scripts/__init__.py`` extends the package
``__path__`` at runtime (pkgutil-style) so the repo-root ``scripts/`` modules
resolve under the ``scripts.*`` namespace. pylint/astroid perform static
analysis and do not execute that ``__path__`` extension, so they emit spurious
import-error / no-name-in-module for these first-party imports even though they
resolve correctly at runtime (verified by the passing test run). Scope the
disable to this import block only.
"""
# pylint: disable=import-error,no-name-in-module
import json
from pathlib import Path

from scripts.backfill_condition_links import (
    match_condition,
    _build_mcq_authoring_map,
    _emr_diagnosis,
)
from scripts.seed_conditions import (
    _mcq_name,
    _persona_name,
    normalize_specialty,
    resolve_specialty,
)
from scripts.content_reconciliation import coverage_by_blueprint
# pylint: enable=import-error,no-name-in-module

_REPO_ROOT = Path(__file__).resolve().parents[3]


def test_match_condition_by_specialty_and_topic():       # Test 6
    """match_condition links same-specialty topics and rejects cross-specialty."""
    conds = [{"id":1,"specialty":"respiratory","name":"Asthma"}]
    same_specialty = {"specialty":"respiratory","topic":"Asthma exacerbation"}
    assert match_condition(same_specialty, conds) == 1
    # Specialty guard: same topic text, wrong specialty -> no link.
    assert match_condition({"specialty":"cardiology","topic":"Asthma"}, conds) is None


def test_real_mcq_question_id_links_to_expected_specialty_condition():   # Test 8
    """A real authored MCQ (recovered by question_id) links to a same-specialty
    condition — proving the authoring-file topic map (not a missing DB column)
    drives MCQ linking. Uses on-disk data only (no database)."""
    conditions = json.loads(
        (_REPO_ROOT / "data" / "amc_blueprints" / "conditions.json").read_text(encoding="utf-8")
    )["conditions"]
    # conditions.json carries no PK (ids live only in the DB); assign synthetic
    # 1-based ids so match_condition can return a concrete id in this offline test.
    for i, c in enumerate(conditions, start=1):
        c["id"] = i

    mcq_map = _build_mcq_authoring_map()
    assert mcq_map, "authoring MCQ map should not be empty"

    # Find the first authored MCQ that both maps to a condition AND has a
    # normalizable specialty, then assert the link is specialty-consistent.
    linked_any = False
    for _qid, item in mcq_map.items():
        cid = match_condition(item, conditions, name_fn=_mcq_name)
        if cid is None:
            continue
        cond = next(c for c in conditions if c["id"] == cid)
        # Use the SAME widened resolution the backfill uses (own specialty ->
        # metadata.specialty -> filename hint), so an authored MCQ that links via
        # an inferred specialty is still asserted specialty-consistent.
        assert resolve_specialty(item) == normalize_specialty(cond["specialty"])
        linked_any = True
        break
    assert linked_any, "at least one real MCQ must link to a same-specialty condition"


def test_metadata_topic_only_mcq_derives_and_links():   # Test 9
    """An MCQ whose topic lives ONLY under metadata.topic (as respiratory/emergency
    files do) must still (a) seed a condition and (b) link back to it — the seed
    and the backfill share _mcq_name, so the derived name == the matched name."""
    # See module docstring re: astroid vs runtime __path__ extension.
    from scripts.seed_conditions import derive_conditions  # pylint: disable=import-error,no-name-in-module

    mcq = {"specialty": "respiratory", "metadata": {"topic": "Asthma"}}
    conds = derive_conditions(mcqs=[mcq], osces=[], personas=[])
    assert any(
        c["name"] == "Asthma" and c["specialty"] == "respiratory" for c in conds
    ), "metadata.topic-only MCQ should derive an 'Asthma' respiratory condition"

    for i, c in enumerate(conds, start=1):
        c["id"] = i
    cid = match_condition(mcq, conds, name_fn=_mcq_name)
    assert cid is not None
    cond = next(c for c in conds if c["id"] == cid)
    assert cond["name"] == "Asthma" and cond["specialty"] == "respiratory"

def test_emr_diagnosis_extracts_primary_impression_not_differentials():   # Test 10
    """``_emr_diagnosis`` returns the leading clause of the FIRST SOAP assessment
    line (the primary impression), and ignores later lines (differentials). A
    MockPatient has NO diagnosis column, so this is the authoritative diagnosis
    text the backfill matches on."""
    vc = {
        "expected": {
            "assessment": [
                "Acute coronary syndrome — likely STEMI given crushing pain (confirm on ECG)",
                "Consider pulmonary embolism and pericarditis as differentials",
            ]
        }
    }
    assert _emr_diagnosis(vc) == "Acute coronary syndrome"
    # No assessment / wrong shapes -> None (never fabricated).
    assert _emr_diagnosis({"expected": {"assessment": []}}) is None
    assert _emr_diagnosis({}) is None
    assert _emr_diagnosis(None) is None


def test_emr_case_links_by_diagnosis_not_symptom():   # Test 11
    """The EMR fix: an EMR case links to a same-specialty condition via its
    EXPECTED DIAGNOSIS (from validation_criteria.expected.assessment), NOT its
    presenting_complaint (a SYMPTOM that never matches a condition NAME). This is
    the exact root cause the backfill change addresses. Uses ``_persona_name`` as
    the extractor (the emr_case name_fn), and remains specialty-guarded."""
    conds = [{"id": 7, "specialty": "cardiology", "name": "Acute Coronary Syndrome"}]

    vc = {
        "expected": {
            "assessment": ["Acute coronary syndrome — likely STEMI given crushing pain"]
        }
    }
    # EMR item as the backfill builds it: expected_diagnosis (from the SOAP "A"),
    # falling back to topic (OSCE title) then chief_complaint (presenting_complaint).
    emr_item = {
        "specialty": "cardiology",
        "expected_diagnosis": _emr_diagnosis(vc),
        "topic": None,
        "chief_complaint": "Central crushing chest pain for 45 minutes",
    }
    assert match_condition(emr_item, conds, name_fn=_persona_name) == 7

    # Symptom-only (the OLD behaviour): presenting_complaint alone must NOT link —
    # proving the diagnosis key, not the symptom, drives the match.
    symptom_only = {
        "specialty": "cardiology",
        "expected_diagnosis": None,
        "topic": None,
        "chief_complaint": "Central crushing chest pain for 45 minutes",
    }
    assert match_condition(symptom_only, conds, name_fn=_persona_name) is None

    # Specialty guard still holds: right diagnosis text, wrong specialty -> no link.
    wrong_spec = {**emr_item, "specialty": "respiratory"}
    assert match_condition(wrong_spec, conds, name_fn=_persona_name) is None


def test_coverage_report_counts_per_blueprint_area():    # Test 7
    """coverage_by_blueprint tallies linked content per AMC blueprint area."""
    rows = coverage_by_blueprint(
        conditions=[{"id":1,"amc_blueprint_area":"Respiratory Medicine"}],
        content={"mcq":[{"condition_id":1}], "osce":[], "persona":[], "emr_case":[]})
    assert rows["Respiratory Medicine"]["mcq"] == 1
