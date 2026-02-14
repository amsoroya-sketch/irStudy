#!/usr/bin/env python3
"""
Analyze MCQ file structures to understand conversion needs
"""
import os
import re

def analyze_file(filepath):
    """Analyze a single file's structure"""

    filename = os.path.basename(filepath)
    print(f"\n{'='*80}")
    print(f"FILE: {filename}")
    print('='*80)

    with open(filepath, 'r') as f:
        lines = f.readlines()

    # Find variable assignment
    for i, line in enumerate(lines[:30]):
        if ' = [' in line or ' = {' in line:
            print(f"Line {i+1}: {line.strip()}")

            # Check format
            if ' = [' in line:
                var_name = line.split('=')[0].strip()
                print(f"  Format: LIST (variable: {var_name})")
                print(f"  ✗ NEEDS CONVERSION")
            elif ' = {' in line:
                var_name = line.split('=')[0].strip()
                print(f"  Format: DICT (variable: {var_name})")
                if var_name == 'GENERATED_MCQS':
                    print(f"  ✓ CORRECT FORMAT")
                else:
                    print(f"  ✗ WRONG VARIABLE NAME")
            break

    # Count MCQ IDs
    mcq_ids = []
    for line in lines:
        # Look for WEEK3-RESP-XXX patterns
        matches = re.findall(r'WEEK3-RESP-(\d+)', line)
        mcq_ids.extend(matches)

    if mcq_ids:
        mcq_ids = sorted(set(mcq_ids), key=int)
        print(f"  MCQ IDs found: {len(mcq_ids)}")
        print(f"  Range: WEEK3-RESP-{mcq_ids[0]} to WEEK3-RESP-{mcq_ids[-1]}")

    # Check for syntax errors
    content = ''.join(lines)
    try:
        compile(content, filename, 'exec')
        print(f"  ✓ No syntax errors")
    except SyntaxError as e:
        print(f"  ✗ SYNTAX ERROR at line {e.lineno}: {e.msg}")
        if e.lineno and e.lineno <= len(lines):
            print(f"     Context: {lines[e.lineno-1].strip()[:100]}")

    return {
        'filename': filename,
        'filepath': filepath,
        'line_count': len(lines),
        'mcq_count': len(mcq_ids),
        'mcq_range': (mcq_ids[0], mcq_ids[-1]) if mcq_ids else (None, None)
    }

def main():
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

    results = []
    for filename in files:
        filepath = os.path.join(base_path, filename)
        if os.path.exists(filepath):
            result = analyze_file(filepath)
            results.append(result)
        else:
            print(f"\n✗ FILE NOT FOUND: {filename}")

    print(f"\n{'='*80}")
    print("SUMMARY")
    print('='*80)
    for r in results:
        print(f"{r['filename']}: {r['mcq_count']} MCQs, {r['line_count']} lines")

if __name__ == '__main__':
    main()
