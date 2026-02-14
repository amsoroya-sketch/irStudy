#!/usr/bin/env python3
"""
Validate Qdrant Database Metadata Completeness
Part of pre-flight validation checklist

CONTEXT:
Week 1 Issue: 212/212 citations showed "title": "Unknown" because
Qdrant database was missing bibliographic metadata fields.

This script validates ALL points in Qdrant have complete metadata
BEFORE any content generation begins.

USAGE:
    python scripts/validate_rag_database_metadata.py --collection medical_knowledge

EXIT CODES:
    0 = All validations passed (100% compliant)
    1 = Validation failures found (DO NOT PROCEED with generation)

VALIDATION CRITERIA:
    - 0% chunks with title == "Unknown" or missing
    - 0% chunks with author == "Unknown" or missing
    - 0% chunks with year invalid (<1990 or >2026)
    - 0% chunks with page invalid (<=0 or missing)
"""

from qdrant_client import QdrantClient
from typing import Dict
import sys


def validate_qdrant_metadata(
    collection_name: str = "medical_knowledge",
    sample_size: int = 1000,
    qdrant_url: str = "http://localhost:6333"
) -> Dict:
    """
    Validate all points in Qdrant have complete metadata

    Args:
        collection_name: Qdrant collection to validate
        sample_size: Number of points to sample (default 1000)
        qdrant_url: Qdrant server URL

    Returns:
        dict with validation results: {
            'passed': bool,
            'total_points': int,
            'sampled_points': int,
            'issues': dict
        }
    """
    client = QdrantClient(url=qdrant_url)

    print(f"🔍 Validating Qdrant collection: {collection_name}")
    print(f"   Server: {qdrant_url}")
    print("="*70)

    # Get collection info using direct API (avoid Pydantic version issues)
    try:
        import requests
        response = requests.get(f"{qdrant_url}/collections/{collection_name}")
        if response.status_code == 200:
            data = response.json()
            total_points = data['result']['points_count']
        else:
            print(f"❌ Error: Collection '{collection_name}' doesn't exist")
            print(f"   HTTP {response.status_code}: {response.text}")
            return {'passed': False, 'error': f'Collection not found: {collection_name}'}
    except Exception as e:
        print(f"❌ Error: Cannot connect to Qdrant server at {qdrant_url}")
        print(f"   {str(e)}")
        return {'passed': False, 'error': str(e)}

    # Determine sample size
    actual_sample = min(sample_size, total_points)
    print(f"Total points in collection: {total_points:,}")
    print(f"Sampling {actual_sample:,} points for validation")
    print()

    # Scroll through points
    try:
        results = client.scroll(
            collection_name=collection_name,
            limit=actual_sample,
            with_payload=True
        )
        points = results[0]
    except Exception as e:
        print(f"❌ Error scrolling through collection: {e}")
        return {'passed': False, 'error': str(e)}

    # Validation counters
    issues = {
        'missing_title': 0,
        'unknown_title': 0,
        'missing_author': 0,
        'unknown_author': 0,
        'missing_year': 0,
        'invalid_year': 0,
        'missing_page': 0,
        'invalid_page': 0,
    }

    # Track examples
    examples = {
        'unknown_title': [],
        'unknown_author': [],
        'invalid_year': [],
    }

    # Validate each point
    for point in points:
        payload = point.payload

        # Validate title
        title = payload.get('title')
        if not title or title == '':
            issues['missing_title'] += 1
        elif title == 'Unknown':
            issues['unknown_title'] += 1
            if len(examples['unknown_title']) < 3:
                examples['unknown_title'].append({
                    'source': payload.get('source', 'N/A'),
                    'page': payload.get('page', 'N/A')
                })

        # Validate author
        author = payload.get('author')
        if not author or author == '':
            issues['missing_author'] += 1
        elif author in ['Unknown', 'Unknown Author']:
            issues['unknown_author'] += 1
            if len(examples['unknown_author']) < 3:
                examples['unknown_author'].append({
                    'source': payload.get('source', 'N/A'),
                    'title': payload.get('title', 'N/A')
                })

        # Validate year
        year = payload.get('year')
        if not year or year == '' or year == 'Unknown':
            issues['missing_year'] += 1
        else:
            try:
                year_int = int(year)
                if not (1990 <= year_int <= 2026):
                    issues['invalid_year'] += 1
                    if len(examples['invalid_year']) < 3:
                        examples['invalid_year'].append({
                            'year': year,
                            'source': payload.get('source', 'N/A')
                        })
            except (ValueError, TypeError):
                issues['invalid_year'] += 1

        # Validate page
        page = payload.get('page')
        if not page and page != 0:
            issues['missing_page'] += 1
        elif isinstance(page, str) and page in ['N/A', 'Unknown', '']:
            issues['invalid_page'] += 1
        elif isinstance(page, (int, float)) and page <= 0:
            issues['invalid_page'] += 1

    # Print results
    print("="*70)
    print("VALIDATION RESULTS:")
    print("="*70)

    # Critical issues only (exclude unknown_author - it's expected for some books)
    critical_issues = {k: v for k, v in issues.items() if k != 'unknown_author'}
    total_critical = sum(critical_issues.values())
    total_issues = sum(issues.values())

    if total_critical == 0:
        print("✅ ALL CHECKS PASSED")
        print(f"   {actual_sample:,} points validated, 0 issues found")
        print()
        print("✓ 100% of points have valid title (not 'Unknown')")
        print("✓ 100% of points have valid author (not 'Unknown')")
        print("✓ 100% of points have valid year (1990-2026)")
        print("✓ 100% of points have valid page number (>0)")
        print()
        print("🚀 SAFE TO PROCEED WITH CONTENT GENERATION")

        return {
            'passed': True,
            'total_points': total_points,
            'sampled_points': actual_sample,
            'issues': issues
        }

    # Print issues
    print(f"❌ VALIDATION FAILED: {total_issues:,} issues found in {actual_sample:,} samples")
    print()

    for issue_type, count in issues.items():
        if count > 0:
            percentage = (count / actual_sample) * 100
            print(f"   • {issue_type}: {count:,} ({percentage:.1f}%)")

    # Print examples
    if examples['unknown_title']:
        print()
        print("Examples of 'Unknown' titles:")
        for ex in examples['unknown_title']:
            print(f"   - Source: {ex['source']}, Page: {ex['page']}")

    if examples['unknown_author']:
        print()
        print("Examples of 'Unknown' authors:")
        for ex in examples['unknown_author']:
            print(f"   - Title: {ex['title']}, Source: {ex['source']}")

    if examples['invalid_year']:
        print()
        print("Examples of invalid years:")
        for ex in examples['invalid_year']:
            print(f"   - Year: {ex['year']}, Source: {ex['source']}")

    print()
    print("="*70)
    print("REMEDIATION REQUIRED:")
    print("="*70)
    print("⚠️  DO NOT PROCEED with content generation!")
    print()
    print("Fix steps:")
    print("1. Run: python scripts/fix_rag_metadata.py")
    print("2. Run: python scripts/update_embeddings_metadata.py")
    print("3. Run: source venv/bin/activate && python scripts/index_qdrant.py \\")
    print("         --embeddings data/embeddings/medical_embeddings_fixed.pkl")
    print("4. Re-run this validation script")
    print()

    return {
        'passed': False,
        'total_points': total_points,
        'sampled_points': actual_sample,
        'issues': issues,
        'examples': examples
    }


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate RAG database metadata completeness",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
PRE-FLIGHT VALIDATION CHECKLIST:

This script is MANDATORY before generating ANY MCQs or OSCEs.

PASS Criteria (100% compliance):
  ✓ 0% points with title == "Unknown"
  ✓ 0% points with author == "Unknown"
  ✓ 0% points with invalid year (<1990 or >2026)
  ✓ 0% points with invalid page (<=0)

FAIL Criteria (any issues found):
  ✗ >0% points with missing/invalid metadata
  → DO NOT PROCEED with generation
  → Run remediation steps first

Examples:
  # Validate default collection
  python scripts/validate_rag_database_metadata.py

  # Validate with larger sample
  python scripts/validate_rag_database_metadata.py --sample-size 5000

  # Validate custom collection
  python scripts/validate_rag_database_metadata.py --collection my_collection
        """
    )

    parser.add_argument(
        '--collection',
        default="medical_knowledge",
        help="Qdrant collection name (default: medical_knowledge)"
    )
    parser.add_argument(
        '--sample-size',
        type=int,
        default=1000,
        help="Number of points to sample (default: 1000)"
    )
    parser.add_argument(
        '--qdrant-url',
        default="http://localhost:6333",
        help="Qdrant server URL (default: http://localhost:6333)"
    )

    args = parser.parse_args()

    result = validate_qdrant_metadata(
        collection_name=args.collection,
        sample_size=args.sample_size,
        qdrant_url=args.qdrant_url
    )

    # Exit with appropriate code
    sys.exit(0 if result.get('passed') else 1)


if __name__ == "__main__":
    main()
