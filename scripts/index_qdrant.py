#!/usr/bin/env python3
"""
Qdrant Vector Database Indexing
Uploads medical embeddings to Qdrant for semantic search
"""

import pickle
import logging
from pathlib import Path
from typing import List, Dict
import uuid
from tqdm import tqdm

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QdrantIndexer:
    def __init__(self, qdrant_url: str = "http://localhost:6333"):
        """Initialize Qdrant client"""
        self.client = QdrantClient(url=qdrant_url)
        logger.info(f"Connected to Qdrant at {qdrant_url}")

    def create_collection(self, collection_name: str, vector_size: int = 768):
        """Create a new collection in Qdrant"""
        try:
            # Delete if exists
            collections = self.client.get_collections().collections
            if any(c.name == collection_name for c in collections):
                logger.info(f"Collection '{collection_name}' already exists, deleting...")
                self.client.delete_collection(collection_name=collection_name)

            # Create collection
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE
                )
            )
            logger.info(f"✓ Created collection '{collection_name}' with {vector_size}-dimensional vectors")

        except Exception as e:
            logger.error(f"Failed to create collection: {e}")
            raise

    def upload_embeddings(self, embeddings_file: str, collection_name: str = "medical_knowledge", batch_size: int = 100):
        """Upload embeddings to Qdrant"""
        # Load embeddings
        logger.info(f"Loading embeddings from {embeddings_file}")
        with open(embeddings_file, 'rb') as f:
            embedded_chunks = pickle.load(f)

        logger.info(f"Loaded {len(embedded_chunks):,} embedded chunks")

        # Create collection
        vector_size = len(embedded_chunks[0]['embedding'])
        self.create_collection(collection_name, vector_size)

        # Prepare points
        logger.info("Preparing points for upload...")
        points = []

        for chunk in tqdm(embedded_chunks, desc="Creating points"):
            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=chunk['embedding'],
                payload={
                    'text': chunk['text'],
                    'source': chunk['metadata'].get('source', ''),
                    'page': chunk['metadata'].get('page', 0),
                    'chunk_index': chunk['metadata'].get('chunk_index', 0),
                    'type': chunk['metadata'].get('type', 'text'),
                    'char_count': chunk['metadata'].get('char_count', 0),
                    'word_count': chunk['metadata'].get('word_count', 0),
                    # Additional metadata for filtering
                    'source_category': self.categorize_source(chunk['metadata'].get('source', '')),
                    'exam_type': self.determine_exam_type(chunk['metadata'].get('source', '')),
                }
            )
            points.append(point)

        # Upload in batches
        logger.info(f"Uploading {len(points):,} points in batches of {batch_size}...")

        for i in tqdm(range(0, len(points), batch_size), desc="Uploading batches"):
            batch = points[i:i + batch_size]
            self.client.upsert(
                collection_name=collection_name,
                points=batch,
                wait=True
            )

        logger.info(f"✓ Upload complete!")

        # Verify
        collection_info = self.client.get_collection(collection_name=collection_name)
        logger.info(f"  Collection '{collection_name}' now has {collection_info.points_count:,} points")

    def categorize_source(self, source: str) -> str:
        """Categorize source by textbook type"""
        source_lower = source.lower()

        if any(x in source_lower for x in ['therapeutic', 'etg', 'guideline']):
            return 'australian_guidelines'
        elif any(x in source_lower for x in ['harrison', 'kumar', 'davidson', 'oxford']):
            return 'core_medicine'
        elif any(x in source_lower for x in ['talley', 'clinical_examination']):
            return 'clinical_skills'
        elif any(x in source_lower for x in ['murtagh', 'general_practice']):
            return 'gp_primary_care'
        elif any(x in source_lower for x in ['nelson', 'pediatric', 'paediatric']):
            return 'pediatrics'
        elif any(x in source_lower for x in ['williams', 'obstetric', 'gynecology', 'gynaecology']):
            return 'obgyn'
        elif any(x in source_lower for x in ['bailey', 'surgery']):
            return 'surgery'
        elif any(x in source_lower for x in ['kaplan', 'sadock', 'psychiatry']):
            return 'psychiatry'
        elif any(x in source_lower for x in ['tintinalli', 'emergency']):
            return 'emergency'
        else:
            return 'other'

    def determine_exam_type(self, source: str) -> str:
        """Determine which exam this content is relevant for"""
        source_lower = source.lower()

        # ICRP-specific
        if any(x in source_lower for x in ['nsw', 'icrp', 'young_hospital']):
            return 'ICRP'

        # AMC Clinical-specific
        if 'talley' in source_lower or 'clinical_examination' in source_lower:
            return 'AMC_Clinical'

        # All exams
        return 'AMC_MCQ'  # Default to MCQ

    def test_search(self, collection_name: str = "medical_knowledge", query: str = "acute coronary syndrome management"):
        """Test search functionality"""
        from sentence_transformers import SentenceTransformer

        logger.info(f"\nTesting search with query: '{query}'")

        # Generate query embedding
        model = SentenceTransformer('pritamdeka/S-PubMedBert-MS-MARCO')
        query_embedding = model.encode(query).tolist()

        # Search
        results = self.client.search(
            collection_name=collection_name,
            query_vector=query_embedding,
            limit=5
        )

        logger.info(f"Top 5 results:")
        for i, result in enumerate(results, 1):
            logger.info(f"\n{i}. Score: {result.score:.4f}")
            logger.info(f"   Source: {result.payload['source']}")
            logger.info(f"   Page: {result.payload['page']}")
            logger.info(f"   Text preview: {result.payload['text'][:200]}...")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Index medical embeddings in Qdrant")
    parser.add_argument("--embeddings", default="data/embeddings/medical_embeddings.pkl", help="Input embeddings file")
    parser.add_argument("--collection", default="medical_knowledge", help="Qdrant collection name")
    parser.add_argument("--qdrant-url", default="http://localhost:6333", help="Qdrant URL")
    parser.add_argument("--batch-size", type=int, default=100, help="Upload batch size")
    parser.add_argument("--test", action="store_true", help="Run test search after indexing")

    args = parser.parse_args()

    indexer = QdrantIndexer(qdrant_url=args.qdrant_url)
    indexer.upload_embeddings(
        embeddings_file=args.embeddings,
        collection_name=args.collection,
        batch_size=args.batch_size
    )

    if args.test:
        indexer.test_search(collection_name=args.collection)


if __name__ == "__main__":
    main()
