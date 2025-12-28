#!/usr/bin/env python3
"""
Remove unverifiable citations (confidence <0.45) from files
Strategy: Remove the generic citation, leave the claim for expert review
"""

import re
import json
from pathlib import Path
from typing import List, Tuple

class UnverifiableCitationRemover:
    def __init__(self):
        self.removed_count = 0
        self.files_modified = []
        self.removed_citations = []

    def remove_generic_book_citations(self, file_path: Path, lines_to_fix: List[int]) -> int:
        """Remove generic book citations from specific lines"""

        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            modified = False
            removed_in_file = 0

            for line_num in lines_to_fix:
                if line_num > len(lines):
                    continue

                line = lines[line_num - 1]  # Convert to 0-indexed

                # Pattern for generic book citations (without page numbers)
                patterns = [
                    (r'\s*\(Talley & O\'Connor\'s Clinical Examination, 8th ed\)', 'Talley'),
                    (r'\s*\(Murtagh\'s General Practice, 8th ed\)', 'Murtagh')
                ]

                for pattern, book in patterns:
                    if re.search(pattern, line):
                        # Check if it already has a page number
                        if ', p.' in line:
                            continue  # Already has page, skip

                        # Remove the generic citation
                        new_line = re.sub(pattern, '', line)

                        # Add comment marker for expert review
                        if not new_line.strip().endswith('<!-- NEEDS CITATION -->'):
                            new_line = new_line.rstrip() + ' <!-- NEEDS CITATION -->'

                        lines[line_num - 1] = new_line
                        modified = True
                        removed_in_file += 1

                        self.removed_citations.append({
                            'file': str(file_path),
                            'line': line_num,
                            'book': book,
                            'original': line.strip(),
                            'new': new_line.strip()
                        })

                        print(f"  ✓ Line {line_num}: Removed unverifiable {book} citation")

            if modified:
                # Write back
                updated_content = '\n'.join(lines)
                file_path.write_text(updated_content, encoding='utf-8')
                self.files_modified.append(str(file_path))
                self.removed_count += removed_in_file
                return removed_in_file

            return 0

        except Exception as e:
            print(f"  ✗ Error processing {file_path}: {e}")
            return 0

def main():
    """Main processing function"""

    print("🧹 Removing unverifiable citations (RAG confidence <0.45)...")
    print("=" * 80)
    print()
    print("Strategy:")
    print("  1. Remove generic citations that RAG couldn't verify")
    print("  2. Add <!-- NEEDS CITATION --> marker for expert review")
    print("  3. Expert can either:")
    print("     - Add proper citation with page number")
    print("     - Remove the claim if it can't be cited")
    print()

    # Load validation report to get unverifiable citations
    with open('citation_validation_report.json', 'r') as f:
        report = json.load(f)

    remover = UnverifiableCitationRemover()

    # Group by file
    citations_by_file = {}
    for cit in report['non_compliant_citations']:
        if cit['type'] == 'book_without_page':
            citation_text = cit['citation']

            # Skip false positives
            if ('AMC Clinical examiners' in citation_text or
                '.md' in citation_text or
                'NICE' in citation_text or
                'Australian' in citation_text and 'Handbook' not in citation_text):
                continue

            # Only process real Talley/Murtagh citations
            if 'Talley' not in citation_text and 'Murtagh' not in citation_text:
                continue

            # Extract file path from context (this is tricky, we'll search)
            # For now, let's search all files for this line number
            line_num = cit['line']
            context = cit['context']

            # We'll need to match based on context
            if context not in citations_by_file:
                citations_by_file[context] = {
                    'line': line_num,
                    'citation': citation_text,
                    'context': context
                }

    print(f"📂 Found {len(citations_by_file)} unverifiable citations to remove...")
    print()

    # Search through files to find and remove these citations
    osce_dir = Path('ICRP_OSCE_Preparation')
    md_files = list(osce_dir.rglob('*.md'))

    for md_file in md_files:
        try:
            content = md_file.read_text(encoding='utf-8')
            lines = content.split('\n')
            lines_to_fix = []

            # Find lines with generic citations
            for line_num, line in enumerate(lines, 1):
                # Check for generic Talley/Murtagh WITHOUT page numbers
                if (('(Talley & O\'Connor\'s Clinical Examination, 8th ed)' in line or
                     '(Murtagh\'s General Practice, 8th ed)' in line) and
                    ', p.' not in line):
                    lines_to_fix.append(line_num)

            if lines_to_fix:
                print(f"Processing: {md_file.name}")
                removed = remover.remove_generic_book_citations(md_file, lines_to_fix)
                if removed > 0:
                    print(f"  Removed {removed} unverifiable citations")
                print()

        except Exception as e:
            continue

    print()
    print("=" * 80)
    print(f"✅ Complete!")
    print(f"   Citations removed: {remover.removed_count}")
    print(f"   Files modified: {len(remover.files_modified)}")
    print()
    print("Next steps:")
    print("  1. Expert reviews lines marked <!-- NEEDS CITATION -->")
    print("  2. Expert either:")
    print("     - Adds proper citation with exact page number")
    print("     - Removes the claim if unsupported")
    print()

    # Save log
    log = {
        'citations_removed': remover.removed_count,
        'files_modified': remover.files_modified,
        'removed_citations': remover.removed_citations
    }

    with open('removed_citations_log.json', 'w') as f:
        json.dump(log, f, indent=2)

    print("📝 Log saved to: removed_citations_log.json")

if __name__ == "__main__":
    main()
