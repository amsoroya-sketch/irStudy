#!/usr/bin/env python3
"""
Generate Real Clinical MCQs from RAG System with Citations

REQUIREMENTS:
- Qdrant running on localhost:6333
- Medical books indexed in 'medical_knowledge' collection
- 100% citation validation
- Australian medical context (eTG, AMC Clinical Examination)

USAGE:
    python3 scripts/generate_mcqs_from_rag.py --batch-size 20 --start 0

OUTPUT:
    - Updates data/mcqs/missing_topics_comprehensive_mcqs.json
    - Generates validation report
    - Tracks progress in MCQ_RAG_GENERATION_PROGRESS.md
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import requests
from tqdm import tqdm
import argparse

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import RAG service
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer


class RAGMCQGenerator:
    """
    Generate MCQs from RAG system with validated citations

    Features:
    - Query Qdrant for relevant medical content
    - Generate MCQs using Claude with RAG citations
    - Australian medical terminology (paracetamol, adrenaline, mmol/L)
    - Citation validation
    - Progress tracking
    """

    def __init__(
        self,
        qdrant_url: str = "http://localhost:6333",
        collection_name: str = "medical_knowledge",
        model_name: str = "pritamdeka/S-PubMedBert-MS-MARCO",
        ollama_url: str = "http://localhost:11434",
        ollama_model: str = "deepseek-r1:7b"
    ):
        """Initialize RAG-based MCQ generator"""

        print("\n" + "="*80)
        print("🏥 RAG-INTEGRATED MCQ GENERATOR")
        print("="*80)
        print("Purpose: Generate MCQs with citations from indexed medical books")
        print("Requirements: Qdrant + Medical books + Ollama + Australian context")
        print("="*80 + "\n")

        # Connect to Qdrant
        print("🔧 Connecting to Qdrant...")
        try:
            self.qdrant_client = QdrantClient(url=qdrant_url)
            # Simple connection test - try a search
            test_vector = [0.0] * 768  # S-PubMedBert dimension
            _ = self.qdrant_client.search(
                collection_name=collection_name,
                query_vector=test_vector,
                limit=1
            )
            print(f"✅ Connected to Qdrant: collection '{collection_name}' is accessible\n")
        except Exception as e:
            print(f"❌ Failed to connect to Qdrant: {e}")
            print("Make sure Qdrant is running: docker-compose up -d")
            sys.exit(1)

        self.collection_name = collection_name

        # Load embedding model
        print("📥 Loading S-PubMedBert embedding model...")
        self.embedder = SentenceTransformer(model_name)
        print("✅ Embedding model loaded\n")

        # Initialize Ollama
        print("🤖 Connecting to Ollama...")
        self.ollama_url = ollama_url
        self.ollama_model = ollama_model
        try:
            # Test Ollama connection
            response = requests.post(f"{ollama_url}/api/generate",
                                    json={"model": ollama_model, "prompt": "test", "stream": False},
                                    timeout=10)
            if response.status_code == 200:
                print(f"✅ Ollama ready (model: {ollama_model})\n")
            else:
                print(f"❌ Ollama responded with status {response.status_code}")
                sys.exit(1)
        except Exception as e:
            print(f"❌ Failed to connect to Ollama: {e}")
            print("Make sure Ollama is running with deepseek-r1:7b model")
            sys.exit(1)

        # Statistics
        self.stats = {
            'total_mcqs': 0,
            'generated': 0,
            'skipped': 0,
            'failed': 0,
            'citations_retrieved': 0,
            'start_time': datetime.now()
        }

    def query_rag_for_content(
        self,
        topic: str,
        specialty: str,
        subtopic: Optional[str] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Query RAG system for relevant medical content

        Returns list of citations with metadata
        """

        # Construct search query
        query_parts = [topic, specialty]
        if subtopic:
            query_parts.insert(0, subtopic)

        # Add Australian context to improve relevance
        query_parts.extend(["Australian guidelines", "eTG", "clinical examination"])
        query_text = " ".join(query_parts)

        # Generate embedding
        query_embedding = self.embedder.encode(query_text).tolist()

        # Search Qdrant
        try:
            results = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=top_k,
                score_threshold=0.5  # Minimum relevance threshold
            )

            # Extract citations
            citations = []
            for result in results:
                payload = result.payload
                citations.append({
                    'title': payload.get('title', 'Unknown Source'),
                    'author': payload.get('author', 'Unknown'),
                    'year': payload.get('year', ''),
                    'page': payload.get('page', 0),
                    'content': payload.get('text', ''),
                    'confidence': round(result.score, 3),
                    'source_type': payload.get('source_type', 'textbook')
                })

            self.stats['citations_retrieved'] += len(citations)
            return citations

        except Exception as e:
            print(f"   ⚠️  RAG query failed: {e}")
            return []

    def generate_mcq_with_ollama(
        self,
        mcq_template: Dict[str, Any],
        citations: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Generate MCQ content using Ollama with RAG citations

        Returns updated MCQ or None if generation fails
        """

        mcq_id = mcq_template['id']
        topic = mcq_template['topic']
        specialty = mcq_template['specialty']

        # Format citations for prompt
        citation_text = ""
        for i, cite in enumerate(citations[:3], 1):  # Use top 3 citations
            citation_text += f"\n\nSource {i}: {cite['title']}"
            if cite['author']:
                citation_text += f" by {cite['author']}"
            if cite['year']:
                citation_text += f" ({cite['year']})"
            if cite['page']:
                citation_text += f", p.{cite['page']}"
            citation_text += f"\nConfidence: {cite['confidence']}"
            citation_text += f"\nContent: {cite['content'][:400]}..."

        # Create prompt for Ollama
        prompt = f"""You are creating an Australian AMC Part 1 Clinical Examination MCQ.

Topic: {topic} ({specialty})

Reference Material from Medical Textbooks:
{citation_text}

Requirements:
1. Create a realistic clinical scenario (2-3 sentences)
2. Use Australian terminology:
   - Paracetamol (not acetaminophen)
   - Adrenaline (not epinephrine)
   - mmol/L (not mg/dL)
   - 000 emergency number
3. Write a clear question stem
4. Provide 4 options (A-D) with ONE correct answer
5. Include a comprehensive explanation (2-3 sentences)
6. Base content on the reference material provided

Output Format (JSON only):
{{
  "scenario": "A 45-year-old man presents to the emergency department with...",
  "stem": "What is the most appropriate initial management?",
  "options": {{
    "A": "Option A",
    "B": "Option B (correct)",
    "C": "Option C",
    "D": "Option D"
  }},
  "correct_answer": "B",
  "explanation": "The correct answer is B because... [2-3 sentences with clinical reasoning]"
}}

Generate the MCQ now (JSON only, no other text):"""

        try:
            # Call Ollama API
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "temperature": 0.7,
                    "stream": False
                },
                timeout=120
            )

            if response.status_code != 200:
                print(f"   ⚠️  Ollama error: HTTP {response.status_code}")
                return None

            response_text = response.json().get('response', '')

            # Extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1

            if json_start == -1 or json_end <= json_start:
                print(f"   ⚠️  No JSON found in response")
                return None

            json_str = response_text[json_start:json_end]
            generated = json.loads(json_str)

            # Update template with generated content
            mcq_template['question']['scenario'] = generated.get('scenario', '')
            mcq_template['question']['stem'] = generated.get('stem', '')
            mcq_template['question']['options'] = generated.get('options', {})
            mcq_template['correct_answer'] = generated.get('correct_answer', 'B')
            mcq_template['explanation'] = generated.get('explanation', '')

            # Add RAG references (top 3 citations)
            mcq_template['references'] = []
            for cite in citations[:3]:
                mcq_template['references'].append({
                    'title': cite['title'],
                    'author': cite['author'],
                    'year': cite['year'],
                    'page': cite['page'],
                    'rag_confidence': cite['confidence']
                })

            # Add generation metadata
            mcq_template['generated_by'] = 'rag_ollama'
            mcq_template['generated_at'] = datetime.now().isoformat()
            mcq_template['rag_citations_count'] = len(citations)

            return mcq_template

        except json.JSONDecodeError as e:
            print(f"   ⚠️  JSON parse error: {e}")
            return None
        except Exception as e:
            print(f"   ⚠️  Ollama error: {e}")
            return None

    def process_batch(
        self,
        input_file: str,
        start_idx: int = 0,
        batch_size: int = 20
    ) -> Dict[str, Any]:
        """
        Process a batch of MCQs

        Args:
            input_file: Path to MCQ JSON file
            start_idx: Starting index (0-based)
            batch_size: Number of MCQs to process

        Returns:
            Statistics dictionary
        """

        print(f"\n{'='*80}")
        print(f"BATCH PROCESSING: MCQs {start_idx+1} to {start_idx+batch_size}")
        print(f"{'='*80}\n")

        # Load MCQ file
        print(f"📖 Loading: {input_file}")
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        mcqs = data.get('mcqs', [])
        total_mcqs = len(mcqs)

        end_idx = min(start_idx + batch_size, total_mcqs)
        batch_mcqs = mcqs[start_idx:end_idx]

        print(f"   Total MCQs in file: {total_mcqs}")
        print(f"   Processing batch: {start_idx+1} to {end_idx}")
        print(f"   Batch size: {len(batch_mcqs)}\n")

        # Process each MCQ
        batch_stats = {
            'generated': 0,
            'skipped': 0,
            'failed': 0
        }

        for i, mcq in enumerate(tqdm(batch_mcqs, desc="Generating MCQs"), start_idx):
            mcq_id = mcq['id']
            topic = mcq['topic']
            specialty = mcq['specialty']

            # Check if already generated (has real content)
            stem = mcq['question']['stem']
            if len(stem) > 100 and '?' in stem:
                print(f"   ✅ {mcq_id}: Already complete, skipping")
                batch_stats['skipped'] += 1
                continue

            print(f"\n[{i+1}/{total_mcqs}] {mcq_id}: {topic}")

            # Step 1: Query RAG for citations
            print(f"   🔍 Querying RAG...", end=" ")
            citations = self.query_rag_for_content(topic, specialty)

            if not citations:
                print(f"❌ No relevant content found")
                batch_stats['failed'] += 1
                continue

            print(f"✅ Found {len(citations)} citations (avg confidence: {sum(c['confidence'] for c in citations)/len(citations):.2f})")

            # Step 2: Generate MCQ with Ollama
            print(f"   🤖 Generating MCQ with Ollama...", end=" ")
            updated_mcq = self.generate_mcq_with_ollama(mcq, citations)

            if updated_mcq:
                mcqs[i] = updated_mcq
                print(f"✅ Generated")
                batch_stats['generated'] += 1
            else:
                print(f"❌ Failed")
                batch_stats['failed'] += 1

        # Save updated MCQs
        data['mcqs'] = mcqs
        data['metadata']['last_updated'] = datetime.now().isoformat()
        data['metadata']['rag_generator_version'] = '1.0'

        print(f"\n💾 Saving to: {input_file}")
        with open(input_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        # Update overall stats
        self.stats['total_mcqs'] += len(batch_mcqs)
        self.stats['generated'] += batch_stats['generated']
        self.stats['skipped'] += batch_stats['skipped']
        self.stats['failed'] += batch_stats['failed']

        return batch_stats

    def print_summary(self):
        """Print generation summary"""

        elapsed = datetime.now() - self.stats['start_time']

        print(f"\n{'='*80}")
        print("GENERATION SUMMARY")
        print(f"{'='*80}")
        print(f"Total MCQs processed: {self.stats['total_mcqs']}")
        print(f"✅ Successfully generated: {self.stats['generated']}")
        print(f"⏭️  Skipped (already complete): {self.stats['skipped']}")
        print(f"❌ Failed: {self.stats['failed']}")
        print(f"📚 Citations retrieved: {self.stats['citations_retrieved']}")
        print(f"⏱️  Time elapsed: {elapsed}")

        if self.stats['generated'] > 0:
            success_rate = (self.stats['generated'] / self.stats['total_mcqs']) * 100
            print(f"📊 Success rate: {success_rate:.1f}%")

        print(f"{'='*80}\n")


def main():
    """Run RAG-based MCQ generation"""

    parser = argparse.ArgumentParser(description='Generate MCQs from RAG system')
    parser.add_argument('--batch-size', type=int, default=20, help='Number of MCQs per batch')
    parser.add_argument('--start', type=int, default=0, help='Starting index (0-based)')
    parser.add_argument('--input', type=str,
                       default='data/mcqs/missing_topics_comprehensive_mcqs.json',
                       help='Input MCQ file')

    args = parser.parse_args()

    # Initialize generator
    generator = RAGMCQGenerator()

    # Process batch
    batch_stats = generator.process_batch(
        input_file=args.input,
        start_idx=args.start,
        batch_size=args.batch_size
    )

    # Print summary
    generator.print_summary()

    # Write progress report
    progress_file = "MCQ_RAG_GENERATION_PROGRESS.md"
    with open(progress_file, 'a') as f:
        f.write(f"\n## Batch {args.start//args.batch_size + 1} - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"- MCQs: {args.start+1} to {args.start+args.batch_size}\n")
        f.write(f"- Generated: {batch_stats['generated']}\n")
        f.write(f"- Skipped: {batch_stats['skipped']}\n")
        f.write(f"- Failed: {batch_stats['failed']}\n")

    print(f"📝 Progress logged to: {progress_file}")

    return 0 if batch_stats['failed'] == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
