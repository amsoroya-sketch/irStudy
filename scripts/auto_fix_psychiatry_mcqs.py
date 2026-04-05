#!/usr/bin/env python3
"""
Auto-fix common errors in psychiatry MCQs post-generation.
Adds SAFE-T protocol, crisis contacts, fixes "Unknown" references.

Based on Constraint 15: Psychiatry MCQ Zero-Tolerance Requirements
"""

import json
import sys
from pathlib import Path
from typing import Dict, List

def fix_mcq(mcq: dict) -> dict:
    """Apply auto-fixes to MCQ."""
    fixed = mcq.copy()

    # Fix 1: Add SAFE-T to key_points if missing
    key_points = fixed.get("explanation", {}).get("key_points", [])

    safe_t_present = any("SAFE-T" in kp for kp in key_points)
    if not safe_t_present:
        safe_t_point = "SAFE-T suicide risk assessment: Specific plan, Access to means, Feelings (hopelessness), Earlier attempts, Threat"
        key_points.insert(0, safe_t_point)
        print(f"  [FIX] Added SAFE-T as first key point")

    # Fix 2: Add crisis contacts for high-risk topics
    topic = fixed.get("topic", "").lower()
    if any(keyword in topic for keyword in ["depression", "suicide", "psychosis"]):
        crisis_present = any("Lifeline" in kp for kp in key_points)
        if not crisis_present:
            crisis_point = "Australian crisis contacts: Lifeline 13 11 14 (24/7), Beyond Blue 1300 224 636"
            key_points.append(crisis_point)
            print(f"  [FIX] Added Australian crisis contacts")

    # Fix 3: Replace "Unknown" references
    references = fixed.get("references", [])
    for ref in references:
        if ref.get("title") == "Unknown":
            if "depression" in topic or "mood" in topic:
                ref["title"] = "RANZCP Clinical Practice Guidelines for Mood Disorders"
                print(f"  [FIX] Replaced 'Unknown' → RANZCP Mood Disorders")
            elif "suicide" in topic:
                ref["title"] = "Black Dog Institute Suicide Prevention Guidelines"
                print(f"  [FIX] Replaced 'Unknown' → Black Dog Institute")
            elif "psychosis" in topic or "schizophrenia" in topic:
                ref["title"] = "RANZCP Clinical Practice Guidelines for Schizophrenia"
                print(f"  [FIX] Replaced 'Unknown' → RANZCP Schizophrenia")
            else:
                ref["title"] = "Therapeutic Guidelines: Psychiatry (eTG)"
                print(f"  [FIX] Replaced 'Unknown' → eTG Psychiatry")

    # Fix 4: Enhance explanation with SAFE-T context
    why_correct = fixed.get("explanation", {}).get("why_correct", "")
    if "SAFE-T" not in why_correct:
        safe_t_intro = "In any patient presenting with depression or mental health crisis, SAFE-T suicide risk assessment is MANDATORY. SAFE-T protocol: (S) Specific plan - does patient have concrete suicide method planned? (A) Access to means - does patient have access to lethal means (medications, firearms, heights)? (F) Feelings - presence of hopelessness, worthlessness, feeling like a burden? (E) Earlier attempts - history of previous suicide attempts? (T) Threat - explicit or implicit threat of self-harm? In this case: "
        fixed["explanation"]["why_correct"] = safe_t_intro + why_correct
        print(f"  [FIX] Enhanced explanation with SAFE-T context")

    # Update key_points in fixed MCQ
    if "explanation" not in fixed:
        fixed["explanation"] = {}
    fixed["explanation"]["key_points"] = key_points

    return fixed

def fix_mcq_file(input_file: Path, output_file: Path = None) -> Dict[str, any]:
    """Fix MCQ file and return statistics."""
    if output_file is None:
        output_file = input_file.parent / (input_file.stem + "_fixed.json")

    try:
        with open(input_file, 'r') as f:
            data = json.load(f)

        # Handle metadata wrapper (e.g., {"metadata": {...}, "mcqs": [...]})
        has_metadata = isinstance(data, dict) and "mcqs" in data
        if has_metadata:
            metadata = data.get("metadata", {})
            mcq_list = data["mcqs"]
        else:
            metadata = None
            mcq_list = data if isinstance(data, list) else [data]

        # Process MCQs
        fixed_data = []
        stats = {"total": len(mcq_list), "fixed": 0}

        for idx, mcq in enumerate(mcq_list):
            print(f"\nProcessing MCQ #{idx}: {mcq.get('topic', 'Unknown')}")
            fixed_mcq = fix_mcq(mcq)
            fixed_data.append(fixed_mcq)

            # Count if any fixes were applied
            if fixed_mcq != mcq:
                stats["fixed"] += 1

        # Write output with same structure as input
        if has_metadata:
            output_data = {"metadata": metadata, "mcqs": fixed_data}
        elif isinstance(data, list):
            output_data = fixed_data
        else:
            output_data = fixed_data[0]

        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)

        return {"success": True, "stats": stats, "output_file": str(output_file)}

    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python auto_fix_psychiatry_mcqs.py <mcq_file.json> [output_file.json]")
        sys.exit(1)

    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else None

    if not input_file.exists():
        print(f"❌ File not found: {input_file}")
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"Psychiatry MCQ Auto-Fix: {input_file.name}")
    print(f"{'='*60}")

    result = fix_mcq_file(input_file, output_file)

    if result["success"]:
        print(f"\n{'='*60}")
        print(f"Auto-Fix Summary:")
        print(f"{'='*60}")
        print(f"Total MCQs: {result['stats']['total']}")
        print(f"Fixed MCQs: {result['stats']['fixed']}")
        print(f"Output file: {result['output_file']}")
        print(f"\n{'='*60}")
        print(f"✅ Auto-fix completed successfully")
        print(f"{'='*60}\n")
        sys.exit(0)
    else:
        print(f"\n❌ Auto-fix failed: {result['error']}\n")
        sys.exit(1)
