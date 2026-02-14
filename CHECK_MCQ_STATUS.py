#!/usr/bin/env python3
"""
MCQ Status Checker
Quick diagnostic to show current state of all 7 respiratory MCQ files
"""
import os
import sys

FILES = [
    "/home/dev/Development/irStudy/data/mcqs/WEEK3_RESP_101_113_VTE_MANAGEMENT.py",
    "/home/dev/Development/irStudy/data/mcqs/WEEK3_RESP_114_125_THROMBOPHILIA_ILD.py",
    "/home/dev/Development/irStudy/data/mcqs/WEEK3_RESP_126_138_ILD_ADVANCED.py",
    "/home/dev/Development/irStudy/data/mcqs/WEEK3_RESP_139_150_PNEUMOCONIOSIS_ARDS.py",
    "/home/dev/Development/irStudy/data/mcqs/WEEK3_RESP_151_163_VENTILATION.py",
    "/home/dev/Development/irStudy/data/mcqs/WEEK3_RESP_164_175_PLEURAL_DISEASE.py",
    "/home/dev/Development/irStudy/data/mcqs/WEEK3_RESP_176_188_LUNG_CANCER.py"
]

def check_file(filepath):
    """Check one file's status"""
    filename = os.path.basename(filepath)

    if not os.path.exists(filepath):
        return {
            'filename': filename,
            'status': 'NOT_FOUND',
            'format': None,
            'count': 0,
            'has_backup': False
        }

    # Check for backup
    has_backup = os.path.exists(filepath + '.BACKUP')

    # Read file
    with open(filepath, 'r') as f:
        content = f.read()

    # Check format
    has_generated_mcqs = 'GENERATED_MCQS = {' in content
    has_list_format = ' = [' in content[:500]

    if has_generated_mcqs:
        format_type = 'DICT ✓'
        status = 'READY'
    elif has_list_format:
        format_type = 'LIST ✗'
        status = 'NEEDS_FIX'
    else:
        format_type = 'UNKNOWN'
        status = 'ERROR'

    # Try to get count
    count = 0
    try:
        namespace = {}
        exec(content, namespace)

        if 'GENERATED_MCQS' in namespace:
            count = len(namespace['GENERATED_MCQS'])
        else:
            # Find any list variable
            for key, value in namespace.items():
                if not key.startswith('__') and isinstance(value, list):
                    count = len(value)
                    break
    except:
        pass

    return {
        'filename': filename,
        'status': status,
        'format': format_type,
        'count': count,
        'has_backup': has_backup
    }

def main():
    """Check all files and print status report"""

    print("="*80)
    print(" MCQ File Status Report")
    print("="*80)
    print("")

    results = []
    for filepath in FILES:
        result = check_file(filepath)
        results.append(result)

    # Print table header
    print(f"{'File':<45} {'Status':<12} {'Format':<10} {'Count':<6} {'Backup':<6}")
    print("-"*80)

    # Print results
    total_count = 0
    ready_count = 0
    for r in results:
        filename_short = r['filename'].replace('WEEK3_RESP_', '')
        status_icon = "✓" if r['status'] == 'READY' else "✗" if r['status'] == 'NEEDS_FIX' else "?"
        backup_icon = "✓" if r['has_backup'] else " "

        print(f"{filename_short:<45} {status_icon} {r['status']:<10} {r['format']:<10} {r['count']:<6} {backup_icon:<6}")

        total_count += r['count']
        if r['status'] == 'READY':
            ready_count += 1

    print("-"*80)
    print(f"Total MCQs: {total_count}")
    print(f"Ready files: {ready_count}/{len(results)}")
    print("")

    # Summary
    if ready_count == len(results):
        print("✓ ALL FILES READY - No conversion needed")
        print("")
        print("Next step: Run consolidation")
        print("  python3 scripts/consolidate_week3_respiratory_mcqs.py")
        return 0
    elif ready_count == 0:
        print("✗ ALL FILES NEED CONVERSION")
        print("")
        print("Run the converter:")
        print("  bash RUN_MCQ_CONVERSION.sh")
        print("  OR")
        print("  python3 FINAL_MCQ_CONVERTER.py")
        return 1
    else:
        print(f"⚠ PARTIAL: {ready_count} ready, {len(results) - ready_count} need conversion")
        print("")
        print("Run the converter to fix remaining files:")
        print("  bash RUN_MCQ_CONVERSION.sh")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
