"""
TDD Test for the MCQ citation corpus validator (PRD-MCQ-CITATION-001).

validate_corpus() scans a list of MCQ records (each with a `citations` list)
and reports which items are missing a qdrant_point_id or carry an
"Unknown Author" reference, flagging them for regeneration rather than
silently accepting fabricated/incomplete citations.
"""
from scripts.remediate_mcq_citations import validate_corpus


def test_report_flags_zero_pointid_and_unknown_author():
    sample = [{"id": "M1", "citations": [{"qdrant_point_id": "", "author": "Unknown Author"}]},
              {"id": "M2", "citations": [{"qdrant_point_id": "550e8400-e29b-41d4-a716-446655440000",
                                          "author": "eTG"}]}]
    rep = validate_corpus(sample)
    assert rep["missing_point_id"] == 1 and rep["unknown_author"] == 1
    assert "M1" in rep["needs_regeneration"] and "M2" not in rep["needs_regeneration"]
