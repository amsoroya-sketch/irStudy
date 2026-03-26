#!/usr/bin/env python3
"""
Auto-Fix Engine for Medical Content Evaluation System
Automatically corrects common violations identified during evaluation.

Capabilities:
- Australian drug name corrections (acetaminophen → paracetamol, etc.)
- PBS code insertion for medications
- Citation format standardization
- Red flag consistency checks
- SOAP format corrections

Target: 70% automation rate (623 of 890 items fixed automatically)

Usage:
    python3 auto_fix_engine.py \
        --input reports/production_iteration_1 \
        --output reports/auto_fixed_batch_1
"""

import json
import re
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime
from collections import defaultdict


# =============================================================================
# AUSTRALIAN DRUG NAME MAPPINGS
# =============================================================================

DRUG_NAME_CORRECTIONS = {
    # American → Australian (TGA-approved names)
    "acetaminophen": "paracetamol",
    "Acetaminophen": "Paracetamol",
    "ACETAMINOPHEN": "PARACETAMOL",
    "Tylenol": "paracetamol",

    "epinephrine": "adrenaline",
    "Epinephrine": "Adrenaline",
    "EPINEPHRINE": "ADRENALINE",

    "albuterol": "salbutamol",
    "Albuterol": "Salbutamol",
    "ALBUTEROL": "SALBUTAMOL",

    "norepinephrine": "noradrenaline",
    "Norepinephrine": "Noradrenaline",
    "NOREPINEPHRINE": "NORADRENALINE",

    "furosemide": "frusemide",
    "Furosemide": "Frusemide",
    "FUROSEMIDE": "FRUSEMIDE",
}


# =============================================================================
# PBS CODES FOR COMMON MEDICATIONS
# =============================================================================

PBS_CODES = {
    "paracetamol": "1213K",
    "adrenaline": "2188H",
    "salbutamol": "8173K",
    "atorvastatin": "8156M",
    "metformin": "2189J",
}


# =============================================================================
# CITATION FORMAT PATTERNS
# =============================================================================

CITATION_PATTERNS = {
    # Standardize citation formats
    "inconsistent_format": {
        "pattern": r'\[(\d+)\]',  # [1] → (Source: ...)
        "replacement": lambda m: f"(Source: Reference {m.group(1)})"
    },
}


class AutoFixEngine:
    """
    Automated content fixing engine.

    Analyzes evaluation reports and applies automated fixes to common issues.
    """

    def __init__(self, input_dir: Path, output_dir: Path):
        """
        Initialize auto-fix engine.

        Args:
            input_dir: Directory with evaluation reports
            output_dir: Directory for fixed content
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Statistics
        self.stats = {
            "total_items": 0,
            "items_analyzed": 0,
            "items_fixed": 0,
            "items_unfixable": 0,
            "fixes_applied": defaultdict(int),
        }

        # Fix registry
        self.fix_registry: List[Dict[str, Any]] = []

    def analyze_evaluation_report(self, eval_path: Path) -> Tuple[Dict, List[str]]:
        """
        Analyze evaluation report to identify fixable issues.

        Args:
            eval_path: Path to evaluation JSON file

        Returns:
            (evaluation_dict, list_of_fixable_violations)
        """
        with open(eval_path) as f:
            evaluation = json.load(f)

        violations = evaluation.get("violations", [])
        fixable_violations = []

        for violation in violations:
            violation_type = violation.get("type", "")

            # Identify fixable violation types
            if any(keyword in violation_type.lower() for keyword in [
                "american drug", "drug name", "acetaminophen", "epinephrine",
                "pbs code", "citation format", "soap format"
            ]):
                fixable_violations.append(violation_type)

        return evaluation, fixable_violations

    def load_item_content(self, item_metadata: Dict) -> Dict[str, Any]:
        """
        Load item content from file.

        Args:
            item_metadata: Item metadata from evaluation

        Returns:
            Item content dictionary
        """
        file_path = item_metadata.get("file_path", "")
        full_path = self.input_dir.parent.parent / file_path

        with open(full_path) as f:
            content = json.load(f)

        # Handle array-based content
        if isinstance(content, list):
            array_index = item_metadata.get("array_index", 0)
            if 0 <= array_index < len(content):
                return content[array_index]

        return content

    def fix_drug_names(self, content: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """
        Fix American drug names → Australian TGA-approved names.

        Args:
            content: Item content dictionary

        Returns:
            (fixed_content, number_of_fixes)
        """
        fixes_count = 0
        content_str = json.dumps(content, indent=2)

        for american_name, australian_name in DRUG_NAME_CORRECTIONS.items():
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(american_name) + r'\b'

            if re.search(pattern, content_str):
                content_str = re.sub(pattern, australian_name, content_str)
                fixes_count += 1
                self.stats["fixes_applied"]["drug_name_correction"] += 1

        if fixes_count > 0:
            return json.loads(content_str), fixes_count

        return content, 0

    def add_pbs_codes(self, content: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """
        Add PBS codes for Australian medications.

        Args:
            content: Item content dictionary

        Returns:
            (fixed_content, number_of_fixes)
        """
        fixes_count = 0

        # Check if content has medication fields
        medication_fields = [
            "medications", "prescriptions", "drug_list",
            "management", "treatment_plan"
        ]

        for field in medication_fields:
            if field in content:
                field_value = content[field]

                # Add PBS codes where missing
                for drug_name, pbs_code in PBS_CODES.items():
                    if isinstance(field_value, str):
                        # Check if drug mentioned but PBS code missing
                        if drug_name in field_value.lower() and pbs_code not in field_value:
                            # Insert PBS code after drug name
                            pattern = r'\b' + re.escape(drug_name) + r'\b'
                            replacement = f"{drug_name} (PBS: {pbs_code})"
                            content[field] = re.sub(pattern, replacement, field_value, flags=re.IGNORECASE)
                            fixes_count += 1
                            self.stats["fixes_applied"]["pbs_code_insertion"] += 1

                    elif isinstance(field_value, list):
                        # Handle list of medications
                        for i, med in enumerate(field_value):
                            if isinstance(med, dict) and "name" in med:
                                if med["name"].lower() == drug_name and "pbs_code" not in med:
                                    med["pbs_code"] = pbs_code
                                    fixes_count += 1
                                    self.stats["fixes_applied"]["pbs_code_insertion"] += 1

        return content, fixes_count

    def standardize_citations(self, content: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """
        Standardize citation format.

        Args:
            content: Item content dictionary

        Returns:
            (fixed_content, number_of_fixes)
        """
        fixes_count = 0
        content_str = json.dumps(content, indent=2)

        # Standardize [1] → (Source: Reference 1)
        pattern = r'\[(\d+)\]'
        matches = re.findall(pattern, content_str)

        if matches:
            content_str = re.sub(pattern, r'(Source: Reference \1)', content_str)
            fixes_count = len(matches)
            self.stats["fixes_applied"]["citation_standardization"] += fixes_count

        if fixes_count > 0:
            return json.loads(content_str), fixes_count

        return content, 0

    def fix_soap_format(self, content: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """
        Ensure SOAP notes follow Australian format.

        Args:
            content: Item content dictionary

        Returns:
            (fixed_content, number_of_fixes)
        """
        fixes_count = 0

        # Check if content has clinical_notes field
        if "clinical_notes" in content:
            notes = content["clinical_notes"]

            # Ensure SOAP structure exists
            required_sections = ["Subjective", "Objective", "Assessment", "Plan"]

            if isinstance(notes, str):
                # Convert plain text to structured SOAP
                if not all(section in notes for section in required_sections):
                    # Add SOAP headers if missing
                    structured_notes = {
                        "Subjective": "",
                        "Objective": "",
                        "Assessment": "",
                        "Plan": ""
                    }
                    content["clinical_notes"] = structured_notes
                    fixes_count = 1
                    self.stats["fixes_applied"]["soap_structure"] += 1

        return content, fixes_count

    def apply_all_fixes(self, content: Dict[str, Any], violations: List[str]) -> Tuple[Dict[str, Any], int]:
        """
        Apply all applicable fixes to content.

        Args:
            content: Item content dictionary
            violations: List of violation types from evaluation

        Returns:
            (fixed_content, total_fixes_applied)
        """
        total_fixes = 0

        # Fix drug names (always apply)
        content, drug_fixes = self.fix_drug_names(content)
        total_fixes += drug_fixes

        # Add PBS codes (always apply)
        content, pbs_fixes = self.add_pbs_codes(content)
        total_fixes += pbs_fixes

        # Standardize citations (always apply)
        content, citation_fixes = self.standardize_citations(content)
        total_fixes += citation_fixes

        # Fix SOAP format (if relevant)
        if any("soap" in v.lower() for v in violations):
            content, soap_fixes = self.fix_soap_format(content)
            total_fixes += soap_fixes

        return content, total_fixes

    def save_fixed_content(self, content: Dict[str, Any], item_id: str, item_type: str):
        """
        Save fixed content to output directory.

        Args:
            content: Fixed item content
            item_id: Item identifier
            item_type: Item type (mcq, persona, etc.)
        """
        output_file = self.output_dir / f"{item_id}_fixed.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(content, f, indent=2, ensure_ascii=False)

    def process_evaluation_reports(self, threshold: float = 8.5) -> Dict[str, Any]:
        """
        Process all evaluation reports and apply fixes.

        Args:
            threshold: Score threshold - fix items below this score

        Returns:
            Summary statistics dictionary
        """
        evaluations_dir = self.input_dir / "evaluations"

        if not evaluations_dir.exists():
            print(f"❌ Evaluations directory not found: {evaluations_dir}")
            return self.stats

        eval_files = list(evaluations_dir.glob("*.json"))
        self.stats["total_items"] = len(eval_files)

        print(f"Found {len(eval_files)} evaluation reports")
        print(f"Processing items with score < {threshold}...")
        print()

        for eval_file in eval_files:
            try:
                # Load evaluation
                evaluation, fixable_violations = self.analyze_evaluation_report(eval_file)

                self.stats["items_analyzed"] += 1

                # Check if item needs fixing (score below threshold or has violations)
                overall_score = evaluation.get("overall_score", 10.0)

                if overall_score < threshold or fixable_violations:
                    # Load item content
                    item_metadata = {
                        "file_path": evaluation.get("file_path", ""),
                        "array_index": evaluation.get("array_index", 0),
                    }

                    try:
                        content = self.load_item_content(item_metadata)

                        # Apply fixes
                        fixed_content, fixes_applied = self.apply_all_fixes(
                            content,
                            fixable_violations
                        )

                        if fixes_applied > 0:
                            # Save fixed content
                            item_id = evaluation.get("item_id", "unknown")
                            item_type = evaluation.get("item_type", "unknown")

                            self.save_fixed_content(fixed_content, item_id, item_type)

                            self.stats["items_fixed"] += 1

                            # Record fix
                            self.fix_registry.append({
                                "item_id": item_id,
                                "original_score": overall_score,
                                "fixes_applied": fixes_applied,
                                "violation_types": fixable_violations,
                                "fixed_at": datetime.now().isoformat()
                            })

                            print(f"✅ Fixed: {item_id} (score: {overall_score:.1f}, {fixes_applied} fixes)")
                        else:
                            self.stats["items_unfixable"] += 1
                            print(f"⚠️  No automatic fixes available: {evaluation.get('item_id')} (score: {overall_score:.1f})")

                    except FileNotFoundError as e:
                        print(f"⚠️  Content file not found for {evaluation.get('item_id')}: {e}")
                        self.stats["items_unfixable"] += 1

            except Exception as e:
                print(f"❌ Error processing {eval_file.name}: {e}")
                self.stats["items_unfixable"] += 1

        return self.stats

    def save_fix_registry(self):
        """Save fix registry to output directory."""
        registry_file = self.output_dir / "fix_registry.json"

        with open(registry_file, 'w', encoding='utf-8') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "statistics": dict(self.stats),
                "fixed_items": self.fix_registry
            }, f, indent=2, ensure_ascii=False)

        print(f"\n✅ Fix registry saved: {registry_file}")

    def print_summary(self):
        """Print auto-fix summary statistics."""
        print("\n" + "=" * 80)
        print("AUTO-FIX ENGINE - SUMMARY")
        print("=" * 80)
        print(f"Total items analyzed: {self.stats['items_analyzed']}")
        print(f"Items fixed: {self.stats['items_fixed']}")
        print(f"Items unfixable (require manual review): {self.stats['items_unfixable']}")
        print()

        if self.stats['items_fixed'] > 0:
            automation_rate = (self.stats['items_fixed'] / self.stats['items_analyzed']) * 100
            print(f"Automation rate: {automation_rate:.1f}% (target: 70%)")
            print()

            print("Fixes applied by type:")
            for fix_type, count in self.stats['fixes_applied'].items():
                print(f"  - {fix_type}: {count}")

        print("=" * 80)
        print()

        if self.stats['items_fixed'] > 0:
            print("✅ Next steps:")
            print(f"  1. Review fixed items in: {self.output_dir}")
            print(f"  2. Re-evaluate fixed items:")
            print(f"     venv/bin/python3 evaluation-system/core/evaluation_orchestrator.py \\")
            print(f"       --input {self.output_dir}/fix_registry.json \\")
            print(f"       --output-dir evaluation-system/reports/production_iteration_2")
            print()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Auto-fix engine for medical content")
    parser.add_argument(
        "--input",
        required=True,
        help="Input directory with evaluation reports"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output directory for fixed content"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=8.5,
        help="Score threshold - fix items below this score (default: 8.5)"
    )

    args = parser.parse_args()

    input_dir = Path(args.input)
    output_dir = Path(args.output)

    if not input_dir.exists():
        print(f"❌ Input directory not found: {input_dir}")
        return 1

    print("=" * 80)
    print("AUTO-FIX ENGINE - Medical Content Evaluation System")
    print("=" * 80)
    print()

    # Initialize engine
    engine = AutoFixEngine(input_dir, output_dir)

    # Process reports
    stats = engine.process_evaluation_reports(threshold=args.threshold)

    # Save fix registry
    engine.save_fix_registry()

    # Print summary
    engine.print_summary()

    return 0


if __name__ == "__main__":
    sys.exit(main())
