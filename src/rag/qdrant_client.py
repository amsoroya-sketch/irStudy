"""Simple Qdrant client wrapper for RAG operations"""

import requests
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer


class SearchResult:
    """Wrapper for Qdrant search results"""
    def __init__(self, score: float, payload: Dict[str, Any]):
        self.score = score
        self.payload = payload


class QdrantClient:
    """Simple Qdrant client for vector search"""

    def __init__(self, host: str = "localhost", port: int = 6333):
        self.base_url = f"http://{host}:{port}"
        # Load embedding model (MUST match the model used for indexing!)
        # Data was indexed with PubMedBERT (768-dim), not all-MiniLM-L6-v2 (384-dim)
        self.model = SentenceTransformer('microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext')

    def search(
        self,
        collection_name: str,
        query_text: str,
        limit: int = 5,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """
        Search for similar vectors in Qdrant collection

        Args:
            collection_name: Name of the Qdrant collection
            query_text: Text query to search for
            limit: Maximum number of results to return
            filter: Optional filter conditions

        Returns:
            List of SearchResult objects with scores and payloads
        """
        try:
            # 1. Generate embedding for query
            query_embedding = self.model.encode(query_text).tolist()

            # 2. Search Qdrant
            url = f"{self.base_url}/collections/{collection_name}/points/search"
            payload = {
                "vector": query_embedding,
                "limit": limit,
                "with_payload": True,
                "score_threshold": 0.5  # Minimum similarity threshold
            }

            if filter:
                payload["filter"] = filter

            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()

            # 3. Return SearchResult objects
            results = response.json().get("result", [])
            return [
                SearchResult(
                    score=hit["score"],
                    payload=hit["payload"]
                )
                for hit in results
            ]
        except Exception as e:
            print(f"ERROR: RAG search failed: {e}")
            return []
