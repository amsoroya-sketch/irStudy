"""
Study Card Generator - Auto-Generate Flashcards from OSCE Feedback
PRD-P1-005 Phase 1-3: Full Study Card Generation Pipeline

Automatically creates 3-5 spaced-repetition flashcards from completed OSCE sessions:
1. Extracts learning points from AI Examiner feedback using Claude 3.5 Sonnet ✅
2. Generates Q&A pairs with clinical context (Phase 2) ✅
3. Adds RAG citations for evidence-based learning (Phase 2) ✅
4. Initializes SM-2 spaced repetition parameters (Phase 3) ✅
5. Persists to database with batch operations (Phase 3) ✅

SECURITY:
- API key from Vault (secret/ai-osce/claude-api-key)
- NO hardcoded credentials
- Input validation for all user-provided data

AUSTRALIAN MEDICAL STANDARDS:
- Use paracetamol (NOT acetaminophen)
- Use mmol/L (NOT mg/dL)
- Use 000 for emergency (NOT 911)
- Reference eTG, RACGP, AMH (NOT US sources)

PERFORMANCE:
- Target: <8 seconds for 3 cards generation
- Uses async/await for Claude API calls (parallel Q&A generation)
- Batch operations where possible

RAG CITATION REQUIREMENTS (Phase 2):
- Confidence threshold: ≥0.65 (ZERO tolerance per constraints/11)
- All citations MUST have qdrant_point_id (UUID format)
- Australian sources prioritized (≥60% target)
- NO placeholders accepted (per constraints/12)

SM-2 INITIALIZATION (Phase 3):
- ease_factor: 2.5 (default per SM-2 algorithm)
- interval_days: 1 (first review tomorrow)
- repetitions: 0 (no reviews yet)
- next_review_date: NOW (available immediately)
"""
import logging
import json
import asyncio
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from anthropic import Anthropic, APIError
from sqlalchemy.exc import IntegrityError

from src.core.vault import get_vault_secret
from src.ai.rag_service import RAGService
from src.db.models import StudyCard, OSCEAttemptAI

logger = logging.getLogger(__name__)


class StudyCardGenerator:
    """
    Generate study cards from OSCE session feedback using Claude 3.5 Sonnet.

    Phase 1 Implementation: ✅
    - Learning point extraction from feedback
    - Claude API integration with Vault secrets
    - Error handling and validation

    Phase 2 Implementation: ✅
    - Q&A pair generation (parallel Claude API calls)
    - RAG citation enrichment (Qdrant integration)
    - Content substance validation (placeholder detection)

    Phase 3 Implementation: ✅
    - SM-2 parameter initialization (ease_factor=2.5, interval=1, repetitions=0)
    - Database persistence with batch operations
    - Full pipeline integration (session → learning points → Q&A → citations → database)
    """

    def __init__(self, rag_service: Optional[RAGService] = None):
        """
        Initialize Claude API client with Vault integration.

        API Key Sources (in order):
        1. Vault: secret/ai-osce/claude-api-key (primary)
        2. Vault: irStudy/claude (fallback)

        Args:
            rag_service: RAG service for citation enrichment (Phase 2)
                        If None, creates default RAGService instance

        Raises:
            ValueError: If Claude API key not found in Vault
        """
        self.model = "claude-3-5-sonnet-20250219"
        self.temperature = 0.3  # Moderate creativity for educational content
        self.max_tokens = 1024  # Sufficient for 3-5 learning points

        # Get API key from Vault (NEVER hardcoded)
        self.api_key = self._get_api_key()

        if not self.api_key:
            raise ValueError(
                "Claude API key not found in Vault. "
                "Expected path: secret/ai-osce/claude-api-key or irStudy/claude"
            )

        # Initialize Anthropic client
        self.client = Anthropic(api_key=self.api_key)

        # Initialize RAG service (Phase 2)
        self.rag_service = rag_service or RAGService()

        logger.info("✅ Study Card Generator initialized with Claude 3.5 Sonnet + RAG service")

    def _get_api_key(self) -> Optional[str]:
        """
        Retrieve Claude API key from Vault.

        Tries multiple Vault paths for compatibility:
        1. secret/ai-osce/claude-api-key (primary - AI OSCE specific)
        2. irStudy/claude (fallback - shared project key)

        Returns:
            str: Claude API key
            None: If not found in Vault

        Security:
            - NEVER returns hardcoded values
            - NEVER logs API key
            - NEVER falls back to environment variables (Vault only)
        """
        try:
            api_key = get_vault_secret("secret/ai-osce/claude-api-key", "value")
            logger.info("✅ Claude API key retrieved from Vault (secret/ai-osce/claude-api-key)")
            return api_key
        except Exception as e1:
            logger.warning(f"⚠️  Primary Vault path failed: {e1}")

            try:
                api_key = get_vault_secret("irStudy/claude", "api_key")
                logger.info("✅ Claude API key retrieved from Vault (irStudy/claude)")
                return api_key
            except Exception as e2:
                logger.error(f"❌ Fallback Vault path failed: {e2}")
                return None

    async def _extract_learning_points(
        self,
        feedback: str,
        strengths: str,
        areas_for_improvement: str,
        persona_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Extract 3-5 key learning points from OSCE feedback using Claude API.

        Learning points prioritize areas for improvement (2-3 points) with
        1-2 strength reinforcement points. Each point is a candidate for
        a study card in Phase 2.

        Args:
            feedback: Overall feedback text from AI Examiner
            strengths: What student did well
            areas_for_improvement: What student should improve
            persona_context: Optional patient context (age, gender, chief_complaint, specialty)

        Returns:
            List of learning point dicts with structure:
            [
                {
                    "topic": "Diabetes history taking - dietary patterns",
                    "category": "improvement",  # or "strength"
                    "priority": "high",  # high/medium/low
                    "clinical_context": "52F Type 2 Diabetes, HbA1c 8.5%"
                },
                ...
            ]

        Raises:
            APIError: If Claude API call fails
            ValueError: If feedback is empty or invalid

        Australian Standards:
            - Uses paracetamol (NOT acetaminophen)
            - Uses eTG, RACGP references (NOT UpToDate)
            - Uses mmol/L for glucose (NOT mg/dL)

        Example:
            >>> generator = StudyCardGenerator()
            >>> points = await generator._extract_learning_points(
            ...     feedback="Good communication, but missed key history elements",
            ...     strengths="Excellent rapport building",
            ...     areas_for_improvement="Explore dietary patterns, medication adherence"
            ... )
            >>> len(points)
            4  # 2-3 improvements + 1-2 strengths
        """
        # Validation
        if not feedback and not areas_for_improvement:
            raise ValueError(
                "Cannot extract learning points - feedback and areas_for_improvement are both empty"
            )

        # Build clinical context string
        context_str = ""
        if persona_context:
            age = persona_context.get('age', 'adult')
            gender = persona_context.get('gender', 'patient')
            complaint = persona_context.get('chief_complaint', 'general consultation')
            specialty = persona_context.get('specialty', 'General Practice')

            context_str = f"\n\nPatient Context:\n- {age}y {gender}, {complaint}\n- Specialty: {specialty}"

        # Build prompt for Claude
        prompt = f"""You are an educational content specialist creating flashcards for medical students preparing for Australian medical exams (AMC Clinical Examination).

Analyze this OSCE feedback and extract 3-5 key learning points that should become flashcards:

OSCE Feedback:
- Overall: {feedback}
- Strengths: {strengths}
- Areas for Improvement: {areas_for_improvement}{context_str}

REQUIREMENTS:
1. Extract 2-3 learning points from "Areas for Improvement" (priority: high)
2. Extract 1-2 learning points from "Strengths" for reinforcement (priority: medium)
3. Each point should be specific and actionable
4. Focus on Australian medical standards (eTG, RACGP, AMH guidelines)
5. Use Australian terminology:
   - paracetamol (NOT acetaminophen)
   - mmol/L (NOT mg/dL)
   - 000 for emergency (NOT 911)

Return JSON array with exactly this structure:
[
  {{
    "topic": "Specific topic with clinical context",
    "category": "improvement" or "strength",
    "priority": "high" or "medium" or "low",
    "clinical_context": "Brief patient context if applicable"
  }}
]

EXAMPLE OUTPUT:
[
  {{
    "topic": "Diabetes history taking - explore dietary patterns in detail",
    "category": "improvement",
    "priority": "high",
    "clinical_context": "52F Type 2 Diabetes management"
  }},
  {{
    "topic": "Medication adherence assessment using open-ended questions",
    "category": "improvement",
    "priority": "high",
    "clinical_context": "Chronic disease management"
  }},
  {{
    "topic": "Rapport building - effective use of empathy statements",
    "category": "strength",
    "priority": "medium",
    "clinical_context": "General communication skill"
  }}
]

Return ONLY valid JSON array, no other text."""

        try:
            # Call Claude API
            logger.info("🤖 Calling Claude API for learning point extraction...")
            message = await self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # Extract response text
            response_text = message.content[0].text
            logger.info(f"✅ Claude API response received ({len(response_text)} chars)")

            # Parse JSON response
            learning_points = json.loads(response_text)

            # Validation
            if not isinstance(learning_points, list):
                raise ValueError(f"Expected list, got {type(learning_points)}")

            if len(learning_points) < 3 or len(learning_points) > 5:
                logger.warning(
                    f"⚠️  Expected 3-5 learning points, got {len(learning_points)}. "
                    f"Adjusting to valid range."
                )
                # Trim to 5 if too many
                if len(learning_points) > 5:
                    learning_points = learning_points[:5]
                # Error if too few
                elif len(learning_points) < 3:
                    raise ValueError(
                        f"Insufficient learning points extracted: {len(learning_points)} "
                        f"(minimum 3 required)"
                    )

            # Validate structure
            for i, point in enumerate(learning_points):
                if not isinstance(point, dict):
                    raise ValueError(f"Learning point {i} is not a dict: {point}")

                required_fields = ['topic', 'category', 'priority']
                for field in required_fields:
                    if field not in point:
                        raise ValueError(f"Learning point {i} missing field: {field}")

                # Validate category
                if point['category'] not in ['improvement', 'strength']:
                    raise ValueError(
                        f"Learning point {i} has invalid category: {point['category']} "
                        f"(must be 'improvement' or 'strength')"
                    )

                # Validate priority
                if point['priority'] not in ['high', 'medium', 'low']:
                    raise ValueError(
                        f"Learning point {i} has invalid priority: {point['priority']} "
                        f"(must be 'high', 'medium', or 'low')"
                    )

            # Check distribution (2-3 improvements, 1-2 strengths)
            improvements = [p for p in learning_points if p['category'] == 'improvement']
            strengths_points = [p for p in learning_points if p['category'] == 'strength']

            logger.info(
                f"📊 Learning points extracted: {len(improvements)} improvements, "
                f"{len(strengths_points)} strengths"
            )

            if len(improvements) < 2:
                logger.warning(
                    f"⚠️  Expected ≥2 improvement points, got {len(improvements)}"
                )

            return learning_points

        except APIError as e:
            logger.error(f"❌ Claude API error: {e}")
            raise APIError(
                f"Failed to extract learning points from feedback: {e}"
            ) from e
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON parsing error: {e}")
            logger.error(f"Response text: {response_text}")
            raise ValueError(
                f"Claude API returned invalid JSON: {e}"
            ) from e
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            raise

    async def _generate_qa_pairs(self, learning_points: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate Q&A pairs from learning points using Claude API (parallel execution).

        Uses async/await to call Claude API in parallel for all learning points,
        optimizing performance (<8 seconds target for 3-5 cards).

        Args:
            learning_points: List of learning point dicts from _extract_learning_points

        Returns:
            List of Q&A pair dicts with structure:
            [
                {
                    "question": "What are the key dietary patterns to explore in diabetes history?",
                    "answer": "Comprehensive dietary assessment including carbohydrate intake, ...",
                    "learning_point": "Diabetes history taking - explore dietary patterns in detail",
                    "category": "improvement",
                    "priority": "high"
                },
                ...
            ]

        Raises:
            APIError: If Claude API call fails
            ValueError: If no valid Q&A pairs generated

        Performance:
            - Parallel API calls (3-5 simultaneous)
            - Target: <3 seconds for 3 cards, <5 seconds for 5 cards

        Example:
            >>> points = [{"topic": "Dietary assessment", "category": "improvement", "priority": "high"}]
            >>> qa_pairs = await generator._generate_qa_pairs(points)
            >>> len(qa_pairs)
            1
            >>> "question" in qa_pairs[0]
            True
        """
        # Create async tasks for parallel execution
        tasks = [self._generate_single_qa_pair(point) for point in learning_points]

        # Execute all API calls in parallel
        qa_pairs = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out errors (return_exceptions=True prevents one failure from breaking all)
        valid_pairs = [pair for pair in qa_pairs if not isinstance(pair, Exception)]

        # Log errors
        errors = [pair for pair in qa_pairs if isinstance(pair, Exception)]
        if errors:
            logger.error(f"❌ Failed to generate {len(errors)}/{len(learning_points)} Q&A pairs: {errors}")

        if not valid_pairs:
            raise ValueError(
                f"No valid Q&A pairs generated from {len(learning_points)} learning points. "
                f"All {len(errors)} API calls failed."
            )

        logger.info(f"✅ Generated {len(valid_pairs)}/{len(learning_points)} Q&A pairs in parallel")

        return valid_pairs

    async def _generate_single_qa_pair(self, learning_point: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate single Q&A pair from learning point (helper for parallel execution).

        Args:
            learning_point: Dict with keys: topic, category, priority, clinical_context

        Returns:
            Dict with keys: question, answer, learning_point, category, priority

        Raises:
            APIError: If Claude API call fails
            ValueError: If response is invalid

        Australian Standards:
            - Uses paracetamol (NOT acetaminophen)
            - Uses mmol/L (NOT mg/dL)
            - References eTG, RACGP, AMH (NOT US sources)
        """
        topic = learning_point.get('topic', '')
        category = learning_point.get('category', 'improvement')
        priority = learning_point.get('priority', 'medium')
        clinical_context = learning_point.get('clinical_context', '')

        # Build prompt for Claude
        prompt = f"""You are an educational content specialist creating flashcards for medical students preparing for Australian medical exams (AMC Clinical Examination).

Create a clinical question-answer pair for this learning point:

LEARNING POINT:
- Topic: {topic}
- Category: {category} (strength to reinforce or improvement area)
- Clinical Context: {clinical_context}

REQUIREMENTS:
1. Question should be specific and clinical (NOT generic)
2. Answer should be evidence-based with Australian guidelines (eTG, RACGP, AMH)
3. Use Australian terminology:
   - paracetamol (NOT acetaminophen)
   - mmol/L (NOT mg/dL)
   - 000 for emergency (NOT 911)
4. Target AMC Clinical Examination standard
5. Length: Question 15-30 words, Answer 50-100 words

Return JSON object with exactly this structure:
{{
  "question": "Specific clinical question about the learning point",
  "answer": "Evidence-based answer with Australian guideline references (eTG/RACGP/AMH)"
}}

EXAMPLE OUTPUT:
{{
  "question": "What are the key dietary patterns to explore when taking a history from a patient with Type 2 Diabetes?",
  "answer": "Explore carbohydrate intake patterns (total amount, timing, types), meal frequency and portion sizes, alcohol consumption, and nutritional knowledge. Assess barriers to healthy eating (cost, cultural preferences, cooking skills). Use open-ended questions to understand current diet. Reference eTG Diabetes Management guidelines for dietary counselling approaches."
}}

Return ONLY valid JSON object, no other text."""

        try:
            # Call Claude API
            logger.info(f"🤖 Generating Q&A for: {topic}")
            message = await self.client.messages.create(
                model=self.model,
                max_tokens=512,  # Shorter for single Q&A
                temperature=self.temperature,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # Extract response text
            response_text = message.content[0].text
            logger.info(f"✅ Claude API response received for: {topic[:50]}...")

            # Parse JSON response
            qa_data = json.loads(response_text)

            # Validation
            if not isinstance(qa_data, dict):
                raise ValueError(f"Expected dict, got {type(qa_data)}")

            if 'question' not in qa_data or 'answer' not in qa_data:
                raise ValueError(f"Missing required fields: {qa_data.keys()}")

            # Add learning point metadata
            qa_pair = {
                "question": qa_data['question'],
                "answer": qa_data['answer'],
                "learning_point": topic,
                "category": category,
                "priority": priority
            }

            return qa_pair

        except APIError as e:
            logger.error(f"❌ Claude API error for topic '{topic}': {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON parsing error for topic '{topic}': {e}")
            logger.error(f"Response text: {response_text}")
            raise ValueError(f"Claude API returned invalid JSON: {e}") from e

    async def _enrich_with_citations(self, qa_pair: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich Q&A pair with RAG citations from Qdrant.

        Queries Qdrant using answer text to find relevant Australian medical sources.
        Filters by confidence ≥0.65 and ensures all citations have qdrant_point_id.

        Args:
            qa_pair: Dict with keys: question, answer, learning_point

        Returns:
            Dict with added "citations" key containing list of citations:
            {
                ...(original qa_pair fields),
                "citations": [
                    {
                        "source": "Talley & O'Connor Clinical Examination 9th Ed",
                        "qdrant_point_id": "550e8400-e29b-41d4-a716-446655440000",
                        "confidence": 0.85,
                        "is_australian": True,
                        "title": "Talley & O'Connor Clinical Examination",
                        "author": "Talley N, O'Connor S",
                        "year": "2023",
                        "page": 412
                    },
                    ...
                ]
            }

        Raises:
            Exception: If RAG query fails (logged but not raised - graceful degradation)

        Citation Requirements (constraints/11):
            - Confidence ≥0.65 (ZERO tolerance)
            - All citations MUST have qdrant_point_id (UUID)
            - Australian sources prioritized (≥60% target)

        Example:
            >>> qa_pair = {"question": "What is SOCRATES?", "answer": "Pain assessment framework"}
            >>> enriched = await generator._enrich_with_citations(qa_pair)
            >>> len(enriched["citations"])
            3
            >>> enriched["citations"][0]["qdrant_point_id"]
            "550e8400-e29b-41d4-a716-446655440000"
        """
        try:
            # Query Qdrant using answer text
            query_text = qa_pair["answer"]
            raw_results = self.rag_service.search_similar(
                query_text=query_text,
                limit=5,  # Top 5 results
                confidence_threshold=0.65  # From constraints/11
            )

            # Filter and format citations
            citations = []
            australian_sources = ["eTG", "AMH", "RACGP", "Talley", "AMC", "Australian", "Therapeutic Guidelines"]

            for result in raw_results:
                # Ensure qdrant_point_id exists (MANDATORY per constraints/11)
                if not result.get("qdrant_point_id"):
                    logger.warning(f"⚠️  Skipping citation without qdrant_point_id: {result.get('source')}")
                    continue  # Skip invalid citations

                # Double-check confidence threshold (belt-and-suspenders)
                if result.get("score", 0) < 0.65:
                    logger.warning(f"⚠️  Skipping low-confidence citation: {result.get('score')}")
                    continue

                # Check if source is Australian
                source = result.get("source", "")
                title = result.get("title", "")
                is_australian = any(aus in source for aus in australian_sources) or \
                               any(aus in title for aus in australian_sources)

                citation = {
                    "source": source,
                    "qdrant_point_id": str(result["qdrant_point_id"]),  # UUID as string
                    "confidence": float(result["score"]),
                    "is_australian": is_australian,
                    "title": title,
                    "author": result.get("author", ""),
                    "year": result.get("year", ""),
                    "page": result.get("page", 0)
                }
                citations.append(citation)

            # Validate Australian source ratio
            if citations:
                aus_ratio = sum(c["is_australian"] for c in citations) / len(citations)
                if aus_ratio < 0.60:
                    logger.warning(
                        f"⚠️  Australian source ratio {aus_ratio:.1%} below 60% target "
                        f"for learning point: {qa_pair.get('learning_point', '')[:50]}"
                    )
                else:
                    logger.info(f"✅ Australian source ratio: {aus_ratio:.1%} (target: ≥60%)")

            # Add citations to Q&A pair
            qa_pair["citations"] = citations
            logger.info(f"✅ Enriched Q&A with {len(citations)} citations (confidence ≥0.65)")

            return qa_pair

        except Exception as e:
            # Graceful degradation - log error but don't fail
            logger.error(f"❌ Failed to enrich citations for Q&A: {e}")
            logger.warning("⚠️  Continuing with empty citations (graceful degradation)")
            qa_pair["citations"] = []
            return qa_pair

    async def _validate_content_substance(self, qa_pair: Dict[str, Any]) -> bool:
        """
        Validate Q&A pair contains substantive content (no placeholders).

        Checks for forbidden placeholder patterns per constraints/12.
        Rejects content with generic templates, Lorem ipsum, etc.

        Args:
            qa_pair: Dict with keys: question, answer

        Returns:
            True if content is substantive, False if placeholders detected

        Forbidden Patterns (constraints/12):
            - "Lorem ipsum"
            - "[Insert"
            - "TODO"
            - "..."
            - "etc."
            - "TBD"
            - Generic templates like "Clinical scenario for {topic}"

        Example:
            >>> qa_pair = {"question": "What is SOCRATES?", "answer": "[Insert answer here]"}
            >>> is_valid = await generator._validate_content_substance(qa_pair)
            >>> print(is_valid)
            False
        """
        # Forbidden patterns (from constraints/12)
        forbidden_patterns = [
            "lorem ipsum",
            "[insert",
            "todo",
            "tbd",
            "...",  # Ellipsis (often indicates incomplete content)
            "etc.",
            "[placeholder",
            "[example",
            "clinical scenario for",
            "question stem about",
            "option a", "option b", "option c", "option d",
            "explanation for",
            "key points for"
        ]

        # Check question and answer
        combined_text = f"{qa_pair['question']} {qa_pair['answer']}".lower()

        for pattern in forbidden_patterns:
            if pattern in combined_text:
                logger.warning(
                    f"⚠️  Placeholder detected in Q&A: '{pattern}' found. "
                    f"Question: {qa_pair['question'][:50]}..."
                )
                return False

        # Check minimum length (substantive content should be >20 chars)
        if len(qa_pair["answer"]) < 20:
            logger.warning(f"⚠️  Answer too short (<20 chars): {qa_pair['answer']}")
            return False

        if len(qa_pair["question"]) < 10:
            logger.warning(f"⚠️  Question too short (<10 chars): {qa_pair['question']}")
            return False

        # Check for Australian context in answer (best effort - not mandatory)
        australian_markers = [
            'australian', 'etg', 'racgp', 'amh', 'pbs', 'ahpra',
            'therapeutic guidelines', 'talley', 'amc'
        ]
        if not any(marker in qa_pair["answer"].lower() for marker in australian_markers):
            logger.info(
                f"ℹ️  No explicit Australian context in answer (acceptable but not ideal): "
                f"{qa_pair.get('learning_point', '')[:50]}..."
            )

        return True

    def _create_study_card(
        self,
        user_id: int,
        session_id: str,
        qa_pair: Dict[str, Any],
        persona_code: Optional[str] = None
    ) -> StudyCard:
        """
        Create StudyCard object with SM-2 initialization.

        Args:
            user_id: User ID
            session_id: OSCE session UUID
            qa_pair: Dict with keys: question, answer, citations, learning_point, category, priority
            persona_code: Optional persona code for card_id generation

        Returns:
            StudyCard object (not yet committed to database)

        SM-2 Initialization (MANDATORY):
            - ease_factor: 2.5 (default per SM-2 algorithm)
            - interval_days: 1 (first review tomorrow)
            - repetitions: 0 (no reviews yet)
            - next_review_date: NOW (available immediately)

        Example:
            >>> qa_pair = {
            ...     "question": "What is SOCRATES?",
            ...     "answer": "Pain assessment framework covering Site, Onset...",
            ...     "citations": [{"source": "eTG", "qdrant_point_id": "uuid", "confidence": 0.85}],
            ...     "learning_point": "Use SOCRATES for pain assessment",
            ...     "category": "improvement",
            ...     "priority": "high"
            ... }
            >>> card = generator._create_study_card(user_id=42, session_id="uuid", qa_pair=qa_pair)
            >>> print(card.ease_factor, card.interval_days, card.repetitions)
            2.5 1 0
        """
        now = datetime.utcnow()

        # Generate card_id (will be replaced by auto-generated ID after commit)
        # Using timestamp for uniqueness
        card_id_suffix = str(int(time.time() * 1000))[-8:]  # Last 8 digits of millisecond timestamp
        card_id = f"OSCE-{persona_code or 'GEN'}-{card_id_suffix}"

        # Extract topic from learning_point for specialty/topic fields
        learning_point = qa_pair.get("learning_point", "General medical knowledge")

        # Default values (StudyCard model doesn't have all required fields from models.py)
        # We'll use minimal fields that exist in the model
        card = StudyCard(
            user_id=user_id,
            card_id=card_id,

            # Content fields
            question=qa_pair["question"],
            answer=qa_pair["answer"],
            explanation=f"Learning point: {learning_point}",

            # Citations (JSONB field)
            citations=qa_pair.get("citations", []),

            # Metadata (StudyCard model has these fields)
            # specialty and topic are required - extract from learning_point
            specialty="general_practice",  # Default (will be enhanced in Phase 4)
            topic=learning_point[:255],  # Truncate to field limit
            subtopic=qa_pair.get("category", "improvement"),

            # SM-2 parameters (MANDATORY defaults per SM-2 algorithm)
            ease_factor=2.5,  # Default ease factor per SM-2 spec
            interval_days=1,  # First review is tomorrow
            repetitions=0,    # No reviews yet
            next_review_date=now,  # Available immediately for first review

            # Timestamps
            created_at=now,
            updated_at=now,

            # Flags
            is_active=True
        )

        logger.info(
            f"✅ Created StudyCard: '{card.question[:50]}...' "
            f"(SM-2: ease={card.ease_factor}, interval={card.interval_days}, reps={card.repetitions})"
        )

        return card

    async def generate_cards_from_session(
        self,
        session_id: str,
        user_id: int,
        db: Any  # SQLAlchemy Session
    ) -> List[StudyCard]:
        """
        Generate study cards from completed OSCE session (PHASE 3 - FULL IMPLEMENTATION).

        Full pipeline implementation:
        1. Fetch OSCE session data from database (validate ownership)
        2. Extract learning points from feedback (Phase 1)
        3. Generate Q&A pairs with Claude API (Phase 2)
        4. Enrich with RAG citations (Phase 2)
        5. Validate content substance (Phase 2)
        6. Create StudyCard objects with SM-2 initialization (Phase 3)
        7. Batch insert to database (Phase 3)

        Args:
            session_id: OSCE attempt_id (UUID string)
            user_id: User who owns the session
            db: SQLAlchemy database session

        Returns:
            List of StudyCard objects with populated IDs

        Raises:
            ValueError: If session_id or user_id invalid
            SessionNotFoundError: If session doesn't exist or user doesn't own it
            IntegrityError: If database insertion fails

        Performance:
            - Target: <8 seconds for 3-5 cards
            - Uses async/await for parallel Claude API calls
            - Batch database insertion (single commit)
            - Performance logged per step

        Example:
            >>> generator = StudyCardGenerator()
            >>> cards = await generator.generate_cards_from_session(
            ...     session_id="9d76cd2a-5ad0-4e01-835a-3ce995023367",
            ...     user_id=123,
            ...     db=db_session
            ... )
            >>> len(cards)
            3  # 3-5 cards generated
            >>> cards[0].ease_factor
            2.5
        """
        start_time = time.time()
        logger.info(f"🚀 Starting card generation for session {session_id} (user {user_id})")

        # Validation
        if not session_id:
            raise ValueError("session_id is required")

        if not user_id or user_id <= 0:
            raise ValueError(f"Invalid user_id: {user_id} (must be positive integer)")

        if not db:
            raise ValueError("Database session is required")

        try:
            # Step 1: Fetch session data (validate ownership)
            step_start = time.time()
            session = db.query(OSCEAttemptAI).filter(
                OSCEAttemptAI.attempt_id == session_id,
                OSCEAttemptAI.user_id == user_id  # Validate ownership
            ).first()

            if not session:
                raise ValueError(
                    f"Session {session_id} not found for user {user_id}. "
                    f"Either session doesn't exist or user doesn't own it."
                )

            # Extract feedback from session
            # OSCEAttemptAI stores feedback in ai_feedback field (JSONB)
            ai_feedback = session.ai_feedback or {}
            feedback_text = ai_feedback.get("overall_feedback", "")
            strengths = ai_feedback.get("strengths", "")
            areas_for_improvement = ai_feedback.get("areas_for_improvement", "")

            if not feedback_text and not areas_for_improvement:
                raise ValueError(
                    f"Session {session_id} has no AI feedback. "
                    f"Ensure session is complete and scored before generating cards."
                )

            # Get persona context for better learning point extraction
            persona = session.persona if hasattr(session, 'persona') else None
            persona_context = None
            persona_code = None

            if persona:
                persona_code = getattr(persona, 'persona_code', None)
                persona_context = {
                    'age': getattr(persona, 'age', None),
                    'gender': getattr(persona, 'gender', None),
                    'chief_complaint': getattr(persona, 'chief_complaint', None),
                    'specialty': getattr(persona, 'specialty', None)
                }

            logger.info(f"Step 1 (fetch session): {time.time() - step_start:.2f}s")

            # Step 2: Extract learning points (Phase 1)
            step_start = time.time()
            learning_points = await self._extract_learning_points(
                feedback=feedback_text,
                strengths=strengths,
                areas_for_improvement=areas_for_improvement,
                persona_context=persona_context
            )
            logger.info(
                f"Step 2 (extract {len(learning_points)} learning points): "
                f"{time.time() - step_start:.2f}s"
            )

            # Step 3: Generate Q&A pairs (Phase 2 - parallel Claude API calls)
            step_start = time.time()
            qa_pairs = await self._generate_qa_pairs(learning_points)
            logger.info(
                f"Step 3 (generate {len(qa_pairs)} Q&A pairs): "
                f"{time.time() - step_start:.2f}s"
            )

            # Step 4: Enrich with citations (Phase 2)
            step_start = time.time()
            enriched_pairs = []
            for qa_pair in qa_pairs:
                enriched = await self._enrich_with_citations(qa_pair)
                enriched_pairs.append(enriched)
            logger.info(f"Step 4 (enrich citations): {time.time() - step_start:.2f}s")

            # Step 5: Validate content (Phase 2)
            step_start = time.time()
            valid_pairs = []
            for pair in enriched_pairs:
                is_valid = await self._validate_content_substance(pair)
                if is_valid:
                    valid_pairs.append(pair)
                else:
                    logger.warning(
                        f"⚠️  Rejected card (placeholder content): {pair['question'][:50]}..."
                    )
            logger.info(
                f"Step 5 (validate {len(valid_pairs)}/{len(enriched_pairs)} cards): "
                f"{time.time() - step_start:.2f}s"
            )

            if not valid_pairs:
                raise ValueError(
                    f"No valid study cards generated from session {session_id}. "
                    f"All {len(enriched_pairs)} cards failed validation (placeholder content)."
                )

            # Step 6: Create StudyCard objects (Phase 3)
            step_start = time.time()
            study_cards = []
            for qa_pair in valid_pairs:
                card = self._create_study_card(
                    user_id=user_id,
                    session_id=session_id,
                    qa_pair=qa_pair,
                    persona_code=persona_code
                )
                study_cards.append(card)
            logger.info(
                f"Step 6 (create {len(study_cards)} StudyCard objects): "
                f"{time.time() - step_start:.2f}s"
            )

            # Step 7: Batch insert to database (SINGLE commit for performance)
            step_start = time.time()
            db.add_all(study_cards)  # Batch add (not individual db.add() calls)
            db.commit()  # Single commit for all cards

            # Refresh to get auto-generated IDs
            for card in study_cards:
                db.refresh(card)

            logger.info(f"Step 7 (batch insert): {time.time() - step_start:.2f}s")

            # Log total performance
            total_time = time.time() - start_time
            logger.info(
                f"✅ Total card generation time: {total_time:.2f}s "
                f"(target: <8s, cards generated: {len(study_cards)})"
            )

            if total_time > 8.0:
                logger.warning(
                    f"⚠️  Performance target exceeded: {total_time:.2f}s > 8.0s "
                    f"(may need optimization)"
                )

            return study_cards

        except IntegrityError as e:
            db.rollback()
            logger.error(f"❌ Database integrity error during card creation: {e}")
            raise ValueError(f"Failed to create study cards (database error): {e}") from e

        except Exception as e:
            db.rollback()
            logger.error(f"❌ Unexpected error during card generation: {e}")
            raise
