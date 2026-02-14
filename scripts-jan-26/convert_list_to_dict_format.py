#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Week 3 Respiratory MCQ Format Converter
Converts list-format MCQ files to GENERATED_MCQS dictionary format
"""

import json
from pathlib import Path
from datetime import datetime
import sys

def convert_file(filepath, start_id, end_id, topic):
    """Convert a list-format MCQ file to dictionary format"""
    print(f"\n{'='*80}")
    print(f"Processing: {filepath.name}")
    print(f"Expected: WEEK3-RESP-{start_id:03d} to WEEK3-RESP-{end_id:03d}")
    print(f"{'='*80}")

    # Create backup
    backup_path = filepath.parent / f"{filepath.stem}.ORIGINAL_BACKUP"
    if not backup_path.exists():
        with open(filepath, 'r') as f:
            backup_content = f.read()
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(backup_content)
        print(f"  [OK] Created backup: {backup_path.name}")

    # Execute the file to load the list variable
    with open(filepath, 'r') as f:
        file_content = f.read()

    # Execute to get the variable
    exec_globals = {}
    try:
        exec(file_content, exec_globals)
    except Exception as e:
        print(f"  [ERROR] Failed to execute file: {e}")
        return None

    # Find the list variable (it's the only list in the namespace)
    mcq_list = None
    for var_name, var_value in exec_globals.items():
        if isinstance(var_value, list) and len(var_value) > 0:
            if isinstance(var_value[0], dict) and 'id' in var_value[0]:
                mcq_list = var_value
                print(f"  Found MCQ list with {len(mcq_list)} items")
                break

    if not mcq_list:
        print(f"  [ERROR] Could not find MCQ list in file")
        return None

    # Convert to dictionary format
    GENERATED_MCQS = {}
    for i, mcq in enumerate(mcq_list, start=start_id):
        if i > end_id:
            break

        new_id = f"WEEK3-RESP-{i:03d}"
        GENERATED_MCQS[new_id] = {
            "question": {
                "scenario": mcq.get("question", ""),
                "stem": mcq.get("question", ""),
                "options": mcq.get("options", {})
            },
            "correct_answer": mcq.get("correct_answer", ""),
            "explanation": mcq.get("explanation", ""),
            "summary": mcq.get("australian_context", ""),
            "citations": mcq.get("citations", []),
            "metadata": {
                "topic": mcq.get("topic", ""),
                "difficulty": mcq.get("difficulty", "intermediate"),
                "australian_context": True
            }
        }

    print(f"  [OK] Converted {len(GENERATED_MCQS)} MCQs")
    print(f"  ID range: {min(GENERATED_MCQS.keys())} to {max(GENERATED_MCQS.keys())}")

    # Write new file
    write_converted_file(filepath, GENERATED_MCQS, topic, start_id, end_id)

    # Validate
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("module", filepath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        if hasattr(module, 'GENERATED_MCQS'):
            mcq_count = len(module.GENERATED_MCQS)
            print(f"  [OK] Validation passed: {mcq_count} MCQs")
            return mcq_count
        else:
            print(f"  [ERROR] GENERATED_MCQS not found after conversion")
            return None
    except Exception as e:
        print(f"  [ERROR] Validation failed: {str(e)[:100]}")
        return None

def write_converted_file(filepath, generated_mcqs, topic, start_id, end_id):
    """Write the converted dictionary format file"""
    file_content = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Week 3 Respiratory Medicine MCQs - {topic}
MCQs {start_id:03d}-{end_id:03d}

Australian Medical Standards - eTG Complete 2024-2025
Generated: {datetime.now().strftime('%Y-%m-%d')}
Format: GENERATED_MCQS dictionary
"""

GENERATED_MCQS = {{
'''

    for mcq_id in sorted(generated_mcqs.keys()):
        mcq = generated_mcqs[mcq_id]

        # Format citations
        citations_json = json.dumps(mcq['citations'], indent=8, ensure_ascii=False)
        citations_json = citations_json.replace('\n', '\n        ')

        # Format options
        options_json = json.dumps(mcq['question']['options'], indent=12, ensure_ascii=False)
        options_json = options_json.replace('\n', '\n            ')

        # Format metadata
        metadata_json = json.dumps(mcq['metadata'], indent=12, ensure_ascii=False)
        metadata_json = metadata_json.replace('\n', '\n        ')

        file_content += f'''    "{mcq_id}": {{
        "question": {{
            "scenario": """{mcq['question']['scenario']}""",
            "stem": """{mcq['question']['stem']}""",
            "options": {options_json}
        }},
        "correct_answer": "{mcq['correct_answer']}",
        "explanation": """{mcq['explanation']}""",
        "summary": """{mcq['summary']}""",
        "citations": {citations_json},
        "metadata": {metadata_json}
    }},
'''

    file_content += "}\n"

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(file_content)

    print(f"  [OK] Wrote converted file")

def main():
    base_dir = Path("/home/dev/Development/irStudy")
    data_dir = base_dir / "data" / "mcqs"

    print("="*80)
    print("WEEK 3 RESPIRATORY MCQ FORMAT CONVERTER")
    print("="*80)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Define files to convert
    files_to_convert = [
        ("WEEK3_RESP_126_138_ILD_ADVANCED.py", 126, 138, "Advanced ILD"),
        ("WEEK3_RESP_139_150_PNEUMOCONIOSIS_ARDS.py", 139, 150, "Pneumoconiosis & ARDS"),
        ("WEEK3_RESP_164_175_PLEURAL_DISEASE.py", 164, 175, "Pleural Disease"),
    ]

    success_count = 0
    total_mcqs = 0

    for filename, start_id, end_id, topic in files_to_convert:
        filepath = data_dir / filename

        if not filepath.exists():
            print(f"[WARNING] File not found: {filename}")
            continue

        mcq_count = convert_file(filepath, start_id, end_id, topic)

        if mcq_count:
            success_count += 1
            total_mcqs += mcq_count

    print()
    print("="*80)
    print("CONVERSION SUMMARY")
    print("="*80)
    print(f"Files successfully converted: {success_count}/{len(files_to_convert)}")
    print(f"Total MCQs converted: {total_mcqs}")

    if success_count == len(files_to_convert):
        print()
        print("="*80)
        print("SUCCESS! All files converted successfully")
        print("="*80)
        return 0
    else:
        print()
        print(f"[WARNING] {len(files_to_convert) - success_count} files failed conversion")
        return 1

if __name__ == "__main__":
    sys.exit(main())
