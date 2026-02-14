#!/usr/bin/env python3
"""
Comprehensive file structure analyzer
Shows exactly what needs to be fixed in each file
"""
import os
import re
import ast

def analyze_detailed(filepath):
    """Detailed analysis of a file"""

    filename = os.path.basename(filepath)
    print(f"\n{'='*80}")
    print(f"ANALYZING: {filename}")
    print('='*80)

    if not os.path.exists(filepath):
        print("✗ FILE NOT FOUND")
        return None

    with open(filepath, 'r') as f:
        content = f.read()
        lines = content.split('\n')

    print(f"Total lines: {len(lines)}")
    print(f"File size: {len(content)} bytes")

    # Find variable assignment in first 20 lines
    print("\nVariable assignment (first 20 lines):")
    for i, line in enumerate(lines[:20]):
        if '=' in line and not line.strip().startswith('#'):
            print(f"  Line {i+1}: {line[:100]}")
            if ' = [' in line:
                print("    → LIST format detected")
            elif ' = {' in line:
                print("    → DICT format detected")

    # Try to parse as Python
    print("\nSyntax check:")
    try:
        tree = ast.parse(content)
        print("  ✓ Valid Python syntax")

        # Find assignments
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        var_name = target.id
                        var_type = type(node.value).__name__
                        print(f"  Assignment: {var_name} = <{var_type}>")

    except SyntaxError as e:
        print(f"  ✗ SYNTAX ERROR at line {e.lineno}: {e.msg}")
        if e.lineno and e.lineno <= len(lines):
            print(f"  Error context:")
            start = max(0, e.lineno - 3)
            end = min(len(lines), e.lineno + 3)
            for i in range(start, end):
                marker = " >>>" if i == e.lineno - 1 else "    "
                print(f"{marker} {i+1:4}: {lines[i][:80]}")

    # Count MCQ IDs
    print("\nMCQ IDs:")
    mcq_ids = []
    for line in lines:
        matches = re.findall(r'WEEK3-RESP-(\d+)', line)
        mcq_ids.extend(matches)

    unique_ids = sorted(set(mcq_ids), key=int)
    if unique_ids:
        print(f"  Found {len(unique_ids)} unique IDs")
        print(f"  Range: WEEK3-RESP-{unique_ids[0]} to WEEK3-RESP-{unique_ids[-1]}")
        print(f"  Expected from filename: {filename.split('_')[2]}_{filename.split('_')[3].replace('.py', '')}")
    else:
        print("  ✗ No MCQ IDs found")

    # Try to execute and extract data
    print("\nData extraction test:")
    try:
        namespace = {}
        exec(content, namespace)

        # Find the MCQ data
        for key, value in namespace.items():
            if not key.startswith('__') and isinstance(value, (list, dict)):
                if isinstance(value, list):
                    print(f"  Found list: {key} with {len(value)} items")
                    if value and isinstance(value[0], dict):
                        print(f"    First item keys: {list(value[0].keys())[:5]}")
                elif isinstance(value, dict):
                    print(f"  Found dict: {key} with {len(value)} items")
                    first_key = list(value.keys())[0] if value else None
                    if first_key:
                        print(f"    First key: {first_key}")
                        print(f"    First value keys: {list(value[first_key].keys())[:5]}")

    except Exception as e:
        print(f"  ✗ Execution error: {e}")

    return {
        'filename': filename,
        'filepath': filepath,
        'has_syntax_error': False,  # Will be updated by actual run
        'ids_found': len(unique_ids),
        'id_range': (unique_ids[0], unique_ids[-1]) if unique_ids else (None, None)
    }

def main():
    """Analyze all files"""

    files = [
        "/home/dev/Development/irStudy/data/mcqs/WEEK3_RESP_101_113_VTE_MANAGEMENT.py",
        "/home/dev/Development/irStudy/data/mcqs/WEEK3_RESP_114_125_THROMBOPHILIA_ILD.py",
        "/home/dev/Development/irStudy/data/mcqs/WEEK3_RESP_126_138_ILD_ADVANCED.py",
        "/home/dev/Development/irStudy/data/mcqs/WEEK3_RESP_139_150_PNEUMOCONIOSIS_ARDS.py",
        "/home/dev/Development/irStudy/data/mcqs/WEEK3_RESP_151_163_VENTILATION.py",
        "/home/dev/Development/irStudy/data/mcqs/WEEK3_RESP_164_175_PLEURAL_DISEASE.py",
        "/home/dev/Development/irStudy/data/mcqs/WEEK3_RESP_176_188_LUNG_CANCER.py"
    ]

    results = []
    for filepath in files:
        result = analyze_detailed(filepath)
        if result:
            results.append(result)

    # Summary
    print(f"\n{'='*80}")
    print("ANALYSIS SUMMARY")
    print('='*80)
    for r in results:
        print(f"\n{r['filename']}:")
        print(f"  MCQs: {r['ids_found']}")
        if r['id_range'][0]:
            print(f"  Range: {r['id_range'][0]}-{r['id_range'][1]}")

    print(f"\n{'='*80}")
    print("Ready to proceed with conversion using fix_all_mcq_files.py")
    print('='*80)

if __name__ == '__main__':
    main()
