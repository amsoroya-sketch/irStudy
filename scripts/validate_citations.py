#!/usr/bin/env python3
"""
Citation Validator
Verifies that all medical claims have proper citations

Features:
- Detect uncited medical claims (dosages, differentials, statistics)
- Verify citation format compliance
- Check citation sources are acceptable (eTG, Murtagh, AMC, Talley)
- Flag suspicious claims without evidence
"""

import re
import logging
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass, field
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class CitationIssue:
    """Represents a citation issue"""
    file_path: str
    line_number: int
    issue_type: str  # 'missing_citation', 'invalid_source', 'weak_citation'
    claim: str
    existing_citation: Optional[str] = None
    severity: str = 'important'  # 'critical', 'important', 'minor'


@dataclass
class CitationReport:
    """Citation validation report"""
    files_scanned: int = 0
    claims_found: int = 0
    cited_claims: int = 0
    uncited_claims: int = 0
    invalid_citations: int = 0
    citation_coverage: float = 0.0
    issues: List[CitationIssue] = field(default_factory=list)


class CitationValidator:
    """
    Validates medical content citations.

    Based on PROJECT_CONSTRAINTS.md citation requirements.
    """

    # Acceptable Australian sources
    ACCEPTABLE_SOURCES = {
        'etg', 'therapeutic guidelines', 'murtagh', 'talley', 'o\'connor',
        'amc', 'harrison', 'oxford', 'kemh', 'ahpra', 'nsw health',
        'racgp', 'racp', 'anzca', 'ranzcp', 'ranzcog',
        'churchill', 'nelson', 'davidson', 'kumar'
    }

    # Patterns that indicate medical claims requiring citation
    CLAIM_PATTERNS = {
        'dosage': r'\d+[-–]?\d*\s*(?:mg|g|mcg|μg|mL|units?|IU)\s*(?:\/\s*(?:kg|day|dose|m2))?\s+(?:once\s+)?(?:daily|BD|TDS|QID|QD|PRN|stat|every|q\d+h|twice|three times|four times)',
        'percentage': r'\d+[-–]?\d*%',
        'sensitivity_specificity': r'(?:sensitivity|specificity|PPV|NPV|accuracy)(?:\s+of)?\s+\d+[-–]?\d*%',
        'statistics': r'(?:prevalence|incidence|mortality|morbidity|risk)(?:\s+of)?\s+\d+',
        'guideline': r'(?:first-line|second-line|recommended|indicated|contraindicated|preferred)',
        'evidence_level': r'(?:level\s+[IVXABC]|grade\s+[ABC]|class\s+[IVX])\s+evidence',
    }

    # Citation format patterns
    CITATION_PATTERNS = [
        r'\(.*?(?:etg|therapeutic|murtagh|talley|amc|harrison|kemh).*?\)',  # (Source Name)
        r'\[.*?(?:etg|therapeutic|murtagh|talley|amc|harrison|kemh).*?\]',  # [Source Name]
        r'(?:etg|therapeutic|murtagh|talley|amc|harrison|kemh).*?(?:p\.\s*\d+|\d{4})',  # Source p.123 or Source 2024
    ]

    def __init__(self, strict_mode: bool = True):
        """
        Initialize citation validator.

        Args:
            strict_mode: If True, enforce strict citation requirements
        """
        self.strict_mode = strict_mode
        self.report = CitationReport()

    def extract_claims(self, line: str) -> List[Tuple[str, str]]:
        """
        Extract medical claims from a line that require citation.

        Returns:
            List of (claim_type, claim_text) tuples
        """
        claims = []

        for claim_type, pattern in self.CLAIM_PATTERNS.items():
            matches = re.finditer(pattern, line, re.IGNORECASE)
            for match in matches:
                # Get context around the match (±30 chars)
                start = max(0, match.start() - 30)
                end = min(len(line), match.end() + 30)
                context = line[start:end].strip()
                claims.append((claim_type, context))

        return claims

    def find_citation(self, line: str) -> Optional[str]:
        """
        Find citation in a line.

        Returns:
            Citation text if found, None otherwise
        """
        for pattern in self.CITATION_PATTERNS:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                return match.group(0)

        return None

    def is_valid_source(self, citation: str) -> bool:
        """
        Check if citation uses an acceptable source.

        Returns:
            True if source is acceptable
        """
        citation_lower = citation.lower()
        return any(source in citation_lower for source in self.ACCEPTABLE_SOURCES)

    def validate_file(self, file_path: Path) -> List[CitationIssue]:
        """
        Validate citations in a file.

        Args:
            file_path: Path to markdown file

        Returns:
            List of citation issues
        """
        issues = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, 1):
                # Skip headers, code blocks, and comments
                if line.startswith('#') or line.startswith('```') or line.startswith('<!--'):
                    continue

                # Extract claims from this line
                claims = self.extract_claims(line)

                if not claims:
                    continue

                # Check if line has citation
                citation = self.find_citation(line)

                for claim_type, claim_text in claims:
                    self.report.claims_found += 1

                    if citation:
                        self.report.cited_claims += 1

                        # Check if citation source is valid
                        if self.strict_mode and not self.is_valid_source(citation):
                            issues.append(CitationIssue(
                                file_path=str(file_path),
                                line_number=line_num,
                                issue_type='invalid_source',
                                claim=claim_text,
                                existing_citation=citation,
                                severity='important'
                            ))
                            self.report.invalid_citations += 1

                    else:
                        self.report.uncited_claims += 1

                        # Determine severity based on claim type
                        if claim_type in ['dosage', 'guideline']:
                            severity = 'critical'
                        elif claim_type in ['sensitivity_specificity', 'statistics']:
                            severity = 'important'
                        else:
                            severity = 'minor'

                        issues.append(CitationIssue(
                            file_path=str(file_path),
                            line_number=line_num,
                            issue_type='missing_citation',
                            claim=claim_text,
                            severity=severity
                        ))

        except Exception as e:
            logger.error(f"Error validating {file_path}: {e}")

        return issues

    def validate_directory(self, directory: Path, pattern: str = "*.md") -> CitationReport:
        """
        Validate all files in a directory.

        Args:
            directory: Directory to scan
            pattern: File pattern

        Returns:
            CitationReport
        """
        files = list(directory.glob(pattern))
        logger.info(f"Scanning {len(files)} files for citation compliance")

        all_issues = []

        for file_path in files:
            if file_path.name.startswith('.'):
                continue

            issues = self.validate_file(file_path)
            all_issues.extend(issues)

        # Generate report
        self.report.files_scanned = len(files)
        self.report.issues = all_issues

        # Calculate citation coverage
        if self.report.claims_found > 0:
            self.report.citation_coverage = (self.report.cited_claims / self.report.claims_found) * 100

        return self.report

    def generate_report_markdown(self, output_path: Path):
        """Generate markdown report"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# Citation Validation Report\n\n")

            f.write("## Summary\n\n")
            f.write(f"- **Files Scanned**: {self.report.files_scanned}\n")
            f.write(f"- **Medical Claims Found**: {self.report.claims_found}\n")
            f.write(f"- **Cited Claims**: {self.report.cited_claims}\n")
            f.write(f"- **Uncited Claims**: {self.report.uncited_claims}\n")
            f.write(f"- **Invalid Citations**: {self.report.invalid_citations}\n")
            f.write(f"- **Citation Coverage**: {self.report.citation_coverage:.1f}%\n\n")

            # Group by severity
            critical = [i for i in self.report.issues if i.severity == 'critical']
            important = [i for i in self.report.issues if i.severity == 'important']
            minor = [i for i in self.report.issues if i.severity == 'minor']

            if critical:
                f.write(f"## 🔴 Critical Issues ({len(critical)})\n\n")
                f.write("These are dosages and guidelines that MUST have citations.\n\n")
                for issue in critical:
                    f.write(f"### {Path(issue.file_path).name}:{issue.line_number}\n")
                    f.write(f"- **Claim**: {issue.claim}\n")
                    f.write(f"- **Issue**: {issue.issue_type}\n")
                    if issue.existing_citation:
                        f.write(f"- **Existing Citation**: {issue.existing_citation}\n")
                    f.write(f"- **Action Required**: Add citation from eTG 2024, Murtagh, or AMC sources\n\n")

            if important:
                f.write(f"## 🟡 Important Issues ({len(important)})\n\n")
                for issue in important:
                    f.write(f"- **{Path(issue.file_path).name}:{issue.line_number}**\n")
                    f.write(f"  - Claim: `{issue.claim}`\n")
                    f.write(f"  - Issue: {issue.issue_type}\n\n")

            if minor:
                f.write(f"## 🟢 Minor Issues ({len(minor)})\n\n")
                for issue in minor:
                    f.write(f"- {Path(issue.file_path).name}:{issue.line_number} - {issue.claim}\n")

            # Citation best practices
            f.write("\n## Citation Best Practices\n\n")
            f.write("### Acceptable Sources\n\n")
            f.write("- **Australian Guidelines**: eTG (Therapeutic Guidelines)\n")
            f.write("- **GP Reference**: Murtagh's General Practice 8th Ed\n")
            f.write("- **Clinical Examination**: Talley & O'Connor 8th Ed\n")
            f.write("- **AMC Resources**: AMC Handbook, AMC Anthology\n")
            f.write("- **Specialty Guidelines**: KEMH, RACGP, RACP, etc.\n\n")

            f.write("### Citation Format\n\n")
            f.write("```\n")
            f.write("Metformin 500mg BD, increase to 1g BD (eTG Diabetes 2024)\n")
            f.write("Chest pain differentials (Murtagh GP 8th Ed p.456)\n")
            f.write("Murphy's sign indicates acute cholecystitis (Talley & O'Connor p.234)\n")
            f.write("```\n\n")

        logger.info(f"✓ Report saved to {output_path}")

    def generate_report_json(self, output_path: Path):
        """Generate JSON report"""
        report_dict = {
            'summary': {
                'files_scanned': self.report.files_scanned,
                'claims_found': self.report.claims_found,
                'cited_claims': self.report.cited_claims,
                'uncited_claims': self.report.uncited_claims,
                'invalid_citations': self.report.invalid_citations,
                'citation_coverage': round(self.report.citation_coverage, 2)
            },
            'issues': [
                {
                    'file': i.file_path,
                    'line': i.line_number,
                    'type': i.issue_type,
                    'claim': i.claim,
                    'existing_citation': i.existing_citation,
                    'severity': i.severity
                }
                for i in self.report.issues
            ]
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_dict, f, indent=2, ensure_ascii=False)

        logger.info(f"✓ JSON report saved to {output_path}")


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Validate medical content citations")
    parser.add_argument("directory", help="Directory to scan")
    parser.add_argument("--pattern", default="*.md", help="File pattern (default: *.md)")
    parser.add_argument("--lenient", action="store_true", help="Use lenient mode (don't validate sources)")
    parser.add_argument("--output", default="validation_reports/citations.md", help="Output report path")
    parser.add_argument("--json", help="Also output JSON report to this path")

    args = parser.parse_args()

    # Create validator
    validator = CitationValidator(strict_mode=not args.lenient)

    # Validate directory
    directory = Path(args.directory)
    if not directory.exists():
        logger.error(f"Directory not found: {directory}")
        return

    logger.info(f"🔍 Validating citations in {directory}")
    logger.info(f"Mode: {'LENIENT' if args.lenient else 'STRICT'}")

    report = validator.validate_directory(directory, args.pattern)

    # Generate reports
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    validator.generate_report_markdown(output_path)

    if args.json:
        json_path = Path(args.json)
        json_path.parent.mkdir(parents=True, exist_ok=True)
        validator.generate_report_json(json_path)

    # Print summary
    print("\n" + "="*60)
    print(f"✓ Citation Validation Complete")
    print("="*60)
    print(f"Files Scanned: {report.files_scanned}")
    print(f"Medical Claims Found: {report.claims_found}")
    print(f"Cited Claims: {report.cited_claims}")
    print(f"Uncited Claims: {report.uncited_claims}")
    print(f"Citation Coverage: {report.citation_coverage:.1f}%")
    print(f"\nReport: {output_path}")
    print("="*60)


if __name__ == "__main__":
    main()
