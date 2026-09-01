"""
TDD Tests for import_mcqs.py preserving structured citations (PRD-MCQ-CITATION-001).

The importer must stop collapsing references[] into a flat string ONLY —
it must also preserve the structured array (with qdrant_point_id when present)
into the `citations` field so downstream remediation has something to work with.
"""
from scripts.import_mcqs import transform_mcq


def test_import_preserves_structured_citations():
    raw = {"id": "MCQ-T-002", "specialty": "respiratory", "correct_answer": "A",
           "question": {"stem": "q", "options": {"A": "a", "B": "b"}}, "explanation": "e",
           "references": [{"title": "eTG", "year": "2024", "page": "p.1",
                           "qdrant_point_id": "550e8400-e29b-41d4-a716-446655440000"}]}
    rec = transform_mcq(raw)
    assert isinstance(rec["citations"], list)
    assert rec["citations"][0]["qdrant_point_id"] == "550e8400-e29b-41d4-a716-446655440000"
    assert isinstance(rec["citation"], str) and len(rec["citation"]) <= 500


def test_import_handles_missing_references():
    raw = {"id": "MCQ-T-003", "specialty": "respiratory", "correct_answer": "A",
           "question": {"stem": "q", "options": {"A": "a", "B": "b"}}, "explanation": "e"}
    rec = transform_mcq(raw)
    assert rec["citations"] in ([], None) or isinstance(rec["citations"], list)
