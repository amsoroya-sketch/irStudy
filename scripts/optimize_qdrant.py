#!/usr/bin/env python3
"""
Qdrant Collection Optimization Script
Optimizes HNSW index parameters for medical knowledge search
"""

import logging
from qdrant_client import QdrantClient
from qdrant_client.models import (
    HnswConfigDiff,
    OptimizersConfigDiff,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QdrantOptimizer:
    def __init__(self, qdrant_url: str = "http://localhost:6333"):
        """Initialize Qdrant client"""
        self.client = QdrantClient(url=qdrant_url)
        logger.info(f"Connected to Qdrant at {qdrant_url}")

    def optimize_collection(self, collection_name: str = "medical_knowledge"):
        """
        Optimize collection for medical search workload

        HNSW Parameters optimized for:
        - 42,647 medical knowledge vectors
        - High recall requirements (medical accuracy critical)
        - Fast query performance (<100ms target)
        - Balanced indexing vs query speed

        Parameter Choices:
        - m=32: Higher connectivity for better recall (default 16)
        - ef_construct=200: Better index quality (default 100)
        - full_scan_threshold=20000: Use HNSW for all queries
        - max_indexing_threads=4: Parallel indexing for faster updates
        """
        logger.info(f"Optimizing collection '{collection_name}'...")

        try:
            # Update HNSW configuration
            self.client.update_collection(
                collection_name=collection_name,
                hnsw_config=HnswConfigDiff(
                    m=32,  # Increased from 16 for better recall
                    ef_construct=200,  # Increased from 100 for better index quality
                    full_scan_threshold=20000,  # Use HNSW for all queries
                    max_indexing_threads=4,  # Parallel indexing
                ),
            )
            logger.info("✓ Updated HNSW configuration")

            # Update optimizer configuration
            self.client.update_collection(
                collection_name=collection_name,
                optimizer_config=OptimizersConfigDiff(
                    indexing_threshold=5000,  # Start indexing earlier
                    max_optimization_threads=4,  # Parallel optimization
                ),
            )
            logger.info("✓ Updated optimizer configuration")

            # Get updated collection info
            info = self.client.get_collection(collection_name=collection_name)
            logger.info(f"\n✓ Optimization complete!")
            logger.info(f"  Points: {info.points_count:,}")
            logger.info(f"  Indexed vectors: {info.indexed_vectors_count:,}")
            logger.info(f"  Status: {info.status}")

            return info

        except Exception as e:
            logger.error(f"Optimization failed: {e}")
            raise

    def get_collection_stats(self, collection_name: str = "medical_knowledge"):
        """Get collection statistics"""
        try:
            info = self.client.get_collection(collection_name=collection_name)

            logger.info(f"\n=== Collection Statistics ===")
            logger.info(f"Collection: {collection_name}")
            logger.info(f"Points: {info.points_count:,}")
            logger.info(f"Indexed vectors: {info.indexed_vectors_count:,}")
            logger.info(f"Status: {info.status}")
            logger.info(f"Optimizer status: {info.optimizer_status}")
            logger.info(f"Segments: {info.segments_count}")
            logger.info(f"\nHNSW Config:")
            logger.info(f"  m: {info.config.hnsw_config.m}")
            logger.info(f"  ef_construct: {info.config.hnsw_config.ef_construct}")
            logger.info(f"  full_scan_threshold: {info.config.hnsw_config.full_scan_threshold}")
            logger.info(f"  max_indexing_threads: {info.config.hnsw_config.max_indexing_threads}")

            return info

        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            raise


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Optimize Qdrant collection")
    parser.add_argument("--collection", default="medical_knowledge", help="Collection name")
    parser.add_argument("--qdrant-url", default="http://localhost:6333", help="Qdrant URL")
    parser.add_argument("--stats-only", action="store_true", help="Only show stats, don't optimize")

    args = parser.parse_args()

    optimizer = QdrantOptimizer(qdrant_url=args.qdrant_url)

    if args.stats_only:
        optimizer.get_collection_stats(collection_name=args.collection)
    else:
        optimizer.optimize_collection(collection_name=args.collection)
        optimizer.get_collection_stats(collection_name=args.collection)


if __name__ == "__main__":
    main()
