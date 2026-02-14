#!/usr/bin/env python3
"""
Generate Real Clinical MCQs from Templates using Local Ollama (Simple Version)
Direct API calls to Ollama without langchain dependencies
"""

import json
import requests
from pathlib import Path
from typing import Dict, List


class SimpleOllamaMCQGenerator:
    """Generate MCQs using Ollama HTTP API"""

    def __init__(self, model: str = "qwen2.5:7b", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        print(f"\n{'='*80}")
        print(f"🏥 MCQ GENERATOR - {model}")
        print(f"{'='*80}\n")

    def generate(self, prompt: str, temperature: float = 0.7) -> str:
        """Call Ollama API to generate text"""

        url = f"{self.base_url}/api/generate"
        payload = {"model": self.model, "prompt": prompt, "temperature": temperature, "stream": False}

        try:
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            return response.json()["response"]
        except Exception as e:
            print(f"   ❌ Ollama error: {e}")
            return ""

    def create_prompt(self, template: Dict, citations: List[Dict]) -> str:
        """Create MCQ generation prompt"""

        topic = template["topic"]
        specialty = template["specialty"]

        # Format first 3 citations
        citation_text = "\n\n".join(
            [
                f"Source {i+1}: {c['title']} ({c['author']}, {c['year']}, p.{c['page']})\n{c['content'][:300]}..."
                for i, c in enumerate(citations[:3])
            ]
        )

        return f"""You are creating an Australian AMC Part 1 exam MCQ.

Topic: {topic} ({specialty})

Reference Sources:
{citation_text}

Create a realistic clinical MCQ with:
1. Patient scenario (2-3 sentences)
2. Clear question stem
3. Four options (A-D) with ONE correct answer
4. Brief explanation

Use Australian medical terminology.

Output as JSON:
{{
  "scenario": "A 45-year-old presents...",
  "question_stem": "What is the most appropriate...",
  "options": {{
    "A": "Option A",
    "B": "Option B (CORRECT)",
    "C": "Option C",
    "D": "Option D"
  }},
  "correct_answer": "B",
  "explanation": "Explanation..."
}}

Generate the MCQ now (JSON only):"""

    def generate_mcq(self, template: Dict) -> Dict:
        """Generate real MCQ from template"""

        mcq_id = template["id"]
        topic = template["topic"]
        citations = template.get("references", [])

        if not citations:
            print(f"   ⚠️  {mcq_id}: No citations, skipping")
            return template

        print(f"   [{mcq_id}] {topic}...", end=" ", flush=True)

        # Create prompt
        prompt = self.create_prompt(template, citations)

        # Generate with Ollama
        response = self.generate(prompt, temperature=0.7)

        if not response:
            print("❌ Generation failed")
            return template

        # Extract JSON
        try:
            # Find JSON in response
            json_start = response.find("{")
            json_end = response.rfind("}") + 1

            if json_start == -1 or json_end <= json_start:
                print("⚠️  No JSON found")
                return template

            json_str = response[json_start:json_end]
            generated = json.loads(json_str)

            # Update template
            template["question"]["scenario"] = generated.get("scenario", "")
            template["question"]["stem"] = generated.get("question_stem", "")
            template["question"]["options"] = generated.get("options", {})
            template["correct_answer"] = generated.get("correct_answer", "B")
            template["explanation"] = generated.get("explanation", "")

            print("✅")
            return template

        except json.JSONDecodeError as e:
            print(f"⚠️  JSON parse error: {e}")
            return template

    def process_templates(self, input_file: str, output_file: str, limit: int = None):
        """Process templates from file"""

        print(f"📖 Loading: {input_file}")
        with open(input_file, "r") as f:
            data = json.load(f)

        templates = data.get("mcqs", [])

        if limit:
            templates = templates[:limit]
            print(f"   Processing first {limit} templates\n")
        else:
            print(f"   Processing all {len(templates)} templates\n")

        stats = {"total": len(templates), "success": 0, "skipped": 0}

        # Process each template
        for i, template in enumerate(templates, 1):
            print(f"[{i}/{len(templates)}]", end=" ")

            # Skip if already generated
            stem = template["question"]["stem"]
            if "?" in stem and len(stem) < 50:  # Placeholder check
                updated = self.generate_mcq(template)

                if updated["question"]["stem"] != stem:
                    stats["success"] += 1
                else:
                    stats["skipped"] += 1

                templates[i - 1] = updated
            else:
                print(f"   ✅ {template['id']}: Already complete")
                stats["success"] += 1

        # Save results
        data["mcqs"] = templates
        data["metadata"]["llm_model"] = self.model
        data["metadata"]["generated_count"] = stats["success"]

        print(f"\n💾 Saving to: {output_file}")
        with open(output_file, "w") as f:
            json.dump(data, f, indent=2)

        # Summary
        print(f"\n{'='*80}")
        print("GENERATION COMPLETE")
        print(f"{'='*80}")
        print(f"Total: {stats['total']}")
        print(f"Success: {stats['success']} ({stats['success']/stats['total']*100:.1f}%)")
        print(f"Skipped: {stats['skipped']}")
        print(f"{'='*80}\n")

        return stats


def main():
    """Run MCQ generation"""

    generator = SimpleOllamaMCQGenerator(model="qwen2.5:7b")

    input_file = "data/mcqs/missing_topics_comprehensive_mcqs.json"
    output_file = "data/mcqs/missing_topics_GENERATED_ollama.json"

    # Test with 5 MCQs first
    stats = generator.process_templates(input_file, output_file, limit=5)

    print(f"✅ Generated MCQs saved to: {output_file}")
    print(f"\nTo process all 658 templates:")
    print(f"   Remove 'limit=5' from script and re-run")


if __name__ == "__main__":
    main()
