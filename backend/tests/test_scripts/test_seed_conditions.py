from scripts.seed_conditions import derive_conditions

def test_derive_conditions_from_content():               # Test 4
    mcqs = [{"specialty":"respiratory","topic":"Asthma"},
            {"specialty":"respiratory","topic":"asthma"},   # dupe (case)
            {"specialty":"cardiology","topic":"STEMI"}]
    conds = derive_conditions(mcqs=mcqs, osces=[], personas=[])
    names = {(c["specialty"], c["name"].lower()) for c in conds}
    assert ("respiratory","asthma") in names and ("cardiology","stemi") in names
    assert len(conds) == 2                                  # deduped, normalized

def test_every_condition_maps_to_valid_specialty():      # Test 5
    from src.db.models import MedicalSpecialty
    valid = {e.value for e in MedicalSpecialty}
    conds = derive_conditions(mcqs=[{"specialty":"cardiology","topic":"AF"}], osces=[], personas=[])
    assert all(c["specialty"] in valid for c in conds)
