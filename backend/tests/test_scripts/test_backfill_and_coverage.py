from scripts.backfill_condition_links import match_condition
from scripts.content_reconciliation import coverage_by_blueprint   # NEW function

def test_match_condition_by_specialty_and_topic():       # Test 6
    conds = [{"id":1,"specialty":"respiratory","name":"Asthma"}]
    assert match_condition({"specialty":"respiratory","topic":"Asthma exacerbation"}, conds) == 1
    assert match_condition({"specialty":"cardiology","topic":"Asthma"}, conds) is None  # specialty guards

def test_coverage_report_counts_per_blueprint_area():    # Test 7
    rows = coverage_by_blueprint(
        conditions=[{"id":1,"amc_blueprint_area":"Respiratory Medicine"}],
        content={"mcq":[{"condition_id":1}], "osce":[], "persona":[], "emr_case":[]})
    assert rows["Respiratory Medicine"]["mcq"] == 1
