#!/usr/bin/env python3
"""
Direct StatPearls Chunking Script
Bypasses JSON conversion - works directly with .txt files
"""

import json
import logging
import re
from pathlib import Path
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def chunk_text_simple(text: str, chunk_size: int = 1000, overlap: int = 150) -> list:
    """Simple text chunking with overlap"""
    # Approximate tokens as words/4
    words = text.split()
    chunks = []

    words_per_chunk = chunk_size
    words_overlap = overlap

    i = 0
    while i < len(words):
        chunk_words = words[i:i + words_per_chunk]
        chunk_text = ' '.join(chunk_words)
        chunks.append(chunk_text)
        i += words_per_chunk - words_overlap

        if i >= len(words):
            break

    return chunks


def process_statpearls_file(txt_file: Path) -> list:
    """Process a single StatPearls .txt file into chunks"""
    # Read file
    with open(txt_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract metadata
    title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
    title = title_match.group(1) if title_match else txt_file.stem

    authors_match = re.search(r'\*\*Authors:\*\* (.+)$', content, re.MULTILINE)
    authors = authors_match.group(1) if authors_match else "Unknown"

    # Chunk the content
    chunk_texts = chunk_text_simple(content)

    # Create chunk objects
    chunks = []
    for idx, chunk_text in enumerate(chunk_texts):
        chunks.append({
            'text': chunk_text,
            'metadata': {
                'source': txt_file.name,
                'page': 1,
                'chunk_index': idx,
                'total_chunks': len(chunk_texts),
                'type': 'text',
                'char_count': len(chunk_text),
                'word_count': len(chunk_text.split()),
                'title': title,
                'authors': authors
            }
        })

    return chunks


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Chunk StatPearls .txt files directly")
    parser.add_argument("--input", default="data/processed/statpearls", help="Input directory with .txt files")
    parser.add_argument("--output", default="data/chunks_statpearls.json", help="Output JSON file")
    parser.add_argument("--chunk-size", type=int, default=1000, help="Chunk size in words")
    parser.add_argument("--overlap", type=int, default=150, help="Overlap in words")

    args = parser.parse_args()

    input_dir = Path(args.input)
    output_file = Path(args.output)

    # Find all .txt files
    txt_files = list(input_dir.glob("*.txt"))

    if not txt_files:
        logger.error(f"No .txt files found in {input_dir}")
        return 1

    logger.info(f"Found {len(txt_files)} StatPearls articles to chunk")

    all_chunks = []
    success_count = 0
    failed_count = 0

    for txt_file in tqdm(txt_files, desc="Chunking StatPearls"):
        try:
            chunks = process_statpearls_file(txt_file)
            all_chunks.extend(chunks)
            success_count += 1
        except Exception as e:
            logger.error(f"Failed to chunk {txt_file.name}: {e}")
            failed_count += 1
            continue

    # Save
    logger.info(f"\nSaving {len(all_chunks):,} chunks...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)

    # Stats
    total_words = sum(c['metadata']['word_count'] for c in all_chunks)
    logger.info(f"\n✓ Chunking complete!")
    logger.info(f"  Files processed: {success_count:,}")
    logger.info(f"  Files failed: {failed_count}")
    logger.info(f"  Total chunks: {len(all_chunks):,}")
    logger.info(f"  Total words: {total_words:,}")
    logger.info(f"  Output: {output_file}")

    return 0


if __name__ == "__main__":
    exit(main())
