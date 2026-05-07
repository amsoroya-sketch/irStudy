#!/usr/bin/env python3
"""
Ralph Learning Template Auto-Filler
Version: 1.0

Analyzes failed task attempts and automatically fills PROJECT_CONSTRAINTS.md
templates with discovered patterns using Claude Sonnet 4.

Usage:
    python ralph-learning-filler.py --task-id CRIT-001 --log-file logs/ralph_CRIT-001_*.log
    python ralph-learning-filler.py --backfill  # Fill all empty templates
"""

import anthropic
import argparse
import re
import os
from pathlib import Path
from datetime import datetime


class RalphLearningFiller:
    def __init__(self, api_key=None):
        self.client = anthropic.Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))
        self.project_root = Path(__file__).parent
        self.constraints_file = self.project_root / "PROJECT_CONSTRAINTS.md"

    def extract_error_patterns(self, log_files):
        """Extract error patterns from Ralph execution logs"""
        patterns = []

        for log_file in log_files:
            if not os.path.exists(log_file):
                continue

            with open(log_file, 'r') as f:
                content = f.read()

                # Extract error messages
                errors = re.findall(r'(ERROR|FAILED|VIOLATION):.*', content)
                patterns.extend(errors)

                # Extract stack traces
                stack_traces = re.findall(r'Traceback.*?(?=\n\n)', content, re.DOTALL)
                patterns.extend(stack_traces)

        return patterns

    def count_attempts(self, task_id):
        """Count number of attempts for a task"""
        log_dir = self.project_root / "logs"
        if not log_dir.exists():
            return 0

        log_files = list(log_dir.glob(f"ralph_{task_id}_*.log"))
        return len(log_files)

    def fill_learning_template(self, task_id, error_logs, attempts):
        """Use Claude to fill PROJECT_CONSTRAINTS.md template with learned pattern"""

        error_summary = "\n".join(error_logs[:20])  # First 20 errors

        prompt = f"""Analyze these {attempts} failed attempts for task {task_id}:

ERROR PATTERNS:
{error_summary}

Based on these errors, fill the following template with a discovered pattern:

## Section: {task_id} (ADDED {datetime.now().strftime('%Y-%m-%d')})

**Pattern discovered from:** {task_id}
**Problem:** [1-2 sentence summary of what went wrong]
**Frequency:** {attempts} occurrences
**Root Cause:** [Technical explanation]

### Correct Pattern (✅)

**When to use:**
[Describe scenario where this pattern applies]

**How to implement:**
```[language]
[Working code example that follows best practices]
```

**Key points:**
- [Critical point 1]
- [Critical point 2]
- [Critical point 3]

### Anti-Patterns (❌)

```[language]
// ❌ WRONG: [What developers did that caused failure]
[Bad code that caused the error]
// Problem: [Why this fails]
```

### Validation Checklist

Before merging code that uses this pattern:

- [ ] [Validation check 1]
- [ ] [Validation check 2]
- [ ] [Validation check 3]

**Validation Commands:**
```bash
[Commands to verify correct implementation]
```

---

IMPORTANT:
- Be specific (use actual code examples, not placeholders)
- Reference actual file paths if mentioned in errors
- Include validation commands that would catch this error
- Use proper markdown formatting
- Language should be Dart, Rust, SQL, or bash based on context
"""

        response = self.client.messages.create(
            model="claude-sonnet-4",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.content[0].text

    def find_empty_templates(self):
        """Find empty template sections in PROJECT_CONSTRAINTS.md"""
        if not self.constraints_file.exists():
            print(f"ERROR: {self.constraints_file} not found")
            return []

        with open(self.constraints_file, 'r') as f:
            content = f.read()

        # Find sections with placeholder templates
        empty_templates = re.findall(
            r'## Section (\d+):.*?\{ROOT_CAUSE_ANALYSIS\}',
            content,
            re.DOTALL
        )

        return empty_templates

    def update_constraints_file(self, section_id, filled_template):
        """Update PROJECT_CONSTRAINTS.md with filled template"""
        if not self.constraints_file.exists():
            print(f"ERROR: {self.constraints_file} not found")
            return False

        with open(self.constraints_file, 'r') as f:
            content = f.read()

        # Find and replace template section
        pattern = rf'## Section {section_id}:.*?(?=\n## |\Z)'
        updated_content = re.sub(
            pattern,
            filled_template,
            content,
            flags=re.DOTALL
        )

        # Backup original
        backup_file = self.constraints_file.with_suffix('.md.backup')
        with open(backup_file, 'w') as f:
            f.write(content)

        # Write updated
        with open(self.constraints_file, 'w') as f:
            f.write(updated_content)

        print(f"✓ Updated {self.constraints_file}")
        print(f"✓ Backup saved to {backup_file}")
        return True

    def create_skill_from_pattern(self, pattern_text, skill_name):
        """Auto-create a new skill from discovered pattern"""
        skills_dir = self.project_root / ".claude" / "skills" / skill_name
        skills_dir.mkdir(parents=True, exist_ok=True)

        skill_file = skills_dir / "SKILL.md"

        # Extract key information from pattern
        skill_content = f"""---
description: |
  Auto-generated skill from Ralph learning pattern.
  {skill_name.replace('-', ' ').title()}
allowed-tools:
  - Read
  - Bash
user-invocable: true
effort: medium
---

# {skill_name.replace('-', ' ').title()} Skill

**Auto-Generated**: {datetime.now().strftime('%Y-%m-%d')}
**Source**: Ralph Learning System

## Pattern Details

{pattern_text}

## Quick Reference

**Full documentation**: `Read PROJECT_CONSTRAINTS.md` (search for "{skill_name}")

**Validation**:
```bash
!`bash .claude/skills/{skill_name}/scripts/validate.sh`
```
"""

        with open(skill_file, 'w') as f:
            f.write(skill_content)

        print(f"✓ Created skill: {skill_file}")
        return skill_file

    def process_task(self, task_id):
        """Process a single task and fill its template"""
        print(f"\n🔍 Processing task: {task_id}")

        # Find log files
        log_dir = self.project_root / "logs"
        log_files = list(log_dir.glob(f"ralph_{task_id}_*.log"))

        if not log_files:
            print(f"⚠️  No log files found for {task_id}")
            return False

        print(f"   Found {len(log_files)} log files")

        # Extract errors
        error_patterns = self.extract_error_patterns([str(f) for f in log_files])
        attempts = len(log_files)

        if not error_patterns:
            print(f"⚠️  No error patterns found")
            return False

        print(f"   Extracted {len(error_patterns)} error patterns")

        # Fill template
        print(f"   Generating pattern with Claude Sonnet 4...")
        filled_template = self.fill_learning_template(task_id, error_patterns, attempts)

        # Update constraints file
        section_id = task_id.replace('CRIT-', '').replace('HIGH-', '').replace('MED-', '')
        success = self.update_constraints_file(section_id, filled_template)

        if success:
            print(f"✅ Successfully filled template for {task_id}")

            # Create skill
            skill_name = f"pattern-{task_id.lower()}"
            self.create_skill_from_pattern(filled_template, skill_name)

        return success

    def backfill_all_templates(self):
        """Backfill all empty templates from historical logs"""
        print("\n🔄 Backfilling all empty templates...")

        empty_templates = self.find_empty_templates()
        print(f"Found {len(empty_templates)} empty templates")

        filled_count = 0

        for template_id in empty_templates:
            # Infer task ID from template
            task_id = f"CRIT-{template_id}"

            if self.process_task(task_id):
                filled_count += 1

        print(f"\n✅ Backfill complete: {filled_count}/{len(empty_templates)} templates filled")


def main():
    parser = argparse.ArgumentParser(description="Ralph Learning Template Auto-Filler")
    parser.add_argument('--task-id', help="Task ID to process (e.g., CRIT-001)")
    parser.add_argument('--backfill', action='store_true', help="Backfill all empty templates")
    parser.add_argument('--api-key', help="Anthropic API key (or set ANTHROPIC_API_KEY env var)")

    args = parser.parse_args()

    filler = RalphLearningFiller(api_key=args.api_key)

    if args.backfill:
        filler.backfill_all_templates()
    elif args.task_id:
        filler.process_task(args.task_id)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
