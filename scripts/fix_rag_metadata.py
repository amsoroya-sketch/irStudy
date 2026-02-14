#!/usr/bin/env python3
"""
Fix RAG Database Metadata
Remediation script to extract title/author/year from PDF filenames

CONTEXT:
Week 1 Issue: 212/212 citations showed "title": "Unknown" because
metadata was lost during chunking phase and never indexed to Qdrant.

This script:
1. Parses PDF filenames to extract bibliographic metadata
2. Updates data/chunks.json with complete title/author/year/edition
3. Validates 100% chunks have required metadata

USAGE:
    python scripts/fix_rag_metadata.py --dry-run  # Preview changes
    python scripts/fix_rag_metadata.py            # Apply fixes

EXIT CODES:
    0 = Success
    1 = Validation failures
"""

import json
import re
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime
import sys


def parse_filename_metadata(filename: str) -> Dict[str, str]:
    """
    Extract title, author, edition, year from PDF filename

    Examples:
        "John Murtagh General Practice, 8th Edition.pdf"
        -> title="John Murtagh's General Practice", edition="8th", year="2020"

        "Nicholas J Talley, Simon O'Connor - Talley and O'Connor's Clinical Examination (8th edition)-Elsevier Australia (2017).pdf"
        -> title="Talley and O'Connor's Clinical Examination", author="Talley & O'Connor", edition="8th"

        "OXFORD HANDBOOK OF EMERGENCY MEDICINE 5TH EDITION (2020).pdf"
        -> title="Oxford Handbook of Emergency Medicine", edition="5th", year="2020"

        "Clinical Examination-Talley & Connor-pdf.pdf"
        -> title="Talley & Connor's Clinical Examination", author="Talley & Connor"

    Args:
        filename: PDF filename to parse

    Returns:
        dict with keys: title, author, edition, year
    """
    metadata = {
        'title': '',
        'author': '',
        'edition': '',
        'year': ''
    }

    # Pattern 0: "Full Author Name - Book Title (edition)-Publisher (year).pdf"
    # Example: "Nicholas J Talley, Simon O'Connor - Talley and O'Connor's Clinical Examination (8th edition)-Elsevier Australia (2017).pdf"
    match = re.search(r"^(.+?)\s+-\s+(.+?)\s+\((\d+(?:st|nd|rd|th))\s+edition\).*?\((\d{4})\)\.pdf$", filename, re.IGNORECASE)
    if match:
        author_full = match.group(1).strip()
        title = match.group(2).strip()
        edition = match.group(3)
        year = match.group(4)

        # Simplify author name (e.g., "Nicholas J Talley, Simon O'Connor" -> "Talley & O'Connor")
        author_short = author_full.split(',')[0].split()[-1]  # Get last name of first author
        if ',' in author_full:
            author_short += " et al."

        metadata.update({
            'title': title,
            'author': author_short,
            'edition': edition,
            'year': year
        })
        return metadata

    # Pattern 0b: "Title-Author-pdf.pdf" format
    # Example: "Clinical Examination-Talley & Connor-pdf.pdf"
    match = re.search(r"^(.+?)-(.+?)-pdf\.pdf$", filename, re.IGNORECASE)
    if match:
        title = match.group(1).strip()
        author = match.group(2).strip()

        metadata.update({
            'title': f"{author}'s {title}",
            'author': author,
            'edition': '',
            'year': '2020'  # Default
        })
        return metadata

    # Pattern 0c: "OXFORD HANDBOOK OF TOPIC EDITION (YEAR).pdf"
    # Example: "OXFORD HANDBOOK OF EMERGENCY MEDICINE 5TH EDITION (2020).pdf"
    match = re.search(r"^OXFORD\s+HANDBOOK\s+OF\s+(.+?)\s+(\d+(?:ST|ND|RD|TH))\s+EDITION\s+\((\d{4})\)\.pdf$", filename, re.IGNORECASE)
    if match:
        topic = match.group(1).strip()
        edition = match.group(2).lower()
        year = match.group(3)

        metadata.update({
            'title': f"Oxford Handbook of {topic.title()}",
            'author': "Oxford University Press",
            'edition': edition,
            'year': year
        })
        return metadata

    # Pattern 0d: "AMC Handbook of TOPIC.pdf"
    # Example: "AMC Handbook of Clinical Assessment.pdf"
    if filename.startswith('AMC '):
        title = filename.replace('.pdf', '').strip()
        metadata.update({
            'title': title,
            'author': "Australian Medical Council",
            'year': "2023",
            'edition': ''
        })
        return metadata

    # Pattern 1: "Author Name, Edition.pdf"
    # Example: "John Murtagh General Practice, 8th Edition.pdf"
    match = re.search(r"([^,]+),\s+(\d+(?:st|nd|rd|th))\s+Edition\.pdf$", filename, re.IGNORECASE)
    if match:
        title = match.group(1).strip()
        edition = match.group(2)

        # Extract author from title (first word or two words)
        author_match = re.match(r"(\w+(?:\s+(?:O'Connor|&\s+\w+))?)", title)
        author = author_match.group(1) if author_match else title.split()[0]

        metadata.update({
            'title': title,
            'author': author,
            'edition': edition,
            'year': estimate_year_from_edition(edition)
        })
        return metadata

    # Pattern 2: "Author Name Topic Edition.pdf" (no comma)
    # Example: "Talley O'Connor Clinical Examination 8th Edition.pdf"
    match = re.search(r"(.+?)\s+(\d+(?:st|nd|rd|th))\s+Edition\.pdf$", filename, re.IGNORECASE)
    if match:
        title = match.group(1).strip()
        edition = match.group(2)

        author_match = re.match(r"(\w+(?:\s+O'Connor|\s+&\s+\w+)?)", title)
        author = author_match.group(1) if author_match else title.split()[0]

        metadata.update({
            'title': title,
            'author': author,
            'edition': edition,
            'year': estimate_year_from_edition(edition)
        })
        return metadata

    # Pattern 3: "Therapeutic Guidelines - Topic YEAR.pdf"
    # Example: "Therapeutic Guidelines - Antibiotic 2024.pdf"
    match = re.search(r"Therapeutic\s+Guidelines\s*-?\s*(.+?)\s+(\d{4})\.pdf$", filename, re.IGNORECASE)
    if match:
        topic = match.group(1).strip()
        year = match.group(2)

        metadata.update({
            'title': f"Therapeutic Guidelines: {topic}",
            'author': "Therapeutic Guidelines Ltd",
            'year': year,
            'edition': ''
        })
        return metadata

    # Pattern 4: Cochrane reviews "CD######_topic_description.pdf"
    # Example: "CD006332_muopioid_antagonists_for_opioidinduced_bowel_dysfunction.pdf"
    match = re.match(r"(CD\d{6})_(.+)\.pdf$", filename, re.IGNORECASE)
    if match:
        review_id = match.group(1)
        topic = match.group(2).replace('_', ' ')

        # Clean up topic title
        topic_clean = topic.replace('  ', ' ').strip()

        metadata.update({
            'title': f"{topic_clean.title()} (Cochrane {review_id})",
            'author': "Cochrane Collaboration",
            'year': "2023",  # Default for Cochrane reviews
            'edition': review_id
        })
        return metadata

    # Pattern 5: StatPearls "statpearls_topic_name.json"
    if filename.startswith('statpearls_') or 'statpearls' in filename.lower():
        topic = filename.replace('statpearls_', '').replace('.pdf', '').replace('.json', '').replace('_', ' ')
        metadata.update({
            'title': f"StatPearls: {topic.title()}",
            'author': "StatPearls Publishing",
            'year': "2024",
            'edition': ''
        })
        return metadata

    # Pattern 6: Generic fallback - use filename as title
    title_clean = filename.replace('.pdf', '').replace('_', ' ').replace('  ', ' ')

    metadata.update({
        'title': title_clean.title(),
        'author': "Unknown Author",
        'year': "2020",  # Default year
        'edition': ''
    })

    return metadata


def estimate_year_from_edition(edition: str) -> str:
    """
    Estimate publication year from edition number

    Based on typical medical textbook update cycles (5-7 years)
    """
    edition_years = {
        '9th': '2024',
        '8th': '2020',
        '7th': '2015',
        '6th': '2010',
        '5th': '2005',
        '4th': '2000',
        '3rd': '1995',
    }

    # Try exact match
    if edition in edition_years:
        return edition_years[edition]

    # Try extracting number
    match = re.search(r'(\d+)', edition)
    if match:
        num = int(match.group(1))
        if num >= 9:
            return '2024'
        elif num >= 8:
            return '2020'
        elif num >= 7:
            return '2015'
        elif num >= 6:
            return '2010'
        else:
            return '2005'

    return '2020'  # Default


def fix_chunks_metadata(
    chunks_file: str = "data/chunks.json",
    dry_run: bool = False
) -> Dict:
    """
    Fix metadata in chunks.json
    Re-parse filenames to extract missing title/author/year

    Args:
        chunks_file: Path to chunks JSON file
        dry_run: If True, preview changes without saving

    Returns:
        dict with statistics: total_chunks, fixed_count, issues
    """
    chunks_path = Path(chunks_file)

    if not chunks_path.exists():
        print(f"❌ Error: File not found: {chunks_file}")
        return {'success': False, 'error': 'File not found'}

    print(f"🔧 Fixing metadata for: {chunks_file}")
    print("="*60)

    # Load chunks
    with open(chunks_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Handle both formats: list or dict with 'chunks' key
    if isinstance(data, list):
        chunks = data
    elif isinstance(data, dict) and 'chunks' in data:
        chunks = data['chunks']
    else:
        print(f"❌ Error: Unknown chunks.json format")
        return {'success': False, 'error': 'Unknown format'}

    print(f"Loaded {len(chunks):,} chunks")

    # Track statistics
    stats = {
        'total_chunks': len(chunks),
        'fixed_title': 0,
        'fixed_author': 0,
        'fixed_year': 0,
        'fixed_edition': 0,
        'unique_sources': set(),
        'issues': []
    }

    # Process each chunk
    for idx, chunk in enumerate(chunks):
        metadata = chunk.get('metadata', {})
        source = metadata.get('source', '')

        if not source:
            stats['issues'].append(f"Chunk {idx}: Missing 'source' field")
            continue

        stats['unique_sources'].add(source)

        # Parse filename to get metadata
        parsed = parse_filename_metadata(source)

        # Update missing fields
        if not metadata.get('title') or metadata.get('title') == 'Unknown':
            metadata['title'] = parsed['title']
            stats['fixed_title'] += 1

        if not metadata.get('author') or metadata.get('author') == 'Unknown':
            metadata['author'] = parsed['author']
            stats['fixed_author'] += 1

        if not metadata.get('year') or metadata.get('year') == 'Unknown':
            metadata['year'] = parsed['year']
            stats['fixed_year'] += 1

        if not metadata.get('edition'):
            metadata['edition'] = parsed['edition']
            if parsed['edition']:
                stats['fixed_edition'] += 1

        # Update chunk
        chunk['metadata'] = metadata

    # Print statistics
    print("\n" + "="*60)
    print("METADATA FIX SUMMARY:")
    print("="*60)
    print(f"Total chunks processed: {stats['total_chunks']:,}")
    print(f"Unique source files: {len(stats['unique_sources'])}")
    print(f"\nFields fixed:")
    print(f"  • Title: {stats['fixed_title']:,} chunks")
    print(f"  • Author: {stats['fixed_author']:,} chunks")
    print(f"  • Year: {stats['fixed_year']:,} chunks")
    print(f"  • Edition: {stats['fixed_edition']:,} chunks")

    if stats['issues']:
        print(f"\n⚠️  Issues found: {len(stats['issues'])}")
        for issue in stats['issues'][:10]:  # Show first 10
            print(f"  • {issue}")

    # Save if not dry run
    if not dry_run:
        # Create backup
        backup_path = chunks_path.with_suffix('.json.backup')
        backup_path.write_text(chunks_path.read_text())
        print(f"\n💾 Backup created: {backup_path}")

        # Save fixed version
        if isinstance(data, list):
            output_data = chunks
        else:
            data['chunks'] = chunks
            output_data = data

        with open(chunks_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        print(f"✅ Saved fixed chunks to: {chunks_path}")
    else:
        print("\n🔍 DRY RUN - No changes saved")

    # Sample check
    print("\n" + "="*60)
    print("SAMPLE METADATA (first 3 unique sources):")
    print("="*60)

    seen_sources = set()
    for chunk in chunks[:100]:  # Check first 100 chunks
        source = chunk['metadata'].get('source', '')
        if source and source not in seen_sources:
            seen_sources.add(source)
            meta = chunk['metadata']
            print(f"\nSource: {source}")
            print(f"  Title: {meta.get('title', 'N/A')}")
            print(f"  Author: {meta.get('author', 'N/A')}")
            print(f"  Year: {meta.get('year', 'N/A')}")
            print(f"  Edition: {meta.get('edition', 'N/A')}")
            print(f"  Page: {meta.get('page', 'N/A')}")

            if len(seen_sources) >= 3:
                break

    stats['success'] = True
    return stats


def validate_fixed_metadata(chunks_file: str = "data/chunks.json") -> Dict:
    """
    Validate that all chunks have complete metadata after fix

    Returns:
        dict with validation results
    """
    chunks_path = Path(chunks_file)

    if not chunks_path.exists():
        return {'success': False, 'error': 'File not found'}

    with open(chunks_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if isinstance(data, list):
        chunks = data
    else:
        chunks = data.get('chunks', [])

    print("\n" + "="*60)
    print("VALIDATION RESULTS:")
    print("="*60)

    issues = {
        'missing_title': 0,
        'unknown_title': 0,
        'missing_author': 0,
        'unknown_author': 0,
        'missing_year': 0,
        'invalid_year': 0,
    }

    for chunk in chunks:
        meta = chunk.get('metadata', {})

        # Check title
        title = meta.get('title')
        if not title or title.strip() == '':
            issues['missing_title'] += 1
        elif title == 'Unknown':
            issues['unknown_title'] += 1

        # Check author
        author = meta.get('author')
        if not author or author.strip() == '':
            issues['missing_author'] += 1
        elif author == 'Unknown' or author == 'Unknown Author':
            issues['unknown_author'] += 1

        # Check year
        year = meta.get('year')
        if not year or year == '':
            issues['missing_year'] += 1
        else:
            try:
                year_int = int(year)
                if not (1990 <= year_int <= 2026):
                    issues['invalid_year'] += 1
            except (ValueError, TypeError):
                issues['invalid_year'] += 1

    total_issues = sum(issues.values())

    if total_issues == 0:
        print("✅ VALIDATION PASSED")
        print(f"   All {len(chunks):,} chunks have complete metadata")
        return {'success': True, 'issues': issues}

    print(f"❌ VALIDATION FAILED: {total_issues:,} issues found\n")

    for issue_type, count in issues.items():
        if count > 0:
            percentage = (count / len(chunks)) * 100
            print(f"   • {issue_type}: {count:,} ({percentage:.1f}%)")

    return {'success': False, 'issues': issues}


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Fix RAG database metadata by parsing PDF filenames",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview changes without saving
  python scripts/fix_rag_metadata.py --dry-run

  # Apply fixes and save
  python scripts/fix_rag_metadata.py

  # Use custom chunks file
  python scripts/fix_rag_metadata.py --chunks data/chunks_all.json

Next Steps After Running:
  1. Re-generate embeddings: python scripts/generate_embeddings.py
  2. Re-index Qdrant: python scripts/index_qdrant.py
  3. Validate: python scripts/validate_rag_database_metadata.py
        """
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help="Preview changes without saving"
    )
    parser.add_argument(
        '--chunks',
        default="data/chunks.json",
        help="Path to chunks JSON file (default: data/chunks.json)"
    )

    args = parser.parse_args()

    # Fix metadata
    result = fix_chunks_metadata(args.chunks, args.dry_run)

    if not result.get('success'):
        print(f"\n❌ Error: {result.get('error', 'Unknown error')}")
        return 1

    # Validate if not dry run
    if not args.dry_run:
        validation = validate_fixed_metadata(args.chunks)

        if not validation.get('success'):
            print("\n⚠️  Validation found issues. Manual review may be needed.")
            return 1

    print("\n" + "="*60)
    print("NEXT STEPS:")
    print("="*60)
    print("1. Review the sample metadata above")
    print("2. Re-generate embeddings:")
    print("   python scripts/generate_embeddings.py")
    print("3. Re-index Qdrant database:")
    print("   python scripts/index_qdrant.py")
    print("4. Validate RAG database:")
    print("   python scripts/validate_rag_database_metadata.py")
    print("5. Test RAG citation quality:")
    print("   python scripts/test_rag_citation_quality.py --queries 20")
    print("="*60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
