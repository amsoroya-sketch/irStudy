#!/usr/bin/env python3
"""
Pre-generation validation for psychiatry MCQs.
Ensures generation prompts include all mandatory requirements.

Based on Constraint 15: Psychiatry MCQ Zero-Tolerance Requirements
"""

import json
import sys
from pathlib import Path

MANDATORY_SAFE_T_KEYWORDS = [
    "SAFE-T",
    "Specific plan",
    "Access to means",
    "Feelings",
    "Earlier attempts",
    "Threat"
]

MANDATORY_CRISIS_CONTACTS = [
    "Lifeline 13 11 14",
    "Beyond Blue 1300 224 636"
]

MANDATORY_REFERENCES = [
    "RANZCP",
    "Black Dog Institute",
    "Therapeutic Guidelines"
]

def validate_generation_prompt(prompt: str) -> tuple[bool, list[str]]:
    """Validate that generation prompt includes mandatory content."""
    errors = []

    # Check SAFE-T keywords
    safe_t_present = all(
        keyword.lower() in prompt.lower()
        for keyword in MANDATORY_SAFE_T_KEYWORDS
    )
    if not safe_t_present:
        errors.append("SAFE-T protocol not fully specified in prompt")

    # Check crisis contacts
    crisis_contacts_present = any(
        contact in prompt
        for contact in MANDATORY_CRISIS_CONTACTS
    )
    if not crisis_contacts_present:
        errors.append("Australian crisis contacts not specified in prompt")

    # Check reference requirements
    references_specified = any(
        ref in prompt
        for ref in MANDATORY_REFERENCES
    )
    if not references_specified:
        errors.append("Australian reference guidelines not specified in prompt")

    # Check for anti-pattern: "Unknown" references
    if "Unknown" in prompt:
        errors.append("Prompt allows 'Unknown' references (NOT PERMITTED)")

    return len(errors) == 0, errors

def validate_generated_mcq(mcq: dict) -> tuple[bool, list[str]]:
    """Validate generated MCQ before saving."""
    errors = []

    # Check key_points[0] is SAFE-T
    if not mcq.get("explanation", {}).get("key_points"):
        errors.append("No key_points found in explanation")
    else:
        first_key_point = mcq["explanation"]["key_points"][0]
        if "SAFE-T" not in first_key_point:
            errors.append("SAFE-T is not first key point (MANDATORY)")

    # Check all 5 SAFE-T elements present
    key_points_str = " ".join(mcq.get("explanation", {}).get("key_points", []))
    for element in MANDATORY_SAFE_T_KEYWORDS:
        if element not in key_points_str:
            errors.append(f"SAFE-T element missing: {element}")

    # Check crisis contacts present (for high-risk topics)
    topic = mcq.get("topic", "").lower()
    if any(keyword in topic for keyword in ["depression", "suicide", "psychosis"]):
        crisis_present = any(
            contact in key_points_str
            for contact in MANDATORY_CRISIS_CONTACTS
        )
        if not crisis_present:
            errors.append("Australian crisis contacts missing (required for high-risk topics)")

    # Check references are not "Unknown"
    for ref in mcq.get("references", []):
        if ref.get("title") == "Unknown":
            errors.append("Reference 'Unknown' not permitted (use RANZCP guidelines)")

    return len(errors) == 0, errors

def validate_mcq_file(file_path: Path) -> dict:
    """Validate MCQ file and return results."""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)

        # Handle metadata wrapper (e.g., {"metadata": {...}, "mcqs": [...]})
        if isinstance(data, dict) and "mcqs" in data:
            data = data["mcqs"]

        # Handle both single MCQ and array of MCQs
        if isinstance(data, list):
            results = {"total": len(data), "passed": 0, "failed": 0, "errors": []}
            for idx, mcq in enumerate(data):
                valid, errors = validate_generated_mcq(mcq)
                if valid:
                    results["passed"] += 1
                else:
                    results["failed"] += 1
                    results["errors"].append({
                        "index": idx,
                        "topic": mcq.get("topic", "Unknown"),
                        "errors": errors
                    })
            return results
        else:
            valid, errors = validate_generated_mcq(data)
            return {
                "total": 1,
                "passed": 1 if valid else 0,
                "failed": 0 if valid else 1,
                "errors": [{"index": 0, "topic": data.get("topic", "Unknown"), "errors": errors}] if not valid else []
            }
    except Exception as e:
        return {
            "total": 0,
            "passed": 0,
            "failed": 1,
            "errors": [{"index": 0, "topic": "File Error", "errors": [str(e)]}]
        }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_psychiatry_mcq_generation.py <mcq_file.json>")
        sys.exit(1)

    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        sys.exit(1)

    results = validate_mcq_file(file_path)

    print(f"\n{'='*60}")
    print(f"Psychiatry MCQ Validation Report: {file_path.name}")
    print(f"{'='*60}")
    print(f"Total MCQs: {results['total']}")
    print(f"✅ Passed: {results['passed']}")
    print(f"❌ Failed: {results['failed']}")

    if results['failed'] > 0:
        print(f"\n{'='*60}")
        print("Validation Errors:")
        print(f"{'='*60}")
        for error_group in results['errors']:
            print(f"\nMCQ #{error_group['index']}: {error_group['topic']}")
            for error in error_group['errors']:
                print(f"  - {error}")
        print(f"\n{'='*60}")
        print("❌ VALIDATION FAILED")
        print(f"{'='*60}\n")
        sys.exit(1)
    else:
        print(f"\n{'='*60}")
        print("✅ VALIDATION PASSED")
        print(f"{'='*60}\n")
        sys.exit(0)
