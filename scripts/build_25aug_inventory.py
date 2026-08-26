#!/usr/bin/env python3
"""
Build INVENTORY.json for the 25-august-docs workshop content drop.

Walks 25-august-docs/extracted/ and maps every case file to its target
specialty directory under ICRP_OSCE_Preparation/ plus pipeline metadata.

USAGE:
    python3 scripts/build_25aug_inventory.py
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXTRACTED = ROOT / "25-august-docs" / "extracted"
OUT = ROOT / "25-august-docs" / "INVENTORY.json"

# bundle dir -> (default target specialty dir, DB specialty enum value)
BUNDLE_MAP = {
    "GIT 2026": ("Medicine", "gastroenterology"),
    "gynae": ("ObGyn", "obstetrics_gynaecology"),
    "obstetrics": ("ObGyn", "obstetrics_gynaecology"),
    "Med 5 MSK and urology": ("Musculoskeletal", "musculoskeletal"),
    "Med workshop 2 - 2026": ("Medicine", "neurology"),
}

# class-folder overrides within bundles (regex on class dir name, case-insensitive)
CLASS_OVERRIDES = [
    # NOTE: neurology must precede urology — "NEUROLOGY" contains "urology"
    (r"headache|neurology", ("Medicine", "neurology")),
    (r"ophthalmology", ("Ophthalmology", "ophthalmology")),
    (r"urology|ureteric", ("Urology", "urology")),
    (r"tiredness|unwell", ("Medicine", "general_practice")),
]


def classify(bundle: str, class_dir: str):
    for pattern, target in CLASS_OVERRIDES:
        if re.search(pattern, class_dir, re.IGNORECASE):
            return target
    return BUNDLE_MAP[bundle]


def main():
    inventory = []
    for bundle_dir in sorted(EXTRACTED.iterdir()):
        if not bundle_dir.is_dir():
            continue
        bundle = bundle_dir.name
        for f in sorted(bundle_dir.rglob("*")):
            if not f.is_file() or f.suffix.lower() not in (".pdf", ".docx"):
                continue
            class_dir = f.parent.name if f.parent != bundle_dir else ""
            target_dir, specialty = classify(bundle, class_dir)
            inventory.append({
                "source": str(f.relative_to(ROOT)),
                "bundle": bundle,
                "class": class_dir,
                "case_name": f.stem,
                "format": f.suffix.lower().lstrip("."),
                "size_kb": f.stat().st_size // 1024,
                "target_dir": target_dir,
                "specialty": specialty,
            })

    by_specialty = {}
    for item in inventory:
        by_specialty.setdefault(item["specialty"], 0)
        by_specialty[item["specialty"]] += 1

    OUT.write_text(json.dumps({
        "generated": "2026-08-25",
        "total_files": len(inventory),
        "by_specialty": by_specialty,
        "files": inventory,
    }, indent=2))

    print(f"Wrote {OUT} — {len(inventory)} files")
    for spec, n in sorted(by_specialty.items(), key=lambda kv: -kv[1]):
        print(f"  {spec:26s} {n}")


if __name__ == "__main__":
    main()
