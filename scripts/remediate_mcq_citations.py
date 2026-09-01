#!/usr/bin/env python3
"""
Remediate MCQ citations corpus-wide (PRD-MCQ-CITATION-001).

Iterates data/mcqs/*.json (reusing backend/scripts/import_mcqs.py's file-scan
and ignore-list), grounds each MCQ's citations via MCQCitationRemediator
(RAGService.search_similar), writes qdrant_point_id-bearing structured
citations back into the source JSON files, and emits
data/mcqs/_reports/mcq_citation_report.json listing anything that could not
be grounded (needs_regeneration) instead of fabricating a citation.

Usage:
    python scripts/remediate_mcq_citations.py --dry-run     # report only, no writes
    python scripts/remediate_mcq_citations.py --limit 20    # smoke test
    python scripts/remediate_mcq_citations.py                # full corpus, writes files
    python scripts/remediate_mcq_citations.py --force        # re-remediate already-grounded items

Security: no credentials are read or written; RAG/DB endpoints come from env
only (QDRANT_URL). No local LLM is used.
"""
from __future__ import annotations

import sys
import json
import argparse
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = REPO_ROOT / "backend"
DATA_DIR = REPO_ROOT / "data" / "mcqs"
REPORT_DIR = DATA_DIR / "_reports"
REPORT_FILE = REPORT_DIR / "mcq_citation_report.json"

SENTINEL_POINT_ID = "00000000-0000-0000-0000-000000000000"
UNKNOWN_AUTHOR_VALUES = {"", "unknown", "unknown author"}


def _has_valid_point_id(citation: Dict[str, Any]) -> bool:
    pid = citation.get("qdrant_point_id")
    return bool(pid) and str(pid) != SENTINEL_POINT_ID


def _is_unknown_author(citation: Dict[str, Any]) -> bool:
    return str(citation.get("author") or "").strip().lower() in UNKNOWN_AUTHOR_VALUES


def _record_id(mcq_data: Dict[str, Any]) -> str:
    return str(mcq_data.get("id") or mcq_data.get("mcq_id") or mcq_data.get("question_id") or "")


def validate_corpus(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Pure, DB/RAG-free corpus validator (no network calls).

    Each record is expected to carry an id/question_id/mcq_id and a
    `citations` list. Flags records with zero citations, any citation
    missing a real qdrant_point_id, or any citation with an unknown/blank
    author — these are the MCQs that still need RAG-grounded remediation.
    """
    missing_point_id = 0
    unknown_author = 0
    needs_regeneration: List[str] = []

    for record in records:
        record_id = record.get("id") or record.get("question_id") or record.get("mcq_id")
        citations = record.get("citations") or []
        record_needs_regen = not citations

        for citation in citations:
            if not _has_valid_point_id(citation):
                missing_point_id += 1
                record_needs_regen = True
            if _is_unknown_author(citation):
                unknown_author += 1
                record_needs_regen = True

        if record_needs_regen:
            needs_regeneration.append(record_id)

    return {
        "total": len(records),
        "missing_point_id": missing_point_id,
        "unknown_author": unknown_author,
        "needs_regeneration": needs_regeneration,
    }


def run(dry_run: bool, limit: Optional[int], force: bool) -> int:
    sys.path.insert(0, str(BACKEND_DIR))
    from scripts.import_mcqs import _is_ignored_file, _extract_list  # backend/scripts/import_mcqs.py
    from src.ai.rag_service import RAGService
    from src.ai.mcq_citation_remediator import MCQCitationRemediator

    remediator = MCQCitationRemediator(rag_service=RAGService())

    candidates = sorted(p for p in DATA_DIR.glob("*.json") if not _is_ignored_file(p))

    stats = {
        "processed": 0,
        "grounded": 0,
        "needs_regeneration": 0,
        "point_id_present_before": 0,
        "point_id_present_after": 0,
        "unknown_author_before": 0,
        "unknown_author_after": 0,
        "australian_count_after": 0,
    }
    needs_regen_ids: List[str] = []
    processed_count = 0

    print("=" * 64)
    print("MCQ Citation Remediation")
    print(f"Source: {DATA_DIR}")
    print(f"Mode:   {'DRY RUN (no writes)' if dry_run else 'REMEDIATE (writes source files)'}")
    print("=" * 64)

    for path in candidates:
        if limit is not None and processed_count >= limit:
            break
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:  # noqa: BLE001
            print(f"[ERROR] Reading {path.name}: {e}")
            continue

        mcq_list = _extract_list(data)
        if not mcq_list:
            continue

        file_changed = False
        for mcq_data in mcq_list:
            if not isinstance(mcq_data, dict):
                continue
            if limit is not None and processed_count >= limit:
                break

            existing_citations = mcq_data.get("citations") or mcq_data.get("references") or []
            existing_citations = [c for c in existing_citations if isinstance(c, dict)]
            for c in existing_citations:
                if _has_valid_point_id(c):
                    stats["point_id_present_before"] += 1
                if _is_unknown_author(c):
                    stats["unknown_author_before"] += 1

            already_grounded = bool(existing_citations) and all(
                _has_valid_point_id(c) for c in existing_citations
            )

            processed_count += 1
            stats["processed"] += 1

            if already_grounded and not force:
                stats["grounded"] += 1
                for c in existing_citations:
                    stats["point_id_present_after"] += 1
                    if c.get("is_australian"):
                        stats["australian_count_after"] += 1
                continue

            result = remediator.remediate(mcq_data)

            if result["citations"]:
                mcq_data["citations"] = result["citations"]
                if result.get("citation"):
                    mcq_data["citation"] = result["citation"]
                file_changed = True
                stats["grounded"] += 1
                for c in result["citations"]:
                    stats["point_id_present_after"] += 1
                    if c.get("is_australian"):
                        stats["australian_count_after"] += 1
                    if _is_unknown_author(c):
                        stats["unknown_author_after"] += 1
            else:
                stats["needs_regeneration"] += 1
                needs_regen_ids.append(_record_id(mcq_data))

        if file_changed and not dry_run:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"[OK] Updated citations in {path.name}")

    australian_ratio = (
        stats["australian_count_after"] / stats["point_id_present_after"]
        if stats["point_id_present_after"]
        else 0.0
    )

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report = {
        "generated_by": "scripts/remediate_mcq_citations.py",
        "dry_run": dry_run,
        "australian_ratio_after": australian_ratio,
        **stats,
        "needs_regeneration_ids": needs_regen_ids,
    }
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print("-" * 64)
    print(f"Processed:              {stats['processed']}")
    print(f"Grounded (>=1 citation): {stats['grounded']}")
    print(f"Needs regeneration:     {stats['needs_regeneration']}")
    print(f"qdrant_point_id before -> after: {stats['point_id_present_before']} -> {stats['point_id_present_after']}")
    print(f"Unknown author before -> after:  {stats['unknown_author_before']} -> {stats['unknown_author_after']}")
    print(f"Australian ratio after: {australian_ratio:.1%}")
    print(f"Report written -> {REPORT_FILE}")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Remediate MCQ citations with RAG-grounded qdrant_point_id")
    parser.add_argument("--dry-run", action="store_true", help="Report only, never write source files")
    parser.add_argument("--limit", type=int, default=None, help="Only process the first N MCQs (smoke test)")
    parser.add_argument("--force", action="store_true", help="Re-remediate MCQs that already have valid point-ids")
    args = parser.parse_args()
    return run(dry_run=args.dry_run, limit=args.limit, force=args.force)


if __name__ == "__main__":
    sys.exit(main())
