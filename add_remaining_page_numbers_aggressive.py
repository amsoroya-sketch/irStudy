#!/usr/bin/env python3
"""
Aggressive RAG for remaining generic citations
- Lower confidence threshold: 0.45 (from 0.55)
- More context: 500 chars (from 300)
- Multiple query strategies
"""

import re
import json
from pathlib import Path
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from typing import List, Tuple, Optional
import time


class AggressiveRAGReferencer:
    def __init__(self, confidence_threshold=0.45):
        """Initialize with aggressive settings"""
        print("Loading embedding model...")
        self.model = SentenceTransformer("pritamdeka/S-PubMedBert-MS-MARCO")
        self.client = QdrantClient(host="localhost", port=6333)
        self.confidence_threshold = confidence_threshold
        print(
            f"✓ Aggressive RAG initialized (confidence: {confidence_threshold}, context: 500 chars)"
        )

    def query_book(self, text: str, book_filter: List[str], limit=5) -> List[dict]:
        """Query Qdrant with more results"""
        try:
            embedding = self.model.encode(text).tolist()
            results = self.client.query_points(
                collection_name="medical_knowledge", query=embedding, limit=limit, with_payload=True
            ).points

            references = []
            for point in results:
                payload = point.payload
                source = payload.get("source", "").lower()
                book = payload.get("book", "").lower()

                if any(
                    filter_term.lower() in source or filter_term.lower() in book
                    for filter_term in book_filter
                ):
                    page = payload.get("page", "unknown")
                    confidence = point.score

                    references.append(
                        {
                            "page": page,
                            "confidence": confidence,
                            "source": payload.get("source", "Unknown"),
                            "text": payload.get("text", "")[:200],
                        }
                    )

            return references

        except Exception as e:
            print(f"Error querying Qdrant: {e}")
            return []

    def get_page_reference(
        self, context: str, citation: str, line_content: str
    ) -> Tuple[Optional[str], float]:
        """
        Aggressive page reference search with multiple strategies
        """

        # Determine book filter
        if "Talley" in citation:
            book_filter = ["talley", "clinical examination"]
            book_name = "Talley & O'Connor's Clinical Examination, 8th ed"
        elif "Murtagh" in citation:
            book_filter = ["murtagh", "general practice"]
            book_name = "Murtagh's General Practice, 8th ed"
        elif "AMC" in citation:
            book_filter = ["amc", "anthology"]
            book_name = "AMC Handbook of Clinical Assessment"
        else:
            return None, 0.0

        # Extract medical keywords from context
        medical_terms = self.extract_medical_keywords(line_content)

        # Multiple query strategies (ordered by priority)
        queries = [
            context,  # Full context (500 chars)
            " ".join(medical_terms) if medical_terms else context,  # Medical keywords
            context.split("(")[0].strip(),  # Before citation
            " ".join(context.split()[-40:]),  # Last 40 words
            line_content.split("(")[0].strip()[:200],  # Current line before citation
        ]

        best_page = None
        best_confidence = 0.0
        best_source_text = ""

        for query_text in queries:
            if len(query_text) < 15:  # Skip very short queries
                continue

            refs = self.query_book(query_text, book_filter, limit=8)

            for ref in refs:
                if ref["confidence"] > best_confidence and ref["page"] != "unknown":
                    best_confidence = ref["confidence"]
                    best_page = ref["page"]
                    best_source_text = ref["text"]

                    # If we have very high confidence, stop searching
                    if best_confidence >= 0.75:
                        break

            if best_confidence >= 0.75:
                break

        # Accept if confidence meets threshold
        if best_page and best_page != "unknown" and best_confidence >= self.confidence_threshold:
            if ", p." not in citation:
                updated = citation.replace(")", f", p.{best_page})")
                return updated, best_confidence

        return None, best_confidence

    def extract_medical_keywords(self, text: str) -> List[str]:
        """Extract medical terminology from text"""
        # Common medical keywords patterns
        patterns = [
            r"\b[A-Z]{2,}\b",  # Acronyms (VTE, DVT, PE, etc.)
            r"\b\d+mg\b",  # Dosages
            r"\b\d+%\b",  # Percentages
            r"\b(?:treatment|diagnosis|examination|assessment|management)\b",
            r"\b(?:patient|clinical|medical|surgical)\b",
        ]

        keywords = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            keywords.extend(matches)

        return list(set(keywords))[:20]  # Limit to 20 keywords

    def process_file(self, file_path: Path) -> int:
        """Process a single markdown file"""

        try:
            content = file_path.read_text(encoding="utf-8")
            lines = content.split("\n")
            modified = False
            updates_count = 0

            # Pattern for generic citations (exclude those already with page numbers)
            generic_patterns = [
                (r"\(Talley[^)]*?8th ed\)(?!\s*,\s*p\.)", "Talley"),
                (r"\(Murtagh[^)]*?8th ed\)(?!\s*,\s*p\.)", "Murtagh"),
                (r"\(AMC[^)]*?\)(?!\s*,\s*p\.)", "AMC"),
            ]

            for line_num, line in enumerate(lines):
                # Skip if line already has multiple citations with pages
                if line.count(", p.") >= 2:
                    continue

                for pattern, book_type in generic_patterns:
                    for match in re.finditer(pattern, line):
                        citation = match.group()

                        # Skip if already has page number
                        if ", p." in citation:
                            continue

                        # Skip "AMC Frequency Indicator added" - not a real citation
                        if "Frequency Indicator" in citation:
                            continue

                        # Get extended context (500 chars before citation)
                        start_idx = max(0, match.start() - 500)
                        context = line[start_idx : match.end()]

                        # Query RAG with aggressive settings
                        updated_citation, confidence = self.get_page_reference(
                            context, citation, line
                        )

                        if updated_citation:
                            # Replace in line
                            lines[line_num] = lines[line_num].replace(citation, updated_citation)
                            modified = True
                            updates_count += 1

                            print(
                                f"  ✓ Line {line_num+1}: {citation[:50]}... → page added (conf: {confidence:.3f})"
                            )

            # Write back if modified
            if modified:
                updated_content = "\n".join(lines)
                file_path.write_text(updated_content, encoding="utf-8")
                return updates_count

            return 0

        except Exception as e:
            print(f"  ✗ Error processing {file_path}: {e}")
            return 0


def main():
    """Main processing function"""

    print("🚀 AGGRESSIVE RAG - Adding page numbers to remaining citations...")
    print("=" * 80)
    print("Settings:")
    print("  - Confidence threshold: 0.45 (was 0.55)")
    print("  - Context window: 500 chars (was 300)")
    print("  - Query strategies: 5 (was 3)")
    print("  - Results per query: 8 (was 5)")
    print()

    # Load generic citations report
    with open("generic_citations_report.json", "r") as f:
        report = json.load(f)

    # Initialize RAG
    rag = AggressiveRAGReferencer(confidence_threshold=0.45)

    # Process files with remaining generic citations
    files_to_process = set()
    for source, citations in report["generic_by_source"].items():
        if source in ["Talley", "Murtagh", "AMC"]:
            for citation_info in citations:
                file_path = Path("ICRP_OSCE_Preparation") / citation_info["file"]
                files_to_process.add(file_path)

    print(f"📂 Processing {len(files_to_process)} files with generic citations...")
    print()

    total_updates = 0
    files_modified = 0

    for file_path in sorted(files_to_process):
        print(f"Processing: {file_path.name}")
        updates = rag.process_file(file_path)

        if updates > 0:
            total_updates += updates
            files_modified += 1

        time.sleep(0.1)  # Rate limiting

    print()
    print("=" * 80)
    print(f"✅ Aggressive RAG Complete!")
    print(f"   Files modified: {files_modified}")
    print(f"   Citations updated: {total_updates}")
    print(f"   Confidence threshold: 0.45")
    print()

    # Generate summary
    summary = {
        "files_modified": files_modified,
        "citations_updated": total_updates,
        "confidence_threshold": 0.45,
        "context_window": 500,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }

    with open("aggressive_rag_log.json", "w") as f:
        json.dump(summary, f, indent=2)

    print(f"📝 Log saved to: aggressive_rag_log.json")


if __name__ == "__main__":
    main()
