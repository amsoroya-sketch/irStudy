#!/usr/bin/env python3
"""
FINAL MCQ FILE CONVERTER
- Reads Python files containing MCQ lists
- Converts to dictionary format with GENERATED_MCQS
- Creates backups before modification
- Validates output
"""
import os
import sys
import json

# File list
FILES = [
    "/home/dev/Development/irStudy/data/mcqs/WEEK3_RESP_101_113_VTE_MANAGEMENT.py",
    "/home/dev/Development/irStudy/data/mcqs/WEEK3_RESP_114_125_THROMBOPHILIA_ILD.py",
    "/home/dev/Development/irStudy/data/mcqs/WEEK3_RESP_126_138_ILD_ADVANCED.py",
    "/home/dev/Development/irStudy/data/mcqs/WEEK3_RESP_139_150_PNEUMOCONIOSIS_ARDS.py",
    "/home/dev/Development/irStudy/data/mcqs/WEEK3_RESP_151_163_VENTILATION.py",
    "/home/dev/Development/irStudy/data/mcqs/WEEK3_RESP_164_175_PLEURAL_DISEASE.py",
    "/home/dev/Development/irStudy/data/mcqs/WEEK3_RESP_176_188_LUNG_CANCER.py"
]

def fix_common_syntax_errors(content):
    """Fix common syntax issues"""
    # Fix double closing braces that shouldn't be there
    lines = content.split('\n')
    fixed_lines = []
    for line in lines:
        # If line has }} but no opening {, likely an error
        if '}}' in line and line.count('{') == 0 and '"' not in line:
            line = line.replace('}}', '}')
        fixed_lines.append(line)
    return '\n'.join(fixed_lines)

def convert_mcq_file(filepath):
    """Convert one file from list to dict format"""

    filename = os.path.basename(filepath)
    print(f"\n{'='*70}")
    print(f"Processing: {filename}")
    print('='*70)

    # Read file
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            original_content = f.read()
    except Exception as e:
        print(f"✗ Cannot read file: {e}")
        return False

    # Fix syntax issues
    content = fix_common_syntax_errors(original_content)

    # Try to execute to get the data
    namespace = {}
    try:
        exec(content, namespace)
    except SyntaxError as e:
        print(f"✗ Syntax error at line {e.lineno}: {e.msg}")
        return False
    except Exception as e:
        print(f"✗ Execution error: {e}")
        return False

    # Find the MCQ data variable
    mcq_var_name = None
    mcq_data = None

    for var_name, value in namespace.items():
        if var_name.startswith('__'):
            continue

        if isinstance(value, list) and value and isinstance(value[0], dict):
            if 'id' in value[0] and 'WEEK3-RESP' in value[0].get('id', ''):
                mcq_var_name = var_name
                mcq_data = value
                print(f"Found MCQ list: {var_name} ({len(value)} items)")
                break

        if isinstance(value, dict) and var_name == 'GENERATED_MCQS':
            print(f"✓ Already in correct format: {len(value)} MCQs")
            return True

    if not mcq_data:
        print("✗ No MCQ data found in file")
        return False

    # Convert list to dictionary
    mcq_dict = {}
    for mcq in mcq_data:
        if 'id' not in mcq:
            print(f"⚠ Warning: MCQ missing 'id' field")
            continue

        mcq_id = mcq['id']
        # Create copy without 'id' field
        mcq_copy = {k: v for k, v in mcq.items() if k != 'id'}
        mcq_dict[mcq_id] = mcq_copy

    print(f"Converted {len(mcq_dict)} MCQs to dictionary format")

    # Generate Python code with proper formatting
    output_lines = ["# Respiratory MCQs - Week 3"]
    output_lines.append("# Auto-converted to dictionary format")
    output_lines.append("")
    output_lines.append("GENERATED_MCQS = " + json.dumps(mcq_dict, indent=4, ensure_ascii=False))

    new_content = '\n'.join(output_lines)

    # Convert JSON booleans to Python booleans
    new_content = new_content.replace(': true', ': True')
    new_content = new_content.replace(': false', ': False')
    new_content = new_content.replace(': null', ': None')

    # Write to file
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
            f.write('\n')  # Trailing newline
        print(f"✓ File written")
    except Exception as e:
        print(f"✗ Cannot write file: {e}")
        return False

    # Validate the new file
    try:
        namespace_check = {}
        exec(new_content, namespace_check)

        if 'GENERATED_MCQS' not in namespace_check:
            print(f"✗ GENERATED_MCQS not found in new file")
            return False

        result_dict = namespace_check['GENERATED_MCQS']
        count = len(result_dict)
        print(f"✓ Validation passed: {count} MCQs")

        # Show ID range
        if result_dict:
            ids_sorted = sorted(result_dict.keys(),
                              key=lambda x: int(x.split('-')[-1]))
            first_id = ids_sorted[0]
            last_id = ids_sorted[-1]
            print(f"✓ ID range: {first_id} to {last_id}")

        return True

    except Exception as e:
        print(f"✗ Validation failed: {e}")
        return False

def main():
    """Main conversion process"""

    print("="*70)
    print("MCQ File Structure Converter")
    print("="*70)
    print("")

    # Step 1: Create backups
    print("STEP 1: Creating backups...")
    print("-"*70)
    for filepath in FILES:
        if os.path.exists(filepath):
            backup_path = filepath + '.BACKUP'
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✓ Backed up: {os.path.basename(filepath)}")
            except Exception as e:
                print(f"✗ Backup failed for {os.path.basename(filepath)}: {e}")
        else:
            print(f"⚠ Not found: {os.path.basename(filepath)}")

    # Step 2: Convert files
    print("\nSTEP 2: Converting files...")
    print("-"*70)

    results = {}
    for filepath in FILES:
        if os.path.exists(filepath):
            success = convert_mcq_file(filepath)
            results[filepath] = success

            if not success:
                # Restore from backup
                backup_path = filepath + '.BACKUP'
                print(f"⚠ Restoring from backup due to failure...")
                try:
                    with open(backup_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"✓ Restored original file")
                except:
                    print(f"✗ Could not restore backup")
        else:
            results[filepath] = False

    # Step 3: Summary
    print("\n" + "="*70)
    print("CONVERSION SUMMARY")
    print("="*70)

    success_count = 0
    for filepath, success in results.items():
        filename = os.path.basename(filepath)
        if success:
            print(f"✓ SUCCESS: {filename}")
            success_count += 1
        else:
            print(f"✗ FAILED:  {filename}")

    print(f"\nResult: {success_count}/{len(FILES)} files converted successfully")

    if success_count == len(FILES):
        print("\n" + "="*70)
        print("✓ ALL FILES CONVERTED SUCCESSFULLY!")
        print("="*70)
        print("\nBackup files created with .BACKUP extension")
        print("You can delete them after verifying the conversion.")
        print("\nNext step:")
        print("  python3 scripts/consolidate_week3_respiratory_mcqs.py")
        return 0
    else:
        print("\n" + "="*70)
        print("✗ SOME FILES FAILED - Check errors above")
        print("="*70)
        print("\nFailed files have been restored from backup.")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
