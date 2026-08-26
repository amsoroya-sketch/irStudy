#!/usr/bin/env python3
"""
Enrich staged workshop case JSONs with RAG context from the Qdrant
medical_knowledge textbook index.

For each 25-august-docs/staging/**/<case>.json, builds queries from the case
title + section headings, retrieves top textbook chunks, and writes them into
the record as `rag_context` (with qdrant_point_id for citations). Expert
agents (which have no Bash access) then consume this context directly.

USAGE:
    source venv/bin/activate
    python3 scripts/enrich_with_rag.py [--force]
"""

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STAGING = ROOT / "25-august-docs" / "staging"
QDRANT_URL = "http://localhost:6333"
COLLECTION = "medical_knowledge"
MODEL = "microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext"

PER_QUERY = 3
MAX_CHUNKS = 12
MAX_QUERIES = 6


def build_queries(record) -> list:
    title = re.sub(r"^\d+[\.\s]*", "", record["title"]).strip()
    specialty = record["specialty"].replace("_", " ")
    queries = [f"{title} {specialty}"]

    headings = []
    if record.get("html_fragment"):
        headings = re.findall(r"<h[123][^>]*>(.*?)</h[123]>", record["html_fragment"])
        headings = [re.sub(r"<[^>]+>", "", h).strip() for h in headings]
    else:
        # PDFs: use short standalone lines that look like headings
        for line in record["raw_text"].split("\n"):
            line = line.strip()
            if 8 < len(line) < 60 and not line[-1:] in ".:;," and line[0].isupper():
                headings.append(line)

    seen = {q.lower() for q in queries}
    for h in headings:
        q = f"{title} {h}"
        if h.lower() not in seen and len(h) > 8:
            queries.append(q)
            seen.add(h.lower())
        if len(queries) >= MAX_QUERIES:
            break
    queries.append(f"{title} red flags differential diagnosis Australian guidelines")
    return queries[:MAX_QUERIES + 1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    import requests
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(MODEL)

    files = sorted(p for p in STAGING.rglob("*.json")
                   if p.name not in ("extraction_summary.json",)
                   and not p.name.endswith(".assessed.json"))
    done = skipped = 0
    for path in files:
        record = json.loads(path.read_text())
        if record.get("rag_context") and not args.force:
            skipped += 1
            continue

        queries = build_queries(record)
        vectors = model.encode(queries, convert_to_numpy=True)
        chunks, seen_ids = [], set()
        for q, vec in zip(queries, vectors):
            resp = requests.post(
                f"{QDRANT_URL}/collections/{COLLECTION}/points/search",
                json={"vector": vec.tolist(), "limit": PER_QUERY, "with_payload": True},
                timeout=30,
            )
            resp.raise_for_status()
            for hit in resp.json()["result"]:
                pid = str(hit["id"])
                if pid in seen_ids:
                    continue
                seen_ids.add(pid)
                p = hit.get("payload", {})
                chunks.append({
                    "qdrant_point_id": pid,
                    "score": round(hit["score"], 3),
                    "source": p.get("source") or p.get("book") or p.get("title") or "Unknown",
                    "page": p.get("page") or p.get("page_ref"),
                    "query": q,
                    "text": (p.get("text") or p.get("content") or "")[:700],
                })
        chunks.sort(key=lambda c: -c["score"])
        record["rag_context"] = chunks[:MAX_CHUNKS]
        path.write_text(json.dumps(record, ensure_ascii=False))
        done += 1
        if done % 20 == 0:
            print(f"  {done}/{len(files)} enriched")

    print(f"Done: {done} enriched, {skipped} skipped (already had context)")


if __name__ == "__main__":
    main()
