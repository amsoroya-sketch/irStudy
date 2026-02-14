#!/usr/bin/env python3
"""
Convert MCQ batch files from list format to dictionary format
Preserves all medical content, citations, and metadata
"""
import os
import re
import json
import ast

def extract_mcqs_from_list_format(content):
    """Extract MCQs from list format and convert to dictionary"""

    # Find the list assignment
    # Match patterns like: VARIABLE_NAME = [ ... ]
    list_match = re.search(r'([A-Z_0-9]+)\s*=\s*\[', content)
    if not list_match:
        print("  No list format found, checking for existing dict format")
        if 'GENERATED_MCQS = {' in content:
            print("  Already in correct dictionary format")
            return None
        raise ValueError("Could not find list assignment")

    var_name = list_match.group(1)
    print(f"  Found variable: {var_name}")

    # Execute the file to get the data structure
    namespace = {}
    try:
        exec(content, namespace)
    except SyntaxError as e:
        print(f"  SYNTAX ERROR at line {e.lineno}: {e.msg}")
        # Try to fix common syntax errors
        content_fixed = fix_syntax_errors(content, e)
        exec(content_fixed, namespace)

    mcq_list = namespace.get(var_name)
    if not mcq_list:
        raise ValueError(f"Could not extract {var_name} from file")

    print(f"  Extracted {len(mcq_list)} MCQs from list")

    # Convert list to dictionary with ID as key
    mcq_dict = {}
    for mcq in mcq_list:
        if 'id' in mcq:
            mcq_id = mcq['id']
            # Remove 'id' from the MCQ object as it's now the key
            mcq_copy = mcq.copy()
            del mcq_copy['id']
            mcq_dict[mcq_id] = mcq_copy
        else:
            print(f"  WARNING: MCQ missing 'id' field: {str(mcq)[:100]}")

    return mcq_dict

def fix_syntax_errors(content, error):
    """Attempt to fix common syntax errors"""
    lines = content.split('\n')

    if error.lineno:
        error_line = error.lineno - 1
        print(f"  Attempting to fix syntax error at line {error.lineno}")

        # Common issue: mismatched brackets
        if 'bracket' in error.msg.lower() or 'parenthesis' in error.msg.lower():
            # Check for common patterns around the error
            context_start = max(0, error_line - 5)
            context_end = min(len(lines), error_line + 5)

            # Look for bracket mismatches in context
            for i in range(context_start, context_end):
                line = lines[i]
                # Fix double closing brackets
                if '}}' in line and '{' not in line:
                    lines[i] = line.replace('}}', '}')
                    print(f"  Fixed double closing bracket at line {i+1}")

    return '\n'.join(lines)

def format_mcq_dict_as_python(mcq_dict):
    """Format MCQ dictionary as valid Python code"""

    lines = ["GENERATED_MCQS = {"]

    for mcq_id, mcq_data in mcq_dict.items():
        lines.append(f'    "{mcq_id}": {{')

        # Question section
        if 'question' in mcq_data:
            lines.append('        "question": {')
            q = mcq_data['question']

            if 'scenario' in q:
                scenario = q['scenario'].replace('"', '\\"').replace('\n', '\\n')
                lines.append(f'            "scenario": "{scenario}",')

            if 'stem' in q:
                stem = q['stem'].replace('"', '\\"').replace('\n', '\\n')
                lines.append(f'            "stem": "{stem}",')

            if 'options' in q:
                lines.append('            "options": {')
                for opt_key, opt_val in q['options'].items():
                    opt_val_clean = opt_val.replace('"', '\\"').replace('\n', '\\n')
                    lines.append(f'                "{opt_key}": "{opt_val_clean}",')
                # Remove trailing comma from last option
                if lines[-1].endswith(','):
                    lines[-1] = lines[-1][:-1]
                lines.append('            }')

            lines.append('        },')

        # Correct answer
        if 'correct_answer' in mcq_data:
            lines.append(f'        "correct_answer": "{mcq_data["correct_answer"]}",')

        # Explanation
        if 'explanation' in mcq_data:
            explanation = mcq_data['explanation'].replace('"', '\\"').replace('\n', '\\n')
            lines.append(f'        "explanation": "{explanation}",')

        # Summary
        if 'summary' in mcq_data:
            summary = mcq_data['summary'].replace('"', '\\"').replace('\n', '\\n')
            lines.append(f'        "summary": "{summary}",')

        # Citations
        if 'citations' in mcq_data:
            lines.append('        "citations": [')
            for citation in mcq_data['citations']:
                citation_clean = citation.replace('"', '\\"').replace('\n', '\\n')
                lines.append(f'            "{citation_clean}",')
            # Remove trailing comma
            if lines[-1].endswith(','):
                lines[-1] = lines[-1][:-1]
            lines.append('        ],')

        # Metadata
        if 'metadata' in mcq_data:
            lines.append('        "metadata": {')
            meta = mcq_data['metadata']

            for key, value in meta.items():
                if isinstance(value, bool):
                    lines.append(f'            "{key}": {str(value)},')
                elif isinstance(value, str):
                    value_clean = value.replace('"', '\\"').replace('\n', '\\n')
                    lines.append(f'            "{key}": "{value_clean}",')
                else:
                    lines.append(f'            "{key}": {json.dumps(value)},')

            # Remove trailing comma
            if lines[-1].endswith(','):
                lines[-1] = lines[-1][:-1]
            lines.append('        }')

        # Remove trailing comma from last field
        if lines[-1].endswith(','):
            lines[-1] = lines[-1][:-1]

        lines.append('    },')

    # Remove trailing comma from last MCQ
    if lines[-1].endswith(','):
        lines[-1] = lines[-1][:-1]

    lines.append('}')

    return '\n'.join(lines)

def convert_file(filepath):
    """Convert a single MCQ file from list to dictionary format"""

    filename = os.path.basename(filepath)
    print(f"\n{'='*80}")
    print(f"Converting: {filename}")
    print('='*80)

    with open(filepath, 'r') as f:
        content = f.read()

    # Extract MCQs
    try:
        mcq_dict = extract_mcqs_from_list_format(content)

        if mcq_dict is None:
            print("  Skipping - already in correct format")
            return True

        # Format as Python code
        new_content = format_mcq_dict_as_python(mcq_dict)

        # Write back to file
        with open(filepath, 'w') as f:
            f.write(new_content)

        print(f"  ✓ Successfully converted {len(mcq_dict)} MCQs")

        # Validate
        namespace = {}
        exec(new_content, namespace)
        if 'GENERATED_MCQS' in namespace:
            actual_count = len(namespace['GENERATED_MCQS'])
            print(f"  ✓ Validation passed: {actual_count} MCQs loaded")
            return True
        else:
            print("  ✗ Validation failed: GENERATED_MCQS not found")
            return False

    except Exception as e:
        print(f"  ✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Convert all MCQ batch files"""

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
        success = convert_file(filepath)
        results[filename] = success

    # Summary
    print(f"\n{'='*80}")
    print("CONVERSION SUMMARY")
    print('='*80)

    success_count = sum(1 for v in results.values() if v)
    total_count = len(results)

    for filename, success in results.items():
        status = "✓ SUCCESS" if success else "✗ FAILED"
        print(f"{status}: {filename}")

    print(f"\nTotal: {success_count}/{total_count} files converted successfully")

    return success_count == total_count

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
