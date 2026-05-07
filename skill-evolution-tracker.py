#!/usr/bin/env python3
"""
Skill Evolution Tracker
Version: 1.0

Tracks skill usage patterns, detects over/under-application,
and auto-generates description improvements for better triggering.

Usage:
    python skill-evolution-tracker.py analyze --skill ato-compliance
    python skill-evolution-tracker.py report --days 30
    python skill-evolution-tracker.py optimize --all
"""

import argparse
import re
import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import sqlite3


class SkillEvolutionTracker:
    def __init__(self, db_path=None):
        self.project_root = Path(__file__).parent
        self.db_path = db_path or (self.project_root / "skill_usage.db")
        self.skills_dir = self.project_root / ".claude" / "skills"
        self.logs_dir = self.project_root / "logs"
        self.init_database()

    def init_database(self):
        """Initialize SQLite database for tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS skill_invocations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                skill_name TEXT NOT NULL,
                task_id TEXT,
                triggered BOOLEAN,
                relevant BOOLEAN,
                outcome TEXT,  -- success, failure, partial
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS skill_performance (
                skill_name TEXT PRIMARY KEY,
                total_invocations INTEGER DEFAULT 0,
                relevant_invocations INTEGER DEFAULT 0,
                successful_outcomes INTEGER DEFAULT 0,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS missing_triggers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL,
                expected_skill TEXT NOT NULL,
                keywords_found TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    def track_skill_invocation(self, skill_name, task_id, triggered=True, relevant=True, outcome='success'):
        """Log skill invocation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO skill_invocations (skill_name, task_id, triggered, relevant, outcome)
            VALUES (?, ?, ?, ?, ?)
        ''', (skill_name, task_id, triggered, relevant, outcome))

        # Update performance stats
        cursor.execute('''
            INSERT INTO skill_performance (skill_name, total_invocations, relevant_invocations, successful_outcomes)
            VALUES (?, 1, ?, ?)
            ON CONFLICT(skill_name) DO UPDATE SET
                total_invocations = total_invocations + 1,
                relevant_invocations = relevant_invocations + ?,
                successful_outcomes = successful_outcomes + ?,
                last_updated = CURRENT_TIMESTAMP
        ''', (skill_name, int(relevant), int(outcome == 'success'), int(relevant), int(outcome == 'success')))

        conn.commit()
        conn.close()

    def analyze_logs_for_patterns(self, days=30):
        """Analyze Ralph logs to detect skill usage patterns"""
        print(f"\n🔍 Analyzing logs from last {days} days...")

        cutoff_date = datetime.now() - timedelta(days=days)
        log_files = sorted(self.logs_dir.glob("ralph_*.log"), key=lambda f: f.stat().st_mtime, reverse=True)

        patterns = defaultdict(lambda: {"triggered": 0, "keywords": Counter()})

        for log_file in log_files:
            # Check file age
            if datetime.fromtimestamp(log_file.stat().st_mtime) < cutoff_date:
                continue

            # Extract task ID
            task_match = re.search(r'ralph_([A-Z]+-\d+)_', log_file.name)
            if not task_match:
                continue

            task_id = task_match.group(1)

            with open(log_file, 'r') as f:
                content = f.read()

                # Detect skill invocations
                skill_refs = re.findall(r'\.claude/skills/([a-z-]+)/SKILL\.md', content)
                for skill in set(skill_refs):
                    patterns[skill]["triggered"] += 1

                    # Extract keywords from context
                    keywords = re.findall(r'\b(tax|super|ATO|contribution|FFI|database|security|encrypt)\b', content, re.IGNORECASE)
                    patterns[skill]["keywords"].update([k.lower() for k in keywords])

                # Track all skills used in this task
                for skill in set(skill_refs):
                    self.track_skill_invocation(skill, task_id, triggered=True, relevant=True)

        print(f"✓ Analyzed {len(log_files)} log files")
        return patterns

    def analyze_skill_performance(self, skill_name):
        """Analyze if skill is over/under applied"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get performance stats
        cursor.execute('''
            SELECT total_invocations, relevant_invocations, successful_outcomes
            FROM skill_performance
            WHERE skill_name = ?
        ''', (skill_name,))

        result = cursor.fetchone()
        if not result:
            print(f"⚠️  No data for skill: {skill_name}")
            conn.close()
            return None

        total, relevant, successful = result

        # Get failures in domain
        cursor.execute('''
            SELECT COUNT(*)
            FROM skill_invocations
            WHERE skill_name != ? AND outcome = 'failure'
            AND task_id IN (
                SELECT DISTINCT task_id
                FROM missing_triggers
                WHERE expected_skill = ?
            )
        ''', (skill_name, skill_name))

        failures_in_domain = cursor.fetchone()[0]

        conn.close()

        # Calculate metrics
        relevance_ratio = relevant / total if total > 0 else 0
        success_ratio = successful / relevant if relevant > 0 else 0

        # Determine over/under application
        over_applied = total > 50 and relevance_ratio < 0.5
        under_applied = failures_in_domain > 10 and total == 0

        return {
            'skill_name': skill_name,
            'total_invocations': total,
            'relevant_invocations': relevant,
            'successful_outcomes': successful,
            'failures_in_domain': failures_in_domain,
            'relevance_ratio': relevance_ratio,
            'success_ratio': success_ratio,
            'over_applied': over_applied,
            'under_applied': under_applied,
            'recommendations': self._generate_recommendations(skill_name, total, relevance_ratio, under_applied, over_applied)
        }

    def _generate_recommendations(self, skill_name, total, relevance_ratio, under_applied, over_applied):
        """Generate skill description improvements"""
        recommendations = []

        if under_applied:
            # Find missed keywords from logs
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT keywords_found FROM missing_triggers
                WHERE expected_skill = ?
                LIMIT 10
            ''', (skill_name,))
            missed_keywords = [row[0] for row in cursor.fetchall() if row[0]]
            conn.close()

            if missed_keywords:
                keywords_str = ", ".join(set(missed_keywords))
                recommendations.append(f"Add to description: {keywords_str}")
                recommendations.append(f"Skill '{skill_name}' under-applied ({total} invocations vs {failures_in_domain} expected)")

        if over_applied:
            recommendations.append(f"Narrow description to exclude false positives (relevance: {relevance_ratio:.0%})")
            recommendations.append(f"Add paths constraint to limit activation scope")

        if not over_applied and not under_applied and relevance_ratio > 0.8:
            recommendations.append(f"✅ Skill performing well (relevance: {relevance_ratio:.0%})")

        return recommendations

    def auto_update_skill_description(self, skill_name, recommendations):
        """Automatically update skill description based on recommendations"""
        skill_file = self.skills_dir / skill_name / "SKILL.md"

        if not skill_file.exists():
            print(f"⚠️  Skill file not found: {skill_file}")
            return False

        with open(skill_file, 'r') as f:
            content = f.read()

        # Extract current description from frontmatter
        description_match = re.search(r'description: \|(.*?)(?=\n[a-z-]+:|\n---)', content, re.DOTALL)
        if not description_match:
            print(f"⚠️  Could not find description in {skill_file}")
            return False

        current_description = description_match.group(1).strip()

        # Add recommended keywords
        for rec in recommendations:
            if rec.startswith("Add to description:"):
                new_keywords = rec.replace("Add to description:", "").strip()
                if new_keywords not in current_description:
                    current_description += f"\n  {new_keywords}"

        # Update frontmatter
        updated_content = re.sub(
            r'(description: \|)(.*?)((?=\n[a-z-]+:|\n---))',
            f'\\1\n  {current_description}\\3',
            content,
            flags=re.DOTALL
        )

        # Backup original
        backup_file = skill_file.with_suffix('.md.backup')
        with open(backup_file, 'w') as f:
            f.write(content)

        # Write updated
        with open(skill_file, 'w') as f:
            f.write(updated_content)

        print(f"✓ Updated {skill_file}")
        print(f"✓ Backup saved to {backup_file}")
        return True

    def generate_report(self, days=30):
        """Generate skill usage report"""
        print(f"\n📊 Skill Usage Report (Last {days} Days)")
        print("=" * 60)

        # Analyze logs first
        self.analyze_logs_for_patterns(days)

        # Get all skills
        skill_dirs = [d for d in self.skills_dir.iterdir() if d.is_dir() and (d / "SKILL.md").exists()]

        for skill_dir in skill_dirs:
            skill_name = skill_dir.name
            analysis = self.analyze_skill_performance(skill_name)

            if not analysis:
                continue

            print(f"\n{skill_name}")
            print("-" * 60)
            print(f"  Total Invocations: {analysis['total_invocations']}")
            print(f"  Relevant: {analysis['relevant_invocations']} ({analysis['relevance_ratio']:.0%})")
            print(f"  Successful: {analysis['successful_outcomes']} ({analysis['success_ratio']:.0%})")

            if analysis['over_applied']:
                print(f"  ⚠️  OVER-APPLIED")
            elif analysis['under_applied']:
                print(f"  ⚠️  UNDER-APPLIED ({analysis['failures_in_domain']} missed opportunities)")

            if analysis['recommendations']:
                print(f"\n  Recommendations:")
                for rec in analysis['recommendations']:
                    print(f"    • {rec}")


def main():
    parser = argparse.ArgumentParser(description="Skill Evolution Tracker")
    parser.add_argument('command', choices=['analyze', 'report', 'optimize'], help="Command to run")
    parser.add_argument('--skill', help="Specific skill to analyze")
    parser.add_argument('--days', type=int, default=30, help="Days of history to analyze")
    parser.add_argument('--all', action='store_true', help="Process all skills")

    args = parser.parse_args()

    tracker = SkillEvolutionTracker()

    if args.command == 'analyze':
        if not args.skill:
            print("ERROR: --skill required for analyze command")
            return

        analysis = tracker.analyze_skill_performance(args.skill)
        if analysis:
            print(f"\n📊 Analysis for '{args.skill}':")
            print(json.dumps(analysis, indent=2, default=str))

    elif args.command == 'report':
        tracker.generate_report(args.days)

    elif args.command == 'optimize':
        if args.all:
            print("\n🔧 Optimizing all skills...")
            skill_dirs = [d for d in tracker.skills_dir.iterdir() if d.is_dir() and (d / "SKILL.md").exists()]

            for skill_dir in skill_dirs:
                skill_name = skill_dir.name
                analysis = tracker.analyze_skill_performance(skill_name)

                if analysis and analysis['recommendations']:
                    print(f"\n{skill_name}:")
                    for rec in analysis['recommendations']:
                        print(f"  • {rec}")

                    if not rec.startswith("✅"):
                        tracker.auto_update_skill_description(skill_name, analysis['recommendations'])
        else:
            print("ERROR: --all required for optimize command")


if __name__ == "__main__":
    main()
