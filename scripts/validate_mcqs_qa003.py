#!/usr/bin/env python3
"""
Validate all generated MCQs using QA-003 RAG Citation Validator
Week 1 Day 4 Afternoon - Initial QA-003 implementation test
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.agents.qa.qa_003_rag_validator import RAGCitationValidator


def load_mcqs(file_path: Path) -> list:
    """Load MCQs from JSON file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data.get('mcqs', [])


def main():
    """Main validation execution"""
    print("\n" + "="*70)
    print("🔬 QA-003 RAG CITATION VALIDATOR - WEEK 1 COMPLETE VALIDATION")
    print("="*70)
    print(f"Testing on: Days 1-5 MCQs (100 total)")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")

    # Initialize validator
    print("🔧 Initializing QA-003 RAG Citation Validator...")
    validator = RAGCitationValidator()
    print("✅ Validator initialized\n")

    # Load all MCQ files
    mcq_files = [
        ("Day 1: Depression", project_root / "data/mcqs/psychiatry_depression_day1.json"),
        ("Day 2: Anxiety/Bipolar", project_root / "data/mcqs/psychiatry_anxiety_bipolar_day2.json"),
        ("Day 3: Psychosis", project_root / "data/mcqs/psychiatry_psychosis_day3.json"),
        ("Day 4: Suicide/MHA", project_root / "data/mcqs/psychiatry_suicide_mha_day4.json"),
        ("Day 5: Final Topics", project_root / "data/mcqs/psychiatry_final_day5.json"),
    ]

    all_mcqs = []
    file_summaries = []

    print("📥 Loading MCQ files...")
    for label, file_path in mcq_files:
        if file_path.exists():
            mcqs = load_mcqs(file_path)
            all_mcqs.extend(mcqs)
            print(f"  ✅ {label}: {len(mcqs)} MCQs loaded")
        else:
            print(f"  ⚠️  {label}: File not found - {file_path}")

    print(f"\n📊 Total MCQs loaded: {len(all_mcqs)}\n")

    # Validate all MCQs
    print("🔍 Validating all MCQs...")
    print("-" * 70)

    overall_results = validator.validate_batch(all_mcqs)

    # Display results
    print("\n" + "="*70)
    print("📊 VALIDATION RESULTS")
    print("="*70)

    print(f"\n**Overall Metrics:**")
    print(f"  Total MCQs Validated: {overall_results['total_mcqs']}")
    print(f"  Average Confidence: {overall_results['average_confidence']:.3f}")
    print(f"  Auto-Approval Rate: {overall_results['auto_approval_rate']:.1%} (Tier 1)")

    print(f"\n**Tier Distribution:**")
    print(f"  Tier 1 (>0.90 - Auto-Approve): {overall_results['tier1_count']} MCQs ({overall_results['tier1_count']/overall_results['total_mcqs']:.1%})")
    print(f"  Tier 2 (0.75-0.90 - LLM Verify): {overall_results['tier2_count']} MCQs ({overall_results['tier2_count']/overall_results['total_mcqs']:.1%})")
    print(f"  Tier 3 (<0.75 - Reject): {overall_results['tier3_count']} MCQs ({overall_results['tier3_count']/overall_results['total_mcqs']:.1%})")

    # Detailed tier breakdown
    print(f"\n**Confidence Score Distribution:**")
    validations = overall_results['validations']
    confidence_ranges = {
        '0.90-1.00': 0,
        '0.85-0.90': 0,
        '0.80-0.85': 0,
        '0.75-0.80': 0,
        '0.70-0.75': 0,
        '0.65-0.70': 0,
        '<0.65': 0
    }

    for v in validations:
        conf = v['average_confidence']
        if conf >= 0.90:
            confidence_ranges['0.90-1.00'] += 1
        elif conf >= 0.85:
            confidence_ranges['0.85-0.90'] += 1
        elif conf >= 0.80:
            confidence_ranges['0.80-0.85'] += 1
        elif conf >= 0.75:
            confidence_ranges['0.75-0.80'] += 1
        elif conf >= 0.70:
            confidence_ranges['0.70-0.75'] += 1
        elif conf >= 0.65:
            confidence_ranges['0.65-0.70'] += 1
        else:
            confidence_ranges['<0.65'] += 1

    for range_label, count in confidence_ranges.items():
        pct = count / overall_results['total_mcqs'] * 100 if overall_results['total_mcqs'] > 0 else 0
        print(f"  {range_label}: {count} MCQs ({pct:.1f}%)")

    # PHASE 3 ENHANCEMENT: Metadata validation statistics
    print(f"\n**Metadata Validation (Phase 3 Enhancement):**")
    metadata_issues_count = 0
    metadata_warnings_count = 0
    metadata_valid_count = 0

    for v in validations:
        for citation in v.get('citations', []):
            metadata_val = citation.get('metadata_validation', {})
            if metadata_val.get('valid'):
                metadata_valid_count += 1
            if metadata_val.get('issues'):
                metadata_issues_count += 1
            if metadata_val.get('warnings'):
                metadata_warnings_count += 1

    total_citations = sum(v.get('citation_count', 0) for v in validations)
    if total_citations > 0:
        valid_pct = (metadata_valid_count / total_citations) * 100
        issues_pct = (metadata_issues_count / total_citations) * 100
        warnings_pct = (metadata_warnings_count / total_citations) * 100

        print(f"  Valid Citations (complete metadata): {metadata_valid_count}/{total_citations} ({valid_pct:.1f}%)")
        print(f"  Citations with Critical Issues: {metadata_issues_count}/{total_citations} ({issues_pct:.1f}%)")
        print(f"  Citations with Warnings: {metadata_warnings_count}/{total_citations} ({warnings_pct:.1f}%)")

        if metadata_issues_count > 0:
            print(f"\n  ⚠️  WARNING: {metadata_issues_count} citations have critical metadata issues!")
            print(f"     This indicates RAG database corruption (Week 1 mistake)")
            print(f"     Run: ./scripts/pre_flight_validation.sh")
        elif valid_pct == 100.0:
            print(f"\n  ✅ ALL citations have complete metadata (Week 1 mistake prevented!)")

    # Show sample validations
    print(f"\n**Sample Validations (first 5 MCQs):**")
    for i, validation in enumerate(validations[:5], 1):
        print(f"\n  MCQ #{i} ({validation['mcq_id']})")
        print(f"    Confidence: {validation['average_confidence']:.3f}")
        print(f"    Tier: {validation['overall_tier']}")
        print(f"    Recommendation: {validation['recommendation'].upper()}")
        if validation['citations']:
            top_citation = validation['citations'][0]
            if top_citation.get('top_match'):
                print(f"    Top Match: {top_citation['top_match']['title'][:50]}...")

    # Analysis and recommendations
    print("\n" + "="*70)
    print("📈 ANALYSIS & RECOMMENDATIONS")
    print("="*70)

    tier1_pct = overall_results['tier1_count'] / overall_results['total_mcqs'] * 100
    tier2_pct = overall_results['tier2_count'] / overall_results['total_mcqs'] * 100
    tier3_pct = overall_results['tier3_count'] / overall_results['total_mcqs'] * 100

    print(f"\n**Current State:**")
    print(f"  - {tier1_pct:.1f}% of MCQs in Tier 1 (auto-approve)")
    print(f"  - {tier2_pct:.1f}% of MCQs in Tier 2 (require LLM verification)")
    print(f"  - {tier3_pct:.1f}% of MCQs in Tier 3 (reject)")

    print(f"\n**Week 2 Goals:**")
    print(f"  - Target: 90%+ auto-approval rate (Tier 1)")
    print(f"  - Current: {tier1_pct:.1f}% auto-approval rate")
    print(f"  - Gap: {90 - tier1_pct:.1f}% improvement needed")

    if tier1_pct < 90:
        print(f"\n**Improvement Strategies:**")
        print(f"  1. Refine RAG queries to be more specific")
        print(f"  2. Improve page number matching tolerance")
        print(f"  3. Prioritize Australian guideline sources (eTG, RANZCP)")
        print(f"  4. Adjust confidence scoring weights")

    if tier2_pct > 15:
        print(f"\n**Week 2 Priority:**")
        print(f"  - Implement LLM verifier for {overall_results['tier2_count']} Tier 2 MCQs")
        print(f"  - Expected LLM processing time: ~{overall_results['tier2_count'] * 10} seconds")

    if tier3_pct > 5:
        print(f"\n**Action Required:**")
        print(f"  - Regenerate {overall_results['tier3_count']} Tier 3 MCQs with improved citations")

    # Save validation report
    report_file = project_root / "planning/jan-22-plan/qa_003_week1_final_report.json"
    report_file.parent.mkdir(parents=True, exist_ok=True)

    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump({
            'metadata': {
                'validation_date': datetime.now().isoformat(),
                'validator_version': 'QA-003 Week 1 Complete (Days 1-5)',
                'total_mcqs': overall_results['total_mcqs']
            },
            'summary': {
                'total_mcqs': overall_results['total_mcqs'],
                'average_confidence': overall_results['average_confidence'],
                'auto_approval_rate': overall_results['auto_approval_rate'],
                'tier1_count': overall_results['tier1_count'],
                'tier2_count': overall_results['tier2_count'],
                'tier3_count': overall_results['tier3_count']
            },
            'confidence_distribution': confidence_ranges,
            'detailed_validations': overall_results['validations']
        }, f, indent=2)

    print(f"\n💾 Validation report saved: {report_file}")

    print("\n" + "="*70)
    print("✅ QA-003 WEEK 1 VALIDATION COMPLETE")
    print("="*70)
    print(f"\n🎯 Next Steps (Week 2):")
    print(f"  1. Implement LLM verifier for Tier 2 MCQs")
    print(f"  2. Improve RAG query specificity")
    print(f"  3. Achieve 90%+ auto-approval rate")
    print(f"  4. Generate summary reports")
    print("\n✅ Week 1 Day 5 QA Validation Complete! 🎉\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
