#!/usr/bin/env python3
"""
Phase 5: chunk + embed the 25-august workshop notes into the Qdrant
`medical_knowledge` collection, so future content generation/validation can
retrieve and cite this workshop material (and to help close the O&G/MSK/
ophthalmology/urology coverage gap the assessment agents flagged).

Reads each staging/<Specialty>/<case>.assessed.json (+ its base .json for the
clinical text), chunks the clinical content, embeds with PubMedBERT (same model
that built the collection), and upserts points with matching payload schema.

USAGE:
    source venv/bin/activate
    python3 scripts/embed_workshop_notes.py [--dry-run]
"""

import argparse
import json
import re
import uuid
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
STAGING = ROOT / "25-august-docs" / "staging"
QDRANT_URL = "http://localhost:6333"
COLLECTION = "medical_knowledge"
MODEL = "microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext"
CHUNK_CHARS = 1000
OVERLAP = 150
# Deterministic namespace so re-runs regenerate identical point IDs (idempotent upsert)
NS = uuid.UUID("5a2b7c00-0000-4000-8000-25a120260825")


def clean_text(record, assessed):
    """Assemble clinical text: raw case text + expert corrections/enhancements."""
    parts = []
    if record.get("raw_text"):
        parts.append(record["raw_text"])
    elif record.get("html_fragment"):
        parts.append(re.sub(r"<[^>]+>", " ", record["html_fragment"]))
    er = assessed.get("expert_review", {})
    for c in er.get("corrections", []):
        parts.append(f"Correction: {c.get('issue','')} — {c.get('correction','')}")
    for e in er.get("enhancements", []):
        parts.append(f"Key point: {e}")
    return re.sub(r"\s+", " ", " ".join(parts)).strip()


def chunk(text):
    out, i = [], 0
    while i < len(text):
        out.append(text[i:i + CHUNK_CHARS])
        i += CHUNK_CHARS - OVERLAP
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(MODEL)

    assessed_files = sorted(STAGING.rglob("*.assessed.json"))
    points, n_notes = [], 0
    for ap_path in assessed_files:
        assessed = json.loads(ap_path.read_text())
        base_path = ap_path.with_name(ap_path.name.replace(".assessed", ""))
        record = json.loads(base_path.read_text()) if base_path.exists() else {}
        text = clean_text(record, assessed)
        if len(text) < 200:
            continue
        n_notes += 1
        title = assessed.get("title", record.get("title", ""))
        specialty = assessed.get("specialty", "")
        meta = assessed.get("expert_review", {}).get("metadata", {})
        for idx, ch in enumerate(chunk(text)):
            pid = str(uuid.uuid5(NS, f"{assessed['case_id']}:{idx}"))
            points.append({
                "id": pid,
                "payload": {
                    "text": ch,
                    "source": f"Dr Amir Workshop 2026 — {title}",
                    "page": None,
                    "chunk_index": idx,
                    "type": "workshop_note",
                    "char_count": len(ch),
                    "word_count": len(ch.split()),
                    "title": title,
                    "author": "Dr Amir Soufi (workshop)",
                    "year": "2026",
                    "edition": "Aug-2026 drop",
                    "source_category": "workshop",
                    "exam_type": "AMC_Clinical",
                    "specialty": specialty,
                    "station_type": meta.get("station_type"),
                },
                "_text": ch,
            })

    print(f"{n_notes} notes → {len(points)} chunks to embed")
    if args.dry_run:
        return

    # embed in batches and upsert
    B = 128
    for i in range(0, len(points), B):
        batch = points[i:i + B]
        vecs = model.encode([p.pop("_text") for p in batch], convert_to_numpy=True)
        payload = {"points": [{"id": p["id"], "vector": v.tolist(), "payload": p["payload"]}
                              for p, v in zip(batch, vecs)]}
        r = requests.put(f"{QDRANT_URL}/collections/{COLLECTION}/points?wait=true", json=payload, timeout=120)
        r.raise_for_status()
        print(f"  upserted {i+len(batch)}/{len(points)}")

    info = requests.get(f"{QDRANT_URL}/collections/{COLLECTION}").json()
    print(f"Collection now has {info['result']['points_count']} points")


if __name__ == "__main__":
    main()
