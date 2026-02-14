"""
AI Router - Kimi 2.5 Adapter
Routes Claude API calls to Kimi 2.5 (Moonshot AI) for free usage
"""

import os
import json
from typing import Dict, Any, Optional, List
import httpx
from anthropic.types import Message, ContentBlock, TextBlock


class KimiAdapter:
    """
    Adapter to translate Claude API format to Kimi API format
    Allows using Kimi 2.5 as a drop-in replacement for Claude
    """

    def __init__(self, kimi_api_key: Optional[str] = None, kimi_base_url: Optional[str] = None):
        """
        Initialize Kimi adapter

        Args:
            kimi_api_key: Kimi API key (defaults to env KIMI_API_KEY)
            kimi_base_url: Kimi API base URL (defaults to Moonshot API)
        """
        self.api_key = kimi_api_key or os.getenv('KIMI_API_KEY')
        self.base_url = kimi_base_url or os.getenv('KIMI_BASE_URL', 'https://api.moonshot.cn/v1')

        if not self.api_key:
            raise ValueError("KIMI_API_KEY environment variable or kimi_api_key parameter required")

        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            },
            timeout=30.0
        )

    def _convert_claude_to_kimi_messages(
        self,
        messages: List[Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        """
        Convert Claude message format to Kimi/OpenAI format

        Claude format:
        [{"role": "user", "content": "text"}]

        Kimi format (OpenAI-compatible):
        [{"role": "user", "content": "text"}]

        Args:
            messages: Claude-style messages

        Returns:
            Kimi-style messages
        """
        kimi_messages = []

        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')

            # Handle content blocks (Claude format)
            if isinstance(content, list):
                text_parts = []
                for block in content:
                    if isinstance(block, dict) and block.get('type') == 'text':
                        text_parts.append(block.get('text', ''))
                content = '\n'.join(text_parts)

            kimi_messages.append({
                'role': role,
                'content': content
            })

        return kimi_messages

    def _convert_kimi_to_claude_response(
        self,
        kimi_response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Convert Kimi response to Claude format

        Kimi response:
        {
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": "text"
                }
            }],
            "usage": {...}
        }

        Claude response format:
        {
            "content": [{"type": "text", "text": "..."}],
            "role": "assistant",
            ...
        }

        Args:
            kimi_response: Kimi API response

        Returns:
            Claude-style response
        """
        try:
            # Extract message from Kimi response
            choice = kimi_response.get('choices', [{}])[0]
            message = choice.get('message', {})
            content_text = message.get('content', '')

            # Convert to Claude format
            claude_response = {
                'id': kimi_response.get('id', 'kimi-msg'),
                'type': 'message',
                'role': 'assistant',
                'content': [
                    {
                        'type': 'text',
                        'text': content_text
                    }
                ],
                'model': kimi_response.get('model', 'moonshot-v1-8k'),
                'stop_reason': 'end_turn',
                'usage': {
                    'input_tokens': kimi_response.get('usage', {}).get('prompt_tokens', 0),
                    'output_tokens': kimi_response.get('usage', {}).get('completion_tokens', 0)
                }
            }

            return claude_response

        except Exception as e:
            # Fallback response
            return {
                'id': 'error',
                'type': 'message',
                'role': 'assistant',
                'content': [
                    {
                        'type': 'text',
                        'text': f'Error converting Kimi response: {str(e)}'
                    }
                ],
                'model': 'kimi-error',
                'stop_reason': 'error',
                'usage': {'input_tokens': 0, 'output_tokens': 0}
            }

    async def create_message(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        max_tokens: int = 2000,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create message (Claude API-compatible interface)

        Args:
            model: Claude model name (will be mapped to Kimi model)
            messages: Messages in Claude format
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional parameters

        Returns:
            Response in Claude format
        """
        # Map Claude model to Kimi model
        kimi_model_map = {
            'claude-3-5-sonnet-20241022': 'moonshot-v1-128k',
            'claude-3-opus-20240229': 'moonshot-v1-128k',
            'claude-3-sonnet-20240229': 'moonshot-v1-32k',
            'claude-3-haiku-20240307': 'moonshot-v1-8k',
        }

        kimi_model = kimi_model_map.get(model, 'moonshot-v1-32k')

        # Convert messages to Kimi format
        kimi_messages = self._convert_claude_to_kimi_messages(messages)

        # Prepare Kimi API request
        request_data = {
            'model': kimi_model,
            'messages': kimi_messages,
            'max_tokens': max_tokens,
            'temperature': temperature,
        }

        try:
            # Call Kimi API
            response = await self.client.post(
                '/chat/completions',
                json=request_data
            )

            response.raise_for_status()
            kimi_response = response.json()

            # Convert to Claude format
            claude_response = self._convert_kimi_to_claude_response(kimi_response)

            return claude_response

        except httpx.HTTPError as e:
            # Return error in Claude format
            return {
                'id': 'error',
                'type': 'message',
                'role': 'assistant',
                'content': [
                    {
                        'type': 'text',
                        'text': f'Kimi API error: {str(e)}'
                    }
                ],
                'model': 'error',
                'stop_reason': 'error',
                'usage': {'input_tokens': 0, 'output_tokens': 0}
            }

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


# Usage example
if __name__ == '__main__':
    import asyncio

    async def test_kimi_adapter():
        adapter = KimiAdapter()

        # Test message
        messages = [
            {
                'role': 'user',
                'content': 'Explain SOAP note format for Australian medical practice in 2 sentences.'
            }
        ]

        response = await adapter.create_message(
            model='claude-3-5-sonnet-20241022',
            messages=messages,
            max_tokens=500,
            temperature=0.3
        )

        print("Response:")
        print(json.dumps(response, indent=2))

        await adapter.close()

    asyncio.run(test_kimi_adapter())
