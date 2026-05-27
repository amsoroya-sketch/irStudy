#!/usr/bin/env python3
"""Validate RAG retrieval quality after embedding fix."""
import sys
sys.path.insert(0, '/home/dev/Development/irStudy/backend')

from src.ai.rag_service import RAGService

def main():
    rag = RAGService()
    
    test_queries = [
        ("heart attack", "cardiac"),
        ("myocardial infarction", "cardiac"),
        ("pneumonia", "respiratory"),
        ("diabetes type 2", "endocrine"),
        ("asthma management", "respiratory"),
        ("appendicitis", "surgery"),
        ("hypertension", "cardiovascular"),
        ("depression screening", "psychiatry"),
        ("pregnancy hypertension", "obstetrics"),
        ("pediatric fever", "paediatrics"),
    ]
    
    passed = 0
    for query, expected_specialty in test_queries:
        results = rag.search_similar(query, limit=3)
        if not results:
            print(f"❌ '{query}' — NO results")
            continue
        top = results[0]
        score = top['score']
        source = top.get('source', '?')
        status = "✅" if score > 0.30 else "⚠️" if score > 0.15 else "❌"
        print(f"{status} '{query}' — score: {score:.4f}, source: {source[:50]}")
        if score > 0.15:
            passed += 1
    
    print(f"\n{'='*60}")
    print(f"Results: {passed}/{len(test_queries)} queries returned meaningful matches")
    if passed >= 7:
        print("✅ RAG validation PASSED")
        sys.exit(0)
    else:
        print("❌ RAG validation FAILED")
        sys.exit(1)

if __name__ == "__main__":
    main()
