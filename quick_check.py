#!/usr/bin/env python3
import os

# Check one file's first 50 lines
filepath = "/home/dev/Development/irStudy/data/mcqs/WEEK3_RESP_114_125_THROMBOPHILIA_ILD.py"

if os.path.exists(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()[:50]

    print(f"First 50 lines of {os.path.basename(filepath)}:")
    print('='*80)
    for i, line in enumerate(lines, 1):
        print(f"{i:3}: {line.rstrip()}")
else:
    print(f"File not found: {filepath}")
