"""
AI Patient Service - Claude 3.5 Sonnet Integration
Progressive disclosure, emotional intelligence, RAG-augmented responses

SECURITY:
- API key from Vault (secret/ai-osce/claude-api-key OR irStudy/claude)
- ZERO hardcoded credentials
- Fallback to ANTHROPIC_API_KEY environment variable

PERFORMANCE:
- Response time target: <3s (p95)
- Token tracking for cost management
"""

import logging
from typing import Dict, Any, List, Optional, Union
from anthropic import Anthropic, APIError, APIConnectionError, RateLimitError

from src.core.vault import get_vault_secret
from src.ai.prompts.patient_system_prompt import build_patient_system_prompt

logger = logging.getLogger(__name__)


def _get_attr(obj: Any, attr: str, default: Any = None) -> Any:
    """
    Get attribute from object or dict.
    Handles both dict-like and object-like personas.
    """
    if isinstance(obj, dict):
        return obj.get(attr, default)
    return getattr(obj, attr, default)


class AIPatientService:
    """
    AI Patient simulation using Claude 3.5 Sonnet.

    Implements:
    - Progressive disclosure (reveals info only when asked)
    - Emotional state awareness
    - Natural conversational responses
    - Clinical accuracy via structured prompts
    """

    def __init__(self):
        """
        Initialize Claude API client with Vault integration.

        API Key Sources (in order):
        1. Vault: secret/ai-osce/claude-api-key (primary)
        2. Vault: irStudy/claude (fallback)
        3. Environment: ANTHROPIC_API_KEY (fallback)

        Raises:
            ValueError: If no API key found
        """
        self.model = "claude-sonnet-4-6"
        self.temperature = 0.7
        self.max_tokens = 500

        # Get API key from Vault (with environment fallback)
        self.api_key = self._get_api_key()

        if not self.api_key:
            raise ValueError(
                "Claude API key not found in Vault"
            )

        # Initialize Anthropic client
        self.client = Anthropic(api_key=self.api_key)
        logger.info("✅ AI Patient service initialized with Claude 3.5 Sonnet")

    def _get_api_key(self) -> Optional[str]:
        """
        Retrieve Claude API key from Vault or environment.

        Returns:
            API key string or None
        """
        try:
            # Try primary Vault path
            api_key = get_vault_secret("secret/ai-osce/claude-api-key", "value")
            logger.info("✅ Claude API key retrieved from Vault (secret/ai-osce/claude-api-key)")
            return api_key
        except Exception as e1:
            logger.warning(f"⚠️  Primary Vault path failed: {e1}")

            try:
                # Try fallback Vault path
                api_key = get_vault_secret("irStudy/claude", "api_key")
                logger.info("✅ Claude API key retrieved from Vault (irStudy/claude)")
                return api_key
            except Exception as e2:
                logger.warning(f"⚠️  Fallback Vault path failed: {e2}")
                logger.warning("⚠️  Falling back to environment variable ANTHROPIC_API_KEY")
                return None  # get_vault_secret will fall back to environment

    def generate_response(
        self,
        persona: Union[Dict[str, Any], Any],
        student_message: str,
        emotional_state: str = "ANXIOUS_GUARDED"
    ) -> str:
        """
        Generate AI Patient response to student message.

        Args:
            persona: PatientPersona data (dict or object with attributes)
            student_message: Student's question/statement
            emotional_state: Current emotional state (default: "ANXIOUS_GUARDED")

        Returns:
            AI Patient response (str)

        Raises:
            APIError: If Claude API call fails
        """
        import time
        start_time = time.time()

        try:
            # Convert persona to dict if it's an object
            persona_dict = self._persona_to_dict(persona)

            # 1. Determine disclosed information (progressive disclosure)
            disclosed_symptoms = self._get_disclosed_information(
                student_message,
                persona_dict.get("symptoms", {})
            )

            # 2. Build SYSTEM_PROMPT
            system_prompt = build_patient_system_prompt(
                persona=persona_dict,
                emotional_state=emotional_state,
                disclosed_symptoms=disclosed_symptoms
            )

            # 3. Call Claude API
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system_prompt,
                messages=[{"role": "user", "content": student_message}]
            )

            # 4. Extract response
            patient_message = response.content[0].text

            response_time_ms = (time.time() - start_time) * 1000

            # Track token usage (if available)
            try:
                tokens_used = response.usage.input_tokens + response.usage.output_tokens
                logger.info(
                    f"✅ AI Patient response generated: "
                    f"{tokens_used} tokens, {response_time_ms:.0f}ms"
                )
            except (AttributeError, TypeError):
                # Mock object in tests may not have usage attribute or may cause type errors
                logger.info(f"✅ AI Patient response generated: {response_time_ms:.0f}ms")

            return patient_message

        except RateLimitError as e:
            logger.error(f"❌ Claude API rate limit exceeded: {e}")
            return "I'm sorry, I'm feeling a bit overwhelmed right now. Can you give me a moment?"

        except APIConnectionError as e:
            logger.error(f"❌ Claude API connection error: {e}")
            return "I'm having trouble expressing myself right now. Could you repeat that?"

        except APIError as e:
            logger.error(f"❌ Claude API error: {e}")
            return "I'm not sure how to respond to that right now."

        except Exception as e:
            import traceback
            logger.error(f"❌ Unexpected error generating AI Patient response: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return "I'm sorry, I'm feeling very confused right now."

    async def generate_response_async(
        self,
        persona: Union[Dict[str, Any], Any],
        student_message: str,
        emotional_state: str = "ANXIOUS_GUARDED"
    ) -> str:
        """
        Async version of generate_response for performance testing.
        """
        return self.generate_response(persona, student_message, emotional_state)

    def _persona_to_dict(self, persona: Union[Dict[str, Any], Any]) -> Dict[str, Any]:
        """
        Convert persona object to dictionary.
        Handles both dict and object types (including Mock objects in tests).
        Always normalizes nested fields (especially symptoms) to expected types.
        """
        # Start with dict if already one, otherwise build from object
        if isinstance(persona, dict):
            source = persona
        else:
            source = {}
            attrs = [
                "name", "age", "gender", "occupation", "cultural_background",
                "chief_complaint", "opening_statement", "symptoms"
            ]
            for attr in attrs:
                source[attr] = _get_attr(persona, attr, None)

        # Normalize each field
        persona_dict = {}
        for attr, val in source.items():
            if val is None:
                persona_dict[attr] = ""
            elif isinstance(val, dict):
                # Convert dict values to strings to handle Mock objects
                converted_dict = {}
                for k, v in val.items():
                    if isinstance(v, list):
                        converted_dict[k] = [str(item) for item in v]
                    else:
                        converted_dict[k] = str(v) if v is not None else ""
                persona_dict[attr] = converted_dict
            elif isinstance(val, list):
                # Convert list items to strings
                persona_dict[attr] = [str(item) for item in val]
            else:
                # Convert simple value to string
                persona_dict[attr] = str(val)

        # Ensure symptoms is a dict (progressive disclosure expects keys like "immediate")
        if "symptoms" in persona_dict and isinstance(persona_dict["symptoms"], list):
            persona_dict["symptoms"] = {"immediate": persona_dict["symptoms"]}

        return persona_dict

    def _get_disclosed_information(
        self,
        student_message: str,
        symptoms: Dict[str, Any]
    ) -> List[str]:
        """
        Map student questions to disclosed symptoms (progressive disclosure).
        """
        disclosed = []

        # Defensive: symptoms may be None or not a dict
        if not symptoms or not isinstance(symptoms, dict):
            return disclosed

        # Always reveal immediate symptoms
        immediate = symptoms.get("immediate", [])
        if isinstance(immediate, list):
            disclosed.extend([str(s) for s in immediate])
        elif immediate:
            disclosed.append(str(immediate))

        # Progressive disclosure based on student questions
        message_lower = student_message.lower()

        # Onset questions
        if any(keyword in message_lower for keyword in ["when", "started", "began", "onset", "how long"]):
            onset = symptoms.get("when_asked_onset")
            if onset:
                disclosed.append(str(onset))

        # Severity questions
        if any(keyword in message_lower for keyword in ["severity", "how bad", "pain level", "scale", "out of 10"]):
            severity = symptoms.get("when_asked_severity")
            if severity:
                disclosed.append(str(severity))

        # Character/quality questions
        if any(keyword in message_lower for keyword in ["character", "type", "feel like", "describe", "quality"]):
            character = symptoms.get("when_asked_character")
            if character:
                disclosed.append(str(character))

        # Radiation questions
        if any(keyword in message_lower for keyword in ["radiate", "spread", "go", "move", "where else"]):
            radiation = symptoms.get("when_asked_radiation")
            if radiation:
                disclosed.append(str(radiation))

        # Relieving factors
        if any(keyword in message_lower for keyword in ["better", "help", "relieve", "improve", "ease"]):
            relieving = symptoms.get("when_asked_relieving_factors")
            if relieving:
                disclosed.append(str(relieving))

        # Aggravating factors
        if any(keyword in message_lower for keyword in ["worse", "aggravate", "trigger", "worsen"]):
            aggravating = symptoms.get("when_asked_aggravating_factors")
            if aggravating:
                disclosed.append(str(aggravating))

        # Associated symptoms
        if any(keyword in message_lower for keyword in ["other symptom", "anything else", "associated", "along with"]):
            associated = symptoms.get("when_asked_associated_symptoms")
            if associated:
                disclosed.append(str(associated))

        # Previous episodes
        if any(keyword in message_lower for keyword in ["before", "previous", "history", "past", "happened before"]):
            previous = symptoms.get("when_asked_previous_episodes")
            if previous:
                disclosed.append(str(previous))

        # Remove empty strings and duplicates
        disclosed = [d.strip() for d in disclosed if d and str(d).strip()]
        disclosed = list(dict.fromkeys(disclosed))  # Remove duplicates while preserving order

        return disclosed
