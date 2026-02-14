#!/usr/bin/env python3
"""
Week 3 Cardiology MCQ Regeneration - Batch 5 (MCQs 076-110)
Arrhythmias Topic (35 MCQs)

ENHANCED QUALITY (Per OSCE Methodology Integration - Table 6):
 Differential diagnosis mentioned in every explanation
 Clinical frameworks referenced (CHA‚DS‚-VASc, HAS-BLED, Vaughan Williams, NBG codes, AV block classification)
 Options represent top 3 differentials plus one unlikely
 Safety-netting included in management explanations
 IMG-focused: comprehensive explanations, no assumed knowledge
 Australian context: PBS, eTG, CSANZ, ARC, NHFA guidelines

Per Constraint 4.2: Claude (Claude Code) generation for complex medical MCQs
Per Constraint 1: Australian medical context, spelling (oedema), drug names (adrenaline, lignocaine, paracetamol)
Per Constraint 12: NO placeholder content

Consolidates MCQs from 5 source files:
1. week3_cardiology_af_076_086.json (11 AF MCQs)
2. WEEK3_CARDIO_087_093_VENTRICULAR_ARRHYTHMIAS.py (7 Ventricular MCQs)
3. week3_cardio_svt_094_100.py (7 SVT MCQs)
4. week3_bradyarrhythmia_mcqs_101-106.json (6 Bradyarrhythmia MCQs)
5. week3_cardio_107_110_other_arrhythmias.py (4 Other Arrhythmia MCQs)
"""

import json
from pathlib import Path
from datetime import datetime
import sys
import importlib.util

def load_python_dict(filepath):
    """Load GENERATED_MCQS dict from a Python file."""
    spec = importlib.util.spec_from_file_location("module", filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.GENERATED_MCQS

def main():
    # Define paths
    base_dir = Path("/home/dev/Development/irStudy")
    data_dir = base_dir / "data" / "mcqs"

    # Source files
    af_file = data_dir / "week3_cardiology_af_076_086.json"
    ventricular_file = data_dir / "WEEK3_CARDIO_087_093_VENTRICULAR_ARRHYTHMIAS.py"
    svt_file = data_dir / "week3_cardio_svt_094_100.py"
    brady_file = data_dir / "week3_bradyarrhythmia_mcqs_101-106.json"
    other_file = data_dir / "week3_cardio_107_110_other_arrhythmias.py"

    # Main MCQ file
    main_file = data_dir / "week3_cardiology_200_mcqs.json"

    print("=" * 80)
    print("WEEK 3 CARDIOLOGY - BATCH 5 REGENERATION (MCQs 076-110)")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Step 1: Load all source files
    print("Step 1: Loading source MCQ files...")
    print(f"  - Loading AF MCQs 076-086 from {af_file.name}...")
    with open(af_file, 'r') as f:
        af_mcqs = json.load(f)
    print(f"     Loaded {len(af_mcqs)} AF MCQs")

    print(f"  - Loading Ventricular MCQs 087-093 from {ventricular_file.name}...")
    ventricular_mcqs = load_python_dict(ventricular_file)
    print(f"     Loaded {len(ventricular_mcqs)} Ventricular MCQs")

    print(f"  - Loading SVT MCQs 094-100 from {svt_file.name}...")
    svt_mcqs = load_python_dict(svt_file)
    print(f"     Loaded {len(svt_mcqs)} SVT MCQs")

    print(f"  - Loading Bradyarrhythmia MCQs 101-106 from {brady_file.name}...")
    with open(brady_file, 'r') as f:
        brady_mcqs = json.load(f)
    print(f"     Loaded {len(brady_mcqs)} Bradyarrhythmia MCQs")

    print(f"  - Loading Other Arrhythmia MCQs 107-110 from {other_file.name}...")
    other_mcqs = load_python_dict(other_file)
    print(f"     Loaded {len(other_mcqs)} Other Arrhythmia MCQs")

    # Step 2: Merge all MCQs into one dict
    print()
    print("Step 2: Merging all MCQs into single dictionary...")
    GENERATED_MCQS = {}
    GENERATED_MCQS.update(af_mcqs)
    GENERATED_MCQS.update(ventricular_mcqs)
    GENERATED_MCQS.update(svt_mcqs)
    GENERATED_MCQS.update(brady_mcqs)
    GENERATED_MCQS.update(other_mcqs)

    total_mcqs = len(GENERATED_MCQS)
    print(f"   Total MCQs merged: {total_mcqs}")

    # Verify we have all 35 MCQs (076-110)
    expected_ids = [f"WEEK3-CARDIO-{str(i).zfill(3)}" for i in range(76, 111)]
    actual_ids = sorted(GENERATED_MCQS.keys())

    if len(GENERATED_MCQS) != 35:
        print(f"     WARNING: Expected 35 MCQs, got {len(GENERATED_MCQS)}")
        missing = set(expected_ids) - set(actual_ids)
        if missing:
            print(f"  L Missing MCQs: {sorted(missing)}")
            return 1

    print(f"   All MCQ IDs present: {actual_ids[0]} to {actual_ids[-1]}")

    # Step 3: Load main MCQ file
    print()
    print(f"Step 3: Loading main MCQ file: {main_file.name}...")

    if not main_file.exists():
        print(f"  L ERROR: Main file not found: {main_file}")
        return 1

    with open(main_file, 'r') as f:
        main_data = json.load(f)

    current_mcqs = main_data.get("mcqs", [])
    print(f"   Loaded main file with {len(current_mcqs)} MCQs")

    # Step 4: Create backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = main_file.parent / f"{main_file.stem}_backup_batch5_{timestamp}.json"

    print()
    print(f"Step 4: Creating backup...")
    print(f"  Backup file: {backup_file.name}")

    with open(backup_file, 'w') as f:
        json.dump(main_data, f, indent=2, ensure_ascii=False)

    print(f"   Backup created successfully")

    # Step 5: Update MCQs 076-110 (indices 75-109)
    print()
    print(f"Step 5: Updating MCQs 076-110 (array indices 75-109)...")

    update_count = 0
    error_count = 0

    for mcq_num in range(76, 111):  # 76 to 110 inclusive
        mcq_id = f"WEEK3-CARDIO-{str(mcq_num).zfill(3)}"
        array_index = mcq_num - 1  # Array is 0-indexed

        if mcq_id not in GENERATED_MCQS:
            print(f"  L ERROR: MCQ {mcq_id} not found in generated MCQs")
            error_count += 1
            continue

        # Get the generated MCQ
        generated_mcq = GENERATED_MCQS[mcq_id]

        # Ensure the main data array is large enough
        while len(current_mcqs) <= array_index:
            current_mcqs.append({})

        # Update the MCQ at the correct index
        current_mcqs[array_index] = {
            "id": mcq_id,
            "question": generated_mcq["question"],
            "correct_answer": generated_mcq["correct_answer"],
            "explanation": generated_mcq["explanation"],
            "summary": generated_mcq.get("summary", ""),
            "citations": generated_mcq.get("citations", generated_mcq.get("references", [])),
            "metadata": generated_mcq.get("metadata", {
                "topic": "Arrhythmias",
                "difficulty": "intermediate",
                "australian_context": True
            }),
            "regenerated": True,
            "regeneration_timestamp": datetime.now().isoformat(),
            "regeneration_batch": "batch_5_arrhythmias_076_110",
            "regeneration_failed": False
        }

        update_count += 1

        if mcq_num % 5 == 0 or mcq_num == 110:
            print(f"   Updated MCQs up to {mcq_id} ({update_count}/{35})")

    print()
    print(f"Step 5 Summary:")
    print(f"   Successfully updated: {update_count} MCQs")
    if error_count > 0:
        print(f"  L Errors encountered: {error_count}")

    # Step 6: Save updated main file
    print()
    print(f"Step 6: Saving updated main MCQ file...")

    main_data["mcqs"] = current_mcqs
    main_data["metadata"]["last_updated"] = datetime.now().isoformat()
    main_data["metadata"]["total_mcqs"] = len(current_mcqs)
    main_data["metadata"]["batch_5_complete"] = True
    main_data["metadata"]["arrhythmias_complete"] = True

    with open(main_file, 'w') as f:
        json.dump(main_data, f, indent=2, ensure_ascii=False)

    print(f"   Main file saved successfully")

    # Step 7: Validation
    print()
    print("=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)

    # Count regenerated MCQs
    regenerated_count = sum(1 for mcq in current_mcqs if mcq.get("regenerated") and not mcq.get("regeneration_failed"))
    print(f"Total MCQs in main file: {len(current_mcqs)}")
    print(f"Successfully regenerated (all batches): {regenerated_count}")
    print(f"Batch 5 (Arrhythmias 076-110): {update_count}/35")

    # Check for placeholders
    placeholder_count = 0
    for i, mcq in enumerate(current_mcqs[:110], start=1):  # Check first 110 MCQs
        scenario = mcq.get("question", {}).get("scenario", "")
        if "Clinical scenario for" in scenario or not scenario:
            placeholder_count += 1

    print(f"Placeholders remaining (MCQs 001-110): {placeholder_count}")

    if placeholder_count == 0:
        print()
        print("<‰ SUCCESS! All MCQs 001-110 have been regenerated with real clinical content!")
        print()
        print("Progress Summary:")
        print("   Batch 1-3 (MCQs 001-040): ACS - COMPLETE")
        print("   Batch 4 (MCQs 041-075): Heart Failure - COMPLETE")
        print("   Batch 5 (MCQs 076-110): Arrhythmias - COMPLETE")
        print()
        print("Total Progress: 110/200 MCQs (55% complete)")
        print()
        print("Next Steps:")
        print("  ó Batch 6 (MCQs 111-135): Hypertension (25 MCQs)")
        print("  ó Batch 7 (MCQs 136-160): Valvular Disease (25 MCQs)")
        print("  ó Batch 8 (MCQs 161-200): Other Cardiology (40 MCQs)")
    else:
        print(f"\n   WARNING: {placeholder_count} placeholders still remaining in MCQs 001-110")

    print()
    print("=" * 80)
    print("BATCH 5 REGENERATION COMPLETE")
    print("=" * 80)

    return 0

if __name__ == "__main__":
    sys.exit(main())
