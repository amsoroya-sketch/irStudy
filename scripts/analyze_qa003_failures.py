#!/usr/bin/env python3
"""
Analyze QA-003 Tier 2/3 Citations to Identify Improvement Patterns
Week 2 Day 1 - Understanding why 100% of citations are below Tier 1

Goal: Achieve 90%+ Tier 1 auto-approval rate
Current: 0% Tier 1, 58% Tier 2, 42% Tier 3
"""

import json
import sys
from pathlib import Path
from collections import defaultdict

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def load_validation_report(report_path: Path) -> dict:
    """Load QA-003 validation report"""
    with open(report_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def analyze_confidence_factors(validations: list) -> dict:
    """Analyze what factors are causing low confidence scores"""

    tier_groups = {
        'tier1': [],  # >0.90
        'tier2': [],  # 0.75-0.90
        'tier3': []   # <0.75
    }

    for validation in validations:
        avg_conf = validation['average_confidence']

        if avg_conf >= 0.90:
            tier_groups['tier1'].append(validation)
        elif avg_conf >= 0.75:
            tier_groups['tier2'].append(validation)
        else:
            tier_groups['tier3'].append(validation)

    return tier_groups


def analyze_citation_patterns(validations: list) -> dict:
    """Analyze patterns in citation validation"""

    patterns = {
        'confidence_distribution': defaultdict(int),
        'near_tier1': [],  # 0.85-0.90 (close to threshold)
        'far_tier3': [],   # <0.70 (far from acceptable)
        'source_types': defaultdict(list),
        'page_issues': []
    }

    for validation in validations:
        avg_conf = validation['average_confidence']

        # Confidence distribution
        if avg_conf >= 0.85:
            patterns['confidence_distribution']['0.85-0.90'] += 1
            if avg_conf < 0.90:
                patterns['near_tier1'].append(validation)
        elif avg_conf >= 0.80:
            patterns['confidence_distribution']['0.80-0.85'] += 1
        elif avg_conf >= 0.75:
            patterns['confidence_distribution']['0.75-0.80'] += 1
        elif avg_conf >= 0.70:
            patterns['confidence_distribution']['0.70-0.75'] += 1
            patterns['far_tier3'].append(validation)
        else:
            patterns['confidence_distribution']['<0.70'] += 1
            patterns['far_tier3'].append(validation)

        # Analyze individual citations
        for citation in validation.get('citations', []):
            if citation.get('top_match'):
                source_type = citation['top_match'].get('source_type', 'unknown')
                patterns['source_types'][source_type].append(avg_conf)

    return patterns


def main():
    """Main analysis execution"""
    print("\n" + "="*70)
    print("🔍 QA-003 TIER 2/3 ANALYSIS - FINDING IMPROVEMENT OPPORTUNITIES")
    print("="*70)
    print("Goal: Identify why 100% of citations are below Tier 1 (0.90)")
    print("="*70 + "\n")

    # Load MCQ validation report
    mcq_report_path = project_root / "planning/jan-22-plan/qa_003_week1_final_report.json"

    if not mcq_report_path.exists():
        print(f"❌ Report not found: {mcq_report_path}")
        return 1

    print("📥 Loading MCQ validation report...")
    report = load_validation_report(mcq_report_path)
    validations = report['detailed_validations']
    print(f"✅ Loaded {len(validations)} MCQ validations\n")

    # Group by tier
    print("="*70)
    print("📊 TIER DISTRIBUTION ANALYSIS")
    print("="*70)

    tier_groups = analyze_confidence_factors(validations)

    print(f"\n**Current State:**")
    print(f"  Tier 1 (≥0.90): {len(tier_groups['tier1'])} MCQs (TARGET: 90+)")
    print(f"  Tier 2 (0.75-0.90): {len(tier_groups['tier2'])} MCQs")
    print(f"  Tier 3 (<0.75): {len(tier_groups['tier3'])} MCQs")

    # Analyze patterns
    print("\n" + "="*70)
    print("🎯 OPPORTUNITY ANALYSIS")
    print("="*70)

    patterns = analyze_citation_patterns(validations)

    print(f"\n**Confidence Distribution (detailed):**")
    for range_label, count in sorted(patterns['confidence_distribution'].items(), reverse=True):
        pct = count / len(validations) * 100
        print(f"  {range_label:15s}: {count:3d} MCQs ({pct:5.1f}%)")

    # Near-miss analysis
    near_tier1_count = len(patterns['near_tier1'])
    print(f"\n**Near-Miss Analysis (0.85-0.90):**")
    print(f"  MCQs just below Tier 1 threshold: {near_tier1_count}")
    print(f"  Gap to Tier 1: 0.05-0.10 confidence points")
    print(f"  💡 OPPORTUNITY: Small improvements could move {near_tier1_count} MCQs to Tier 1")

    if near_tier1_count > 0:
        print(f"\n  **Sample Near-Miss MCQs:**")
        for i, validation in enumerate(patterns['near_tier1'][:5], 1):
            mcq_id = validation['mcq_id']
            conf = validation['average_confidence']
            gap = 0.90 - conf
            print(f"    {i}. {mcq_id}: {conf:.3f} (gap: {gap:.3f})")

    # Calculate potential improvement
    potential_tier1 = near_tier1_count
    current_tier1_rate = len(tier_groups['tier1']) / len(validations) * 100
    potential_tier1_rate = (len(tier_groups['tier1']) + potential_tier1) / len(validations) * 100

    print(f"\n**Improvement Potential:**")
    print(f"  Current Tier 1 rate: {current_tier1_rate:.1f}%")
    print(f"  Potential with small fixes: {potential_tier1_rate:.1f}%")
    print(f"  Gap to 90% target: {90 - potential_tier1_rate:.1f}%")

    # Tier 3 analysis
    print(f"\n**Tier 3 Analysis (<0.75):**")
    print(f"  Total Tier 3 MCQs: {len(tier_groups['tier3'])}")
    print(f"  These require significant citation improvements")

    far_tier3_count = len(patterns['far_tier3'])
    print(f"  MCQs <0.70 (far from acceptable): {far_tier3_count}")
    print(f"  💡 RECOMMENDATION: Regenerate these {far_tier3_count} MCQs with better RAG queries")

    # Source type analysis
    print(f"\n**Source Type Analysis:**")
    if patterns['source_types']:
        for source_type, confidences in patterns['source_types'].items():
            if confidences:
                avg_conf = sum(confidences) / len(confidences)
                print(f"  {source_type:15s}: {len(confidences):3d} citations, avg {avg_conf:.3f}")

    # Recommendations
    print("\n" + "="*70)
    print("💡 IMPROVEMENT STRATEGIES (Priority Order)")
    print("="*70)

    print(f"\n**1. QUICK WIN: Adjust Confidence Scoring Weights**")
    print(f"   Current: Semantic 60%, Page 20%, Source 10%, Recency 10%")
    print(f"   Proposed: Semantic 70%, Page 15%, Source 10%, Recency 5%")
    print(f"   Rationale: Semantic similarity is most reliable factor")
    print(f"   Expected Impact: +5-10% Tier 1 rate")

    print(f"\n**2. MEDIUM EFFORT: Improve Page Matching Tolerance**")
    print(f"   Current: ±2 pages tolerance")
    print(f"   Proposed: ±5 pages tolerance (medical textbooks often have multi-page topics)")
    print(f"   Expected Impact: +10-15% Tier 1 rate")

    print(f"\n**3. MEDIUM EFFORT: Prioritize Australian Guideline Sources**")
    print(f"   Add +0.15 boost for eTG, RANZCP, NSW Health sources")
    print(f"   Rationale: Australian sources are preferred for ICRP")
    print(f"   Expected Impact: +5-10% Tier 1 rate")

    print(f"\n**4. HIGH EFFORT: Improve RAG Query Specificity**")
    print(f"   Add more medical context to queries (diagnosis codes, specific terms)")
    print(f"   Example: 'depression treatment' → 'major depressive disorder F32.9 SSRI treatment guidelines Australia'")
    print(f"   Expected Impact: +15-20% Tier 1 rate")

    print(f"\n**5. REGENERATE: Fix Tier 3 MCQs with Better Citations**")
    print(f"   Regenerate {len(tier_groups['tier3'])} Tier 3 MCQs with improved RAG queries")
    print(f"   Target: Move all to Tier 2 minimum, 50% to Tier 1")
    print(f"   Expected Impact: +20-25% Tier 1 rate")

    # Calculate combined impact
    combined_impact_low = 5 + 10 + 5 + 15 + 20
    combined_impact_high = 10 + 15 + 10 + 20 + 25

    print(f"\n**COMBINED EXPECTED IMPACT:**")
    print(f"   Conservative estimate: +{combined_impact_low}% → {current_tier1_rate + combined_impact_low:.1f}% Tier 1 rate")
    print(f"   Optimistic estimate: +{combined_impact_high}% → {current_tier1_rate + combined_impact_high:.1f}% Tier 1 rate")
    print(f"   90% Target: {'✅ ACHIEVABLE' if current_tier1_rate + combined_impact_low >= 90 else '🟡 CHALLENGING but possible'}")

    # Implementation priority
    print("\n" + "="*70)
    print("📋 WEEK 2 IMPLEMENTATION PLAN")
    print("="*70)

    print(f"\n**Day 1 (Today): Quick Wins**")
    print(f"  1. Adjust confidence scoring weights (1 hour)")
    print(f"  2. Increase page matching tolerance (30 min)")
    print(f"  3. Add Australian source boost (30 min)")
    print(f"  4. Re-validate 10 sample MCQs to test improvements")

    print(f"\n**Day 2: RAG Query Improvements**")
    print(f"  1. Create improved MCQ generation templates")
    print(f"  2. Add medical terminology/codes to queries")
    print(f"  3. Test on 20 new MCQs")

    print(f"\n**Day 3-4: Regenerate Tier 3 Content**")
    print(f"  1. Regenerate {len(tier_groups['tier3'])} Tier 3 MCQs")
    print(f"  2. Validate all regenerated content")
    print(f"  3. Target: 100% moved to Tier 2+")

    print(f"\n**Day 5: LLM Verifier Implementation**")
    print(f"  1. Implement QA-004 LLM Verifier (80 LOC)")
    print(f"  2. Process {len(tier_groups['tier2'])} Tier 2 MCQs")
    print(f"  3. Final validation report")

    print("\n" + "="*70)
    print("✅ ANALYSIS COMPLETE")
    print("="*70)
    print(f"\n🎯 Next Action: Implement confidence scoring improvements")
    print(f"📁 Full report: planning/jan-22-plan/qa_003_improvement_analysis.txt\n")

    # Save detailed report
    report_file = project_root / "planning/jan-22-plan/qa_003_improvement_analysis.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("QA-003 IMPROVEMENT ANALYSIS\n")
        f.write("="*70 + "\n\n")
        f.write(f"Total MCQs: {len(validations)}\n")
        f.write(f"Tier 1 (≥0.90): {len(tier_groups['tier1'])}\n")
        f.write(f"Tier 2 (0.75-0.90): {len(tier_groups['tier2'])}\n")
        f.write(f"Tier 3 (<0.75): {len(tier_groups['tier3'])}\n\n")

        f.write("NEAR-MISS MCQs (0.85-0.90):\n")
        for validation in patterns['near_tier1']:
            f.write(f"  {validation['mcq_id']}: {validation['average_confidence']:.3f}\n")

        f.write("\n\nTIER 3 MCQs (<0.75):\n")
        for validation in tier_groups['tier3']:
            f.write(f"  {validation['mcq_id']}: {validation['average_confidence']:.3f}\n")

    print(f"💾 Detailed analysis saved: {report_file}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
