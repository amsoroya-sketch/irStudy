#!/usr/bin/env python3
"""
Detect placeholder content in medical knowledge items.
Identifies templates that were never properly generated.

Usage:
    python3 detect_placeholder_content.py <file.json>
    python3 detect_placeholder_content.py data/osces/*.json
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Placeholder patterns that indicate content wasn't generated
PLACEHOLDER_PATTERNS = {
    "generic_openings": [
        "A patient presents for",
        "A patient presents with",
        "Clinical scenario for",
        "Question about",
        "Answer for",
        "Explanation for",
    ],
    "generic_content": [
        "Clinical history relevant to",
        "Mental status examination findings for",
        "Examination findings for",
        "Systematic assessment findings for",
        "According to Australian guidelines for",
        "Key points for",
        "Definition and clinical significance of",
        "Diagnostic approach for",
        "Management principles for",
        "Important clinical pearls",
        "Australian-specific guideline for",
    ],
    "empty_content": [
        '""',
        "N/A",
        "TBD",
        "[Insert",
        "[TODO",
        "placeholder",
    ],
}

def check_osce_placeholders(osce: dict) -> Tuple[bool, List[str]]:
    """Check if OSCE has placeholder content."""
    issues = []

    # Check patient presentation
    presentation = osce.get("scenario", {}).get("patient_presentation", "")
    for pattern in PLACEHOLDER_PATTERNS["generic_openings"]:
        if pattern in presentation and len(presentation) < 200:
            issues.append(f"Generic presentation: '{presentation[:100]}'")
            break

    # Check history
    history = osce.get("scenario", {}).get("history", "")
    for pattern in PLACEHOLDER_PATTERNS["generic_content"]:
        if pattern in history:
            issues.append(f"Generic history: '{history[:100]}'")
            break

    # Check examination findings
    examination = osce.get("scenario", {}).get("examination_findings", "")
    for pattern in PLACEHOLDER_PATTERNS["generic_content"]:
        if pattern in examination:
            issues.append(f"Generic examination: '{examination[:100]}'")
            break

    # Check expected answers
    for key, value in osce.get("expected_answers", {}).items():
        if isinstance(value, str):
            for pattern in PLACEHOLDER_PATTERNS["generic_content"]:
                if pattern in value:
                    issues.append(f"Generic {key}: '{value[:100]}'")
                    break

    # Check references have content
    for idx, ref in enumerate(osce.get("references", [])):
        content = ref.get("content", "").strip()
        if not content or content == '""':
            issues.append(f"Reference {idx+1} has empty content field")

    return len(issues) == 0, issues

def check_mcq_placeholders(mcq: dict) -> Tuple[bool, List[str]]:
    """Check if MCQ has placeholder content."""
    issues = []

    # Check explanation
    explanation = mcq.get("explanation", {})
    if isinstance(explanation, str):
        for pattern in PLACEHOLDER_PATTERNS["generic_content"]:
            if pattern in explanation:
                issues.append(f"Generic explanation: '{explanation[:100]}'")
                break
    elif isinstance(explanation, dict):
        why_correct = explanation.get("why_correct", "")
        if len(why_correct) < 100:
            issues.append(f"Explanation too short ({len(why_correct)} chars)")

    # Check references
    for idx, ref in enumerate(mcq.get("references", [])):
        title = ref.get("title", "")
        if title == "Unknown":
            issues.append(f"Reference {idx+1} is 'Unknown'")

        content = ref.get("content", "").strip()
        if not content or content == '""':
            issues.append(f"Reference {idx+1} has empty content field")

    return len(issues) == 0, issues

def check_study_card_placeholders(card: dict) -> Tuple[bool, List[str]]:
    """Check if study card has placeholder content."""
    issues = []

    # Check front
    front = card.get("front", {})
    if isinstance(front, dict):
        question = front.get("question", "")
        for pattern in PLACEHOLDER_PATTERNS["generic_openings"]:
            if pattern in question:
                issues.append(f"Generic question: '{question[:100]}'")
                break

    # Check back
    back = card.get("back", {})
    if isinstance(back, dict):
        answer = back.get("answer", "")
        for pattern in PLACEHOLDER_PATTERNS["generic_content"]:
            if pattern in answer and len(answer) < 100:
                issues.append(f"Generic answer: '{answer[:100]}'")
                break

        # Check key_facts
        key_facts = back.get("key_facts", [])
        if key_facts:
            for fact in key_facts:
                if any(p in fact for p in PLACEHOLDER_PATTERNS["generic_content"]):
                    issues.append(f"Generic fact: '{fact[:100]}'")
                    break

    # Check references
    for idx, ref in enumerate(card.get("references", [])):
        content = ref.get("content", "").strip()
        if not content or content == '""':
            issues.append(f"Reference {idx+1} has empty content field")

    return len(issues) == 0, issues

def analyze_file(file_path: Path) -> Dict:
    """Analyze a single file for placeholder content."""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)

        # Determine content type and extract items
        if "osces" in data or file_path.stem.endswith("osces"):
            content_type = "osce"
            items = data.get("osces", [data] if "id" in data else [])
            check_func = check_osce_placeholders
        elif "mcqs" in data or file_path.stem.endswith("mcqs"):
            content_type = "mcq"
            items = data.get("mcqs", [data] if "id" in data else [])
            check_func = check_mcq_placeholders
        elif "cards" in data or file_path.stem.endswith("cards"):
            content_type = "study_card"
            items = data.get("cards", [data] if "id" in data else [])
            check_func = check_study_card_placeholders
        else:
            return {
                "file": str(file_path),
                "content_type": "unknown",
                "error": "Unknown content type"
            }

        # Check each item
        total = len(items)
        placeholder_count = 0
        all_issues = []

        for idx, item in enumerate(items):
            is_valid, issues = check_func(item)
            if not is_valid:
                placeholder_count += 1
                all_issues.append({
                    "item_id": item.get("id", f"item_{idx}"),
                    "issues": issues
                })

        return {
            "file": str(file_path),
            "content_type": content_type,
            "total_items": total,
            "placeholder_count": placeholder_count,
            "valid_count": total - placeholder_count,
            "placeholder_rate": round(placeholder_count / total * 100, 1) if total > 0 else 0,
            "issues": all_issues[:5],  # First 5 items with issues
            "status": "NEEDS_REGENERATION" if placeholder_count > total * 0.5 else "NEEDS_REVIEW" if placeholder_count > 0 else "OK"
        }

    except Exception as e:
        return {
            "file": str(file_path),
            "error": str(e)
        }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 detect_placeholder_content.py <file.json> [additional_files...]")
        sys.exit(1)

    results = []

    print(f"\n{'='*80}")
    print("Placeholder Content Detection Report")
    print(f"{'='*80}\n")

    for file_arg in sys.argv[1:]:
        file_path = Path(file_arg)
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            continue

        result = analyze_file(file_path)
        results.append(result)

        if "error" in result and "content_type" not in result:
            print(f"❌ {result['file']}: {result['error']}\n")
            continue

        status_icon = "✅" if result["status"] == "OK" else "⚠️" if result["status"] == "NEEDS_REVIEW" else "❌"

        print(f"{status_icon} {result['file']}")
        print(f"   Type: {result['content_type']}")
        print(f"   Total items: {result['total_items']}")
        print(f"   Placeholder items: {result['placeholder_count']} ({result['placeholder_rate']}%)")
        print(f"   Status: {result['status']}")

        if result.get("issues"):
            print(f"\n   Sample Issues:")
            for issue_item in result["issues"][:3]:
                print(f"     • {issue_item['item_id']}:")
                for issue in issue_item["issues"][:2]:
                    print(f"       - {issue}")

        print()

    # Summary
    if len(results) > 1:
        print(f"{'='*80}")
        print("Summary")
        print(f"{'='*80}")

        total_files = len(results)
        needs_regen = sum(1 for r in results if r.get("status") == "NEEDS_REGENERATION")
        needs_review = sum(1 for r in results if r.get("status") == "NEEDS_REVIEW")
        ok = sum(1 for r in results if r.get("status") == "OK")

        print(f"Total files analyzed: {total_files}")
        print(f"❌ Needs regeneration: {needs_regen}")
        print(f"⚠️  Needs review: {needs_review}")
        print(f"✅ OK: {ok}")

        total_items = sum(r.get("total_items", 0) for r in results)
        total_placeholders = sum(r.get("placeholder_count", 0) for r in results)

        print(f"\nTotal items: {total_items}")
        print(f"Placeholder items: {total_placeholders} ({round(total_placeholders/total_items*100, 1) if total_items > 0 else 0}%)")
        print(f"{'='*80}\n")

        if needs_regen > 0:
            sys.exit(1)  # Exit with error code if regeneration needed
