#!/usr/bin/env python3
"""
Validation gate for workshop case assessments (Phase 3 of the 25-august-docs
ingestion). Checks every <case>.assessed.json in staging against the rules in
25-august-docs/ASSESSMENT_INSTRUCTIONS.md.

Checks per case:
  - valid JSON with required keys
  - >=3 citations, each with a qdrant_point_id that exists in the base
    record's rag_context (no fabricated IDs)
  - >=2 enhancements
  - metadata station_type/difficulty from allowed enums
  - no placeholder patterns (PROJECT_CONSTRAINTS §15 style)
  - PDF cases must have non-empty sections; DOCX cases use_fragment=true
  - Australian context: flags 'acetaminophen', '911', 'mg/dL'

USAGE:
    python3 scripts/validate_workshop_assessments.py [--dir <TargetDir>]
Exit code 1 if any case fails.
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STAGING = ROOT / "25-august-docs" / "staging"

STATION_TYPES = {"history_taking", "physical_examination", "counselling",
                 "communication", "diagnosis_management", "emergency_scenario"}
DIFFICULTIES = {"easy", "medium", "hard"}

PLACEHOLDER_PATTERNS = [
    r"\blorem ipsum\b", r"\bTODO\b", r"\[insert", r"\[placeholder",
    r"Clinical scenario for \[", r"^Option [A-D]$", r"XXX+", r"\bTBD\b",
]
NON_AU_PATTERNS = [r"\bacetaminophen\b", r"\b911\b", r"\bmg/dL\b"]


def validate_case(path: Path):
    errors, warnings = [], []
    try:
        a = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        return [f"invalid JSON: {e}"], []

    base_path = path.with_name(path.name.replace(".assessed", ""))
    base = json.loads(base_path.read_text()) if base_path.exists() else {}
    valid_ids = {c["qdrant_point_id"] for c in base.get("rag_context", [])}

    er = a.get("expert_review") or {}
    for key in ("case_id", "title", "expert_review"):
        if not a.get(key):
            errors.append(f"missing {key}")

    cits = er.get("citations") or []
    if len(cits) < 3:
        errors.append(f"only {len(cits)} citations (need >=3)")
    for c in cits:
        pid = c.get("qdrant_point_id", "")
        if not pid:
            errors.append("citation missing qdrant_point_id")
        elif valid_ids and pid not in valid_ids:
            errors.append(f"fabricated qdrant_point_id {pid[:13]}… (not in rag_context)")

    if len(er.get("enhancements") or []) < 2:
        errors.append("fewer than 2 enhancements")

    meta = er.get("metadata") or {}
    if meta.get("station_type") not in STATION_TYPES:
        errors.append(f"bad station_type: {meta.get('station_type')}")
    if meta.get("difficulty") not in DIFFICULTIES:
        errors.append(f"bad difficulty: {meta.get('difficulty')}")
    if not meta.get("tags"):
        errors.append("no tags")

    is_docx = bool(base.get("html_fragment"))
    if is_docx and not a.get("use_fragment"):
        warnings.append("DOCX case without use_fragment=true")
    if not is_docx and not a.get("sections"):
        errors.append("PDF case with empty sections")

    blob = json.dumps(a)
    for pat in PLACEHOLDER_PATTERNS:
        if re.search(pat, blob, re.IGNORECASE if "lorem" in pat else 0):
            errors.append(f"placeholder pattern: {pat}")
    for pat in NON_AU_PATTERNS:
        if re.search(pat, blob):
            warnings.append(f"non-Australian terminology: {pat}")

    return errors, warnings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=None)
    args = ap.parse_args()

    root = STAGING / args.dir if args.dir else STAGING
    files = sorted(root.rglob("*.assessed.json"))
    if not files:
        print("No assessed files found.")
        sys.exit(1)

    failed = 0
    for path in files:
        errors, warnings = validate_case(path)
        if errors:
            failed += 1
            print(f"✗ {path.relative_to(STAGING)}")
            for e in errors:
                print(f"    ERROR: {e}")
        for w in warnings:
            print(f"  ⚠ {path.stem}: {w}")

    print(f"\n{len(files) - failed}/{len(files)} passed, {failed} failed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
