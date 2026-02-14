#!/usr/bin/env python3
"""
Inspect RAG Database Content
Week 2 Day 1 - Understanding why semantic scores are stuck at 0.76-0.79

Critical Finding: Improved queries made NO difference (+0.000 improvement)
Hypothesis: RAG database doesn't contain Australian guidelines we're querying
"""

import sys
from pathlib import Path
from collections import defaultdict

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from qdrant_client import QdrantClient


def main():
    """Inspect RAG database content"""
    print("\n" + "="*70)
    print("🔍 RAG DATABASE CONTENT INSPECTION")
    print("="*70)
    print("Goal: Understand why semantic scores stuck at 0.76-0.79")
    print("Hypothesis: Database missing Australian guidelines")
    print("="*70 + "\n")

    client = QdrantClient(url="http://localhost:6333")
    collection = "medical_knowledge"

    # Get collection info
    print("📊 Collection Statistics:")
    try:
        collection_info = client.get_collection(collection)
        total_points = collection_info.points_count
        print(f"   Total vectors: {total_points:,}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return 1

    # Sample random points to analyze content
    print(f"\n📥 Sampling {min(100, total_points)} random points...")

    sample_size = min(100, total_points)
    samples = client.scroll(
        collection_name=collection,
        limit=sample_size,
        with_payload=True,
        with_vectors=False
    )[0]

    print(f"   Retrieved {len(samples)} samples\n")

    # Analyze metadata
    source_types = defaultdict(int)
    years = defaultdict(int)
    titles_with_keywords = defaultdict(int)

    australian_keywords = [
        'therapeutic guidelines', 'etg', 'ranzcp', 'nsw health',
        'australian', 'talley', "o'connor", 'mims', 'amh', 'tga'
    ]

    for sample in samples:
        payload = sample.payload

        # Source type
        source_type = payload.get('source_type', 'unknown')
        source_types[source_type] += 1

        # Year
        year = payload.get('year', 'Unknown')
        years[str(year)[:4]] += 1

        # Title analysis
        title = payload.get('title', '').lower()

        # Check for Australian keywords
        for keyword in australian_keywords:
            if keyword in title:
                titles_with_keywords[keyword] += 1

    # Display results
    print("="*70)
    print("📈 CONTENT ANALYSIS RESULTS")
    print("="*70)

    print(f"\n**Source Type Distribution:**")
    total_sampled = len(samples)
    for source_type, count in sorted(source_types.items(), key=lambda x: x[1], reverse=True):
        pct = count / total_sampled * 100
        print(f"   {source_type:20s}: {count:3d} ({pct:5.1f}%)")

    print(f"\n**Year Distribution (Top 10):**")
    for year, count in sorted(years.items(), key=lambda x: x[1], reverse=True)[:10]:
        pct = count / total_sampled * 100
        print(f"   {year:10s}: {count:3d} ({pct:5.1f}%)")

    print(f"\n**Australian Source Detection:**")
    australian_total = sum(titles_with_keywords.values())
    australian_pct = australian_total / total_sampled * 100 if total_sampled > 0 else 0

    print(f"   Samples with Australian keywords: {australian_total}/{total_sampled} ({australian_pct:.1f}%)")

    if titles_with_keywords:
        print(f"\n   **Keyword Breakdown:**")
        for keyword, count in sorted(titles_with_keywords.items(), key=lambda x: x[1], reverse=True):
            print(f"      '{keyword}': {count} occurrences")
    else:
        print(f"   ⚠️  NO AUSTRALIAN KEYWORDS FOUND IN SAMPLE")

    # Show sample titles
    print(f"\n**Sample Titles (first 10):**")
    for i, sample in enumerate(samples[:10], 1):
        title = sample.payload.get('title', 'Unknown')[:60]
        source = sample.payload.get('source_type', 'unknown')
        year = sample.payload.get('year', 'N/A')
        print(f"   {i:2d}. [{source:10s}] {title}... ({year})")

    # Critical analysis
    print("\n" + "="*70)
    print("💡 CRITICAL FINDINGS")
    print("="*70)

    if australian_pct < 10:
        print(f"\n❌ **PROBLEM IDENTIFIED: LOW AUSTRALIAN CONTENT**")
        print(f"   Only {australian_pct:.1f}% of sampled content has Australian keywords")
        print(f"   This explains why queries for 'eTG', 'RANZCP', 'Talley' return low scores")
        print(f"\n   **Impact on Tier 1 Rate:**")
        print(f"   - Queries specifically for Australian guidelines get poor matches")
        print(f"   - Semantic scores stuck at 0.76-0.79 (generic medical content)")
        print(f"   - Cannot reach 0.90+ threshold without Australian sources")
    else:
        print(f"\n✅ **ADEQUATE AUSTRALIAN CONTENT**")
        print(f"   {australian_pct:.1f}% of content has Australian keywords")

    if 'guideline' in source_types:
        guideline_pct = source_types['guideline'] / total_sampled * 100
        print(f"\n   Guidelines: {source_types['guideline']} ({guideline_pct:.1f}%)")
    else:
        print(f"\n   ⚠️  NO 'guideline' source_type found in sample")

    if source_types.get('unknown', 0) > total_sampled * 0.5:
        print(f"\n⚠️  **METADATA ISSUE**")
        print(f"   {source_types['unknown']} samples ({source_types['unknown']/total_sampled*100:.1f}%) have unknown source_type")
        print(f"   This prevents Australian source boost from working")

    # Recommendations
    print("\n" + "="*70)
    print("💡 RECOMMENDATIONS")
    print("="*70)

    if australian_pct < 10:
        print(f"\n**OPTION 1: Add Australian Guidelines to RAG Database**")
        print(f"   Priority sources to index:")
        print(f"   - Therapeutic Guidelines (eTG) - Psychiatry, Emergency, etc.")
        print(f"   - RANZCP Clinical Practice Guidelines")
        print(f"   - Talley & O'Connor Clinical Examination (8th ed)")
        print(f"   - NSW Health Mental Health Act 2007 documentation")
        print(f"   - Australian Medicines Handbook (AMH)")
        print(f"\n   Expected Impact: Semantic scores → 0.85-0.95, Tier 1 rate → 80-90%")
        print(f"   Effort: HIGH (2-3 days to download, process, index)")

    print(f"\n**OPTION 2: Accept Current Limitations, Use LLM Verifier**")
    print(f"   Current Tier 2 (58 MCQs) require LLM verification")
    print(f"   Implement QA-004 LLM Verifier (80 LOC, 1 day)")
    print(f"   Process Tier 2 with Claude (~10 seconds per MCQ = 10 minutes total)")
    print(f"\n   Expected Impact: 100% of MCQs validated (Tier 1 auto + Tier 2 LLM)")
    print(f"   Effort: LOW (1 day implementation)")

    print(f"\n**OPTION 3: Lower Tier 1 Threshold to 0.80**")
    print(f"   Current: Tier 1 ≥0.90 (0% of MCQs)")
    print(f"   Proposed: Tier 1 ≥0.80 (likely 60-70% of MCQs)")
    print(f"   Tier 2: 0.70-0.80 (likely 25-35%)")
    print(f"   Tier 3: <0.70 (likely 5-10%)")
    print(f"\n   Expected Impact: High auto-approval without changing database")
    print(f"   Risk: Lower quality threshold, some false positives")

    print(f"\n**RECOMMENDED APPROACH: Hybrid**")
    print(f"   1. Implement QA-004 LLM Verifier (Day 1-2) - IMMEDIATE")
    print(f"   2. Process current Tier 2 MCQs (Day 2)")
    print(f"   3. Add Australian guidelines to RAG (Week 3-4) - LONG-TERM")
    print(f"   4. Re-validate all content with improved database")

    print("\n" + "="*70)
    print("✅ INSPECTION COMPLETE")
    print("="*70)
    print(f"\n🎯 Next Action: {'Implement LLM Verifier (QA-004)' if australian_pct < 10 else 'Optimize query templates'}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
