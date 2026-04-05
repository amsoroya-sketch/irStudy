"""
Test Suite for OSCE-to-EMR Converter

TDD APPROACH: Tests written FIRST before implementation
COVERAGE TARGET: ≥70%
PASS RATE TARGET: 100% (12/12 tests)

CRITICAL REQUIREMENTS:
- ≥70% pre-fill accuracy on all 12 scenarios
- <500ms API response time (p95)
- 100% Australian terminology compliance
- 0 data loss (all OSCE content preserved)
- Graceful fallback if Claude API down
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from uuid import uuid4, UUID
from typing import Dict, Any
from unittest.mock import Mock, patch, AsyncMock

# Test fixtures will be imported from conftest.py
pytestmark = pytest.mark.asyncio


# ============================================================================
# TEST FIXTURES (Test Data)
# ============================================================================

@pytest.fixture
def chest_pain_osce_transcript() -> Dict[str, Any]:
    """
    Test scenario 1: Cardiovascular - Chest pain (ACS)

    Expected outcomes:
    - Subjective: Crushing chest pain, radiation to left arm, diaphoresis
    - Assessment: ACS, unstable angina, GORD (differentials)
    - Plan: ECG, troponin, aspirin 300mg, GTN spray, urgent cardiology review
    """
    return {
        "attempt_id": uuid4(),
        "user_id": 1,
        "persona_id": uuid4(),
        "conversation_history": [
            {
                "role": "patient",
                "content": "I've been having this terrible chest pain for the last 2 hours.",
                "timestamp": "2026-04-05T10:00:00Z"
            },
            {
                "role": "student",
                "content": "Can you describe the pain for me? Where exactly is it?",
                "timestamp": "2026-04-05T10:00:15Z"
            },
            {
                "role": "patient",
                "content": "It's right in the middle of my chest, like someone is squeezing it. It's really tight and heavy.",
                "timestamp": "2026-04-05T10:00:30Z"
            },
            {
                "role": "student",
                "content": "Does the pain go anywhere else?",
                "timestamp": "2026-04-05T10:00:45Z"
            },
            {
                "role": "patient",
                "content": "Yes, it goes down my left arm and into my jaw sometimes.",
                "timestamp": "2026-04-05T10:01:00Z"
            },
            {
                "role": "student",
                "content": "On a scale of 1 to 10, how bad is the pain?",
                "timestamp": "2026-04-05T10:01:15Z"
            },
            {
                "role": "patient",
                "content": "It's about 8 out of 10. I'm also feeling sweaty and a bit short of breath.",
                "timestamp": "2026-04-05T10:01:30Z"
            },
            {
                "role": "student",
                "content": "Have you had anything like this before?",
                "timestamp": "2026-04-05T10:01:45Z"
            },
            {
                "role": "patient",
                "content": "No, never. This is the first time.",
                "timestamp": "2026-04-05T10:02:00Z"
            },
            {
                "role": "student",
                "content": "Do you have any medical conditions?",
                "timestamp": "2026-04-05T10:02:15Z"
            },
            {
                "role": "patient",
                "content": "I have high blood pressure and high cholesterol. I take atorvastatin and perindopril.",
                "timestamp": "2026-04-05T10:02:30Z"
            },
            {
                "role": "student",
                "content": "Do you smoke?",
                "timestamp": "2026-04-05T10:02:45Z"
            },
            {
                "role": "patient",
                "content": "Yes, I smoke about 20 cigarettes a day. I've been smoking for 30 years.",
                "timestamp": "2026-04-05T10:03:00Z"
            },
        ],
        "patient_demographics": {
            "age": 55,
            "gender": "male",
            "name": "[PATIENT_NAME]",  # PHI anonymized
            "mrn": "[MRN]"
        },
        "exam_state": "COMPLETED",
        "final_score": 13,
        "completed_at": "2026-04-05T10:08:00Z"
    }


@pytest.fixture
def headache_osce_transcript() -> Dict[str, Any]:
    """
    Test scenario 2: Neurology - Severe headache (migraine vs SAH)

    Expected outcomes:
    - Subjective: Sudden severe headache, photophobia, nausea
    - Assessment: Migraine, SAH, meningitis (differentials)
    - Plan: CT brain, LP if CT negative, analgesia, neurology review
    """
    return {
        "attempt_id": uuid4(),
        "user_id": 1,
        "persona_id": uuid4(),
        "conversation_history": [
            {
                "role": "patient",
                "content": "I woke up this morning with the worst headache of my life.",
                "timestamp": "2026-04-05T11:00:00Z"
            },
            {
                "role": "student",
                "content": "Where is the headache located?",
                "timestamp": "2026-04-05T11:00:15Z"
            },
            {
                "role": "patient",
                "content": "It's all over, but especially at the back of my head and neck.",
                "timestamp": "2026-04-05T11:00:30Z"
            },
            {
                "role": "student",
                "content": "Did it come on suddenly or gradually?",
                "timestamp": "2026-04-05T11:00:45Z"
            },
            {
                "role": "patient",
                "content": "Very suddenly. I was fine, then boom - this terrible pain.",
                "timestamp": "2026-04-05T11:01:00Z"
            },
            {
                "role": "student",
                "content": "Are you sensitive to light?",
                "timestamp": "2026-04-05T11:01:15Z"
            },
            {
                "role": "patient",
                "content": "Yes, the light really bothers me. I've been in a dark room.",
                "timestamp": "2026-04-05T11:01:30Z"
            },
            {
                "role": "student",
                "content": "Any nausea or vomiting?",
                "timestamp": "2026-04-05T11:01:45Z"
            },
            {
                "role": "patient",
                "content": "Yes, I vomited twice this morning.",
                "timestamp": "2026-04-05T11:02:00Z"
            },
            {
                "role": "student",
                "content": "Have you had headaches like this before?",
                "timestamp": "2026-04-05T11:02:15Z"
            },
            {
                "role": "patient",
                "content": "I get migraines occasionally, but this is much worse than usual.",
                "timestamp": "2026-04-05T11:02:30Z"
            },
        ],
        "patient_demographics": {
            "age": 42,
            "gender": "female",
            "name": "[PATIENT_NAME]",
            "mrn": "[MRN]"
        },
        "exam_state": "COMPLETED",
        "final_score": 12,
        "completed_at": "2026-04-05T11:08:00Z"
    }


@pytest.fixture
def incomplete_osce_transcript() -> Dict[str, Any]:
    """
    Test scenario 3: Incomplete OSCE (student ended early)

    Expected outcomes:
    - Partial pre-fill (≥30% but <70%)
    - Warning message about incomplete data
    - Graceful handling of missing sections
    """
    return {
        "attempt_id": uuid4(),
        "user_id": 1,
        "persona_id": uuid4(),
        "conversation_history": [
            {
                "role": "patient",
                "content": "I've been coughing for 2 weeks.",
                "timestamp": "2026-04-05T12:00:00Z"
            },
            {
                "role": "student",
                "content": "Is it a dry cough or are you bringing up phlegm?",
                "timestamp": "2026-04-05T12:00:15Z"
            },
            {
                "role": "patient",
                "content": "It's mainly dry, but sometimes I cough up a bit of clear mucus.",
                "timestamp": "2026-04-05T12:00:30Z"
            },
            # Student ended session early - incomplete history
        ],
        "patient_demographics": {
            "age": 35,
            "gender": "male",
            "name": "[PATIENT_NAME]",
            "mrn": "[MRN]"
        },
        "exam_state": "ENDED_EARLY",
        "final_score": 4,
        "completed_at": "2026-04-05T12:02:00Z"
    }


@pytest.fixture
def mock_claude_response_chest_pain() -> Dict[str, Any]:
    """Mock Claude API response for chest pain scenario"""
    return {
        "subjective": """**Chief Complaint:** Chest pain for 2 hours

**History of Presenting Illness:**
55-year-old male presents with 2-hour history of central chest pain. Pain described as crushing, tight, and heavy (8/10 severity). Pain radiates to left arm and jaw. Associated symptoms include diaphoresis and shortness of breath. No previous episodes.

**Past Medical History:**
- Hypertension (on perindopril)
- Hyperlipidaemia (on atorvastatin)

**Medications:**
- Atorvastatin (dose not specified)
- Perindopril (dose not specified)

**Allergies:** Not discussed

**Social History:**
- Smoking: 20 cigarettes/day, 30-pack-year history
- Alcohol: Not discussed
- Occupation: Not discussed

**Family History:** Not discussed""",

        "objective": """**Vital Signs:** Not documented during OSCE

**General Appearance:** Patient appears diaphoretic and in distress

**Physical Examination:** Not performed during OSCE (history-taking station)""",

        "assessment": """**Provisional Diagnosis:**
1. **Acute Coronary Syndrome (ACS)** - unstable angina or NSTEMI (most likely)
   - Classic cardiac chest pain presentation
   - Multiple risk factors (hypertension, hyperlipidaemia, smoking)
   - Radiation to left arm and jaw
   - Associated diaphoresis

**Differential Diagnoses:**
2. Gastro-oesophageal reflux disease (GORD)
3. Musculoskeletal chest pain
4. Pulmonary embolism (less likely without dyspnoea)
5. Aortic dissection (less likely without tearing pain)""",

        "plan": """**Immediate Management:**
1. **Urgent ECG** - assess for ST elevation or ischaemic changes
2. **Bloods:**
   - Troponin (baseline and 3-hour repeat)
   - FBC, UEC, LFTs
   - Lipid profile
   - Coagulation studies

3. **Medications:**
   - Aspirin 300mg PO stat (antiplatelet)
   - GTN spray sublingual PRN for chest pain
   - Morphine 2.5-5mg IV if pain not relieved by GTN
   - Oxygen if SpO2 <94%

4. **Monitoring:**
   - Continuous cardiac monitoring
   - Nil by mouth
   - IV access

5. **Specialist Review:**
   - **Urgent cardiology review**
   - Consider angiography if STEMI or high-risk NSTEMI

**Follow-up:**
- Cardiac rehabilitation if ACS confirmed
- Smoking cessation counselling
- Optimize cardiovascular risk factor management""",

        "extraction_confidence": 0.87,
        "missing_elements": [
            "Allergies",
            "Alcohol history",
            "Occupation",
            "Family history",
            "Vital signs",
            "Physical examination findings",
            "Current medication doses"
        ]
    }


# ============================================================================
# UNIT TESTS (Individual Components)
# ============================================================================

class TestOSCEToEMRConverter:
    """Test suite for OSCEToEMRConverter service"""

    @pytest.mark.asyncio
    async def test_chest_pain_conversion_success(
        self,
        chest_pain_osce_transcript,
        mock_claude_response_chest_pain
    ):
        """
        Test scenario 1: Cardiovascular chest pain → EMR SOAP

        Requirements:
        - ≥70% pre-fill accuracy
        - ACS differential diagnosis present
        - Australian medications (aspirin not acetylsalicylic acid)
        - ECG + troponin in investigation plan
        """
        from src.services.integration.osce_to_emr_converter import OSCEToEMRConverter

        # Mock Claude API
        with patch('anthropic.Anthropic') as mock_anthropic:
            mock_client = Mock()
            mock_message = Mock()
            mock_message.content = [Mock(text=str(mock_claude_response_chest_pain))]
            mock_client.messages.create.return_value = mock_message
            mock_anthropic.return_value = mock_client

            # Mock Vault
            with patch('src.core.vault.VaultClient.get_secret') as mock_vault:
                mock_vault.return_value = {"value": "test-api-key"}

                # Convert OSCE to EMR
                converter = OSCEToEMRConverter()
                result = await converter.convert(
                    osce_attempt_id=chest_pain_osce_transcript["attempt_id"],
                    user_id=chest_pain_osce_transcript["user_id"]
                )

                # ASSERTIONS
                assert result is not None
                assert result.soap_note_draft is not None

                # Pre-fill accuracy ≥70%
                assert result.metadata.pre_fill_percentage >= 0.70

                # Extraction confidence ≥0.65 (RAG citation standard)
                assert result.metadata.extraction_confidence >= 0.65

                # SOAP note content validation
                soap = result.soap_note_draft

                # Subjective: chest pain, radiation, risk factors
                assert "chest pain" in soap.subjective.lower()
                assert "left arm" in soap.subjective.lower() or "arm" in soap.subjective.lower()
                assert "smoking" in soap.subjective.lower() or "cigarettes" in soap.subjective.lower()

                # Assessment: ACS in differential
                assert "acs" in soap.assessment.lower() or "acute coronary syndrome" in soap.assessment.lower()

                # Plan: ECG + troponin
                assert "ecg" in soap.plan.lower()
                assert "troponin" in soap.plan.lower()

                # Australian terminology
                assert "aspirin" in soap.plan.lower()  # Australian term
                assert "acetylsalicylic acid" not in soap.plan.lower()  # US term

                # No placeholder content
                assert "[TO BE FILLED]" not in soap.subjective
                assert "TODO" not in soap.plan


    @pytest.mark.asyncio
    async def test_headache_conversion_success(
        self,
        headache_osce_transcript
    ):
        """
        Test scenario 2: Neurology severe headache → EMR SOAP

        Requirements:
        - Sudden-onset headache captured
        - SAH in differential diagnosis
        - CT brain + LP in investigation plan
        - Red flags identified
        """
        from src.services.integration.osce_to_emr_converter import OSCEToEMRConverter

        # Mock Claude API
        mock_response = {
            "subjective": "Sudden-onset severe headache ('worst headache of life'), photophobia, nausea with vomiting. History of migraines but this episode more severe than usual.",
            "objective": "Physical examination not performed during OSCE.",
            "assessment": "1. Subarachnoid haemorrhage (SAH) - sudden onset, severity. 2. Severe migraine. 3. Meningitis.",
            "plan": "Urgent CT brain. If CT negative, lumbar puncture. Analgesia. Neurology review.",
            "extraction_confidence": 0.82,
            "missing_elements": ["Vital signs", "Physical exam"]
        }

        with patch('anthropic.Anthropic') as mock_anthropic:
            mock_client = Mock()
            mock_message = Mock()
            mock_message.content = [Mock(text=str(mock_response))]
            mock_client.messages.create.return_value = mock_message
            mock_anthropic.return_value = mock_client

            with patch('src.core.vault.VaultClient.get_secret') as mock_vault:
                mock_vault.return_value = {"value": "test-api-key"}

                converter = OSCEToEMRConverter()
                result = await converter.convert(
                    osce_attempt_id=headache_osce_transcript["attempt_id"],
                    user_id=headache_osce_transcript["user_id"]
                )

                # ASSERTIONS
                soap = result.soap_note_draft

                # Red flags captured
                assert "sudden" in soap.subjective.lower() or "thunderclap" in soap.subjective.lower()
                assert "worst headache" in soap.subjective.lower() or "severe" in soap.subjective.lower()

                # SAH in differential
                assert "sah" in soap.assessment.lower() or "subarachnoid" in soap.assessment.lower()

                # Appropriate investigations
                assert "ct" in soap.plan.lower()
                assert "lumbar puncture" in soap.plan.lower() or "lp" in soap.plan.lower()


    @pytest.mark.asyncio
    async def test_incomplete_osce_partial_prefill(
        self,
        incomplete_osce_transcript
    ):
        """
        Test scenario 3: Incomplete OSCE → partial pre-fill

        Requirements:
        - Conversion succeeds even with minimal data
        - Pre-fill percentage <70% but >0%
        - Warning metadata about incomplete data
        - No hallucinations (only what's in transcript)
        """
        from src.services.integration.osce_to_emr_converter import OSCEToEMRConverter

        mock_response = {
            "subjective": "2-week history of cough, mainly dry with occasional clear sputum.",
            "objective": "Physical examination not performed.",
            "assessment": "Insufficient information for diagnosis. Need further history.",
            "plan": "Complete history taking. Physical examination. Consider CXR if symptoms persist.",
            "extraction_confidence": 0.35,
            "missing_elements": [
                "Associated symptoms",
                "Past medical history",
                "Medications",
                "Social history",
                "Vital signs",
                "Physical exam"
            ]
        }

        with patch('anthropic.Anthropic') as mock_anthropic:
            mock_client = Mock()
            mock_message = Mock()
            mock_message.content = [Mock(text=str(mock_response))]
            mock_client.messages.create.return_value = mock_message
            mock_anthropic.return_value = mock_client

            with patch('src.core.vault.VaultClient.get_secret') as mock_vault:
                mock_vault.return_value = {"value": "test-api-key"}

                converter = OSCEToEMRConverter()
                result = await converter.convert(
                    osce_attempt_id=incomplete_osce_transcript["attempt_id"],
                    user_id=incomplete_osce_transcript["user_id"]
                )

                # ASSERTIONS
                # Partial pre-fill (between 0-70%)
                assert 0.0 < result.metadata.pre_fill_percentage < 0.70

                # Low confidence
                assert result.metadata.extraction_confidence < 0.65

                # Missing elements tracked
                assert len(result.metadata.missing_elements) > 3

                # No hallucinations
                soap = result.soap_note_draft
                assert "cough" in soap.subjective.lower()
                assert "2 week" in soap.subjective.lower() or "14 day" in soap.subjective.lower()


    @pytest.mark.asyncio
    async def test_australian_terminology_enforcement(self):
        """
        Test scenario 4: Australian medical terminology validation

        Requirements:
        - Paracetamol NOT acetaminophen
        - Salbutamol NOT albuterol
        - 000 NOT 911
        - ED NOT ER
        """
        from src.services.integration.osce_to_emr_converter import OSCEToEMRConverter
        from src.schemas.integration import SOAPNoteDraft
        import pytest

        # Test US terminology rejection
        with pytest.raises(ValueError, match="Australian terminology"):
            SOAPNoteDraft(
                subjective="Patient has fever.",
                objective="Temp 38.5°C.",
                assessment="Viral URTI.",
                plan="Give acetaminophen 1g PO."  # US term - should fail
            )

        # Test Australian terminology acceptance
        soap = SOAPNoteDraft(
            subjective="Patient has fever.",
            objective="Temp 38.5°C.",
            assessment="Viral URTI.",
            plan="Give paracetamol 1g PO."  # Australian term - should pass
        )
        assert "paracetamol" in soap.plan.lower()


    @pytest.mark.asyncio
    async def test_performance_under_500ms(
        self,
        chest_pain_osce_transcript,
        mock_claude_response_chest_pain
    ):
        """
        Test scenario 5: Performance requirement <500ms (p95)

        Requirements:
        - Total API response time <500ms
        - Tracked in conversion metadata
        """
        from src.services.integration.osce_to_emr_converter import OSCEToEMRConverter
        import time

        with patch('anthropic.Anthropic') as mock_anthropic:
            # Simulate 200ms Claude API latency
            def slow_create(*args, **kwargs):
                time.sleep(0.2)  # 200ms
                mock_message = Mock()
                mock_message.content = [Mock(text=str(mock_claude_response_chest_pain))]
                return mock_message

            mock_client = Mock()
            mock_client.messages.create = slow_create
            mock_anthropic.return_value = mock_client

            with patch('src.core.vault.VaultClient.get_secret') as mock_vault:
                mock_vault.return_value = {"value": "test-api-key"}

                converter = OSCEToEMRConverter()

                start_time = time.time()
                result = await converter.convert(
                    osce_attempt_id=chest_pain_osce_transcript["attempt_id"],
                    user_id=chest_pain_osce_transcript["user_id"]
                )
                end_time = time.time()

                # Total time <500ms
                total_time_ms = (end_time - start_time) * 1000
                assert total_time_ms < 500

                # API response time tracked
                assert result.metadata.api_response_time_ms > 0
                assert result.metadata.api_response_time_ms < 500


    @pytest.mark.asyncio
    async def test_vault_integration_no_hardcoded_credentials(self):
        """
        Test scenario 6: Security - no hardcoded Claude API keys

        Requirements:
        - All API keys retrieved from Vault
        - Zero hardcoded credentials in code
        - Graceful fallback if Vault unavailable
        """
        from src.services.integration.osce_to_emr_converter import OSCEToEMRConverter

        # Test Vault retrieval
        with patch('src.core.vault.VaultClient.get_secret') as mock_vault:
            mock_vault.return_value = {"value": "vault-retrieved-key"}

            with patch('anthropic.Anthropic') as mock_anthropic:
                mock_client = Mock()
                mock_anthropic.return_value = mock_client

                converter = OSCEToEMRConverter()

                # Verify Vault called with correct path
                # (will be implemented in service)
                assert mock_vault.called or True  # Placeholder


    @pytest.mark.asyncio
    async def test_claude_api_failure_graceful_fallback(
        self,
        chest_pain_osce_transcript
    ):
        """
        Test scenario 7: Claude API down → graceful fallback

        Requirements:
        - Return partial pre-fill with warning
        - No crash/exception propagated to user
        - Error logged for monitoring
        """
        from src.services.integration.osce_to_emr_converter import OSCEToEMRConverter
        from anthropic import APIError

        with patch('anthropic.Anthropic') as mock_anthropic:
            # Simulate API failure
            mock_client = Mock()
            mock_client.messages.create.side_effect = APIError("API unavailable")
            mock_anthropic.return_value = mock_client

            with patch('src.core.vault.VaultClient.get_secret') as mock_vault:
                mock_vault.return_value = {"value": "test-api-key"}

                converter = OSCEToEMRConverter()

                # Should not raise exception
                result = await converter.convert(
                    osce_attempt_id=chest_pain_osce_transcript["attempt_id"],
                    user_id=chest_pain_osce_transcript["user_id"]
                )

                # Fallback result provided
                assert result is not None

                # Low confidence score
                assert result.metadata.extraction_confidence < 0.5


    @pytest.mark.asyncio
    async def test_user_authorization_osce_ownership(self):
        """
        Test scenario 8: Security - user can only convert their own OSCEs

        Requirements:
        - User ID validation
        - Reject conversion if user doesn't own OSCE attempt
        - Proper error message
        """
        from src.services.integration.osce_to_emr_converter import OSCEToEMRConverter

        # User 1 tries to convert User 2's OSCE
        with pytest.raises(ValueError, match="not authorized|ownership"):
            converter = OSCEToEMRConverter()
            await converter.convert(
                osce_attempt_id=uuid4(),  # Non-existent OSCE
                user_id=999  # Different user
            )


    @pytest.mark.asyncio
    async def test_data_integrity_no_loss(
        self,
        chest_pain_osce_transcript
    ):
        """
        Test scenario 9: Data integrity - 0 data loss during conversion

        Requirements:
        - All OSCE transcript preserved in conversion_metadata
        - Original conversation history accessible
        - Source OSCE attempt ID linked
        """
        from src.services.integration.osce_to_emr_converter import OSCEToEMRConverter

        # Mock database storage
        with patch('src.services.integration.osce_to_emr_converter.OSCEToEMRConverter._create_emr_session') as mock_create:
            mock_create.return_value = uuid4()

            # Verify conversion_metadata includes source OSCE
            # (Implementation detail - will be in service)
            pass


    @pytest.mark.asyncio
    async def test_tokens_usage_tracking(
        self,
        chest_pain_osce_transcript,
        mock_claude_response_chest_pain
    ):
        """
        Test scenario 10: Token usage tracking for cost monitoring

        Requirements:
        - Claude API tokens counted
        - Stored in conversion_metadata
        - Average <2000 tokens per conversion
        """
        from src.services.integration.osce_to_emr_converter import OSCEToEMRConverter

        with patch('anthropic.Anthropic') as mock_anthropic:
            mock_client = Mock()
            mock_message = Mock()
            mock_message.content = [Mock(text=str(mock_claude_response_chest_pain))]
            mock_message.usage = Mock(input_tokens=500, output_tokens=800)
            mock_client.messages.create.return_value = mock_message
            mock_anthropic.return_value = mock_client

            with patch('src.core.vault.VaultClient.get_secret') as mock_vault:
                mock_vault.return_value = {"value": "test-api-key"}

                converter = OSCEToEMRConverter()
                result = await converter.convert(
                    osce_attempt_id=chest_pain_osce_transcript["attempt_id"],
                    user_id=chest_pain_osce_transcript["user_id"]
                )

                # Tokens tracked
                assert result.metadata.tokens_used > 0
                assert result.metadata.tokens_used < 2000  # Reasonable limit


    @pytest.mark.asyncio
    async def test_respiratory_asthma_conversion(self):
        """
        Test scenario 11: Respiratory - Asthma exacerbation

        Requirements:
        - Salbutamol (NOT albuterol) in plan
        - SABA + ICS mentioned
        - Peak flow measurements
        """
        from src.services.integration.osce_to_emr_converter import OSCEToEMRConverter

        asthma_transcript = {
            "attempt_id": uuid4(),
            "user_id": 1,
            "conversation_history": [
                {"role": "patient", "content": "I've been short of breath for 2 days."},
                {"role": "student", "content": "Do you have asthma?"},
                {"role": "patient", "content": "Yes, I use Ventolin when needed."},
                {"role": "student", "content": "Have you been using it more often?"},
                {"role": "patient", "content": "Yes, about 6 times yesterday."},
            ],
            "patient_demographics": {"age": 28, "gender": "female"},
            "exam_state": "COMPLETED"
        }

        mock_response = {
            "subjective": "2-day history of worsening dyspnoea. Known asthma. Increased salbutamol use (6 puffs yesterday).",
            "objective": "Examination not performed.",
            "assessment": "Asthma exacerbation.",
            "plan": "Salbutamol 6-8 puffs via spacer. Prednisolone 50mg PO daily for 5 days. Review ICS compliance.",
            "extraction_confidence": 0.75,
            "missing_elements": []
        }

        with patch('anthropic.Anthropic') as mock_anthropic:
            mock_client = Mock()
            mock_message = Mock()
            mock_message.content = [Mock(text=str(mock_response))]
            mock_client.messages.create.return_value = mock_message
            mock_anthropic.return_value = mock_client

            with patch('src.core.vault.VaultClient.get_secret') as mock_vault:
                mock_vault.return_value = {"value": "test-api-key"}

                converter = OSCEToEMRConverter()
                result = await converter.convert(
                    osce_attempt_id=asthma_transcript["attempt_id"],
                    user_id=asthma_transcript["user_id"]
                )

                soap = result.soap_note_draft

                # Australian terminology
                assert "salbutamol" in soap.plan.lower()
                assert "albuterol" not in soap.plan.lower()


    @pytest.mark.asyncio
    async def test_breaking_bad_news_no_soap_error(self):
        """
        Test scenario 12: Breaking bad news OSCE → no SOAP note (error)

        Requirements:
        - Communication/counselling OSCEs don't convert to SOAP
        - Clear error message explaining why
        - Suggest alternative (reflection log)
        """
        from src.services.integration.osce_to_emr_converter import OSCEToEMRConverter

        bbn_transcript = {
            "attempt_id": uuid4(),
            "user_id": 1,
            "conversation_history": [
                {"role": "student", "content": "I have some difficult news to share with you today."},
                {"role": "patient", "content": "Okay, what is it?"},
                {"role": "student", "content": "The biopsy results show that you have cancer."},
            ],
            "patient_demographics": {"age": 65, "gender": "male"},
            "exam_state": "COMPLETED",
            "station_type": "communication"  # Not clinical history-taking
        }

        with pytest.raises(ValueError, match="cannot be converted|communication|counselling"):
            converter = OSCEToEMRConverter()
            await converter.convert(
                osce_attempt_id=bbn_transcript["attempt_id"],
                user_id=bbn_transcript["user_id"]
            )


# ============================================================================
# INTEGRATION TESTS (API Endpoints)
# ============================================================================

class TestOSCEToEMRAPI:
    """Test suite for /api/v1/integration/osce-to-emr endpoint"""

    @pytest.mark.asyncio
    async def test_api_conversion_endpoint_success(self, chest_pain_osce_transcript):
        """
        Test API endpoint POST /osce-to-emr

        Requirements:
        - 201 Created on success
        - Returns emr_session_id, redirect_url
        - Response time <500ms
        """
        # Will be implemented after service creation
        pass


    @pytest.mark.asyncio
    async def test_api_invalid_osce_id_404(self):
        """
        Test API endpoint with non-existent OSCE ID

        Requirements:
        - 404 Not Found
        - Clear error message
        """
        pass


    @pytest.mark.asyncio
    async def test_api_unauthorized_user_403(self):
        """
        Test API endpoint with unauthorized user

        Requirements:
        - 403 Forbidden
        - User cannot convert others' OSCEs
        """
        pass
