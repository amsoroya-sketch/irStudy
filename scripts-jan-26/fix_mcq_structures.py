#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Week 3 Respiratory MCQ Structure Fixer
Extracts medical content from incorrectly formatted files and converts to proper structure
"""

import json
import re
from pathlib import Path
from datetime import datetime
import sys

def extract_mcq_from_dict(mcq_data, expected_id):
    """Extract MCQ content from dictionary format and reformat with correct ID"""
    return {
        "question": {
            "scenario": mcq_data.get("question", ""),
            "stem": mcq_data.get("question", ""),
            "options": mcq_data.get("options", {})
        },
        "correct_answer": mcq_data.get("correct_answer", ""),
        "explanation": mcq_data.get("explanation", ""),
        "summary": mcq_data.get("summary", mcq_data.get("australian_context", "")),
        "citations": mcq_data.get("citations", []),
        "metadata": {
            "topic": mcq_data.get("topic", ""),
            "difficulty": mcq_data.get("difficulty", "intermediate"),
            "australian_context": True
        }
    }

def fix_file_structure(filepath, start_id, end_id):
    """Read file, extract MCQs, convert to correct format"""
    print(f"\n{'='*80}")
    print(f"Processing: {filepath.name}")
    print(f"Expected range: WEEK3-RESP-{start_id:03d} to WEEK3-RESP-{end_id:03d}")
    print(f"{'='*80}")

    # Read file content
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Try to extract list variable
    # Pattern: WEEK3_RESP_XXX_YYY_TOPIC = [...]
    list_pattern = r'(WEEK3_RESP_\d+_\d+_[A-Z_]+)\s*=\s*\['
    match = re.search(list_pattern, content)

    if not match:
        print(f"  [ERROR] Could not find list variable pattern")
        return None

    var_name = match.group(1)
    print(f"  Found list variable: {var_name}")

    # Extract MCQ dictionaries from list
    # Find all dictionary blocks starting with "id":
    mcq_blocks = re.findall(r'\{[^}]*"id":\s*"[^"]*"[^}]*(?:\{[^}]*\}[^}]*)*\}', content, re.DOTALL)

    if not mcq_blocks:
        print(f"  [ERROR] Could not extract MCQ blocks")
        return None

    print(f"  Found {len(mcq_blocks)} MCQ blocks")

    # Parse each MCQ
    generated_mcqs = {}
    mcq_num = start_id

    for block in mcq_blocks:
        if mcq_num > end_id:
            break

        try:
            # Try to evaluate as Python dict
            mcq_dict = eval(block)

            # Extract content
            new_id = f"WEEK3-RESP-{mcq_num:03d}"

            # Build properly structured MCQ
            generated_mcqs[new_id] = {
                "question": {
                    "scenario": mcq_dict.get("question", ""),
                    "stem": mcq_dict.get("question", ""),
                    "options": mcq_dict.get("options", {})
                },
                "correct_answer": mcq_dict.get("correct_answer", ""),
                "explanation": mcq_dict.get("explanation", ""),
                "summary": mcq_dict.get("australian_context", ""),
                "citations": [
                    {
                        "source": c.get("source", ""),
                        "evidence": c.get("evidence", ""),
                        "relevance": c.get("relevance", "")
                    } if isinstance(c, dict) else c
                    for c in mcq_dict.get("citations", [])
                ],
                "metadata": {
                    "topic": mcq_dict.get("topic", ""),
                    "difficulty": mcq_dict.get("difficulty", "intermediate"),
                    "australian_context": True
                }
            }

            print(f"  [OK] Converted: {new_id}")
            mcq_num += 1

        except Exception as e:
            print(f"  [WARNING] Failed to parse MCQ block: {str(e)[:100]}")
            continue

    if not generated_mcqs:
        print(f"  [ERROR] No MCQs successfully converted")
        return None

    print(f"  [OK] Successfully converted {len(generated_mcqs)} MCQs")
    return generated_mcqs

def write_fixed_file(filepath, generated_mcqs, topic):
    """Write corrected file with GENERATED_MCQS format"""

    # Create backup
    backup_path = filepath.parent / f"{filepath.stem}.ORIGINAL_BACKUP"
    if not backup_path.exists():
        with open(filepath, 'r') as f:
            backup_content = f.read()
        with open(backup_path, 'w') as f:
            f.write(backup_content)
        print(f"  [OK] Created backup: {backup_path.name}")

    # Generate new file content
    ids = sorted(generated_mcqs.keys())
    start_id = ids[0].split('-')[-1]
    end_id = ids[-1].split('-')[-1]

    file_content = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Week 3 Respiratory Medicine MCQs - {topic}
MCQs {start_id}-{end_id}

Australian Medical Standards - eTG Complete 2024-2025
Generated: {datetime.now().strftime('%Y-%m-%d')}
Structure: GENERATED_MCQS dictionary format
"""

GENERATED_MCQS = {{
'''

    for mcq_id in ids:
        mcq = generated_mcqs[mcq_id]
        file_content += f'''    "{mcq_id}": {{
        "question": {{
            "scenario": """{mcq['question']['scenario']}""",
            "stem": """{mcq['question']['stem']}""",
            "options": {json.dumps(mcq['question']['options'], indent=16, ensure_ascii=False)}
        }},
        "correct_answer": "{mcq['correct_answer']}",
        "explanation": """{mcq['explanation']}""",
        "summary": """{mcq['summary']}""",
        "citations": {json.dumps(mcq['citations'], indent=8, ensure_ascii=False)},
        "metadata": {json.dumps(mcq['metadata'], indent=12, ensure_ascii=False)}
    }},
'''

    file_content += "}\n"

    # Write file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(file_content)

    print(f"  [OK] Wrote corrected file: {filepath.name}")

def main():
    base_dir = Path("/home/dev/Development/irStudy")
    data_dir = base_dir / "data" / "mcqs"

    print("="*80)
    print("WEEK 3 RESPIRATORY MCQ STRUCTURE FIXER")
    print("="*80)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Define files to fix
    files_to_fix = [
        ("WEEK3_RESP_101_113_VTE_MANAGEMENT.py", 101, 113, "VTE/DVT/PE Management"),
        ("WEEK3_RESP_126_138_ILD_ADVANCED.py", 126, 138, "Advanced ILD"),
        ("WEEK3_RESP_139_150_PNEUMOCONIOSIS_ARDS.py", 139, 150, "Pneumoconiosis & ARDS"),
        ("WEEK3_RESP_151_163_VENTILATION.py", 151, 163, "Mechanical Ventilation"),
        ("WEEK3_RESP_164_175_PLEURAL_DISEASE.py", 164, 175, "Pleural Disease"),
        ("WEEK3_RESP_176_188_LUNG_CANCER.py", 176, 188, "Lung Cancer"),
    ]

    success_count = 0
    total_mcqs = 0

    for filename, start_id, end_id, topic in files_to_fix:
        filepath = data_dir / filename

        if not filepath.exists():
            print(f"[WARNING] File not found: {filename}")
            continue

        # Extract and convert MCQs
        generated_mcqs = fix_file_structure(filepath, start_id, end_id)

        if generated_mcqs:
            # Write corrected file
            write_fixed_file(filepath, generated_mcqs, topic)

            # Validate
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location("module", filepath)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                if hasattr(module, 'GENERATED_MCQS'):
                    mcq_count = len(module.GENERATED_MCQS)
                    print(f"  [OK] Validation passed: {mcq_count} MCQs")
                    print(f"  [OK] ID range: {min(module.GENERATED_MCQS.keys())} to {max(module.GENERATED_MCQS.keys())}")
                    success_count += 1
                    total_mcqs += mcq_count
                else:
                    print(f"  [ERROR] GENERATED_MCQS not found after conversion")
            except Exception as e:
                print(f"  [ERROR] Validation failed: {str(e)[:100]}")

    print()
    print("="*80)
    print("CONVERSION SUMMARY")
    print("="*80)
    print(f"Files successfully converted: {success_count}/6")
    print(f"Total MCQs converted: {total_mcqs}")

    if success_count == 6:
        print()
        print("="*80)
        print("SUCCESS! All 6 files converted successfully")
        print("="*80)
        print("Next step: Run consolidation script")
        print("  python3 scripts-jan-26/respiratory_consolidation/consolidate_all_respiratory_mcqs.py")
        return 0
    else:
        print()
        print(f"[WARNING] {6 - success_count} files failed conversion")
        return 1

if __name__ == "__main__":
    sys.exit(main())
