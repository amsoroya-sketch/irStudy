#!/usr/bin/env python3
"""
Content reconciliation report — AUTHORED vs LIVE vs MALFORMED.

Purpose:
    Detect silent import losses (like the respiratory MCQ incident where 200
    authored items yielded ~1 live row) by comparing what was AUTHORED on disk
    against what is actually LIVE in the database, per specialty per content-type.

What it does:
    1. Scans authored content on disk:
         - data/mcqs/*.json          (keys: mcqs | questions | bare list)
         - data/osces/*.json         (keys: osces | bare list)
         - data/study_cards/*.json   (keys: cards | bare list)
         - data/emr_practice_cases/*.json  (one case object per file)
       Ignores *_backup_*, *_with_images*, and anything under a backups/ dir.
       Flags MALFORMED MCQs (question-as-string or missing/insufficient options).
    2. If the database is reachable (get_database_url succeeds AND a password is
       configured), queries live counts from mcqs / osces / study_cards /
       mock_patients and prints an AUTHORED vs LIVE vs MALFORMED table, flagging
       any specialty where LIVE << AUTHORED.
    3. If the DB is unavailable, prints the AUTHORED / MALFORMED table only and
       notes that the DB was unavailable.

Usage:
    python scripts/content_reconciliation.py
    python scripts/content_reconciliation.py --json   # also write reconciliation.json

Security: no credentials are read or written; DB access is best-effort and uses
the project's get_database_url() (Docker secret / env var) only.
"""

import os
import sys
import json
import glob
import argparse
from pathlib import Path
from collections import defaultdict

REPO_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = REPO_ROOT / "backend"
DATA_DIR = REPO_ROOT / "data"
REPORT_DIR = DATA_DIR / "mcqs" / "_reports"
RECON_REPORT = REPORT_DIR / "reconciliation.json"

# Reuse the exact specialty mapping AND malformed-guard from the importer so the
# report and the importer AGREE on what is malformed (no false positives).
sys.path.insert(0, str(BACKEND_DIR / "scripts"))
try:
    from import_mcqs import map_specialty, transform_mcq, validate_record  # type: ignore
except Exception:  # noqa: BLE001 — fallback keeps the report usable in isolation
    def map_specialty(specialty_str: str) -> str:  # type: ignore
        return (specialty_str or "general_practice").lower().strip().replace(" ", "_")

    transform_mcq = None  # type: ignore
    validate_record = None  # type: ignore


CONTENT_TYPES = ("mcq", "osce", "study_card", "emr_case")


def _is_ignored(path: Path) -> bool:
    name = path.name.lower()
    if "backups" in path.parts or "backup" in [p.lower() for p in path.parts]:
        return True
    if "_backup_" in name or "_with_images" in name:
        return True
    return False


def _load_json(path: Path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:  # noqa: BLE001
        return None


def _extract_items(data, keys):
    """Return a list of item dicts from a {key:[...]} dict or a bare list."""
    if isinstance(data, dict):
        for k in keys:
            if isinstance(data.get(k), list):
                return data[k]
        # bare object (e.g. a single EMR case) is itself the item
        return None
    if isinstance(data, list):
        return data
    return []


def _spec(raw) -> str:
    """Coerce a specialty value (str, list, or None) to a canonical specialty."""
    if isinstance(raw, list):
        raw = raw[0] if raw else "general_practice"
    if not isinstance(raw, str):
        raw = "general_practice"
    return map_specialty(raw)


def _mcq_is_malformed(item: dict) -> bool:
    """
    An MCQ is malformed ONLY IF the importer would skip it as unimportable.

    We delegate to the importer's own transform_mcq + validate_record so the
    report and the importer AGREE exactly. A string `question` is FINE as long as
    a usable options container exists (nested question.options OR top-level
    options) and the correct_answer letter resolves into those options.
    """
    if transform_mcq is not None and validate_record is not None:
        try:
            return validate_record(transform_mcq(item)) is not None
        except Exception:  # noqa: BLE001 — treat unparseable items as malformed
            return True

    # Fallback (importer not importable): check BOTH nested and top-level options.
    q = item.get("question")
    options = q.get("options", {}) if isinstance(q, dict) else {}
    if not options:
        options = item.get("options", {})
    if isinstance(options, list):
        return len(options) < 2
    return not (isinstance(options, dict) and len(options) >= 2)


def scan_authored():
    """Return (authored, malformed): dict[content_type][specialty] -> int."""
    authored = {ct: defaultdict(int) for ct in CONTENT_TYPES}
    malformed = {ct: defaultdict(int) for ct in CONTENT_TYPES}

    # --- MCQs ---
    for fp in sorted(glob.glob(str(DATA_DIR / "mcqs" / "*.json"))):
        path = Path(fp)
        if _is_ignored(path):
            continue
        items = _extract_items(_load_json(path), ("mcqs", "questions"))
        if not items:
            continue
        for it in items:
            if not isinstance(it, dict):
                continue
            spec = _spec(it.get("specialty"))
            authored["mcq"][spec] += 1
            if _mcq_is_malformed(it):
                malformed["mcq"][spec] += 1

    # --- OSCEs ---
    for fp in sorted(glob.glob(str(DATA_DIR / "osces" / "*.json"))):
        path = Path(fp)
        if _is_ignored(path):
            continue
        items = _extract_items(_load_json(path), ("osces",))
        if not items:
            continue
        for it in items:
            if isinstance(it, dict):
                authored["osce"][_spec(it.get("specialty"))] += 1

    # --- Study cards ---
    for fp in sorted(glob.glob(str(DATA_DIR / "study_cards" / "*.json"))):
        path = Path(fp)
        if _is_ignored(path):
            continue
        items = _extract_items(_load_json(path), ("cards",))
        if not items:
            continue
        for it in items:
            if isinstance(it, dict):
                authored["study_card"][_spec(it.get("specialty"))] += 1

    # --- EMR practice cases (one object per file) ---
    emr_dir = DATA_DIR / "emr_practice_cases"
    if emr_dir.exists():
        for fp in sorted(glob.glob(str(emr_dir / "*.json"))):
            path = Path(fp)
            if _is_ignored(path):
                continue
            data = _load_json(path)
            if isinstance(data, dict) and data.get("specialty"):
                authored["emr_case"][_spec(data.get("specialty"))] += 1
            elif isinstance(data, list):
                for it in data:
                    if isinstance(it, dict) and it.get("specialty"):
                        authored["emr_case"][_spec(it.get("specialty"))] += 1

    return authored, malformed


def query_live():
    """Best-effort live DB counts. Returns dict[content_type][specialty]->int or None."""
    # Skip cleanly if no password is configured (avoids import-time crash in base.py).
    if not os.getenv("DATABASE_URL") and not os.getenv("DATABASE_PASSWORD") \
            and not os.path.exists("/run/secrets/db_password"):
        return None
    sys.path.insert(0, str(BACKEND_DIR))
    try:
        from sqlalchemy import create_engine, func
        from sqlalchemy.orm import sessionmaker
        from src.db.base import get_database_url
        from src.db.models import MCQ, OSCE, StudyCard  # type: ignore

        engine = create_engine(get_database_url())
        db = sessionmaker(bind=engine)()
    except Exception as e:  # noqa: BLE001
        print(f"[note] DB unavailable: {str(e)[:120]}")
        return None

    live = {ct: defaultdict(int) for ct in CONTENT_TYPES}
    try:
        for model, ct in ((MCQ, "mcq"), (OSCE, "osce"), (StudyCard, "study_card")):
            try:
                rows = db.query(model.specialty, func.count(model.id)).group_by(
                    model.specialty
                ).all()
                for spec, cnt in rows:
                    key = getattr(spec, "value", str(spec))
                    live[ct][key] = cnt
            except Exception as e:  # noqa: BLE001
                print(f"[note] could not count {ct}: {str(e)[:100]}")
        # mock_patients feeds EMR practice; count if present
        try:
            from src.db.models import MockPatient  # type: ignore
            rows = db.query(MockPatient.specialty, func.count(MockPatient.id)).group_by(
                MockPatient.specialty
            ).all()
            for spec, cnt in rows:
                live["emr_case"][getattr(spec, "value", str(spec))] = cnt
        except Exception:  # noqa: BLE001
            pass
    finally:
        db.close()
    return live


def coverage_by_blueprint(conditions, content):
    """
    Count linked content items per AMC blueprint area, per content type.

    PRD-CONDITIONS-SPINE-001.

    Args:
        conditions: list of {"id", "amc_blueprint_area", ...} (the seeded spine).
        content: dict[content_type] -> list of items each carrying "condition_id",
            e.g. {"mcq": [...], "osce": [...], "persona": [...], "emr_case": [...]}.

    Returns:
        dict[blueprint_area] -> {content_type: count}. Every blueprint area present
        in ``conditions`` appears (zero-filled), so true gaps are visible. Items
        whose ``condition_id`` doesn't resolve to a known condition are ignored
        (never fabricated into a bucket).
    """
    content = content or {}
    content_types = list(content.keys())

    # condition_id -> blueprint area
    area_by_condition = {}
    areas = set()
    for cond in conditions or []:
        area = cond.get("amc_blueprint_area")
        if area is None:
            continue
        areas.add(area)
        if cond.get("id") is not None:
            area_by_condition[cond["id"]] = area

    # Zero-fill every known blueprint area across every content type.
    rows = {area: {ct: 0 for ct in content_types} for area in areas}

    for ct, items in content.items():
        for item in items or []:
            cid = item.get("condition_id") if isinstance(item, dict) else None
            area = area_by_condition.get(cid)
            if area is None:
                continue
            rows[area][ct] = rows[area].get(ct, 0) + 1

    return rows


def query_coverage():
    """Best-effort live coverage-by-blueprint. Returns rows dict or None."""
    if not os.getenv("DATABASE_URL") and not os.getenv("DATABASE_PASSWORD") \
            and not os.path.exists("/run/secrets/db_password"):
        return None
    sys.path.insert(0, str(BACKEND_DIR))
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from src.db.base import get_database_url
        from src.db.models import (  # type: ignore
            Condition, MCQ, OSCE, PatientPersona, MockPatient,
        )

        engine = create_engine(get_database_url())
        db = sessionmaker(bind=engine)()
    except Exception:  # noqa: BLE001
        return None

    try:
        conditions = [
            {"id": c.id, "amc_blueprint_area": c.amc_blueprint_area}
            for c in db.query(Condition).all()
        ]
        content = {
            "mcq": [{"condition_id": cid} for (cid,) in db.query(MCQ.condition_id).all()],
            "osce": [{"condition_id": cid} for (cid,) in db.query(OSCE.condition_id).all()],
            "persona": [
                {"condition_id": cid} for (cid,) in db.query(PatientPersona.condition_id).all()
            ],
            "emr_case": [
                {"condition_id": cid} for (cid,) in db.query(MockPatient.condition_id).all()
            ],
        }
    except Exception:  # noqa: BLE001
        return None
    finally:
        db.close()

    return coverage_by_blueprint(conditions, content)


def _print_table(authored, malformed, live):
    all_specs = sorted(
        {s for ct in CONTENT_TYPES for s in authored[ct]}
        | ({s for ct in CONTENT_TYPES for s in (live or {}).get(ct, {})} if live else set())
    )
    flags = []
    for ct in CONTENT_TYPES:
        header = f"CONTENT TYPE: {ct.upper()}"
        print("\n" + "=" * 72)
        print(header)
        print("=" * 72)
        if live:
            print(f"  {'specialty':<24}{'AUTHORED':>10}{'LIVE':>8}{'MALFORMED':>12}")
        else:
            print(f"  {'specialty':<24}{'AUTHORED':>10}{'MALFORMED':>12}")
        print("  " + "-" * 54)
        for spec in all_specs:
            auth = authored[ct].get(spec, 0)
            mal = malformed[ct].get(spec, 0)
            if live:
                lv = live[ct].get(spec, 0)
                if auth == 0 and lv == 0:
                    continue
                marker = ""
                importable = auth - mal
                if importable > 0 and lv < importable * 0.5:
                    marker = "  <== SILENT LOSS?"
                    flags.append((ct, spec, importable, lv))
                print(f"  {spec:<24}{auth:>10}{lv:>8}{mal:>12}{marker}")
            else:
                if auth == 0:
                    continue
                print(f"  {spec:<24}{auth:>10}{mal:>12}")
    return flags


def main() -> int:
    parser = argparse.ArgumentParser(description="Content reconciliation report")
    parser.add_argument(
        "--json", action="store_true", help="Also write data/mcqs/_reports/reconciliation.json"
    )
    args = parser.parse_args()

    print("=" * 72)
    print("CONTENT RECONCILIATION — AUTHORED vs LIVE vs MALFORMED")
    print("=" * 72)

    authored, malformed = scan_authored()
    live = query_live()
    if live is None:
        print("\n[note] Database was UNAVAILABLE — showing AUTHORED / MALFORMED only.")

    flags = _print_table(authored, malformed, live)

    print("\n" + "=" * 72)
    print("SUMMARY")
    print("=" * 72)
    for ct in CONTENT_TYPES:
        total_auth = sum(authored[ct].values())
        total_mal = sum(malformed[ct].values())
        line = f"  {ct:<12} authored={total_auth:>5} malformed={total_mal:>4}"
        if live:
            line += f" live={sum(live[ct].values()):>5}"
        print(line)
    if live and flags:
        print("\n  POTENTIAL SILENT IMPORT LOSSES (importable >> live):")
        for ct, spec, importable, lv in flags:
            print(f"    - {ct}/{spec}: importable≈{importable} but live={lv}")
    elif live:
        print("\n  No silent import losses detected.")

    coverage = query_coverage() if live else None
    if coverage:
        print("\n" + "=" * 72)
        print("COVERAGE BY AMC BLUEPRINT AREA (linked content per type)")
        print("=" * 72)
        for area in sorted(coverage):
            counts = coverage[area]
            print(f"  {area:<28}" + "  ".join(f"{ct}={counts.get(ct, 0)}" for ct in
                  ("mcq", "osce", "persona", "emr_case")))

    if args.json:
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        payload = {
            "authored": {ct: dict(authored[ct]) for ct in CONTENT_TYPES},
            "malformed": {ct: dict(malformed[ct]) for ct in CONTENT_TYPES},
            "live": ({ct: dict(live[ct]) for ct in CONTENT_TYPES} if live else None),
            "db_available": live is not None,
            "coverage_by_blueprint": coverage,
            "flags": [
                {"content_type": ct, "specialty": s, "importable": imp, "live": lv}
                for (ct, s, imp, lv) in flags
            ],
        }
        with open(RECON_REPORT, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        print(f"\n[OK] Wrote reconciliation report -> {RECON_REPORT}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
