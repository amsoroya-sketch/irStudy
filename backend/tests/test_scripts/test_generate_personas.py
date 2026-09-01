# FILE: backend/tests/test_scripts/test_generate_personas.py
from unittest.mock import MagicMock
from scripts.generate_personas import PersonaGenerator, validate_persona, REQUIRED_FIELDS

def _gen(claude_json, rag_hits):
    claude = MagicMock(); claude.generate.return_value = claude_json
    rag = MagicMock(); rag.search_similar.return_value = rag_hits
    return PersonaGenerator(claude_client=claude, rag_service=rag)

VALID = {"name":"Jane","age":54,"gender":"female","specialty":"neurology",
         "difficulty":"medium","chief_complaint":"sudden weakness",
         "opening_statement":"...", "symptoms":{}, "past_medical_history":[],
         "medications":[], "allergies":[], "examination_findings":{},
         "expected_diagnosis":"Ischaemic stroke","expected_management":"...",
         "critical_errors":["missed thrombolysis window"],"learning_objectives":["..."]}

def test_generated_persona_has_required_fields():        # Test 1
    g=_gen(VALID, [{"qdrant_point_id":"550e8400-e29b-41d4-a716-446655440000","score":0.8,"is_australian":True,"source":"eTG"}])
    p=g.generate(specialty="neurology", condition="Ischaemic stroke", difficulty="medium")
    assert all(f in p for f in REQUIRED_FIELDS)

def test_specialty_and_difficulty_honoured():            # Test 2
    g=_gen(VALID, [{"qdrant_point_id":"id","score":0.8,"is_australian":True,"source":"eTG"}])
    p=g.generate(specialty="neurology", condition="Stroke", difficulty="medium")
    assert p["specialty"]=="neurology" and p["difficulty"]=="medium"

def test_persona_grounded_with_citation_pointid():       # Test 3
    g=_gen(VALID, [{"qdrant_point_id":"550e8400-e29b-41d4-a716-446655440000","score":0.82,"is_australian":True,"source":"eTG"}])
    p=g.generate(specialty="neurology", condition="Stroke", difficulty="medium")
    assert p["citations"] and all(c["qdrant_point_id"] for c in p["citations"])

def test_ungrounded_persona_rejected():                  # Test 4  (no RAG hit ≥0.65)
    g=_gen(VALID, [])
    p=g.generate(specialty="neurology", condition="Stroke", difficulty="medium")
    assert p["needs_review"] is True and p["citations"]==[]

def test_validate_persona_rejects_missing_fields():      # Test 5
    bad=dict(VALID); del bad["expected_diagnosis"]
    errs=validate_persona(bad); assert any("expected_diagnosis" in e for e in errs)

def test_never_uses_local_llm():                          # Test 6  (guard the project rule)
    import inspect, scripts.generate_personas as m
    src=inspect.getsource(m)
    assert "ollama" not in src.lower() and "localhost:11434" not in src
