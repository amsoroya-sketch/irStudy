#!/usr/bin/env python3
"""
RAG Fact-Checking Validator
Cross-checks medical claims against RAG knowledge base with auto-correction

Features:
- Extract medical claims from OSCE content
- Query RAG system with Australian source boosting
- Auto-correct claims with confidence ≥0.85
- Create unverified claim documents for confidence <0.85
- Generate comprehensive validation report
"""

import re
import logging
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
import json
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.rag_query_service import RAGQueryService, RAGVerificationResult

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MedicalClaim:
    """Represents a medical claim to verify"""
    file_path: str
    line_number: int
    claim_type: str  # 'dosage', 'differential', 'red_flag', 'management', 'examination'
    claim_text: str
    context: Dict[str, str] = field(default_factory=dict)
    original_line: str = ""


@dataclass
class RAGValidationIssue:
    """RAG validation issue"""
    claim: MedicalClaim
    rag_result: RAGVerificationResult
    action_taken: str  # 'auto_corrected', 'flagged_unverified', 'verified'
    severity: str  # 'critical', 'important', 'info'


@dataclass
class RAGValidationReport:
    """RAG validation report"""
    files_scanned: int = 0
    claims_extracted: int = 0
    rag_verified: int = 0
    auto_corrected: int = 0
    unverified_claims: int = 0
    high_confidence_matches: int = 0
    low_confidence_matches: int = 0
    australian_sources_used: int = 0
    average_confidence: float = 0.0
    issues: List[RAGValidationIssue] = field(default_factory=list)
    corrections_applied: List[Dict] = field(default_factory=list)
    unverified_documents_created: List[str] = field(default_factory=list)


class RAGFactValidator:
    """
    RAG-powered fact validator with auto-correction.

    Uses RAGQueryService to verify and auto-correct medical claims.
    """

    # Claim extraction patterns
    CLAIM_PATTERNS = {
        'dosage': r'(?:First-line|Second-line|Treatment|Dose|Dosage|Give|Administer):?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(\d+[-–]?\d*\s*(?:mg|g|mcg|mL|units?)\s*(?:\/\s*(?:kg|day|dose))?\s+(?:once\s+)?(?:daily|BD|TDS|QID|stat|PRN))',
        'differential': r'(?:Differential|Consider|Top\s+\d+):?\s*([A-Z][^\.!?\n]{10,100})',
        'red_flag': r'(?:Red flag|Warning|Call 000|Emergency|Urgent):?\s*([A-Z][^\.!?\n]{10,150})',
        'management': r'(?:Management|Treat|Investigate|Refer):?\s*([A-Z][^\.!?\n]{10,200})',
        'examination': r'(?:Examination|Inspect|Palpate|Auscultate|Percuss):?\s*([A-Z][^\.!?\n]{10,150})',
    }

    AUTO_CORRECT_THRESHOLD = 0.85
    VERIFICATION_THRESHOLD = 0.70

    def __init__(
        self,
        auto_correct: bool = True,
        unverified_claims_dir: Optional[Path] = None
    ):
        """
        Initialize RAG fact validator.

        Args:
            auto_correct: Enable auto-correction for high-confidence matches
            unverified_claims_dir: Directory to create unverified claim documents
        """
        self.auto_correct = auto_correct
        self.unverified_claims_dir = unverified_claims_dir or Path("validation_reports/unverified_claims")
        self.unverified_claims_dir.mkdir(parents=True, exist_ok=True)

        # Initialize RAG service
        logger.info("Initializing RAG Query Service...")
        self.rag = RAGQueryService()

        self.report = RAGValidationReport()
        self.corrections_log = []

    def extract_specialty_from_path(self, file_path: Path) -> str:
        """Extract specialty from file path"""
        specialty_map = {
            'medicine': 'medicine',
            'surgery': 'surgery',
            'psychiatry': 'psychiatry',
            'obgyn': 'obgyn',
            'paediatrics': 'paediatrics',
            'ethics': 'communication',
            'communication': 'communication'
        }

        path_str = str(file_path).lower()
        for key, specialty in specialty_map.items():
            if key in path_str:
                return specialty

        return 'general'

    def extract_claims(self, file_path: Path) -> List[MedicalClaim]:
        """
        Extract medical claims from a file.

        Returns:
            List of MedicalClaim objects
        """
        claims = []
        specialty = self.extract_specialty_from_path(file_path)

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, 1):
                # Skip headers, code blocks
                if line.startswith('#') or line.startswith('```'):
                    continue

                # Try each claim pattern
                for claim_type, pattern in self.CLAIM_PATTERNS.items():
                    matches = re.finditer(pattern, line, re.IGNORECASE)
                    for match in matches:
                        claim_text = match.group(0).strip()

                        claim = MedicalClaim(
                            file_path=str(file_path),
                            line_number=line_num,
                            claim_type=claim_type,
                            claim_text=claim_text,
                            context={'specialty': specialty},
                            original_line=line.strip()
                        )
                        claims.append(claim)

        except Exception as e:
            logger.error(f"Error extracting claims from {file_path}: {e}")

        return claims

    def verify_claim(self, claim: MedicalClaim) -> RAGVerificationResult:
        """
        Verify a claim using RAG system.

        Returns:
            RAGVerificationResult
        """
        # Choose verification method based on claim type
        if claim.claim_type == 'dosage':
            # Extract drug name and indication
            drug_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+\d+', claim.claim_text)
            if drug_match:
                drug_name = drug_match.group(1)
                return self.rag.find_correct_dosage(drug_name, claim.context.get('specialty', 'general'))

        elif claim.claim_type == 'differential':
            # Extract presentation and differential
            return self.rag.verify_differential(
                presentation=claim.context.get('specialty', 'unknown'),
                differential=claim.claim_text
            )

        elif claim.claim_type == 'examination':
            # Verify examination technique
            return self.rag.verify_examination_technique(
                system=claim.context.get('specialty', 'general'),
                technique=claim.claim_text
            )

        else:
            # Generic claim verification
            return self.rag.verify_claim_with_correction(claim.claim_text, claim.context)

    def create_unverified_document(
        self,
        claim: MedicalClaim,
        rag_result: RAGVerificationResult
    ) -> str:
        """
        Create individual document for unverified claim.

        Returns:
            Path to created document
        """
        # Create specialty subdirectory
        specialty = claim.context.get('specialty', 'general')
        specialty_dir = self.unverified_claims_dir / specialty.capitalize()
        specialty_dir.mkdir(parents=True, exist_ok=True)

        # Generate filename
        file_name = Path(claim.file_path).stem
        claim_id = f"{file_name}_claim_{len(list(specialty_dir.glob('*.md'))) + 1:03d}"
        doc_path = specialty_dir / f"{claim_id}.md"

        # Generate document
        with open(doc_path, 'w', encoding='utf-8') as f:
            f.write(f"# Unverified Claim: {claim_id}\n\n")
            f.write(f"**Source File**: {Path(claim.file_path).name}  \n")
            f.write(f"**Line**: {claim.line_number}  \n")
            f.write(f"**Date Flagged**: {datetime.now().strftime('%Y-%m-%d')}  \n")
            f.write(f"**RAG Confidence**: {rag_result.confidence:.2f} (BELOW THRESHOLD 0.85)\n\n")
            f.write("---\n\n")

            f.write("## Original Claim\n\n")
            f.write(f"> {claim.claim_text}\n\n")

            # Extract original citation if present
            citation_match = re.search(r'\([^)]*(?:etg|murtagh|talley|amc|harrison)[^)]*\)', claim.original_line, re.IGNORECASE)
            if citation_match:
                f.write(f"**Original Citation in File**: {citation_match.group(0)}\n\n")

            f.write("---\n\n")

            f.write("## RAG Verification Attempt\n\n")
            f.write(f"**Query**: \"{claim.claim_text[:100]}...\"\n\n")
            f.write("**Top RAG Matches**:\n\n")

            for i, source in enumerate(rag_result.sources[:3], 1):
                australian_flag = " 🇦🇺" if source.get('is_australian', False) else ""
                f.write(f"{i}. **{source['source']}** p.{source['page']}{australian_flag} [Score: {source['score']:.2f}]\n")
                f.write(f"   - {source.get('text_preview', 'No preview')}\n\n")

            f.write("---\n\n")

            f.write("## Why Unverified\n\n")
            f.write(f"- ❌ RAG confidence ({rag_result.confidence:.2f}) below threshold (0.85)\n")
            if rag_result.reasoning:
                f.write(f"- ℹ️ {rag_result.reasoning}\n")
            f.write("\n")

            f.write("---\n\n")

            f.write("## Recommended Action\n\n")
            f.write("**Options**:\n")
            f.write("1. ✅ **ACCEPT** - If you can verify the claim from the original citation\n")
            f.write("2. ⚠️ **MODIFY** - Update claim based on RAG evidence above\n")
            f.write("3. 🔍 **RESEARCH** - Add missing source to RAG database\n")
            f.write("4. ❌ **REMOVE** - If claim cannot be verified\n\n")

            f.write("---\n\n")

            f.write("## Manual Review Required\n\n")
            f.write("**Reviewer**: _____________  \n")
            f.write("**Date**: _____________  \n")
            f.write("**Decision**: [ ] Accept  [ ] Modify  [ ] Research  [ ] Remove  \n")
            f.write("**Notes**: \n\n")
            f.write("_____________________________________________\n")

        logger.info(f"Created unverified claim document: {doc_path.name}")
        return str(doc_path)

    def apply_correction(
        self,
        file_path: Path,
        line_number: int,
        original: str,
        corrected: str
    ) -> bool:
        """
        Apply auto-correction to a file.

        Returns:
            True if successful
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            if line_number <= len(lines):
                original_line = lines[line_number - 1]
                corrected_line = original_line.replace(original, corrected)

                if corrected_line != original_line:
                    lines[line_number - 1] = corrected_line

                    # Write back
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.writelines(lines)

                    logger.info(f"✓ Auto-corrected {file_path.name}:{line_number}")
                    return True

        except Exception as e:
            logger.error(f"Error applying correction to {file_path}:{line_number}: {e}")

        return False

    def validate_file(self, file_path: Path) -> List[RAGValidationIssue]:
        """
        Validate a single file with RAG fact-checking.

        Returns:
            List of issues found
        """
        issues = []

        # Extract claims
        claims = self.extract_claims(file_path)
        logger.info(f"Extracted {len(claims)} claims from {file_path.name}")

        for claim in claims:
            self.report.claims_extracted += 1

            # Verify with RAG
            rag_result = self.verify_claim(claim)

            # Update statistics
            if rag_result.verified:
                self.report.rag_verified += 1

            if rag_result.confidence >= self.AUTO_CORRECT_THRESHOLD:
                self.report.high_confidence_matches += 1
            elif rag_result.confidence >= self.VERIFICATION_THRESHOLD:
                self.report.low_confidence_matches += 1

            self.report.australian_sources_used += rag_result.australian_sources_used

            # Determine action
            if rag_result.should_correct and rag_result.corrected and self.auto_correct:
                # AUTO-CORRECT
                success = self.apply_correction(
                    file_path,
                    claim.line_number,
                    claim.claim_text,
                    rag_result.corrected
                )

                if success:
                    self.report.auto_corrected += 1
                    self.report.corrections_applied.append({
                        'file': str(file_path),
                        'line': claim.line_number,
                        'original': claim.claim_text,
                        'corrected': rag_result.corrected,
                        'confidence': rag_result.confidence,
                        'citation': rag_result.citation
                    })

                    issues.append(RAGValidationIssue(
                        claim=claim,
                        rag_result=rag_result,
                        action_taken='auto_corrected',
                        severity='info'
                    ))

            elif rag_result.confidence < self.AUTO_CORRECT_THRESHOLD:
                # CREATE UNVERIFIED DOCUMENT
                doc_path = self.create_unverified_document(claim, rag_result)
                self.report.unverified_claims += 1
                self.report.unverified_documents_created.append(doc_path)

                issues.append(RAGValidationIssue(
                    claim=claim,
                    rag_result=rag_result,
                    action_taken='flagged_unverified',
                    severity='important' if rag_result.confidence < 0.70 else 'minor'
                ))

            else:
                # VERIFIED
                issues.append(RAGValidationIssue(
                    claim=claim,
                    rag_result=rag_result,
                    action_taken='verified',
                    severity='info'
                ))

        return issues

    def validate_directory(self, directory: Path, pattern: str = "*.md") -> RAGValidationReport:
        """
        Validate all files in directory.

        Returns:
            RAGValidationReport
        """
        files = list(directory.glob(pattern))
        logger.info(f"🔍 RAG fact-checking {len(files)} files")
        logger.info(f"Auto-correction: {'ENABLED' if self.auto_correct else 'DISABLED'}")

        all_issues = []

        for file_path in files:
            if file_path.name.startswith('.'):
                continue

            issues = self.validate_file(file_path)
            all_issues.extend(issues)

        # Generate report
        self.report.files_scanned = len(files)
        self.report.issues = all_issues

        # Calculate average confidence
        if self.report.claims_extracted > 0:
            total_confidence = sum(issue.rag_result.confidence for issue in all_issues)
            self.report.average_confidence = total_confidence / len(all_issues)

        return self.report

    def generate_report_markdown(self, output_path: Path):
        """Generate markdown report"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# RAG Fact-Checking Validation Report\n\n")
            f.write(f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            f.write("## Summary\n\n")
            f.write(f"- **Files Scanned**: {self.report.files_scanned}\n")
            f.write(f"- **Claims Extracted**: {self.report.claims_extracted}\n")
            f.write(f"- **RAG Verified**: {self.report.rag_verified}\n")
            f.write(f"- **Auto-Corrected**: {self.report.auto_corrected}\n")
            f.write(f"- **Unverified Claims**: {self.report.unverified_claims}\n")
            f.write(f"- **Average RAG Confidence**: {self.report.average_confidence:.2f}\n")
            f.write(f"- **Australian Sources Used**: {self.report.australian_sources_used}\n\n")

            # Auto-corrections
            if self.report.corrections_applied:
                f.write(f"## Auto-Corrections Applied ({len(self.report.corrections_applied)})\n\n")
                for correction in self.report.corrections_applied[:20]:  # Limit to 20
                    f.write(f"### {Path(correction['file']).name}:{correction['line']}\n")
                    f.write(f"- **Original**: {correction['original']}\n")
                    f.write(f"- **Corrected**: {correction['corrected']}\n")
                    f.write(f"- **Citation**: {correction['citation']}\n")
                    f.write(f"- **Confidence**: {correction['confidence']:.2f}\n\n")

            # Unverified claims
            if self.report.unverified_documents_created:
                f.write(f"## Unverified Claims ({len(self.report.unverified_documents_created)})\n\n")
                f.write("Individual documents created for manual review:\n\n")
                for doc_path in self.report.unverified_documents_created[:20]:
                    f.write(f"- [{Path(doc_path).name}]({doc_path})\n")

        logger.info(f"✓ Report saved to {output_path}")

    def generate_report_json(self, output_path: Path):
        """Generate JSON report"""
        report_dict = {
            'summary': {
                'files_scanned': self.report.files_scanned,
                'claims_extracted': self.report.claims_extracted,
                'rag_verified': self.report.rag_verified,
                'auto_corrected': self.report.auto_corrected,
                'unverified_claims': self.report.unverified_claims,
                'average_confidence': round(self.report.average_confidence, 2),
                'australian_sources_used': self.report.australian_sources_used
            },
            'corrections_applied': self.report.corrections_applied,
            'unverified_documents': self.report.unverified_documents_created
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_dict, f, indent=2, ensure_ascii=False)

        logger.info(f"✓ JSON report saved to {output_path}")


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="RAG-powered medical content fact-checking")
    parser.add_argument("directory", help="Directory to scan")
    parser.add_argument("--pattern", default="*.md", help="File pattern (default: *.md)")
    parser.add_argument("--no-auto-correct", action="store_true", help="Disable auto-correction")
    parser.add_argument("--unverified-dir", default="validation_reports/unverified_claims", help="Unverified claims directory")
    parser.add_argument("--output", default="validation_reports/rag_validation.md", help="Output report path")
    parser.add_argument("--json", help="Also output JSON report to this path")

    args = parser.parse_args()

    # Create validator
    validator = RAGFactValidator(
        auto_correct=not args.no_auto_correct,
        unverified_claims_dir=Path(args.unverified_dir)
    )

    # Validate directory
    directory = Path(args.directory)
    if not directory.exists():
        logger.error(f"Directory not found: {directory}")
        return

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
    print(f"✓ RAG Fact-Checking Validation Complete")
    print("="*60)
    print(f"Files Scanned: {report.files_scanned}")
    print(f"Claims Extracted: {report.claims_extracted}")
    print(f"RAG Verified: {report.rag_verified}")
    print(f"Auto-Corrected: {report.auto_corrected}")
    print(f"Unverified Claims: {report.unverified_claims}")
    print(f"Average Confidence: {report.average_confidence:.2f}")
    print(f"\nReport: {output_path}")
    print(f"Unverified Claims: {args.unverified_dir}/")
    print("="*60)


if __name__ == "__main__":
    main()
