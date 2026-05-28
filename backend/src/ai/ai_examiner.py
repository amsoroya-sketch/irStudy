"""
AI Examiner Service - Claude 3.5 Sonnet Integration
AMC 15-Mark Rubric Scoring

SECURITY:
- API key from Vault (secret/ai-osce/claude-api-key)
- ZERO hardcoded credentials

PERFORMANCE:
- Scoring time target: <5s (p95)
- Consistent scoring with temp=0.1
"""
import logging
import json
from typing import Dict, Any, List, Union, Optional
from anthropic import Anthropic, APIError

from src.core.vault import get_vault_secret
from src.ai.prompts.examiner_system_prompt import build_examiner_system_prompt

logger = logging.getLogger(__name__)


class AIExaminerService:
    """
    AI Examiner for OSCE scoring using Claude 3.5 Sonnet.
    
    Implements:
    - AMC 15-mark rubric (5 domains)
    - Critical error detection
    - Pass/fail determination
    - Structured JSON feedback
    """
    
    def __init__(self):
        """
        Initialize Claude API client with Vault integration.
        
        API Key Sources (in order):
        1. Vault: secret/ai-osce/claude-api-key (primary)
        2. Vault: irStudy/claude (fallback)
        3. Environment: ANTHROPIC_API_KEY (fallback)
        """
        self.model = "claude-sonnet-4-6"
        self.temperature = 0.1  # Consistent scoring
        self.max_tokens = 2000
        
        # Get API key from Vault
        self.api_key = self._get_api_key()
        
        if not self.api_key:
            raise ValueError("Claude API key not found in Vault")
        
        # Initialize Anthropic client
        self.client = Anthropic(api_key=self.api_key)
        logger.info("✅ AI Examiner service initialized with Claude 3.5 Sonnet")
    
    def _get_api_key(self) -> Optional[str]:
        """Retrieve Claude API key from Vault or environment."""
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
                logger.warning(f"⚠️  Fallback Vault path failed: {e2}")
                return None
    
    def score_session(
        self,
        persona: Union[Dict[str, Any], Any],
        transcript: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Score OSCE session using AMC 15-mark rubric.
        
        Args:
            persona: PatientPersona data (dict or object)
            transcript: Conversation history [{"role": "student"/"patient", "message": "..."}]
        
        Returns:
            Dict with structure:
            {
                "communication_score": 0-3,
                "communication_feedback": "...",
                "clinical_reasoning_score": 0-4,
                "clinical_reasoning_feedback": "...",
                "information_gathering_score": 0-4,
                "information_gathering_feedback": "...",
                "management_score": 0-2,
                "management_feedback": "...",
                "professionalism_score": 0-2,
                "professionalism_feedback": "...",
                "total_score": 0-15,
                "pass_fail": "PASS|BORDERLINE|FAIL",
                "critical_errors": [],
                "strengths": [],
                "areas_for_improvement": [],
                "overall_feedback": "..."
            }
        """
        import time
        start_time = time.time()
        
        try:
            # 1. Build SYSTEM_PROMPT
            system_prompt = build_examiner_system_prompt(persona, transcript)
            
            # 2. Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": "Please score this OSCE session using the AMC 15-mark rubric."}]
            )
            
            # 3. Parse JSON response
            response_text = response.content[0].text
            scores = self._parse_json_response(response_text)
            
            # 4. Validate scores
            validated_scores = self._validate_scores(scores)
            
            response_time_ms = (time.time() - start_time) * 1000
            
            # Track token usage
            try:
                tokens_used = response.usage.input_tokens + response.usage.output_tokens
                logger.info(
                    f"✅ AI Examiner scoring complete: "
                    f"{validated_scores['total_score']}/15 ({validated_scores['pass_fail']}), "
                    f"{tokens_used} tokens, {response_time_ms:.0f}ms"
                )
            except (AttributeError, TypeError):
                logger.info(f"✅ AI Examiner scoring complete: {response_time_ms:.0f}ms")
            
            return validated_scores
        
        except APIError as e:
            logger.error(f"❌ Claude API error during scoring: {e}")
            return self._get_fallback_scores()
        
        except Exception as e:
            logger.error(f"❌ Unexpected error during scoring: {e}")
            return self._get_fallback_scores()
    
    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """Parse JSON from Claude response."""
        try:
            # Try direct JSON parse
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code block
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
                return json.loads(json_text)
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
                return json.loads(json_text)
            else:
                raise ValueError("Could not parse JSON from response")
    
    def _validate_scores(self, scores: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate scores are within correct ranges.
        
        Ensures:
        - communication_score: 0-3
        - clinical_reasoning_score: 0-4
        - information_gathering_score: 0-4
        - management_score: 0-2
        - professionalism_score: 0-2
        - total_score = sum of 5 domains
        - pass_fail in ["PASS", "BORDERLINE", "FAIL"]
        """
        validated = scores.copy()
        
        # Clamp scores to valid ranges
        validated["communication_score"] = max(0, min(3, scores.get("communication_score", 0)))
        validated["clinical_reasoning_score"] = max(0, min(4, scores.get("clinical_reasoning_score", 0)))
        validated["information_gathering_score"] = max(0, min(4, scores.get("information_gathering_score", 0)))
        validated["management_score"] = max(0, min(2, scores.get("management_score", 0)))
        validated["professionalism_score"] = max(0, min(2, scores.get("professionalism_score", 0)))
        
        # Calculate total_score
        validated["total_score"] = (
            validated["communication_score"] +
            validated["clinical_reasoning_score"] +
            validated["information_gathering_score"] +
            validated["management_score"] +
            validated["professionalism_score"]
        )
        
        # Determine pass_fail
        critical_errors = scores.get("critical_errors", [])
        if critical_errors:
            validated["pass_fail"] = "FAIL"
        elif validated["total_score"] >= 9:
            validated["pass_fail"] = "PASS"
        elif validated["total_score"] == 8:
            validated["pass_fail"] = "BORDERLINE"
        else:
            validated["pass_fail"] = "FAIL"
        
        # Ensure required fields exist
        validated.setdefault("critical_errors", [])
        validated.setdefault("strengths", [])
        validated.setdefault("areas_for_improvement", [])
        validated.setdefault("overall_feedback", "")

        # NEW: Ensure all FEEDBACK fields exist and are strings
        feedback_fields = [
            "communication_feedback",
            "clinical_reasoning_feedback",
            "information_gathering_feedback",
            "management_feedback",
            "professionalism_feedback",
            "overall_feedback"
        ]

        for field in feedback_fields:
            if field not in validated or not isinstance(validated[field], str):
                validated[field] = "No feedback provided"
            elif len(validated[field].strip()) == 0:
                validated[field] = "No specific feedback"

        # NEW: Ensure arrays exist and are lists
        if not isinstance(validated["critical_errors"], list):
            validated["critical_errors"] = []
        if not isinstance(validated["strengths"], list):
            validated["strengths"] = []
        if not isinstance(validated["areas_for_improvement"], list):
            validated["areas_for_improvement"] = []

        return validated
    
    def _get_fallback_scores(self) -> Dict[str, Any]:
        """Return fallback scores when API fails."""
        return {
            "communication_score": 0,
            "communication_feedback": "Unable to score - API error",
            "clinical_reasoning_score": 0,
            "clinical_reasoning_feedback": "Unable to score - API error",
            "information_gathering_score": 0,
            "information_gathering_feedback": "Unable to score - API error",
            "management_score": 0,
            "management_feedback": "Unable to score - API error",
            "professionalism_score": 0,
            "professionalism_feedback": "Unable to score - API error",
            "total_score": 0,
            "pass_fail": "FAIL",
            "critical_errors": ["API error during scoring"],
            "strengths": [],
            "areas_for_improvement": ["Session could not be scored due to technical error"],
            "overall_feedback": "Unable to score session due to API error. Please try again."
        }
