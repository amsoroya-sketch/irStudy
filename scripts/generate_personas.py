#!/usr/bin/env python3
"""
PRD-PERSONA-BREADTH-001 — Patient Persona generator (Phase 1 scaffolding).

Generates RAG-grounded, schema-valid patient personas for the AMC OSCE
mock-exam engine, filling the measured specialty gaps (Neurology,
Gastroenterology, Psychiatry, O&G, Endocrinology, Surgery, ...).

PROJECT RULE — Claude-only generation:
    Content is generated ONLY via the project's Claude API path (mirrors
    ``scripts/generate_mcqs_claude.py``). A local / self-hosted LLM MUST NEVER
    be used for irStudy content generation. This module therefore contains no
    local-LLM references (enforced by Test 6).

Grounding rule (mirrors ``src/ai/study_card_generator.py`` /
``RAGService.search_similar``): every clinical persona MUST be anchored to at
least one Qdrant hit carrying a ``qdrant_point_id`` with ``score >= 0.65``.
Personas with no grounded hit are flagged ``needs_review=True`` and are NOT
fabricated a citation and NOT imported.

Phase boundaries:
    * Phase 1 (THIS module's tested surface): ``PersonaGenerator`` +
      ``validate_persona`` + ``REQUIRED_FIELDS`` — fully unit-tested with a
      mocked ``claude_client`` and ``rag_service`` (no live calls).
    * Phase 2 (batch generation) and Phase 3 (import) are SCAFFOLDED under
      ``if __name__ == "__main__":`` only. They require a live Claude API,
      Qdrant, and PostgreSQL and are executed by the operator — never in tests.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# Persona schema
# ---------------------------------------------------------------------------
# The field set persisted for every persona (PRD 0.2). Mirrors the shape of
# archive/.../batch1_personas/*_persona.json, reduced to the fields the
# mock-exam engine and importer require.
REQUIRED_FIELDS: List[str] = [
    "name",
    "age",
    "gender",
    "specialty",
    "difficulty",
    "chief_complaint",
    "opening_statement",
    "symptoms",
    "past_medical_history",
    "medications",
    "allergies",
    "examination_findings",
    "expected_diagnosis",
    "expected_management",
    "critical_errors",
    "learning_objectives",
]

VALID_DIFFICULTIES = {"easy", "medium", "hard"}

# RAG grounding threshold (mirrors RAGService.search_similar default and the
# study_card_generator citation gate).
GROUNDING_SCORE_THRESHOLD = 0.65


def validate_persona(persona: Dict[str, Any]) -> List[str]:
    """Validate a persona dict against the schema.

    Returns a list of human-readable error strings (empty list == valid):
      * one error per missing REQUIRED_FIELDS entry,
      * an error if ``difficulty`` is not one of {easy, medium, hard},
      * an error if there is fewer than 1 ``critical_error``.

    Args:
        persona: The persona dict to validate.

    Returns:
        List of error strings; empty when the persona is valid.
    """
    errors: List[str] = []

    for field in REQUIRED_FIELDS:
        if field not in persona:
            errors.append(f"Missing required field: {field}")

    difficulty = persona.get("difficulty")
    if difficulty is not None and difficulty not in VALID_DIFFICULTIES:
        errors.append(
            f"Invalid difficulty '{difficulty}': must be one of "
            f"{sorted(VALID_DIFFICULTIES)}"
        )

    critical_errors = persona.get("critical_errors")
    if not critical_errors:
        errors.append("At least 1 critical_error is required")

    return errors


class PersonaGenerator:
    """Generate a RAG-grounded patient persona via Claude.

    The Claude client and RAG service are injected so unit tests can mock them
    (no live API calls). In a real run (Phase 2), ``claude_client`` wraps the
    project's Claude API path (see ``scripts/generate_mcqs_claude.py``) and
    ``rag_service`` is an instance of ``src.ai.rag_service.RAGService``.

    Args:
        claude_client: Object exposing ``.generate(...) -> dict`` returning the
            persona JSON. Claude-only — never a local LLM.
        rag_service: Object exposing
            ``.search_similar(query_text, ...) -> list[dict]`` where each hit
            carries ``qdrant_point_id``, ``score``, ``is_australian``, ``source``.
    """

    def __init__(self, claude_client: Any, rag_service: Any) -> None:
        self.claude_client = claude_client
        self.rag_service = rag_service

    def _ground(self, condition: str) -> List[Dict[str, Any]]:
        """Return only grounded RAG hits (truthy qdrant_point_id AND score>=0.65).

        Mirrors the study_card_generator citation gate. No hits => ungrounded.
        """
        query = f"{condition} Australian management"
        hits = self.rag_service.search_similar(query) or []
        grounded = [
            hit
            for hit in hits
            if hit.get("qdrant_point_id")
            and hit.get("score", 0) >= GROUNDING_SCORE_THRESHOLD
        ]
        return grounded

    @staticmethod
    def _build_citations(grounded_hits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Build citation records from grounded hits (each keeps its point id)."""
        return [
            {
                "qdrant_point_id": hit["qdrant_point_id"],
                "score": hit.get("score"),
                "is_australian": hit.get("is_australian", False),
                "source": hit.get("source"),
            }
            for hit in grounded_hits
        ]

    def generate(
        self, specialty: str, condition: str, difficulty: str
    ) -> Dict[str, Any]:
        """Generate one persona for (specialty, condition, difficulty).

        Flow:
          1. Ground the condition via RAG (drop hits without qdrant_point_id
             or with score < 0.65).
          2. If nothing grounded: return the persona with ``needs_review=True``
             and ``citations=[]`` — do NOT fabricate citations, do NOT import.
          3. Otherwise call Claude to produce the persona JSON, attach citations
             built from the grounded hits, honour the requested specialty /
             difficulty, and set ``needs_review=False``.

        Returns:
            The persona dict, always including ``specialty``, ``difficulty``,
            ``citations`` and ``needs_review``.
        """
        grounded_hits = self._ground(condition)

        if not grounded_hits:
            # Ungrounded -> flag for human review; never fabricate a citation.
            persona = self.claude_client.generate(
                specialty=specialty, condition=condition, difficulty=difficulty
            )
            persona = dict(persona) if persona else {}
            persona["specialty"] = specialty
            persona["difficulty"] = difficulty
            persona["citations"] = []
            persona["needs_review"] = True
            return persona

        # Grounded -> generate with Claude and attach real citations.
        persona = self.claude_client.generate(
            specialty=specialty,
            condition=condition,
            difficulty=difficulty,
            grounded_facts=grounded_hits,
        )
        persona = dict(persona)
        persona["specialty"] = specialty
        persona["difficulty"] = difficulty
        persona["citations"] = self._build_citations(grounded_hits)
        persona["needs_review"] = False
        return persona


# ===========================================================================
# Phase 2 / Phase 3 SCAFFOLD — operator-run only (NOT executed by tests).
#
# The functions below require a LIVE Claude API, a running Qdrant instance
# (medical_knowledge collection), and PostgreSQL. They are intentionally
# guarded under ``if __name__ == "__main__":`` and are NOT imported or invoked
# by the unit test suite. Run them manually as the operator once Phase 1 is
# green:
#
#   Phase 2:  python scripts/generate_personas.py --generate --limit 3
#   Phase 3:  python backend/scripts/import_patient_personas.py --source <dir>
# ===========================================================================


def _build_real_claude_client():  # pragma: no cover - live path, not unit-tested
    """Construct the real Claude-backed client for a Phase-2 batch run.

    Claude-only. Mirrors scripts/generate_mcqs_claude.py (Anthropic client).
    The API key is read from the environment / Vault at runtime — never
    hardcoded. Returns an object exposing ``.generate(**kwargs) -> dict``.
    """
    raise NotImplementedError(
        "Phase 2 real Claude client wiring is operator-run only. Wire the "
        "Anthropic client here (see scripts/generate_mcqs_claude.py) and a "
        "prompt/parse loop that returns a schema-valid persona dict."
    )


def _build_real_rag_service():  # pragma: no cover - live path, not unit-tested
    """Construct the real RAGService for a Phase-2 batch run (needs Qdrant)."""
    from src.ai.rag_service import RAGService  # local import: heavy deps

    return RAGService()


def run_batch(  # pragma: no cover - live path, not unit-tested
    targets: List[Dict[str, str]],
    output_dir: str,
    limit: Optional[int] = None,
) -> None:
    """PHASE 2 (operator-run): generate + validate + write *_persona.json.

    Requires live Claude API + Qdrant. Writes ungrounded personas to a
    _reports/personas_needs_review.json sink instead of importing them.
    """
    raise NotImplementedError(
        "Phase 2 batch generation requires live Claude API + Qdrant and is "
        "executed by the operator, not by tests."
    )


if __name__ == "__main__":  # pragma: no cover - operator entrypoint
    import argparse

    parser = argparse.ArgumentParser(
        description=(
            "PRD-PERSONA-BREADTH-001 persona generator. "
            "Phase 2/3 (real generation + import) require live Claude API + "
            "Qdrant + PostgreSQL and are run by the operator, NOT in tests."
        )
    )
    parser.add_argument(
        "--generate",
        action="store_true",
        help="Phase 2: run a real Claude+RAG batch (operator-only).",
    )
    parser.add_argument(
        "--limit", type=int, default=None, help="Cap personas per specialty."
    )
    parser.add_argument(
        "--output-dir",
        default="archive/prds/clinical-content-prds/validation-system/batch1_personas",
        help="Where to write *_persona.json files.",
    )
    args = parser.parse_args()

    if not args.generate:
        parser.error(
            "Nothing to do. Phase 1 (generator + validate_persona) is unit "
            "tested via pytest. Use --generate for the operator-only Phase 2 "
            "run (needs live Claude API + Qdrant)."
        )

    # NOTE: intentionally raises — Phase 2 wiring is operator responsibility.
    print(
        json.dumps(
            {
                "status": "phase2_operator_only",
                "message": (
                    "Real generation requires live Claude API + Qdrant. "
                    "Wire _build_real_claude_client / _build_real_rag_service "
                    "and run_batch, then import via "
                    "backend/scripts/import_patient_personas.py --source <dir>."
                ),
            },
            indent=2,
        )
    )
