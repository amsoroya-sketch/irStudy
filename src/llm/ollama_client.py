"""Simple Ollama client wrapper for LLM operations"""

import requests
import json
from typing import Optional, Dict, Any


class OllamaClient:
    """Simple Ollama client for LLM generation"""

    def __init__(self, model: str = "qwen2.5:7b", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url

    def generate(
        self,
        prompt: str,
        max_tokens: int = 1500,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """
        Generate text using Ollama API

        Args:
            prompt: The prompt to send to the LLM
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature

        Returns:
            Generated text as a string
        """
        url = f"{self.base_url}/api/generate"

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature
            }
        }

        try:
            # Longer timeout for complex medical reasoning prompts
            response = requests.post(url, json=payload, timeout=300)
            response.raise_for_status()

            result = response.json()
            generated_text = result.get("response", "")

            # Log if response is empty (debugging)
            if not generated_text:
                print(f"WARNING: Empty LLM response for prompt: {prompt[:100]}...")

            return generated_text

        except Exception as e:
            raise Exception(f"Ollama generation failed: {e}")
