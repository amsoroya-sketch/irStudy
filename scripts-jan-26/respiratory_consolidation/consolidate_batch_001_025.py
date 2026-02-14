#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Week 3 Respiratory MCQ Consolidation - Batch 1 (MCQs 001-025)
Asthma & Early COPD

Consolidates MCQs from:
- WEEK3_RESP_001_025_ASTHMA_COPD.py (25 MCQs)
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

    # Source file
    source_file = data_dir / "WEEK3_RESP_001_025_ASTHMA_COPD.py"
    main_file = data_dir / "week3_respiratory_200_mcqs.json"

    print("=" * 80)
    print("WEEK 3 RESPIRATORY - BATCH 1 CONSOLIDATION (MCQs 001-025)")
    print("=" * 80)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Step 1: Load source file
    print("Step 1: Loading source MCQ file...")
    print(f"  - Loading {source_file.name}...")
    GENERATED_MCQS = load_python_dict(source_file)
    print(f"    [OK] Loaded {len(GENERATED_MCQS)} MCQs")

    expected_ids = [f"WEEK3-RESP-{str(i).zfill(3)}" for i in range(1, 26)]
    actual_ids = sorted(GENERATED_MCQS.keys())

    if len(GENERATED_MCQS) != 25:
        print(f"  [WARNING] Expected 25 MCQs, got {len(GENERATED_MCQS)}")
        missing = set(expected_ids) - set(actual_ids)
        if missing:
            print(f"  [ERROR] Missing: {sorted(missing)}")
            return 1

    print(f"  [OK] All MCQ IDs present: {actual_ids[0]} to {actual_ids[-1]}")

    # Step 2: Load main file
    print()
    print(f"Step 2: Loading main MCQ file...")
    with open(main_file, 'r') as f:
        main_data = json.load(f)
    current_mcqs = main_data.get("mcqs", [])
    print(f"  [OK] Loaded {len(current_mcqs)} MCQs")

    # Step 3: Backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = main_file.parent / f"{main_file.stem}_backup_batch1_{timestamp}.json"
    print()
    print(f"Step 3: Creating backup...")
    with open(backup_file, 'w') as f:
        json.dump(main_data, f, indent=2, ensure_ascii=False)
    print(f"  [OK] Backup: {backup_file.name}")

    # Step 4: Update MCQs 001-025 (indices 0-24)
    print()
    print(f"Step 4: Updating MCQs 001-025...")
    update_count = 0

    for mcq_num in range(1, 26):
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
                "topic": "Asthma & COPD",
                "difficulty": "intermediate",
                "australian_context": True
            }),
            "regenerated": True,
            "regeneration_timestamp": datetime.now().isoformat(),
            "regeneration_batch": "batch_1_asthma_copd_001_025",
            "regeneration_failed": False
        }
        update_count += 1

        if mcq_num % 5 == 0 or mcq_num == 25:
            print(f"  [OK] Updated up to {mcq_id} ({update_count}/25)")

    print(f"\n  [OK] Successfully updated: {update_count} MCQs")

    # Step 5: Save
    print()
    print(f"Step 5: Saving updated file...")
    main_data["mcqs"] = current_mcqs
    main_data["metadata"]["last_updated"] = datetime.now().isoformat()
    main_data["metadata"]["total_mcqs"] = len(current_mcqs)
    main_data["metadata"]["batch_1_complete"] = True

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
    print(f"Batch 1 (Asthma & COPD 001-025): {update_count}/25")
    print()
    print("=" * 80)
    print("BATCH 1 CONSOLIDATION COMPLETE")
    print("=" * 80)

    return 0

if __name__ == "__main__":
    sys.exit(main())
