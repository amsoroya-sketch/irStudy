#!/usr/bin/env python3
"""
QA-003 RAG Citation Validator
Validates MCQ citations using RAG system

Week 1 Day 4 Implementation: RAGCitationValidator + confidence scoring (50 LOC core)
Week 2 Enhancement: Added metadata completeness validation (Phase 3)
"""

from typing import Dict, Any, List
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGCitationValidator:
    """
    Validates citations using RAG system with three-tier confidence scoring

    Tier 1 (>0.90): Auto-approve
    Tier 2 (0.75-0.90): LLM verification required
    Tier 3 (<0.75): Reject and regenerate
    """

    def __init__(self, qdrant_url: str = "http://localhost:6333"):
        """Initialize with RAG system connection"""
        self.client = QdrantClient(url=qdrant_url)
        self.collection = "medical_knowledge"
        self.embedder = SentenceTransformer('pritamdeka/S-PubMedBert-MS-MARCO')

    def validate_citation(
        self,
        citation_text: str,
        expected_page: str = None,
        mcq_content: str = None
    ) -> Dict[str, Any]:
        """
        Validate a single citation

        Args:
            citation_text: Citation text to validate
            expected_page: Expected page number (optional)
            mcq_content: MCQ question content for context (optional)

        Returns:
            {
                'valid': bool,
                'confidence': float (0.0-1.0),
                'tier': int (1, 2, or 3),
                'recommendation': str,  # 'approve', 'llm_verify', 'reject'
                'matches': list[dict],
                'top_match': dict
            }
        """
        # Embed citation text
        query_embedding = self.embedder.encode(citation_text)

        # Query Qdrant
        results = self.client.search(
            collection_name=self.collection,
            query_vector=query_embedding,
            limit=5,
            score_threshold=0.5
        )

        if not results:
            return {
                'valid': False,
                'confidence': 0.0,
                'tier': 3,
                'recommendation': 'reject',
                'matches': [],
                'top_match': None,
                'reason': 'No RAG matches found'
            }

        # Calculate confidence score
        confidence = self._calculate_confidence(
            rag_results=results,
            expected_page=expected_page
        )

        # PHASE 3 ENHANCEMENT: Validate metadata completeness
        top_result = results[0]
        metadata_validation = self._validate_citation_metadata(
            payload=top_result.payload,
            mcq_id=f"Citation: {citation_text[:50]}"
        )

        # Determine tier and recommendation (accounting for metadata validity)
        tier, recommendation = self._determine_tier(
            confidence=confidence,
            metadata_valid=metadata_validation['valid'],
            metadata_issues=metadata_validation.get('issues', [])
        )

        # Format matches
        matches = []
        for result in results:
            matches.append({
                'title': result.payload.get('title', 'Unknown'),
                'page': result.payload.get('page', 'N/A'),
                'year': result.payload.get('year', 'Unknown'),
                'author': result.payload.get('author', 'Unknown'),
                'score': round(result.score, 3),
                'source_type': result.payload.get('source_type', 'unknown')
            })

        return {
            'valid': tier in [1, 2],
            'confidence': confidence,
            'tier': tier,
            'recommendation': recommendation,
            'matches': matches,
            'top_match': matches[0] if matches else None,
            # PHASE 3 ENHANCEMENT: Include metadata validation results
            'metadata_validation': metadata_validation
        }

    def _calculate_confidence(
        self,
        rag_results: list,
        expected_page: str = None
    ) -> float:
        """
        Calculate multi-factor confidence score

        Factors (Week 2 optimized):
        - Semantic similarity (RAG score): 70% weight (increased from 60%)
        - Page number match: 15% weight (decreased from 20%)
        - Source type: 10% weight (with Australian boost)
        - Recency: 5% weight (decreased from 10%)

        Returns:
            float: 0.0-1.0 confidence score
        """
        top_result = rag_results[0]

        # Factor 1: Semantic similarity (70% weight - INCREASED)
        # Rationale: Most reliable indicator of citation quality
        semantic_score = top_result.score  # Already 0.0-1.0

        # Factor 2: Page number match (15% weight - DECREASED)
        # Rationale: Page tolerance increased to ±5 for multi-page topics
        page_score = 1.0  # Default if no expected page
        if expected_page:
            result_page = top_result.payload.get('page', '')
            page_score = 1.0 if self._pages_match(result_page, expected_page) else 0.5

        # Factor 3: Source type (10% weight with Australian boost)
        # Rationale: Australian guidelines preferred for ICRP preparation
        source_type = top_result.payload.get('source_type', 'other')
        title = top_result.payload.get('title', '').lower()

        # Base source scores
        source_scores = {
            'guideline': 1.0,
            'journal': 0.9,
            'textbook': 0.8,
            'other': 0.6
        }
        source_score = source_scores.get(source_type, 0.5)

        # Australian source boost (+0.15 for eTG, RANZCP, NSW Health, etc.)
        australian_keywords = [
            'therapeutic guidelines', 'etg', 'ranzcp', 'nsw health',
            'australian', 'talley', "o'connor", 'mims', 'amh'
        ]
        is_australian = any(keyword in title for keyword in australian_keywords)
        if is_australian:
            source_score = min(1.0, source_score + 0.15)

        # Factor 4: Recency (5% weight - DECREASED)
        # Rationale: Less critical than semantic match
        year = top_result.payload.get('year', '2020')
        try:
            year_int = int(str(year)[:4])  # Handle 'YYYY' format
            recency_score = min(1.0, max(0.5, 1.0 - (2024 - year_int) * 0.05))
        except (ValueError, TypeError):
            recency_score = 0.7  # Default if year parsing fails

        # Weighted average (REVERTED TO WEEK 1: 60/20/10/10)
        # Week 2 Day 1 experiment showed 70/15/10/5 made scores WORSE
        # Root cause: RAG semantic scores too low (0.70-0.75)
        # Solution: Improve RAG queries, not weights
        confidence = (
            semantic_score * 0.60 +
            page_score * 0.20 +
            source_score * 0.10 +
            recency_score * 0.10
        )

        return round(confidence, 3)

    def _pages_match(self, page1: str, page2: str) -> bool:
        """
        Check if page numbers match (with tolerance ±5)

        Week 2 Update: Increased tolerance from ±2 to ±5
        Rationale: Medical textbook topics often span 3-10 pages

        Handles formats: "45", "45-47", "p.45", "Section 11.3"
        """
        try:
            # Extract first number from each page string
            import re
            num1 = int(re.search(r'\d+', str(page1)).group())
            num2 = int(re.search(r'\d+', str(page2)).group())
            return abs(num1 - num2) <= 5  # ±5 page tolerance (increased from ±2)
        except (AttributeError, ValueError, TypeError):
            return False  # Can't parse pages

    def _validate_citation_metadata(self, payload: Dict[str, Any], mcq_id: str = "unknown") -> Dict[str, Any]:
        """
        Validate citation metadata completeness (Week 2 Phase 3 Enhancement)

        CONTEXT: Week 1 mistake had 212/212 citations with title="Unknown"
        This validation prevents that by checking RAG returned complete metadata

        Validation criteria (from constraints/11-rag-citation-requirements.md):
        - title: NOT "Unknown", not empty (CRITICAL)
        - author: NOT "Unknown" preferred ("Unknown Author" is WARNING only)
        - year: 1990-2026 range (CRITICAL)
        - page: >0 (CRITICAL)

        Args:
            payload: Citation payload from Qdrant search result
            mcq_id: MCQ identifier for logging

        Returns:
            {
                'valid': bool,  # True if all CRITICAL checks pass
                'issues': list[str],  # List of issues found
                'warnings': list[str],  # Non-critical warnings
                'tier': int  # 1 = valid, 3 = critical issues found
            }
        """
        issues = []
        warnings = []

        # CRITICAL: Title must not be "Unknown"
        title = payload.get('title', '')
        if not title or title.strip() == '':
            issues.append("Missing title (empty)")
            logger.error(f"{mcq_id}: Citation has empty title")
        elif title == 'Unknown':
            issues.append("Invalid title: 'Unknown'")
            logger.error(f"{mcq_id}: Citation has title='Unknown' (Week 1 mistake detected!)")

        # Author validation (WARNING only for "Unknown Author")
        author = payload.get('author', '')
        if not author or author.strip() == '':
            warnings.append("Missing author (empty)")
        elif author in ['Unknown', 'Unknown Author']:
            warnings.append(f"Author is '{author}' (16% of books acceptable)")
            logger.warning(f"{mcq_id}: Citation has author='{author}' (non-critical)")

        # CRITICAL: Year must be valid (1990-2026)
        year = payload.get('year', '')
        if not year or year == 'Unknown':
            issues.append("Missing year")
            logger.error(f"{mcq_id}: Citation has missing/unknown year")
        else:
            try:
                year_int = int(str(year)[:4])  # Handle various formats
                if not (1990 <= year_int <= 2026):
                    issues.append(f"Year {year_int} out of range (1990-2026)")
                    logger.error(f"{mcq_id}: Citation year {year_int} out of valid range")
            except (ValueError, TypeError):
                issues.append(f"Invalid year format: '{year}'")
                logger.error(f"{mcq_id}: Cannot parse year '{year}'")

        # CRITICAL: Page must be >0
        page = payload.get('page', 0)
        if not page:
            issues.append("Missing page number")
            logger.error(f"{mcq_id}: Citation has missing page")
        elif isinstance(page, str) and page in ['N/A', 'Unknown', '']:
            issues.append(f"Invalid page: '{page}'")
            logger.error(f"{mcq_id}: Citation has invalid page '{page}'")
        elif isinstance(page, (int, float)) and page <= 0:
            issues.append(f"Invalid page number: {page} (must be >0)")
            logger.error(f"{mcq_id}: Citation page {page} is <=0")

        # Determine validity
        has_critical_issues = len(issues) > 0
        valid = not has_critical_issues

        # Log summary
        if valid and not warnings:
            logger.debug(f"{mcq_id}: Citation metadata valid - {title} ({author}, {year}), p. {page}")
        elif valid and warnings:
            logger.info(f"{mcq_id}: Citation metadata valid with {len(warnings)} warnings")

        return {
            'valid': valid,
            'issues': issues,
            'warnings': warnings,
            'tier': 3 if has_critical_issues else 1,  # Critical issues = Tier 3 (reject)
            'metadata': {
                'title': title,
                'author': author,
                'year': year,
                'page': page
            }
        }

    def _determine_tier(self, confidence: float, metadata_valid: bool = True, metadata_issues: list = None) -> tuple:
        """
        Determine tier and recommendation based on confidence AND metadata validity

        Week 2 Phase 3 Enhancement: Added metadata validity check
        CRITICAL: Invalid metadata (title="Unknown", invalid year, etc.) = Tier 3 (reject)

        Returns:
            (tier: int, recommendation: str)
        """
        # CRITICAL: Metadata issues = automatic Tier 3 (reject)
        # This prevents the Week 1 mistake (212/212 citations with title="Unknown")
        if not metadata_valid:
            logger.warning(f"Citation metadata invalid, forcing Tier 3: {metadata_issues}")
            return (3, 'reject_metadata_invalid')

        # Standard confidence-based tiering (only if metadata is valid)
        if confidence >= 0.90:
            return (1, 'approve')
        elif confidence >= 0.75:
            return (2, 'llm_verify')
        else:
            return (3, 'reject')

    def validate_mcq(self, mcq: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate all citations in an MCQ

        Args:
            mcq: MCQ dictionary with 'references' and 'question' fields

        Returns:
            {
                'mcq_id': str,
                'overall_valid': bool,
                'average_confidence': float,
                'overall_tier': int,
                'recommendation': str,
                'citations': list[dict]  # Individual citation validations
            }
        """
        mcq_id = mcq.get('id', 'unknown')
        references = mcq.get('references', [])
        question = mcq.get('question', {})
        mcq_content = f"{question.get('scenario', '')} {question.get('stem', '')}"

        citation_validations = []
        confidences = []

        for ref in references:
            citation_text = f"{ref.get('title', '')} {ref.get('page', '')}"
            expected_page = ref.get('page', None)

            validation = self.validate_citation(
                citation_text=citation_text,
                expected_page=expected_page,
                mcq_content=mcq_content
            )

            citation_validations.append(validation)
            confidences.append(validation['confidence'])

        # Calculate overall metrics
        avg_confidence = round(sum(confidences) / len(confidences), 3) if confidences else 0.0
        overall_tier, overall_recommendation = self._determine_tier(avg_confidence)

        return {
            'mcq_id': mcq_id,
            'overall_valid': all(c['valid'] for c in citation_validations),
            'average_confidence': avg_confidence,
            'overall_tier': overall_tier,
            'recommendation': overall_recommendation,
            'citations': citation_validations,
            'citation_count': len(citation_validations)
        }

    def validate_batch(self, mcqs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate a batch of MCQs

        Args:
            mcqs: List of MCQ dictionaries

        Returns:
            {
                'total_mcqs': int,
                'tier1_count': int,
                'tier2_count': int,
                'tier3_count': int,
                'auto_approval_rate': float,
                'average_confidence': float,
                'validations': list[dict]
            }
        """
        validations = []
        tier_counts = {1: 0, 2: 0, 3: 0}
        all_confidences = []

        for mcq in mcqs:
            validation = self.validate_mcq(mcq)
            validations.append(validation)

            tier = validation['overall_tier']
            tier_counts[tier] += 1
            all_confidences.append(validation['average_confidence'])

        total = len(mcqs)
        auto_approval_rate = tier_counts[1] / total if total > 0 else 0.0
        avg_confidence = round(sum(all_confidences) / len(all_confidences), 3) if all_confidences else 0.0

        return {
            'total_mcqs': total,
            'tier1_count': tier_counts[1],
            'tier2_count': tier_counts[2],
            'tier3_count': tier_counts[3],
            'auto_approval_rate': round(auto_approval_rate, 3),
            'average_confidence': avg_confidence,
            'validations': validations
        }
