#!/usr/bin/env python3
"""
Add page numbers to remaining generic Talley/Murtagh/AMC citations
Using improved RAG with:
- Lower confidence threshold (0.55)
- More context (300 chars)
- Multiple query attempts
"""

import re
import json
from pathlib import Path
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from typing import List, Tuple, Optional
import time

class ImprovedRAGPageReferencer:
    def __init__(self, confidence_threshold=0.55):
        """Initialize with lower confidence threshold"""
        print("Loading embedding model...")
        self.model = SentenceTransformer('pritamdeka/S-PubMedBert-MS-MARCO')
        self.client = QdrantClient(host="localhost", port=6333)
        self.confidence_threshold = confidence_threshold
        print(f"✓ RAG Referencer initialized (confidence threshold: {confidence_threshold})")

    def query_book(self, text: str, book_filter: List[str], limit=3) -> List[dict]:
        """Query Qdrant for relevant book passages"""
        try:
            # Generate embedding
            embedding = self.model.encode(text).tolist()

            # Query Qdrant
            results = self.client.query_points(
                collection_name='medical_knowledge',
                query=embedding,
                limit=limit,
                with_payload=True
            ).points

            # Filter by book and extract results
            references = []
            for point in results:
                payload = point.payload
                source = payload.get('source', '').lower()
                book = payload.get('book', '').lower()

                # Check if matches book filter
                if any(filter_term.lower() in source or filter_term.lower() in book
                       for filter_term in book_filter):

                    page = payload.get('page', 'unknown')
                    confidence = point.score

                    references.append({
                        'page': page,
                        'confidence': confidence,
                        'source': payload.get('source', 'Unknown'),
                        'text': payload.get('text', '')[:200]
                    })

            return references

        except Exception as e:
            print(f"Error querying Qdrant: {e}")
            return []

    def get_page_reference(self, context: str, citation: str) -> Tuple[Optional[str], float]:
        """
        Get page reference for a citation using improved RAG
        Returns: (updated_citation, confidence_score)
        """

        # Determine book filter
        if 'Talley' in citation:
            book_filter = ['talley', 'clinical examination']
            book_name = 'Talley & O\'Connor\'s Clinical Examination, 8th ed'
        elif 'Murtagh' in citation:
            book_filter = ['murtagh', 'general practice']
            book_name = 'Murtagh\'s General Practice, 8th ed'
        elif 'AMC' in citation:
            book_filter = ['amc', 'anthology']
            book_name = 'AMC Handbook of Clinical Assessment'
        else:
            return None, 0.0

        # Try multiple query strategies
        queries = [
            context,  # Full context
            context.split('(')[0].strip(),  # Before citation
            ' '.join(context.split()[-30:])  # Last 30 words
        ]

        best_page = None
        best_confidence = 0.0

        for query_text in queries:
            if len(query_text) < 20:  # Skip very short queries
                continue

            refs = self.query_book(query_text, book_filter, limit=5)

            for ref in refs:
                if ref['confidence'] > best_confidence:
                    best_confidence = ref['confidence']
                    best_page = ref['page']

                    # If we have high confidence, stop searching
                    if best_confidence >= 0.70:
                        break

            if best_confidence >= 0.70:
                break

        # If we found a page with sufficient confidence
        if best_page and best_page != 'unknown' and best_confidence >= self.confidence_threshold:
            # Update citation with page number
            if ', p.' not in citation:
                updated = citation.replace(')', f', p.{best_page})')
                return updated, best_confidence

        return None, best_confidence

    def process_file(self, file_path: Path) -> int:
        """Process a single markdown file"""

        try:
            content = file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            modified = False
            updates_count = 0

            # Pattern for generic citations
            generic_patterns = [
                (r'\(Talley[^)]*?8th ed\)(?!\s*,\s*p\.)', 'Talley'),
                (r'\(Murtagh[^)]*?8th ed\)(?!\s*,\s*p\.)', 'Murtagh'),
                (r'\(AMC[^)]*?\)(?!\s*,\s*p\.)', 'AMC')
            ]

            for line_num, line in enumerate(lines):
                for pattern, book_type in generic_patterns:
                    for match in re.finditer(pattern, line):
                        citation = match.group()

                        # Skip if already has page number
                        if ', p.' in citation:
                            continue

                        # Get context (300 chars before citation)
                        start_idx = max(0, match.start() - 300)
                        context = line[start_idx:match.end()]

                        # Query RAG for page number
                        updated_citation, confidence = self.get_page_reference(context, citation)

                        if updated_citation:
                            # Replace in line
                            lines[line_num] = lines[line_num].replace(citation, updated_citation)
                            modified = True
                            updates_count += 1

                            print(f"  ✓ Line {line_num+1}: {citation} → {updated_citation} (confidence: {confidence:.2f})")

            # Write back if modified
            if modified:
                updated_content = '\n'.join(lines)
                file_path.write_text(updated_content, encoding='utf-8')
                return updates_count

            return 0

        except Exception as e:
            print(f"  ✗ Error processing {file_path}: {e}")
            return 0

def main():
    """Main processing function"""

    print("🔍 Adding page numbers to remaining generic citations...")
    print("=" * 80)

    # Load generic citations report
    with open('generic_citations_report.json', 'r') as f:
        report = json.load(f)

    # Initialize RAG
    rag = ImprovedRAGPageReferencer(confidence_threshold=0.55)

    # Process files with generic citations
    files_to_process = set()
    for source, citations in report['generic_by_source'].items():
        if source in ['Talley', 'Murtagh', 'AMC']:
            for citation_info in citations:
                file_path = Path('ICRP_OSCE_Preparation') / citation_info['file']
                files_to_process.add(file_path)

    print(f"\n📂 Processing {len(files_to_process)} files...")
    print()

    total_updates = 0
    files_modified = 0

    for file_path in sorted(files_to_process):
        print(f"Processing: {file_path.relative_to('ICRP_OSCE_Preparation')}")
        updates = rag.process_file(file_path)

        if updates > 0:
            total_updates += updates
            files_modified += 1

        time.sleep(0.1)  # Rate limiting

    print()
    print("=" * 80)
    print(f"✅ Complete!")
    print(f"   Files modified: {files_modified}")
    print(f"   Citations updated: {total_updates}")
    print()

    # Generate summary
    summary = {
        'files_modified': files_modified,
        'citations_updated': total_updates,
        'confidence_threshold': 0.55,
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    }

    with open('remaining_page_numbers_log.json', 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"📝 Log saved to: remaining_page_numbers_log.json")

if __name__ == "__main__":
    main()
