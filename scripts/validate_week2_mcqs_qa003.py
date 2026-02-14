#!/usr/bin/env python3
"""
Validate Week 2 MCQs using QA-003 RAG Citation Validator
Week 2 - Psychiatry Day 6 (80 MCQs)
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
    print("🔬 QA-003 RAG CITATION VALIDATOR - WEEK 2 VALIDATION")
    print("="*70)
    print(f"Testing on: Week 2 MCQs")
    print(f"  • Psychiatry Day 6: 80 MCQs")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")

    # Initialize validator
    print("🔧 Initializing QA-003 RAG Citation Validator...")
    validator = RAGCitationValidator()
    print("✅ Validator initialized\n")

    # Load Week 2 MCQ file
    week2_file = project_root / "data/mcqs/week2_day6_psychiatry_80_mcqs.json"

    print("📂 Loading MCQ file...\n")
    if week2_file.exists():
        mcqs = load_mcqs(week2_file)
        print(f"✅ Loaded: {len(mcqs)} MCQs from {week2_file.name}")
    else:
        print(f"❌ File not found: {week2_file}")
        return 1

    print(f"\n📊 Total MCQs loaded: {len(mcqs)}")
    print("="*70 + "\n")

    if not mcqs:
        print("❌ No MCQs found to validate!")
        return 1

    # Validate all MCQs
    print("🔍 Running QA-003 validation on all MCQs...\n")
    results = validator.validate_batch(mcqs)

    # Print detailed results
    print("\n" + "="*70)
    print("📊 VALIDATION RESULTS")
    print("="*70 + "\n")

    # Overall statistics
    print(f"**Overall Metrics:**")
    print(f"  Total MCQs Validated: {results['total_mcqs']}")
    print(f"  Average Confidence: {results['average_confidence']:.3f}")
    print(f"  Auto-Approval Rate: {results['auto_approval_rate']:.1%} (Tier 1)")
    print()

    # Tier distribution
    print(f"**Tier Distribution:**")
    print(f"  Tier 1 (>0.90 - Auto-Approve): {results['tier1_count']} MCQs ({results['tier1_count']/results['total_mcqs']:.1%})")
    print(f"  Tier 2 (0.75-0.90 - LLM Verify): {results['tier2_count']} MCQs ({results['tier2_count']/results['total_mcqs']:.1%})")
    print(f"  Tier 3 (<0.75 - Reject): {results['tier3_count']} MCQs ({results['tier3_count']/results['total_mcqs']:.1%})")
    print()

    # Metadata validation (Phase 3 Enhancement)
    print(f"**Metadata Validation (Phase 3 Enhancement):**")
    validations = results['validations']
    metadata_issues_count = 0
    metadata_warnings_count = 0
    metadata_valid_count = 0
    missing_author_count = 0
    unknown_title_count = 0

    for v in validations:
        for citation in v.get('citations', []):
            metadata_val = citation.get('metadata_validation', {})
            if metadata_val.get('valid'):
                metadata_valid_count += 1
            if metadata_val.get('issues'):
                metadata_issues_count += 1
                # Count specific issues
                for issue in metadata_val.get('issues', []):
                    if 'author' in issue.lower():
                        missing_author_count += 1
                    if 'title' in issue.lower() and 'unknown' in issue.lower():
                        unknown_title_count += 1
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
        print()

        # Specific issue breakdown
        if metadata_issues_count > 0:
            print(f"  ⚠️  Critical Issue Breakdown:")
            if missing_author_count > 0:
                print(f"     • Missing author field: {missing_author_count} citations")
            if unknown_title_count > 0:
                print(f"     • Title=\"Unknown\": {unknown_title_count} citations")
            print()

        if metadata_issues_count > 0:
            print(f"  ❌ Week 2 has citation metadata issues!")
            print(f"     Recommendation: Regenerate Week 2 with RAG validation")
        elif valid_pct == 100.0:
            print(f"  ✅ ALL citations have complete metadata")
        print()

    # Citations per MCQ analysis
    print(f"**Citations per MCQ Analysis:**")
    citations_per_mcq = {}
    for v in validations:
        count = v.get('citation_count', 0)
        citations_per_mcq[count] = citations_per_mcq.get(count, 0) + 1

    for count in sorted(citations_per_mcq.keys()):
        mcq_count = citations_per_mcq[count]
        print(f"  {count} citations/MCQ: {mcq_count} MCQs ({mcq_count/results['total_mcqs']:.1%})")

    if 2 in citations_per_mcq or 1 in citations_per_mcq:
        print(f"\n  ⚠️  WARNING: Some MCQs have <3 citations!")
        print(f"     Standard requirement: 3 citations per MCQ (Constraint 11)")

    print("\n" + "="*70)

    # Save detailed results
    report_path = project_root / "planning/jan-22-plan/qa_003_week2_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump({
            'validation_date': datetime.now().isoformat(),
            'week': 'Week 2',
            'file': str(week2_file),
            'results': results,
            'summary': {
                'total_mcqs': results['total_mcqs'],
                'total_citations': total_citations,
                'valid_citations': metadata_valid_count,
                'citations_with_issues': metadata_issues_count,
                'citations_with_warnings': metadata_warnings_count,
                'validity_rate': valid_pct if total_citations > 0 else 0,
                'tier_distribution': {
                    'tier1': results['tier1_count'],
                    'tier2': results['tier2_count'],
                    'tier3': results['tier3_count']
                },
                'average_confidence': results['average_confidence'],
                'missing_author_count': missing_author_count,
                'unknown_title_count': unknown_title_count,
                'citations_per_mcq': citations_per_mcq
            }
        }, f, indent=2)

    print(f"\n📄 Detailed report saved to: {report_path}")

    # Return exit code
    if metadata_issues_count > 0 or results['tier3_count'] > 0:
        print("\n❌ VALIDATION FAILED - Issues found")
        print("\n📋 RECOMMENDATION: Regenerate Week 2 with validated RAG citations")
        return 1
    else:
        print("\n✅ VALIDATION PASSED - All citations valid with complete metadata")
        return 0


if __name__ == "__main__":
    sys.exit(main())
