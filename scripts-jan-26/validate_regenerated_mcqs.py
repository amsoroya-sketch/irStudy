#!/usr/bin/env python3
"""
Validate Regenerated MCQs - Constraint Compliance Checker

Validates that regenerated MCQs meet all constraints:
- Constraint 1: Australian medical context
- Constraint 12: No placeholder content
- Citations preserved (3 per MCQ, >0.70 confidence)

Usage:
    python scripts-jan-26/validate_regenerated_mcqs.py data/mcqs/week3_cardiology_200_mcqs.json
"""

import json
import sys
import re
from pathlib import Path
from typing import Dict, List, Tuple


class MCQValidator:
    """Validate regenerated MCQs against project constraints"""
    
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.data = None
        self.errors = []
        self.warnings = []
        
    def load_file(self):
        """Load MCQ file"""
        print(f"📥 Loading: {self.file_path}")
        
        if not self.file_path.exists():
            print(f"❌ ERROR: File not found: {self.file_path}")
            sys.exit(1)
        
        with open(self.file_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        
        print(f"   Total MCQs: {len(self.data['mcqs'])}")
    
    def validate_all(self) -> bool:
        """Run all validation checks"""
        print("\n" + "="*70)
        print("CONSTRAINT VALIDATION")
        print("="*70)
        
        # Check 1: No placeholders (Constraint 12)
        print("\n1. Checking for placeholder content (Constraint 12)...")
        placeholders = self.check_placeholders()
        if placeholders > 0:
            self.errors.append(f"Found {placeholders} MCQs with placeholder content")
        else:
            print("   ✅ No placeholder content detected")
        
        # Check 2: Australian spelling (Constraint 1)
        print("\n2. Checking Australian spelling (Constraint 1)...")
        american_terms = self.check_australian_spelling()
        if american_terms > 0:
            self.errors.append(f"Found {american_terms} MCQs with American spelling")
        else:
            print("   ✅ Australian spelling used throughout")
        
        # Check 3: Australian drug names (Constraint 1)
        print("\n3. Checking Australian drug names (Constraint 1)...")
        american_drugs = self.check_australian_drugs()
        if american_drugs > 0:
            self.errors.append(f"Found {american_drugs} MCQs with American drug names")
        else:
            print("   ✅ Australian drug names used")
        
        # Check 4: Citations preserved
        print("\n4. Checking RAG citations preserved...")
        citation_issues = self.check_citations()
        if citation_issues > 0:
            self.errors.append(f"Found {citation_issues} MCQs with citation issues")
        else:
            print("   ✅ All citations preserved (3 per MCQ, >0.70 confidence)")
        
        # Check 5: Content substance
        print("\n5. Checking content substance...")
        substance_issues = self.check_content_substance()
        if substance_issues > 0:
            self.warnings.append(f"Found {substance_issues} MCQs with minimal content")
        else:
            print("   ✅ All MCQs have substantial content")
        
        # Check 6: Patient demographics
        print("\n6. Checking patient demographics...")
        demo_issues = self.check_demographics()
        if demo_issues > 0:
            self.warnings.append(f"Found {demo_issues} MCQs without demographics")
        else:
            print("   ✅ All MCQs have patient demographics")
        
        # Summary
        print("\n" + "="*70)
        print("VALIDATION SUMMARY")
        print("="*70)
        
        if len(self.errors) == 0 and len(self.warnings) == 0:
            print("✅ ALL CHECKS PASSED")
            print(f"   File: {self.file_path}")
            print(f"   MCQs: {len(self.data['mcqs'])}")
            print(f"   Constraints: 1 (Australian), 12 (No placeholders)")
            return True
        else:
            if len(self.errors) > 0:
                print(f"❌ {len(self.errors)} ERRORS:")
                for error in self.errors:
                    print(f"   - {error}")
            
            if len(self.warnings) > 0:
                print(f"⚠️  {len(self.warnings)} WARNINGS:")
                for warning in self.warnings:
                    print(f"   - {warning}")
            
            return len(self.errors) == 0  # Pass if no errors (warnings OK)
    
    def check_placeholders(self) -> int:
        """Check for placeholder patterns (Constraint 12)"""
        placeholder_patterns = [
            "Clinical scenario for",
            "Question stem about",
            "Question about",
            "Option A",
            "Option B",
            "Explanation for",
            "Explanation based on",
            "[Continue with",
            "[detailed explanation"
        ]
        
        issues = 0
        for mcq in self.data['mcqs']:
            mcq_id = mcq['id']
            
            # Check scenario
            scenario = mcq.get('question', {}).get('scenario', '')
            stem = mcq.get('question', {}).get('stem', '')
            options = json.dumps(mcq.get('question', {}).get('options', {}))
            explanation = mcq.get('explanation', '')
            
            full_text = f"{scenario} {stem} {options} {explanation}"
            
            for pattern in placeholder_patterns:
                if pattern in full_text:
                    print(f"   ❌ {mcq_id}: Placeholder detected: '{pattern}'")
                    issues += 1
                    break
        
        return issues
    
    def check_australian_spelling(self) -> int:
        """Check Australian vs American spelling (Constraint 1)"""
        # Common American spellings that should be Australian
        american_patterns = [
            (r'\bpediatric\b', 'pediatric → paediatric'),
            (r'\banesthesia\b', 'anesthesia → anaesthesia'),
            (r'\besophag', 'esophag → oesophag'),
            (r'\bhemoglobin\b', 'hemoglobin → haemoglobin'),
            (r'\banemia\b', 'anemia → anaemia'),
            (r'\bestrogen\b', 'estrogen → oestrogen'),
            (r'\bfavor\b', 'favor → favour'),
            (r'\bcolor\b', 'color → colour'),
        ]
        
        issues = 0
        for mcq in self.data['mcqs']:
            mcq_id = mcq['id']
            full_text = json.dumps(mcq).lower()
            
            for pattern, desc in american_patterns:
                if re.search(pattern, full_text):
                    print(f"   ❌ {mcq_id}: American spelling: {desc}")
                    issues += 1
        
        return issues
    
    def check_australian_drugs(self) -> int:
        """Check Australian vs American drug names (Constraint 1)"""
        # American drug names that should be Australian
        american_drugs = [
            ('acetaminophen', 'paracetamol'),
            ('albuterol', 'salbutamol'),
            ('epinephrine', 'adrenaline'),
            ('norepinephrine', 'noradrenaline'),
        ]
        
        issues = 0
        for mcq in self.data['mcqs']:
            mcq_id = mcq['id']
            full_text = json.dumps(mcq).lower()
            
            for american, australian in american_drugs:
                if american in full_text:
                    print(f"   ❌ {mcq_id}: American drug name: {american} → use {australian}")
                    issues += 1
        
        return issues
    
    def check_citations(self) -> int:
        """Check citations preserved (3 per MCQ, >0.70 confidence)"""
        issues = 0
        for mcq in self.data['mcqs']:
            mcq_id = mcq['id']
            refs = mcq.get('references', [])
            
            # Check count
            if len(refs) != 3:
                print(f"   ❌ {mcq_id}: Expected 3 citations, found {len(refs)}")
                issues += 1
                continue
            
            # Check confidence
            for i, ref in enumerate(refs):
                confidence = ref.get('rag_confidence', 0)
                if confidence < 0.70:
                    print(f"   ❌ {mcq_id}: Citation {i+1} confidence too low: {confidence:.2f}")
                    issues += 1
        
        return issues
    
    def check_content_substance(self) -> int:
        """Check content has substance (not minimal)"""
        issues = 0
        for mcq in self.data['mcqs']:
            mcq_id = mcq['id']
            
            scenario = mcq.get('question', {}).get('scenario', '')
            explanation = mcq.get('explanation', '')
            
            # Check minimum length
            if len(scenario) < 100:
                print(f"   ⚠️  {mcq_id}: Short scenario ({len(scenario)} chars, expect ≥100)")
                issues += 1
            
            if len(explanation) < 200:
                print(f"   ⚠️  {mcq_id}: Short explanation ({len(explanation)} chars, expect ≥200)")
                issues += 1
        
        return issues
    
    def check_demographics(self) -> int:
        """Check patient demographics present"""
        issues = 0
        demographic_markers = [
            r'\d+-year-old',  # "58-year-old"
            r'\byear old\b',  # "year old"
            r'\baged \d+\b',  # "aged 58"
        ]
        
        for mcq in self.data['mcqs']:
            mcq_id = mcq['id']
            scenario = mcq.get('question', {}).get('scenario', '').lower()
            
            has_demographics = any(re.search(pattern, scenario) for pattern in demographic_markers)
            
            if not has_demographics:
                print(f"   ⚠️  {mcq_id}: No patient demographics found in scenario")
                issues += 1
        
        return issues


def main():
    """Entry point"""
    if len(sys.argv) < 2:
        print("Usage: python validate_regenerated_mcqs.py <mcq_file.json>")
        print("Example: python validate_regenerated_mcqs.py data/mcqs/week3_cardiology_200_mcqs.json")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    validator = MCQValidator(file_path)
    validator.load_file()
    
    success = validator.validate_all()
    
    if success:
        print("\n✅ VALIDATION PASSED - MCQs meet all constraints")
        sys.exit(0)
    else:
        print("\n❌ VALIDATION FAILED - Fix errors before committing")
        sys.exit(1)


if __name__ == '__main__':
    main()
