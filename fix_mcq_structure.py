#!/usr/bin/env python3
"""
Quick diagnostic script to check MCQ file structures
"""
import os
import json

files = [
    "WEEK3_RESP_101_113_VTE_MANAGEMENT.py",
    "WEEK3_RESP_114_125_THROMBOPHILIA_ILD.py",
    "WEEK3_RESP_126_138_ILD_ADVANCED.py",
    "WEEK3_RESP_139_150_PNEUMOCONIOSIS_ARDS.py",
    "WEEK3_RESP_151_163_VENTILATION.py",
    "WEEK3_RESP_164_175_PLEURAL_DISEASE.py",
    "WEEK3_RESP_176_188_LUNG_CANCER.py"
]

base_path = "/home/dev/Development/irStudy/data/mcqs/"

for filename in files:
    filepath = os.path.join(base_path, filename)
    print(f"\n{'='*80}")
    print(f"FILE: {filename}")
    print('='*80)

    try:
        with open(filepath, 'r') as f:
            content = f.read()

        # Check for variable names
        if "GENERATED_MCQS = {" in content:
            print("✓ Already has GENERATED_MCQS dictionary format")
        elif "GENERATED_MCQS = [" in content:
            print("✗ Has GENERATED_MCQS but in LIST format (needs conversion)")
        elif " = [" in content[:500]:
            # Find the variable name
            for line in content.split('\n')[:20]:
                if ' = [' in line:
                    print(f"✗ Has custom variable: {line.strip()[:80]}...")
                    break
        else:
            print("? Unknown format")

        # Check for syntax errors
        try:
            compile(content, filename, 'exec')
            print("✓ No syntax errors")
        except SyntaxError as e:
            print(f"✗ SYNTAX ERROR: Line {e.lineno}: {e.msg}")
            if e.lineno:
                lines = content.split('\n')
                start = max(0, e.lineno - 3)
                end = min(len(lines), e.lineno + 2)
                print("\nContext:")
                for i in range(start, end):
                    marker = ">>> " if i == e.lineno - 1 else "    "
                    print(f"{marker}{i+1:4d}: {lines[i][:100]}")

    except FileNotFoundError:
        print(f"✗ FILE NOT FOUND: {filepath}")
    except Exception as e:
        print(f"✗ ERROR: {e}")

print("\n" + "="*80)
