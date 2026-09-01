from src.db.models import Condition, MCQ, OSCE, PatientPersona, MockPatient

def test_condition_table_exists():                       # Test 1
    assert Condition.__tablename__ == "conditions"
    cols = Condition.__table__.columns
    for c in ("id", "condition_code", "name", "specialty", "amc_blueprint_area"):
        assert c in cols

def test_content_tables_have_condition_fk():             # Test 2
    for model in (MCQ, OSCE, PatientPersona, MockPatient):
        assert "condition_id" in model.__table__.columns
        assert model.__table__.columns["condition_id"].nullable is True

def test_condition_persists_and_links_mcq(db_session):   # Test 3
    c = Condition(condition_code="RESP-ASTHMA", name="Asthma",
                  specialty="respiratory", amc_blueprint_area="Respiratory Medicine")
    db_session.add(c); db_session.commit(); db_session.refresh(c)
    m = MCQ(question_id="MCQ-C-1", question_text="q", options={"A":"a","B":"b"},
            correct_answer="A", explanation="e", citation="x",
            specialty="respiratory", difficulty="medium", condition_id=c.id)
    db_session.add(m); db_session.commit(); db_session.refresh(m)
    assert m.condition_id == c.id
