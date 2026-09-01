"""
TDD Tests for MCQ.citations structured JSON column (PRD-MCQ-CITATION-001).

RAG-grounded MCQ citation remediation: every MCQ must be able to persist a
structured citations list (mirroring StudyCard.citations) so each reference
can carry a qdrant_point_id.
"""
from src.db.models import MCQ


def test_mcq_has_structured_citations_column():
    assert hasattr(MCQ, "citations")
    col = MCQ.__table__.columns["citations"]
    assert col.type.__class__.__name__ == "JSON"


def test_mcq_persists_citation_list(db_session):
    cites = [{"source": "eTG", "qdrant_point_id": "550e8400-e29b-41d4-a716-446655440000",
              "confidence": 0.81, "is_australian": True, "title": "Therapeutic Guidelines",
              "author": "eTG", "year": "2024", "page": "p.12"}]
    m = MCQ(question_id="MCQ-T-001", question_text="q", options={"A": "a", "B": "b"},
            correct_answer="A", explanation="e", citation="eTG (2024)", citations=cites,
            specialty="respiratory", difficulty="medium")
    db_session.add(m)
    db_session.commit()
    db_session.refresh(m)
    assert m.citations[0]["qdrant_point_id"] == "550e8400-e29b-41d4-a716-446655440000"
