"""
Services module for irStudy medical education platform.

Provides:
- RAG Query Service: Medical knowledge verification with Australian source prioritization
"""

from .rag_query_service import RAGQueryService, RAGVerificationResult, RAGMatch

__all__ = ['RAGQueryService', 'RAGVerificationResult', 'RAGMatch']
