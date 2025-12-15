#!/usr/bin/env python3
"""
Medical Text Chunking Pipeline
Intelligently chunks medical texts while preserving context
"""

import json
import logging
from pathlib import Path
from typing import List, Dict
from tqdm import tqdm
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MedicalTextChunker:
    def __init__(self, chunk_size: int = 1000, overlap: int = 150):
        """
        Args:
            chunk_size: Target chunk size in tokens (approximate)
            overlap: Overlap between chunks in tokens
        """
        self.chunk_size = chunk_size
        self.overlap = overlap

    def count_tokens(self, text: str) -> int:
        """Approximate token count (rough estimate: 1 token ≈ 4 chars)"""
        return len(text) // 4

    def is_table(self, text: str) -> bool:
        """Check if text is a table"""
        indicators = ['│', '┌', '┐', '└', '┘', '├', '┤', '─', '|']
        return any(ind in text for ind in indicators)

    def is_drug_info(self, text: str) -> bool:
        """Check if text contains drug dosage info (keep intact)"""
        patterns = [r'\d+\s*mg', r'\d+\s*mcg', r'Dose:', r'Dosage:']
        return any(re.search(p, text, re.IGNORECASE) for p in patterns)

    def is_list(self, text: str) -> bool:
        """Check if text is a list (differential diagnosis, etc.)"""
        lines = text.strip().split('\n')
        if len(lines) < 3:
            return False
        # Check if most lines start with bullets or numbers
        bullet_count = sum(1 for line in lines if re.match(r'^\s*[-•*\d+.)]', line))
        return bullet_count / len(lines) > 0.5

    def split_text(self, text: str) -> List[str]:
        """Split text into chunks"""
        # Try different separators in order of preference
        separators = [
            "\n\n## ",     # Major headings
            "\n\n### ",    # Sub-headings
            "\n\n#### ",   # Sub-sub-headings
            "\n\n",        # Paragraphs
            "\n",          # Lines
            ". ",          # Sentences
            " ",           # Words
        ]

        chunks = [text]

        for separator in separators:
            new_chunks = []
            for chunk in chunks:
                if self.count_tokens(chunk) <= self.chunk_size:
                    new_chunks.append(chunk)
                else:
                    # Split by this separator
                    parts = chunk.split(separator)
                    current = ""

                    for part in parts:
                        if self.count_tokens(current + separator + part) <= self.chunk_size:
                            current += separator + part if current else part
                        else:
                            if current:
                                new_chunks.append(current)
                            current = part

                    if current:
                        new_chunks.append(current)

            chunks = new_chunks

            # If all chunks are small enough, stop
            if all(self.count_tokens(c) <= self.chunk_size for c in chunks):
                break

        return chunks

    def add_overlap(self, chunks: List[str]) -> List[str]:
        """Add overlap between chunks for context"""
        if len(chunks) <= 1:
            return chunks

        overlapped = []
        for i, chunk in enumerate(chunks):
            if i == 0:
                overlapped.append(chunk)
            else:
                # Add end of previous chunk to beginning of current
                prev_chunk = chunks[i - 1]
                prev_words = prev_chunk.split()
                overlap_words = prev_words[-self.overlap:] if len(prev_words) > self.overlap else prev_words

                overlapped_chunk = " ".join(overlap_words) + " " + chunk
                overlapped.append(overlapped_chunk)

        return overlapped

    def chunk_page(self, page_data: Dict, source_metadata: Dict) -> List[Dict]:
        """Chunk a single page"""
        text = page_data['text']
        page_num = page_data['page_number']

        # Don't chunk special content
        if page_data.get('has_table') or page_data.get('has_drug_info'):
            return [{
                'text': text,
                'metadata': {
                    'source': source_metadata['filename'],
                    'page': page_num,
                    'type': 'table' if page_data.get('has_table') else 'drug_info',
                    'char_count': page_data['char_count'],
                    'word_count': page_data['word_count'],
                }
            }]

        # Check for lists (keep intact)
        if self.is_list(text):
            return [{
                'text': text,
                'metadata': {
                    'source': source_metadata['filename'],
                    'page': page_num,
                    'type': 'list',
                    'char_count': page_data['char_count'],
                    'word_count': page_data['word_count'],
                }
            }]

        # Normal chunking
        chunks_text = self.split_text(text)
        chunks_text = self.add_overlap(chunks_text)

        chunks = []
        for idx, chunk_text in enumerate(chunks_text):
            chunks.append({
                'text': chunk_text,
                'metadata': {
                    'source': source_metadata['filename'],
                    'page': page_num,
                    'chunk_index': idx,
                    'total_chunks': len(chunks_text),
                    'type': 'text',
                    'char_count': len(chunk_text),
                    'word_count': len(chunk_text.split()),
                }
            })

        return chunks

    def chunk_book(self, book_data: Dict) -> List[Dict]:
        """Chunk entire book"""
        all_chunks = []

        source_metadata = {
            'filename': book_data['filename'],
            'source_path': book_data.get('source_path', ''),
            'title': book_data.get('metadata', {}).get('title', ''),
            'author': book_data.get('metadata', {}).get('author', ''),
        }

        for page_data in book_data['pages']:
            page_chunks = self.chunk_page(page_data, source_metadata)
            all_chunks.extend(page_chunks)

        return all_chunks

    def process_all_books(self, input_dir: str = "data/processed", output_file: str = "data/chunks.json"):
        """Process all extracted books"""
        input_path = Path(input_dir)
        output_path = Path(output_file)

        if not input_path.exists():
            logger.error(f"Input directory not found: {input_dir}")
            return

        # Find all JSON files
        json_files = list(input_path.glob("*.json"))

        if not json_files:
            logger.warning(f"No JSON files found in {input_dir}")
            return

        logger.info(f"Found {len(json_files)} books to chunk")

        all_chunks = []

        for json_file in tqdm(json_files, desc="Chunking books"):
            try:
                # Load book data
                with open(json_file, 'r', encoding='utf-8') as f:
                    book_data = json.load(f)

                # Chunk
                chunks = self.chunk_book(book_data)
                all_chunks.extend(chunks)

                logger.info(f"  {json_file.stem}: {len(chunks)} chunks")

            except Exception as e:
                logger.error(f"Failed to chunk {json_file.name}: {e}")
                continue

        # Save all chunks
        logger.info(f"\nSaving {len(all_chunks)} total chunks...")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(all_chunks, f, indent=2, ensure_ascii=False)

        # Statistics
        total_words = sum(c['metadata']['word_count'] for c in all_chunks)
        logger.info(f"✓ Chunking complete!")
        logger.info(f"  Total chunks: {len(all_chunks):,}")
        logger.info(f"  Total words: {total_words:,}")
        logger.info(f"  Output: {output_path}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Chunk medical texts intelligently")
    parser.add_argument("--input", default="data/processed", help="Input directory with extracted JSON")
    parser.add_argument("--output", default="data/chunks.json", help="Output file for all chunks")
    parser.add_argument("--chunk-size", type=int, default=1000, help="Target chunk size in tokens")
    parser.add_argument("--overlap", type=int, default=150, help="Overlap between chunks in tokens")

    args = parser.parse_args()

    chunker = MedicalTextChunker(chunk_size=args.chunk_size, overlap=args.overlap)
    chunker.process_all_books(input_dir=args.input, output_file=args.output)


if __name__ == "__main__":
    main()
