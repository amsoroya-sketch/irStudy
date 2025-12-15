"""
Ollama Local LLM Client
Interface for interacting with local Ollama models
"""

import logging
from typing import List, Dict, Optional
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OllamaClient:
    """Client for interacting with local Ollama LLMs"""

    # Model registry with recommended use cases
    MODELS = {
        'meditron:7b': {
            'description': 'Medical-specific LLM trained on medical literature',
            'best_for': ['medical_facts', 'clinical_reasoning', 'medical_qa'],
            'temperature': 0.3,
        },
        'biomistral:7b': {
            'description': 'BioMedical LLM optimized for medical domain',
            'best_for': ['biomedical_text', 'research', 'medical_terminology'],
            'temperature': 0.3,
        },
        'llama3.1:70b': {
            'description': 'Best reasoning capabilities, largest model',
            'best_for': ['complex_reasoning', 'question_generation', 'validation'],
            'temperature': 0.7,
        },
        'mixtral:8x7b': {
            'description': 'Mixture of Experts, excellent quality',
            'best_for': ['content_generation', 'mcq_creation', 'explanations'],
            'temperature': 0.7,
        },
        'deepseek-coder:6.7b': {
            'description': 'Code and structured output generation',
            'best_for': ['structured_output', 'json_generation', 'code'],
            'temperature': 0.2,
        },
        'qwen2.5:7b': {
            'description': 'General purpose, fast',
            'best_for': ['general_tasks', 'fast_inference', 'simple_qa'],
            'temperature': 0.5,
        },
        'qwen2.5vl:7b': {
            'description': 'Vision-language model for images',
            'best_for': ['image_analysis', 'diagram_interpretation', 'charts'],
            'temperature': 0.5,
        },
        'phi3:mini': {
            'description': 'Smallest, fastest model for simple tasks',
            'best_for': ['simple_classification', 'quick_tasks', 'lightweight'],
            'temperature': 0.3,
        },
    }

    def __init__(self, base_url: str = "http://localhost:11434"):
        """
        Initialize Ollama client

        Args:
            base_url: Ollama server URL
        """
        self.base_url = base_url
        logger.info(f"Initialized Ollama client at {base_url}")

    def get_model(self, model_name: str, temperature: Optional[float] = None, streaming: bool = False) -> Ollama:
        """
        Get Ollama model instance

        Args:
            model_name: Name of the model (e.g., 'meditron:7b')
            temperature: Sampling temperature (0.0-1.0), uses default if None
            streaming: Enable streaming output

        Returns:
            Ollama model instance
        """
        if model_name not in self.MODELS:
            logger.warning(f"Model '{model_name}' not in registry, using anyway")
            default_temp = 0.5
        else:
            default_temp = self.MODELS[model_name]['temperature']

        temp = temperature if temperature is not None else default_temp

        callbacks = [StreamingStdOutCallbackHandler()] if streaming else None

        return Ollama(
            model=model_name,
            base_url=self.base_url,
            temperature=temp,
            callbacks=callbacks
        )

    def generate(self, prompt: str, model_name: str = "meditron:7b", temperature: Optional[float] = None) -> str:
        """
        Generate text using specified model

        Args:
            prompt: Input prompt
            model_name: Model to use
            temperature: Sampling temperature

        Returns:
            Generated text
        """
        model = self.get_model(model_name, temperature)
        response = model.invoke(prompt)
        return response

    def generate_with_template(self, template: str, variables: Dict, model_name: str = "meditron:7b") -> str:
        """
        Generate using a prompt template

        Args:
            template: Prompt template string with {variables}
            variables: Dictionary of template variables
            model_name: Model to use

        Returns:
            Generated text
        """
        prompt_template = PromptTemplate(
            input_variables=list(variables.keys()),
            template=template
        )

        model = self.get_model(model_name)
        chain = prompt_template | model

        response = chain.invoke(variables)
        return response

    def list_available_models(self) -> List[str]:
        """List all models in registry"""
        return list(self.MODELS.keys())

    def get_model_info(self, model_name: str) -> Dict:
        """Get information about a model"""
        return self.MODELS.get(model_name, {})

    def recommend_model(self, task: str) -> str:
        """
        Recommend best model for a task

        Args:
            task: Task type (e.g., 'medical_qa', 'question_generation')

        Returns:
            Recommended model name
        """
        for model_name, info in self.MODELS.items():
            if task in info.get('best_for', []):
                logger.info(f"Recommended model for '{task}': {model_name}")
                return model_name

        # Default to meditron for medical tasks
        logger.info(f"No specific recommendation for '{task}', using meditron:7b")
        return 'meditron:7b'


# Convenience functions
def get_medical_expert() -> Ollama:
    """Get medical expert model (Meditron)"""
    client = OllamaClient()
    return client.get_model('meditron:7b')


def get_question_generator() -> Ollama:
    """Get best model for question generation"""
    client = OllamaClient()
    return client.get_model('mixtral:8x7b', temperature=0.7)


def get_validator() -> Ollama:
    """Get best model for validation"""
    client = OllamaClient()
    return client.get_model('llama3.1:70b', temperature=0.3)


def get_fast_model() -> Ollama:
    """Get fast model for simple tasks"""
    client = OllamaClient()
    return client.get_model('phi3:mini')


if __name__ == "__main__":
    # Test the client
    client = OllamaClient()

    print("Available models:")
    for model in client.list_available_models():
        info = client.get_model_info(model)
        print(f"  - {model}: {info.get('description', 'No description')}")

    print("\nTesting medical expert model...")
    response = client.generate(
        prompt="What are the symptoms of acute coronary syndrome?",
        model_name="meditron:7b"
    )
    print(f"Response: {response[:200]}...")
