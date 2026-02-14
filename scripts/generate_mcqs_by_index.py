#!/usr/bin/env python3
"""
Generate MCQs for specific indices using RAG system
"""

import json
import sys
import argparse
from pathlib import Path

# Add parent directory to path to import RAG generator
sys.path.insert(0, str(Path(__file__).parent))

from generate_mcqs_from_rag import RAGMCQGenerator
from datetime import datetime
from tqdm import tqdm

def main():
    parser = argparse.ArgumentParser(description='Generate MCQs by index')
    parser.add_argument('--indices', type=str, required=True, help='Comma-separated list of indices (e.g., 94,95,120)')
    parser.add_argument('--input', type=str, 
                       default='data/mcqs/missing_topics_comprehensive_mcqs.json',
                       help='Input MCQ file')
    
    args = parser.parse_args()
    
    # Parse indices
    indices = [int(x.strip()) for x in args.indices.split(',')]
    
    print(f"\n{'='*80}")
    print(f"GENERATING MCQs FOR SPECIFIC INDICES")
    print(f"{'='*80}")
    print(f"Total indices: {len(indices)}")
    print(f"Indices: {indices[:10]}{'...' if len(indices) > 10 else ''}\n")
    
    # Load MCQ file
    with open(args.input, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    mcqs = data.get('mcqs', [])
    
    # Initialize generator
    generator = RAGMCQGenerator()
    
    # Process each index
    stats = {'generated': 0, 'failed': 0, 'skipped': 0}
    
    for idx in tqdm(indices, desc="Generating MCQs"):
        if idx >= len(mcqs):
            print(f"❌ Index {idx} out of range (max: {len(mcqs)-1})")
            stats['failed'] += 1
            continue
            
        mcq = mcqs[idx]
        mcq_id = mcq['id']
        
        # Skip if already has RAG generation
        if mcq.get('generated_by') == 'rag_ollama':
            print(f"⏭️  Skipping {mcq_id} - already has RAG generation")
            stats['skipped'] += 1
            continue
        
        topic = mcq['topic']
        specialty = mcq['specialty']

        print(f"\n🔄 Generating {mcq_id}: {topic} ({specialty})")

        # Step 1: Query RAG for citations
        print(f"   🔍 Querying RAG...", end=" ")
        citations = generator.query_rag_for_content(topic, specialty)

        if not citations:
            print(f"❌ No relevant content found")
            stats['failed'] += 1
            continue

        print(f"✅ Found {len(citations)} citations")

        # Step 2: Generate MCQ with Ollama
        print(f"   🤖 Generating MCQ...", end=" ")
        updated_mcq = generator.generate_mcq_with_ollama(mcq, citations)

        if updated_mcq:
            mcqs[idx] = updated_mcq
            stats['generated'] += 1
            print(f"✅ Generated")
        else:
            stats['failed'] += 1
            print(f"❌ Failed")
    
    # Save updated MCQs
    data['mcqs'] = mcqs
    data['metadata']['last_updated'] = datetime.now().isoformat()
    
    print(f"\n💾 Saving to: {args.input}")
    with open(args.input, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print(f"\n{'='*80}")
    print("GENERATION SUMMARY")
    print(f"{'='*80}")
    print(f"✅ Successfully generated: {stats['generated']}")
    print(f"⏭️  Skipped (already complete): {stats['skipped']}")
    print(f"❌ Failed: {stats['failed']}")
    print(f"{'='*80}\n")

if __name__ == '__main__':
    main()
