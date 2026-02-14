#!/usr/bin/env python3
"""
QA-004 LLM Citation Verifier
Week 2 Day 2 Implementation

Purpose: Verify Tier 2 citations (0.75-0.90 confidence) using LLM
Method: Claude evaluates if citation actually supports MCQ content
Target: Process 58 Tier 2 MCQs, expected 95%+ pass rate
"""

from typing import Dict, Any, List
import json
import os


class LLMCitationVerifier:
    """
    Verifies citations using LLM (Claude) for Tier 2 MCQs

    Tier 2: RAG confidence 0.75-0.90 (not high enough for auto-approve)
    LLM verifies: Does the citation actually support this MCQ?
    """

    def __init__(self, model: str = "claude-sonnet-4"):
        """
        Initialize LLM verifier

        Args:
            model: Claude model to use (default: claude-sonnet-4)
        """
        self.model = model

    def verify_citation(
        self,
        mcq: Dict[str, Any],
        citation: Dict[str, Any],
        rag_confidence: float
    ) -> Dict[str, Any]:
        """
        Verify a single citation using LLM

        Args:
            mcq: MCQ dictionary with question, options, explanation
            citation: Citation dictionary with title, page, etc.
            rag_confidence: RAG confidence score (0.75-0.90)

        Returns:
            {
                'verified': bool,
                'llm_confidence': float (0.0-1.0),
                'reasoning': str,
                'recommendation': 'approve' or 'reject',
                'processing_time': float (seconds)
            }
        """
        import time
        start_time = time.time()

        # Extract MCQ components
        question_text = self._format_mcq_for_verification(mcq)
        citation_text = self._format_citation_for_verification(citation)

        # Construct LLM prompt
        prompt = self._construct_verification_prompt(
            question_text=question_text,
            citation_text=citation_text,
            rag_confidence=rag_confidence
        )

        # Call LLM (Claude)
        llm_response = self._call_llm(prompt)

        # Parse LLM response
        result = self._parse_llm_response(llm_response)

        processing_time = time.time() - start_time
        result['processing_time'] = round(processing_time, 2)
        result['rag_confidence'] = rag_confidence

        return result

    def _format_mcq_for_verification(self, mcq: Dict[str, Any]) -> str:
        """Format MCQ into readable text for LLM"""
        question = mcq.get('question', {})
        scenario = question.get('scenario', '')
        stem = question.get('stem', '')
        options = question.get('options', {})
        explanation = mcq.get('explanation', '')

        formatted = f"""MCQ Question:
Scenario: {scenario}

Question: {stem}

Options:
"""
        for key in ['A', 'B', 'C', 'D', 'E']:
            if key in options:
                formatted += f"{key}. {options[key]}\n"

        formatted += f"\nExplanation: {explanation}"

        return formatted

    def _format_citation_for_verification(self, citation: Dict[str, Any]) -> str:
        """Format citation into readable text for LLM"""
        title = citation.get('title', 'Unknown')
        page = citation.get('page', 'N/A')
        year = citation.get('year', 'Unknown')

        return f"Citation: {title}, Page {page} ({year})"

    def _construct_verification_prompt(
        self,
        question_text: str,
        citation_text: str,
        rag_confidence: float
    ) -> str:
        """Construct prompt for LLM verification"""

        prompt = f"""You are a medical education quality assurance expert verifying MCQ citations.

**Task:** Verify if this citation appropriately supports this medical MCQ.

**RAG System Confidence:** {rag_confidence:.3f} (Tier 2: requires manual verification)

{question_text}

---

**Proposed Citation:**
{citation_text}

---

**Verification Criteria:**

1. **Relevance:** Does the citation source cover the medical topic in the MCQ?
2. **Specificity:** Does it address the specific clinical scenario/question asked?
3. **Appropriateness:** Is this citation type appropriate for this content level?
   - Guidelines/textbooks: Appropriate for clinical management
   - Research articles: Appropriate for evidence-based recommendations
   - Legislative sources: Appropriate for legal/regulatory content

4. **Australian Context:** For Australian medical exams (ICRP/AMC):
   - Is an Australian source used where appropriate (eTG, RANZCP, NSW Health)?
   - If not Australian, is the content still applicable to Australian practice?

**Your Response (JSON format):**

```json
{{
  "verified": true/false,
  "llm_confidence": 0.0-1.0,
  "reasoning": "Brief explanation of your decision (2-3 sentences)",
  "recommendation": "approve" or "reject",
  "concerns": ["List any concerns, empty if none"]
}}
```

**Guidelines:**
- **Approve** if citation is relevant, specific, and appropriate (even if not perfect)
- **Reject** only if citation is clearly wrong topic, misleading, or inappropriate
- Be lenient: This is supplementary verification, not primary source checking
- RAG already filtered to 0.75+ confidence, so major mismatches unlikely

Please verify this citation:"""

        return prompt

    def _call_llm(self, prompt: str) -> str:
        """
        Call LLM (Claude) for verification

        Note: In production, this would call Claude API
        For now, returns structured mock response for testing
        """
        # TODO: Implement actual Claude API call
        # For Week 2 Day 2 implementation, using mock response

        # Mock response (replace with actual API call)
        mock_response = """{
  "verified": true,
  "llm_confidence": 0.85,
  "reasoning": "The citation is relevant to the clinical scenario and provides appropriate guidance for the question topic. While not perfectly specific, it covers the general domain adequately for an educational MCQ.",
  "recommendation": "approve",
  "concerns": []
}"""

        return mock_response

    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM JSON response"""
        try:
            # Extract JSON from response (handle markdown code blocks)
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                response = response[start:end].strip()
            elif "```" in response:
                start = response.find("```") + 3
                end = response.find("```", start)
                response = response[start:end].strip()

            result = json.loads(response)

            # Validate required fields
            required_fields = ['verified', 'llm_confidence', 'reasoning', 'recommendation']
            for field in required_fields:
                if field not in result:
                    raise ValueError(f"Missing required field: {field}")

            return result

        except (json.JSONDecodeError, ValueError) as e:
            # Fallback if parsing fails
            return {
                'verified': False,
                'llm_confidence': 0.0,
                'reasoning': f"LLM response parsing failed: {str(e)}",
                'recommendation': 'reject',
                'concerns': ['LLM response format error']
            }

    def verify_mcq(self, mcq: Dict[str, Any], rag_validation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify all citations in an MCQ

        Args:
            mcq: MCQ dictionary
            rag_validation: QA-003 RAG validation result

        Returns:
            {
                'mcq_id': str,
                'tier': int (from RAG),
                'rag_confidence': float,
                'llm_verified': bool,
                'llm_confidence': float,
                'final_recommendation': 'approve' or 'reject',
                'citation_verifications': list[dict]
            }
        """
        mcq_id = mcq.get('id', 'unknown')
        rag_confidence = rag_validation.get('average_confidence', 0.0)
        tier = rag_validation.get('overall_tier', 3)

        # Only verify Tier 2 (0.75-0.90)
        if tier != 2:
            return {
                'mcq_id': mcq_id,
                'tier': tier,
                'rag_confidence': rag_confidence,
                'llm_verified': False,
                'skipped': True,
                'reason': f'Tier {tier} does not require LLM verification'
            }

        # Verify each citation
        references = mcq.get('references', [])
        citation_verifications = []

        for i, ref in enumerate(references):
            verification = self.verify_citation(
                mcq=mcq,
                citation=ref,
                rag_confidence=rag_confidence
            )
            citation_verifications.append(verification)

        # Overall decision: approve if majority of citations verified
        verified_count = sum(1 for v in citation_verifications if v.get('verified', False))
        total_citations = len(citation_verifications)

        llm_verified = verified_count >= (total_citations * 0.5)  # 50% threshold
        avg_llm_confidence = sum(v.get('llm_confidence', 0) for v in citation_verifications) / total_citations if total_citations > 0 else 0.0

        final_recommendation = 'approve' if llm_verified else 'reject'

        return {
            'mcq_id': mcq_id,
            'tier': tier,
            'rag_confidence': rag_confidence,
            'llm_verified': llm_verified,
            'llm_confidence': round(avg_llm_confidence, 3),
            'final_recommendation': final_recommendation,
            'citation_count': total_citations,
            'verified_count': verified_count,
            'citation_verifications': citation_verifications
        }

    def verify_batch(
        self,
        mcqs: List[Dict[str, Any]],
        rag_validations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Verify a batch of MCQs

        Args:
            mcqs: List of MCQ dictionaries
            rag_validations: List of QA-003 RAG validation results

        Returns:
            {
                'total_mcqs': int,
                'tier2_count': int,
                'verified_count': int,
                'rejected_count': int,
                'approval_rate': float,
                'avg_llm_confidence': float,
                'verifications': list[dict]
            }
        """
        # Create MCQ ID to validation mapping
        validation_map = {v['mcq_id']: v for v in rag_validations}

        verifications = []
        tier2_count = 0
        verified_count = 0
        rejected_count = 0
        llm_confidences = []

        for mcq in mcqs:
            mcq_id = mcq.get('id', 'unknown')
            rag_validation = validation_map.get(mcq_id, {})

            verification = self.verify_mcq(mcq, rag_validation)
            verifications.append(verification)

            if verification.get('tier') == 2:
                tier2_count += 1
                if verification.get('llm_verified'):
                    verified_count += 1
                else:
                    rejected_count += 1

                if 'llm_confidence' in verification:
                    llm_confidences.append(verification['llm_confidence'])

        approval_rate = verified_count / tier2_count if tier2_count > 0 else 0.0
        avg_llm_confidence = sum(llm_confidences) / len(llm_confidences) if llm_confidences else 0.0

        return {
            'total_mcqs': len(mcqs),
            'tier2_count': tier2_count,
            'verified_count': verified_count,
            'rejected_count': rejected_count,
            'approval_rate': round(approval_rate, 3),
            'avg_llm_confidence': round(avg_llm_confidence, 3),
            'verifications': verifications
        }


def main():
    """Test the LLM verifier"""
    print("="*70)
    print("QA-004 LLM CITATION VERIFIER")
    print("="*70)
    print("Status: Mock implementation (replace _call_llm with actual API)")
    print("Purpose: Verify Tier 2 citations (0.75-0.90 confidence)")
    print("="*70)

    verifier = LLMCitationVerifier()

    # Mock test
    mock_mcq = {
        'id': 'TEST-001',
        'question': {
            'scenario': 'A 45-year-old presents with low mood',
            'stem': 'What is the first-line treatment?',
            'options': {
                'A': 'SSRI antidepressant',
                'B': 'TCA antidepressant',
                'C': 'MAOI',
                'D': 'ECT',
                'E': 'No treatment'
            }
        },
        'explanation': 'SSRIs are first-line for major depression',
        'references': [
            {
                'title': 'Therapeutic Guidelines: Psychiatry',
                'page': '245',
                'year': '2024'
            }
        ]
    }

    mock_rag_validation = {
        'mcq_id': 'TEST-001',
        'average_confidence': 0.82,
        'overall_tier': 2
    }

    result = verifier.verify_mcq(mock_mcq, mock_rag_validation)

    print("\nTest Result:")
    print(json.dumps(result, indent=2))

    print("\n" + "="*70)
    print("✅ QA-004 Implementation Complete (Mock Mode)")
    print("="*70)
    print("\nNext Steps:")
    print("1. Replace _call_llm() with actual Claude API integration")
    print("2. Test on 5 real Tier 2 MCQs")
    print("3. Process all 58 Tier 2 MCQs")
    print("4. Generate validation report")


if __name__ == "__main__":
    import sys
    sys.exit(main())
