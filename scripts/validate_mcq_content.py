#!/usr/bin/env python3
"""
MCQ Content Validation Script
Validates MCQ JSON files for placeholder content before database insertion

USAGE:
    python3 scripts/validate_mcq_content.py data/mcqs/[FILE].json

RETURNS:
    Exit 0: All MCQs valid (no placeholders)
    Exit 1: Validation failures detected
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

# Placeholder detection patterns
PLACEHOLDER_PATTERNS = [
    # Question text placeholders
    (r"Clinical scenario for \[.*?\]", "Question: Generic scenario template"),
    (r"Question about \[.*?\]", "Question: Generic question template"),
    (r"A \d+-year-old (?:male|female) presents? (?:to|with) \[.*?\]", "Question: Placeholder location/symptom"),
    (r"\[Topic\]", "Question: [Topic] placeholder"),
    (r"\[Condition\]", "Question: [Condition] placeholder"),
    (r"\[Treatment\]", "Question: [Treatment] placeholder"),

    # Option placeholders
    (r"Option [A-E](?:\s*\(Correct\))?$", "Options: Generic 'Option A' pattern"),
    (r"^[A-E][\.\)]?\s*Option [A-E]", "Options: Lettered option placeholder"),
    (r"^[A-E][\.\)]?\s*\[.*?\]", "Options: Bracketed placeholder"),
    (r"^Answer choice [A-E]", "Options: Answer choice template"),

    # Explanation placeholders
    (r"Explanation based on Australian guidelines for \[.*?\]", "Explanation: Generic guideline template"),
    (r"According to \[Guideline\]", "Explanation: [Guideline] placeholder"),
    (r"The correct answer is based on \[Source\]", "Explanation: [Source] placeholder"),
    (r"See \[Reference\] for details", "Explanation: [Reference] placeholder"),

    # Generic content markers
    (r"TODO:", "Content: TODO marker"),
    (r"PLACEHOLDER", "Content: PLACEHOLDER marker"),
    (r"TBD", "Content: TBD marker"),
    (r"FIXME", "Content: FIXME marker"),
    (r"\[INSERT.*?\]", "Content: [INSERT...] marker"),
]


def validate_mcq_content(mcq_data: Dict, mcq_index: int) -> Tuple[bool, List[str]]:
    """
    Validate MCQ content for placeholder patterns.

    Args:
        mcq_data: MCQ data dictionary
        mcq_index: MCQ index in file (for reporting)

    Returns:
        (is_valid, list_of_errors)
    """
    errors = []
    mcq_id = mcq_data.get('id', f'MCQ-{mcq_index+1:03d}')

    # Extract question components
    question_obj = mcq_data.get('question', {})
    scenario = question_obj.get('scenario', '')
    stem = question_obj.get('stem', '')
    question_text = f"{scenario} {stem}".strip()

    # 1. Check question text length
    if len(question_text) < 100:
        errors.append(f"Question text too short: {len(question_text)} chars (<100 required)")

    # 2. Check question text for placeholders
    for pattern, description in PLACEHOLDER_PATTERNS:
        if re.search(pattern, question_text, re.IGNORECASE):
            errors.append(f"{description} found in question text")

    # 3. Check options
    options = question_obj.get('options', {})
    if not options:
        errors.append("No options provided")
    else:
        for key, value in options.items():
            # Check for placeholder option patterns
            if re.match(r"^Option [A-E]", str(value), re.IGNORECASE):
                errors.append(f"Placeholder option {key}: '{value}'")

            # Check for bracketed placeholders
            if re.search(r"\[.*?\]", str(value)):
                errors.append(f"Bracketed placeholder in option {key}: '{value}'")

    # 4. Check explanation
    explanation = mcq_data.get('explanation', '')
    if isinstance(explanation, dict):
        explanation = explanation.get('text', '')

    if len(explanation.strip()) < 50:
        errors.append(f"Explanation too short: {len(explanation)} chars (<50 required)")

    for pattern, description in PLACEHOLDER_PATTERNS:
        if re.search(pattern, explanation, re.IGNORECASE):
            errors.append(f"{description} found in explanation")

    # 5. Check citations
    citations = mcq_data.get('references', [])
    if not citations or len(citations) == 0:
        errors.append("No citations provided (≥3 required)")
    elif len(citations) < 3:
        errors.append(f"Insufficient citations: {len(citations)}/3 required")

    # Check for placeholder citations
    citation_text = json.dumps(citations)
    if re.search(r"\[Guideline\]|\[Reference\]|\[Source\]", citation_text):
        errors.append("Placeholder citation detected ([Guideline], [Reference], or [Source])")

    # Check for qdrant_point_id in citations
    for i, citation in enumerate(citations):
        if not citation.get('qdrant_point_id'):
            errors.append(f"Citation {i+1} missing qdrant_point_id (required for traceability)")

    # 6. Check for American terminology
    american_terms = {
        'acetaminophen': 'paracetamol',
        'albuterol': 'salbutamol',
        'epinephrine': 'adrenaline',
        'PCP': 'GP',
        'ER': 'ED/A&E',
    }

    full_text = f"{question_text} {explanation}"
    for american, australian in american_terms.items():
        if re.search(rf"\b{american}\b", full_text, re.IGNORECASE):
            errors.append(f"American terminology detected: '{american}' (use '{australian}' instead)")

    return (len(errors) == 0, errors)


def validate_file(filepath: str) -> Tuple[int, int, List[Dict]]:
    """
    Validate all MCQs in a JSON file.

    Args:
        filepath: Path to MCQ JSON file

    Returns:
        (total_mcqs, valid_mcqs, list_of_failures)
    """
    print(f"\n{'='*80}")
    print(f"🔍 MCQ CONTENT VALIDATION")
    print(f"{'='*80}")
    print(f"File: {filepath}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}\n")

    # Load JSON file
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ ERROR: File not found: {filepath}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ ERROR: Invalid JSON: {e}")
        sys.exit(1)

    # Extract MCQs from nested structure
    mcqs_data = data.get('mcqs', data) if isinstance(data, dict) else data

    if not isinstance(mcqs_data, list):
        print(f"❌ ERROR: MCQ data is not a list (type: {type(mcqs_data)})")
        sys.exit(1)

    total_mcqs = len(mcqs_data)
    valid_mcqs = 0
    failures = []

    # Validate each MCQ
    for i, mcq_data in enumerate(mcqs_data):
        mcq_id = mcq_data.get('id', f'MCQ-{i+1:03d}')

        # Skip if already marked as regeneration_failed
        if mcq_data.get('regeneration_failed', False):
            failures.append({
                'id': mcq_id,
                'index': i,
                'errors': ['Marked as regeneration_failed'],
            })
            continue

        # Validate content
        is_valid, errors = validate_mcq_content(mcq_data, i)

        if is_valid:
            valid_mcqs += 1
            print(f"  ✅ {mcq_id}: VALID")
        else:
            failures.append({
                'id': mcq_id,
                'index': i,
                'errors': errors,
            })
            print(f"  ❌ {mcq_id}: FAILED ({len(errors)} errors)")
            for error in errors:
                print(f"      - {error}")

    return total_mcqs, valid_mcqs, failures


def main():
    if len(sys.argv) != 2:
        print("USAGE: python3 scripts/validate_mcq_content.py data/mcqs/[FILE].json")
        sys.exit(1)

    filepath = sys.argv[1]

    # Validate file
    total_mcqs, valid_mcqs, failures = validate_file(filepath)

    # Print summary
    print(f"\n{'='*80}")
    print(f"📊 VALIDATION SUMMARY")
    print(f"{'='*80}")
    print(f"Total MCQs:        {total_mcqs}")
    print(f"Valid MCQs:        {valid_mcqs} ({valid_mcqs/total_mcqs*100:.1f}%)")
    print(f"Failed MCQs:       {len(failures)} ({len(failures)/total_mcqs*100:.1f}%)")
    print(f"{'='*80}\n")

    if len(failures) == 0:
        print("✅ VALIDATION PASSED: All MCQs are valid (no placeholder content detected)")
        print("   This file is ready for database insertion.\n")
        sys.exit(0)
    else:
        print("❌ VALIDATION FAILED: Placeholder content detected")
        print(f"   {len(failures)}/{total_mcqs} MCQs contain placeholder patterns")
        print("\n   REQUIRED ACTION:")
        print("   1. Regenerate failed MCQs using Claude API (NOT local LLMs)")
        print("   2. Re-run validation: python3 scripts/validate_mcq_content.py [FILE].json")
        print("   3. Only insert to database when validation passes\n")

        # Save failure report
        report_path = Path(filepath).with_suffix('.validation_report.json')
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'file': filepath,
                'total_mcqs': total_mcqs,
                'valid_mcqs': valid_mcqs,
                'failed_mcqs': len(failures),
                'failures': failures,
            }, f, indent=2, ensure_ascii=False)

        print(f"   Failure report saved: {report_path}\n")
        sys.exit(1)


if __name__ == '__main__':
    main()
