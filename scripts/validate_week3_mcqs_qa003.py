#!/usr/bin/env python3
"""
Validate all Week 3 generated MCQs using QA-003 RAG Citation Validator
Week 3 - Cardiology + Respiratory + Psychiatry Additional (500 MCQs total)
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
    print("🔬 QA-003 RAG CITATION VALIDATOR - WEEK 3 COMPLETE VALIDATION")
    print("="*70)
    print(f"Testing on: Week 3 MCQs (500 total)")
    print(f"  • Cardiology: 200 MCQs (600 citations)")
    print(f"  • Respiratory: 200 MCQs (600 citations)")
    print(f"  • Psychiatry Additional: 100 MCQs (300 citations)")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")

    # Initialize validator
    print("🔧 Initializing QA-003 RAG Citation Validator...")
    validator = RAGCitationValidator()
    print("✅ Validator initialized\n")

    # Load all Week 3 MCQ files
    mcq_files = [
        ("Cardiology (200)", project_root / "data/mcqs/week3_cardiology_200_mcqs.json"),
        ("Respiratory (200)", project_root / "data/mcqs/week3_respiratory_200_mcqs.json"),
        ("Psychiatry Additional (100)", project_root / "data/mcqs/week3_psychiatry_additional_100_mcqs.json"),
    ]

    all_mcqs = []
    file_summaries = []

    print("📂 Loading MCQ files...\n")
    for name, filepath in mcq_files:
        if filepath.exists():
            mcqs = load_mcqs(filepath)
            all_mcqs.extend(mcqs)
            print(f"✅ {name}: {len(mcqs)} MCQs loaded from {filepath.name}")
            file_summaries.append({
                'name': name,
                'path': str(filepath),
                'count': len(mcqs)
            })
        else:
            print(f"❌ {name}: File not found - {filepath}")
            file_summaries.append({
                'name': name,
                'path': str(filepath),
                'count': 0,
                'error': 'File not found'
            })

    print(f"\n📊 Total MCQs loaded: {len(all_mcqs)}")
    print("="*70 + "\n")

    if not all_mcqs:
        print("❌ No MCQs found to validate!")
        return 1

    # Validate all MCQs
    print("🔍 Running QA-003 validation on all MCQs...\n")
    results = validator.validate_batch(all_mcqs)

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
        elif valid_pct == 100.0:
            print(f"\n  ✅ ALL citations have complete metadata (Week 1 mistake prevented!)")
        print()

    print("="*70)

    # Save detailed results
    report_path = project_root / "planning/jan-22-plan/qa_003_week3_final_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump({
            'validation_date': datetime.now().isoformat(),
            'week': 'Week 3',
            'files_validated': file_summaries,
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
                'average_confidence': results['average_confidence']
            }
        }, f, indent=2)

    print(f"\n📄 Detailed report saved to: {report_path}")

    # Return exit code
    if metadata_issues_count > 0 or results['tier3_count'] > 0:
        print("\n❌ VALIDATION FAILED - Issues found")
        return 1
    else:
        print("\n✅ VALIDATION PASSED - All citations valid with complete metadata")
        return 0


if __name__ == "__main__":
    sys.exit(main())
