#!/usr/bin/env python3
"""
Test Day 1 RAG Integration - Proof of Concept
Generate 5 STEMI MCQs to verify RAG system works before full Day 1 execution

Test Criteria (from CRITICAL_GAPS_RESOLUTION.md):
1. Run Day 1 script with first topic (STEMI)
2. Generate 3-5 MCQs as proof-of-concept
3. Validate output structure
4. Confirm no placeholder patterns

Expected Results:
- RAG returns 3 citations per MCQ with confidence >0.70
- LLM generates complete MCQs (no placeholders)
- All validation checks pass
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

# Import dependencies
try:
    from rag.qdrant_client import QdrantClient
    from llm.ollama_client import OllamaClient
    from agents.medical.med_001_cardiology import CardiologyExpert
except ImportError as e:
    print(f"ERROR: Failed to import dependencies: {e}")
    sys.exit(1)

# Configuration
TEST_COUNT = 5
OUTPUT_FILE = "data-jan-26/test/test_rag_integration_5_mcqs.json"
LOG_FILE = "data-jan-26/test/test_rag_integration.log"

# STEMI topic configuration
TOPIC = {
    "name": "STEMI",
    "count": TEST_COUNT,
    "keywords": ["STEMI", "ST elevation", "myocardial infarction", "troponin", "ECG"]
}

# Validation constraints
CITATIONS_REQUIRED = 3
RAG_CONFIDENCE_MIN = 0.70
PLACEHOLDER_PATTERNS = [
    "Clinical scenario for",
    "Question about",
    "Option A",
    "Option B",
    "Explanation for",
    "Explanation based on Australian guidelines for"
]


class TestRAGIntegration:
    """Test RAG integration with 5 MCQ proof-of-concept"""

    def __init__(self):
        # Create output directories
        Path(OUTPUT_FILE).parent.mkdir(parents=True, exist_ok=True)
        Path(LOG_FILE).parent.mkdir(parents=True, exist_ok=True)

        self.log_file = open(LOG_FILE, 'w', encoding='utf-8')
        self.mcqs = []
        self.test_results = {
            "rag_operational": False,
            "llm_operational": False,
            "citations_valid": [],
            "mcqs_generated": 0,
            "validation_passed": 0,
            "placeholder_detected": 0
        }

    def log(self, message):
        """Log to console and file"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        self.log_file.write(log_msg + "\n")
        self.log_file.flush()

    def test_rag_system(self):
        """Test 1: Verify RAG system operational"""
        self.log("\n" + "="*60)
        self.log("TEST 1: RAG System Operational Check")
        self.log("="*60)

        try:
            self.qdrant = QdrantClient(host="localhost", port=6333)

            # Test query
            query_text = " ".join(TOPIC["keywords"][:3])
            self.log(f"Test query: '{query_text}'")

            results = self.qdrant.search(
                collection_name="medical_knowledge",
                query_text=query_text,
                limit=5
            )

            if not results:
                self.log("❌ FAILED: RAG returned 0 results")
                return False

            self.log(f"✓ RAG returned {len(results)} results")

            # Check confidence scores
            for i, result in enumerate(results[:3], 1):
                self.log(f"  Result {i}: score={result.score:.4f}, source={result.payload.get('source', 'Unknown')}")
                if result.score >= RAG_CONFIDENCE_MIN:
                    self.test_results["citations_valid"].append(result.score)

            if len(self.test_results["citations_valid"]) >= CITATIONS_REQUIRED:
                self.log(f"✓ Found {len(self.test_results['citations_valid'])} citations with confidence >{RAG_CONFIDENCE_MIN}")
                self.test_results["rag_operational"] = True
                return True
            else:
                self.log(f"❌ FAILED: Only {len(self.test_results['citations_valid'])} citations above threshold")
                return False

        except Exception as e:
            self.log(f"❌ FAILED: RAG error: {e}")
            import traceback
            traceback.print_exc()
            return False

    def test_llm_system(self):
        """Test 2: Verify LLM system operational"""
        self.log("\n" + "="*60)
        self.log("TEST 2: LLM System Operational Check")
        self.log("="*60)

        try:
            self.llm = OllamaClient(model="qwen2.5:7b")

            # Simple test prompt
            test_prompt = "Generate a single word: 'OPERATIONAL'"
            response = self.llm.generate(test_prompt, max_tokens=10)

            if response and len(response) > 0:
                self.log(f"✓ LLM responded: '{response[:50]}...'")
                self.test_results["llm_operational"] = True
                return True
            else:
                self.log("❌ FAILED: LLM returned empty response")
                return False

        except Exception as e:
            self.log(f"❌ FAILED: LLM error: {e}")
            import traceback
            traceback.print_exc()
            return False

    def generate_single_mcq(self, mcq_number):
        """Test 3: Generate a single MCQ with RAG citations"""
        self.log(f"\n{'='*60}")
        self.log(f"TEST 3.{mcq_number}: Generate MCQ {mcq_number}/{TEST_COUNT}")
        self.log(f"{'='*60}")

        try:
            # Step 1: Fetch RAG citations
            self.log("Step 1: Fetching RAG citations...")
            query_text = " ".join(TOPIC["keywords"][:3])
            results = self.qdrant.search(
                collection_name="medical_knowledge",
                query_text=query_text,
                limit=5
            )

            valid_citations = [r for r in results if r.score >= RAG_CONFIDENCE_MIN]
            if len(valid_citations) < CITATIONS_REQUIRED:
                self.log(f"❌ FAILED: Only found {len(valid_citations)} citations")
                return None

            citations = [
                {
                    "source": c.payload.get("source", "Unknown"),
                    "title": c.payload.get("title", ""),
                    "content": c.payload.get("content", ""),
                    "page": c.payload.get("page", ""),
                    "rag_confidence": c.score
                }
                for c in valid_citations[:CITATIONS_REQUIRED]
            ]

            avg_confidence = sum(c["rag_confidence"] for c in citations) / len(citations)
            self.log(f"✓ Fetched {len(citations)} citations (avg confidence: {avg_confidence:.4f})")

            # Step 2: Generate MCQ with LLM
            self.log("Step 2: Generating MCQ with LLM...")

            citation_text = "\n\n".join([
                f"Citation {i+1} ({c['source']}):\n{c['content'][:500]}"
                for i, c in enumerate(citations)
            ])

            llm_prompt = f"""Generate a clinical MCQ for AMC exam preparation about {TOPIC['name']}.

MEDICAL KNOWLEDGE CONTEXT (from Australian guidelines):
{citation_text}

REQUIREMENTS:
1. Create a realistic clinical scenario with:
   - Patient age and gender (specific, not generic)
   - Vital signs (HR, BP, SpO2, temp)
   - Presenting complaint
   - Relevant history
   - Clinical findings

2. Write a specific question stem (NOT "Question about...")

3. Provide 4 detailed options (A, B, C, D) with:
   - One clearly correct answer
   - Three plausible distractors
   - Each option should be a complete clinical decision/diagnosis/management step

4. Write a comprehensive explanation with:
   - why_correct: Why the correct option is right (reference Australian guidelines)
   - why_incorrect: Why each incorrect option is wrong
   - key_points: 5-7 bullet points for AMC exam
   - australian_context: Mention eTG/RANZCP/AMH/PBS/Medicare where relevant

5. Write a summary (50-200 characters) capturing the key learning point

6. Use Australian English spelling (favour, programme, etc.)

7. For STEMI topics, include relevant:
   - ECG findings (ST elevation in which leads)
   - Biomarker values (troponin, CK-MB)
   - Time to reperfusion targets
   - Management algorithms per eTG Cardiovascular

OUTPUT FORMAT (JSON):
{{
    "scenario": "A 62-year-old man presents to ED with...",
    "stem": "What is the most appropriate immediate management?",
    "options": {{
        "A": "Detailed option A",
        "B": "Detailed option B",
        "C": "Detailed option C",
        "D": "Detailed option D"
    }},
    "correct_option": "A",
    "explanation": {{
        "why_correct": "Option A is correct because...",
        "why_incorrect": "Options B, C, D are incorrect because...",
        "key_points": [
            "Point 1",
            "Point 2",
            "Point 3",
            "Point 4",
            "Point 5"
        ],
        "australian_context": "Per eTG Cardiovascular..."
    }},
    "summary": "Key learning point in 50-200 chars"
}}

Generate the MCQ now:
"""

            response = self.llm.generate(llm_prompt, max_tokens=1500)

            # Parse JSON response
            try:
                mcq_data = json.loads(response)
            except json.JSONDecodeError:
                # Try to extract JSON from response
                import re
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    mcq_data = json.loads(json_match.group())
                else:
                    self.log(f"❌ FAILED: Could not parse JSON from LLM response")
                    return None

            # Add metadata and references
            mcq_data['id'] = mcq_number
            mcq_data['metadata'] = {
                "specialty": "Cardiology",
                "topic": TOPIC['name'],
                "agent_id": "MED-001",
                "difficulty": "Medium",
                "date_generated": datetime.now().isoformat()
            }
            mcq_data['references'] = citations

            self.log("✓ LLM generated MCQ successfully")

            # Step 3: Validate MCQ
            self.log("Step 3: Validating MCQ...")
            valid, errors = self.validate_mcq(mcq_data)

            if valid:
                self.log("✓ MCQ validation PASSED")
                self.test_results["validation_passed"] += 1
                self.test_results["mcqs_generated"] += 1
                return mcq_data
            else:
                self.log("❌ MCQ validation FAILED:")
                for error in errors:
                    self.log(f"   - {error}")
                return None

        except Exception as e:
            self.log(f"❌ FAILED: MCQ generation error: {e}")
            import traceback
            traceback.print_exc()
            return None

    def validate_mcq(self, mcq):
        """Validate MCQ structure and content"""
        errors = []

        # Check placeholder patterns
        full_text = json.dumps(mcq)
        for pattern in PLACEHOLDER_PATTERNS:
            if pattern in full_text:
                errors.append(f"Placeholder pattern detected: '{pattern}'")
                self.test_results["placeholder_detected"] += 1

        # Check patient demographics
        scenario = mcq.get('scenario', '')
        has_age = any(word in scenario for word in ["year-old", "yo ", "aged"])
        has_gender = any(word in scenario for word in ["man", "woman", "male", "female"])
        if not (has_age and has_gender):
            errors.append("Missing patient demographics (age and/or gender)")

        # Check summary
        summary = mcq.get('summary', '')
        if not summary or len(summary) < 50 or len(summary) > 200:
            errors.append(f"Summary length invalid (must be 50-200 chars, got {len(summary)})")

        # Check references
        references = mcq.get('references', [])
        if len(references) != CITATIONS_REQUIRED:
            errors.append(f"Must have exactly {CITATIONS_REQUIRED} references, got {len(references)}")

        # Check Australian context
        full_text_lower = full_text.lower()
        has_australian_marker = any(marker in full_text_lower for marker in ["etg", "ranzcp", "amh", "pbs", "medicare", "therapeutic guidelines"])
        if not has_australian_marker:
            errors.append("Missing Australian context markers (eTG/RANZCP/AMH/PBS/Medicare)")

        return len(errors) == 0, errors

    def run_test(self):
        """Run complete test suite"""
        self.log("\n" + "="*60)
        self.log("DAY 1 RAG INTEGRATION TEST - PROOF OF CONCEPT")
        self.log(f"Target: Generate {TEST_COUNT} STEMI MCQs")
        self.log("="*60)

        # Test 1: RAG operational
        if not self.test_rag_system():
            self.log("\n❌ CRITICAL: RAG system not operational. Aborting test.")
            return False

        # Test 2: LLM operational
        if not self.test_llm_system():
            self.log("\n❌ CRITICAL: LLM system not operational. Aborting test.")
            return False

        # Test 3: Generate MCQs
        self.log("\n" + "="*60)
        self.log("TEST 3: MCQ Generation")
        self.log("="*60)

        for i in range(1, TEST_COUNT + 1):
            mcq = self.generate_single_mcq(i)
            if mcq:
                self.mcqs.append(mcq)

        # Save results
        self.save_results()

        # Final report
        self.print_final_report()

        # Return success if all tests passed
        return (
            self.test_results["rag_operational"] and
            self.test_results["llm_operational"] and
            self.test_results["mcqs_generated"] >= 3 and
            self.test_results["placeholder_detected"] == 0
        )

    def save_results(self):
        """Save MCQs to output file"""
        output_path = Path(OUTPUT_FILE)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.mcqs, f, indent=2, ensure_ascii=False)

        self.log(f"\n✓ Saved {len(self.mcqs)} MCQs to {OUTPUT_FILE}")

    def print_final_report(self):
        """Print final test report"""
        self.log("\n" + "="*60)
        self.log("FINAL TEST REPORT")
        self.log("="*60)
        self.log(f"RAG Operational:        {'✓ PASS' if self.test_results['rag_operational'] else '❌ FAIL'}")
        self.log(f"LLM Operational:        {'✓ PASS' if self.test_results['llm_operational'] else '❌ FAIL'}")
        self.log(f"MCQs Generated:         {self.test_results['mcqs_generated']}/{TEST_COUNT}")
        self.log(f"Validation Passed:      {self.test_results['validation_passed']}/{self.test_results['mcqs_generated']}")
        self.log(f"Placeholder Patterns:   {self.test_results['placeholder_detected']} (MUST be 0)")
        self.log(f"Avg RAG Confidence:     {sum(self.test_results['citations_valid'])/len(self.test_results['citations_valid']):.4f}" if self.test_results['citations_valid'] else "N/A")
        self.log("")
        self.log(f"Output File:            {OUTPUT_FILE}")
        self.log(f"Log File:               {LOG_FILE}")
        self.log("="*60)

        # Success criteria
        success = (
            self.test_results["rag_operational"] and
            self.test_results["llm_operational"] and
            self.test_results["mcqs_generated"] >= 3 and
            self.test_results["placeholder_detected"] == 0
        )

        if success:
            self.log("\n✓✓✓ TEST PASSED ✓✓✓")
            self.log("RAG integration is working. Ready for Day 1 full execution (145 MCQs).")
        else:
            self.log("\n❌❌❌ TEST FAILED ❌❌❌")
            self.log("Fix issues before proceeding with Day 1 full execution.")

    def __del__(self):
        """Cleanup"""
        if hasattr(self, 'log_file'):
            self.log_file.close()


def main():
    """Main entry point"""
    tester = TestRAGIntegration()
    success = tester.run_test()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
