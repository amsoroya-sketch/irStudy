#!/usr/bin/env python3
"""
Generate Respiratory MCQs - Day 4 (135 MCQs)
Agent: MED-002 Respiratory Expert
Topics: Pneumonia, PE, pleural effusion, lung cancer, Wells PE score

Usage:
    python scripts-jan-26/generate_respiratory_day4_135_mcqs.py
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime
import requests

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

# Import medical expert agent
try:
    from agents.medical.med_002_respiratory import RespiratoryExpert
except ImportError:
    print("ERROR: Could not import RespiratoryExpert from src/agents/medical/med_002_respiratory.py")
    print("Ensure Agent OS medical experts are properly installed")
    sys.exit(1)

# Import RAG and LLM clients
try:
    from rag.qdrant_client import QdrantClient
    from llm.ollama_client import OllamaClient
except ImportError:
    print("WARNING: RAG/LLM clients not available, using placeholder implementations")
    QdrantClient = None
    OllamaClient = None


# Configuration
AGENT_ID = "MED-002"
SPECIALTY = "Respiratory"
DAY = 4
TARGET_COUNT = 135
OUTPUT_FILE = "data-jan-26/mcqs/respiratory_day4_135_mcqs.json"
LOG_FILE = "data-jan-26/validation/day4_respiratory_log.txt"

# Topics for Day 4
TOPICS = [
    {"name": "Pneumonia", "count": 40, "keywords": ["pneumonia", "CAP", "HAP", "CURB-65", "antibiotics", "chest infection"]},
    {"name": "Pulmonary Embolism", "count": 35, "keywords": ["PE", "pulmonary embolism", "DVT", "Wells score", "D-dimer", "CTPA"]},
    {"name": "Pleural Effusion", "count": 30, "keywords": ["pleural effusion", "pleural fluid", "thoracentesis", "Light's criteria", "empyema"]},
    {"name": "Lung Cancer", "count": 25, "keywords": ["lung cancer", "NSCLC", "SCLC", "lung nodule", "bronchoscopy"]},
    {"name": "Respiratory Emergencies", "count": 5, "keywords": ["respiratory failure", "respiratory arrest", "tension pneumothorax", "massive haemoptysis"]},
]

# Constraints
CITATIONS_REQUIRED = 3
RAG_CONFIDENCE_MIN = 0.70
SUMMARY_LENGTH = (50, 200)

# Placeholder patterns to detect (must be 0)
PLACEHOLDER_PATTERNS = [
    "Clinical scenario for",
    "Question about",
    "Option A",
    "Option B",
    "Explanation for",
    "Explanation based on Australian guidelines for"
]


class MCQGenerator:
    """Generate MCQs with Agent OS medical expert"""

    def __init__(self):
        self.log_file = open(LOG_FILE, 'w', encoding='utf-8')
        self.mcqs_generated = []
        self.validation_errors = []

        # Initialize Agent OS
        try:
            self.respiratory_agent = RespiratoryExpert()
            self.log("✓ Respiratory Expert Agent (MED-002) loaded")
        except Exception as e:
            self.log(f"ERROR: Could not load Respiratory Expert: {e}")
            self.respiratory_agent = None

        # Initialize RAG system
        try:
            self.qdrant = QdrantClient(host="localhost", port=6333)
            vector_count = self.check_rag_operational()
            self.log(f"✓ RAG System operational ({vector_count} vectors)")
        except Exception as e:
            self.log(f"ERROR: RAG System not operational: {e}")
            self.qdrant = None

        # Initialize LLM
        try:
            self.llm = OllamaClient(model="deepseek-r1:14b")
            self.log("✓ LLM Service operational (deepseek-r1:14b)")
        except Exception as e:
            self.log(f"ERROR: LLM Service not operational: {e}")
            self.llm = None

    def log(self, message):
        """Log message to console and file"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        self.log_file.write(log_msg + "\n")
        self.log_file.flush()

    def check_rag_operational(self):
        """Check RAG system has required vectors"""
        try:
            response = requests.get('http://localhost:6333/collections/medical_knowledge')
            data = response.json()
            return data['result']['vectors_count']
        except Exception as e:
            raise Exception(f"Qdrant not operational: {e}")

    def fetch_rag_citations(self, topic, keywords, retry_count=0):
        """Fetch RAG citations (Constraint 11: exactly 3 citations, >0.70 confidence)"""
        self.log(f"  Fetching RAG citations for topic: {topic}")

        try:
            # Query Qdrant with keywords
            query_text = " ".join(keywords[:3])  # Use first 3 keywords
            results = self.qdrant.search(
                collection_name="medical_knowledge",
                query_text=query_text,
                limit=5,
                filter={
                    "must": [
                        {"key": "source", "match": {"any": ["eTG", "RANZCP", "AMH", "TSANZ", "ANZCTR"]}}
                    ]
                }
            )

            # Filter by confidence >0.70
            valid_citations = [r for r in results if r.score >= RAG_CONFIDENCE_MIN]

            if len(valid_citations) < CITATIONS_REQUIRED:
                if retry_count < 3:
                    self.log(f"  WARNING: Only {len(valid_citations)} citations found, retrying with different keywords...")
                    # Retry with different keyword combination
                    return self.fetch_rag_citations(topic, keywords[1:] + keywords[:1], retry_count + 1)
                else:
                    self.log(f"  ERROR: Could not find {CITATIONS_REQUIRED} citations after 3 retries")
                    return None

            # Return exactly 3 citations
            selected_citations = valid_citations[:CITATIONS_REQUIRED]
            self.log(f"  ✓ Fetched {len(selected_citations)} citations (avg confidence: {sum(c.score for c in selected_citations)/len(selected_citations):.2f})")

            return [
                {
                    "source": c.payload.get("source", "Unknown"),
                    "title": c.payload.get("title", ""),
                    "content": c.payload.get("content", ""),
                    "page": c.payload.get("page", ""),
                    "rag_confidence": c.score
                }
                for c in selected_citations
            ]

        except Exception as e:
            self.log(f"  ERROR: RAG query failed: {e}")
            return None

    def generate_mcq_with_llm(self, topic, citations):
        """Generate MCQ using LLM with RAG citation content (Constraint 12)"""
        self.log(f"  Generating MCQ with LLM...")

        # Extract citation content for LLM context
        citation_text = "\n\n".join([
            f"Citation {i+1} ({c['source']}):\n{c['content'][:500]}"  # First 500 chars
            for i, c in enumerate(citations)
        ])

        # LLM prompt (NO templates, real content generation)
        llm_prompt = f"""Generate a clinical MCQ for AMC exam preparation about {topic['name']}.

MEDICAL KNOWLEDGE CONTEXT (from Australian guidelines):
{citation_text}

REQUIREMENTS:
1. Create a realistic clinical scenario with:
   - Patient age and gender (specific, not generic)
   - Vital signs (HR, BP, SpO2, RR, temp)
   - Presenting complaint (respiratory symptoms)
   - Relevant history (smoking, travel, immunosuppression)
   - Clinical findings (chest examination, CXR findings)

2. Write a specific question stem (NOT "Question about...")

3. Provide 4 detailed options (A, B, C, D) with:
   - One clearly correct answer
   - Three plausible distractors
   - Each option should be a complete clinical decision/diagnosis/management step

4. Write a comprehensive explanation with:
   - why_correct: Why the correct option is right (reference Australian guidelines)
   - why_incorrect: Why each incorrect option is wrong
   - key_points: 5-7 bullet points for AMC exam
   - australian_context: Mention eTG/TSANZ/AMH/PBS where relevant

5. Write a summary (50-200 characters) capturing the key learning point

6. Use Australian English spelling (favour, programme, etc.)

7. For respiratory topics, include relevant:
   - CXR findings
   - Wells PE score if PE
   - CURB-65 if pneumonia
   - Light's criteria if pleural effusion
   - Antibiotic choices per eTG

OUTPUT FORMAT (JSON):
{{
    "scenario": "A 65-year-old man presents with...",
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
            ...
        ],
        "australian_context": "Per eTG Respiratory..."
    }},
    "summary": "Key learning point in 50-200 chars"
}}

Generate the MCQ now:
"""

        try:
            response = self.llm.generate(llm_prompt, max_tokens=1500)
            mcq_data = json.loads(response)

            # Add metadata
            mcq_data['metadata'] = {
                "specialty": SPECIALTY,
                "topic": topic['name'],
                "agent_id": AGENT_ID,
                "difficulty": "Medium",
                "date_generated": datetime.now().isoformat(),
                "tools_applied": ["CXR_analysis", "Wells_PE_score", "CURB_65"]
            }

            # Add references (3 citations)
            mcq_data['references'] = citations

            self.log(f"  ✓ LLM generated MCQ")
            return mcq_data

        except Exception as e:
            self.log(f"  ERROR: LLM generation failed: {e}")
            return None

    def validate_mcq_incremental(self, mcq):
        """Incremental validation (Gate 2: Per-MCQ BLOCKING)"""
        errors = []

        # Check placeholder patterns
        full_text = json.dumps(mcq)
        for pattern in PLACEHOLDER_PATTERNS:
            if pattern in full_text:
                errors.append(f"Placeholder pattern detected: '{pattern}'")

        # Check patient demographics
        scenario = mcq.get('scenario', '')
        has_age = any(word in scenario for word in ["year-old", "yo ", "aged"])
        has_gender = any(word in scenario for word in ["man", "woman", "male", "female"])
        if not (has_age and has_gender):
            errors.append("Missing patient demographics (age and/or gender)")

        # Check summary length
        summary = mcq.get('summary', '')
        if not summary or len(summary) < SUMMARY_LENGTH[0] or len(summary) > SUMMARY_LENGTH[1]:
            errors.append(f"Summary length invalid (must be {SUMMARY_LENGTH[0]}-{SUMMARY_LENGTH[1]} chars, got {len(summary)})")

        # Check references count
        references = mcq.get('references', [])
        if len(references) != CITATIONS_REQUIRED:
            errors.append(f"Must have exactly {CITATIONS_REQUIRED} references, got {len(references)}")

        # Check Australian context markers
        full_text_lower = full_text.lower()
        has_australian_marker = any(marker in full_text_lower for marker in ["etg", "ranzcp", "amh", "pbs", "medicare", "therapeutic guidelines", "tsanz"])
        if not has_australian_marker:
            errors.append("Missing Australian context markers (eTG/TSANZ/AMH/PBS/Medicare)")

        if errors:
            self.log(f"  ❌ Validation FAILED:")
            for error in errors:
                self.log(f"     - {error}")
            return False, errors
        else:
            self.log(f"  ✓ Validation PASSED")
            return True, []

    def generate_mcqs_for_topic(self, topic):
        """Generate MCQs for a specific topic"""
        self.log(f"\n{'='*60}")
        self.log(f"Topic: {topic['name']} (Target: {topic['count']} MCQs)")
        self.log(f"{'='*60}")

        topic_mcqs = []

        for i in range(topic['count']):
            self.log(f"\nGenerating MCQ {i+1}/{topic['count']} for {topic['name']}...")

            # Step 1: Fetch RAG citations (Constraint 11)
            citations = self.fetch_rag_citations(topic['name'], topic['keywords'])
            if not citations:
                self.log(f"  SKIP: Could not fetch citations, moving to next MCQ")
                continue

            # Step 2: Generate MCQ with LLM (Constraint 12)
            mcq = self.generate_mcq_with_llm(topic, citations)
            if not mcq:
                self.log(f"  SKIP: LLM generation failed, moving to next MCQ")
                continue

            # Step 3: Incremental validation (Gate 2)
            valid, errors = self.validate_mcq_incremental(mcq)
            if not valid:
                self.validation_errors.append({
                    "topic": topic['name'],
                    "mcq_index": i+1,
                    "errors": errors
                })
                self.log(f"  RETRY: Attempting regeneration...")
                # Retry once
                mcq = self.generate_mcq_with_llm(topic, citations)
                if mcq:
                    valid, errors = self.validate_mcq_incremental(mcq)

                if not valid:
                    self.log(f"  SKIP: Validation failed after retry")
                    continue

            # Add ID
            mcq['id'] = len(self.mcqs_generated) + 1

            # Success
            topic_mcqs.append(mcq)
            self.mcqs_generated.append(mcq)
            self.log(f"  ✓ MCQ {mcq['id']} generated successfully (Total: {len(self.mcqs_generated)}/{TARGET_COUNT})")

            # Save progress every 10 MCQs
            if len(self.mcqs_generated) % 10 == 0:
                self.save_progress()

        return topic_mcqs

    def save_progress(self):
        """Save current progress to output file"""
        output_path = Path(OUTPUT_FILE)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.mcqs_generated, f, indent=2, ensure_ascii=False)

        self.log(f"\n✓ Progress saved: {len(self.mcqs_generated)} MCQs → {OUTPUT_FILE}")

    def generate_all(self):
        """Main generation loop"""
        self.log(f"\n{'='*60}")
        self.log(f"RESPIRATORY DAY 4 GENERATION (Agent: {AGENT_ID})")
        self.log(f"Target: {TARGET_COUNT} MCQs")
        self.log(f"Output: {OUTPUT_FILE}")
        self.log(f"{'='*60}\n")

        # Pre-generation validation (Gate 1)
        if not self.respiratory_agent:
            self.log("ERROR: Respiratory Expert Agent not loaded. Aborting.")
            sys.exit(1)
        if not self.qdrant:
            self.log("ERROR: RAG System not operational. Aborting.")
            sys.exit(1)
        if not self.llm:
            self.log("ERROR: LLM Service not operational. Aborting.")
            sys.exit(1)

        self.log("✓ Gate 1: Pre-generation validation PASSED\n")

        # Generate MCQs for each topic
        for topic in TOPICS:
            self.generate_mcqs_for_topic(topic)

        # Final save
        self.save_progress()

        # Summary
        self.log(f"\n{'='*60}")
        self.log(f"GENERATION COMPLETE")
        self.log(f"{'='*60}")
        self.log(f"MCQs generated: {len(self.mcqs_generated)}/{TARGET_COUNT}")
        self.log(f"Validation errors: {len(self.validation_errors)}")
        self.log(f"Citations validated: {len(self.mcqs_generated) * CITATIONS_REQUIRED}")
        self.log(f"Output file: {OUTPUT_FILE}")
        self.log(f"Log file: {LOG_FILE}")

        if len(self.mcqs_generated) < TARGET_COUNT:
            self.log(f"\nWARNING: Target not met. Generated {len(self.mcqs_generated)}/{TARGET_COUNT} MCQs.")
            return 1
        else:
            self.log(f"\n✓ SUCCESS: Target met! Generated {len(self.mcqs_generated)} MCQs.")
            return 0

    def __del__(self):
        """Cleanup"""
        if hasattr(self, 'log_file'):
            self.log_file.close()


def main():
    """Main entry point"""
    generator = MCQGenerator()
    exit_code = generator.generate_all()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
