#!/usr/bin/env python3
"""
Repair staged case JSONs whose target_dir/specialty disagree with the current
INVENTORY.json (e.g. the NEUROLOGY-matched-'urology' misclassification fixed
on 2026-08-25). Moves files + their assets to the correct staging dir and
patches the JSON fields.
"""

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STAGING = ROOT / "25-august-docs" / "staging"
INVENTORY = ROOT / "25-august-docs" / "INVENTORY.json"

inv = json.loads(INVENTORY.read_text())
by_source = {f["source"]: f for f in inv["files"]}

moved = patched = 0
for path in sorted(STAGING.rglob("*.json")):
    if path.name.endswith((".assessed.json",)) or path.name == "extraction_summary.json":
        continue
    rec = json.loads(path.read_text())
    item = by_source.get(rec.get("source_file"))
    if not item:
        continue
    if rec["target_dir"] == item["target_dir"] and rec["specialty"] == item["specialty"]:
        continue

    rec["target_dir"], rec["specialty"] = item["target_dir"], item["specialty"]
    new_dir = STAGING / item["target_dir"]
    (new_dir / "assets").mkdir(parents=True, exist_ok=True)
    for img in rec.get("images", []):
        src = path.parent / "assets" / img
        if src.exists():
            shutil.move(str(src), new_dir / "assets" / img)
    new_path = new_dir / path.name
    new_path.write_text(json.dumps(rec, ensure_ascii=False))
    if new_path != path:
        path.unlink()
        moved += 1
    patched += 1
    print(f"  {path.name}: → {item['target_dir']}/{item['specialty']}")

print(f"Repaired {patched} records ({moved} moved)")
