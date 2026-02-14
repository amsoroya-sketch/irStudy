#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Week 3 Respiratory MCQ Consolidation - Batch 2 (MCQs 026-050)
COPD Management & Bronchiectasis

Consolidates MCQs from:
- WEEK3_RESP_026_038_COPD_PART1.py (13 MCQs)
- WEEK3_RESP_039_050_INHALERS_BIOLOGICS.py (12 MCQs)
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
    base_dir = Path("/home/dev/Development/irStudy")
    data_dir = base_dir / "data" / "mcqs"

    # Source files
    part1_file = data_dir / "WEEK3_RESP_026_038_COPD_PART1.py"
    part2_file = data_dir / "WEEK3_RESP_039_050_INHALERS_BIOLOGICS.py"
    main_file = data_dir / "week3_respiratory_200_mcqs.json"

    print("=" * 80)
    print("WEEK 3 RESPIRATORY - BATCH 2 CONSOLIDATION (MCQs 026-050)")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Step 1: Load source files
    print("Step 1: Loading source MCQ files...")
    print(f"  - Loading Part 1 (026-038)...")
    part1_mcqs = load_python_dict(part1_file)
    print(f"    [OK] Loaded {len(part1_mcqs)} MCQs")

    print(f"  - Loading Part 2 (039-050)...")
    part2_mcqs = load_python_dict(part2_file)
    print(f"    [OK] Loaded {len(part2_mcqs)} MCQs")

    # Step 2: Merge
    print()
    print("Step 2: Merging all MCQs...")
    GENERATED_MCQS = {}
    GENERATED_MCQS.update(part1_mcqs)
    GENERATED_MCQS.update(part2_mcqs)

    print(f"  [OK] Total MCQs merged: {len(GENERATED_MCQS)}")

    expected_ids = [f"WEEK3-RESP-{str(i).zfill(3)}" for i in range(26, 51)]
    actual_ids = sorted(GENERATED_MCQS.keys())

    if len(GENERATED_MCQS) != 25:
        print(f"  [WARNING] Expected 25 MCQs, got {len(GENERATED_MCQS)}")
        missing = set(expected_ids) - set(actual_ids)
        if missing:
            print(f"  [ERROR] Missing: {sorted(missing)}")
            return 1

    print(f"  [OK] All MCQ IDs present: {actual_ids[0]} to {actual_ids[-1]}")

    # Step 3: Load main file
    print()
    print(f"Step 3: Loading main MCQ file...")
    with open(main_file, 'r') as f:
        main_data = json.load(f)
    current_mcqs = main_data.get("mcqs", [])
    print(f"  [OK] Loaded {len(current_mcqs)} MCQs")

    # Step 4: Backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = main_file.parent / f"{main_file.stem}_backup_batch2_{timestamp}.json"
    print()
    print(f"Step 4: Creating backup...")
    with open(backup_file, 'w') as f:
        json.dump(main_data, f, indent=2, ensure_ascii=False)
    print(f"  [OK] Backup: {backup_file.name}")

    # Step 5: Update MCQs 026-050 (indices 25-49)
    print()
    print(f"Step 5: Updating MCQs 026-050...")
    update_count = 0

    for mcq_num in range(26, 51):
        mcq_id = f"WEEK3-RESP-{str(mcq_num).zfill(3)}"
        array_index = mcq_num - 1

        if mcq_id not in GENERATED_MCQS:
            print(f"  [ERROR] {mcq_id} not found")
            continue

        generated_mcq = GENERATED_MCQS[mcq_id]

        while len(current_mcqs) <= array_index:
            current_mcqs.append({})

        current_mcqs[array_index] = {
            "id": mcq_id,
            "question": generated_mcq["question"],
            "correct_answer": generated_mcq["correct_answer"],
            "explanation": generated_mcq["explanation"],
            "summary": generated_mcq.get("summary", ""),
            "citations": generated_mcq.get("citations", generated_mcq.get("references", [])),
            "metadata": generated_mcq.get("metadata", {
                "topic": "COPD Management",
                "difficulty": "intermediate",
                "australian_context": True
            }),
            "regenerated": True,
            "regeneration_timestamp": datetime.now().isoformat(),
            "regeneration_batch": "batch_2_copd_management_026_050",
            "regeneration_failed": False
        }
        update_count += 1

        if mcq_num % 5 == 0 or mcq_num == 50:
            print(f"  [OK] Updated up to {mcq_id} ({update_count}/25)")

    print(f"\n  [OK] Successfully updated: {update_count} MCQs")

    # Step 6: Save
    print()
    print(f"Step 6: Saving updated file...")
    main_data["mcqs"] = current_mcqs
    main_data["metadata"]["last_updated"] = datetime.now().isoformat()
    main_data["metadata"]["total_mcqs"] = len(current_mcqs)
    main_data["metadata"]["batch_2_complete"] = True

    with open(main_file, 'w') as f:
        json.dump(main_data, f, indent=2, ensure_ascii=False)
    print(f"  [OK] Saved successfully")

    # Validation
    print()
    print("=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    regenerated = sum(1 for mcq in current_mcqs if mcq.get("regenerated") and not mcq.get("regeneration_failed"))
    print(f"Total MCQs: {len(current_mcqs)}")
    print(f"Regenerated (all batches): {regenerated}")
    print(f"Batch 2 (COPD Management 026-050): {update_count}/25")
    print()
    print("Progress: 50/200 MCQs (25% complete)")
    print()
    print("=" * 80)
    print("BATCH 2 CONSOLIDATION COMPLETE")
    print("=" * 80)

    return 0

if __name__ == "__main__":
    sys.exit(main())
