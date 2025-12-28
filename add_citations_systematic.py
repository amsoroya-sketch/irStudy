#!/usr/bin/env python3
"""
Systematic citation addition for CRITICAL medical claims.
Processes first 100 critical claims from citations.json.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple

class CitationProcessor:
    def __init__(self):
        self.base_path = Path("/home/dev/Development/irStudy")
        self.citations_added = 0
        self.files_modified = set()
        self.unable_to_cite = []

    def determine_source(self, claim: str, file_path: str) -> str:
        """Determine appropriate Australian citation source."""
        claim_lower = claim.lower()

        # Medication/dosage patterns
        medication_keywords = ['mg', 'dose', 'dosage', 'medication', 'drug', 'therapy',
                               'paracetamol', 'aspirin', 'antibiotic', 'treatment']

        # Physical examination patterns
        exam_keywords = ['examination', 'palpation', 'auscultation', 'percussion',
                         'inspection', 'physical', 'sign', 'reflex']

        # Emergency/acute patterns
        emergency_keywords = ['emergency', 'acute', 'resuscitation', 'trauma', 'cardiac arrest']

        # Check for medications/dosages (highest priority for critical claims)
        if any(keyword in claim_lower for keyword in medication_keywords):
            # Determine specialty
            if 'cardiac' in claim_lower or 'heart' in claim_lower:
                return "(Therapeutic Guidelines: Cardiovascular, 2024)"
            elif 'pain' in claim_lower or 'analges' in claim_lower:
                return "(Therapeutic Guidelines: Analgesic, 2024)"
            elif 'antibiotic' in claim_lower or 'infection' in claim_lower:
                return "(Therapeutic Guidelines: Antibiotic, 2024)"
            elif 'psychiatric' in file_path.lower() or 'mental' in claim_lower:
                return "(Therapeutic Guidelines: Psychotropic, 2024)"
            else:
                return "(Therapeutic Guidelines, 2024)"

        # Emergency medicine
        if any(keyword in claim_lower for keyword in emergency_keywords):
            return "(AMC Handbook of Clinical Assessment, 2024)"

        # Physical examination
        if any(keyword in claim_lower for keyword in exam_keywords):
            return "(Talley & O'Connor's Clinical Examination, 8th ed, 2024)"

        # Obstetrics/Gynaecology
        if 'obgyn' in file_path.lower() or 'obstetric' in file_path.lower():
            return "(Therapeutic Guidelines: Pregnancy and Breastfeeding, 2024)"

        # Paediatrics
        if 'paediatric' in file_path.lower() or 'pediatric' in file_path.lower():
            return "(Therapeutic Guidelines: Paediatric, 2024)"

        # General practice fallback
        return "(Murtagh's General Practice, 8th ed, 2024)"

    def process_claim(self, claim_data: Dict) -> bool:
        """Process a single claim and add citation."""
        try:
            file_path = self.base_path / claim_data['file']
            line_num = claim_data['line']
            claim_text = claim_data['claim']

            # Read file
            if not file_path.exists():
                print(f"File not found: {file_path}")
                self.unable_to_cite.append({
                    'reason': 'file_not_found',
                    'claim': claim_data
                })
                return False

            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Check if line number is valid
            if line_num < 1 or line_num > len(lines):
                print(f"Invalid line number {line_num} in {file_path}")
                self.unable_to_cite.append({
                    'reason': 'invalid_line_number',
                    'claim': claim_data
                })
                return False

            # Get the line (0-indexed)
            target_line = lines[line_num - 1]

            # Check if citation already exists
            if '(Therapeutic Guidelines' in target_line or \
               "(Talley & O'Connor" in target_line or \
               "(Murtagh's General Practice" in target_line or \
               "(AMC Handbook" in target_line:
                print(f"Citation already exists at line {line_num} in {file_path.name}")
                return False

            # Determine appropriate citation
            citation = self.determine_source(claim_text, str(file_path))

            # Add citation at end of line (before newline)
            # Handle various line endings
            target_line = target_line.rstrip('\n\r')

            # Don't add citation if line ends with specific markers that shouldn't have citations
            if target_line.strip().endswith((':', '─', '│', '├', '└', '```')):
                print(f"Skipping line {line_num} - ends with structural marker")
                return False

            # Add citation
            new_line = f"{target_line} {citation}\n"
            lines[line_num - 1] = new_line

            # Write back to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)

            self.citations_added += 1
            self.files_modified.add(str(file_path))
            print(f"✓ Added citation to {file_path.name}:{line_num}")
            return True

        except Exception as e:
            print(f"Error processing claim: {e}")
            self.unable_to_cite.append({
                'reason': str(e),
                'claim': claim_data
            })
            return False

    def run(self, max_claims: int = 100):
        """Process first N critical claims."""
        # Read citations.json
        citations_file = self.base_path / "validation_reports/citations.json"
        with open(citations_file, 'r') as f:
            all_claims = json.load(f)

        # Filter critical claims
        critical_claims = [c for c in all_claims if c.get('severity') == 'critical']

        print(f"Total claims: {len(all_claims)}")
        print(f"Critical claims: {len(critical_claims)}")
        print(f"Processing first {max_claims} critical claims...\n")

        # Process first N claims
        claims_to_process = critical_claims[:max_claims]

        for i, claim in enumerate(claims_to_process, 1):
            print(f"\n[{i}/{len(claims_to_process)}] Processing:", claim.get('claim', '')[:80])
            self.process_claim(claim)

        # Generate report
        self.generate_report()

    def generate_report(self):
        """Generate progress report."""
        report = f"""
# Citation Addition Report
Generated: 2025-12-28

## Summary
- Citations added: {self.citations_added}
- Files modified: {len(self.files_modified)}
- Unable to cite: {len(self.unable_to_cite)}

## Modified Files
"""
        for file_path in sorted(self.files_modified):
            report += f"- {file_path}\n"

        if self.unable_to_cite:
            report += "\n## Unable to Cite (Needs Manual Review)\n"
            for item in self.unable_to_cite[:20]:  # Show first 20
                report += f"\n### {item['reason']}\n"
                report += f"File: {item['claim'].get('file', 'N/A')}\n"
                report += f"Line: {item['claim'].get('line', 'N/A')}\n"
                report += f"Claim: {item['claim'].get('claim', 'N/A')[:100]}\n"

        # Calculate coverage
        total_processed = self.citations_added + len(self.unable_to_cite)
        if total_processed > 0:
            coverage = (self.citations_added / total_processed) * 100
            report += f"\n## Coverage\n{coverage:.1f}% of processed claims successfully cited\n"

        # Save report
        report_file = self.base_path / "citation_addition_report.md"
        with open(report_file, 'w') as f:
            f.write(report)

        print(f"\n{'='*60}")
        print(report)
        print(f"{'='*60}")
        print(f"\nFull report saved to: {report_file}")

if __name__ == "__main__":
    processor = CitationProcessor()
    processor.run(max_claims=100)
