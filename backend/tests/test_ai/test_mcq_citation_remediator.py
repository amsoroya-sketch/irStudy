"""
TDD Tests for MCQCitationRemediator (PRD-MCQ-CITATION-001).

Grounds an MCQ's citations against RAGService.search_similar, mirroring
StudyCardGenerator._enrich_with_citations (backend/src/ai/study_card_generator.py:574-636):
- drop hits without qdrant_point_id
- drop hits below the 0.65 confidence threshold
- drop "Unknown/blank" authors
- flag low Australian-source ratio (<0.60)
- NEVER fabricate a citation — flag needs_regeneration instead

RAGService is always mocked here; this test never touches live Qdrant.
"""
from unittest.mock import MagicMock

from src.ai.mcq_citation_remediator import MCQCitationRemediator


def _hit(pid, score, author="eTG", title="Therapeutic Guidelines", au=True):
    return {"source": title, "qdrant_point_id": pid, "score": score, "content": "…",
            "page": "p.1", "title": title, "author": author, "year": "2024", "is_australian": au}


def _remediator(hits):
    rag = MagicMock()
    rag.search_similar.return_value = hits
    return MCQCitationRemediator(rag_service=rag)


def test_grounds_mcq_with_point_ids():
    r = _remediator([_hit("550e8400-e29b-41d4-a716-446655440000", 0.82)])
    out = r.remediate({"question": {"stem": "q"}, "explanation": "e", "correct_answer": "A"})
    assert out["citations"] and all(c["qdrant_point_id"] for c in out["citations"])
    assert out["citations"][0]["confidence"] >= 0.65


def test_drops_results_without_point_id():
    bad = _hit("", 0.9)
    bad["qdrant_point_id"] = ""
    r = _remediator([bad])
    out = r.remediate({"question": {"stem": "q"}, "explanation": "e", "correct_answer": "A"})
    assert out["citations"] == [] and out["needs_regeneration"] is True


def test_drops_below_confidence_threshold():
    r = _remediator([_hit("550e8400-e29b-41d4-a716-446655440000", 0.40)])
    out = r.remediate({"question": {"stem": "q"}, "explanation": "e", "correct_answer": "A"})
    assert out["citations"] == [] and out["needs_regeneration"] is True


def test_no_unknown_author_in_output():
    r = _remediator([_hit("550e8400-e29b-41d4-a716-446655440000", 0.8, author="Unknown Author")])
    out = r.remediate({"question": {"stem": "q"}, "explanation": "e", "correct_answer": "A"})
    assert all((c.get("author") or "").lower() not in ("unknown author", "unknown", "")
               for c in out["citations"])


def test_flags_low_australian_ratio():
    r = _remediator([_hit("id1", 0.8, title="StatPearls", au=False)])
    out = r.remediate({"question": {"stem": "q"}, "explanation": "e", "correct_answer": "A"})
    assert out["australian_ratio"] < 0.60
