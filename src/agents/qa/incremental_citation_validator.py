#!/usr/bin/env python3
"""
Incremental Citation Validator (Phase 3 Enhancement)
Helper module for fail-fast validation during MCQ/OSCE generation

CONTEXT:
Week 1 mistake: Generated 100 MCQs before discovering all citations were invalid
Phase 3 solution: Validate EACH citation immediately after RAG retrieval (fail-fast)

USAGE:
    from src.agents.qa.incremental_citation_validator import validate_citation_immediate

    # In generation loop
    for i in range(num_mcqs):
        # ... RAG retrieval ...
        citations = rag_search(query)

        # CRITICAL: Validate immediately (fail-fast on first invalid citation)
        validate_citation_immediate(
            citations=citations,
            question_id=f"MCQ-{i+1:03d}",
            fail_fast=True  # Raise exception on first invalid citation
        )

        # Only reach here if validation passed
        mcq = create_mcq(question_data, citations)
"""

from typing import Dict, Any, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CitationValidationError(Exception):
    """
    Exception raised when citation validation fails

    Used for fail-fast behavior in generation loops
    """
    pass


def validate_citation_metadata(citation: Dict[str, Any], question_id: str = "unknown") -> Dict[str, Any]:
    """
    Validate a single citation's metadata (from constraints/11-rag-citation-requirements.md)

    CRITICAL checks (ZERO TOLERANCE):
    - title: NOT "Unknown", not empty
    - year: 1990-2026 range
    - page: >0

    WARNING checks (non-critical):
    - author: "Unknown Author" is acceptable (16% of books)

    Args:
        citation: Citation dict with keys: title, author, year, page
        question_id: Question ID for error reporting

    Returns:
        {
            'valid': bool,
            'issues': list[str],  # Critical issues
            'warnings': list[str],  # Non-critical warnings
        }
    """
    issues = []
    warnings = []

    # CRITICAL: Title must not be "Unknown"
    title = citation.get('title', '')
    if not title or title.strip() == '':
        issues.append("Missing title (empty)")
        logger.error(f"{question_id}: Citation has empty title")
    elif title == 'Unknown':
        issues.append("Invalid title: 'Unknown'")
        logger.error(
            f"{question_id}: Citation has title='Unknown'\n"
            "   This indicates RAG database corruption (Week 1 mistake)\n"
            "   Run: ./scripts/pre_flight_validation.sh"
        )

    # Author validation (WARNING only)
    author = citation.get('author', '')
    if not author or author.strip() == '':
        warnings.append("Missing author (empty)")
    elif author in ['Unknown', 'Unknown Author']:
        warnings.append(f"Author is '{author}' (16% of books acceptable)")

    # CRITICAL: Year must be valid
    year = citation.get('year', '')
    if not year or year == 'Unknown':
        issues.append("Missing year")
        logger.error(f"{question_id}: Citation has missing/unknown year")
    else:
        try:
            year_int = int(str(year)[:4])  # Handle various formats
            if not (1990 <= year_int <= 2026):
                issues.append(f"Year {year_int} out of range (1990-2026)")
                logger.error(f"{question_id}: Citation year {year_int} out of valid range")
        except (ValueError, TypeError):
            issues.append(f"Invalid year format: '{year}'")
            logger.error(f"{question_id}: Cannot parse year '{year}'")

    # CRITICAL: Page must be >0
    page = citation.get('page', 0)
    if not page:
        issues.append("Missing page number")
        logger.error(f"{question_id}: Citation has missing page")
    elif isinstance(page, str) and page in ['N/A', 'Unknown', '']:
        issues.append(f"Invalid page: '{page}'")
        logger.error(f"{question_id}: Citation has invalid page '{page}'")
    elif isinstance(page, (int, float)) and page <= 0:
        issues.append(f"Invalid page number: {page} (must be >0)")
        logger.error(f"{question_id}: Citation page {page} is <=0")

    # Determine validity
    valid = len(issues) == 0

    # Log result
    if valid and not warnings:
        logger.debug(f"{question_id}: Citation valid - {title} ({author}, {year}), p. {page}")
    elif valid and warnings:
        logger.info(f"{question_id}: Citation valid with {len(warnings)} warnings - {title}")
    else:
        logger.error(f"{question_id}: Citation invalid - {len(issues)} critical issues")

    return {
        'valid': valid,
        'issues': issues,
        'warnings': warnings
    }


def validate_citation_immediate(
    citations: List[Dict[str, Any]],
    question_id: str,
    fail_fast: bool = True
) -> Dict[str, Any]:
    """
    Validate citations immediately after RAG retrieval (fail-fast)

    This is the CRITICAL function for preventing the Week 1 mistake.
    Called in generation loop IMMEDIATELY after RAG search, BEFORE creating MCQ.

    Args:
        citations: List of citation dicts from RAG
        question_id: Question ID (e.g., "MCQ-042")
        fail_fast: If True, raise exception on first invalid citation (default: True)

    Returns:
        {
            'all_valid': bool,
            'valid_count': int,
            'invalid_count': int,
            'validations': list[dict]
        }

    Raises:
        CitationValidationError: If fail_fast=True and any citation is invalid
    """
    validations = []
    valid_count = 0
    invalid_count = 0

    for i, citation in enumerate(citations, 1):
        validation = validate_citation_metadata(
            citation=citation,
            question_id=f"{question_id} Citation {i}"
        )
        validations.append(validation)

        if validation['valid']:
            valid_count += 1
        else:
            invalid_count += 1

            # FAIL-FAST: Raise exception on first invalid citation
            if fail_fast:
                error_msg = (
                    f"\n{'='*70}\n"
                    f"CITATION VALIDATION FAILED: {question_id} Citation {i}\n"
                    f"{'='*70}\n"
                    f"Citation: {citation.get('title', 'N/A')} ({citation.get('year', 'N/A')}), p. {citation.get('page', 'N/A')}\n"
                    f"\n"
                    f"CRITICAL ISSUES:\n"
                )
                for issue in validation['issues']:
                    error_msg += f"  • {issue}\n"

                error_msg += (
                    f"\n"
                    f"This indicates RAG database corruption (Week 1 mistake).\n"
                    f"\n"
                    f"REMEDIATION:\n"
                    f"1. Stop generation immediately (DO NOT continue)\n"
                    f"2. Run: ./scripts/pre_flight_validation.sh\n"
                    f"3. If validation fails, run:\n"
                    f"     python scripts/fix_rag_metadata.py\n"
                    f"     python scripts/update_embeddings_metadata.py\n"
                    f"     python scripts/index_qdrant.py --embeddings data/embeddings/medical_embeddings_fixed.pkl\n"
                    f"4. Re-run pre-flight validation\n"
                    f"5. Only after validation PASSES, restart generation\n"
                    f"\n"
                    f"DO NOT GENERATE CONTENT WITH INVALID CITATIONS.\n"
                    f"{'='*70}\n"
                )

                raise CitationValidationError(error_msg)

    all_valid = invalid_count == 0

    result = {
        'all_valid': all_valid,
        'valid_count': valid_count,
        'invalid_count': invalid_count,
        'validations': validations
    }

    # Log summary
    if all_valid:
        logger.info(f"{question_id}: All {valid_count} citations validated ✅")
    else:
        logger.error(
            f"{question_id}: {invalid_count}/{len(citations)} citations invalid ❌"
        )

    return result


def validate_rag_before_generation(
    qdrant_url: str = "http://localhost:6333",
    collection_name: str = "medical_knowledge"
) -> None:
    """
    MANDATORY pre-generation validation check

    Run this BEFORE starting any MCQ/OSCE generation to verify RAG database health

    Raises:
        CitationValidationError: If RAG database has invalid metadata
    """
    from qdrant_client import QdrantClient
    from sentence_transformers import SentenceTransformer

    logger.info("Running pre-generation RAG validation...")

    client = QdrantClient(url=qdrant_url)
    embedder = SentenceTransformer('pritamdeka/S-PubMedBert-MS-MARCO')

    # Test query
    test_query = "depression SSRI first-line treatment Therapeutic Guidelines"
    query_embedding = embedder.encode(test_query)

    results = client.search(
        collection_name=collection_name,
        query_vector=query_embedding.tolist(),
        limit=3
    )

    if not results:
        raise CitationValidationError(
            "RAG returned no results - database may be empty\n"
            "Run: ./scripts/pre_flight_validation.sh"
        )

    # Validate top result metadata
    top_result = results[0]
    citation = {
        'title': top_result.payload.get('title', ''),
        'author': top_result.payload.get('author', ''),
        'year': top_result.payload.get('year', ''),
        'page': top_result.payload.get('page', 0)
    }

    validation = validate_citation_metadata(
        citation=citation,
        question_id="PRE-GENERATION-TEST"
    )

    if not validation['valid']:
        error_msg = (
            f"\n{'='*70}\n"
            f"PRE-GENERATION VALIDATION FAILED\n"
            f"{'='*70}\n"
            f"RAG database returned invalid metadata for test query.\n"
            f"\n"
            f"Test Query: {test_query}\n"
            f"Result: {citation['title']} ({citation['year']}), p. {citation['page']}\n"
            f"\n"
            f"CRITICAL ISSUES:\n"
        )
        for issue in validation['issues']:
            error_msg += f"  • {issue}\n"

        error_msg += (
            f"\n"
            f"DO NOT PROCEED WITH GENERATION!\n"
            f"\n"
            f"REMEDIATION:\n"
            f"1. Run: ./scripts/pre_flight_validation.sh\n"
            f"2. Follow remediation steps if validation fails\n"
            f"3. Only proceed after validation PASSES\n"
            f"{'='*70}\n"
        )

        raise CitationValidationError(error_msg)

    logger.info(f"✅ Pre-generation validation PASSED")
    logger.info(f"   Test citation: {citation['title']} ({citation['year']}), p. {citation['page']}")


# Example usage in generation script
if __name__ == "__main__":
    import sys

    # Example: Test with mock citation data
    print("Testing Incremental Citation Validator...")
    print("="*70)

    # Test 1: Valid citation
    print("\nTest 1: Valid citation")
    valid_citation = {
        'title': 'John Murtagh General Practice',
        'author': 'John Murtagh',
        'year': '2020',
        'page': 2113
    }
    try:
        result = validate_citation_immediate(
            citations=[valid_citation],
            question_id="MCQ-TEST-001",
            fail_fast=True
        )
        print(f"Result: {result['all_valid']} ✅")
    except CitationValidationError as e:
        print(f"FAILED: {e}")
        sys.exit(1)

    # Test 2: Invalid citation (title="Unknown")
    print("\nTest 2: Invalid citation (title='Unknown')")
    invalid_citation = {
        'title': 'Unknown',
        'author': 'John Smith',
        'year': '2020',
        'page': 100
    }
    try:
        result = validate_citation_immediate(
            citations=[invalid_citation],
            question_id="MCQ-TEST-002",
            fail_fast=True
        )
        print(f"Result: {result['all_valid']} ❌ (Should have raised exception!)")
        sys.exit(1)
    except CitationValidationError as e:
        print(f"Exception raised as expected ✅")
        print(f"Error message preview: {str(e)[:200]}...")

    # Test 3: Pre-generation validation
    print("\nTest 3: Pre-generation RAG validation")
    try:
        validate_rag_before_generation()
        print("Pre-generation validation PASSED ✅")
    except CitationValidationError as e:
        print(f"Pre-generation validation FAILED: {e}")
        sys.exit(1)

    print("\n" + "="*70)
    print("✅ ALL TESTS PASSED")
    print("="*70)
