"""
Unit Tests for Study Card Generator
PRD-P1-005 Phase 1: Database Migration + Core Generator Structure

TDD Approach:
1. Tests written FIRST
2. Expected initial result: Tests fail (RED phase) until implementation complete
3. After implementation: Tests pass (GREEN phase)

Test Coverage:
- Vault integration (API key retrieval)
- Learning point extraction (Claude API)
- Edge cases (empty feedback, API errors)
- Input validation
- Australian medical standards
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
import json

from src.ai.study_card_generator import StudyCardGenerator


@pytest.fixture
def mock_vault():
    """Mock Vault client that returns test API key"""
    with patch('src.ai.study_card_generator.get_vault_secret') as mock_get_secret:
        mock_get_secret.return_value = "test-api-key-from-vault"
        # Also mock Anthropic client initialization to avoid httpx version issues
        with patch('src.ai.study_card_generator.Anthropic') as mock_anthropic:
            mock_client = MagicMock()
            mock_anthropic.return_value = mock_client
            yield mock_get_secret


@pytest.fixture
def mock_claude_response():
    """Mock successful Claude API response with learning points"""
    return [
        {
            "topic": "Diabetes history taking - explore dietary patterns in detail",
            "category": "improvement",
            "priority": "high",
            "clinical_context": "52F Type 2 Diabetes management"
        },
        {
            "topic": "Medication adherence assessment using open-ended questions",
            "category": "improvement",
            "priority": "high",
            "clinical_context": "Chronic disease management"
        },
        {
            "topic": "Red flag screening for diabetic complications",
            "category": "improvement",
            "priority": "high",
            "clinical_context": "Diabetes complications screening"
        },
        {
            "topic": "Rapport building - effective use of empathy statements",
            "category": "strength",
            "priority": "medium",
            "clinical_context": "General communication skill"
        }
    ]


class TestStudyCardGeneratorInitialization:
    """Test suite for StudyCardGenerator initialization"""

    def test_study_card_generator_initializes_with_vault_key(self, mock_vault):
        """Test StudyCardGenerator initializes with Vault API key (NO hardcoded credentials)"""
        generator = StudyCardGenerator()

        # Verify Vault was called for API key
        mock_vault.assert_called()

        # Verify generator initialized correctly
        assert generator.client is not None
        assert generator.model == "claude-3-5-sonnet-20250219"
        assert generator.temperature == 0.3  # Moderate creativity for educational content
        assert generator.max_tokens == 1024

    def test_no_hardcoded_api_key(self, mock_vault):
        """Test that API key comes from Vault, NOT hardcoded"""
        generator = StudyCardGenerator()
        assert generator.api_key == "test-api-key-from-vault"

    def test_raises_error_if_vault_key_missing(self):
        """Test raises ValueError if Vault API key not found"""
        with patch('src.ai.study_card_generator.get_vault_secret') as mock_vault:
            mock_vault.side_effect = Exception("Vault key not found")

            with pytest.raises(ValueError, match="Claude API key not found in Vault"):
                StudyCardGenerator()


class TestLearningPointExtraction:
    """Test suite for learning point extraction from OSCE feedback"""

    @pytest.mark.asyncio
    async def test_extract_learning_points_from_feedback(self, mock_vault, mock_claude_response):
        """Test that 3-5 learning points are extracted from OSCE feedback"""
        generator = StudyCardGenerator()

        # Mock Claude API response
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text=json.dumps(mock_claude_response))]

        with patch.object(generator.client.messages, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_message

            # Call extraction method
            points = await generator._extract_learning_points(
                feedback="Good communication, but missed key history elements",
                strengths="Excellent rapport building, clear explanations",
                areas_for_improvement="Explore dietary patterns, medication adherence, screen for complications"
            )

            # Assertions
            assert len(points) >= 3, "Should extract at least 3 learning points"
            assert len(points) <= 5, "Should extract at most 5 learning points"

            # Check distribution: 2-3 improvements, 1-2 strengths
            improvements = [p for p in points if p['category'] == 'improvement']
            strengths = [p for p in points if p['category'] == 'strength']

            assert len(improvements) >= 2, "Should have at least 2 improvement points"
            assert len(strengths) >= 1, "Should have at least 1 strength point"

            # Validate structure
            for point in points:
                assert 'topic' in point, "Each point should have a topic"
                assert 'category' in point, "Each point should have a category"
                assert 'priority' in point, "Each point should have a priority"
                assert point['category'] in ['improvement', 'strength']
                assert point['priority'] in ['high', 'medium', 'low']

            # Verify Claude API was called with correct parameters
            mock_create.assert_called_once()
            call_kwargs = mock_create.call_args[1]
            assert call_kwargs['model'] == "claude-3-5-sonnet-20250219"
            assert call_kwargs['temperature'] == 0.3
            assert call_kwargs['max_tokens'] == 1024

    @pytest.mark.asyncio
    async def test_extract_learning_points_handles_empty_feedback(self, mock_vault):
        """Test extraction raises ValueError when feedback is empty"""
        generator = StudyCardGenerator()

        with pytest.raises(ValueError, match="feedback and areas_for_improvement are both empty"):
            await generator._extract_learning_points(
                feedback="",
                strengths="",
                areas_for_improvement=""
            )

    @pytest.mark.asyncio
    async def test_extract_learning_points_handles_api_error(self, mock_vault):
        """Test extraction handles Claude API errors gracefully"""
        generator = StudyCardGenerator()

        # Mock Claude API error (use generic Exception instead of APIError due to constructor complexity)
        with patch.object(generator.client.messages, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.side_effect = Exception("API rate limit exceeded")

            with pytest.raises(Exception):
                await generator._extract_learning_points(
                    feedback="Good session",
                    strengths="Excellent",
                    areas_for_improvement="Minor improvements needed"
                )

    @pytest.mark.asyncio
    async def test_extract_learning_points_with_persona_context(self, mock_vault, mock_claude_response):
        """Test extraction includes patient persona context in prompt"""
        generator = StudyCardGenerator()

        # Mock Claude API response
        mock_message = MagicMock()
        mock_message.content = [MagicMock(text=json.dumps(mock_claude_response))]

        with patch.object(generator.client.messages, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_message

            persona_context = {
                'age': 52,
                'gender': 'Female',
                'chief_complaint': 'Type 2 Diabetes',
                'specialty': 'General Practice'
            }

            points = await generator._extract_learning_points(
                feedback="Good overall",
                strengths="Good rapport",
                areas_for_improvement="More detailed history",
                persona_context=persona_context
            )

            # Verify Claude API was called
            mock_create.assert_called_once()

            # Verify prompt includes persona context
            call_kwargs = mock_create.call_args[1]
            messages = call_kwargs['messages']
            prompt = messages[0]['content']

            assert '52y Female' in prompt
            assert 'Type 2 Diabetes' in prompt
            assert 'General Practice' in prompt

    @pytest.mark.asyncio
    async def test_extract_learning_points_validates_australian_standards(self, mock_vault):
        """Test extraction uses Australian medical terminology (NOT US terms)"""
        generator = StudyCardGenerator()

        # Mock Claude API response with US terminology (should be rejected in production)
        us_terminology_response = [
            {
                "topic": "Use acetaminophen for pain management",  # ❌ WRONG - should be paracetamol
                "category": "improvement",
                "priority": "high",
                "clinical_context": "Pain management"
            },
            {
                "topic": "Monitor blood glucose in mg/dL",  # ❌ WRONG - should be mmol/L
                "category": "improvement",
                "priority": "high",
                "clinical_context": "Diabetes monitoring"
            },
            {
                "topic": "Call 911 for emergencies",  # ❌ WRONG - should be 000
                "category": "improvement",
                "priority": "high",
                "clinical_context": "Emergency care"
            }
        ]

        mock_message = MagicMock()
        mock_message.content = [MagicMock(text=json.dumps(us_terminology_response))]

        with patch.object(generator.client.messages, 'create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_message

            # Extract points (should pass validation even with US terms in response)
            # Note: Validation of Australian terminology in generated content is Phase 2
            points = await generator._extract_learning_points(
                feedback="Good session",
                strengths="Good",
                areas_for_improvement="Improve medication knowledge"
            )

            # Verify prompt instructs Claude to use Australian terminology
            call_kwargs = mock_create.call_args[1]
            messages = call_kwargs['messages']
            prompt = messages[0]['content']

            assert 'paracetamol' in prompt.lower()
            assert 'mmol/L' in prompt
            assert '000' in prompt
            assert 'Australian' in prompt or 'eTG' in prompt or 'RACGP' in prompt


class TestGenerateCardsFromSession:
    """Test suite for generate_cards_from_session (Phase 1 scaffold)"""

    @pytest.mark.asyncio
    async def test_generate_cards_validates_session_id(self, mock_vault):
        """Test generate_cards_from_session validates session_id is provided"""
        generator = StudyCardGenerator()
        mock_db = Mock()

        with pytest.raises(ValueError, match="session_id is required"):
            await generator.generate_cards_from_session(
                session_id="",  # ❌ Empty session_id
                user_id=123,
                db=mock_db
            )

    @pytest.mark.asyncio
    async def test_generate_cards_validates_user_id(self, mock_vault):
        """Test generate_cards_from_session validates user_id is valid"""
        generator = StudyCardGenerator()
        mock_db = Mock()

        with pytest.raises(ValueError, match="Invalid user_id"):
            await generator.generate_cards_from_session(
                session_id="9d76cd2a-5ad0-4e01-835a-3ce995023367",
                user_id=0,  # ❌ Invalid user_id
                db=mock_db
            )

    @pytest.mark.asyncio
    async def test_generate_cards_validates_db_session(self, mock_vault):
        """Test generate_cards_from_session validates database session is provided"""
        generator = StudyCardGenerator()

        with pytest.raises(ValueError, match="Database session is required"):
            await generator.generate_cards_from_session(
                session_id="9d76cd2a-5ad0-4e01-835a-3ce995023367",
                user_id=123,
                db=None  # ❌ No database session
            )

    # NOTE: Phase 1 test removed - Phase 3 now has full implementation
    # See TestPhase3FullPipeline for comprehensive integration tests


# ==============================================================================
# PHASE 2 TESTS: RAG Integration + Citation Validation
# ==============================================================================


class TestQAPairGeneration:
    """Test suite for Q&A pair generation (Phase 2)"""

    @pytest.mark.asyncio
    async def test_generate_qa_pairs_from_learning_points(self, mock_vault):
        """Test Q&A pairs generated from learning points with parallel Claude API calls"""
        generator = StudyCardGenerator()

        learning_points = [
            {
                "topic": "Diabetes history taking - explore dietary patterns",
                "category": "improvement",
                "priority": "high",
                "clinical_context": "52F Type 2 Diabetes"
            },
            {
                "topic": "Medication adherence assessment",
                "category": "improvement",
                "priority": "high",
                "clinical_context": "Chronic disease"
            },
            {
                "topic": "Rapport building with empathy",
                "category": "strength",
                "priority": "medium",
                "clinical_context": "Communication"
            }
        ]

        # Mock Claude API responses
        mock_responses = [
            {"question": "What dietary patterns should be explored in diabetes?", "answer": "Explore carbohydrate intake, meal timing, and portion sizes per eTG guidelines."},
            {"question": "How to assess medication adherence?", "answer": "Use open-ended questions about missed doses, barriers to adherence per RACGP guidelines."},
            {"question": "What are effective empathy statements?", "answer": "Use reflective listening and validation statements per AMC communication standards."}
        ]

        async def mock_single_qa(point):
            idx = learning_points.index(point)
            return {
                **mock_responses[idx],
                "learning_point": point["topic"],
                "category": point["category"],
                "priority": point["priority"]
            }

        with patch.object(generator, '_generate_single_qa_pair', side_effect=mock_single_qa):
            qa_pairs = await generator._generate_qa_pairs(learning_points)

            # Assertions
            assert len(qa_pairs) == 3, "Should generate Q&A for all 3 learning points"

            # Validate structure
            for qa in qa_pairs:
                assert 'question' in qa
                assert 'answer' in qa
                assert 'learning_point' in qa
                assert 'category' in qa
                assert 'priority' in qa

            # Validate parallel execution (all called)
            assert len(qa_pairs) == len(learning_points)

    @pytest.mark.asyncio
    async def test_generate_qa_pairs_handles_partial_failures(self, mock_vault):
        """Test Q&A generation handles partial API failures gracefully"""
        generator = StudyCardGenerator()

        learning_points = [
            {"topic": "Topic 1", "category": "improvement", "priority": "high"},
            {"topic": "Topic 2", "category": "improvement", "priority": "high"},
            {"topic": "Topic 3", "category": "improvement", "priority": "high"}
        ]

        # Mock: 2 succeed, 1 fails
        async def mock_single_qa(point):
            if point["topic"] == "Topic 2":
                raise Exception("API error")
            return {
                "question": f"Question for {point['topic']}",
                "answer": f"Answer for {point['topic']}",
                "learning_point": point["topic"],
                "category": point["category"],
                "priority": point["priority"]
            }

        with patch.object(generator, '_generate_single_qa_pair', side_effect=mock_single_qa):
            qa_pairs = await generator._generate_qa_pairs(learning_points)

            # Should get 2 valid pairs (Topic 1 and 3)
            assert len(qa_pairs) == 2, "Should return valid pairs despite 1 failure"
            assert all(qa["learning_point"] in ["Topic 1", "Topic 3"] for qa in qa_pairs)

    @pytest.mark.asyncio
    async def test_generate_qa_pairs_raises_if_all_fail(self, mock_vault):
        """Test Q&A generation raises error if ALL API calls fail"""
        generator = StudyCardGenerator()

        learning_points = [
            {"topic": "Topic 1", "category": "improvement", "priority": "high"}
        ]

        # Mock: All fail
        async def mock_single_qa(point):
            raise Exception("API error")

        with patch.object(generator, '_generate_single_qa_pair', side_effect=mock_single_qa):
            with pytest.raises(ValueError, match="No valid Q&A pairs generated"):
                await generator._generate_qa_pairs(learning_points)


class TestRAGCitationEnrichment:
    """Test suite for RAG citation enrichment (Phase 2)"""

    @pytest.mark.asyncio
    async def test_enrich_with_citations_queries_qdrant(self, mock_vault):
        """Test citation enrichment queries RAG service"""
        mock_rag = Mock()
        generator = StudyCardGenerator(rag_service=mock_rag)

        qa_pair = {
            "question": "What is SOCRATES framework?",
            "answer": "SOCRATES is a pain assessment framework covering Site, Onset, Character, Radiation, Associations, Time course, Exacerbating/relieving factors, Severity. Referenced in Talley & O'Connor Clinical Examination.",
            "learning_point": "Pain assessment"
        }

        # Mock RAG results
        mock_rag.search_similar.return_value = [
            {
                "source": "Talley & O'Connor Clinical Examination 9th Ed",
                "qdrant_point_id": "550e8400-e29b-41d4-a716-446655440000",
                "score": 0.85,
                "content": "SOCRATES mnemonic for pain assessment...",
                "page": 412,
                "title": "Talley & O'Connor Clinical Examination",
                "author": "Talley N, O'Connor S",
                "year": "2023"
            }
        ]

        enriched = await generator._enrich_with_citations(qa_pair)

        # Assertions
        assert 'citations' in enriched
        assert len(enriched['citations']) == 1
        assert enriched['citations'][0]['qdrant_point_id'] == "550e8400-e29b-41d4-a716-446655440000"
        assert enriched['citations'][0]['confidence'] == 0.85

        # Verify RAG was queried
        mock_rag.search_similar.assert_called_once_with(
            query_text=qa_pair["answer"],
            limit=5,
            confidence_threshold=0.65
        )

    @pytest.mark.asyncio
    async def test_enrich_filters_low_confidence_citations(self, mock_vault):
        """Test enrichment filters citations with confidence <0.65"""
        mock_rag = Mock()
        generator = StudyCardGenerator(rag_service=mock_rag)

        qa_pair = {
            "question": "Test question",
            "answer": "Test answer",
            "learning_point": "Test"
        }

        # Mock RAG results with low confidence
        mock_rag.search_similar.return_value = [
            {
                "source": "Source 1",
                "qdrant_point_id": "uuid-1",
                "score": 0.85,  # PASS
                "content": "Content 1",
                "page": 1,
                "title": "Title 1",
                "author": "Author 1",
                "year": "2023"
            },
            {
                "source": "Source 2",
                "qdrant_point_id": "uuid-2",
                "score": 0.52,  # FAIL (below 0.65)
                "content": "Content 2",
                "page": 2,
                "title": "Title 2",
                "author": "Author 2",
                "year": "2023"
            }
        ]

        enriched = await generator._enrich_with_citations(qa_pair)

        # Should only include high-confidence citation
        assert len(enriched['citations']) == 1
        assert enriched['citations'][0]['qdrant_point_id'] == "uuid-1"
        assert enriched['citations'][0]['confidence'] == 0.85

    @pytest.mark.asyncio
    async def test_enrich_prioritizes_australian_sources(self, mock_vault):
        """Test enrichment tracks Australian source ratio (≥60% target)"""
        mock_rag = Mock()
        generator = StudyCardGenerator(rag_service=mock_rag)

        qa_pair = {
            "question": "Test question",
            "answer": "Test answer with eTG reference",
            "learning_point": "Test"
        }

        # Mock RAG results: 3 Australian, 1 non-Australian
        mock_rag.search_similar.return_value = [
            {"source": "eTG Diabetes", "qdrant_point_id": "uuid-1", "score": 0.85, "content": "", "page": 1, "title": "Therapeutic Guidelines", "author": "eTG", "year": "2023"},
            {"source": "RACGP Guidelines", "qdrant_point_id": "uuid-2", "score": 0.80, "content": "", "page": 1, "title": "RACGP Red Book", "author": "RACGP", "year": "2023"},
            {"source": "Talley Clinical Exam", "qdrant_point_id": "uuid-3", "score": 0.75, "content": "", "page": 1, "title": "Talley & O'Connor", "author": "Talley", "year": "2023"},
            {"source": "UpToDate", "qdrant_point_id": "uuid-4", "score": 0.70, "content": "", "page": 1, "title": "UpToDate", "author": "UpToDate", "year": "2023"}
        ]

        enriched = await generator._enrich_with_citations(qa_pair)

        # Check Australian ratio
        australian_count = sum(c["is_australian"] for c in enriched['citations'])
        total_count = len(enriched['citations'])
        aus_ratio = australian_count / total_count

        assert aus_ratio >= 0.60, f"Australian ratio {aus_ratio:.1%} should be ≥60%"

    @pytest.mark.asyncio
    async def test_enrich_attaches_qdrant_point_ids(self, mock_vault):
        """Test all citations have qdrant_point_id (UUID format)"""
        mock_rag = Mock()
        generator = StudyCardGenerator(rag_service=mock_rag)

        qa_pair = {
            "question": "Test question",
            "answer": "Test answer",
            "learning_point": "Test"
        }

        # Mock RAG results
        mock_rag.search_similar.return_value = [
            {"source": "Source 1", "qdrant_point_id": "550e8400-e29b-41d4-a716-446655440000", "score": 0.85, "content": "", "page": 1, "title": "Title", "author": "Author", "year": "2023"},
            {"source": "Source 2", "qdrant_point_id": "550e8400-e29b-41d4-a716-446655440001", "score": 0.80, "content": "", "page": 1, "title": "Title", "author": "Author", "year": "2023"}
        ]

        enriched = await generator._enrich_with_citations(qa_pair)

        # All citations must have qdrant_point_id
        assert all('qdrant_point_id' in c for c in enriched['citations'])
        assert all(len(c['qdrant_point_id']) > 0 for c in enriched['citations'])

    @pytest.mark.asyncio
    async def test_enrich_graceful_degradation_on_rag_failure(self, mock_vault):
        """Test enrichment handles RAG service failures gracefully with fallback citation"""
        mock_rag = Mock()
        generator = StudyCardGenerator(rag_service=mock_rag)

        qa_pair = {
            "question": "Test question",
            "answer": "Test answer",
            "learning_point": "Test"
        }

        # Mock RAG failure
        mock_rag.search_similar.side_effect = Exception("Qdrant connection error")

        # Should not raise, instead return fallback citation
        enriched = await generator._enrich_with_citations(qa_pair)

        assert 'citations' in enriched
        assert len(enriched['citations']) >= 1  # Fallback citation provided
        assert enriched['citations'][0]['source'] == "ICRP OSCE Preparation Modules"


class TestContentValidation:
    """Test suite for content substance validation (Phase 2)"""

    @pytest.mark.asyncio
    async def test_validate_content_rejects_placeholders(self, mock_vault):
        """Test validation rejects placeholder content"""
        generator = StudyCardGenerator()

        # Test forbidden patterns
        test_cases = [
            {"question": "What is SOCRATES?", "answer": "[Insert answer here]"},
            {"question": "Lorem ipsum dolor sit amet", "answer": "Valid answer"},
            {"question": "Valid question", "answer": "TODO: Add content"},
            {"question": "Valid question", "answer": "TBD - to be determined"},
            {"question": "Valid question", "answer": "Answer with ellipsis..."},
        ]

        for qa_pair in test_cases:
            is_valid = await generator._validate_content_substance(qa_pair)
            assert is_valid is False, f"Should reject: {qa_pair}"

    @pytest.mark.asyncio
    async def test_validate_content_accepts_real_content(self, mock_vault):
        """Test validation accepts real clinical content"""
        generator = StudyCardGenerator()

        qa_pair = {
            "question": "What is the SOCRATES framework for pain assessment?",
            "answer": "SOCRATES is a systematic pain assessment framework covering Site, Onset, Character, Radiation, Associations, Time course, Exacerbating/relieving factors, and Severity. Referenced in Australian guidelines (eTG, Talley & O'Connor)."
        }

        is_valid = await generator._validate_content_substance(qa_pair)
        assert is_valid is True

    @pytest.mark.asyncio
    async def test_validate_content_rejects_short_answers(self, mock_vault):
        """Test validation rejects answers that are too short"""
        generator = StudyCardGenerator()

        qa_pair = {
            "question": "What is SOCRATES?",
            "answer": "Pain tool"  # Too short (<20 chars)
        }

        is_valid = await generator._validate_content_substance(qa_pair)
        assert is_valid is False

    @pytest.mark.asyncio
    async def test_validate_content_logs_warnings(self, mock_vault, caplog):
        """Test validation logs warnings for rejected content"""
        import logging
        caplog.set_level(logging.WARNING)

        generator = StudyCardGenerator()

        qa_pair = {
            "question": "Test question",
            "answer": "[Insert answer]"
        }

        await generator._validate_content_substance(qa_pair)

        # Check that warning was logged
        assert "Placeholder detected" in caplog.text
        assert "[insert" in caplog.text.lower()


class TestPhase3FullPipeline:
    """Test suite for Phase 3 - Full pipeline integration and database persistence"""

    @pytest.fixture
    def mock_db_session(self):
        """Mock SQLAlchemy database session"""
        db = Mock()
        db.query.return_value.filter.return_value.first.return_value = Mock(
            attempt_id="550e8400-e29b-41d4-a716-446655440000",
            user_id=42,
            ai_feedback={
                "overall_feedback": "Good communication, but missed key history elements",
                "strengths": "Excellent rapport building",
                "areas_for_improvement": "Explore dietary patterns, medication adherence"
            },
            persona=Mock(
                persona_code="CARD-001",
                age=52,
                gender="Female",
                chief_complaint="Chest pain",
                specialty="cardiology"
            )
        )
        db.add_all = Mock()
        db.commit = Mock()
        db.refresh = Mock()
        db.rollback = Mock()
        return db

    @pytest.fixture
    def mock_claude_api_phase3(self):
        """Mock Claude API responses for full pipeline"""
        with patch('src.ai.study_card_generator.Anthropic') as mock_anthropic:
            mock_client = MagicMock()

            # Mock learning point extraction response
            learning_points_response = MagicMock()
            learning_points_response.content = [MagicMock()]
            learning_points_response.content[0].text = json.dumps([
                {
                    "topic": "Dietary patterns assessment in diabetes",
                    "category": "improvement",
                    "priority": "high",
                    "clinical_context": "52F Type 2 Diabetes"
                },
                {
                    "topic": "Medication adherence exploration",
                    "category": "improvement",
                    "priority": "high",
                    "clinical_context": "Chronic disease management"
                },
                {
                    "topic": "Empathy in communication",
                    "category": "strength",
                    "priority": "medium",
                    "clinical_context": "General communication"
                }
            ])

            # Mock Q&A generation responses (parallel calls)
            qa_response_1 = MagicMock()
            qa_response_1.content = [MagicMock()]
            qa_response_1.content[0].text = json.dumps({
                "question": "What dietary patterns should be explored in diabetes history?",
                "answer": "Comprehensive dietary assessment including carbohydrate intake, meal frequency, and nutritional knowledge. Reference eTG Diabetes Management guidelines."
            })

            qa_response_2 = MagicMock()
            qa_response_2.content = [MagicMock()]
            qa_response_2.content[0].text = json.dumps({
                "question": "How should medication adherence be assessed?",
                "answer": "Use open-ended questions to explore barriers to adherence, including cost, side effects, and understanding. Reference RACGP guidelines."
            })

            qa_response_3 = MagicMock()
            qa_response_3.content = [MagicMock()]
            qa_response_3.content[0].text = json.dumps({
                "question": "What are effective empathy techniques in clinical communication?",
                "answer": "Use reflective listening, validate patient emotions, and show genuine concern. Referenced in AMC Clinical Examination standards."
            })

            # Configure mock to return different responses for different calls
            mock_client.messages.create = AsyncMock(
                side_effect=[learning_points_response, qa_response_1, qa_response_2, qa_response_3]
            )

            mock_anthropic.return_value = mock_client
            yield mock_client

    @pytest.mark.asyncio
    async def test_generate_cards_from_session_full_pipeline(
        self, mock_vault, mock_db_session, mock_claude_api_phase3
    ):
        """Test full pipeline from session to database (Phase 3)"""
        # Mock RAG service
        mock_rag = Mock()
        mock_rag.search_similar.return_value = [
            {
                "source": "eTG Diabetes Management",
                "qdrant_point_id": "550e8400-e29b-41d4-a716-446655440000",
                "score": 0.85,
                "title": "eTG",
                "author": "TG",
                "year": "2023",
                "page": 42
            }
        ]

        generator = StudyCardGenerator(rag_service=mock_rag)

        # Execute full pipeline
        cards = await generator.generate_cards_from_session(
            session_id="550e8400-e29b-41d4-a716-446655440000",
            user_id=42,
            db=mock_db_session
        )

        # Verify pipeline completed
        assert len(cards) >= 3  # Should generate 3 cards
        # Cards are StudyCard objects (from src.db.models)
        from src.db.models import StudyCard
        assert all(isinstance(card, StudyCard) for card in cards)

        # Verify database operations
        mock_db_session.add_all.assert_called_once()  # Batch insert
        mock_db_session.commit.assert_called_once()  # Single commit

        # Verify refresh called for each card (to get auto-generated IDs)
        assert mock_db_session.refresh.call_count == len(cards)

    @pytest.mark.asyncio
    async def test_generate_cards_creates_sm2_parameters(
        self, mock_vault, mock_db_session, mock_claude_api_phase3
    ):
        """Test cards are created with correct SM-2 initialization"""
        mock_rag = Mock()
        mock_rag.search_similar.return_value = [
            {
                "source": "Test",
                "qdrant_point_id": "uuid",
                "score": 0.85,
                "title": "Test",
                "author": "Test",
                "year": "2023",
                "page": 1
            }
        ]

        generator = StudyCardGenerator(rag_service=mock_rag)

        # Execute pipeline
        await generator.generate_cards_from_session(
            session_id="550e8400-e29b-41d4-a716-446655440000",
            user_id=42,
            db=mock_db_session
        )

        # Get cards passed to add_all
        call_args = mock_db_session.add_all.call_args
        cards = call_args[0][0]  # First positional argument

        # Verify SM-2 parameters (MANDATORY)
        for card in cards:
            assert card.ease_factor == 2.5, "ease_factor must be 2.5 (SM-2 default)"
            assert card.interval_days == 1, "interval_days must be 1 (first review tomorrow)"
            assert card.repetitions == 0, "repetitions must be 0 (no reviews yet)"
            assert card.next_review_date is not None, "next_review_date must be set"

    @pytest.mark.asyncio
    async def test_generate_cards_batch_inserts_to_db(
        self, mock_vault, mock_db_session, mock_claude_api_phase3
    ):
        """Test batch insert uses single commit (not multiple commits)"""
        mock_rag = Mock()
        mock_rag.search_similar.return_value = [
            {
                "source": "Test",
                "qdrant_point_id": "uuid",
                "score": 0.85,
                "title": "Test",
                "author": "Test",
                "year": "2023",
                "page": 1
            }
        ]

        generator = StudyCardGenerator(rag_service=mock_rag)

        # Execute pipeline
        await generator.generate_cards_from_session(
            session_id="550e8400-e29b-41d4-a716-446655440000",
            user_id=42,
            db=mock_db_session
        )

        # Verify batch operations
        assert mock_db_session.add_all.call_count == 1, "Should use add_all for batch insert"
        assert mock_db_session.commit.call_count == 1, "Should use single commit (not 3-5)"

    @pytest.mark.asyncio
    async def test_generate_cards_completes_within_8_seconds(
        self, mock_vault, mock_db_session, mock_claude_api_phase3
    ):
        """Test card generation completes within 8-second performance target"""
        import time

        mock_rag = Mock()
        mock_rag.search_similar.return_value = [
            {
                "source": "Test",
                "qdrant_point_id": "uuid",
                "score": 0.85,
                "title": "Test",
                "author": "Test",
                "year": "2023",
                "page": 1
            }
        ]

        generator = StudyCardGenerator(rag_service=mock_rag)

        # Measure performance
        start_time = time.time()
        await generator.generate_cards_from_session(
            session_id="550e8400-e29b-41d4-a716-446655440000",
            user_id=42,
            db=mock_db_session
        )
        elapsed_time = time.time() - start_time

        # With mocked API calls, should complete very quickly
        # In production with real Claude API, target is <8 seconds
        assert elapsed_time < 2.0, f"Mocked pipeline should complete in <2s (actual: {elapsed_time:.2f}s)"

    @pytest.mark.asyncio
    async def test_generate_cards_logs_performance_metrics(
        self, mock_vault, mock_db_session, mock_claude_api_phase3, caplog
    ):
        """Test performance metrics are logged for each step"""
        import logging
        caplog.set_level(logging.INFO)

        mock_rag = Mock()
        mock_rag.search_similar.return_value = [
            {
                "source": "Test",
                "qdrant_point_id": "uuid",
                "score": 0.85,
                "title": "Test",
                "author": "Test",
                "year": "2023",
                "page": 1
            }
        ]

        generator = StudyCardGenerator(rag_service=mock_rag)

        # Execute pipeline
        await generator.generate_cards_from_session(
            session_id="550e8400-e29b-41d4-a716-446655440000",
            user_id=42,
            db=mock_db_session
        )

        # Verify performance logging
        log_text = caplog.text
        assert "Step 1 (fetch session):" in log_text
        assert "Step 2 (extract" in log_text
        assert "Step 3 (generate" in log_text
        assert "Step 4 (enrich citations):" in log_text
        assert "Step 5 (validate" in log_text
        assert "Step 6 (create" in log_text
        assert "Step 7 (batch insert):" in log_text
        assert "Total card generation time:" in log_text

    @pytest.mark.asyncio
    async def test_generate_cards_rollback_on_database_error(
        self, mock_vault, mock_db_session, mock_claude_api_phase3
    ):
        """Test transaction rollback on database error"""
        mock_rag = Mock()
        mock_rag.search_similar.return_value = [
            {
                "source": "Test",
                "qdrant_point_id": "uuid",
                "score": 0.85,
                "title": "Test",
                "author": "Test",
                "year": "2023",
                "page": 1
            }
        ]

        generator = StudyCardGenerator(rag_service=mock_rag)

        # Mock database commit failure
        from sqlalchemy.exc import IntegrityError
        mock_db_session.commit.side_effect = IntegrityError("Mock integrity error", None, None)

        # Should raise error and rollback
        with pytest.raises(ValueError, match="Failed to create study cards"):
            await generator.generate_cards_from_session(
                session_id="550e8400-e29b-41d4-a716-446655440000",
                user_id=42,
                db=mock_db_session
            )

        # Verify rollback was called
        mock_db_session.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_cards_validates_session_ownership(
        self, mock_vault, mock_claude_api_phase3
    ):
        """Test validation that user owns the session"""
        # Mock database that returns no session (user doesn't own it)
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = None

        mock_rag = Mock()
        generator = StudyCardGenerator(rag_service=mock_rag)

        # Should raise ValueError
        with pytest.raises(ValueError, match="Session .* not found for user"):
            await generator.generate_cards_from_session(
                session_id="550e8400-e29b-41d4-a716-446655440000",
                user_id=999,  # Different user
                db=mock_db
            )

    @pytest.mark.asyncio
    async def test_generate_cards_validates_session_has_feedback(
        self, mock_vault, mock_claude_api_phase3
    ):
        """Test validation that session has AI feedback"""
        # Mock database that returns session without feedback
        mock_db = Mock()
        mock_db.query.return_value.filter.return_value.first.return_value = Mock(
            attempt_id="550e8400-e29b-41d4-a716-446655440000",
            user_id=42,
            ai_feedback=None  # No feedback
        )

        mock_rag = Mock()
        generator = StudyCardGenerator(rag_service=mock_rag)

        # Should raise ValueError
        with pytest.raises(ValueError, match="has no AI feedback"):
            await generator.generate_cards_from_session(
                session_id="550e8400-e29b-41d4-a716-446655440000",
                user_id=42,
                db=mock_db
            )


class TestPhase3StudyCardCreation:
    """Test suite for _create_study_card helper method"""

    def test_create_study_card_with_sm2_initialization(self, mock_vault):
        """Test _create_study_card initializes SM-2 parameters correctly"""
        generator = StudyCardGenerator()

        qa_pair = {
            "question": "What is SOCRATES?",
            "answer": "Pain assessment framework covering Site, Onset, Character...",
            "citations": [
                {
                    "source": "eTG",
                    "qdrant_point_id": "550e8400-e29b-41d4-a716-446655440000",
                    "confidence": 0.85
                }
            ],
            "learning_point": "Use SOCRATES for pain assessment",
            "category": "improvement",
            "priority": "high"
        }

        card = generator._create_study_card(
            user_id=42,
            session_id="550e8400-e29b-41d4-a716-446655440000",
            qa_pair=qa_pair,
            persona_code="CARD-001"
        )

        # Verify SM-2 initialization (MANDATORY)
        assert card.ease_factor == 2.5, "ease_factor must be 2.5 (SM-2 default)"
        assert card.interval_days == 1, "interval_days must be 1 (first review tomorrow)"
        assert card.repetitions == 0, "repetitions must be 0 (no reviews yet)"
        assert card.next_review_date is not None, "next_review_date must be set"

    def test_create_study_card_populates_content_fields(self, mock_vault):
        """Test _create_study_card populates all content fields"""
        generator = StudyCardGenerator()

        qa_pair = {
            "question": "Test question",
            "answer": "Test answer with clinical content",
            "citations": [{"source": "eTG", "qdrant_point_id": "uuid", "confidence": 0.85}],
            "learning_point": "Test learning point",
            "category": "improvement",
            "priority": "high"
        }

        card = generator._create_study_card(
            user_id=42,
            session_id="uuid",
            qa_pair=qa_pair
        )

        # Verify content fields
        assert card.user_id == 42
        assert card.question == "Test question"
        assert card.answer == "Test answer with clinical content"
        assert len(card.citations) == 1
        assert card.citations[0]["source"] == "eTG"
        assert "Test learning point" in card.explanation

    def test_create_study_card_generates_unique_card_id(self, mock_vault):
        """Test _create_study_card generates unique card IDs"""
        import time
        generator = StudyCardGenerator()

        qa_pair = {
            "question": "Test",
            "answer": "Test",
            "citations": [],
            "learning_point": "Test",
            "category": "improvement",
            "priority": "high"
        }

        card1 = generator._create_study_card(user_id=42, session_id="uuid", qa_pair=qa_pair, persona_code="CARD-001")
        time.sleep(0.001)  # Ensure timestamp changes (millisecond precision)
        card2 = generator._create_study_card(user_id=42, session_id="uuid", qa_pair=qa_pair, persona_code="CARD-001")

        # Card IDs should be different (timestamp-based uniqueness)
        assert card1.card_id != card2.card_id

    def test_create_study_card_sets_active_flag(self, mock_vault):
        """Test _create_study_card sets is_active=True"""
        generator = StudyCardGenerator()

        qa_pair = {
            "question": "Test",
            "answer": "Test",
            "citations": [],
            "learning_point": "Test",
            "category": "improvement",
            "priority": "high"
        }

        card = generator._create_study_card(user_id=42, session_id="uuid", qa_pair=qa_pair)

        assert card.is_active is True
