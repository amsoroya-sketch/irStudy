#!/usr/bin/env python3
"""
Import MCQs from JSON files into the database (resilient, correct, idempotent).

PRD: PRD-MVP-003-CONTENT-POPULATION-MVP.md
Purpose: Import authored MCQs from data/mcqs/ directory.

DEFECT FIX (respiratory silent-loss incident):
    - Per-row durability via SAVEPOINTs (db.begin_nested + db.flush). One bad row
      NEVER wipes previously-persisted rows. Single final db.commit().
    - correct_answer read from TOP-LEVEL first (data had it top-level; the old code
      read it from inside the `question` dict and silently defaulted every dict-form
      answer to 'A' -> data corruption).
    - Validation guard SKIPS (does not insert) garbage rows: empty question_text,
      options that are not a dict with >=2 entries, or a correct_answer letter that
      is not a key in options. Skipped items are written to
      data/mcqs/_reports/respiratory_unimportable.json for later regeneration.
    - citation coerced to str and truncated to 500 chars (model column is String(500)).
    - explanation coerced to a non-empty str (NOT NULL column).

DESIGN NOTE:
    DB imports (SQLAlchemy + src.db.*) are DEFERRED into the DB code path so that
    `--dry-run` works with NO database connection at all. src.db.base calls
    get_database_url() at module import time, which raises when DATABASE_PASSWORD is
    unset; importing it eagerly would break offline dry-runs.

Usage:
    python scripts/import_mcqs.py --source /home/dev/Development/irStudy/data/mcqs/
    python scripts/import_mcqs.py --source ../data/mcqs/ --dry-run   # no DB needed
"""

import sys
import json
import argparse
from pathlib import Path
from uuid import uuid4

# Add backend directory to path (so `src...` imports resolve when we defer them)
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# NOTE: Do NOT import sqlalchemy or src.db.* at module level — see DESIGN NOTE above.

# ---------------------------------------------------------------------------
# Static config (plain strings, NOT credentials). Mirrors the SQLAlchemy enums
# in src/db/models.py so the transform/validation stage needs no DB import.
# ---------------------------------------------------------------------------
VALID_SPECIALTIES = {
    "cardiology",
    "respiratory",
    "gastroenterology",
    "neurology",
    "psychiatry",
    "endocrinology",
    "emergency_medicine",
    "general_practice",
    "paediatrics",
    "obstetrics_gynaecology",
    "surgery",
    "ophthalmology",
    "urology",
    "musculoskeletal",
}

SPECIALTY_MAP = {
    "cardiology": "cardiology",
    "respiratory": "respiratory",
    "psychiatry": "psychiatry",
    "general_practice": "general_practice",
    "emergency": "emergency_medicine",
    "emergency_medicine": "emergency_medicine",
    "pediatrics": "paediatrics",  # US -> Australian spelling
    "paediatrics": "paediatrics",
    "gastroenterology": "gastroenterology",
    "neurology": "neurology",
    "endocrinology": "endocrinology",
    "obstetrics": "obstetrics_gynaecology",
    "gynaecology": "obstetrics_gynaecology",
    "obstetrics_gynaecology": "obstetrics_gynaecology",
    "surgery": "surgery",
    "ophthalmology": "ophthalmology",
    "urology": "urology",
    "musculoskeletal": "musculoskeletal",
}

DIFFICULTY_MAP = {
    "easy": "easy",
    "basic": "easy",
    "medium": "medium",
    "moderate": "medium",
    "intermediate": "medium",
    "hard": "hard",
    "advanced": "hard",
}

# Instead of a hardcoded allow-list (which silently missed ~10 real content files
# and ~170 authored MCQs), we SCAN data/mcqs/*.json and EXCLUDE known non-content
# files. Per-row SAVEPOINT + validation guard skip anything invalid, and question_id
# dedup handles cross-file overlaps.
#
# IGNORE rules (case-insensitive):
#   - anything under a `backups/` subdirectory
#   - filenames containing `_backup_` or `_with_images`
#   - generator / scratch / test files: temp_*, test_*, *_GENERATED_ollama*
#   - non-MCQ helper file: mcq_image_matches.json
IGNORE_SUBSTRINGS = ("_backup_", "_with_images", "_generated_ollama")
IGNORE_PREFIXES = ("temp_", "test_")
IGNORE_EXACT = {
    "mcq_image_matches.json",
    # id-keyed fragment files whose items lack inner id/specialty and are already
    # fully contained (WEEK3-CARDIO-076..106) in week3_cardiology_200_mcqs.json.
    # Parsing them would risk duplicate, mislabelled (general_practice) rows.
    "week3_bradyarrhythmia_101-106.json",
    "week3_bradyarrhythmia_mcqs_101-106.json",
    "week3_cardio_af_076_081.json",
    "week3_cardiology_af_076_086.json",
}


def _is_ignored_file(path: Path) -> bool:
    """Return True if a data/mcqs JSON file is NOT authored MCQ content."""
    if "backups" in (p.lower() for p in path.parts):
        return True
    name = path.name.lower()
    if name in IGNORE_EXACT:
        return True
    if any(name.startswith(pre) for pre in IGNORE_PREFIXES):
        return True
    if any(sub in name for sub in IGNORE_SUBSTRINGS):
        return True
    return False

REPORT_DIR = backend_dir.parent / "data" / "mcqs" / "_reports"
UNIMPORTABLE_REPORT = REPORT_DIR / "respiratory_unimportable.json"

EXPLANATION_PLACEHOLDER = "No explanation provided."


# ---------------------------------------------------------------------------
# Mapping helpers
# ---------------------------------------------------------------------------
def map_specialty(specialty_str: str) -> str:
    """Map a raw specialty string to a canonical MedicalSpecialty *value* string."""
    key = (specialty_str or "").lower().strip()
    return SPECIALTY_MAP.get(key, "general_practice")


def map_difficulty(difficulty_str: str) -> str:
    """Map a raw difficulty string to a canonical DifficultyLevel *value* string."""
    key = (difficulty_str or "").lower().strip()
    return DIFFICULTY_MAP.get(key, "medium")


def _normalise_correct_answer(raw) -> str:
    """Uppercase and keep only the first A-E letter. Returns '' if none found."""
    if not raw:
        return ""
    text = str(raw).upper()
    for ch in text:
        if ch in "ABCDE":
            return ch
    return ""


def _coerce_citation(mcq_data: dict) -> str:
    """Build a citation string and truncate to the model's String(500) limit."""
    # Preferred: structured references [{title, year, page}, ...]
    references = mcq_data.get("references")
    if isinstance(references, list) and references:
        ref = references[0]
        if isinstance(ref, dict):
            citation = (
                f"{ref.get('title', 'Australian medical guidelines')} "
                f"({ref.get('year', 'N/A')}), p. {ref.get('page', 'N/A')}"
            )
        else:
            citation = str(ref)
    else:
        # Respiratory files use `citations`: a list of plain strings.
        citations = mcq_data.get("citations")
        if isinstance(citations, list) and citations:
            citation = "; ".join(str(c) for c in citations)
        elif isinstance(citations, str) and citations.strip():
            citation = citations
        else:
            citation = str(mcq_data.get("citation") or "Australian medical guidelines")

    citation = str(citation).strip() or "Australian medical guidelines"
    return citation[:500]


def _coerce_structured_citations(mcq_data: dict) -> list:
    """
    Preserve the structured references[]/citations[] array (with any
    qdrant_point_id already present) instead of collapsing it into a flat
    string. Returns [] when no structured (dict-shaped) entries exist —
    a bare list of plain strings carries no point-id and is not preserved
    here (the flat `citation` summary already covers that case).
    """
    references = mcq_data.get("references")
    if isinstance(references, list) and references:
        return [ref for ref in references if isinstance(ref, dict)]

    citations = mcq_data.get("citations")
    if isinstance(citations, list) and citations:
        return [c for c in citations if isinstance(c, dict)]

    return []


def _coerce_explanation(mcq_data: dict) -> str:
    """Coerce explanation to a non-empty string (NOT NULL column)."""
    explanation_obj = mcq_data.get("explanation", {})
    if isinstance(explanation_obj, dict):
        why_correct = explanation_obj.get("why_correct", "")
        key_points = explanation_obj.get("key_points", []) or []
        if key_points:
            kp = "\n\nKey Points:\n" + "\n".join(f"- {p}" for p in key_points)
        else:
            kp = ""
        explanation = f"{why_correct}{kp}".strip()
    else:
        explanation = str(explanation_obj or "").strip()

    if not explanation:
        explanation = str(mcq_data.get("rationale") or "").strip()
    if not explanation:
        explanation = str(mcq_data.get("summary") or "").strip()
    if not explanation:
        explanation = EXPLANATION_PLACEHOLDER
    return explanation


def transform_mcq(mcq_data: dict) -> dict:
    """
    Transform a raw MCQ dict into a normalised record of plain (DB-agnostic) fields.

    Returns a dict with: question_id, question_text, options (dict), correct_answer,
    explanation, citation, learning_points, specialty (str), difficulty (str), tags,
    image_url.
    """
    question_id = (
        mcq_data.get("id")
        or mcq_data.get("mcq_id")
        or mcq_data.get("question_id")
        or f"IMPORTED-{uuid4().hex[:12].upper()}"
    )

    # --- question text / options / nested-answer fallback ---
    question_obj = mcq_data.get("question", {})
    nested_answer = ""
    if isinstance(question_obj, dict):
        scenario = question_obj.get("scenario", "")
        stem = question_obj.get("stem", "")
        question_text = f"{scenario}\n\n{stem}".strip() if scenario else (stem or "")
        options = question_obj.get("options", {})
        nested_answer = question_obj.get("correct_answer", "")
    else:
        # Bare-string question form: no options are available in-data.
        question_text = str(question_obj or "").strip() or (
            mcq_data.get("question_text") or mcq_data.get("stem", "") or ""
        )
        options = mcq_data.get("options", {})

    # Ensure options is a dict (convert list -> {'A': ..., 'B': ...}).
    if isinstance(options, list):
        options = {chr(65 + i): opt for i, opt in enumerate(options)}
    elif not isinstance(options, dict):
        options = {}

    # Normalise single-letter option keys to uppercase so a lowercase-key/
    # uppercase-answer mismatch (e.g. keys 'a'..'e' with correct_answer 'B')
    # does not silently discard an otherwise-valid item. This aligns key case
    # only — it never invents option text.
    if options and all(isinstance(k, str) and len(k) == 1 for k in options):
        options = {k.upper(): v for k, v in options.items()}

    # --- correct_answer: TOP-LEVEL first, then nested, then 'A' ---
    raw_answer = mcq_data.get("correct_answer")
    if raw_answer in (None, ""):
        raw_answer = nested_answer
    if raw_answer in (None, ""):
        raw_answer = mcq_data.get("answer")
    correct_answer = _normalise_correct_answer(raw_answer) or "A"

    # --- specialty / difficulty (difficulty may live under metadata) ---
    specialty = map_specialty(mcq_data.get("specialty", "general_practice"))
    metadata = mcq_data.get("metadata") or {}
    raw_difficulty = mcq_data.get("difficulty") or metadata.get("difficulty")
    difficulty = map_difficulty(raw_difficulty)

    # --- tags ---
    tags = list(mcq_data.get("tags", []) or [])
    if not tags:
        if metadata.get("australian_context"):
            tags.append("australian_context")
        topic = mcq_data.get("topic") or metadata.get("topic")
        if topic:
            tags.append(str(topic).lower())

    # --- learning points ---
    explanation_obj = mcq_data.get("explanation", {})
    learning_points = (
        list(explanation_obj.get("key_points", []) or [])
        if isinstance(explanation_obj, dict)
        else []
    )

    return {
        "question_id": str(question_id),
        "question_text": str(question_text or "").strip(),
        "options": options,
        "correct_answer": correct_answer,
        "explanation": _coerce_explanation(mcq_data),
        "citation": _coerce_citation(mcq_data),
        "citations": _coerce_structured_citations(mcq_data),
        "learning_points": learning_points,
        "specialty": specialty,
        "difficulty": difficulty,
        "tags": tags,
        "image_url": mcq_data.get("image_url"),
    }


def validate_record(record: dict) -> str | None:
    """
    Validate a transformed record. Returns a reason string if INVALID, else None.

    We NEVER fabricate options; malformed items are skipped and reported.
    """
    if not record["question_text"]:
        return "empty_question_text"

    options = record["options"]
    if not isinstance(options, dict) or len(options) < 2:
        return "missing_or_insufficient_options"

    # correct_answer must reference an actual option key.
    if record["correct_answer"] not in options:
        return f"correct_answer_'{record['correct_answer']}'_not_in_options"

    return None


# ---------------------------------------------------------------------------
# File loading
# ---------------------------------------------------------------------------
def _extract_list(data):
    if isinstance(data, dict):
        for key in ("mcqs", "questions"):
            if isinstance(data.get(key), list):
                return data[key]
        for value in data.values():
            if isinstance(value, list) and value:
                return value
        return []
    if isinstance(data, list):
        return data
    return []


def load_mcq_files(source_dir: Path) -> list[tuple[str, dict]]:
    """
    Load MCQs by SCANNING source_dir/*.json (deterministic, sorted), excluding
    non-content files via _is_ignored_file. Returns list of (filename, mcq_dict).
    """
    items: list[tuple[str, dict]] = []
    candidates = sorted(
        p for p in source_dir.glob("*.json") if not _is_ignored_file(p)
    )
    for file_path in candidates:
        filename = file_path.name
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"[ERROR] Invalid JSON in {filename}: {e}")
            continue
        except Exception as e:  # noqa: BLE001
            print(f"[ERROR] Reading {filename}: {e}")
            continue

        mcq_list = _extract_list(data)
        if not mcq_list:
            print(f"[WARN] Unknown/empty JSON structure in {filename}")
            continue
        print(f"[OK] Loaded {len(mcq_list)} MCQs from {filename}")
        for m in mcq_list:
            if isinstance(m, dict):
                items.append((filename, m))
    return items


def _write_unimportable_report(skipped_invalid: list[dict]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_by": "backend/scripts/import_mcqs.py",
        "count": len(skipped_invalid),
        "description": (
            "MCQ items skipped by the importer because they are unimportable "
            "(e.g. bare-string question with no options). Regenerate these into "
            "full {question:{scenario,stem,options}} form and re-run the importer."
        ),
        "items": skipped_invalid,
    }
    with open(UNIMPORTABLE_REPORT, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    print(f"[OK] Wrote {len(skipped_invalid)} unimportable items -> {UNIMPORTABLE_REPORT}")


# ---------------------------------------------------------------------------
# Main import routine
# ---------------------------------------------------------------------------
def import_mcqs(source_dir: str, dry_run: bool = False, validate: bool = False) -> int:
    print("=" * 64)
    print("MCQ Import Script")
    print("=" * 64)
    print(f"Source: {source_dir}")
    print(f"Mode:   {'DRY RUN (no database)' if dry_run else 'IMPORT'}")
    print("")

    source_path = Path(source_dir)
    if not source_path.exists():
        print(f"[ERROR] Source directory not found: {source_dir}")
        return 1

    print("Loading MCQ files...")
    items = load_mcq_files(source_path)
    print(f"\n[OK] Total MCQ items loaded: {len(items)}\n")

    # ---- Transform + validate every item up front (DB-agnostic) ----
    per_specialty: dict[str, dict[str, int]] = {}

    def bump(spec: str, field: str) -> None:
        per_specialty.setdefault(
            spec, {"importable": 0, "skipped_invalid": 0}
        )[field] += 1

    valid_records: list[dict] = []
    skipped_invalid: list[dict] = []

    for source_file, mcq_data in items:
        record = transform_mcq(mcq_data)
        reason = validate_record(record)
        if reason:
            skipped_invalid.append(
                {
                    "id": record["question_id"],
                    "source_file": source_file,
                    "specialty": record["specialty"],
                    "reason": reason,
                }
            )
            bump(record["specialty"], "skipped_invalid")
        else:
            valid_records.append(record)
            bump(record["specialty"], "importable")

    # Always (re)write the unimportable report so it can be regenerated later.
    _write_unimportable_report(skipped_invalid)

    # ---- Per-specialty summary ----
    print("\n" + "-" * 64)
    print("Per-specialty summary (importable / skipped_invalid):")
    print("-" * 64)
    for spec in sorted(per_specialty):
        counts = per_specialty[spec]
        print(
            f"  {spec:<24} importable={counts['importable']:>4} "
            f"skipped_invalid={counts['skipped_invalid']:>4}"
        )
    print("-" * 64)
    print(
        f"  TOTAL importable={len(valid_records)} "
        f"skipped_invalid={len(skipped_invalid)}"
    )
    print("")

    if dry_run:
        print("DRY RUN complete — no database was touched.")
        return 0

    # ---- Persist to database (deferred imports keep dry-run DB-free) ----
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from src.db.models import MCQ, MedicalSpecialty, DifficultyLevel
        from src.db.base import Base, get_database_url

        engine = create_engine(get_database_url())
        Base.metadata.create_all(engine)
        db = sessionmaker(bind=engine)()
    except Exception as e:  # noqa: BLE001
        print(f"[ERROR] Database connection failed: {e}")
        return 1

    print("Importing MCQs to database (per-row SAVEPOINTs)...")
    print("-" * 64)

    imported = 0
    skipped_duplicate = 0
    errors = 0

    try:
        for record in valid_records:
            # Idempotency: skip if question_id already exists.
            exists = (
                db.query(MCQ.id)
                .filter(MCQ.question_id == record["question_id"])
                .first()
            )
            if exists:
                skipped_duplicate += 1
                continue

            savepoint = db.begin_nested()
            try:
                mcq = MCQ(
                    question_id=record["question_id"],
                    question_text=record["question_text"],
                    options=record["options"],
                    correct_answer=record["correct_answer"],
                    explanation=record["explanation"],
                    citation=record["citation"],
                    citations=record["citations"] or None,
                    learning_points=record["learning_points"],
                    specialty=MedicalSpecialty(record["specialty"]),
                    difficulty=DifficultyLevel(record["difficulty"]),
                    tags=record["tags"],
                    image_url=record["image_url"],
                    is_published=True,
                )
                db.add(mcq)
                db.flush()  # surface constraint errors inside this savepoint only
                savepoint.commit()  # RELEASE SAVEPOINT — don't let them accumulate/recurse
                imported += 1
                if imported % 50 == 0:
                    print(f"  Imported {imported} MCQs...")
            except Exception as e:  # noqa: BLE001
                savepoint.rollback()  # roll back ONLY this row; keep good rows staged
                errors += 1
                print(f"  [ERROR] {record['question_id']}: {str(e)[:140]}")

        db.commit()  # single final commit; released savepoints persist
    except Exception as e:  # noqa: BLE001
        db.rollback()
        print(f"[ERROR] Fatal import error, rolled back staged rows: {e}")
        db.close()
        return 1

    print("-" * 64)
    print("\n[DONE] Import complete!")
    print(f"  - Imported:            {imported}")
    print(f"  - Skipped (duplicate): {skipped_duplicate}")
    print(f"  - Skipped (invalid):   {len(skipped_invalid)}")
    print(f"  - Errors:              {errors}")

    # Verify DB state.
    try:
        total = db.query(MCQ).count()
        resp = (
            db.query(MCQ)
            .filter(MCQ.specialty == MedicalSpecialty.RESPIRATORY)
            .count()
        )
        print(f"\nTotal MCQs in database:  {total}")
        print(f"Respiratory MCQs in DB:  {resp}")
    finally:
        db.close()

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import MCQs from JSON files")
    parser.add_argument(
        "--source",
        default="/home/dev/Development/irStudy/data/mcqs/",
        help="Source directory containing MCQ JSON files",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse + transform + validate + report only. No database connection.",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Alias kept for backwards compatibility (behaves like transform check).",
    )

    args = parser.parse_args()
    sys.exit(import_mcqs(args.source, dry_run=args.dry_run, validate=args.validate))
