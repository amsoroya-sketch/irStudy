#!/usr/bin/env python3
"""
Citation Extractor for ICRP OSCE Medical Education Files
Identifies uncited medical claims requiring citations from Australian sources.
"""

import re
import json
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass, asdict
from enum import Enum


class Severity(Enum):
    """Severity levels for uncited claims"""

    CRITICAL = "critical"  # Drug dosages, clinical guidelines
    IMPORTANT = "important"  # Diagnostic criteria, red flags
    MINOR = "minor"  # General medical statements


@dataclass
class UncitedClaim:
    """Represents an uncited medical claim"""

    file: str
    line: int
    claim: str
    severity: str
    category: str
    context: str  # Surrounding text for RAG query


class CitationExtractor:
    """Extract uncited medical claims from markdown files"""

    # Citation patterns to detect existing citations
    CITATION_PATTERNS = [
        r"\(Therapeutic Guidelines:.*?\d{4}\)",
        r"\(eTG.*?\d{4}\)",
        r"\(Talley.*?Clinical Examination.*?\)",
        r"\(Murtagh.*?General Practice.*?\)",
        r"\(AMC Handbook.*?\)",
        r"\(PBS:.*?\)",
        r"\(NSW Health.*?\)",
        r"\(\w+\s+et al\.?,?\s+\d{4}\)",
        r"\[\d+\]",  # Numbered references
    ]

    # Patterns for CRITICAL severity claims
    CRITICAL_PATTERNS = [
        # Drug dosages
        r"\b\d+\s*(?:mg|g|mL|L|units?|mcg|microgram)\b.*?\b(?:PO|IV|IM|SC|PR|SL|subcut|oral|intravenous)\b",
        r"\b(?:paracetamol|aspirin|morphine|adrenaline|salbutamol|GTN|insulin|heparin|warfarin|metformin|atorvastatin)\b.*?\b\d+\s*(?:mg|g|mL|units?)\b",
        # Vital signs ranges and thresholds
        r"\b(?:HR|heart rate|BP|blood pressure|RR|respiratory rate|SpO2|oxygen saturation|temp|temperature)\b.*?\b\d+\s*(?:-|to)\s*\d+\b",
        r"\b(?:systolic|diastolic)\b.*?\b\d+\s*mmHg\b",
        # Clinical guidelines and protocols
        r"\b(?:STEMI|stroke|sepsis|DKA|anaphylaxis|trauma)\s+(?:protocol|pathway|guideline|management)\b",
        r"\bGRACE score\b",
        r"\bNIHSS\b",
        r"\bqSOFA\b",
        r"\bAPGAR\b",
        r"\bGCS\b.*?\b\d+\b",
    ]

    # Patterns for IMPORTANT severity claims
    IMPORTANT_PATTERNS = [
        # Diagnostic criteria
        r"\b(?:diagnostic criteria|diagnosis requires|defined as)\b",
        r"\b(?:positive|negative) if\b.*?\b\d+\b",
        # Red flags and warning signs
        r"\b(?:red flag|warning sign|emergency|urgent|immediate)\b",
        r"\b(?:contraindication|absolute contraindication|relative contraindication)\b",
        # Time-critical thresholds
        r"\bwithin\s+\d+\s+(?:minutes|hours|days)\b",
        r"\bdoor-to-(?:balloon|needle|CT)\b",
        # Investigation thresholds
        r"\b(?:troponin|D-dimer|lactate|WCC|white cell count|CRP|ESR)\b.*?\b(?:elevated|raised|>|<)\s*\d+\b",
    ]

    # Patterns for MINOR severity claims
    MINOR_PATTERNS = [
        # General medical statements
        r"\b(?:common|rare|typical|usual|frequently|often|sometimes)\s+(?:cause|presentation|symptom|sign)\b",
        r"\b(?:most|least)\s+(?:common|likely|frequent)\b",
        r"\b(?:incidence|prevalence|mortality|morbidity)\b",
    ]

    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.uncited_claims: List[UncitedClaim] = []

    def has_citation(self, line: str) -> bool:
        """Check if a line already has a citation"""
        for pattern in self.CITATION_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                return True
        return False

    def get_severity(self, text: str) -> Severity:
        """Determine severity of uncited claim"""
        # Check CRITICAL patterns first
        for pattern in self.CRITICAL_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return Severity.CRITICAL

        # Check IMPORTANT patterns
        for pattern in self.IMPORTANT_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return Severity.IMPORTANT

        # Check MINOR patterns
        for pattern in self.MINOR_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return Severity.MINOR

        return Severity.MINOR  # Default

    def categorize_claim(self, text: str) -> str:
        """Categorize the type of medical claim"""
        text_lower = text.lower()

        if any(
            drug in text_lower
            for drug in ["paracetamol", "aspirin", "morphine", "medication", "drug", "mg", "dose"]
        ):
            return "medication"
        elif any(term in text_lower for term in ["bp", "hr", "rr", "spo2", "vital", "mmhg"]):
            return "vital_signs"
        elif any(
            term in text_lower for term in ["stemi", "stroke", "protocol", "guideline", "pathway"]
        ):
            return "clinical_guideline"
        elif any(term in text_lower for term in ["diagnostic", "criteria", "diagnosis"]):
            return "diagnostic_criteria"
        elif any(
            term in text_lower for term in ["red flag", "warning", "emergency", "contraindication"]
        ):
            return "safety"
        elif any(
            term in text_lower
            for term in ["examination", "inspect", "palpate", "auscult", "percuss"]
        ):
            return "examination"
        elif any(
            term in text_lower
            for term in ["investigation", "test", "imaging", "pathology", "ecg", "xray"]
        ):
            return "investigation"
        else:
            return "general"

    def extract_claims_from_file(self, file_path: Path) -> None:
        """Extract uncited claims from a single file"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            relative_path = str(file_path.relative_to(self.base_dir))

            for i, line in enumerate(lines, start=1):
                line = line.strip()

                # Skip empty lines, headers, code blocks, tables
                if (
                    not line
                    or line.startswith("#")
                    or line.startswith("```")
                    or line.startswith("|")
                ):
                    continue

                # Skip lines that already have citations
                if self.has_citation(line):
                    continue

                # Check if line contains medical content requiring citation
                severity = self.get_severity(line)

                # Only extract claims with identifiable severity markers
                if any(
                    re.search(p, line, re.IGNORECASE)
                    for p in self.CRITICAL_PATTERNS + self.IMPORTANT_PATTERNS + self.MINOR_PATTERNS
                ):
                    # Get context (current line + previous and next lines)
                    context_lines = []
                    if i > 1:
                        context_lines.append(lines[i - 2].strip())
                    context_lines.append(line)
                    if i < len(lines):
                        context_lines.append(lines[i].strip())
                    context = " ".join(context_lines)

                    category = self.categorize_claim(line)

                    claim = UncitedClaim(
                        file=relative_path,
                        line=i,
                        claim=line,
                        severity=severity.value,
                        category=category,
                        context=context,
                    )

                    self.uncited_claims.append(claim)

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    def extract_all_claims(self) -> List[UncitedClaim]:
        """Extract uncited claims from all OSCE preparation files"""
        osce_dir = self.base_dir / "ICRP_OSCE_Preparation"

        if not osce_dir.exists():
            raise FileNotFoundError(f"OSCE directory not found: {osce_dir}")

        # Get all markdown files
        md_files = list(osce_dir.rglob("*.md"))

        print(f"Found {len(md_files)} markdown files")

        for md_file in md_files:
            print(f"Processing: {md_file.name}")
            self.extract_claims_from_file(md_file)

        return self.uncited_claims

    def generate_report(self, output_file: str) -> Dict:
        """Generate JSON report of uncited claims"""
        # Sort by severity (critical first)
        severity_order = {
            Severity.CRITICAL.value: 0,
            Severity.IMPORTANT.value: 1,
            Severity.MINOR.value: 2,
        }

        sorted_claims = sorted(
            self.uncited_claims, key=lambda c: (severity_order.get(c.severity, 3), c.file, c.line)
        )

        # Convert to dict format
        claims_dict = [asdict(claim) for claim in sorted_claims]

        # Generate statistics
        stats = {
            "total_claims": len(sorted_claims),
            "by_severity": {
                "critical": sum(1 for c in sorted_claims if c.severity == Severity.CRITICAL.value),
                "important": sum(
                    1 for c in sorted_claims if c.severity == Severity.IMPORTANT.value
                ),
                "minor": sum(1 for c in sorted_claims if c.severity == Severity.MINOR.value),
            },
            "by_category": {},
            "by_file": {},
        }

        # Count by category
        for claim in sorted_claims:
            stats["by_category"][claim.category] = stats["by_category"].get(claim.category, 0) + 1
            stats["by_file"][claim.file] = stats["by_file"].get(claim.file, 0) + 1

        report = {"statistics": stats, "claims": claims_dict}

        # Save to file
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\n=== CITATION EXTRACTION REPORT ===")
        print(f"Total uncited claims: {stats['total_claims']}")
        print(f"\nBy Severity:")
        print(f"  CRITICAL:   {stats['by_severity']['critical']}")
        print(f"  IMPORTANT:  {stats['by_severity']['important']}")
        print(f"  MINOR:      {stats['by_severity']['minor']}")
        print(f"\nBy Category:")
        for category, count in sorted(
            stats["by_category"].items(), key=lambda x: x[1], reverse=True
        ):
            print(f"  {category}: {count}")
        print(f"\nReport saved to: {output_path}")

        return report


def main():
    """Main execution"""
    base_dir = "/home/dev/Development/irStudy"
    output_file = "/home/dev/Development/irStudy/validation_reports/citations.json"

    extractor = CitationExtractor(base_dir)
    extractor.extract_all_claims()
    report = extractor.generate_report(output_file)

    return report


if __name__ == "__main__":
    main()
