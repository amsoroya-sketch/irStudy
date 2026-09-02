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
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

# Make `src.*` (backend package) importable when this script is run directly
# (e.g. `python scripts/generate_personas.py --generate`), mirroring
# backend/scripts/import_patient_personas.py's own sys.path bootstrap.
_backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

# Load backend/.env (ANTHROPIC_API_KEY, DATABASE_PASSWORD, QDRANT_URL) for
# standalone runs, mirroring backend/src/main.py's own load_dotenv() call.
# No-op (and no secrets touched) when the vars are already exported.
try:
    from dotenv import load_dotenv

    load_dotenv(_backend_dir / ".env")
except ImportError:  # pragma: no cover - dotenv is a backend dependency
    pass

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
# Phase 2 / Phase 3 — operator-run only (NOT executed by tests).
#
# The functions below require a LIVE Claude API and a running Qdrant instance
# (medical_knowledge collection). They are guarded under
# ``if __name__ == "__main__":`` and are NOT imported or invoked by the unit
# test suite:
#
#   Phase 2:  python scripts/generate_personas.py --generate --limit 8
#   Phase 3:  python backend/scripts/import_patient_personas.py --source <dir>
# ===========================================================================

# Fallback condition lists for specialties not yet in the conditions spine
# (data/amc_blueprints/conditions.json has 0 rows for these two — PRD 0.1/0.5
# permits running standalone against a known fallback list).
_FALLBACK_CONDITIONS: Dict[str, List[str]] = {
    "obstetrics_gynaecology": [
        "Antepartum Haemorrhage",
        "Pre-eclampsia",
        "Postpartum Haemorrhage",
        "Ectopic Pregnancy",
        "Pelvic Inflammatory Disease",
        "Menorrhagia",
        "Early Pregnancy Loss (Miscarriage)",
        "Gestational Diabetes",
    ],
    "surgery": [
        "Acute Appendicitis",
        "Inguinal Hernia",
        "Acute Cholecystitis",
        "Bowel Obstruction (Surgical)",
        "Breast Lump Assessment",
        "Post-operative Wound Infection",
        "Diverticulitis",
        "Testicular Torsion",
    ],
}

# The 6 specialties this PRD targets (0.1). Maps to the persona `specialty`
# value used by import_patient_personas.map_specialty().
TARGET_SPECIALTIES: List[str] = [
    "neurology",
    "gastroenterology",
    "psychiatry",
    "obstetrics_gynaecology",
    "endocrinology",
    "surgery",
]

_DIFFICULTY_CYCLE = ["easy", "medium", "hard"]


def _conditions_from_spine(specialty: str) -> List[str]:
    """Read condition names for a specialty from the conditions spine JSON.

    Falls back to [] if the spine file or the specialty isn't present yet
    (PRD-CONDITIONS-SPINE-001 may not have run for every specialty).
    """
    spine_path = (
        Path(__file__).resolve().parent.parent
        / "data"
        / "amc_blueprints"
        / "conditions.json"
    )
    if not spine_path.exists():
        return []
    try:
        data = json.loads(spine_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    return [
        c["name"]
        for c in data.get("conditions", [])
        if c.get("specialty") == specialty
    ]


def build_targets(per_specialty: int = 8) -> List[Dict[str, str]]:
    """Build (specialty, condition, difficulty) targets for every missing
    specialty, spreading difficulty across the easy/medium/hard cycle.

    Uses the conditions spine when available, else the fallback list (0.1).
    Conditions are cycled (not deduplicated away) when a specialty has fewer
    distinct conditions than ``per_specialty``, so every specialty still gets
    the requested count with a difficulty spread.
    """
    targets: List[Dict[str, str]] = []
    for specialty in TARGET_SPECIALTIES:
        conditions = _conditions_from_spine(specialty) or _FALLBACK_CONDITIONS.get(
            specialty, []
        )
        if not conditions:
            continue
        for i in range(per_specialty):
            condition = conditions[i % len(conditions)]
            difficulty = _DIFFICULTY_CYCLE[i % len(_DIFFICULTY_CYCLE)]
            targets.append(
                {
                    "specialty": specialty,
                    "condition": condition,
                    "difficulty": difficulty,
                }
            )
    return targets


def _get_claude_api_key() -> Optional[str]:  # pragma: no cover - live path
    """Retrieve the Claude API key (Vault primary, env fallback).

    Mirrors src/ai/ai_patient.py._get_api_key — never a hardcoded key.
    """
    from src.core.vault import get_vault_secret

    try:
        return get_vault_secret("secret/ai-osce/claude-api-key", "value")
    except Exception:
        try:
            return get_vault_secret("irStudy/claude", "api_key")
        except Exception:
            import os

            return os.environ.get("ANTHROPIC_API_KEY")


class _ClaudePersonaClient:  # pragma: no cover - live path, not unit-tested
    """Claude-only persona generator. Mirrors scripts/generate_mcqs_claude.py.

    Uses the current bare Sonnet model id and omits temperature/top_p/top_k —
    current models (Sonnet 5 / Opus 4.8) reject those params with a 400 (see
    backend/src/services/emr/validators/claude_validator.py).
    """

    MODEL = "claude-sonnet-5"

    def __init__(self, api_key: str) -> None:
        from anthropic import Anthropic

        self.client = Anthropic(api_key=api_key)

    @staticmethod
    def _prompt(
        specialty: str,
        condition: str,
        difficulty: str,
        grounded_facts: Optional[List[Dict[str, Any]]],
    ) -> str:
        facts_text = ""
        if grounded_facts:
            facts_text = "\n\n".join(
                f"Source: {hit.get('source', 'Unknown')}\n{hit.get('content', '')[:500]}"
                for hit in grounded_facts[:5]
            )

        fields = ", ".join(REQUIRED_FIELDS)
        return f"""You are a medical educator creating an AMC OSCE patient persona for the
Australian Medical Council Clinical Examination.

**Specialty:** {specialty}
**Condition:** {condition}
**Difficulty:** {difficulty} (must be exactly "{difficulty}")

**Grounding facts (Australian clinical guidelines — use these for accuracy):**
{facts_text or "(none available — use standard Australian clinical practice)"}

**Task:** Create ONE realistic, clinically accurate patient persona for an OSCE
station simulating {condition}.

**Requirements:**
- Australian context: use "paracetamol" (not acetaminophen), "GP" (not PCP),
  "000" (not 911), mmol/L for glucose, reference eTG/RACGP/AMC guidelines.
- `critical_errors`: at least one plausible clinical error a candidate could make.
- `learning_objectives`: at least one specific, assessable objective.

**Output ONLY valid, strictly well-formed JSON with exactly these top-level
fields (no markdown fences, no trailing commas, all strings on a single
logical value properly quoted/escaped):** {fields}

Field shapes:
- name (str), age (int), gender (str)
- chief_complaint (str), opening_statement (str, first-person patient speech)
- symptoms (object), past_medical_history (array of str)
- medications (array of str), allergies (array of str)
- examination_findings (object)
- expected_diagnosis (str), expected_management (str)
- critical_errors (array of str), learning_objectives (array of str)

Generate the persona now (JSON only, no markdown fences):"""

    def generate(
        self,
        specialty: str,
        condition: str,
        difficulty: str,
        grounded_facts: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        prompt = self._prompt(specialty, condition, difficulty, grounded_facts)
        response = self.client.messages.create(
            model=self.MODEL,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        # Current models may prepend non-text blocks (e.g. ThinkingBlock) to
        # `content`; find the first block that actually carries text.
        text = next(
            (block.text for block in response.content if hasattr(block, "text")), ""
        )
        start, end = text.find("{"), text.rfind("}") + 1
        if start == -1 or end <= start:
            raise ValueError(f"No JSON object found in Claude response: {text[:200]}")
        return json.loads(text[start:end])


class _AustralianTaggingRAGAdapter:  # pragma: no cover - live path
    """Wrap RAGService.search_similar to tag each hit with `is_australian`.

    RAGService.search_similar() does not itself compute is_australian; reuse
    the single canonical classifier (src.ai.mcq_citation_remediator) so this
    matches study_card_generator / MCQ citation grounding exactly.
    """

    def __init__(self, rag_service: Any) -> None:
        self._rag = rag_service

    def search_similar(self, query_text: str, **kwargs: Any) -> List[Dict[str, Any]]:
        from src.ai.mcq_citation_remediator import is_australian_source

        hits = self._rag.search_similar(query_text, **kwargs) or []
        for hit in hits:
            hit["is_australian"] = is_australian_source(
                hit.get("source", ""), hit.get("title", "")
            )
        return hits


def _build_real_claude_client() -> _ClaudePersonaClient:  # pragma: no cover
    """Construct the real Claude-backed client for a Phase-2 batch run."""
    api_key = _get_claude_api_key()
    if not api_key:
        raise ValueError("Claude API key not found (Vault or ANTHROPIC_API_KEY)")
    return _ClaudePersonaClient(api_key)


def _build_real_rag_service() -> _AustralianTaggingRAGAdapter:  # pragma: no cover
    """Construct the real RAGService for a Phase-2 batch run (needs Qdrant)."""
    from src.ai.rag_service import RAGService  # local import: heavy deps

    return _AustralianTaggingRAGAdapter(RAGService())


def _slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def _to_import_schema(persona: Dict[str, Any], persona_code: str) -> Dict[str, Any]:
    """Map the PRD schema (REQUIRED_FIELDS) onto the fields
    backend/scripts/import_patient_personas.py reads, without dropping the
    original fields (extra keys are ignored by the importer, not rejected).
    """
    out = dict(persona)
    out["id"] = persona_code
    out["persona_code"] = persona_code
    out.setdefault("occupation", None)
    out.setdefault("cultural_background", None)
    out.setdefault("preferred_language", "English")
    out["medical_history"] = {
        "past_medical_history": persona.get("past_medical_history", []),
        "medications": persona.get("medications", []),
        "allergies": persona.get("allergies", []),
        "examination_findings": persona.get("examination_findings", {}),
    }
    out["emotional_profile"] = {
        "baseline": "Calm, cooperative, appropriately concerned",
        "triggers": [],
        "responses": {},
    }
    # NOTE: rag_query_hints/key_differentials/critical_actions/amc_competencies
    # are declared JSON in src.db.models.PatientPersona but the live table has
    # them as native Postgres ARRAY columns (a pre-existing model/schema
    # mismatch — the 207 pre-existing personas never populated these fields,
    # so it never surfaced). Leave them empty here rather than risk a
    # DatatypeMismatch on import; the real grounding record (qdrant_point_id
    # citations) is preserved in this file's own `citations` field regardless.
    out["rag_query_hints"] = []
    out["key_differentials"] = []
    out["critical_actions"] = []
    out["amc_blueprint_area"] = persona.get("specialty", "").replace("_", " ").title()
    out["amc_competencies"] = []
    return out


def run_batch(  # pragma: no cover - live path, not unit-tested
    generator: "PersonaGenerator",
    targets: List[Dict[str, str]],
    output_dir: str,
    reports_dir: str,
    limit: Optional[int] = None,
) -> Dict[str, Any]:
    """PHASE 2 (operator-run): generate + validate + write *_persona.json.

    Ungrounded personas are written to
    ``<reports_dir>/personas_needs_review.json`` and are NEVER imported.
    Invalid personas (validate_persona() errors) are written to
    ``<reports_dir>/personas_validation_errors.json`` and are also NOT written
    as importable *_persona.json files.
    """
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    reports_path = Path(reports_dir)
    reports_path.mkdir(parents=True, exist_ok=True)

    if limit is not None:
        targets = targets[:limit]

    needs_review: List[Dict[str, Any]] = []
    validation_errors: List[Dict[str, Any]] = []
    generation_errors: List[Dict[str, Any]] = []
    written: List[str] = []
    per_specialty_counts: Dict[str, int] = {}
    australian_ratios: List[float] = []

    # Stable per-specialty index (1-based position among that specialty's
    # targets), NOT a running count of successes — so a retry after a partial
    # failure overwrites the same filename instead of renumbering everything
    # after it and leaving orphaned stale files behind.
    specialty_seen: Dict[str, int] = {}
    indexed_targets: List[tuple] = []
    for target in targets:
        specialty_seen[target["specialty"]] = specialty_seen.get(target["specialty"], 0) + 1
        indexed_targets.append((specialty_seen[target["specialty"]], target))

    for n, target in indexed_targets:
        specialty = target["specialty"]
        condition = target["condition"]
        difficulty = target["difficulty"]

        # The live Claude call occasionally returns malformed JSON (truncation,
        # a stray brace in prose). Retry once, then skip-and-log rather than
        # aborting the whole batch over one bad response.
        persona = None
        last_error: Optional[Exception] = None
        for _attempt in range(3):
            try:
                persona = generator.generate(
                    specialty=specialty, condition=condition, difficulty=difficulty
                )
                break
            except Exception as exc:  # noqa: BLE001 - log and retry/skip, don't crash the batch
                last_error = exc
        if persona is None:
            generation_errors.append(
                {"specialty": specialty, "condition": condition,
                 "difficulty": difficulty, "error": str(last_error)}
            )
            continue

        if persona.get("needs_review"):
            needs_review.append(
                {"specialty": specialty, "condition": condition,
                 "difficulty": difficulty, "reason": "no_grounded_citation"}
            )
            continue

        errors = validate_persona(persona)
        if errors:
            validation_errors.append(
                {"specialty": specialty, "condition": condition,
                 "difficulty": difficulty, "errors": errors}
            )
            continue

        citations = persona.get("citations", [])
        if citations:
            ratio = sum(1 for c in citations if c.get("is_australian")) / len(citations)
            australian_ratios.append(ratio)

        per_specialty_counts[specialty] = per_specialty_counts.get(specialty, 0) + 1
        persona_code = f"{specialty[:4].upper()}-{n:03d}-{_slugify(condition)[:20].upper()}"
        importable = _to_import_schema(persona, persona_code)

        filename = f"{specialty}_{n:03d}_{_slugify(condition)}_persona.json"
        (out_path / filename).write_text(
            json.dumps(importable, indent=2), encoding="utf-8"
        )
        written.append(filename)

    (reports_path / "personas_needs_review.json").write_text(
        json.dumps(needs_review, indent=2), encoding="utf-8"
    )
    if validation_errors:
        (reports_path / "personas_validation_errors.json").write_text(
            json.dumps(validation_errors, indent=2), encoding="utf-8"
        )
    if generation_errors:
        (reports_path / "personas_generation_errors.json").write_text(
            json.dumps(generation_errors, indent=2), encoding="utf-8"
        )

    summary = {
        "generated": len(written),
        "needs_review": len(needs_review),
        "validation_errors": len(validation_errors),
        "generation_errors": len(generation_errors),
        "per_specialty_counts": per_specialty_counts,
        "avg_australian_ratio": (
            sum(australian_ratios) / len(australian_ratios) if australian_ratios else 0.0
        ),
        "output_dir": str(out_path),
    }
    return summary


if __name__ == "__main__":  # pragma: no cover - operator entrypoint
    import argparse

    parser = argparse.ArgumentParser(
        description=(
            "PRD-PERSONA-BREADTH-001 persona generator. "
            "Phase 2 (real generation) requires a live Claude API + Qdrant "
            "and is run by the operator, not by tests."
        )
    )
    parser.add_argument(
        "--generate",
        action="store_true",
        help="Phase 2: run a real Claude+RAG batch (operator-only).",
    )
    parser.add_argument(
        "--limit", type=int, default=None, help="Cap total targets processed."
    )
    parser.add_argument(
        "--per-specialty", type=int, default=8, help="Personas per specialty."
    )
    parser.add_argument(
        "--specialty",
        default=None,
        choices=TARGET_SPECIALTIES,
        help="Only generate for this one specialty (for resumable, chunked runs).",
    )
    parser.add_argument(
        "--output-dir",
        default="archive/prds/clinical-content-prds/validation-system/batch1_personas",
        help="Where to write *_persona.json files.",
    )
    parser.add_argument(
        "--reports-dir",
        default="data/amc_blueprints/_reports",
        help="Where to write personas_needs_review.json / validation errors.",
    )
    args = parser.parse_args()

    if not args.generate:
        parser.error(
            "Nothing to do. Phase 1 (generator + validate_persona) is unit "
            "tested via pytest. Use --generate for the operator-only Phase 2 "
            "run (needs live Claude API + Qdrant)."
        )

    targets = build_targets(per_specialty=args.per_specialty)
    if args.specialty:
        targets = [t for t in targets if t["specialty"] == args.specialty]
    generator = PersonaGenerator(
        claude_client=_build_real_claude_client(),
        rag_service=_build_real_rag_service(),
    )
    summary = run_batch(
        generator=generator,
        targets=targets,
        output_dir=args.output_dir,
        reports_dir=args.reports_dir,
        limit=args.limit,
    )
    print(json.dumps(summary, indent=2))
