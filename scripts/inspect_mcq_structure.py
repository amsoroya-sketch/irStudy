#!/usr/bin/env python3
"""Quick inspection of MCQ file structure before applying SAFE-T fixes."""

import json
from pathlib import Path

mcq_file = Path("/home/dev/Development/irStudy/data/mcqs/week1_all_100_unique_mcqs.json")

if not mcq_file.exists():
    print(f"ERROR: File not found: {mcq_file}")
    exit(1)

print(f"Reading: {mcq_file}")
print(f"File size: {mcq_file.stat().st_size:,} bytes")
print()

with open(mcq_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

mcqs = data.get("mcqs", [])
print(f"Total MCQs: {len(mcqs)}")
print()

# Sample MCQ structure
if len(mcqs) > 0:
    sample = mcqs[0]
    print("Sample MCQ structure:")
    print(f"  mcq_id: {sample.get('mcq_id')}")
    print(f"  scenario length: {len(sample.get('scenario', ''))} chars")
    print(f"  stem length: {len(sample.get('stem', ''))} chars")
    print(f"  options count: {len(sample.get('options', []))}")
    print(f"  key_points count: {len(sample.get('key_points', []))}")
    print(f"  has explanation: {bool(sample.get('explanation'))}")
    print()

# Count psychiatry MCQs
psy_mcqs = {
    "PSY-DEP": 0,
    "PSY-SUICIDE-MHA": 0,
    "PSY-MHA": 0,
    "PSY-PSYCHOSIS": 0,
    "PSY-ANX": 0,
    "Other PSY": 0
}

for mcq in mcqs:
    mcq_id = mcq.get("mcq_id", "")
    if "PSY-DEP" in mcq_id:
        psy_mcqs["PSY-DEP"] += 1
    elif "PSY-SUICIDE-MHA" in mcq_id:
        psy_mcqs["PSY-SUICIDE-MHA"] += 1
    elif "PSY-MHA" in mcq_id:
        psy_mcqs["PSY-MHA"] += 1
    elif "PSY-PSYCHOSIS" in mcq_id:
        psy_mcqs["PSY-PSYCHOSIS"] += 1
    elif "PSY-ANX" in mcq_id:
        psy_mcqs["PSY-ANX"] += 1
    elif mcq_id.startswith("PSY-"):
        psy_mcqs["Other PSY"] += 1

print("Psychiatry MCQ breakdown:")
for category, count in psy_mcqs.items():
    if count > 0:
        print(f"  {category}: {count}")
print()

# Check for existing SAFE-T content
safet_count = 0
for mcq in mcqs:
    if mcq.get("mcq_id", "").startswith("PSY-"):
        key_points = " ".join(mcq.get("key_points", []))
        if "SAFE-T" in key_points or "suicide risk assessment" in key_points.lower():
            safet_count += 1

total_psy = sum(psy_mcqs.values())
print(f"Psychiatry MCQs with SAFE-T content: {safet_count}/{total_psy}")
print()

# Show 1 depression MCQ example
for mcq in mcqs:
    if "PSY-DEP" in mcq.get("mcq_id", ""):
        print("Example Depression MCQ:")
        print(f"  ID: {mcq.get('mcq_id')}")
        print(f"  Scenario: {mcq.get('scenario', '')[:200]}...")
        print(f"  Key points ({len(mcq.get('key_points', []))}):")
        for kp in mcq.get('key_points', [])[:3]:
            print(f"    - {kp[:100]}")
        print(f"  Reference: {mcq.get('explanation', {}).get('reference', 'N/A')}")
        break

print()
print("Inspection complete ✓")
