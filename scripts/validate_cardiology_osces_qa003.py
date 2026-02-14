#!/usr/bin/env python3
"""
Validate Cardiology OSCEs using QA-003 RAG Citation Validator
50 Cardiology OSCEs with 150 validated citations and medical images
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.agents.qa.qa_003_rag_validator import RAGCitationValidator


def load_osces(file_path: Path) -> list:
    """Load OSCEs from JSON file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data.get('osces', [])


def convert_osce_to_mcq_format(osce: dict) -> dict:
    """
    Convert OSCE format to MCQ-like format for QA-003 validation

    QA-003 expects 'question' field as dict, so we adapt OSCE structure
    """
    return {
        'id': osce.get('id'),
        'specialty': osce.get('specialty'),
        'topic': osce.get('topic'),
        'subtopic': osce.get('subtopic'),
        'question': {
            'scenario': osce.get('scenario', {}).get('patient_presentation', ''),
            'stem': f"Clinical scenario: {osce.get('scenario_type', '')}"
        },
        'references': osce.get('references', []),
        'difficulty': osce.get('difficulty', 'intermediate'),
        'generated_at': osce.get('generated_at')
    }


def main():
    """Main validation execution"""
    print("\n" + "="*70)
    print("🔬 QA-003 RAG CITATION VALIDATOR - CARDIOLOGY OSCEs VALIDATION")
    print("="*70)
    print(f"Testing on: Cardiology OSCEs (50 scenarios)")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")

    # Initialize validator
    print("🔧 Initializing QA-003 RAG Citation Validator...")
    validator = RAGCitationValidator()
    print("✅ Validator initialized\n")

    # Load cardiology OSCEs
    osces_file = project_root / "data/osces/cardiology_50_osces.json"

    print("📂 Loading OSCE file...\n")
    if osces_file.exists():
        osces = load_osces(osces_file)
        print(f"✅ Loaded: {len(osces)} OSCEs from {osces_file.name}")
    else:
        print(f"❌ File not found: {osces_file}")
        return 1

    print(f"\n📊 Total OSCEs loaded: {len(osces)}")
    print("="*70 + "\n")

    if not osces:
        print("❌ No OSCEs found to validate!")
        return 1

    # Convert OSCEs to MCQ-like format for validation
    print("🔄 Converting OSCEs to validation format...")
    converted_osces = [convert_osce_to_mcq_format(osce) for osce in osces]
    print(f"✅ Converted {len(converted_osces)} OSCEs\n")

    # Validate all OSCEs
    print("🔍 Running QA-003 validation on all OSCEs...\n")
    results = validator.validate_batch(converted_osces)

    # Print detailed results
    print("\n" + "="*70)
    print("📊 VALIDATION RESULTS")
    print("="*70 + "\n")

    # Overall statistics
    print(f"**Overall Metrics:**")
    print(f"  Total OSCEs Validated: {results['total_mcqs']}")
    print(f"  Average Confidence: {results['average_confidence']:.3f}")
    print(f"  Auto-Approval Rate: {results['auto_approval_rate']:.1%} (Tier 1)")
    print()

    # Tier distribution
    print(f"**Tier Distribution:**")
    print(f"  Tier 1 (>0.90 - Auto-Approve): {results['tier1_count']} OSCEs ({results['tier1_count']/results['total_mcqs']:.1%})")
    print(f"  Tier 2 (0.75-0.90 - LLM Verify): {results['tier2_count']} OSCEs ({results['tier2_count']/results['total_mcqs']:.1%})")
    print(f"  Tier 3 (<0.75 - Reject): {results['tier3_count']} OSCEs ({results['tier3_count']/results['total_mcqs']:.1%})")
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
        elif valid_pct == 100.0:
            print(f"\n  ✅ ALL citations have complete metadata (OSCE generation successful!)")
        print()

    # Citations per OSCE analysis
    print(f"**Citations per OSCE Analysis:**")
    citations_per_osce = {}
    for v in validations:
        count = v.get('citation_count', 0)
        citations_per_osce[count] = citations_per_osce.get(count, 0) + 1

    for count in sorted(citations_per_osce.keys()):
        osce_count = citations_per_osce[count]
        print(f"  {count} citations/OSCE: {osce_count} OSCEs ({osce_count/results['total_mcqs']:.1%})")

    if 3 in citations_per_osce and citations_per_osce[3] == results['total_mcqs']:
        print(f"\n  ✅ All OSCEs have exactly 3 citations (Constraint 11 for OSCEs met!)")

    # Image metadata analysis
    print(f"\n**Image Metadata Analysis:**")
    total_images = sum(len(osce.get('scenario', {}).get('images', [])) for osce in osces)
    print(f"  Total Images: {total_images}")
    print(f"  Average Images per OSCE: {total_images/len(osces):.1f}")

    # Count image types
    image_types = {}
    for osce in osces:
        for image in osce.get('scenario', {}).get('images', []):
            img_type = image.get('type', 'Unknown')
            image_types[img_type] = image_types.get(img_type, 0) + 1

    print(f"\n  Image Type Distribution:")
    for img_type, count in sorted(image_types.items(), key=lambda x: x[1], reverse=True):
        print(f"    {img_type}: {count} images")

    print("\n" + "="*70)

    # Save detailed results
    report_path = project_root / "planning/qa_003_cardiology_osces_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump({
            'validation_date': datetime.now().isoformat(),
            'content_type': 'Cardiology OSCEs',
            'file': str(osces_file),
            'results': results,
            'summary': {
                'total_osces': results['total_mcqs'],
                'total_citations': total_citations,
                'total_images': total_images,
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
                'citations_per_osce': citations_per_osce,
                'image_types': image_types,
                'avg_images_per_osce': total_images/len(osces) if osces else 0
            }
        }, f, indent=2)

    print(f"\n📄 Detailed report saved to: {report_path}")

    # Return exit code
    if metadata_issues_count > 0:
        print("\n❌ VALIDATION FAILED - Metadata issues found")
        return 1
    elif 3 not in citations_per_osce or citations_per_osce.get(3, 0) != results['total_mcqs']:
        print("\n⚠️  VALIDATION WARNING - Not all OSCEs have 3 citations")
        return 1
    else:
        print("\n✅ VALIDATION PASSED - All citations valid with complete metadata")
        print("✅ CONSTRAINT 11 MET - All OSCEs have exactly 3 citations")
        print(f"✅ IMAGES INCLUDED - {total_images} medical images across {len(osces)} OSCEs")
        return 0


if __name__ == "__main__":
    sys.exit(main())
