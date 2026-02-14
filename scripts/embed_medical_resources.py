#!/usr/bin/env python3
"""
Medical Resources RAG Pipeline - Complete Workflow
Processes PDFs from medical resources directory and creates searchable embeddings

This script orchestrates the complete RAG pipeline:
1. Extract PDFs to text
2. Chunk text intelligently
3. Generate embeddings with PubMedBERT
4. Index to Qdrant vector database
"""

import argparse
import logging
import sys
from pathlib import Path
import json
import subprocess
import os

# Add scripts directory to Python path
SCRIPT_DIR = Path(__file__).parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MedicalResourcesPipeline:
    def __init__(self, input_dir: str, output_dir: str = "data"):
        """
        Initialize the RAG pipeline

        Args:
            input_dir: Path to medical_resources directory with PDFs
            output_dir: Output directory for processed data
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)

        # Create output directories
        self.processed_dir = self.output_dir / "processed"
        self.embeddings_dir = self.output_dir / "embeddings"

        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.embeddings_dir.mkdir(parents=True, exist_ok=True)

        # File paths
        self.chunks_file = self.output_dir / "chunks.json"
        self.embeddings_file = self.embeddings_dir / "medical_embeddings.pkl"

        logger.info(f"Input directory: {self.input_dir}")
        logger.info(f"Output directory: {self.output_dir}")

    def find_pdfs(self):
        """Find all PDF files in input directory"""
        if not self.input_dir.exists():
            logger.error(f"Input directory does not exist: {self.input_dir}")
            return []

        pdfs = list(self.input_dir.rglob("*.pdf"))
        logger.info(f"Found {len(pdfs)} PDF files")

        # Organize by source
        sources = {}
        for pdf in pdfs:
            # Get subdirectory name (e.g., cochrane, statpearls, etc.)
            relative = pdf.relative_to(self.input_dir)
            source = relative.parts[0] if len(relative.parts) > 1 else 'root'

            if source not in sources:
                sources[source] = []
            sources[source].append(pdf)

        for source, files in sources.items():
            logger.info(f"  {source}: {len(files)} PDFs")

        return pdfs

    def step1_extract_pdfs(self, limit: int = None):
        """
        Step 1: Extract text from PDFs

        Args:
            limit: Maximum number of PDFs to process (for testing)
        """
        logger.info("\n" + "="*80)
        logger.info("STEP 1: Extracting PDFs")
        logger.info("="*80)

        pdfs = self.find_pdfs()

        if limit:
            pdfs = pdfs[:limit]
            logger.info(f"Processing first {limit} PDFs only (limit set)")

        if not pdfs:
            logger.warning("No PDFs found to process")
            return False

        # Import extractor
        try:
            from extract_pdfs import MedicalPDFExtractor
        except ImportError as e:
            logger.error(f"Cannot import MedicalPDFExtractor: {e}")
            logger.error(f"Python path: {sys.path}")
            logger.error(f"Script directory: {SCRIPT_DIR}")
            logger.error(f"Files in script directory: {list(SCRIPT_DIR.glob('*.py'))}")
            return False

        extractor = MedicalPDFExtractor(output_dir=str(self.processed_dir))

        success_count = 0
        for pdf in pdfs:
            try:
                logger.info(f"\nProcessing: {pdf.name}")
                book_data = extractor.extract_with_pymupdf(pdf)

                # Save to JSON
                output_file = self.processed_dir / f"{pdf.stem}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(book_data, f, indent=2, ensure_ascii=False)

                logger.info(f"✓ Extracted {book_data['total_pages']} pages")
                success_count += 1

            except Exception as e:
                logger.error(f"✗ Failed to extract {pdf.name}: {e}")
                continue

        logger.info(f"\n✓ Step 1 complete: {success_count}/{len(pdfs)} PDFs extracted")
        return success_count > 0

    def step2_chunk_texts(self):
        """Step 2: Chunk extracted texts"""
        logger.info("\n" + "="*80)
        logger.info("STEP 2: Chunking Texts")
        logger.info("="*80)

        # Import chunker
        try:
            from chunk_medical_texts import MedicalTextChunker
        except ImportError as e:
            logger.error(f"Cannot import MedicalTextChunker: {e}")
            return False

        chunker = MedicalTextChunker(chunk_size=1000, overlap=150)
        chunker.process_all_books(
            input_dir=str(self.processed_dir),
            output_file=str(self.chunks_file)
        )

        logger.info(f"✓ Step 2 complete: Chunks saved to {self.chunks_file}")
        return True

    def step3_generate_embeddings(self):
        """Step 3: Generate embeddings with PubMedBERT"""
        logger.info("\n" + "="*80)
        logger.info("STEP 3: Generating Embeddings")
        logger.info("="*80)

        # Import embedding generator
        try:
            from generate_embeddings import MedicalEmbeddingGenerator
        except ImportError as e:
            logger.error(f"Cannot import MedicalEmbeddingGenerator: {e}")
            return False

        # Use the PubMedBERT model we just downloaded
        model_name = "microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext"

        generator = MedicalEmbeddingGenerator(model_name=model_name)
        generator.process_chunks(
            chunks_file=str(self.chunks_file),
            output_file=str(self.embeddings_file),
            batch_size=32
        )

        logger.info(f"✓ Step 3 complete: Embeddings saved to {self.embeddings_file}")
        return True

    def step4_index_qdrant(self, collection_name: str = "medical_knowledge"):
        """Step 4: Index embeddings to Qdrant"""
        logger.info("\n" + "="*80)
        logger.info("STEP 4: Indexing to Qdrant")
        logger.info("="*80)

        # Import indexer
        try:
            from index_qdrant import QdrantIndexer
        except ImportError as e:
            logger.error(f"Cannot import QdrantIndexer: {e}")
            return False

        indexer = QdrantIndexer(qdrant_url="http://localhost:6333")
        indexer.upload_embeddings(
            embeddings_file=str(self.embeddings_file),
            collection_name=collection_name,
            batch_size=100
        )

        logger.info(f"✓ Step 4 complete: Indexed to collection '{collection_name}'")
        return True

    def run_pipeline(self, steps: str = "all", limit: int = None, collection_name: str = "medical_knowledge"):
        """
        Run the complete pipeline or specific steps

        Args:
            steps: Comma-separated step numbers (e.g., "1,2,3,4") or "all"
            limit: Maximum PDFs to process (for testing)
            collection_name: Qdrant collection name
        """
        logger.info("\n" + "="*80)
        logger.info("MEDICAL RESOURCES RAG PIPELINE")
        logger.info("="*80)

        # Parse steps
        if steps == "all":
            run_steps = [1, 2, 3, 4]
        else:
            run_steps = [int(s.strip()) for s in steps.split(",")]

        logger.info(f"Running steps: {run_steps}")

        # Execute steps
        try:
            if 1 in run_steps:
                if not self.step1_extract_pdfs(limit=limit):
                    logger.error("Step 1 failed")
                    return False

            if 2 in run_steps:
                if not self.step2_chunk_texts():
                    logger.error("Step 2 failed")
                    return False

            if 3 in run_steps:
                if not self.step3_generate_embeddings():
                    logger.error("Step 3 failed")
                    return False

            if 4 in run_steps:
                if not self.step4_index_qdrant(collection_name=collection_name):
                    logger.error("Step 4 failed")
                    return False

            logger.info("\n" + "="*80)
            logger.info("✓ PIPELINE COMPLETE!")
            logger.info("="*80)
            logger.info(f"\nYour medical knowledge base is ready for search:")
            logger.info(f"  • Qdrant collection: {collection_name}")
            logger.info(f"  • Access dashboard: http://localhost:6333/dashboard")
            logger.info(f"\nTest search:")
            logger.info(f"  python3 scripts/test_rag_search.py --query 'acute myocardial infarction'")

            return True

        except Exception as e:
            logger.error(f"Pipeline failed: {e}", exc_info=True)
            return False


def main():
    parser = argparse.ArgumentParser(
        description="Medical Resources RAG Pipeline - Complete workflow",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process all PDFs (complete pipeline)
  python3 embed_medical_resources.py --input /mnt/data/medical_resources/

  # Test with first 10 PDFs only
  python3 embed_medical_resources.py --input /mnt/data/medical_resources/ --limit 10

  # Run specific steps only
  python3 embed_medical_resources.py --input /mnt/data/medical_resources/ --steps 3,4

  # Use custom collection name
  python3 embed_medical_resources.py --input /mnt/data/medical_resources/ --collection cochrane_reviews

Pipeline Steps:
  1. Extract PDFs to structured text
  2. Chunk texts intelligently (preserving medical context)
  3. Generate embeddings with PubMedBERT
  4. Index to Qdrant vector database
        """
    )

    parser.add_argument(
        "--input",
        required=True,
        help="Path to medical_resources directory containing PDFs"
    )
    parser.add_argument(
        "--output",
        default="data",
        help="Output directory for processed data (default: data)"
    )
    parser.add_argument(
        "--steps",
        default="all",
        help="Steps to run: 'all' or comma-separated numbers (e.g., '1,2,3,4')"
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Maximum number of PDFs to process (for testing)"
    )
    parser.add_argument(
        "--collection",
        default="medical_knowledge",
        help="Qdrant collection name (default: medical_knowledge)"
    )

    args = parser.parse_args()

    # Create and run pipeline
    pipeline = MedicalResourcesPipeline(
        input_dir=args.input,
        output_dir=args.output
    )

    success = pipeline.run_pipeline(
        steps=args.steps,
        limit=args.limit,
        collection_name=args.collection
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
