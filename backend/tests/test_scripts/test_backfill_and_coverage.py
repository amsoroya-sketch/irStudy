import json
from pathlib import Path

from scripts.backfill_condition_links import match_condition, _build_mcq_authoring_map
from scripts.seed_conditions import _mcq_name, normalize_specialty
from scripts.content_reconciliation import coverage_by_blueprint   # NEW function

_REPO_ROOT = Path(__file__).resolve().parents[3]


def test_match_condition_by_specialty_and_topic():       # Test 6
    conds = [{"id":1,"specialty":"respiratory","name":"Asthma"}]
    assert match_condition({"specialty":"respiratory","topic":"Asthma exacerbation"}, conds) == 1
    assert match_condition({"specialty":"cardiology","topic":"Asthma"}, conds) is None  # specialty guards


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
        assert normalize_specialty(item.get("specialty")) == normalize_specialty(cond["specialty"])
        linked_any = True
        break
    assert linked_any, "at least one real MCQ must link to a same-specialty condition"


def test_metadata_topic_only_mcq_derives_and_links():   # Test 9
    """An MCQ whose topic lives ONLY under metadata.topic (as respiratory/emergency
    files do) must still (a) seed a condition and (b) link back to it — the seed
    and the backfill share _mcq_name, so the derived name == the matched name."""
    from scripts.seed_conditions import derive_conditions

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

def test_coverage_report_counts_per_blueprint_area():    # Test 7
    rows = coverage_by_blueprint(
        conditions=[{"id":1,"amc_blueprint_area":"Respiratory Medicine"}],
        content={"mcq":[{"condition_id":1}], "osce":[], "persona":[], "emr_case":[]})
    assert rows["Respiratory Medicine"]["mcq"] == 1
