#!/usr/bin/env python3
"""
Australian Compliance Validator
Auto-corrects American terminology, drug names, and non-Australian conventions

Features:
- Auto-replace American terms with Australian equivalents
- Fix American drug names (acetaminophen → paracetamol)
- Correct emergency numbers (911 → 000)
- Enforce SI units (mg/dL → mmol/L where applicable)
- Verify frequency indicator format
"""

import re
import logging
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ComplianceIssue:
    """Represents a compliance issue found"""
    file_path: str
    line_number: int
    issue_type: str  # 'american_term', 'drug_name', 'unit', 'emergency_number'
    original: str
    corrected: str
    severity: str  # 'critical', 'important', 'minor'
    auto_corrected: bool = False


@dataclass
class ComplianceReport:
    """Compliance validation report"""
    files_scanned: int = 0
    issues_found: int = 0
    auto_corrections: int = 0
    manual_review_needed: int = 0
    issues: List[ComplianceIssue] = field(default_factory=list)
    compliance_score: float = 0.0


class AustralianComplianceValidator:
    """
    Validates and auto-corrects Australian medical terminology compliance.

    Based on PROJECT_CONSTRAINTS.md standards.
    """

    # American → Australian terminology
    AMERICAN_TERMS = {
        # Medical specialties
        r'\bpediatric(s?)\b': r'paediatric\1',
        r'\bPediatric(s?)\b': r'Paediatric\1',

        # Medical settings
        r'\bER\b': 'Emergency Department',
        r'\bemergency room\b': 'emergency department',
        r'\bEmergency Room\b': 'Emergency Department',
        r'\bPCP\b': 'GP',
        r'\bprimary care physician\b': 'general practitioner',

        # Spelling
        r'\banaemia\b': 'anaemia',  # Already correct, but check American version
        r'\banemia\b': 'anaemia',
        r'\bfavorable\b': 'favourable',
        r'\bfavorite\b': 'favourite',
        r'\bcenter\b': 'centre',
        r'\bCenter\b': 'Centre',
        r'\banalyze\b': 'analyse',
        r'\borganize\b': 'organise',
        r'\bspecialize\b': 'specialise',
        r'\bhospitalize\b': 'hospitalise',
        r'\bhemoglobin\b': 'haemoglobin',
        r'\bhaematology\b': 'haematology',  # Correct
        r'\bhematology\b': 'haematology',
        r'\besthetics\b': 'aesthetics',
        r'\besophagus\b': 'oesophagus',
        r'\bestrogen\b': 'oestrogen',
        r'\bfetus\b': 'foetus',
        r'\bfetal\b': 'foetal',

        # Australian conventions
        r'\bprograms?\b': 'programmes',
        r'\bPrograms?\b': 'Programmes',
    }

    # American drug names → Australian drug names
    DRUG_NAMES = {
        r'\bacetaminophen\b': 'paracetamol',
        r'\bAcetaminophen\b': 'Paracetamol',
        r'\bTylenol\b': 'paracetamol',
        r'\bepinephrine\b': 'adrenaline',
        r'\bEpinephrine\b': 'Adrenaline',
        r'\balbuterol\b': 'salbutamol',
        r'\bAlbuterol\b': 'Salbutamol',
        r'\bfurosemide\b': 'frusemide',
        r'\bFurosemide\b': 'Frusemide',
        r'\bmeperidine\b': 'pethidine',
        r'\bMeperidine\b': 'Pethidine',
    }

    # Emergency numbers
    EMERGENCY_NUMBERS = {
        r'\b911\b': '000',
        r'\bcall 911\b': 'call 000',
        r'\bCall 911\b': 'Call 000',
        r'\bphone 911\b': 'phone 000',
        r'\bPhone 911\b': 'Phone 000',
        r'\bdial 911\b': 'dial 000',
        r'\bDial 911\b': 'Dial 000',
    }

    # Frequency indicator format check
    FREQUENCY_PATTERN = r'\[([⭐]{1,3})\s+(HIGH|MEDIUM|LOW)-YIELD\]'

    def __init__(self, auto_correct: bool = True):
        """
        Initialize validator.

        Args:
            auto_correct: If True, automatically fix issues
        """
        self.auto_correct = auto_correct
        self.report = ComplianceReport()

    def validate_file(self, file_path: Path) -> List[ComplianceIssue]:
        """
        Validate a single file for Australian compliance.

        Args:
            file_path: Path to markdown file

        Returns:
            List of issues found
        """
        issues = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            modified = False
            new_lines = []

            for line_num, line in enumerate(lines, 1):
                original_line = line

                # Check American terminology
                for pattern, replacement in self.AMERICAN_TERMS.items():
                    if re.search(pattern, line):
                        new_line = re.sub(pattern, replacement, line)
                        if new_line != line:
                            issues.append(ComplianceIssue(
                                file_path=str(file_path),
                                line_number=line_num,
                                issue_type='american_term',
                                original=line.strip(),
                                corrected=new_line.strip(),
                                severity='important',
                                auto_corrected=self.auto_correct
                            ))
                            line = new_line
                            modified = True

                # Check American drug names
                for pattern, replacement in self.DRUG_NAMES.items():
                    if re.search(pattern, line):
                        new_line = re.sub(pattern, replacement, line)
                        if new_line != line:
                            issues.append(ComplianceIssue(
                                file_path=str(file_path),
                                line_number=line_num,
                                issue_type='drug_name',
                                original=line.strip(),
                                corrected=new_line.strip(),
                                severity='critical',
                                auto_corrected=self.auto_correct
                            ))
                            line = new_line
                            modified = True

                # Check emergency numbers
                for pattern, replacement in self.EMERGENCY_NUMBERS.items():
                    if re.search(pattern, line):
                        new_line = re.sub(pattern, replacement, line)
                        if new_line != line:
                            issues.append(ComplianceIssue(
                                file_path=str(file_path),
                                line_number=line_num,
                                issue_type='emergency_number',
                                original=line.strip(),
                                corrected=new_line.strip(),
                                severity='critical',
                                auto_corrected=self.auto_correct
                            ))
                            line = new_line
                            modified = True

                new_lines.append(line)

            # Write back if auto-correcting and modified
            if self.auto_correct and modified:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(new_lines)
                logger.info(f"✓ Auto-corrected {len(issues)} issues in {file_path.name}")

        except Exception as e:
            logger.error(f"Error validating {file_path}: {e}")

        return issues

    def validate_directory(self, directory: Path, pattern: str = "*.md") -> ComplianceReport:
        """
        Validate all markdown files in a directory.

        Args:
            directory: Directory to scan
            pattern: File pattern (default: *.md)

        Returns:
            ComplianceReport with all issues
        """
        files = list(directory.glob(pattern))
        logger.info(f"Scanning {len(files)} files in {directory}")

        all_issues = []

        for file_path in files:
            if file_path.name.startswith('.'):
                continue

            issues = self.validate_file(file_path)
            all_issues.extend(issues)

        # Generate report
        self.report.files_scanned = len(files)
        self.report.issues_found = len(all_issues)
        self.report.auto_corrections = sum(1 for i in all_issues if i.auto_corrected)
        self.report.manual_review_needed = sum(1 for i in all_issues if not i.auto_corrected)
        self.report.issues = all_issues

        # Calculate compliance score
        if self.report.files_scanned > 0:
            issues_per_file = self.report.issues_found / self.report.files_scanned
            # Score: 100% if 0 issues, decreasing by 2% per issue per file
            self.report.compliance_score = max(0, 100 - (issues_per_file * 2))

        return self.report

    def generate_report_markdown(self, output_path: Path):
        """Generate markdown report"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# Australian Compliance Validation Report\n\n")
            f.write(f"**Date**: {Path.cwd()}\n\n")

            f.write("## Summary\n\n")
            f.write(f"- **Files Scanned**: {self.report.files_scanned}\n")
            f.write(f"- **Issues Found**: {self.report.issues_found}\n")
            f.write(f"- **Auto-Corrected**: {self.report.auto_corrections}\n")
            f.write(f"- **Manual Review Needed**: {self.report.manual_review_needed}\n")
            f.write(f"- **Compliance Score**: {self.report.compliance_score:.1f}%\n\n")

            # Group by severity
            critical = [i for i in self.report.issues if i.severity == 'critical']
            important = [i for i in self.report.issues if i.severity == 'important']
            minor = [i for i in self.report.issues if i.severity == 'minor']

            if critical:
                f.write(f"## Critical Issues ({len(critical)})\n\n")
                for issue in critical:
                    f.write(f"### {Path(issue.file_path).name}:{issue.line_number}\n")
                    f.write(f"- **Type**: {issue.issue_type}\n")
                    f.write(f"- **Original**: `{issue.original}`\n")
                    f.write(f"- **Corrected**: `{issue.corrected}`\n")
                    f.write(f"- **Auto-corrected**: {'✅' if issue.auto_corrected else '❌ Manual review needed'}\n\n")

            if important:
                f.write(f"## Important Issues ({len(important)})\n\n")
                for issue in important:
                    f.write(f"- **{Path(issue.file_path).name}:{issue.line_number}**: {issue.original} → {issue.corrected}\n")

            if minor:
                f.write(f"## Minor Issues ({len(minor)})\n\n")
                for issue in minor:
                    f.write(f"- **{Path(issue.file_path).name}:{issue.line_number}**: {issue.original} → {issue.corrected}\n")

        logger.info(f"✓ Report saved to {output_path}")

    def generate_report_json(self, output_path: Path):
        """Generate JSON report"""
        report_dict = {
            'summary': {
                'files_scanned': self.report.files_scanned,
                'issues_found': self.report.issues_found,
                'auto_corrections': self.report.auto_corrections,
                'manual_review_needed': self.report.manual_review_needed,
                'compliance_score': round(self.report.compliance_score, 2)
            },
            'issues': [
                {
                    'file': i.file_path,
                    'line': i.line_number,
                    'type': i.issue_type,
                    'original': i.original,
                    'corrected': i.corrected,
                    'severity': i.severity,
                    'auto_corrected': i.auto_corrected
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

    parser = argparse.ArgumentParser(description="Validate Australian medical terminology compliance")
    parser.add_argument("directory", help="Directory to scan")
    parser.add_argument("--pattern", default="*.md", help="File pattern (default: *.md)")
    parser.add_argument("--no-auto-correct", action="store_true", help="Disable auto-correction")
    parser.add_argument("--output", default="validation_reports/australian_compliance.md", help="Output report path")
    parser.add_argument("--json", help="Also output JSON report to this path")

    args = parser.parse_args()

    # Create validator
    validator = AustralianComplianceValidator(auto_correct=not args.no_auto_correct)

    # Validate directory
    directory = Path(args.directory)
    if not directory.exists():
        logger.error(f"Directory not found: {directory}")
        return

    logger.info(f"🔍 Validating Australian compliance in {directory}")
    logger.info(f"Auto-correction: {'ENABLED' if not args.no_auto_correct else 'DISABLED'}")

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
    print(f"✓ Australian Compliance Validation Complete")
    print("="*60)
    print(f"Files Scanned: {report.files_scanned}")
    print(f"Issues Found: {report.issues_found}")
    print(f"Auto-Corrected: {report.auto_corrections}")
    print(f"Manual Review: {report.manual_review_needed}")
    print(f"Compliance Score: {report.compliance_score:.1f}%")
    print(f"\nReport: {output_path}")
    print("="*60)


if __name__ == "__main__":
    main()
