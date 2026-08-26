#!/usr/bin/env python3
"""
CLI RAG query against the Qdrant medical_knowledge collection (textbook index).

Used by expert agents during content assessment to fact-check claims and
collect citations with qdrant_point_id.

USAGE:
    source venv/bin/activate
    python3 scripts/rag_query_cli.py "postmenopausal bleeding endometrial cancer" [--top 5] [--json]

Batch mode (one query per line on stdin, JSON-lines out):
    echo -e "q1\nq2" | python3 scripts/rag_query_cli.py --stdin --json
"""

import argparse
import json
import sys

QDRANT_URL = "http://localhost:6333"
COLLECTION = "medical_knowledge"
MODEL = "microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext"

_model = None


def get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(MODEL)
    return _model


def search(query: str, top: int = 5):
    import requests
    vec = get_model().encode(query, convert_to_numpy=True).tolist()
    resp = requests.post(
        f"{QDRANT_URL}/collections/{COLLECTION}/points/search",
        json={"vector": vec, "limit": top, "with_payload": True},
        timeout=30,
    )
    resp.raise_for_status()
    out = []
    for hit in resp.json()["result"]:
        p = hit.get("payload", {})
        out.append({
            "qdrant_point_id": str(hit["id"]),
            "score": round(hit["score"], 3),
            "source": p.get("source") or p.get("book") or p.get("title") or "Unknown",
            "page": p.get("page") or p.get("page_ref"),
            "text": (p.get("text") or p.get("content") or "")[:600],
        })
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query", nargs="?", default=None)
    ap.add_argument("--top", type=int, default=5)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--stdin", action="store_true")
    args = ap.parse_args()

    queries = [l.strip() for l in sys.stdin if l.strip()] if args.stdin else [args.query]
    if not queries or queries[0] is None:
        ap.error("provide a query or --stdin")

    for q in queries:
        results = search(q, args.top)
        if args.json:
            print(json.dumps({"query": q, "results": results}, ensure_ascii=False))
        else:
            print(f"\n=== {q} ===")
            for r in results:
                print(f"[{r['score']}] {r['source']} (p.{r['page']}) id={r['qdrant_point_id']}")
                print(f"    {r['text'][:200]}")


if __name__ == "__main__":
    main()
