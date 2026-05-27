"""
RAG Service - Qdrant Vector DB Integration
Retrieval-Augmented Generation for clinical guideline context

PERFORMANCE TARGET: <500ms per query (p95)
SOURCES: eTG, AMC Handbook, evidence-based guidelines
"""
import logging
import os
from typing import List, Dict, Any, Optional
import time

from qdrant_client import QdrantClient

logger = logging.getLogger(__name__)


class RAGService:
    """
    RAG service for medical guideline retrieval.
    
    Integrates with Qdrant vector database for semantic search
    of clinical guidelines and evidence-based protocols.
    """
    
    def __init__(
        self,
        qdrant_url: Optional[str] = None,
        collection_name: str = "medical_guidelines"
    ):
        """
        Initialize RAG service with Qdrant client.
        
        Args:
            qdrant_url: Qdrant server URL (default: http://localhost:6333)
            collection_name: Vector collection name
        """
        self.qdrant_url = qdrant_url or os.getenv("QDRANT_URL", "http://localhost:6333")
        self.collection_name = collection_name
        
        try:
            self.client = QdrantClient(url=self.qdrant_url)
            logger.info(f"✅ RAG service initialized: {self.qdrant_url}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Qdrant client: {e}")
            self.client = None
    
    def retrieve_context(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve top-K clinical guideline chunks for query.
        
        Args:
            query: Student question or clinical scenario
            top_k: Number of chunks to retrieve (default: 5)
        
        Returns:
            List of dicts with structure:
            [
                {
                    "text": "Clinical guideline chunk...",
                    "source": "eTG Cardiovascular",
                    "page_ref": "p.245"
                },
                ...
            ]
        
        Performance: <500ms target (p95)
        """
        start_time = time.time()
        
        if not self.client:
            logger.warning("⚠️  Qdrant client not initialized, returning empty results")
            return []
        
        try:
            # Convert query to embedding vector
            query_vector = self._embed_query(query)
            
            # Search Qdrant collection
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=top_k
            )
            
            # Format results
            formatted_results = []
            seen_texts = set()  # For deduplication
            
            for hit in results:
                text = hit.payload.get("text", "")
                
                # Deduplicate
                if text in seen_texts:
                    continue
                seen_texts.add(text)
                
                formatted_results.append({
                    "text": text,
                    "source": hit.payload.get("source", "Unknown"),
                    "page_ref": hit.payload.get("page_ref", "N/A")
                })
            
            elapsed_ms = (time.time() - start_time) * 1000
            logger.info(
                f"✅ RAG retrieval: {len(formatted_results)} chunks, "
                f"{elapsed_ms:.0f}ms (target: <500ms)"
            )
            
            return formatted_results
        
        except Exception as e:
            logger.error(f"❌ RAG retrieval failed: {e}")
            return []
    
    def _embed_query(self, query: str) -> List[float]:
        """
        Convert query text to embedding vector.
        
        Args:
            query: Text to embed
        
        Returns:
            Embedding vector (768 dimensions for mock)
        
        NOTE: In production, use actual embedding model.
        For tests, return mock vector.
        """
        # TODO: Implement actual embedding
        # Options:
        # 1. OpenAI text-embedding-3-small (1536 dims, $0.00002/1K tokens)
        # 2. Sentence Transformers (local, free)
        # 3. Qdrant native embedding
        
        # For now, return mock vector for testing
        import hashlib
        hash_val = int(hashlib.md5(query.encode()).hexdigest()[:8], 16)
        return [float((hash_val >> i) & 1) for i in range(768)]  # Mock 768-dim vector
    
    def search_similar(
        self,
        query_text: str,
        limit: int = 5,
        confidence_threshold: float = 0.65
    ) -> List[Dict[str, Any]]:
        """
        Search for similar content in Qdrant with confidence filtering.

        Args:
            query_text: Text to search for
            limit: Maximum number of results (default: 5)
            confidence_threshold: Minimum confidence score (default: 0.65)

        Returns:
            List of dicts with structure:
            [
                {
                    "source": "eTG Cardiovascular",
                    "qdrant_point_id": "550e8400-e29b-41d4-a716-446655440000",
                    "score": 0.85,
                    "content": "Clinical guideline text...",
                    "page": 42,
                    "title": "Therapeutic Guidelines",
                    "author": "eTG Complete",
                    "year": "2023"
                },
                ...
            ]

        Note:
            - Filters results by confidence_threshold (≥0.65 per constraints/11)
            - Returns qdrant_point_id as UUID string
            - Australian sources prioritized in future enhancement
        """
        if not self.client:
            logger.warning("⚠️  Qdrant client not initialized, returning empty results")
            return []

        try:
            # Convert query to embedding vector
            query_vector = self._embed_query(query_text)

            # Search Qdrant collection
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit,
                score_threshold=confidence_threshold
            )

            # Format results with complete metadata
            formatted_results = []

            for hit in results:
                # Ensure minimum confidence threshold
                if hit.score < confidence_threshold:
                    continue

                # Extract payload with complete bibliographic metadata
                payload = hit.payload

                formatted_results.append({
                    "source": payload.get("source", "Unknown"),
                    "qdrant_point_id": str(hit.id),  # UUID as string
                    "score": float(hit.score),
                    "content": payload.get("text", ""),
                    "page": payload.get("page", 0),
                    "title": payload.get("title", ""),
                    "author": payload.get("author", ""),
                    "year": payload.get("year", "")
                })

            logger.info(
                f"✅ RAG search: {len(formatted_results)} results with confidence ≥{confidence_threshold}"
            )

            return formatted_results

        except Exception as e:
            logger.error(f"❌ RAG search failed: {e}")
            return []

    def health_check(self) -> bool:
        """
        Check Qdrant connection health.

        Returns:
            True if Qdrant reachable, False otherwise
        """
        if not self.client:
            return False

        try:
            # Attempt to get collection info
            self.client.get_collection(self.collection_name)
            return True
        except Exception as e:
            logger.warning(f"⚠️  Qdrant health check failed: {e}")
            return False
