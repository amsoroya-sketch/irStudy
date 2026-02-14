#!/usr/bin/env python3
"""
Final MCQ file fixer - converts list format to dictionary format
Handles syntax errors and validates output
"""
import os
import sys
import ast
import json
import re

def fix_syntax_errors(content):
    """Fix common syntax errors before parsing"""
    lines = content.split('\n')

    # Fix double closing braces
    for i, line in enumerate(lines):
        if '}}' in line and '{' not in line and '"' not in line:
            # Likely an error - replace }} with }
            lines[i] = line.replace('}}', '}')

    return '\n'.join(lines)

def convert_file(filepath):
    """Convert a single file"""

    filename = os.path.basename(filepath)
    print(f"\n{'='*80}")
    print(f"File: {filename}")
    print('='*80)

    # Read
    with open(filepath, 'r') as f:
        content = f.read()

    # Try to fix syntax errors first
    content_fixed = fix_syntax_errors(content)

    # Parse to check format
    try:
        tree = ast.parse(content_fixed)
    except SyntaxError as e:
        print(f"✗ Syntax error at line {e.lineno}: {e.msg}")
        return False

    # Find the variable assignment
    var_name = None
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Assign):
            if len(node.targets) == 1:
                target = node.targets[0]
                if isinstance(target, ast.Name):
                    var_name = target.id
                    var_type = type(node.value).__name__
                    print(f"Found: {var_name} = {var_type}")

                    # Check if already correct
                    if var_name == 'GENERATED_MCQS' and var_type == 'Dict':
                        print("✓ Already in correct format")
                        # Validate
                        namespace = {}
                        exec(content_fixed, namespace)
                        count = len(namespace.get('GENERATED_MCQS', {}))
                        print(f"✓ Contains {count} MCQs")
                        return True

                    # Check if needs conversion
                    if var_type == 'List':
                        print(f"→ Converting from list to dict")
                        break

    if not var_name:
        print("✗ No variable assignment found")
        return False

    # Execute to get the data
    namespace = {}
    exec(content_fixed, namespace)

    mcq_list = namespace.get(var_name, [])
    print(f"Extracted {len(mcq_list)} items from {var_name}")

    # Convert to dictionary
    mcq_dict = {}
    for item in mcq_list:
        if isinstance(item, dict) and 'id' in item:
            mcq_id = item['id']
            mcq_data = {k: v for k, v in item.items() if k != 'id'}
            mcq_dict[mcq_id] = mcq_data

    print(f"Converted to {len(mcq_dict)} MCQ dictionary entries")

    # Generate new Python code
    new_content = "GENERATED_MCQS = " + json.dumps(mcq_dict, indent=4, ensure_ascii=False)

    # Convert JSON booleans to Python
    new_content = new_content.replace('true', 'True').replace('false', 'False').replace('null', 'None')

    # Write
    with open(filepath, 'w') as f:
        f.write(new_content)
        f.write('\n')

    print("✓ File written")

    # Validate
    try:
        namespace = {}
        exec(new_content, namespace)
        result_dict = namespace.get('GENERATED_MCQS', {})
        count = len(result_dict)
        print(f"✓ Validation passed: {count} MCQs")

        # Check ID range
        if result_dict:
            ids = sorted(result_dict.keys(), key=lambda x: int(x.split('-')[-1]))
            first_num = int(ids[0].split('-')[-1])
            last_num = int(ids[-1].split('-')[-1])
            print(f"✓ ID range: {first_num:03d}-{last_num:03d}")

        return True

    except Exception as e:
        print(f"✗ Validation failed: {e}")
        return False

def main():
    """Process all files"""

    files = [
        "/home/dev/Development/irStudy/data/mcqs/WEEK3_RESP_101_113_VTE_MANAGEMENT.py",
        "/home/dev/Development/irStudy/data/mcqs/WEEK3_RESP_114_125_THROMBOPHILIA_ILD.py",
        "/home/dev/Development/irStudy/data/mcqs/WEEK3_RESP_126_138_ILD_ADVANCED.py",
        "/home/dev/Development/irStudy/data/mcqs/WEEK3_RESP_139_150_PNEUMOCONIOSIS_ARDS.py",
        "/home/dev/Development/irStudy/data/mcqs/WEEK3_RESP_151_163_VENTILATION.py",
        "/home/dev/Development/irStudy/data/mcqs/WEEK3_RESP_164_175_PLEURAL_DISEASE.py",
        "/home/dev/Development/irStudy/data/mcqs/WEEK3_RESP_176_188_LUNG_CANCER.py"
    ]

    # Create backups
    print("Creating backups...")
    for filepath in files:
        if os.path.exists(filepath):
            backup = filepath + '.backup'
            with open(filepath, 'r') as f:
                content = f.read()
            with open(backup, 'w') as f:
                f.write(content)
            print(f"✓ Backed up: {os.path.basename(filepath)}")

    # Convert
    results = {}
    for filepath in files:
        if os.path.exists(filepath):
            success = convert_file(filepath)
            results[filepath] = success

            if not success:
                # Restore backup
                backup = filepath + '.backup'
                print(f"⚠ Restoring from backup...")
                with open(backup, 'r') as f:
                    content = f.read()
                with open(filepath, 'w') as f:
                    f.write(content)
        else:
            print(f"\n✗ Not found: {filepath}")
            results[filepath] = False

    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print('='*80)

    success_count = 0
    for filepath, success in results.items():
        filename = os.path.basename(filepath)
        status = "✓" if success else "✗"
        print(f"{status} {filename}")
        if success:
            success_count += 1

    print(f"\n{success_count}/{len(results)} files converted successfully")

    if success_count == len(results):
        print("\n✓ ALL FILES FIXED!")
        print("\nNext step: Run consolidation script")
        return 0
    else:
        print("\n✗ Some files failed - restored from backup")
        return 1

if __name__ == '__main__':
    sys.exit(main())
