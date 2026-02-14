#!/usr/bin/env python3
"""
Process Tier 2 MCQs with QA-004 LLM Verifier
Week 2 Day 2 - LLM Verification of 58 Tier 2 MCQs

Input: 100 MCQs + QA-003 validation results
Process: LLM verify all Tier 2 MCQs (0.75-0.90 confidence)
Output: Complete validation report with LLM verification
"""

import json
import sys
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.agents.qa.qa_004_llm_verifier import LLMCitationVerifier


def load_mcqs(file_path: Path) -> list:
    """Load MCQs from JSON file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data.get('mcqs', [])


def load_rag_validations(file_path: Path) -> list:
    """Load QA-003 RAG validation results"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data.get('detailed_validations', [])


def main():
    """Main processing execution"""
    print("\n" + "="*70)
    print("🤖 QA-004 LLM VERIFICATION - PROCESSING TIER 2 MCQs")
    print("="*70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Target: 58 Tier 2 MCQs (confidence 0.75-0.90)")
    print("="*70 + "\n")

    # Load MCQs
    print("📥 Loading MCQs...")
    mcq_files = [
        project_root / "data/mcqs/psychiatry_depression_day1.json",
        project_root / "data/mcqs/psychiatry_anxiety_bipolar_day2.json",
        project_root / "data/mcqs/psychiatry_psychosis_day3.json",
        project_root / "data/mcqs/psychiatry_suicide_mha_day4.json",
        project_root / "data/mcqs/psychiatry_final_day5.json",
    ]

    all_mcqs = []
    for file_path in mcq_files:
        if file_path.exists():
            mcqs = load_mcqs(file_path)
            all_mcqs.extend(mcqs)
            print(f"  ✅ Loaded {len(mcqs)} MCQs from {file_path.name}")

    print(f"\n📊 Total MCQs loaded: {len(all_mcqs)}\n")

    # Load RAG validations
    print("📥 Loading QA-003 RAG validation results...")
    rag_report_path = project_root / "planning/jan-22-plan/qa_003_week1_final_report.json"

    if not rag_report_path.exists():
        print(f"❌ RAG validation report not found: {rag_report_path}")
        return 1

    rag_validations = load_rag_validations(rag_report_path)
    print(f"✅ Loaded {len(rag_validations)} RAG validation results\n")

    # Initialize LLM verifier
    print("🔧 Initializing QA-004 LLM Verifier...")
    print("⚠️  NOTE: Currently using MOCK LLM responses for testing")
    print("   Production: Replace _call_llm() with actual Claude API\n")

    verifier = LLMCitationVerifier()

    # Count Tier 2 MCQs
    tier2_count = sum(1 for v in rag_validations if v.get('overall_tier') == 2)
    print(f"🎯 Target: {tier2_count} Tier 2 MCQs will be processed\n")

    # Process batch
    print("🔍 Processing MCQs with LLM verifier...")
    print("-" * 70)

    results = verifier.verify_batch(all_mcqs, rag_validations)

    # Display results
    print("\n" + "="*70)
    print("📊 LLM VERIFICATION RESULTS")
    print("="*70)

    print(f"\n**Overall Metrics:**")
    print(f"  Total MCQs Processed: {results['total_mcqs']}")
    print(f"  Tier 2 MCQs (requiring LLM verification): {results['tier2_count']}")
    print(f"  LLM Verified (approved): {results['verified_count']}")
    print(f"  LLM Rejected: {results['rejected_count']}")
    print(f"  LLM Approval Rate: {results['approval_rate']:.1%}")
    print(f"  Average LLM Confidence: {results['avg_llm_confidence']:.3f}")

    # Combined validation coverage
    tier1_count = sum(1 for v in rag_validations if v.get('overall_tier') == 1)
    tier3_count = sum(1 for v in rag_validations if v.get('overall_tier') == 3)

    total_validated = tier1_count + results['verified_count']
    total_coverage = total_validated / results['total_mcqs'] * 100

    print(f"\n**Combined Validation Coverage:**")
    print(f"  Tier 1 (RAG auto-approved): {tier1_count} MCQs")
    print(f"  Tier 2 (LLM verified): {results['verified_count']} MCQs")
    print(f"  Total Validated: {total_validated}/{results['total_mcqs']} ({total_coverage:.1f}%)")
    print(f"  Tier 3 (rejected): {tier3_count} MCQs")

    # Sample verifications
    tier2_verifications = [v for v in results['verifications'] if v.get('tier') == 2]

    print(f"\n**Sample LLM Verifications (first 5 Tier 2 MCQs):**")
    for i, verification in enumerate(tier2_verifications[:5], 1):
        mcq_id = verification['mcq_id']
        rag_conf = verification['rag_confidence']
        llm_verified = verification['llm_verified']
        llm_conf = verification.get('llm_confidence', 0)
        rec = verification['final_recommendation']

        status = "✅" if llm_verified else "❌"
        print(f"\n  {status} MCQ #{i} ({mcq_id})")
        print(f"      RAG Confidence: {rag_conf:.3f}")
        print(f"      LLM Confidence: {llm_conf:.3f}")
        print(f"      Recommendation: {rec.upper()}")

    # Analysis
    print("\n" + "="*70)
    print("📈 ANALYSIS & IMPACT")
    print("="*70)

    print(f"\n**Week 1 Baseline (RAG only):**")
    print(f"  - Tier 1 auto-approved: 0% (0 MCQs)")
    print(f"  - Tier 2 pending: 58% (58 MCQs)")
    print(f"  - Tier 3 rejected: 42% (42 MCQs)")
    print(f"  - **Validation coverage: 0%**")

    print(f"\n**Week 2 with LLM Verifier:**")
    print(f"  - Tier 1 auto-approved: 0% (0 MCQs)")
    print(f"  - Tier 2 LLM verified: {results['verified_count']/results['total_mcqs']*100:.1f}% ({results['verified_count']} MCQs)")
    print(f"  - Tier 2 LLM rejected: {results['rejected_count']/results['total_mcqs']*100:.1f}% ({results['rejected_count']} MCQs)")
    print(f"  - Tier 3 rejected: {tier3_count/results['total_mcqs']*100:.1f}% ({tier3_count} MCQs)")
    print(f"  - **Validation coverage: {total_coverage:.1f}%** ⬆️ +{total_coverage:.1f}%")

    print(f"\n**Impact:**")
    improvement = total_coverage - 0
    print(f"  ✅ Validation coverage increased by {improvement:.1f}% (0% → {total_coverage:.1f}%)")
    print(f"  ✅ {results['verified_count']} additional MCQs approved via LLM verification")

    if results['approval_rate'] >= 0.90:
        print(f"  ✅ High LLM approval rate ({results['approval_rate']:.1%}) - citations generally good quality")
    elif results['approval_rate'] >= 0.75:
        print(f"  🟡 Moderate LLM approval rate ({results['approval_rate']:.1%}) - some citations need improvement")
    else:
        print(f"  ⚠️  Low LLM approval rate ({results['approval_rate']:.1%}) - many citations problematic")

    # Save results
    output_file = project_root / "planning/jan-22-plan/qa_004_llm_verification_report.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'metadata': {
                'verification_date': datetime.now().isoformat(),
                'verifier_version': 'QA-004 Week 2 Day 2',
                'total_mcqs': results['total_mcqs'],
                'tier2_count': results['tier2_count'],
                'note': 'Using MOCK LLM responses - replace with actual Claude API for production'
            },
            'summary': {
                'total_mcqs': results['total_mcqs'],
                'tier2_count': results['tier2_count'],
                'verified_count': results['verified_count'],
                'rejected_count': results['rejected_count'],
                'approval_rate': results['approval_rate'],
                'avg_llm_confidence': results['avg_llm_confidence'],
                'validation_coverage': total_coverage / 100
            },
            'combined_validation': {
                'tier1_auto': tier1_count,
                'tier2_llm_verified': results['verified_count'],
                'tier2_llm_rejected': results['rejected_count'],
                'tier3_rejected': tier3_count,
                'total_validated': total_validated,
                'validation_coverage_pct': total_coverage
            },
            'detailed_verifications': results['verifications']
        }, f, indent=2)

    print(f"\n💾 Verification report saved: {output_file}")

    # Recommendations
    print("\n" + "="*70)
    print("💡 RECOMMENDATIONS")
    print("="*70)

    print(f"\n**Immediate Actions:**")
    print(f"  1. ⚠️  Replace _call_llm() with actual Claude API integration")
    print(f"  2. Re-run verification on 58 Tier 2 MCQs with real LLM")
    print(f"  3. Review {results['rejected_count']} LLM-rejected MCQs (if any)")

    print(f"\n**Week 2 Remaining Tasks:**")
    print(f"  1. Address {tier3_count} Tier 3 MCQs (regenerate with better citations)")
    print(f"  2. Generate Week 2 final report")
    print(f"  3. Plan Week 3: Add Australian guidelines to RAG database")

    print(f"\n**Long-term (Week 3-4):**")
    print(f"  1. Add eTG, RANZCP, Talley & O'Connor to RAG database")
    print(f"  2. Re-validate all 100 MCQs with improved RAG")
    print(f"  3. Target: 80-90% Tier 1 auto-approval rate")

    print("\n" + "="*70)
    print("✅ QA-004 LLM VERIFICATION COMPLETE")
    print("="*70)
    print(f"\n🎯 Result: {total_coverage:.1f}% validation coverage achieved")
    print(f"📋 Next: Implement actual Claude API integration\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
