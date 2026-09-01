"""
MCQ Citation Remediator (PRD-MCQ-CITATION-001)

Grounds a single MCQ's citations against Qdrant via RAGService.search_similar,
mirroring StudyCardGenerator._enrich_with_citations (study_card_generator.py:574-636)
so MCQ references reach parity with study cards: every citation carries a real
qdrant_point_id, meets the 0.65 confidence threshold, has a known author, and
Australian-source coverage is tracked.

Never fabricates a citation. An MCQ with no qualifying hit is returned with
citations=[] and needs_regeneration=True for the caller to flag/report — it is
NOT given a synthetic or sentinel citation.
"""
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Mirrors study_card_generator.py:582 — sources treated as Australian.
AUSTRALIAN_SOURCES = ["eTG", "AMH", "RACGP", "Talley", "AMC", "Australian", "Therapeutic Guidelines"]

# Sentinel point-id used as a fallback citation elsewhere (study_card_generator.py:628);
# never a real grounded citation, so treat it as if no point-id were present.
SENTINEL_POINT_ID = "00000000-0000-0000-0000-000000000000"

UNKNOWN_AUTHOR_VALUES = {"", "unknown", "unknown author"}

CONFIDENCE_THRESHOLD = 0.65
AUSTRALIAN_RATIO_TARGET = 0.60


class MCQCitationRemediator:
    """Grounds MCQ citations in Qdrant, reusing RAGService.search_similar."""

    def __init__(self, rag_service):
        self.rag_service = rag_service

    def _build_query_text(self, mcq: Dict[str, Any]) -> str:
        question = mcq.get("question")
        stem = question.get("stem", "") if isinstance(question, dict) else str(mcq.get("stem") or "")
        explanation = str(mcq.get("explanation") or "")

        parts = [stem]
        if len(explanation.strip()) >= 20:
            parts.append(explanation)
        else:
            options = (
                question.get("options", {})
                if isinstance(question, dict)
                else mcq.get("options", {})
            )
            correct_answer = mcq.get("correct_answer")
            if isinstance(options, dict) and correct_answer in options:
                parts.append(str(options[correct_answer]))

        return "\n".join(p for p in parts if p).strip()

    def _is_australian(self, source: str, title: str) -> bool:
        return any(a in source for a in AUSTRALIAN_SOURCES) or any(a in title for a in AUSTRALIAN_SOURCES)

    def remediate(self, mcq: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ground an MCQ's citations. Returns a copy of `mcq` with:
        - citations: list of grounded citation dicts (never fabricated)
        - needs_regeneration: True when no citation qualified
        - australian_ratio: fraction of surviving citations that are Australian
        - citation: human-readable summary of the primary citation (only if grounded)
        """
        query_text = self._build_query_text(mcq)
        raw_results: Optional[List[Dict[str, Any]]] = self.rag_service.search_similar(
            query_text=query_text,
            limit=5,
            confidence_threshold=CONFIDENCE_THRESHOLD,
        )

        citations: List[Dict[str, Any]] = []
        for result in raw_results or []:
            point_id = result.get("qdrant_point_id")
            if not point_id or str(point_id) == SENTINEL_POINT_ID:
                logger.warning("Skipping citation without a real qdrant_point_id: %s", result.get("source"))
                continue

            score = result.get("score", 0)
            if score < CONFIDENCE_THRESHOLD:
                logger.warning("Skipping low-confidence citation: %s", score)
                continue

            author = str(result.get("author") or "").strip()
            if author.lower() in UNKNOWN_AUTHOR_VALUES:
                logger.warning("Skipping citation with unknown/blank author: %s", result.get("source"))
                continue

            source = result.get("source", "")
            title = result.get("title", "")
            citations.append({
                "source": source,
                "qdrant_point_id": str(point_id),
                "confidence": float(score),
                "is_australian": self._is_australian(source, title),
                "title": title,
                "author": author,
                "year": result.get("year", ""),
                "page": result.get("page", 0),
            })

        needs_regeneration = len(citations) == 0
        australian_ratio = (
            sum(1 for c in citations if c["is_australian"]) / len(citations) if citations else 0.0
        )
        if citations and australian_ratio < AUSTRALIAN_RATIO_TARGET:
            logger.warning("Australian source ratio %.1f%% below 60%% target", australian_ratio * 100)

        out = dict(mcq)
        out["citations"] = citations
        out["needs_regeneration"] = needs_regeneration
        out["australian_ratio"] = australian_ratio
        if citations:
            primary = citations[0]
            out["citation"] = f"{primary['title'] or primary['source']} ({primary['year'] or 'n.d.'})"[:500]

        return out
