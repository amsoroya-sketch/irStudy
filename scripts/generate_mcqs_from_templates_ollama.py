#!/usr/bin/env python3
"""
Generate Real Clinical MCQs from Templates using Local Ollama
Uses deepseek-r1:7b for medical reasoning and MCQ generation
Converts placeholder templates into full clinical scenarios with RAG citations
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.models.ollama_client import OllamaClient


class MCQGenerator:
    """Generate real clinical MCQs from templates using local Ollama"""

    def __init__(self):
        print("\n" + "=" * 80)
        print("🏥 MCQ GENERATOR - Local Ollama (deepseek-r1:7b)")
        print("=" * 80)
        print("Converting templates → real clinical scenarios")
        print("=" * 80 + "\n")

        # Initialize Ollama client
        self.ollama = OllamaClient()
        self.model = "deepseek-r1:7b"  # Best for medical reasoning

        print(f"✅ Using model: {self.model}")
        print(f"   Temperature: 0.7 (creative but controlled)")
        print()

    def create_mcq_prompt(self, template: Dict, citations: List[Dict]) -> str:
        """Create prompt for MCQ generation with RAG citations"""

        topic = template["topic"]
        specialty = template["specialty"]

        # Format citations for prompt
        citation_text = "\n\n".join(
            [
                f"Source {i+1}: {c['title']} ({c['author']}, {c['year']}, p.{c['page']})\n{c['content'][:500]}..."
                for i, c in enumerate(citations[:3])
            ]
        )

        prompt = f"""You are a medical educator creating Australian AMC Part 1 exam MCQs.

**Topic:** {topic}
**Specialty:** {specialty}

**Reference Sources:**
{citation_text}

**Task:** Create a realistic clinical MCQ based on Australian medical guidelines.

**Requirements:**
1. Create a clinical scenario (2-3 sentences) with patient demographics, symptoms, examination findings
2. Write a clear question stem asking for diagnosis, next step, or management
3. Provide 4 options (A, B, C, D) with ONE clearly correct answer
4. Include brief explanation referencing the sources above
5. Use Australian terminology (e.g., "paracetamol" not "acetaminophen", "GP" not "PCP")

**Output Format (JSON):**
{{
  "scenario": "A 45-year-old male presents to ED with...",
  "question_stem": "What is the most appropriate immediate management?",
  "options": {{
    "A": "Option A text",
    "B": "Option B text (CORRECT)",
    "C": "Option C text",
    "D": "Option D text"
  }},
  "correct_answer": "B",
  "explanation": "Brief explanation citing sources..."
}}

Generate the MCQ now:"""

        return prompt

    def generate_mcq(self, template: Dict) -> Dict:
        """Generate real clinical MCQ from template"""

        mcq_id = template["id"]
        citations = template.get("references", [])

        print(f"  Generating: {mcq_id} - {template['topic']}...", end=" ", flush=True)

        # Create prompt
        prompt = self.create_mcq_prompt(template, citations)

        # Generate with Ollama
        try:
            response = self.ollama.generate(prompt=prompt, model_name=self.model, temperature=0.7)

            # Try to extract JSON from response
            # Sometimes model wraps JSON in ```json ... ```
            json_start = response.find("{")
            json_end = response.rfind("}") + 1

            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                generated = json.loads(json_str)

                # Update template with generated content
                template["question"]["scenario"] = generated.get(
                    "scenario", template["question"].get("scenario", "")
                )
                template["question"]["stem"] = generated.get("question_stem", "")
                template["question"]["options"] = generated.get("options", {})
                template["correct_answer"] = generated.get("correct_answer", "B")
                template["explanation"] = generated.get(
                    "explanation", template.get("explanation", "")
                )

                print("✅")
                return template

            else:
                print("⚠️  (JSON parse failed, keeping template)")
                return template

        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return template

    def process_templates(
        self, input_file: str, output_file: str, limit: int = None
    ) -> Dict[str, int]:
        """Process all templates in file"""

        print(f"📖 Loading templates from: {input_file}")
        with open(input_file, "r") as f:
            data = json.load(f)

        templates = data.get("mcqs", [])
        total = len(templates)

        if limit:
            templates = templates[:limit]
            print(f"   Processing first {limit} of {total} templates\n")
        else:
            print(f"   Found {total} templates\n")

        stats = {"total": len(templates), "generated": 0, "failed": 0}

        # Generate MCQs
        for i, template in enumerate(templates, 1):
            print(f"[{i}/{len(templates)}]", end=" ")

            # Skip if already generated (not a placeholder)
            if "?" not in template["question"]["stem"]:
                print(f"  ✅ {template['id']} - Already has content, skipping")
                stats["generated"] += 1
                continue

            # Generate
            updated = self.generate_mcq(template)

            # Check if successful
            if "?" not in updated["question"]["stem"]:
                stats["generated"] += 1
            else:
                stats["failed"] += 1

            templates[i - 1] = updated

        # Save results
        data["mcqs"] = templates
        data["metadata"]["generation_complete"] = stats["generated"] == stats["total"]
        data["metadata"]["llm_model"] = self.model

        print(f"\n💾 Saving to: {output_file}")
        with open(output_file, "w") as f:
            json.dump(data, f, indent=2)

        print(f"\n{'='*80}")
        print("GENERATION COMPLETE")
        print(f"{'='*80}")
        print(f"Total templates: {stats['total']}")
        print(f"Generated: {stats['generated']} ({stats['generated']/stats['total']*100:.1f}%)")
        print(f"Failed: {stats['failed']}")
        print(f"{'='*80}\n")

        return stats


def main():
    """Generate real MCQs from templates"""

    generator = MCQGenerator()

    # Configuration
    input_file = "data/mcqs/missing_topics_comprehensive_mcqs.json"
    output_file = "data/mcqs/missing_topics_comprehensive_mcqs_GENERATED.json"

    # For testing, start with just 10 MCQs
    # Remove limit=10 to process all 658 templates
    stats = generator.process_templates(input_file, output_file, limit=10)

    print(f"✅ Done! Generated MCQs saved to: {output_file}")
    print(f"   To process all 658 templates, remove 'limit=10' from script")


if __name__ == "__main__":
    main()
