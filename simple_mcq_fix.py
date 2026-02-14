#!/usr/bin/env python3
"""
Simple and safe MCQ file converter using AST parsing
"""
import os
import ast
import json

def convert_mcq_file(filepath):
    """Convert MCQ file from list to dict format using AST parsing"""

    filename = os.path.basename(filepath)
    print(f"\n{'='*80}")
    print(f"Processing: {filename}")
    print('='*80)

    # Read file
    with open(filepath, 'r') as f:
        content = f.read()

    # Try to parse as Python AST
    try:
        tree = ast.parse(content, filename=filename)
    except SyntaxError as e:
        print(f"  ✗ SYNTAX ERROR at line {e.lineno}: {e.msg}")
        print(f"  Attempting to fix common syntax errors...")

        # Common fix: bracket mismatches
        # Read file line by line
        lines = content.split('\n')
        if e.lineno and e.lineno <= len(lines):
            error_line_idx = e.lineno - 1
            print(f"  Error line: {lines[error_line_idx][:100]}")

            # Try simple fixes
            # 1. Double closing braces
            if '}}' in lines[error_line_idx]:
                lines[error_line_idx] = lines[error_line_idx].replace('}}', '}')
                content = '\n'.join(lines)
                print(f"  Fixed double closing braces")
                try:
                    tree = ast.parse(content, filename=filename)
                    print(f"  ✓ Syntax error fixed!")
                except SyntaxError as e2:
                    print(f"  ✗ Still have syntax error: {e2.msg}")
                    return False

    # Find the assignment
    var_name = None
    var_value = None

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                var_name = node.targets[0].id
                var_value = node.value
                print(f"  Found variable: {var_name}")
                break

    if not var_name or not var_value:
        print(f"  ✗ Could not find variable assignment")
        return False

    # Check if it's a list
    if not isinstance(var_value, ast.List):
        if isinstance(var_value, ast.Dict):
            if var_name == 'GENERATED_MCQS':
                print(f"  ✓ Already in correct format (dictionary)")
                # Verify the content
                namespace = {}
                exec(content, namespace)
                if 'GENERATED_MCQS' in namespace:
                    count = len(namespace['GENERATED_MCQS'])
                    print(f"  ✓ Verified: {count} MCQs")
                    return True
            else:
                print(f"  ✗ Wrong variable name: {var_name} (should be GENERATED_MCQS)")
        else:
            print(f"  ✗ Not a list or dict: {type(var_value)}")
        return False

    print(f"  Converting from list to dictionary format...")

    # Execute to get the actual data
    namespace = {}
    exec(content, namespace)

    mcq_list = namespace.get(var_name)
    if not mcq_list:
        print(f"  ✗ Could not extract {var_name}")
        return False

    print(f"  Extracted {len(mcq_list)} MCQs from list")

    # Convert to dictionary
    mcq_dict = {}
    for mcq in mcq_list:
        if isinstance(mcq, dict) and 'id' in mcq:
            mcq_id = mcq['id']
            # Remove 'id' key as it's now the dictionary key
            mcq_copy = mcq.copy()
            del mcq_copy['id']
            mcq_dict[mcq_id] = mcq_copy
        else:
            print(f"  ⚠ Warning: MCQ missing 'id' field")

    print(f"  Created dictionary with {len(mcq_dict)} MCQs")

    # Generate Python source code
    new_content = generate_python_dict(mcq_dict)

    # Write back
    with open(filepath, 'w') as f:
        f.write(new_content)

    print(f"  ✓ File written")

    # Validate
    try:
        namespace = {}
        exec(new_content, namespace)
        if 'GENERATED_MCQS' in namespace:
            count = len(namespace['GENERATED_MCQS'])
            print(f"  ✓ Validation passed: {count} MCQs")

            # Verify IDs match expected range
            ids = sorted(namespace['GENERATED_MCQS'].keys(),
                        key=lambda x: int(x.split('-')[-1]))
            if ids:
                first_id = int(ids[0].split('-')[-1])
                last_id = int(ids[-1].split('-')[-1])
                print(f"  ✓ ID range: WEEK3-RESP-{first_id:03d} to WEEK3-RESP-{last_id:03d}")

            return True
        else:
            print(f"  ✗ GENERATED_MCQS not found")
            return False
    except Exception as e:
        print(f"  ✗ Validation error: {e}")
        import traceback
        traceback.print_exc()
        return False

def generate_python_dict(mcq_dict):
    """Generate Python source code for GENERATED_MCQS dictionary"""

    lines = ["# Generated MCQ dictionary"]
    lines.append("GENERATED_MCQS = {")

    # Sort by MCQ ID number
    sorted_ids = sorted(mcq_dict.keys(), key=lambda x: int(x.split('-')[-1]))

    for i, mcq_id in enumerate(sorted_ids):
        mcq = mcq_dict[mcq_id]

        # Use json.dumps for safe serialization, then convert to Python format
        mcq_json = json.dumps(mcq, indent=4, ensure_ascii=False)

        # Convert JSON to Python format
        # Replace 'true' with 'True', 'false' with 'False', 'null' with 'None'
        mcq_python = mcq_json.replace('true', 'True').replace('false', 'False').replace('null', 'None')

        # Indent for dictionary entry
        mcq_lines = mcq_python.split('\n')
        indented_lines = ['    ' + line for line in mcq_lines]

        # Add the MCQ ID as key
        lines.append(f'    "{mcq_id}": {{')

        # Add the MCQ content (skip first and last lines which are {})
        for line in indented_lines[1:-1]:
            lines.append(line)

        # Close this MCQ entry
        if i < len(sorted_ids) - 1:
            lines.append('    },')
        else:
            lines.append('    }')

    lines.append('}')

    return '\n'.join(lines)

def main():
    """Main conversion process"""

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

    results = {}

    for filename in files:
        filepath = os.path.join(base_path, filename)

        if not os.path.exists(filepath):
            print(f"\n✗ FILE NOT FOUND: {filepath}")
            results[filename] = False
            continue

        # Create backup
        backup_path = filepath + '.backup'
        with open(filepath, 'r') as f:
            backup_content = f.read()
        with open(backup_path, 'w') as f:
            f.write(backup_content)
        print(f"Created backup: {os.path.basename(backup_path)}")

        # Convert
        success = convert_mcq_file(filepath)
        results[filename] = success

        if not success:
            # Restore from backup
            print(f"  Restoring from backup...")
            with open(backup_path, 'r') as f:
                content = f.read()
            with open(filepath, 'w') as f:
                f.write(content)

    # Summary report
    print(f"\n{'='*80}")
    print("CONVERSION SUMMARY")
    print('='*80)

    for filename, success in results.items():
        status = "✓ SUCCESS" if success else "✗ FAILED"
        print(f"{status}: {filename}")

    success_count = sum(1 for v in results.values() if v)
    total_count = len(results)

    print(f"\n{success_count}/{total_count} files converted successfully")

    if success_count == total_count:
        print("\n✓ ALL FILES CONVERTED SUCCESSFULLY")
        print("\nNext steps:")
        print("1. Run: python3 scripts/consolidate_week3_respiratory_mcqs.py")
        print("2. Verify: python3 -m pytest tests/test_week3_respiratory.py")
        print("\nBackup files (*.backup) can be deleted after verification.")
        return True
    else:
        print("\n✗ SOME FILES FAILED")
        print("Failed files have been restored from backup.")
        print("Review errors above for details.")
        return False

if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)
