#!/usr/bin/env python3
"""
Convert Markdown PRDs to JSON format for Ralph loop execution

Usage:
    python scripts/convert_prds_to_json.py --all
    python scripts/convert_prds_to_json.py --prd PRD-PHASE1-001
"""

import json
import re
from pathlib import Path
from typing import Dict, List

def extract_sections(md_content: str) -> Dict[str, str]:
    """Extract R-A-L-P-H sections from markdown PRD"""
    sections = {}

    # Extract title and metadata
    title_match = re.search(r'^# PRD: (.+)$', md_content, re.MULTILINE)
    sections['title'] = title_match.group(1) if title_match else "Unknown"

    # Extract PRD ID
    id_match = re.search(r'\*\*PRD ID\*\*: (.+)$', md_content, re.MULTILINE)
    sections['id'] = id_match.group(1) if id_match else "UNKNOWN"

    # Extract agent assignment
    agent_match = re.search(r'\*\*Agent Assignment\*\*: (.+)$', md_content, re.MULTILINE)
    sections['agent'] = agent_match.group(1) if agent_match else "general-purpose"

    # Extract estimated effort
    effort_match = re.search(r'\*\*Estimated Effort\*\*: (.+)$', md_content, re.MULTILINE)
    sections['estimated_effort'] = effort_match.group(1) if effort_match else "Unknown"

    # Extract full content as prompt
    sections['prompt'] = md_content

    # Extract acceptance criteria (look for checklist items)
    acceptance_criteria = []
    in_handoff = False
    for line in md_content.split('\n'):
        if '## H - HANDOFF' in line:
            in_handoff = True
        if in_handoff and line.strip().startswith('- [ ]'):
            criterion = line.strip().replace('- [ ]', '').strip()
            if criterion:
                acceptance_criteria.append(criterion)

    sections['acceptance_criteria'] = acceptance_criteria if acceptance_criteria else [
        "Implementation is complete",
        "All tests pass",
        "Code follows project conventions",
        "Documentation is updated"
    ]

    return sections

def md_to_json(md_file: Path, output_dir: Path) -> Path:
    """Convert single Markdown PRD to JSON format"""

    # Read markdown content
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Extract sections
    sections = extract_sections(md_content)

    # Create JSON structure following ralph-claude-code format
    prd_json = {
        "$schema": ".ralph/schemas/prd-schema.json",
        "id": sections['id'],
        "title": sections['title'],
        "description": f"{sections['title']}. {sections['estimated_effort']}",
        "agent": sections['agent'],
        "prompt": sections['prompt'],
        "acceptance_criteria": sections['acceptance_criteria'],
        "validations": [
            {
                "type": "compilation",
                "description": "Code must compile without errors",
                "blocking": True
            },
            {
                "type": "test_suite",
                "description": "All tests must pass",
                "blocking": True
            }
        ]
    }

    # Create output file
    output_file = output_dir / f"{sections['id']}.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(prd_json, f, indent=2)

    return output_file

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Convert MD PRDs to JSON for Ralph")
    parser.add_argument("--all", action="store_true", help="Convert all PRDs")
    parser.add_argument("--prd", type=str, help="Convert specific PRD by ID")

    args = parser.parse_args()

    project_root = Path("/home/dev/Development/irStudy")
    prds_dir = project_root / "production-launch-prds"
    output_dir = project_root / "prds"

    # Find MD files to convert
    md_files = []

    if args.all:
        md_files = list(prds_dir.glob("phase*/PRD-*.md"))
    elif args.prd:
        md_files = list(prds_dir.glob(f"phase*/{args.prd}.md"))
    else:
        print("Error: Specify --all or --prd <ID>")
        return

    if not md_files:
        print("No PRD files found")
        return

    print(f"Converting {len(md_files)} PRD(s) to JSON...")

    for md_file in md_files:
        try:
            json_file = md_to_json(md_file, output_dir)
            print(f"✓ {md_file.name} → {json_file.name}")
        except Exception as e:
            print(f"✗ {md_file.name}: {e}")

    print(f"\n✅ Conversion complete. JSON PRDs in: {output_dir}")
    print(f"\nNext: cd /home/dev/Development/irStudy && /home/dev/Development/ralph-claude-code/ralph_loop.sh")

if __name__ == "__main__":
    main()
