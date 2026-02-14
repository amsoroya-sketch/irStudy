#!/usr/bin/env python3
"""
Generate Real Clinical MCQs from Templates using Claude API
Fast, high-quality medical content generation with Anthropic's Claude
"""

import json
import os
from pathlib import Path
from typing import Dict, List

# Check for anthropic
try:
    from anthropic import Anthropic
except ImportError:
    print("ERROR: Install anthropic package: pip install anthropic")
    exit(1)


class ClaudeMCQGenerator:
    """Generate MCQs using Claude API (Anthropic)"""

    def __init__(self, model: str = "claude-3-5-sonnet-20241022"):
        self.model = model

        # Get API key from environment
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            print("ERROR: Set ANTHROPIC_API_KEY environment variable")
            print("   export ANTHROPIC_API_KEY='your-key-here'")
            exit(1)

        self.client = Anthropic(api_key=api_key)

        print(f"\n{'='*80}")
        print(f"🏥 MCQ GENERATOR - Claude API")
        print(f"{'='*80}")
        print(f"Model: {model}")
        print(f"{'='*80}\n")

    def create_prompt(self, template: Dict, citations: List[Dict]) -> str:
        """Create MCQ generation prompt"""

        topic = template["topic"]
        specialty = template["specialty"]

        # Format citations
        citation_text = "\n\n".join(
            [
                f"**Source {i+1}:** {c['title']} ({c['author']}, {c['year']}, p.{c['page']})\n{c['content'][:400]}..."
                for i, c in enumerate(citations[:3])
            ]
        )

        return f"""You are a medical educator creating Australian AMC Part 1 exam MCQs.

**Topic:** {topic}
**Specialty:** {specialty}

**Reference Sources (use these for clinical accuracy):**
{citation_text}

**Task:** Create ONE realistic clinical MCQ based on Australian medical guidelines.

**Requirements:**
1. **Patient scenario:** 2-3 sentences with demographics, presentation, symptoms, examination findings
2. **Question stem:** Clear question asking for diagnosis, next step, or management
3. **Four options (A-D):** ONE clearly correct answer based on Australian guidelines
4. **Brief explanation:** 1-2 sentences citing the sources above
5. **Australian terminology:** Use "paracetamol" (not "acetaminophen"), "GP" (not "PCP"), etc.

**Output Format - ONLY return valid JSON:**
```json
{{
  "scenario": "A 45-year-old male presents to ED with...",
  "question_stem": "What is the most appropriate immediate management?",
  "options": {{
    "A": "First option",
    "B": "Second option (CORRECT - mark this)",
    "C": "Third option",
    "D": "Fourth option"
  }},
  "correct_answer": "B",
  "explanation": "Brief explanation citing sources..."
}}
```

Generate the MCQ now (JSON only, no markdown):"""

    def generate_mcq(self, template: Dict) -> Dict:
        """Generate real MCQ from template using Claude"""

        mcq_id = template["id"]
        topic = template["topic"]
        citations = template.get("references", [])

        if not citations:
            print(f"   ⚠️  {mcq_id}: No citations, skipping")
            return template

        print(f"   [{mcq_id}] {topic}...", end=" ", flush=True)

        # Create prompt
        prompt = self.create_prompt(template, citations)

        try:
            # Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )

            # Extract response text
            response_text = response.content[0].text

            # Parse JSON from response
            json_start = response_text.find("{")
            json_end = response_text.rfind("}") + 1

            if json_start == -1 or json_end <= json_start:
                print("⚠️  No JSON found")
                return template

            json_str = response_text[json_start:json_end]
            generated = json.loads(json_str)

            # Update template with generated content
            template["question"]["scenario"] = generated.get("scenario", "")
            template["question"]["stem"] = generated.get("question_stem", "")
            template["question"]["options"] = generated.get("options", {})
            template["correct_answer"] = generated.get("correct_answer", "B")
            template["explanation"] = generated.get("explanation", "")

            print("✅")
            return template

        except json.JSONDecodeError as e:
            print(f"⚠️  JSON error: {e}")
            return template
        except Exception as e:
            print(f"❌ API error: {e}")
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

        stats = {"total": len(templates), "success": 0, "skipped": 0, "failed": 0}

        # Process each template
        for i, template in enumerate(templates, 1):
            print(f"[{i}/{len(templates)}]", end=" ")

            # Skip if already generated (not a placeholder)
            stem = template["question"]["stem"]
            if "?" in stem and len(stem) < 50:  # Placeholder check
                updated = self.generate_mcq(template)

                # Check if successful
                if updated["question"]["stem"] != stem and len(updated["question"]["stem"]) > 50:
                    stats["success"] += 1
                    templates[i - 1] = updated
                else:
                    stats["failed"] += 1
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
        print(f"Failed: {stats['failed']}")
        print(f"Skipped: {stats['skipped']}")
        print(f"{'='*80}\n")

        return stats


def main():
    """Run MCQ generation with Claude"""

    generator = ClaudeMCQGenerator(model="claude-3-5-sonnet-20241022")

    input_file = "data/mcqs/missing_topics_comprehensive_mcqs.json"
    output_file = "data/mcqs/missing_topics_GENERATED_claude.json"

    # Test with 5 MCQs first (fast with Claude!)
    stats = generator.process_templates(input_file, output_file, limit=5)

    print(f"✅ Generated MCQs saved to: {output_file}")
    print(f"\n📊 Quality check:")
    print(f"   - Read the generated file to verify clinical accuracy")
    print(f"   - Check Australian terminology usage")
    print(f"   - Verify citations are properly referenced")
    print(f"\n🚀 To process all 658 templates:")
    print(f"   Remove 'limit=5' from script and re-run")
    print(f"   Expected time: ~30-45 minutes for full batch")


if __name__ == "__main__":
    main()
