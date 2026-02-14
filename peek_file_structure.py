#!/usr/bin/env python3
"""Quick peek at file structure"""
import os

filepath = "/home/dev/Development/irStudy/data/mcqs/WEEK3_RESP_114_125_THROMBOPHILIA_ILD.py"

with open(filepath, 'r') as f:
    lines = f.readlines()

print("First 30 lines:")
print('='*80)
for i, line in enumerate(lines[:30], 1):
    print(f"{i:3d}: {line.rstrip()}")

print('\n'+'='*80)
print(f"Total lines: {len(lines)}")

# Count MCQ IDs
import re
ids = []
for line in lines:
    matches = re.findall(r'WEEK3-RESP-(\d+)', line)
    ids.extend(matches)

unique_ids = sorted(set(ids), key=int)
print(f"MCQ IDs found: {len(unique_ids)}")
if unique_ids:
    print(f"Range: WEEK3-RESP-{unique_ids[0]} to WEEK3-RESP-{unique_ids[-1]}")
