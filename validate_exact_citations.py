#!/usr/bin/env python3
"""
Validate that all citations have exact references (page numbers or section numbers)
Enforce PROJECT_CONSTRAINTS.md Section 1.4
"""

import re
import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List

class CitationValidator:
    def __init__(self):
        self.results = {
            'compliant_citations': [],
            'non_compliant_citations': [],
            'etg_specialty_citations': [],
            'statistics': {},
            'files_checked': 0,
            'total_citations': 0
        }

    def is_citation_compliant(self, citation: str) -> tuple:
        """
        Check if citation is compliant with PROJECT_CONSTRAINTS.md Section 1.4
        Returns: (is_compliant, compliance_type, reason)
        """

        # Book citations MUST have page numbers
        if any(book in citation for book in ['Talley', 'Murtagh', 'Oxford', 'AMC', 'Harrison']):
            if re.search(r'p\.\s*\d+', citation):
                return (True, 'book_with_page', 'Book citation with page number')
            else:
                return (False, 'book_without_page', 'Book citation missing page number')

        # eTG citations MUST have section numbers OR specialty
        if 'Therapeutic Guidelines' in citation or 'eTG' in citation:
            # Check for section number
            if re.search(r'Section\s+[\d.]+', citation):
                return (True, 'etg_with_section', 'eTG citation with section number')

            # Check for specialty (acceptable for digital resource)
            if re.search(r'Therapeutic Guidelines:\s*\w+', citation):
                # Extract specialty
                match = re.search(r'Therapeutic Guidelines:\s*(\w+)', citation)
                if match:
                    specialty = match.group(1)
                    if specialty not in ['2024', '2023']:  # Not just a year
                        return (True, 'etg_with_specialty', f'eTG citation with specialty ({specialty})')

            return (False, 'etg_generic', 'eTG citation without section or specialty')

        # Other medical sources
        if any(term in citation for term in ['Guidelines', 'Handbook', 'Manual']):
            # Should have page or section
            if re.search(r'(p\.\s*\d+|Section\s+[\d.]+|Chapter\s+\d+)', citation):
                return (True, 'other_with_ref', 'Other source with reference')
            else:
                return (False, 'other_without_ref', 'Other source without reference')

        # Not a medical citation (might be general reference)
        return (True, 'other', 'Non-medical citation')

    def validate_file(self, file_path: Path) -> Dict:
        """Validate all citations in a markdown file"""

        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')

            file_stats = {
                'file': str(file_path.relative_to('ICRP_OSCE_Preparation')),
                'compliant': [],
                'non_compliant': [],
                'etg_specialty': []
            }

            # Pattern to find citations
            citation_pattern = r'\([^)]*?(?:Talley|Murtagh|Therapeutic Guidelines|eTG|Oxford|AMC|Guidelines|Handbook)[^)]*?\)'

            for line_num, line in enumerate(lines, 1):
                for match in re.finditer(citation_pattern, line):
                    citation = match.group()

                    # Skip "AMC Frequency Indicator" - not a real citation
                    if 'Frequency Indicator' in citation:
                        continue

                    self.results['total_citations'] += 1

                    is_compliant, comp_type, reason = self.is_citation_compliant(citation)

                    citation_info = {
                        'line': line_num,
                        'citation': citation,
                        'type': comp_type,
                        'reason': reason,
                        'context': line.strip()[:150]
                    }

                    if is_compliant:
                        if comp_type == 'etg_with_specialty':
                            file_stats['etg_specialty'].append(citation_info)
                            self.results['etg_specialty_citations'].append(citation_info)
                        else:
                            file_stats['compliant'].append(citation_info)
                            self.results['compliant_citations'].append(citation_info)
                    else:
                        file_stats['non_compliant'].append(citation_info)
                        self.results['non_compliant_citations'].append(citation_info)

            return file_stats

        except Exception as e:
            print(f"Error validating {file_path}: {e}")
            return {}

    def generate_report(self) -> str:
        """Generate human-readable validation report"""

        total = self.results['total_citations']
        compliant = len(self.results['compliant_citations'])
        etg_specialty = len(self.results['etg_specialty_citations'])
        non_compliant = len(self.results['non_compliant_citations'])

        exact_ref_count = compliant
        acceptable_count = compliant + etg_specialty
        total_compliant_pct = (acceptable_count / total * 100) if total > 0 else 0
        exact_ref_pct = (exact_ref_count / total * 100) if total > 0 else 0

        report = []
        report.append("=" * 80)
        report.append("CITATION VALIDATION REPORT")
        report.append("=" * 80)
        report.append("")
        report.append("📊 Summary Statistics:")
        report.append(f"   Total citations checked: {total}")
        report.append(f"   ✅ Exact references (page/section): {exact_ref_count} ({exact_ref_pct:.1f}%)")
        report.append(f"   ✅ eTG with specialty (acceptable): {etg_specialty} ({etg_specialty/total*100 if total > 0 else 0:.1f}%)")
        report.append(f"   ✅ TOTAL COMPLIANT: {acceptable_count} ({total_compliant_pct:.1f}%)")
        report.append(f"   ❌ Non-compliant (generic): {non_compliant} ({non_compliant/total*100 if total > 0 else 0:.1f}%)")
        report.append("")

        # Breakdown by type
        type_counts = defaultdict(int)
        for citation in self.results['compliant_citations']:
            type_counts[citation['type']] += 1
        for citation in self.results['etg_specialty_citations']:
            type_counts[citation['type']] += 1
        for citation in self.results['non_compliant_citations']:
            type_counts[citation['type']] += 1

        report.append("📋 Citation Type Breakdown:")
        for cit_type, count in sorted(type_counts.items(), key=lambda x: -x[1]):
            status = "✅" if cit_type not in ['book_without_page', 'etg_generic', 'other_without_ref'] else "❌"
            report.append(f"   {status} {cit_type}: {count}")
        report.append("")

        # Non-compliant details
        if non_compliant > 0:
            report.append("❌ NON-COMPLIANT CITATIONS (need manual review):")
            report.append("-" * 80)

            # Group by file
            by_file = defaultdict(list)
            for citation in self.results['non_compliant_citations']:
                # Find file from context
                for comp_cit in self.results['compliant_citations'] + self.results['etg_specialty_citations'] + self.results['non_compliant_citations']:
                    if citation == comp_cit:
                        continue

            # Just list them
            for i, citation in enumerate(self.results['non_compliant_citations'][:50], 1):  # Limit to 50
                report.append(f"{i}. Line {citation.get('line', 'N/A')}: {citation['citation']}")
                report.append(f"   Type: {citation['type']} - {citation['reason']}")
                report.append(f"   Context: {citation.get('context', 'N/A')[:100]}...")
                report.append("")

        # eTG specialty citations (accepted as compliant)
        if etg_specialty > 0:
            report.append("")
            report.append("✅ eTG CITATIONS WITH SPECIALTY (accepted as compliant for digital resource):")
            report.append("-" * 80)
            report.append(f"Total: {etg_specialty} eTG citations")
            report.append("")
            report.append("Sample eTG specialty citations:")
            for citation in self.results['etg_specialty_citations'][:10]:
                report.append(f"   - {citation['citation']}")

        report.append("")
        report.append("=" * 80)

        if total_compliant_pct >= 95:
            report.append("✅ VALIDATION PASSED - Citation compliance >=95%")
        elif total_compliant_pct >= 90:
            report.append("⚠️  VALIDATION WARNING - Citation compliance 90-95%")
        else:
            report.append("❌ VALIDATION FAILED - Citation compliance <90%")

        report.append("=" * 80)

        return "\n".join(report)

def main():
    """Main validation function"""

    print("🔍 Validating citation compliance with PROJECT_CONSTRAINTS.md Section 1.4...")
    print()

    validator = CitationValidator()

    # Scan all markdown files
    osce_dir = Path('ICRP_OSCE_Preparation')
    md_files = list(osce_dir.rglob('*.md'))

    print(f"📂 Checking {len(md_files)} files...")
    print()

    file_results = []

    for md_file in md_files:
        file_stats = validator.validate_file(md_file)
        if file_stats:
            file_results.append(file_stats)
            validator.results['files_checked'] += 1

    # Generate report
    report = validator.generate_report()
    print(report)

    # Save detailed JSON report
    detailed_report = {
        'summary': {
            'total_citations': validator.results['total_citations'],
            'exact_references': len(validator.results['compliant_citations']),
            'etg_with_specialty': len(validator.results['etg_specialty_citations']),
            'non_compliant': len(validator.results['non_compliant_citations']),
            'compliance_percentage': ((len(validator.results['compliant_citations']) +
                                       len(validator.results['etg_specialty_citations'])) /
                                      validator.results['total_citations'] * 100)
                                     if validator.results['total_citations'] > 0 else 0,
            'files_checked': validator.results['files_checked']
        },
        'non_compliant_citations': validator.results['non_compliant_citations'],
        'etg_specialty_citations': validator.results['etg_specialty_citations']
    }

    with open('citation_validation_report.json', 'w') as f:
        json.dump(detailed_report, f, indent=2)

    print()
    print("📝 Detailed report saved to: citation_validation_report.json")

if __name__ == "__main__":
    main()
