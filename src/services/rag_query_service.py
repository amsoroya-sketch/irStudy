#!/usr/bin/env python3
"""
RAG Query Service - Medical Knowledge Verification System
Provides semantic search across medical textbooks with Australian source prioritization
"""

import logging
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, field
import re
from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue, SearchRequest
from sentence_transformers import SentenceTransformer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class RAGVerificationResult:
    """Result of a RAG verification query"""
    verified: bool
    confidence: float
    should_correct: bool
    original: str
    corrected: Optional[str] = None
    sources: List[Dict[str, Any]] = field(default_factory=list)
    citation: Optional[str] = None
    evidence: List[str] = field(default_factory=list)
    australian_sources_used: int = 0
    reasoning: str = ""


@dataclass
class RAGMatch:
    """Individual RAG search match"""
    score: float
    text: str
    source: str
    page: int
    is_australian: bool
    source_category: str
    exam_type: str


class RAGQueryService:
    """
    RAG Query Service for medical content validation.

    Features:
    - Australian source prioritization (2x boost)
    - Confidence-based auto-correction (threshold: 0.85)
    - Multi-source verification
    - Citation generation
    """

    # Australian sources get 2x score boost
    AUSTRALIAN_SOURCES = {
        'murtagh': 2.0,
        'amc': 2.0,
        'talley': 2.0,
        'etg': 2.0,
        'therapeutic': 2.0,
        'kemh': 2.0,
        'australian': 2.0,
        'nsw': 2.0,
        'ahpra': 2.0,
    }

    # Confidence threshold for auto-correction
    AUTO_CORRECT_THRESHOLD = 0.85

    # Verification confidence threshold
    VERIFICATION_THRESHOLD = 0.70

    def __init__(
        self,
        qdrant_url: str = "http://localhost:6333",
        collection_name: str = "medical_knowledge",
        model_name: str = "pritamdeka/S-PubMedBert-MS-MARCO"
    ):
        """Initialize RAG Query Service"""
        self.client = QdrantClient(url=qdrant_url)
        self.collection_name = collection_name

        # Load embedding model
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        logger.info(f"✓ RAG Query Service initialized (Australian sources 2x boosted)")

    def is_australian_source(self, source: str) -> bool:
        """Check if source is Australian"""
        source_lower = source.lower()
        return any(key in source_lower for key in self.AUSTRALIAN_SOURCES.keys())

    def boost_australian_sources(self, results: List[Any]) -> List[RAGMatch]:
        """Apply 2x multiplier to Australian source scores"""
        boosted_matches = []

        for result in results:
            is_aus = self.is_australian_source(result.payload.get('source', ''))
            original_score = result.score

            # Apply boost if Australian
            if is_aus:
                for aus_keyword in self.AUSTRALIAN_SOURCES:
                    if aus_keyword in result.payload.get('source', '').lower():
                        multiplier = self.AUSTRALIAN_SOURCES[aus_keyword]
                        result.score *= multiplier
                        break

            match = RAGMatch(
                score=result.score,
                text=result.payload.get('text', ''),
                source=result.payload.get('source', ''),
                page=result.payload.get('page', 0),
                is_australian=is_aus,
                source_category=result.payload.get('source_category', 'other'),
                exam_type=result.payload.get('exam_type', 'unknown')
            )
            boosted_matches.append(match)

        # Re-sort by boosted scores
        boosted_matches.sort(key=lambda x: x.score, reverse=True)

        return boosted_matches

    def search(
        self,
        query: str,
        limit: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        boost_australian: bool = True
    ) -> List[RAGMatch]:
        """
        Search RAG system with Australian source boosting.

        Args:
            query: Search query text
            limit: Maximum results to return
            filters: Optional filters (source_category, exam_type, source)
            boost_australian: Apply 2x boost to Australian sources

        Returns:
            List of RAGMatch objects, sorted by boosted score
        """
        # Generate query embedding
        query_vector = self.model.encode(query).tolist()

        # Build filters
        qdrant_filter = None
        if filters:
            conditions = []
            for key, value in filters.items():
                conditions.append(FieldCondition(key=key, match=MatchValue(value=value)))
            if conditions:
                qdrant_filter = Filter(must=conditions)

        # Execute search
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit * 2 if boost_australian else limit,  # Get more for boosting
            query_filter=qdrant_filter
        )

        # Boost Australian sources and re-rank
        if boost_australian:
            matches = self.boost_australian_sources(results)
            return matches[:limit]  # Return top after boosting
        else:
            return [
                RAGMatch(
                    score=r.score,
                    text=r.payload.get('text', ''),
                    source=r.payload.get('source', ''),
                    page=r.payload.get('page', 0),
                    is_australian=self.is_australian_source(r.payload.get('source', '')),
                    source_category=r.payload.get('source_category', 'other'),
                    exam_type=r.payload.get('exam_type', 'unknown')
                )
                for r in results[:limit]
            ]

    def verify_claim_with_correction(
        self,
        claim: str,
        context: Optional[Dict[str, str]] = None
    ) -> RAGVerificationResult:
        """
        Verify a medical claim against RAG knowledge base.

        Args:
            claim: Medical claim to verify (e.g., "First-line for T2DM: Metformin 500mg BD")
            context: Optional context (specialty, topic, etc.)

        Returns:
            RAGVerificationResult with verification status and auto-correction if needed
        """
        # Search RAG
        filters = {}
        if context:
            if 'specialty' in context:
                # Map specialty to source_category
                specialty_map = {
                    'medicine': 'core_medicine',
                    'surgery': 'surgery',
                    'psychiatry': 'psychiatry',
                    'obgyn': 'obgyn',
                    'paediatrics': 'pediatrics',
                    'gp': 'gp_primary_care'
                }
                if context['specialty'].lower() in specialty_map:
                    filters['source_category'] = specialty_map[context['specialty'].lower()]

        matches = self.search(claim, limit=5, filters=filters if filters else None)

        if not matches:
            return RAGVerificationResult(
                verified=False,
                confidence=0.0,
                should_correct=False,
                original=claim,
                reasoning="No matching evidence found in RAG knowledge base"
            )

        # Get top match
        top_match = matches[0]

        # Count Australian sources
        aus_sources = sum(1 for m in matches if m.is_australian)

        # Determine if verified
        verified = top_match.score >= self.VERIFICATION_THRESHOLD
        should_correct = top_match.score >= self.AUTO_CORRECT_THRESHOLD

        # Generate citation
        citation = self._generate_citation(matches[:3])

        # Extract evidence text
        evidence = [m.text for m in matches[:3]]

        # Generate corrected version if needed
        corrected = None
        reasoning = ""

        if should_correct and top_match.is_australian:
            corrected = self._generate_corrected_claim(claim, top_match)
            reasoning = f"High-confidence Australian source match (score: {top_match.score:.2f}). Auto-correction applied."
        elif verified:
            reasoning = f"Verified by {top_match.source} (score: {top_match.score:.2f})"
        else:
            reasoning = f"Low confidence (score: {top_match.score:.2f}). Flagged for manual review."

        return RAGVerificationResult(
            verified=verified,
            confidence=top_match.score,
            should_correct=should_correct,
            original=claim,
            corrected=corrected,
            sources=[{
                'source': m.source,
                'page': m.page,
                'score': m.score,
                'is_australian': m.is_australian,
                'text_preview': m.text[:200] + '...' if len(m.text) > 200 else m.text
            } for m in matches],
            citation=citation,
            evidence=evidence,
            australian_sources_used=aus_sources,
            reasoning=reasoning
        )

    def find_correct_dosage(
        self,
        drug_name: str,
        indication: str,
        age_group: str = 'adult'
    ) -> RAGVerificationResult:
        """
        Find correct Australian drug dosage.

        Prioritizes: eTG → Murtagh → AMC sources
        """
        query = f"{drug_name} dosage {indication} {age_group} Australian"

        # Prioritize Australian guidelines
        filters = {'source_category': 'australian_guidelines'}

        matches = self.search(query, limit=5, filters=filters)

        # Fallback to GP sources if no guidelines found
        if not matches or matches[0].score < 0.7:
            filters = {'source_category': 'gp_primary_care'}
            matches = self.search(query, limit=5, filters=filters)

        if not matches:
            return RAGVerificationResult(
                verified=False,
                confidence=0.0,
                should_correct=False,
                original=f"{drug_name} for {indication}",
                reasoning=f"No Australian dosing guidance found for {drug_name}"
            )

        top_match = matches[0]
        citation = self._generate_citation(matches[:2])

        return RAGVerificationResult(
            verified=top_match.score >= 0.7,
            confidence=top_match.score,
            should_correct=top_match.score >= self.AUTO_CORRECT_THRESHOLD,
            original=f"{drug_name} for {indication}",
            corrected=self._extract_dosage(top_match.text, drug_name) if top_match.score >= 0.85 else None,
            sources=[{
                'source': m.source,
                'page': m.page,
                'score': m.score,
                'text_preview': m.text[:300]
            } for m in matches[:3]],
            citation=citation,
            evidence=[m.text for m in matches[:3]],
            australian_sources_used=sum(1 for m in matches if m.is_australian),
            reasoning=f"Dosing from {top_match.source} p.{top_match.page}"
        )

    def verify_differential(
        self,
        presentation: str,
        differential: str,
        rank: int = 1
    ) -> RAGVerificationResult:
        """
        Verify if a differential diagnosis is appropriate.

        Args:
            presentation: Clinical presentation (e.g., "chest pain")
            differential: Proposed differential (e.g., "acute MI")
            rank: Expected rank (1 = most likely)
        """
        query = f"{presentation} differential diagnosis {differential}"

        # Prioritize Australian clinical sources
        matches = self.search(query, limit=5)

        if not matches:
            return RAGVerificationResult(
                verified=False,
                confidence=0.0,
                should_correct=False,
                original=f"{differential} for {presentation}",
                reasoning="No evidence found in textbooks"
            )

        top_match = matches[0]
        citation = self._generate_citation(matches[:3])

        return RAGVerificationResult(
            verified=top_match.score >= 0.70,
            confidence=top_match.score,
            should_correct=False,  # Differential ranking requires expert judgment
            original=f"{differential} for {presentation} (rank {rank})",
            sources=[{
                'source': m.source,
                'page': m.page,
                'score': m.score
            } for m in matches[:3]],
            citation=citation,
            evidence=[m.text for m in matches[:3]],
            australian_sources_used=sum(1 for m in matches if m.is_australian),
            reasoning=f"Differential supported by {top_match.source}"
        )

    def verify_examination_technique(
        self,
        system: str,
        technique: str
    ) -> RAGVerificationResult:
        """
        Cross-check examination technique against Talley & O'Connor.

        Args:
            system: Body system (e.g., "cardiovascular", "respiratory")
            technique: Examination technique to verify
        """
        query = f"{system} physical examination {technique} systematic"

        # Prioritize Talley & O'Connor
        matches_talley = self.search(query, limit=5, filters={'source': 'Talley'})

        # Fallback to all clinical skills sources
        if not matches_talley or matches_talley[0].score < 0.7:
            matches = self.search(query, limit=5, filters={'source_category': 'clinical_skills'})
        else:
            matches = matches_talley

        if not matches:
            return RAGVerificationResult(
                verified=False,
                confidence=0.0,
                should_correct=False,
                original=f"{technique} for {system} examination",
                reasoning="No examination technique guidance found"
            )

        top_match = matches[0]
        citation = self._generate_citation(matches[:2])

        return RAGVerificationResult(
            verified=top_match.score >= 0.75,
            confidence=top_match.score,
            should_correct=top_match.score >= 0.88,  # Higher threshold for exam techniques
            original=f"{technique} for {system} examination",
            corrected=top_match.text if top_match.score >= 0.88 else None,
            sources=[{
                'source': m.source,
                'page': m.page,
                'score': m.score,
                'text_preview': m.text[:250]
            } for m in matches[:3]],
            citation=citation,
            evidence=[m.text for m in matches[:3]],
            australian_sources_used=sum(1 for m in matches if m.is_australian),
            reasoning=f"Technique per {top_match.source} p.{top_match.page}"
        )

    def _generate_citation(self, matches: List[RAGMatch]) -> str:
        """Generate formatted citation from top matches"""
        if not matches:
            return ""

        citations = []
        for match in matches[:2]:  # Top 2 sources
            source = match.source.replace('.pdf', '').replace('_', ' ')
            page = f"p.{match.page}" if match.page > 0 else ""
            citations.append(f"{source} {page}".strip())

        return ", ".join(citations)

    def _generate_corrected_claim(self, original: str, match: RAGMatch) -> str:
        """
        Generate corrected version of claim based on RAG match.

        This is a simple implementation - could be enhanced with NLP.
        """
        # For now, append citation to original
        citation = f"{match.source.replace('.pdf', '')} p.{match.page}"

        # Check if original already has citation
        if '(' in original and ')' in original:
            # Replace existing citation
            corrected = re.sub(r'\([^)]*\)', f'({citation})', original)
        else:
            # Add citation
            corrected = f"{original} ({citation})"

        return corrected

    def _extract_dosage(self, text: str, drug_name: str) -> Optional[str]:
        """
        Extract dosage information from RAG text.

        Looks for patterns like:
        - "500mg BD"
        - "5-10mg daily"
        - "1g twice daily"
        """
        # Simple regex for dosage extraction
        dosage_pattern = r'\d+[-–]?\d*\s?(?:mg|g|mcg|mL|units?)\s+(?:once\s+)?(?:daily|BD|TDS|QID|twice|three|four times)'

        matches = re.findall(dosage_pattern, text, re.IGNORECASE)

        if matches:
            return f"{drug_name}: {matches[0]}"

        return None

    def get_statistics(self) -> Dict[str, Any]:
        """Get RAG system statistics"""
        try:
            collection_info = self.client.get_collection(collection_name=self.collection_name)
            return {
                'collection': self.collection_name,
                'total_chunks': collection_info.points_count,
                'vector_size': collection_info.config.params.vectors.size,
                'distance_metric': collection_info.config.params.vectors.distance.name,
                'australian_boost_active': True,
                'boost_multiplier': '2.0x',
                'auto_correct_threshold': self.AUTO_CORRECT_THRESHOLD,
                'verification_threshold': self.VERIFICATION_THRESHOLD
            }
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {'error': str(e)}


# Example usage
if __name__ == "__main__":
    # Initialize service
    rag = RAGQueryService()

    # Test 1: Verify drug dosage
    print("\n=== Test 1: Verify Drug Dosage ===")
    result = rag.find_correct_dosage("metformin", "type 2 diabetes")
    print(f"Verified: {result.verified}")
    print(f"Confidence: {result.confidence:.2f}")
    print(f"Citation: {result.citation}")
    print(f"Australian sources: {result.australian_sources_used}")

    # Test 2: Verify claim
    print("\n=== Test 2: Verify Medical Claim ===")
    claim = "Acute MI: Aspirin 300mg stat"
    result = rag.verify_claim_with_correction(claim)
    print(f"Original: {result.original}")
    print(f"Verified: {result.verified}")
    print(f"Confidence: {result.confidence:.2f}")
    print(f"Should auto-correct: {result.should_correct}")
    if result.corrected:
        print(f"Corrected: {result.corrected}")
    print(f"Reasoning: {result.reasoning}")

    # Test 3: Get statistics
    print("\n=== RAG Statistics ===")
    stats = rag.get_statistics()
    for key, value in stats.items():
        print(f"{key}: {value}")
