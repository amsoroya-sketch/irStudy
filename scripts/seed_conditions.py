#!/usr/bin/env python3
"""
Seed the AMC conditions/blueprint spine — deterministically, from real content.

PRD-CONDITIONS-SPINE-001.

What it does:
    1. ``derive_conditions(mcqs, osces, personas)`` — a PURE function that extracts
       distinct ``(specialty, normalized-name)`` pairs from existing content
       topics/titles/diagnoses, normalizes case + whitespace, dedupes, maps the
       specialty through the controlled ``MedicalSpecialty`` vocabulary (skipping
       + logging anything unmappable), and assigns an AMC blueprint area from the
       single documented ``SPECIALTY_TO_BLUEPRINT`` dict. NO LLM. Never fabricates
       conditions — every row traces back to a real content item.
    2. ``main()`` — loads content from disk (and, when a DB is reachable, from the
       live tables), calls ``derive_conditions``, writes
       ``data/amc_blueprints/conditions.json``, and (best-effort) upserts rows into
       the ``conditions`` table. Idempotent: ``condition_code`` is unique, so a
       re-run inserts nothing new.

Usage:
    python scripts/seed_conditions.py            # write conditions.json (+ DB if reachable)
    python scripts/seed_conditions.py --dry-run  # derive + write JSON only, never touch DB

Security: no credentials are read or written; DB access is best-effort and uses
the project's get_database_url() only.
"""

from __future__ import annotations

import os
import re
import sys
import json
import glob
import argparse
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = REPO_ROOT / "backend"
DATA_DIR = REPO_ROOT / "data"
BLUEPRINT_DIR = DATA_DIR / "amc_blueprints"
CONDITIONS_JSON = BLUEPRINT_DIR / "conditions.json"
REPORT_DIR = BLUEPRINT_DIR / "_reports"
SKIPPED_JSON = REPORT_DIR / "seed_skipped.json"

# Controlled specialty vocabulary. Imported lazily so the pure functions work
# even when SQLAlchemy models can't be imported (fallback list mirrors the enum).
try:  # pragma: no cover - import guard
    sys.path.insert(0, str(BACKEND_DIR))
    from src.db.models import MedicalSpecialty  # type: ignore

    _VALID_SPECIALTIES = {e.value for e in MedicalSpecialty}
except Exception:  # noqa: BLE001
    _VALID_SPECIALTIES = {
        "cardiology", "respiratory", "gastroenterology", "neurology", "psychiatry",
        "endocrinology", "emergency_medicine", "general_practice", "paediatrics",
        "obstetrics_gynaecology", "surgery", "ophthalmology", "urology",
        "musculoskeletal",
    }


# ---------------------------------------------------------------------------
# Specialty normalization (raw string -> MedicalSpecialty value, or None)
# ---------------------------------------------------------------------------
# Unmappable specialties return None (they are SKIPPED + logged, never coerced to
# a default) so the seed never fabricates a wrong classification.
_SPECIALTY_ALIASES: Dict[str, str] = {
    "cardiology": "cardiology",
    "cardiovascular": "cardiology",
    "respiratory": "respiratory",
    "respiratory_medicine": "respiratory",
    "pulmonology": "respiratory",
    "gastroenterology": "gastroenterology",
    "gastrointestinal": "gastroenterology",
    "neurology": "neurology",
    "psychiatry": "psychiatry",
    "mental_health": "psychiatry",
    "endocrinology": "endocrinology",
    "endocrine": "endocrinology",
    "emergency": "emergency_medicine",
    "emergency_medicine": "emergency_medicine",
    "general_practice": "general_practice",
    "gp": "general_practice",
    "pediatrics": "paediatrics",
    "paediatrics": "paediatrics",
    "child_health": "paediatrics",
    "obstetrics": "obstetrics_gynaecology",
    "gynaecology": "obstetrics_gynaecology",
    "gynecology": "obstetrics_gynaecology",
    "obstetrics_gynaecology": "obstetrics_gynaecology",
    "obstetrics_and_gynaecology": "obstetrics_gynaecology",
    "womens_health": "obstetrics_gynaecology",
    "surgery": "surgery",
    "general_surgery": "surgery",
    "ophthalmology": "ophthalmology",
    "urology": "urology",
    "musculoskeletal": "musculoskeletal",
    "orthopaedics": "musculoskeletal",
    "orthopedics": "musculoskeletal",
    "rheumatology": "musculoskeletal",
}


def normalize_specialty(raw: Any) -> Optional[str]:
    """Coerce a raw specialty value to a canonical MedicalSpecialty value, or None."""
    if isinstance(raw, list):
        raw = raw[0] if raw else None
    if not isinstance(raw, str):
        return None
    key = raw.lower().strip().replace(" ", "_").replace("&", "and").replace("/", "_")
    key = re.sub(r"_+", "_", key).strip("_")
    mapped = _SPECIALTY_ALIASES.get(key)
    if mapped is None and key in _VALID_SPECIALTIES:
        mapped = key
    if mapped in _VALID_SPECIALTIES:
        return mapped
    return None


# ---------------------------------------------------------------------------
# Documented specialty -> AMC blueprint-area map (the ONE source of truth).
# ---------------------------------------------------------------------------
SPECIALTY_TO_BLUEPRINT: Dict[str, str] = {
    # Adult Internal Medicine sub-areas
    "cardiology": "Cardiovascular Medicine",
    "respiratory": "Respiratory Medicine",
    "gastroenterology": "Gastroenterology",
    "endocrinology": "Endocrinology",
    "neurology": "Neurology",
    # Standalone AMC domains
    "psychiatry": "Mental Health",
    "obstetrics_gynaecology": "Women's Health",
    "paediatrics": "Child Health",
    "general_practice": "General Practice",
    "emergency_medicine": "Emergency Medicine",
    # Surgery & Procedures cluster
    "surgery": "Surgery & Procedures",
    "urology": "Surgery & Procedures",
    "ophthalmology": "Surgery & Procedures",
    "musculoskeletal": "Surgery & Procedures",
}


def blueprint_for(specialty: str) -> str:
    """Blueprint area for a canonical specialty (falls back to a titled label)."""
    return SPECIALTY_TO_BLUEPRINT.get(specialty, specialty.replace("_", " ").title())


# ---------------------------------------------------------------------------
# Name normalization + code generation
# ---------------------------------------------------------------------------
def normalize_name(raw: Any) -> Optional[str]:
    """Collapse whitespace + trim; return None for empty/non-string names."""
    if not isinstance(raw, str):
        return None
    name = re.sub(r"\s+", " ", raw).strip()
    return name or None


_SPECIALTY_ABBR: Dict[str, str] = {
    "cardiology": "CARD",
    "respiratory": "RESP",
    "gastroenterology": "GAST",
    "neurology": "NEUR",
    "psychiatry": "PSYC",
    "endocrinology": "ENDO",
    "emergency_medicine": "EMER",
    "general_practice": "GENP",
    "paediatrics": "PAED",
    "obstetrics_gynaecology": "OBGY",
    "surgery": "SURG",
    "ophthalmology": "OPHT",
    "urology": "UROL",
    "musculoskeletal": "MUSC",
}


def _slug(name: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", name).strip("-").upper()
    return slug or "UNKNOWN"


def make_condition_code(specialty: str, name: str) -> str:
    """Stable, unique-per-(specialty,name) condition code, e.g. RESP-ASTHMA."""
    abbr = _SPECIALTY_ABBR.get(specialty, specialty[:4].upper())
    return f"{abbr}-{_slug(name)}"


# ---------------------------------------------------------------------------
# Field extraction per content type
# ---------------------------------------------------------------------------
def _mcq_name(item: Dict[str, Any]) -> Optional[str]:
    return normalize_name(item.get("topic") or item.get("subtopic") or item.get("title"))


def _osce_name(item: Dict[str, Any]) -> Optional[str]:
    return normalize_name(
        item.get("title") or item.get("station_title") or item.get("topic")
    )


def _persona_name(item: Dict[str, Any]) -> Optional[str]:
    return normalize_name(
        item.get("expected_diagnosis")
        or item.get("diagnosis")
        or item.get("topic")
        or item.get("chief_complaint")
    )


# ---------------------------------------------------------------------------
# Core (PURE) derivation
# ---------------------------------------------------------------------------
def derive_conditions(
    mcqs: Optional[List[Dict[str, Any]]] = None,
    osces: Optional[List[Dict[str, Any]]] = None,
    personas: Optional[List[Dict[str, Any]]] = None,
    skipped: Optional[List[Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    """
    Derive a deduped, deterministic list of condition records from content.

    Each returned dict: condition_code, name, specialty, amc_blueprint_area,
    aliases (None), system (None). Deduped by (specialty, name.lower()); the
    first-seen original name casing wins. Unmappable specialties / empty names
    are skipped (appended to ``skipped`` when provided). No LLM, no fabrication.
    """
    sources = (
        (mcqs or [], _mcq_name),
        (osces or [], _osce_name),
        (personas or [], _persona_name),
    )

    seen: Dict[tuple, Dict[str, Any]] = {}
    skip_log = skipped if skipped is not None else []

    for items, name_fn in sources:
        for item in items:
            if not isinstance(item, dict):
                continue
            specialty = normalize_specialty(item.get("specialty"))
            name = name_fn(item)
            if specialty is None or name is None:
                skip_log.append(
                    {
                        "reason": "unmappable_specialty" if specialty is None else "empty_name",
                        "specialty": item.get("specialty"),
                        "name": name,
                    }
                )
                continue
            key = (specialty, name.lower())
            if key in seen:
                continue
            seen[key] = {
                "condition_code": make_condition_code(specialty, name),
                "name": name,
                "specialty": specialty,
                "amc_blueprint_area": blueprint_for(specialty),
                "aliases": None,
                "system": None,
            }

    # Deterministic ordering by condition_code.
    return sorted(seen.values(), key=lambda c: c["condition_code"])


# ---------------------------------------------------------------------------
# Content loading from disk (for the standalone script)
# ---------------------------------------------------------------------------
def _is_ignored(path: Path) -> bool:
    name = path.name.lower()
    if "backups" in [p.lower() for p in path.parts]:
        return True
    if "_backup_" in name or "_with_images" in name or "_regenerated" in name:
        return True
    return False


def _load_json(path: Path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:  # noqa: BLE001
        return None


def _extract_items(data, keys):
    if isinstance(data, dict):
        for k in keys:
            if isinstance(data.get(k), list):
                return data[k]
        if data.get("specialty"):  # bare single object (e.g. EMR case / persona)
            return [data]
        return []
    if isinstance(data, list):
        return data
    return []


def _load_disk_content():
    mcqs: List[Dict[str, Any]] = []
    osces: List[Dict[str, Any]] = []
    personas: List[Dict[str, Any]] = []

    for fp in sorted(glob.glob(str(DATA_DIR / "mcqs" / "*.json"))):
        path = Path(fp)
        if _is_ignored(path):
            continue
        for it in _extract_items(_load_json(path), ("mcqs", "questions")):
            if isinstance(it, dict):
                mcqs.append(it)

    for fp in sorted(glob.glob(str(DATA_DIR / "osces" / "*.json"))):
        path = Path(fp)
        if _is_ignored(path):
            continue
        for it in _extract_items(_load_json(path), ("osces",)):
            if isinstance(it, dict):
                osces.append(it)

    # EMR practice cases carry an expected diagnosis-like specialty/complaint; feed
    # them through the persona extractor.
    emr_dir = DATA_DIR / "emr_practice_cases"
    if emr_dir.exists():
        for fp in sorted(glob.glob(str(emr_dir / "*.json"))):
            path = Path(fp)
            if _is_ignored(path):
                continue
            for it in _extract_items(_load_json(path), ()):
                if isinstance(it, dict):
                    personas.append(it)

    return mcqs, osces, personas


# ---------------------------------------------------------------------------
# Best-effort DB upsert (idempotent via unique condition_code)
# ---------------------------------------------------------------------------
def _db_available() -> bool:
    return bool(
        os.getenv("DATABASE_URL")
        or os.getenv("DATABASE_PASSWORD")
        or os.path.exists("/run/secrets/db_password")
    )


def upsert_conditions(conditions: List[Dict[str, Any]]) -> Dict[str, int]:
    """Insert any conditions whose condition_code is not already present."""
    sys.path.insert(0, str(BACKEND_DIR))
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from src.db.base import get_database_url
    from src.db.models import Condition  # type: ignore

    engine = create_engine(get_database_url())
    db = sessionmaker(bind=engine)()
    inserted = 0
    try:
        existing = {code for (code,) in db.query(Condition.condition_code).all()}
        for c in conditions:
            if c["condition_code"] in existing:
                continue
            db.add(
                Condition(
                    condition_code=c["condition_code"],
                    name=c["name"],
                    specialty=c["specialty"],
                    amc_blueprint_area=c["amc_blueprint_area"],
                    aliases=c.get("aliases"),
                    system=c.get("system"),
                )
            )
            existing.add(c["condition_code"])
            inserted += 1
        db.commit()
    finally:
        db.close()
    return {"inserted": inserted, "total": len(conditions)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed AMC conditions/blueprint spine")
    parser.add_argument(
        "--dry-run", action="store_true", help="Derive + write JSON only; never touch the DB"
    )
    args = parser.parse_args()

    mcqs, osces, personas = _load_disk_content()
    skipped: List[Dict[str, Any]] = []
    conditions = derive_conditions(mcqs=mcqs, osces=osces, personas=personas, skipped=skipped)

    BLUEPRINT_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONDITIONS_JSON, "w", encoding="utf-8") as f:
        json.dump({"conditions": conditions, "count": len(conditions)}, f, indent=2, ensure_ascii=False)
    print(f"[OK] Derived {len(conditions)} conditions -> {CONDITIONS_JSON}")

    if skipped:
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        with open(SKIPPED_JSON, "w", encoding="utf-8") as f:
            json.dump({"skipped": skipped, "count": len(skipped)}, f, indent=2, ensure_ascii=False)
        print(f"[note] {len(skipped)} content rows skipped (unmapped specialty / empty name)"
              f" -> {SKIPPED_JSON}")

    # by-specialty summary
    by_spec: Dict[str, int] = {}
    for c in conditions:
        by_spec[c["specialty"]] = by_spec.get(c["specialty"], 0) + 1
    print("  by specialty:", json.dumps(by_spec, sort_keys=True))

    if args.dry_run:
        print("[note] --dry-run: DB not touched.")
        return 0

    if not _db_available():
        print("[note] Database unavailable — wrote conditions.json only.")
        return 0

    try:
        result = upsert_conditions(conditions)
        print(f"[OK] DB upsert: inserted {result['inserted']} / {result['total']} conditions.")
    except Exception as e:  # noqa: BLE001
        print(f"[note] DB upsert skipped: {str(e)[:160]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
