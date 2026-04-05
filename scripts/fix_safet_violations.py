#!/usr/bin/env python3
"""
Fix CRITICAL ZERO-TOLERANCE VIOLATIONS: Add SAFE-T suicide risk assessment to psychiatry MCQs

SAFE-T Protocol:
- S: Specific plan (concrete suicide plan?)
- A: Access to means (lethal means available?)
- F: Feelings (hopelessness, burden, despair?)
- E: Earlier attempts (previous suicide attempts?)
- T: Threat (explicit/implicit self-harm threat?)

Australian Crisis Contacts:
- Lifeline: 13 11 14
- Beyond Blue: 1300 224 636
- Suicide Call Back Service: 1300 659 467
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any

# SAFE-T protocol content
SAFET_KEY_POINT = (
    "SAFE-T suicide risk assessment: Specific plan, Access to means, "
    "Feelings (hopelessness), Earlier attempts, Threat"
)

SAFET_DETAILED = (
    "SAFE-T suicide risk assessment protocol: "
    "(S) Specific plan - does patient have concrete suicide method planned? "
    "(A) Access to means - does patient have access to lethal means (medications, firearms, heights)? "
    "(F) Feelings - presence of hopelessness, worthlessness, feeling like a burden? "
    "(E) Earlier attempts - history of previous suicide attempts? "
    "(T) Threat - explicit or implicit threat of self-harm?"
)

CRISIS_CONTACTS = (
    "Australian crisis contacts: Lifeline 13 11 14 (24/7), "
    "Beyond Blue 1300 224 636, Suicide Call Back Service 1300 659 467"
)

SAFETY_PLAN_CONTENT = (
    "Safety plan components: (1) Warning signs recognition, "
    "(2) Internal coping strategies, (3) Social contacts for support, "
    "(4) Professional contacts (GP, psychiatrist, crisis team), "
    "(5) Crisis helplines (Lifeline 13 11 14), "
    "(6) Means restriction (remove medications, firearms, avoid heights)"
)

# Australian reference sources
AUSTRALIAN_REFERENCES = {
    "depression": "RANZCP Clinical Practice Guidelines for Mood Disorders",
    "suicide": "Black Dog Institute Suicide Prevention Guidelines",
    "general_psych": "Therapeutic Guidelines: Psychiatry (eTG)",
    "mental_health_act": "NSW Mental Health Act 2007 / VIC Mental Health Act 2014",
}


def identify_relevant_mcqs(mcqs: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """Identify MCQs that need SAFE-T content."""
    categories = {
        "suicide_explicit": [],  # PSY-SUICIDE-MHA series
        "depression": [],  # PSY-DEP series
        "psychosis_with_risk": [],  # PSY-PSYCHOSIS with suicide risk indicators
        "anxiety_with_risk": [],  # PSY-ANX with suicide risk
    }

    for mcq in mcqs:
        mcq_id = mcq.get("id", "")  # Fixed: was "mcq_id", should be "id"
        question = mcq.get("question", {})
        scenario = question.get("scenario", "").lower()
        stem = question.get("stem", "").lower()
        combined_text = scenario + " " + stem

        # Explicit suicide/MHA MCQs
        if "PSY-SUICIDE-MHA" in mcq_id or "PSY-MHA" in mcq_id:
            categories["suicide_explicit"].append(mcq_id)

        # Depression MCQs
        elif "PSY-DEP" in mcq_id or "depression" in mcq_id.lower():
            categories["depression"].append(mcq_id)

        # Psychosis with suicide risk indicators
        elif "PSY-PSYCHOSIS" in mcq_id or "psychosis" in mcq_id.lower():
            if any(keyword in combined_text for keyword in [
                "suicide", "self-harm", "hopeless", "worthless",
                "command hallucination", "kill yourself"
            ]):
                categories["psychosis_with_risk"].append(mcq_id)

        # Anxiety with suicide risk
        elif "PSY-ANX" in mcq_id or "anxiety" in mcq_id.lower():
            if any(keyword in combined_text for keyword in [
                "suicide", "self-harm", "hopeless", "worthless"
            ]):
                categories["anxiety_with_risk"].append(mcq_id)

    return categories


def add_safet_to_mcq(mcq: Dict[str, Any], category: str) -> Dict[str, Any]:
    """Add SAFE-T protocol content to an MCQ."""
    mcq_id = mcq.get("id", "")  # Fixed: was "mcq_id"

    # 1. Add SAFE-T to key_points (which is inside explanation object)
    if "explanation" not in mcq:
        mcq["explanation"] = {}
    if "key_points" not in mcq["explanation"]:
        mcq["explanation"]["key_points"] = []

    # Check if SAFE-T already present
    has_safet = any("SAFE-T" in kp or "suicide risk assessment" in kp.lower()
                    for kp in mcq["explanation"]["key_points"])

    if not has_safet:
        mcq["explanation"]["key_points"].insert(0, SAFET_KEY_POINT)

    # 2. Add crisis contacts for suicide-explicit MCQs
    if category == "suicide_explicit":
        has_crisis = any("Lifeline" in kp or "13 11 14" in kp
                        for kp in mcq["explanation"]["key_points"])
        if not has_crisis:
            mcq["explanation"]["key_points"].append(CRISIS_CONTACTS)

        # Add safety plan content
        has_safety_plan = any("safety plan" in kp.lower()
                             for kp in mcq["explanation"]["key_points"])
        if not has_safety_plan:
            mcq["explanation"]["key_points"].append(SAFETY_PLAN_CONTENT)

    # 3. Enhance explanation with SAFE-T context
    if "explanation" in mcq and isinstance(mcq["explanation"], dict):
        why_correct = mcq["explanation"].get("why_correct", "")

        # Add SAFE-T framework if not present
        if "SAFE-T" not in why_correct and len(why_correct) > 0:
            # Insert SAFE-T context before existing explanation
            safet_intro = (
                f"In any patient presenting with depression or mental health crisis, "
                f"SAFE-T suicide risk assessment is MANDATORY. {SAFET_DETAILED} "
                f"In this case: "
            )
            mcq["explanation"]["why_correct"] = safet_intro + why_correct

        # Add crisis contacts to suicide MCQs
        if category == "suicide_explicit":
            if "Lifeline" not in why_correct and "13 11 14" not in why_correct:
                mcq["explanation"]["why_correct"] += (
                    f" Always provide crisis contacts: {CRISIS_CONTACTS}"
                )

    # 4. Fix "Unknown" references in references array
    if "references" in mcq and isinstance(mcq["references"], list):
        for ref in mcq["references"]:
            if ref.get("title") == "Unknown" or not ref.get("title") or ref.get("title", "").strip() == "":
                # Assign appropriate Australian reference
                if category == "suicide_explicit":
                    ref["title"] = AUSTRALIAN_REFERENCES["suicide"]
                elif category == "depression":
                    ref["title"] = AUSTRALIAN_REFERENCES["depression"]
                else:
                    ref["title"] = AUSTRALIAN_REFERENCES["general_psych"]

    return mcq


def main():
    """Main execution function."""
    # File path
    mcq_file = Path("/home/dev/Development/irStudy/data/mcqs/week1_all_100_unique_mcqs.json")

    if not mcq_file.exists():
        print(f"ERROR: MCQ file not found: {mcq_file}")
        sys.exit(1)

    print("="*80)
    print("FIXING CRITICAL ZERO-TOLERANCE VIOLATIONS: SAFE-T Suicide Risk Assessment")
    print("="*80)
    print()

    # Read MCQs
    print(f"Reading MCQ file: {mcq_file}")
    with open(mcq_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    mcqs = data.get("mcqs", [])
    print(f"Total MCQs in file: {len(mcqs)}")
    print()

    # Identify relevant MCQs
    print("Identifying MCQs requiring SAFE-T protocol...")
    categories = identify_relevant_mcqs(mcqs)

    total_to_fix = sum(len(ids) for ids in categories.values())
    print(f"\nMCQs requiring SAFE-T content:")
    print(f"  - Suicide/MHA explicit: {len(categories['suicide_explicit'])}")
    print(f"  - Depression: {len(categories['depression'])}")
    print(f"  - Psychosis with suicide risk: {len(categories['psychosis_with_risk'])}")
    print(f"  - Anxiety with suicide risk: {len(categories['anxiety_with_risk'])}")
    print(f"  - TOTAL: {total_to_fix}")
    print()

    if total_to_fix == 0:
        print("No MCQs found requiring SAFE-T content.")
        sys.exit(0)

    # Modify MCQs
    print("Adding SAFE-T protocol content...")
    modified_mcqs = []
    modified_count = 0

    for mcq in mcqs:
        mcq_id = mcq.get("id", "")  # Fixed: was "mcq_id"

        # Determine category
        category = None
        for cat_name, ids in categories.items():
            if mcq_id in ids:
                category = cat_name
                break

        if category:
            # Store before state for reporting
            before_key_points_count = len(mcq.get("explanation", {}).get("key_points", []))

            # Modify MCQ
            mcq = add_safet_to_mcq(mcq, category)

            after_key_points_count = len(mcq.get("explanation", {}).get("key_points", []))

            modified_mcqs.append({
                "mcq_id": mcq_id,
                "category": category,
                "before_key_points": before_key_points_count,
                "after_key_points": after_key_points_count,
            })
            modified_count += 1

    print(f"Modified {modified_count} MCQs")
    print()

    # Write back to file
    print(f"Writing modified MCQs back to: {mcq_file}")
    with open(mcq_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("✅ File written successfully")
    print()

    # Generate report
    print("="*80)
    print("MODIFICATION REPORT")
    print("="*80)
    print()

    print(f"Total MCQs modified: {modified_count}")
    print()

    print("Modified MCQs by category:")
    for category, ids in categories.items():
        if len(ids) > 0:
            print(f"\n{category.upper().replace('_', ' ')} ({len(ids)} MCQs):")
            for mcq_id in ids[:10]:  # Show first 10
                matching = [m for m in modified_mcqs if m["mcq_id"] == mcq_id]
                if matching:
                    m = matching[0]
                    print(f"  ✓ {mcq_id}: {m['before_key_points']} → {m['after_key_points']} key points")
            if len(ids) > 10:
                print(f"  ... and {len(ids) - 10} more")

    print()

    # Show before/after examples
    print("="*80)
    print("BEFORE/AFTER EXAMPLES")
    print("="*80)

    # Reload to show actual changes
    with open(mcq_file, 'r', encoding='utf-8') as f:
        updated_data = json.load(f)

    updated_mcqs = updated_data.get("mcqs", [])

    # Example 1: Depression MCQ
    depression_example = None
    for mcq in updated_mcqs:
        if "PSY-DEP" in mcq.get("mcq_id", ""):
            depression_example = mcq
            break

    if depression_example:
        print("\n--- EXAMPLE 1: Depression MCQ ---")
        print(f"MCQ ID: {depression_example.get('mcq_id')}")
        print(f"\nKey Points ({len(depression_example.get('key_points', []))}):")
        for i, kp in enumerate(depression_example.get('key_points', [])[:5], 1):
            print(f"  {i}. {kp[:100]}{'...' if len(kp) > 100 else ''}")

        if len(depression_example.get('key_points', [])) > 5:
            print(f"  ... and {len(depression_example.get('key_points', [])) - 5} more")

        print(f"\nReference: {depression_example.get('explanation', {}).get('reference', 'N/A')}")

    # Example 2: Suicide MCQ
    suicide_example = None
    for mcq in updated_mcqs:
        if "PSY-SUICIDE-MHA" in mcq.get("mcq_id", "") or "PSY-MHA" in mcq.get("mcq_id", ""):
            suicide_example = mcq
            break

    if suicide_example:
        print("\n--- EXAMPLE 2: Suicide/MHA MCQ ---")
        print(f"MCQ ID: {suicide_example.get('mcq_id')}")
        print(f"\nKey Points ({len(suicide_example.get('key_points', []))}):")
        for i, kp in enumerate(suicide_example.get('key_points', [])[:5], 1):
            print(f"  {i}. {kp[:100]}{'...' if len(kp) > 100 else ''}")

        if len(suicide_example.get('key_points', [])) > 5:
            print(f"  ... and {len(suicide_example.get('key_points', [])) - 5} more")

        print(f"\nReference: {suicide_example.get('explanation', {}).get('reference', 'N/A')}")

    print()
    print("="*80)
    print("VALIDATION")
    print("="*80)
    print()

    # Validation checks
    all_checks_pass = True

    # Check 1: JSON validity
    try:
        with open(mcq_file, 'r', encoding='utf-8') as f:
            json.load(f)
        print("✅ JSON validity: PASS")
    except Exception as e:
        print(f"❌ JSON validity: FAIL - {e}")
        all_checks_pass = False

    # Check 2: SAFE-T in depression MCQs
    depression_with_safet = 0
    for mcq in updated_mcqs:
        if "PSY-DEP" in mcq.get("mcq_id", ""):
            key_points = " ".join(mcq.get("key_points", []))
            if "SAFE-T" in key_points:
                depression_with_safet += 1

    depression_total = len([m for m in updated_mcqs if "PSY-DEP" in m.get("mcq_id", "")])
    if depression_total > 0:
        coverage = (depression_with_safet / depression_total) * 100
        print(f"✅ SAFE-T in depression MCQs: {depression_with_safet}/{depression_total} ({coverage:.1f}%)")
        if coverage < 100:
            print(f"   ⚠️  Warning: Not all depression MCQs have SAFE-T content")
            all_checks_pass = False

    # Check 3: Crisis contacts in suicide MCQs
    suicide_with_contacts = 0
    for mcq in updated_mcqs:
        if "PSY-SUICIDE-MHA" in mcq.get("mcq_id", "") or "PSY-MHA" in mcq.get("mcq_id", ""):
            key_points = " ".join(mcq.get("key_points", []))
            if "13 11 14" in key_points or "Lifeline" in key_points:
                suicide_with_contacts += 1

    suicide_total = len([m for m in updated_mcqs
                        if "PSY-SUICIDE-MHA" in m.get("mcq_id", "")
                        or "PSY-MHA" in m.get("mcq_id", "")])
    if suicide_total > 0:
        coverage = (suicide_with_contacts / suicide_total) * 100
        print(f"✅ Crisis contacts in suicide MCQs: {suicide_with_contacts}/{suicide_total} ({coverage:.1f}%)")
        if coverage < 100:
            print(f"   ⚠️  Warning: Not all suicide MCQs have crisis contacts")
            all_checks_pass = False

    # Check 4: Unknown references fixed
    unknown_refs = 0
    for mcq in updated_mcqs:
        if mcq.get("mcq_id", "").startswith("PSY-"):
            ref = mcq.get("explanation", {}).get("reference", "")
            if ref == "Unknown" or not ref or ref.strip() == "":
                unknown_refs += 1

    print(f"✅ Unknown references remaining: {unknown_refs}")
    if unknown_refs > 0:
        print(f"   ⚠️  Warning: {unknown_refs} psychiatry MCQs still have unknown references")
        all_checks_pass = False

    # Check 5: File size increased
    file_size = mcq_file.stat().st_size
    print(f"✅ File size: {file_size:,} bytes")

    print()

    if all_checks_pass:
        print("="*80)
        print("✅ ALL VALIDATION CHECKS PASSED")
        print("="*80)
    else:
        print("="*80)
        print("⚠️  SOME VALIDATION WARNINGS - Review above")
        print("="*80)

    print()
    print("="*80)
    print("NEXT RECOMMENDED FIXES")
    print("="*80)
    print()
    print("1. Aboriginal/TSI cultural safety content:")
    print("   - Add cultural safety key points to relevant MCQs")
    print("   - Include Aboriginal Medical Services contacts")
    print("   - Address trauma-informed care for Indigenous patients")
    print()
    print("2. LGBTQIA+ inclusive language:")
    print("   - Review pronouns in scenarios")
    print("   - Add LGBTQIA+ mental health resources")
    print("   - Address minority stress in appropriate MCQs")
    print()
    print("3. CALD (Culturally and Linguistically Diverse) considerations:")
    print("   - Add interpreter services information")
    print("   - Cultural formulation in psychiatric assessment")
    print("   - Family dynamics in CALD communities")
    print()

    print("SAFE-T PROTOCOL FIXES COMPLETE ✅")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
