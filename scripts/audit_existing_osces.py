#!/usr/bin/env python3
"""
Audit Existing OSCE Modules
Week 1 Day 5 Afternoon - Catalog all existing OSCE modules

Catalogs:
- Module count by specialty
- Citation presence/absence
- Content type (history, examination, counseling, etc.)
- File sizes and structure
"""

import csv
import re
from pathlib import Path
from datetime import datetime


def extract_osce_metadata(file_path: Path) -> dict:
    """Extract metadata from OSCE markdown file"""

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract title (first # heading)
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    title = title_match.group(1) if title_match else file_path.stem

    # Count citations (look for References, Citations sections)
    has_citations = bool(re.search(r'(?i)(##\s*references|##\s*citations|bibliography)', content))

    # Count references
    citation_count = len(re.findall(r'^\d+\.\s+\[.*?\]|^\*\s+\[.*?\]', content, re.MULTILINE))

    # Detect content type
    content_lower = content.lower()
    content_types = []
    if 'history' in content_lower:
        content_types.append('History Taking')
    if 'examination' in content_lower or 'physical exam' in content_lower:
        content_types.append('Physical Examination')
    if 'communication' in content_lower or 'breaking bad news' in content_lower:
        content_types.append('Communication')
    if 'counsell' in content_lower:
        content_types.append('Counseling')
    if 'differential' in content_lower:
        content_types.append('Differentials')
    if 'osce' in content_lower and 'station' in content_lower:
        content_types.append('OSCE Station')

    # Word count and file size
    word_count = len(content.split())
    file_size_kb = file_path.stat().st_size / 1024

    # Extract specialty from directory
    specialty = file_path.parent.name

    return {
        'file_path': str(file_path.relative_to(file_path.parents[2])),  # Relative to project root
        'filename': file_path.name,
        'specialty': specialty,
        'title': title,
        'has_citations': has_citations,
        'citation_count': citation_count,
        'content_types': ', '.join(content_types) if content_types else 'General',
        'word_count': word_count,
        'file_size_kb': round(file_size_kb, 2),
        'last_modified': datetime.fromtimestamp(file_path.stat().st_mtime).strftime('%Y-%m-%d')
    }


def main():
    """Main audit execution"""
    print("\n" + "="*70)
    print("📋 EXISTING OSCE MODULES AUDIT")
    print("="*70)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Find project root
    project_root = Path(__file__).parent.parent
    osce_dir = project_root / "ICRP_OSCE_Preparation"

    if not osce_dir.exists():
        print(f"❌ OSCE directory not found: {osce_dir}")
        return 1

    # Find all OSCE markdown files
    print("🔍 Scanning for OSCE modules...")
    osce_files = []

    for md_file in osce_dir.rglob("*.md"):
        # Exclude index and README files
        if md_file.name in ['START_HERE.md', 'README.md'] or 'MASTER_INDEX' in md_file.name:
            continue
        osce_files.append(md_file)

    osce_files.sort()

    print(f"✅ Found {len(osce_files)} OSCE modules\n")

    # Extract metadata from each file
    print("📊 Extracting metadata...")
    modules = []

    for osce_file in osce_files:
        try:
            metadata = extract_osce_metadata(osce_file)
            modules.append(metadata)
            print(f"  ✓ {metadata['specialty']}: {metadata['filename']}")
        except Exception as e:
            print(f"  ✗ Error processing {osce_file.name}: {e}")

    print(f"\n✅ Processed {len(modules)} modules\n")

    # Generate summary statistics
    print("="*70)
    print("📈 AUDIT SUMMARY")
    print("="*70)

    # Count by specialty
    specialty_counts = {}
    for module in modules:
        specialty = module['specialty']
        specialty_counts[specialty] = specialty_counts.get(specialty, 0) + 1

    print("\n**Modules by Specialty:**")
    for specialty, count in sorted(specialty_counts.items()):
        print(f"  {specialty:25s}: {count:2d} modules")

    print(f"\n  {'TOTAL':25s}: {len(modules):2d} modules")

    # Citation analysis
    modules_with_citations = sum(1 for m in modules if m['has_citations'])
    modules_without_citations = len(modules) - modules_with_citations
    total_citations = sum(m['citation_count'] for m in modules)

    print("\n**Citation Analysis:**")
    print(f"  Modules WITH citations:    {modules_with_citations:2d} ({modules_with_citations/len(modules)*100:.1f}%)")
    print(f"  Modules WITHOUT citations: {modules_without_citations:2d} ({modules_without_citations/len(modules)*100:.1f}%)")
    print(f"  Total citations found:     {total_citations}")
    print(f"  Average citations/module:  {total_citations/len(modules):.1f}")

    # Content type distribution
    content_type_counts = {}
    for module in modules:
        for content_type in module['content_types'].split(', '):
            content_type_counts[content_type] = content_type_counts.get(content_type, 0) + 1

    print("\n**Content Types:**")
    for content_type, count in sorted(content_type_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {content_type:25s}: {count:2d} modules")

    # Word count statistics
    total_words = sum(m['word_count'] for m in modules)
    avg_words = total_words / len(modules)
    min_words = min(m['word_count'] for m in modules)
    max_words = max(m['word_count'] for m in modules)

    print("\n**Content Statistics:**")
    print(f"  Total words:     {total_words:,}")
    print(f"  Average words:   {avg_words:,.0f}")
    print(f"  Min words:       {min_words:,}")
    print(f"  Max words:       {max_words:,}")

    # Save to CSV
    output_file = project_root / "planning/jan-22-plan/existing_osce_audit.csv"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = [
            'specialty', 'filename', 'title', 'content_types',
            'has_citations', 'citation_count', 'word_count',
            'file_size_kb', 'last_modified', 'file_path'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(modules)

    print(f"\n💾 Audit report saved: {output_file}")

    # Identify modules without citations (for Week 2 improvement)
    print("\n" + "="*70)
    print("⚠️  MODULES WITHOUT CITATIONS (Week 2 Priority)")
    print("="*70)

    no_citation_modules = [m for m in modules if not m['has_citations']]
    if no_citation_modules:
        for module in no_citation_modules[:10]:  # Show first 10
            print(f"  • {module['specialty']}: {module['filename']}")

        if len(no_citation_modules) > 10:
            print(f"  ... and {len(no_citation_modules) - 10} more")
    else:
        print("  ✅ All modules have citations!")

    print("\n" + "="*70)
    print("✅ OSCE AUDIT COMPLETE")
    print("="*70)

    print(f"\n📊 Summary:")
    print(f"  • Total OSCE modules: {len(modules)}")
    print(f"  • Specialties covered: {len(specialty_counts)}")
    print(f"  • Modules with citations: {modules_with_citations}/{len(modules)}")
    print(f"  • Modules needing citations: {modules_without_citations}")
    print(f"\n🎯 Week 2 Action: Add citations to {modules_without_citations} modules\n")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
