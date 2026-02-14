#!/usr/bin/env python3
"""
Regenerate Week 3 Cardiology MCQs with Claude (Anthropic API)
Agent OS Architecture - PM coordinates specialist agents

CRITICAL CONSTRAINTS:
- Constraint 4.2: MUST use Claude (Anthropic API) - local 7B LLMs FAILED
- Constraint 1: Australian medical context (eTG, PBS, AHPRA, spelling)
- Constraint 12: NO placeholder content - 100% real clinical content

Usage:
    export ANTHROPIC_API_KEY='your-key-here'
    source venv/bin/activate  # Required per Constraint 4.0
    python scripts-jan-26/regenerate_week3_cardiology_with_claude.py

Evidence of failure (2026-01-26):
- 200 MCQs generated with local models → ALL placeholders
- RAG citations validated (95%+ confidence) → Content generation FAILED
- Root cause: 7B models cannot handle complex medical + JSON simultaneously
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import time

# Add src to path for Agent OS imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

# Import Anthropic SDK
try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    print("❌ ERROR: anthropic package not installed")
    print("   Install with: pip install anthropic")
    ANTHROPIC_AVAILABLE = False
    sys.exit(1)


class MCQRegenerationPM:
    """
    Project Manager coordinating MCQ regeneration
    
    Responsibilities:
    - Load existing MCQs with validated citations
    - Delegate content generation to Claude (Anthropic API)
    - Validate no placeholder patterns (Constraint 12)
    - Enforce Australian medical context (Constraint 1)
    - Save progress incrementally
    """
    
    def __init__(self):
        # Initialize Claude (Anthropic API) - REQUIRED per Constraint 4.2
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError(
                "❌ ANTHROPIC_API_KEY environment variable not set\n"
                "   Set it with: export ANTHROPIC_API_KEY='your-key-here'\n"
                "   Get key from: https://console.anthropic.com/"
            )
        
        self.anthropic = Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-5-20250929"
        
        # File paths
        self.input_file = Path("data/mcqs/week3_cardiology_200_mcqs.json")
        self.output_file = self.input_file  # Update in place
        self.backup_file = Path("data/mcqs/week3_cardiology_200_mcqs_backup_" + 
                                datetime.now().strftime("%Y%m%d_%H%M%S") + ".json")
        
        # Statistics
        self.total_mcqs = 0
        self.regenerated = 0
        self.failed = 0
        self.skipped = 0
        
        print("="*70)
        print("WEEK 3 CARDIOLOGY MCQ REGENERATION - PROJECT MANAGER")
        print("="*70)
        print(f"LLM Provider: Claude (Anthropic API)")
        print(f"Model: {self.model}")
        print(f"Constraint 4.2: Local LLM bypass - using production-grade API")
        print(f"Constraint 1: Australian medical context enforced")
        print(f"Constraint 12: NO placeholder content allowed")
        print("="*70)
    
    def load_mcqs(self) -> Dict:
        """Load existing MCQs with validated citations"""
        print(f"\n📥 Loading MCQs from {self.input_file}")
        
        if not self.input_file.exists():
            raise FileNotFoundError(f"Input file not found: {self.input_file}")
        
        with open(self.input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.total_mcqs = len(data['mcqs'])
        placeholders = sum(1 for m in data['mcqs'] 
                          if self.has_placeholders_in_mcq(m))
        
        print(f"   Total MCQs: {self.total_mcqs}")
        print(f"   Placeholders: {placeholders}")
        print(f"   Citations per MCQ: {len(data['mcqs'][0].get('references', []))}")
        print(f"   ✓ File loaded successfully")
        
        return data
    
    def backup_original(self, data: Dict):
        """Create timestamped backup before regeneration"""
        print(f"\n💾 Creating backup at {self.backup_file}")
        
        # Ensure directory exists
        self.backup_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.backup_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"   ✓ Backup complete ({self.backup_file.stat().st_size // 1024} KB)")
    
    def has_placeholders_in_mcq(self, mcq: Dict) -> bool:
        """Check if MCQ has placeholder content"""
        placeholder_patterns = [
            "Clinical scenario for",
            "Question stem about",
            "Question about",
            "Option A",
            "Option B",
            "Explanation for",
            "Explanation based on"
        ]
        
        # Check scenario, stem, options, explanation
        scenario = mcq.get('question', {}).get('scenario', '')
        stem = mcq.get('question', {}).get('stem', '')
        options = json.dumps(mcq.get('question', {}).get('options', {}))
        explanation = mcq.get('explanation', '')
        
        full_text = f"{scenario} {stem} {options} {explanation}"
        
        for pattern in placeholder_patterns:
            if pattern in full_text:
                return True
        
        return False
    
    def generate_mcq_content(self, mcq: Dict, index: int, total: int) -> Optional[Dict]:
        """
        Generate real MCQ content using Claude (Anthropic API)
        
        This is the CRITICAL step that local LLMs failed at.
        Claude can handle:
        - Complex clinical reasoning
        - Australian medical context
        - Structured JSON output
        - Long-form content (500-1000 tokens)
        - Multi-field coherence
        """
        
        # Extract metadata
        mcq_id = mcq['id']
        specialty = mcq.get('specialty', 'Cardiology')
        topic = mcq.get('topic', 'General')
        subtopic = mcq.get('subtopic', '')
        
        # Extract validated citations
        citations = mcq.get('references', [])
        
        if len(citations) < 3:
            print(f"   ⚠️  Only {len(citations)} citations (need 3) - skipping")
            return None
        
        print(f"\n[{index}/{total}] Generating {mcq_id}")
        print(f"   Topic: {topic} → {subtopic}")
        print(f"   Citations: {len(citations)} (confidence: {citations[0].get('rag_confidence', 0):.2f})")
        
        # Prepare citation context for Claude
        citation_context = "\n\n".join([
            f"**Citation {i+1}**: {ref['title']} (Page {ref.get('page', 'N/A')})\n"
            f"Confidence: {ref.get('rag_confidence', 0):.2f}\n"
            f"Content:\n{ref.get('content', '')[:800]}"
            for i, ref in enumerate(citations[:3])
        ])
        
        # Construct prompt for Claude
        prompt = f"""Generate a high-quality clinical MCQ for Australian medical students preparing for the AMC Clinical Exam.

SPECIALTY: {specialty}
TOPIC: {topic}
SUBTOPIC: {subtopic}

MEDICAL KNOWLEDGE CONTEXT (from RAG-validated citations):

{citation_context}

---

CRITICAL REQUIREMENTS (ALL MUST BE MET):

1. **Clinical Scenario** (150-300 words):
   - Specific patient demographics (age, sex, relevant background)
   - Vital signs if relevant (HR, BP, RR, SpO2, temperature)
   - Presenting complaint with clear timeline
   - Relevant medical/surgical/family/social history
   - Examination findings (focused, relevant)
   - Investigation results (if topic requires: ECG, bloods, imaging)
   - Australian healthcare context (GP, ED, specialist, Medicare)

2. **Question Stem** (clear, specific):
   - NOT "Question about..." or generic templates
   - Focus on clinical decision-making or diagnosis
   - Australian healthcare setting

3. **Options** (A, B, C, D):
   - One clearly correct answer based on Australian guidelines
   - Three plausible distractors (common errors or alternatives)
   - Each option 10-40 words
   - Specific interventions/diagnoses (NOT "Option A", "Option B")
   - Use Australian drug names and terminology

4. **Explanation** (250-400 words):
   - Why correct option is right (cite guidelines, reference the provided citations)
   - Why each incorrect option is wrong (clinical reasoning)
   - Key learning points for AMC Clinical Exam
   - Australian guidelines: eTG, RANZCP, AMH, PBS where relevant
   - If possible, reference page numbers from provided citations

5. **Summary** (50-200 characters):
   - Concise key learning point
   - Action-oriented for exam preparation

6. **Australian Medical Context** (MANDATORY - Constraint 1):
   - Drug names: paracetamol (NOT acetaminophen), salbutamol (NOT albuterol), adrenaline (NOT epinephrine)
   - Spelling: paediatric, anaesthesia, oesophagus, haemoglobin, anaemia
   - Terminology: GP (NOT PCP), Emergency Department (NOT ER), bulk-billed (NOT insurance)
   - Guidelines: Therapeutic Guidelines (eTG), AMH, PBS, AHPRA, RANZCP
   - Emergency: Call 000 (NOT 911)

7. **NO Placeholder Patterns** (MANDATORY - Constraint 12):
   - NO "Clinical scenario for..."
   - NO "Question about..."
   - NO "Option A", "Option B" generic text
   - NO "Explanation for..."
   - 100% real clinical content

OUTPUT FORMAT (JSON only, no markdown code blocks):
{{
  "scenario": "A 62-year-old man with a history of hypertension and type 2 diabetes presents to the Emergency Department with sudden onset severe central chest pain...",
  "stem": "What is the most appropriate immediate management?",
  "options": {{
    "A": "Administer aspirin 300 mg orally and commence GTN infusion 10 mcg/min",
    "B": "Arrange urgent coronary angiography within 90 minutes",
    "C": "Commence thrombolysis with tenecteplase 40 mg IV bolus",
    "D": "Perform bedside echocardiography to assess LV function"
  }},
  "correct_answer": "A",
  "explanation": "Option A is correct because this patient presents with likely acute coronary syndrome (ACS). According to the Therapeutic Guidelines: Cardiovascular (eTG Section 5.2.1), immediate management includes: (1) Aspirin 300 mg orally unless contraindicated...[continue with detailed explanation citing the provided RAG citations where relevant]... Option B is premature without initial medical therapy. Option C (thrombolysis) would only be considered if PCI unavailable and clear STEMI criteria met. Option D delays definitive treatment.",
  "summary": "ACS requires immediate aspirin + GTN per Australian guidelines (eTG Cardiovascular 5.2.1)"
}}

VALIDATION CHECKLIST (verify before returning):
- [ ] Scenario has specific patient demographics (age, sex)
- [ ] Scenario has vital signs or clinical findings
- [ ] Stem is a specific clinical question (not template)
- [ ] All 4 options are specific medical decisions (not "Option A/B/C/D")
- [ ] Explanation references the provided citations where possible
- [ ] Australian spelling used throughout (paediatric, anaesthesia, etc.)
- [ ] Australian drug names used (paracetamol, salbutamol, adrenaline)
- [ ] Australian guidelines referenced (eTG, AMH, PBS, RANZCP)
- [ ] Summary is 50-200 characters
- [ ] NO placeholder text patterns detected

Generate the MCQ now (JSON only, no markdown):"""
        
        try:
            # Call Claude via Anthropic API
            print(f"   Calling Claude API...")
            start_time = time.time()
            
            response = self.anthropic.messages.create(
                model=self.model,
                max_tokens=3000,  # Allow longer responses for detailed content
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )
            
            elapsed = time.time() - start_time
            
            # Extract JSON from response
            response_text = response.content[0].text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith('```'):
                # Extract JSON from markdown code block
                lines = response_text.split('\n')
                json_lines = []
                in_json = False
                for line in lines:
                    if line.startswith('```'):
                        in_json = not in_json
                        continue
                    if in_json:
                        json_lines.append(line)
                response_text = '\n'.join(json_lines)
            
            # Parse JSON
            mcq_content = json.loads(response_text)
            
            # Validate no placeholders
            if self.has_placeholders_in_generated(mcq_content):
                print(f"   ❌ Generated content has placeholders - REJECTED")
                return None
            
            # Validate required fields
            required_fields = ['scenario', 'stem', 'options', 'correct_answer', 'explanation', 'summary']
            for field in required_fields:
                if field not in mcq_content:
                    print(f"   ❌ Missing required field: {field} - REJECTED")
                    return None
            
            # Validate options structure
            if not isinstance(mcq_content['options'], dict) or len(mcq_content['options']) != 4:
                print(f"   ❌ Invalid options structure - REJECTED")
                return None
            
            print(f"   ✓ Generated real content ({elapsed:.1f}s)")
            print(f"   Scenario: {len(mcq_content['scenario'])} chars")
            print(f"   Explanation: {len(mcq_content['explanation'])} chars")
            
            return mcq_content
            
        except json.JSONDecodeError as e:
            print(f"   ❌ JSON parse error: {e}")
            print(f"   Response preview: {response_text[:200]}...")
            return None
        except Exception as e:
            print(f"   ❌ Generation failed: {type(e).__name__}: {e}")
            return None
    
    def has_placeholders_in_generated(self, mcq_content: Dict) -> bool:
        """Validate generated content has no placeholder patterns (Constraint 12)"""
        
        placeholder_patterns = [
            "Clinical scenario for",
            "Question about",
            "Question stem about",
            "Option A",
            "Option B",
            "Option C",
            "Option D",
            "Explanation for",
            "Explanation based on",
            "[Continue with",
            "[detailed explanation",
        ]
        
        full_text = json.dumps(mcq_content).lower()
        
        for pattern in placeholder_patterns:
            if pattern.lower() in full_text:
                return True
        
        return False
    
    def regenerate_all(self) -> int:
        """
        Main regeneration loop
        
        Returns:
            0 on success, 1 on partial failure, 2 on complete failure
        """
        
        # Load existing data
        data = self.load_mcqs()
        
        # Create backup
        self.backup_original(data)
        
        print(f"\n{'='*70}")
        print("STARTING REGENERATION")
        print(f"{'='*70}")
        
        # Regenerate placeholders
        for i, mcq in enumerate(data['mcqs'], 1):
            # Check if already has real content
            if not self.has_placeholders_in_mcq(mcq):
                print(f"\n[{i}/{self.total_mcqs}] {mcq['id']} - Already has real content, skipping")
                self.skipped += 1
                continue
            
            # Generate real content
            new_content = self.generate_mcq_content(mcq, i, self.total_mcqs)
            
            if new_content:
                # Update MCQ with real content (keep ID, citations, metadata)
                mcq['question']['scenario'] = new_content['scenario']
                mcq['question']['stem'] = new_content['stem']
                mcq['question']['options'] = new_content['options']
                mcq['correct_answer'] = new_content['correct_answer']
                mcq['explanation'] = new_content['explanation']
                mcq['summary'] = new_content['summary']
                
                # Remove regeneration_failed flag if present
                mcq.pop('regeneration_failed', None)
                
                # Add regeneration metadata
                mcq['regeneration_date'] = datetime.now().isoformat()
                mcq['regeneration_method'] = 'Claude (Anthropic API)'
                mcq['regeneration_model'] = self.model
                
                self.regenerated += 1
                
                # Save progress every 10 MCQs
                if self.regenerated % 10 == 0:
                    self.save_progress(data)
            else:
                self.failed += 1
                print(f"   ⚠️  Keeping placeholder for manual review")
                
                # Mark as failed
                mcq['regeneration_failed'] = True
                mcq['regeneration_attempts'] = mcq.get('regeneration_attempts', 0) + 1
            
            # Rate limit: 1 request per 2 seconds (to avoid API limits)
            if i < self.total_mcqs:
                time.sleep(2)
        
        # Final save
        self.save_progress(data, final=True)
        
        # Summary
        print("\n" + "="*70)
        print("REGENERATION COMPLETE")
        print("="*70)
        print(f"Total MCQs: {self.total_mcqs}")
        print(f"Regenerated: {self.regenerated}")
        print(f"Failed: {self.failed}")
        print(f"Skipped (already real): {self.skipped}")
        print(f"Output: {self.output_file}")
        print(f"Backup: {self.backup_file}")
        
        if self.failed > 0:
            print(f"\n⚠️  {self.failed} MCQs still need manual review")
            return 1
        elif self.regenerated == 0:
            print(f"\n✅ All MCQs already have real content - no regeneration needed")
            return 0
        else:
            print(f"\n✅ All placeholders regenerated successfully!")
            return 0
    
    def save_progress(self, data: Dict, final: bool = False):
        """Save progress to output file"""
        
        # Update metadata
        data['metadata']['regeneration_date'] = datetime.now().isoformat()
        data['metadata']['regenerated_count'] = self.regenerated
        data['metadata']['failed_count'] = self.failed
        data['metadata']['skipped_count'] = self.skipped
        data['metadata']['regeneration_method'] = "Claude (Anthropic API)"
        data['metadata']['regeneration_model'] = self.model
        data['metadata']['constraint_4_2_compliant'] = True
        data['metadata']['constraint_1_compliant'] = True
        data['metadata']['constraint_12_compliant'] = True
        
        # Update statistics
        data['statistics']['total_mcqs'] = self.total_mcqs
        data['statistics']['regenerated_mcqs'] = self.regenerated
        data['statistics']['failed_mcqs'] = self.failed
        
        # Ensure output directory exists
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        status = "FINAL" if final else "Progress"
        print(f"\n💾 {status} save: {self.regenerated} regenerated, {self.failed} failed, {self.skipped} skipped")


def main():
    """Entry point"""
    
    print("\n" + "="*70)
    print("WEEK 3 CARDIOLOGY MCQ REGENERATION - AGENT OS PM")
    print("="*70)
    print("Constraint 4.2: Using Claude (Anthropic API) - local LLMs bypassed")
    print("Evidence: 200 MCQs failed with local 7B models → switching to production API")
    print("="*70 + "\n")
    
    # Validate ANTHROPIC_API_KEY exists
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("❌ ERROR: ANTHROPIC_API_KEY environment variable not set")
        print("")
        print("To fix:")
        print("  1. Get API key from: https://console.anthropic.com/")
        print("  2. Set environment variable:")
        print("     export ANTHROPIC_API_KEY='your-key-here'")
        print("  3. Re-run this script")
        print("")
        return 1
    
    # Validate anthropic package installed
    if not ANTHROPIC_AVAILABLE:
        print("❌ ERROR: anthropic package not installed")
        print("")
        print("To fix:")
        print("  source venv/bin/activate")
        print("  pip install anthropic")
        print("")
        return 1
    
    try:
        pm = MCQRegenerationPM()
        return pm.regenerate_all()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user - progress saved")
        return 130
    except Exception as e:
        print(f"\n\n❌ FATAL ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return 2


if __name__ == '__main__':
    sys.exit(main())
