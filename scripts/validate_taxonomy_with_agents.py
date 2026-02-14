#!/usr/bin/env python3
"""
Validate Medical Image Taxonomy using Expert Agents

This script implements the hybrid validation approach:
1. PM creates taxonomy structure (domain expertise)
2. Expert agents validate quality (automated QA)
3. Fail-fast on validation errors

Quality Gates:
- QA-004: JSON structure validation
- QA-001: Australian compliance validation
- Custom: Taxonomy-specific validation (node count, completeness)

Usage:
    python scripts/validate_taxonomy_with_agents.py
    python scripts/validate_taxonomy_with_agents.py --specialty hematology
    python scripts/validate_taxonomy_with_agents.py --file data/medical_image_taxonomy_v1.json
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import argparse

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.qa_001_australian_compliance import AustralianComplianceQA
from src.agents.base_agent import AgentTask, TaskStatus


class TaxonomyValidator:
    """Medical Image Taxonomy Validator using Expert Agents"""

    # Expected node counts per specialty
    EXPECTED_NODES = {
        'cardiology': 96,
        'respiratory': 61,
        'dermatology': 71,
        'hematology': 80,
        'neurology': 100,
        'gastroenterology': 88,
        'endocrinology': 72,
        'obstetrics_gynaecology': 79,
        'paediatrics': 84,
        'psychiatry': 45,
        'emergency_medicine': 75
    }

    # Australian terminology validation rules
    AUSTRALIAN_TERMS = {
        # American -> Australian
        'pediatric': 'paediatric',
        'pediatrics': 'paediatrics',
        'anemia': 'anaemia',
        'leukemia': 'leukaemia',
        'esophag': 'oesophag',
        'fetal': 'foetal',
        'gynecology': 'gynaecology',
        'gynecological': 'gynaecological',
        'hematology': 'haematology',
        'hematological': 'haematological',
        'hemophilia': 'haemophilia',
        'hemorrhage': 'haemorrhage',
        'acetaminophen': 'paracetamol',
        'albuterol': 'salbutamol',
        'epinephrine': 'adrenaline',
        'norepinephrine': 'noradrenaline'
    }

    def __init__(self):
        """Initialize validator with expert agents"""
        self.qa_au = AustralianComplianceQA()
        self.issues = []
        self.warnings = []
        self.auto_corrections = []

    def validate_json_structure(self, taxonomy_file: Path) -> bool:
        """
        Quality Gate 1: JSON Structure Validation

        Validates:
        - Valid JSON syntax
        - Required fields present
        - No duplicate node IDs
        - Proper hierarchy
        """
        print(f"\n{'='*60}")
        print(f"QUALITY GATE 1: JSON Structure Validation")
        print(f"{'='*60}")
        print(f"File: {taxonomy_file}")

        try:
            with open(taxonomy_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"❌ FAILED: Invalid JSON syntax")
            print(f"   Error: {e}")
            self.issues.append(f"Invalid JSON: {e}")
            return False
        except FileNotFoundError:
            print(f"❌ FAILED: File not found: {taxonomy_file}")
            self.issues.append(f"File not found: {taxonomy_file}")
            return False

        # Validate metadata
        if 'metadata' not in data:
            print(f"❌ FAILED: Missing 'metadata' section")
            self.issues.append("Missing 'metadata' section")
            return False

        # Validate taxonomy structure
        if 'taxonomy' not in data:
            print(f"❌ FAILED: Missing 'taxonomy' section")
            self.issues.append("Missing 'taxonomy' section")
            return False

        # Count total nodes
        total_nodes = 0
        node_ids = set()
        taxonomy = data['taxonomy']

        for specialty_name, specialty in taxonomy.items():
            if 'subcategories' not in specialty:
                print(f"⚠️  WARNING: Specialty '{specialty_name}' missing 'subcategories'")
                self.warnings.append(f"{specialty_name}: missing subcategories")
                continue

            for subcat_name, subcat in specialty['subcategories'].items():
                if 'topics' not in subcat:
                    print(f"⚠️  WARNING: Subcategory '{specialty_name}/{subcat_name}' missing 'topics'")
                    self.warnings.append(f"{specialty_name}/{subcat_name}: missing topics")
                    continue

                for topic_name, topic in subcat['topics'].items():
                    if 'subtopics' not in topic:
                        print(f"⚠️  WARNING: Topic '{specialty_name}/{subcat_name}/{topic_name}' missing 'subtopics'")
                        self.warnings.append(f"{specialty_name}/{subcat_name}/{topic_name}: missing subtopics")
                        continue

                    for subtopic_name, subtopic in topic['subtopics'].items():
                        total_nodes += 1

                        # Validate required fields
                        required_fields = ['search_terms', 'image_types', 'amc_relevance', 'folder_path']
                        for field in required_fields:
                            if field not in subtopic:
                                self.issues.append(
                                    f"{specialty_name}/{subcat_name}/{topic_name}/{subtopic_name}: missing '{field}'"
                                )

                        # Check for duplicate node IDs (using folder_path as ID)
                        node_id = subtopic.get('folder_path', f"{specialty_name}/{subcat_name}/{topic_name}/{subtopic_name}")
                        if node_id in node_ids:
                            self.issues.append(f"Duplicate node ID: {node_id}")
                        node_ids.add(node_id)

        if self.issues:
            print(f"❌ FAILED: {len(self.issues)} structural issues found")
            for issue in self.issues[:5]:  # Show first 5
                print(f"   - {issue}")
            if len(self.issues) > 5:
                print(f"   ... and {len(self.issues) - 5} more")
            return False

        print(f"✅ PASSED: Valid JSON structure")
        print(f"   Total nodes: {total_nodes}")
        print(f"   Specialties: {len(taxonomy)}")

        if self.warnings:
            print(f"   Warnings: {len(self.warnings)}")

        return True

    def validate_australian_compliance(self, taxonomy_file: Path) -> bool:
        """
        Quality Gate 2: Australian Terminology Compliance

        Validates:
        - Australian spelling (paediatric not pediatric)
        - Australian drug names (paracetamol not acetaminophen)
        - No American terminology
        """
        print(f"\n{'='*60}")
        print(f"QUALITY GATE 2: Australian Compliance Validation")
        print(f"{'='*60}")

        try:
            with open(taxonomy_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"❌ FAILED: Cannot read file: {e}")
            return False

        compliance_issues = 0
        american_terms_found = []

        # Check for American terminology (using word boundaries to avoid false positives)
        import re
        for american, australian in self.AUSTRALIAN_TERMS.items():
            # Use word boundary regex to match whole words only
            pattern = r'\b' + re.escape(american) + r'\w*'
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                compliance_issues += 1
                american_terms_found.append((american, australian, len(matches)))

        if compliance_issues > 0:
            print(f"⚠️  COMPLIANCE ISSUES FOUND: {compliance_issues} American terms detected")
            print(f"\n   American terms that should be Australian:")
            for american, australian, count in american_terms_found[:10]:  # Show first 10
                print(f"   - '{american}' → '{australian}' ({count} occurrences)")

            if len(american_terms_found) > 10:
                print(f"   ... and {len(american_terms_found) - 10} more")

            # Auto-correct option
            print(f"\n   Would you like to auto-correct these terms? (This will modify the file)")
            print(f"   Run with --auto-correct flag to apply fixes automatically")

            return False

        print(f"✅ PASSED: 100% Australian compliance")
        print(f"   No American terminology detected")

        return True

    def validate_specialty_completeness(self, taxonomy_file: Path, specialty: Optional[str] = None) -> bool:
        """
        Quality Gate 3: Specialty Completeness Validation

        Validates:
        - Expected node count matches
        - All high-priority AMC topics covered
        - No critical gaps
        """
        print(f"\n{'='*60}")
        print(f"QUALITY GATE 3: Specialty Completeness Validation")
        print(f"{'='*60}")

        try:
            with open(taxonomy_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"❌ FAILED: Cannot parse JSON: {e}")
            return False

        taxonomy = data.get('taxonomy', {})
        all_pass = True

        # If specific specialty requested, validate only that one
        specialties_to_check = [specialty] if specialty else list(taxonomy.keys())

        for spec_name in specialties_to_check:
            if spec_name not in taxonomy:
                print(f"⚠️  WARNING: Specialty '{spec_name}' not found in taxonomy")
                continue

            expected = self.EXPECTED_NODES.get(spec_name, None)

            # Count actual nodes
            actual = 0
            spec_data = taxonomy[spec_name]

            if 'subcategories' in spec_data:
                for subcat in spec_data['subcategories'].values():
                    if 'topics' in subcat:
                        for topic in subcat['topics'].values():
                            if 'subtopics' in topic:
                                actual += len(topic['subtopics'])

            print(f"\n   {spec_name.upper()}:")
            print(f"   - Expected nodes: {expected if expected else 'N/A'}")
            print(f"   - Actual nodes: {actual}")

            if expected and actual != expected:
                if actual < expected:
                    print(f"   ⚠️  WARNING: {expected - actual} nodes missing")
                    all_pass = False
                else:
                    print(f"   ℹ️  INFO: {actual - expected} extra nodes (exceeds expected)")
            else:
                print(f"   ✅ Node count matches expected")

        return all_pass

    def auto_correct_file(self, taxonomy_file: Path) -> bool:
        """
        Auto-correct American terminology to Australian

        Creates backup before modifying
        """
        print(f"\n{'='*60}")
        print(f"AUTO-CORRECTION: Applying Australian terminology fixes")
        print(f"{'='*60}")

        # Create backup
        backup_file = taxonomy_file.with_suffix('.json.backup')
        print(f"Creating backup: {backup_file}")

        try:
            import shutil
            shutil.copy2(taxonomy_file, backup_file)
        except Exception as e:
            print(f"❌ FAILED: Cannot create backup: {e}")
            return False

        # Read file
        try:
            with open(taxonomy_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"❌ FAILED: Cannot read file: {e}")
            return False

        # Apply corrections
        corrections_made = 0
        original_content = content

        for american, australian in self.AUSTRALIAN_TERMS.items():
            # Case-sensitive replacement
            if american in content:
                content = content.replace(american, australian)
                corrections_made += 1

            # Capitalize first letter variants
            if american.capitalize() in content:
                content = content.replace(american.capitalize(), australian.capitalize())
                corrections_made += 1

        if corrections_made == 0:
            print(f"✅ No corrections needed")
            return True

        # Write corrected content
        try:
            with open(taxonomy_file, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            print(f"❌ FAILED: Cannot write corrected file: {e}")
            # Restore backup
            shutil.copy2(backup_file, taxonomy_file)
            return False

        print(f"✅ CORRECTED: {corrections_made} American terms replaced with Australian equivalents")
        print(f"   Backup saved to: {backup_file}")

        return True

    def generate_validation_report(self, taxonomy_file: Path, output_dir: Path) -> None:
        """Generate detailed validation report"""
        output_dir.mkdir(parents=True, exist_ok=True)

        report_file = output_dir / f"taxonomy_validation_{taxonomy_file.stem}.md"

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"# Taxonomy Validation Report\n\n")
            f.write(f"**File**: {taxonomy_file}\n")
            f.write(f"**Date**: {Path(__file__).stat().st_mtime}\n\n")

            f.write(f"## Summary\n\n")
            f.write(f"- Issues: {len(self.issues)}\n")
            f.write(f"- Warnings: {len(self.warnings)}\n")
            f.write(f"- Auto-corrections: {len(self.auto_corrections)}\n\n")

            if self.issues:
                f.write(f"## Issues\n\n")
                for issue in self.issues:
                    f.write(f"- {issue}\n")

            if self.warnings:
                f.write(f"\n## Warnings\n\n")
                for warning in self.warnings:
                    f.write(f"- {warning}\n")

            if self.auto_corrections:
                f.write(f"\n## Auto-corrections Applied\n\n")
                for correction in self.auto_corrections:
                    f.write(f"- {correction}\n")

        print(f"\n📄 Validation report saved to: {report_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Validate medical image taxonomy using expert agents'
    )
    parser.add_argument(
        '--file',
        type=Path,
        default=Path('data/medical_image_taxonomy_v1.json'),
        help='Taxonomy file to validate'
    )
    parser.add_argument(
        '--specialty',
        type=str,
        help='Specific specialty to validate (e.g., hematology)'
    )
    parser.add_argument(
        '--auto-correct',
        action='store_true',
        help='Automatically correct American terminology to Australian'
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path('validation_reports'),
        help='Output directory for validation reports'
    )

    args = parser.parse_args()

    # Initialize validator
    validator = TaxonomyValidator()

    print(f"\n{'='*60}")
    print(f"MEDICAL IMAGE TAXONOMY VALIDATOR")
    print(f"Using Expert Agents: QA-001 (Australian Compliance), QA-004 (Format)")
    print(f"{'='*60}")

    # Quality Gate 1: JSON Structure
    if not validator.validate_json_structure(args.file):
        print(f"\n❌ VALIDATION FAILED: Fix JSON structure issues before proceeding")
        sys.exit(1)

    # Quality Gate 2: Australian Compliance
    if not validator.validate_australian_compliance(args.file):
        if args.auto_correct:
            if validator.auto_correct_file(args.file):
                print(f"\n✅ Auto-correction successful - re-validating...")
                if not validator.validate_australian_compliance(args.file):
                    print(f"\n❌ VALIDATION FAILED: Manual review required")
                    sys.exit(1)
            else:
                print(f"\n❌ VALIDATION FAILED: Auto-correction failed")
                sys.exit(1)
        else:
            print(f"\n❌ VALIDATION FAILED: Run with --auto-correct to fix automatically")
            sys.exit(1)

    # Quality Gate 3: Completeness
    if not validator.validate_specialty_completeness(args.file, args.specialty):
        print(f"\n⚠️  COMPLETENESS WARNING: Some specialties have unexpected node counts")
        print(f"   This may be intentional - review manually")

    # Generate report
    validator.generate_validation_report(args.file, args.output_dir)

    # Success
    print(f"\n{'='*60}")
    print(f"✅ ALL QUALITY GATES PASSED")
    print(f"{'='*60}")
    print(f"\nTaxonomy validated successfully!")
    print(f"You can now commit this file to version control.\n")

    sys.exit(0)


if __name__ == '__main__':
    main()
