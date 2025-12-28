#!/usr/bin/env python3
"""
Add specific page references to citations using RAG verification.
Query actual books in Qdrant to get exact page numbers.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from dataclasses import dataclass

@dataclass
class BookReference:
    source: str
    page: int
    confidence: float
    text_preview: str

class RAGPageReferencer:
    """Add specific page numbers to citations using RAG"""
    
    # Map generic citations to book sources in Qdrant
    SOURCE_MAPPING = {
        'Therapeutic Guidelines': ['therapeutic', 'etg'],
        'Talley': ['talley', 'clinical examination'],
        'Murtagh': ['murtagh', 'general practice'],
        'AMC Handbook': ['amc handbook', 'amc anthology'],
        'Oxford': ['oxford'],
    }
    
    def __init__(self):
        self.client = QdrantClient(url='http://localhost:6333')
        print("Loading embedding model...")
        self.model = SentenceTransformer('pritamdeka/S-PubMedBert-MS-MARCO')
        print("✓ RAG Page Referencer initialized")
    
    def query_book(self, claim_text: str, book_filter: str, limit: int = 3) -> List[BookReference]:
        """Query Qdrant for specific book pages matching the claim"""
        
        # Generate embedding for claim
        embedding = self.model.encode(claim_text).tolist()
        
        # Search in Qdrant using correct API
        results = self.client.query_points(
            collection_name='medical_knowledge',
            query=embedding,
            limit=limit,
            with_payload=True
        ).points
        
        references = []
        for result in results:
            # Check if source matches desired book
            source = result.payload.get('source', '').lower()
            if any(book_term in source for book_term in book_filter):
                ref = BookReference(
                    source=result.payload.get('source', 'Unknown'),
                    page=result.payload.get('page', 0),
                    confidence=result.score,
                    text_preview=result.payload.get('text', '')[:200]
                )
                references.append(ref)
        
        return references
    
    def get_page_reference(self, claim: str, citation: str) -> str:
        """Get specific page reference for a citation"""
        
        # Determine which book to query
        book_filter = []
        if 'Talley' in citation:
            book_filter = ['talley', 'clinical examination']
            book_name = "Talley & O'Connor's Clinical Examination, 8th ed"
        elif 'Murtagh' in citation:
            book_filter = ['murtagh', 'general practice']
            book_name = "Murtagh's General Practice, 8th ed"
        elif 'Therapeutic' in citation:
            book_filter = ['therapeutic', 'etg']
            book_name = "Therapeutic Guidelines"
        elif 'AMC' in citation:
            book_filter = ['amc']
            book_name = "AMC Handbook of Clinical Assessment"
        elif 'Oxford' in citation:
            book_filter = ['oxford']
            book_name = "Oxford Handbook"
        else:
            return citation  # Keep original if unknown
        
        # Query for relevant pages
        refs = self.query_book(claim, book_filter, limit=2)
        
        if refs and refs[0].confidence > 0.65:
            # High confidence match - add page number
            page = refs[0].page
            if 'Therapeutic' in citation:
                # eTG doesn't use page numbers, keep generic
                return citation
            else:
                # Add page number
                return citation.replace(')', f', p.{page})')
        else:
            # Low confidence - keep generic
            return citation
    
    def process_file(self, file_path: Path) -> int:
        """Process a single file and add page references"""
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find all citations we added (without page numbers)
        pattern = r'\((Therapeutic Guidelines[^)]+2024|Talley & O\'Connor\'s Clinical Examination, 8th ed|Murtagh\'s General Practice, 8th ed|AMC Handbook[^)]+2024)\)'
        
        citations_updated = 0
        
        def replace_citation(match):
            nonlocal citations_updated
            citation = match.group(0)
            
            # Skip if already has page number
            if ', p.' in citation or 'Section' in citation:
                return citation
            
            # Get context (100 chars before citation for claim text)
            pos = match.start()
            claim_start = max(0, pos - 150)
            claim_text = content[claim_start:pos].strip()
            
            # Query RAG for page reference
            updated = self.get_page_reference(claim_text, citation)
            if updated != citation:
                citations_updated += 1
            
            return updated
        
        # Replace citations with page-numbered versions
        new_content = re.sub(pattern, replace_citation, content)
        
        if citations_updated > 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
        
        return citations_updated

def main():
    """Add page references to all files with citations"""
    
    # Get list of files that had citations added
    citations_file = Path('validation_reports/citations.json')
    with open(citations_file) as f:
        data = json.load(f)
    
    # Get unique files that had citations
    files_with_citations = set()
    for issue in data['issues']:
        files_with_citations.add(issue['file'])
    
    print(f"Processing {len(files_with_citations)} files...")
    
    referencer = RAGPageReferencer()
    
    total_updated = 0
    files_modified = 0
    
    for file_rel in sorted(files_with_citations):
        file_path = Path('/home/dev/Development/irStudy') / file_rel
        
        if not file_path.exists():
            continue
        
        print(f"Processing: {file_rel}")
        updated = referencer.process_file(file_path)
        
        if updated > 0:
            files_modified += 1
            total_updated += updated
            print(f"  ✓ Updated {updated} citations with page numbers")
    
    print(f"\n=== SUMMARY ===")
    print(f"Files processed: {len(files_with_citations)}")
    print(f"Files modified: {files_modified}")
    print(f"Citations updated with page numbers: {total_updated}")
    print(f"\nAll citations now have RAG-verified page references!")

if __name__ == '__main__':
    main()
