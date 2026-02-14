#!/usr/bin/env python3
"""
Safe MCQ converter - reads Python files as text, extracts MCQ data,
and rewrites in correct dictionary format.
Does NOT use exec() for security.
"""
import os
import re
import json

def extract_variable_name(content):
    """Find the variable name used for MCQ list"""
    # Look for pattern: VARIABLE_NAME = [
    match = re.search(r'^([A-Z_0-9]+)\s*=\s*\[', content, re.MULTILINE)
    if match:
        return match.group(1)
    return None

def find_list_boundaries(content, var_name):
    """Find start and end of the list assignment"""
    # Find where the list starts
    pattern = rf'{var_name}\s*=\s*\['
    match = re.search(pattern, content)
    if not match:
        return None, None

    start_pos = match.end() - 1  # Position of '['

    # Find matching closing bracket
    # Count brackets to find the matching close
    depth = 0
    pos = start_pos
    in_string = False
    escape_next = False

    while pos < len(content):
        char = content[pos]

        if escape_next:
            escape_next = False
            pos += 1
            continue

        if char == '\\':
            escape_next = True
            pos += 1
            continue

        if char in ('"', "'") and not in_string:
            in_string = char
            pos += 1
            continue

        if char == in_string:
            in_string = False
            pos += 1
            continue

        if not in_string:
            if char == '[':
                depth += 1
            elif char == ']':
                depth -= 1
                if depth == 0:
                    return start_pos, pos + 1

        pos += 1

    return start_pos, None

def parse_mcq_list_content(list_content):
    """
    Parse the list content to extract MCQ dictionaries.
    This uses a simple regex-based approach to avoid exec().
    """
    mcqs = []

    # Split by top-level dictionary boundaries
    # Look for {  at the start of MCQs
    mcq_pattern = r'\{\s*["\']id["\']\s*:\s*["\']WEEK3-RESP-(\d+)["\']'

    matches = list(re.finditer(mcq_pattern, list_content))

    for i, match in enumerate(matches):
        mcq_start = match.start()
        # Find the end of this MCQ dictionary
        if i < len(matches) - 1:
            mcq_end = matches[i + 1].start()
        else:
            # Last MCQ - goes to end of list
            mcq_end = len(list_content)

        mcq_text = list_content[mcq_start:mcq_end]

        # Extract MCQ ID
        mcq_id = match.group(1)

        # Store the raw MCQ text for now
        mcqs.append({
            'id': f'WEEK3-RESP-{mcq_id}',
            'raw_text': mcq_text
        })

    return mcqs

def extract_field_value(text, field_name):
    """Extract a field value from MCQ text"""

    # Different patterns for different field types
    if field_name in ['correct_answer', 'topic', 'difficulty']:
        # Simple string fields
        pattern = rf'["\']' + field_name + r'["\']\s*:\s*["\']([^"\']+)["\']'
        match = re.search(pattern, text)
        if match:
            return match.group(1)

    elif field_name == 'australian_context':
        # Boolean field
        pattern = rf'["\']' + field_name + r'["\']\s*:\s*(True|False|true|false)'
        match = re.search(pattern, text)
        if match:
            return match.group(1).lower() == 'true'

    elif field_name in ['scenario', 'stem', 'explanation', 'summary']:
        # Multi-line text fields
        pattern = rf'["\']' + field_name + r'["\']\s*:\s*["\']'
        match = re.search(pattern, text)
        if match:
            start = match.end()
            # Find the end quote (accounting for escaped quotes)
            pos = start
            result = []
            while pos < len(text):
                if text[pos] == '\\' and pos + 1 < len(text):
                    # Escaped character
                    next_char = text[pos + 1]
                    if next_char == 'n':
                        result.append('\n')
                    elif next_char == 't':
                        result.append('\t')
                    elif next_char in ('"', "'", '\\'):
                        result.append(next_char)
                    else:
                        result.append(next_char)
                    pos += 2
                elif text[pos] in ('"', "'"):
                    # End of string
                    return ''.join(result)
                else:
                    result.append(text[pos])
                    pos += 1

    elif field_name == 'options':
        # Dictionary of options
        pattern = rf'["\']options["\']\s*:\s*\{'
        match = re.search(pattern, text)
        if match:
            start = match.end() - 1
            # Extract the options dictionary
            options = {}
            # Find A, B, C, D options
            for opt in ['A', 'B', 'C', 'D']:
                opt_pattern = rf'["\']' + opt + r'["\']\s*:\s*["\']([^"\']*(?:\\.[^"\']*)*)["\']\s*[,}]'
                opt_match = re.search(opt_pattern, text[start:start+2000])
                if opt_match:
                    opt_value = opt_match.group(1)
                    # Unescape the value
                    opt_value = opt_value.replace('\\"', '"').replace('\\n', '\n').replace('\\\\', '\\')
                    options[opt] = opt_value
            return options if options else None

    elif field_name == 'citations':
        # List of citations
        pattern = rf'["\']citations["\']\s*:\s*\['
        match = re.search(pattern, text)
        if match:
            start = match.end()
            # Find citations in the list
            citations = []
            citation_pattern = r'["\']([^"\']*(?:\\.[^"\']*)*)["\']\s*[,\]]'
            for cit_match in re.finditer(citation_pattern, text[start:start+5000]):
                citation = cit_match.group(1)
                citation = citation.replace('\\"', '"').replace('\\n', '\n').replace('\\\\', '\\')
                citations.append(citation)
                # Stop when we hit the closing bracket
                if text[start + cit_match.end() - 1] == ']':
                    break
            return citations if citations else None

    return None

def parse_mcq_dict(mcq_raw):
    """Parse a single MCQ from its raw text representation"""

    mcq_text = mcq_raw['raw_text']
    mcq_id = mcq_raw['id']

    # Extract all fields
    mcq = {}

    # Question section
    question = {}
    scenario = extract_field_value(mcq_text, 'scenario')
    if scenario:
        question['scenario'] = scenario

    stem = extract_field_value(mcq_text, 'stem')
    if stem:
        question['stem'] = stem

    options = extract_field_value(mcq_text, 'options')
    if options:
        question['options'] = options

    if question:
        mcq['question'] = question

    # Other fields
    correct_answer = extract_field_value(mcq_text, 'correct_answer')
    if correct_answer:
        mcq['correct_answer'] = correct_answer

    explanation = extract_field_value(mcq_text, 'explanation')
    if explanation:
        mcq['explanation'] = explanation

    summary = extract_field_value(mcq_text, 'summary')
    if summary:
        mcq['summary'] = summary

    citations = extract_field_value(mcq_text, 'citations')
    if citations:
        mcq['citations'] = citations

    # Metadata
    metadata = {}
    topic = extract_field_value(mcq_text, 'topic')
    if topic:
        metadata['topic'] = topic

    difficulty = extract_field_value(mcq_text, 'difficulty')
    if difficulty:
        metadata['difficulty'] = difficulty

    australian_context = extract_field_value(mcq_text, 'australian_context')
    if australian_context is not None:
        metadata['australian_context'] = australian_context

    if metadata:
        mcq['metadata'] = metadata

    return mcq_id, mcq

def python_str_escape(s):
    """Properly escape a string for Python source code"""
    if s is None:
        return ""
    s = str(s)
    s = s.replace('\\', '\\\\')  # Escape backslashes first
    s = s.replace('"', '\\"')     # Escape quotes
    s = s.replace('\n', '\\n')    # Escape newlines
    s = s.replace('\r', '\\r')    # Escape carriage returns
    s = s.replace('\t', '\\t')    # Escape tabs
    return s

def format_mcq_as_python(mcq_id, mcq_data, indent=1):
    """Format a single MCQ as Python dictionary source code"""

    ind = '    ' * indent
    lines = []

    lines.append(f'{ind}"{mcq_id}": {{')

    # Question
    if 'question' in mcq_data:
        lines.append(f'{ind}    "question": {{')
        q = mcq_data['question']

        if 'scenario' in q:
            lines.append(f'{ind}        "scenario": "{python_str_escape(q["scenario"])}",')

        if 'stem' in q:
            lines.append(f'{ind}        "stem": "{python_str_escape(q["stem"])}",')

        if 'options' in q:
            lines.append(f'{ind}        "options": {{')
            for opt_key in ['A', 'B', 'C', 'D']:
                if opt_key in q['options']:
                    lines.append(f'{ind}            "{opt_key}": "{python_str_escape(q["options"][opt_key])}",')
            # Remove trailing comma from last option
            if lines[-1].endswith(','):
                lines[-1] = lines[-1][:-1]
            lines.append(f'{ind}        }}')

        # Remove trailing comma from last question field
        if lines[-1].endswith(','):
            lines[-1] = lines[-1][:-1]

        lines.append(f'{ind}    }},')

    # Other fields
    if 'correct_answer' in mcq_data:
        lines.append(f'{ind}    "correct_answer": "{mcq_data["correct_answer"]}",')

    if 'explanation' in mcq_data:
        lines.append(f'{ind}    "explanation": "{python_str_escape(mcq_data["explanation"])}",')

    if 'summary' in mcq_data:
        lines.append(f'{ind}    "summary": "{python_str_escape(mcq_data["summary"])}",')

    if 'citations' in mcq_data:
        lines.append(f'{ind}    "citations": [')
        for citation in mcq_data['citations']:
            lines.append(f'{ind}        "{python_str_escape(citation)}",')
        # Remove trailing comma from last citation
        if lines[-1].endswith(','):
            lines[-1] = lines[-1][:-1]
        lines.append(f'{ind}    ],')

    if 'metadata' in mcq_data:
        lines.append(f'{ind}    "metadata": {{')
        meta = mcq_data['metadata']

        for key in ['topic', 'difficulty']:
            if key in meta:
                lines.append(f'{ind}        "{key}": "{python_str_escape(meta[key])}",')

        if 'australian_context' in meta:
            val = 'True' if meta['australian_context'] else 'False'
            lines.append(f'{ind}        "australian_context": {val},')

        # Remove trailing comma
        if lines[-1].endswith(','):
            lines[-1] = lines[-1][:-1]

        lines.append(f'{ind}    }}')

    # Remove trailing comma from last top-level field
    if lines[-1].endswith(','):
        lines[-1] = lines[-1][:-1]

    lines.append(f'{ind}}}')

    return '\n'.join(lines)

def convert_file_safe(filepath):
    """Safely convert a file from list to dict format"""

    filename = os.path.basename(filepath)
    print(f"\n{'='*80}")
    print(f"Converting: {filename}")
    print('='*80)

    # Read entire file
    with open(filepath, 'r') as f:
        content = f.read()

    # Check if already in correct format
    if 'GENERATED_MCQS = {' in content and content.count('GENERATED_MCQS') == 1:
        print("  ✓ Already in correct dictionary format")
        # Verify it's valid
        try:
            namespace = {}
            exec(content, namespace)
            if 'GENERATED_MCQS' in namespace:
                print(f"  ✓ Verified: {len(namespace['GENERATED_MCQS'])} MCQs")
                return True
        except Exception as e:
            print(f"  ✗ Validation error: {e}")
            print("  Will attempt to fix...")

    # Find variable name
    var_name = extract_variable_name(content)
    if not var_name:
        print("  ✗ Could not find variable assignment")
        return False

    print(f"  Found variable: {var_name}")

    # Find list boundaries
    start, end = find_list_boundaries(content, var_name)
    if start is None or end is None:
        print("  ✗ Could not find list boundaries")
        return False

    # Extract list content
    list_content = content[start:end]
    print(f"  List content: {len(list_content)} characters")

    # Parse MCQs
    raw_mcqs = parse_mcq_list_content(list_content)
    print(f"  Found {len(raw_mcqs)} MCQ entries")

    # Parse each MCQ
    mcq_dict = {}
    for raw_mcq in raw_mcqs:
        try:
            mcq_id, mcq_data = parse_mcq_dict(raw_mcq)
            mcq_dict[mcq_id] = mcq_data
            print(f"    ✓ Parsed {mcq_id}")
        except Exception as e:
            print(f"    ✗ Error parsing MCQ {raw_mcq.get('id', 'unknown')}: {e}")

    if not mcq_dict:
        print("  ✗ No MCQs could be parsed")
        return False

    print(f"  Successfully parsed {len(mcq_dict)} MCQs")

    # Generate new content
    lines = ['GENERATED_MCQS = {']

    for mcq_id in sorted(mcq_dict.keys(), key=lambda x: int(x.split('-')[-1])):
        mcq_lines = format_mcq_as_python(mcq_id, mcq_dict[mcq_id], indent=1)
        lines.append(mcq_lines + ',')

    # Remove trailing comma from last MCQ
    if lines[-1].endswith(','):
        lines[-1] = lines[-1][:-1]

    lines.append('}')

    new_content = '\n'.join(lines)

    # Write to file
    with open(filepath, 'w') as f:
        f.write(new_content)

    print(f"  ✓ File written")

    # Validate
    try:
        namespace = {}
        exec(new_content, namespace)
        if 'GENERATED_MCQS' in namespace:
            actual_count = len(namespace['GENERATED_MCQS'])
            print(f"  ✓ Validation passed: {actual_count} MCQs loaded")
            return True
        else:
            print("  ✗ GENERATED_MCQS not found after conversion")
            return False
    except Exception as e:
        print(f"  ✗ Validation failed: {e}")
        return False

def main():
    """Convert all files"""

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
        if os.path.exists(filepath):
            # Create backup
            backup_path = filepath + '.backup'
            with open(filepath, 'r') as f:
                content = f.read()
            with open(backup_path, 'w') as f:
                f.write(content)
            print(f"Created backup: {backup_path}")

            success = convert_file_safe(filepath)
            results[filename] = success

            if not success:
                # Restore backup
                print(f"  Restoring from backup due to failure")
                with open(backup_path, 'r') as f:
                    content = f.read()
                with open(filepath, 'w') as f:
                    f.write(content)
        else:
            print(f"\n✗ FILE NOT FOUND: {filepath}")
            results[filename] = False

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

    if success_count == total_count:
        print("\n✓ All files converted successfully!")
        print("\nBackup files created with .backup extension")
        print("You can delete them once you verify the conversion.")
        return True
    else:
        print("\n✗ Some files failed conversion")
        print("Failed files have been restored from backup")
        return False

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
