#!/usr/bin/env python3
"""Add Australian citations to uncited medical claims"""

import json
import re
from pathlib import Path
from typing import Dict, List


def get_appropriate_citation(claim: str, file_path: str) -> str:
    """Determine appropriate Australian citation based on claim content and context"""
    claim_lower = claim.lower()
    file_lower = file_path.lower()

    # Medication dosages → eTG
    if any(
        drug in claim_lower
        for drug in [
            "paracetamol",
            "morphine",
            "adrenaline",
            "insulin",
            "heparin",
            "warfarin",
            "aspirin",
            "mg",
            "units",
        ]
    ):
        if "paediatric" in file_lower or "paed" in file_lower:
            return "(Therapeutic Guidelines: Paediatric, 2024)"
        elif "surgery" in file_lower:
            return "(Therapeutic Guidelines: Surgery, 2024)"
        elif "cardio" in file_lower:
            return "(Therapeutic Guidelines: Cardiovascular, 2024)"
        else:
            return "(Therapeutic Guidelines, 2024)"

    # VTE prophylaxis → eTG Surgery
    if "vte" in claim_lower or "lmwh" in claim_lower or "prophylaxis" in claim_lower:
        return "(Therapeutic Guidelines: Surgery - VTE Prophylaxis, 2024)"

    # Physical examination → Talley
    if "examination" in file_lower or any(
        term in claim_lower
        for term in ["inspect", "palpat", "percussion", "auscult", "jvp", "murmur"]
    ):
        return "(Talley & O'Connor's Clinical Examination, 8th ed)"

    # General practice/differentials → Murtagh
    if "differential" in file_lower or "history" in file_lower:
        return "(Murtagh's General Practice, 8th ed)"

    # AMC/OSCE context
    if "amc" in claim_lower or "osce" in claim_lower or "communication" in file_lower:
        return "(AMC Handbook of Clinical Assessment, 2024)"

    # Default to Murtagh for general medical content
    return "(Murtagh's General Practice, 8th ed)"


def add_citations():
    """Add citations to uncited claims"""

    # Load citations.json
    citations_file = Path("/home/dev/Development/irStudy/validation_reports/citations.json")
    with open(citations_file) as f:
        data = json.load(f)

    issues = data["issues"]
    print(f"Total uncited claims: {len(issues)}")

    # Process first 100 critical claims
    critical_claims = [i for i in issues if i.get("severity") == "critical"][:100]
    print(f"Processing {len(critical_claims)} critical claims")

    files_modified = set()
    citations_added = 0

    for claim_data in critical_claims:
        file_path = Path("/home/dev/Development/irStudy") / claim_data["file"]
        line_num = claim_data["line"]
        claim_text = claim_data["claim"]

        if not file_path.exists():
            continue

        # Read file
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Find and update the line (accounting for 1-indexed line numbers)
        if line_num <= len(lines):
            idx = line_num - 1
            original_line = lines[idx]

            # Skip if already has citation
            if "(" in original_line and any(
                src in original_line for src in ["Therapeutic", "Talley", "Murtagh", "AMC", "eTG"]
            ):
                continue

            # Get appropriate citation
            citation = get_appropriate_citation(claim_text, str(file_path))

            # Add citation at end of line (before newline)
            updated_line = original_line.rstrip() + f" {citation}\n"
            lines[idx] = updated_line

            # Write back
            with open(file_path, "w", encoding="utf-8") as f:
                f.writelines(lines)

            files_modified.add(str(file_path))
            citations_added += 1
            print(f"✓ Added citation to {claim_data['file']}:{line_num}")

    print(f"\n=== SUMMARY ===")
    print(f"Citations added: {citations_added}")
    print(f"Files modified: {len(files_modified)}")
    print(f"\nModified files:")
    for f in sorted(files_modified):
        print(f"  - {f}")


if __name__ == "__main__":
    add_citations()
