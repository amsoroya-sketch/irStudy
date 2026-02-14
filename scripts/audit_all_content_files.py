#!/usr/bin/env python3
"""
Comprehensive Content Audit Script
Checks ALL MCQ/OSCE/Study Card files for placeholder content
Generates detailed report of regeneration scope

Usage: python3 scripts/audit_all_content_files.py
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

# Paths
PROJECT_ROOT = Path("/home/dev/Development/irStudy")
VALIDATOR_SCRIPT = PROJECT_ROOT / "scripts" / "validate_content_substance.sh"

def count_items_in_file(file_path: Path) -> int:
    """Count the number of items in a JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Handle different structures
        if isinstance(data, dict):
            if 'mcqs' in data:
                return len(data['mcqs'])
            elif 'osces' in data:
                return len(data['osces'])
            elif 'study_cards' in data:
                return len(data['study_cards'])
            elif 'cards' in data:
                return len(data['cards'])
            else:
                # Might be a single item
                return 1
        elif isinstance(data, list):
            return len(data)
        else:
            return 0
    except Exception as e:
        print(f"  ❌ ERROR counting items in {file_path.name}: {e}")
        return 0

def validate_file(file_path: Path) -> Tuple[bool, int]:
    """
    Validate a file using the content substance validator.
    Returns: (passed: bool, placeholder_count: int)
    """
    try:
        result = subprocess.run(
            ["bash", str(VALIDATOR_SCRIPT), str(file_path)],
            capture_output=True,
            text=True,
            timeout=30
        )

        # Exit code 0 = PASS, Exit code 2 = FAIL (placeholders)
        passed = result.returncode == 0

        # Extract placeholder count from output
        placeholder_count = 0
        for line in result.stdout.split('\n') + result.stderr.split('\n'):
            if 'placeholder patterns detected' in line.lower():
                # Extract number from "❌ VALIDATION FAILED: 1400 placeholder patterns detected"
                parts = line.split()
                for i, part in enumerate(parts):
                    if 'placeholder' in part.lower() and i > 0:
                        try:
                            placeholder_count = int(parts[i-1])
                            break
                        except (ValueError, IndexError):
                            pass

        return (passed, placeholder_count)

    except subprocess.TimeoutExpired:
        print(f"  ⏱️  TIMEOUT validating {file_path.name}")
        return (False, 0)
    except Exception as e:
        print(f"  ❌ ERROR validating {file_path.name}: {e}")
        return (False, 0)

def audit_all_files():
    """Audit all MCQ/OSCE/Study Card files and generate report."""

    print("━" * 80)
    print("🔍 COMPREHENSIVE CONTENT AUDIT")
    print("━" * 80)
    print()

    # File categories
    file_patterns = {
        'MCQs': PROJECT_ROOT / "data" / "mcqs" / "*.json",
        'OSCEs': PROJECT_ROOT / "data" / "osces" / "*.json",
        'Study Cards': PROJECT_ROOT / "data" / "study_cards" / "*.json"
    }

    # Results storage
    results = {
        'passed': [],
        'failed': [],
        'total_items': 0,
        'items_needing_regeneration': 0,
        'total_placeholder_patterns': 0
    }

    # Audit each category
    for category, pattern in file_patterns.items():
        print(f"📂 {category}")
        print(f"   Pattern: {pattern}")
        print()

        files = sorted(PROJECT_ROOT.glob(str(pattern).replace(str(PROJECT_ROOT) + "/", "")))

        if not files:
            print(f"   ℹ️  No files found\n")
            continue

        for file_path in files:
            # Count items
            item_count = count_items_in_file(file_path)
            results['total_items'] += item_count

            # Validate
            passed, placeholder_count = validate_file(file_path)

            if passed:
                results['passed'].append({
                    'file': file_path.name,
                    'category': category,
                    'items': item_count,
                    'status': 'PASS'
                })
                print(f"   ✅ {file_path.name} ({item_count} items) - PASSED")
            else:
                results['failed'].append({
                    'file': file_path.name,
                    'category': category,
                    'items': item_count,
                    'status': 'FAIL',
                    'placeholder_patterns': placeholder_count
                })
                results['items_needing_regeneration'] += item_count
                results['total_placeholder_patterns'] += placeholder_count
                print(f"   ❌ {file_path.name} ({item_count} items) - FAILED ({placeholder_count} placeholders)")

        print()

    # Generate summary report
    print("━" * 80)
    print("📊 AUDIT SUMMARY")
    print("━" * 80)
    print()

    print(f"Total Files Audited: {len(results['passed']) + len(results['failed'])}")
    print(f"  ✅ Passed: {len(results['passed'])}")
    print(f"  ❌ Failed: {len(results['failed'])}")
    print()

    print(f"Total Items: {results['total_items']}")
    print(f"  ✅ Valid items: {results['total_items'] - results['items_needing_regeneration']}")
    print(f"  ❌ Items needing regeneration: {results['items_needing_regeneration']}")
    print()

    print(f"Total Placeholder Patterns Detected: {results['total_placeholder_patterns']:,}")
    print()

    # Breakdown by category
    if results['failed']:
        print("━" * 80)
        print("🚨 FILES REQUIRING REGENERATION")
        print("━" * 80)
        print()

        by_category = {}
        for item in results['failed']:
            cat = item['category']
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(item)

        for category, items in by_category.items():
            print(f"📂 {category}")
            total_items = sum(item['items'] for item in items)
            total_placeholders = sum(item['placeholder_patterns'] for item in items)
            print(f"   Total items: {total_items}")
            print(f"   Total placeholder patterns: {total_placeholders:,}")
            print()

            for item in items:
                print(f"   ❌ {item['file']}")
                print(f"      Items: {item['items']}")
                print(f"      Placeholders: {item['placeholder_patterns']:,}")
            print()

    # Priority recommendations
    print("━" * 80)
    print("🎯 REGENERATION PRIORITY")
    print("━" * 80)
    print()

    if results['items_needing_regeneration'] == 0:
        print("✅ All content validated successfully!")
        print("   No regeneration required.")
    else:
        print(f"⚠️  {results['items_needing_regeneration']} items require LLM-powered regeneration")
        print()
        print("Recommended Actions:")
        print("  1. Create LLM-powered regeneration scripts (with summaries for MCQs)")
        print("  2. Apply Constraint 11: 3 citations per MCQ")
        print("  3. Apply Constraint 12: LLM-powered generation (not templates)")
        print("  4. Include images where appropriate")
        print("  5. Run incremental citation validation")
        print("  6. Run QA-003 validation")
        print("  7. Verify 0% placeholder patterns")

    print()
    print("━" * 80)
    print("🏁 AUDIT COMPLETE")
    print("━" * 80)

    # Save detailed report to JSON
    report_file = PROJECT_ROOT / "CONTENT_AUDIT_REPORT.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump({
            'audit_date': '2026-01-26',
            'total_files': len(results['passed']) + len(results['failed']),
            'passed_files': len(results['passed']),
            'failed_files': len(results['failed']),
            'total_items': results['total_items'],
            'items_needing_regeneration': results['items_needing_regeneration'],
            'total_placeholder_patterns': results['total_placeholder_patterns'],
            'passed_files_detail': results['passed'],
            'failed_files_detail': results['failed']
        }, f, indent=2)

    print(f"\n📄 Detailed report saved to: {report_file}")
    print()

if __name__ == "__main__":
    audit_all_files()
