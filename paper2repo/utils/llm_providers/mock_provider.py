"""Mock LLM provider for testing."""
from typing import List
import json
from .base import BaseLLMProvider, LLMResponse, LLMMessage


class MockLLMProvider(BaseLLMProvider):
    """Mock LLM provider for testing without real API calls."""
    
    def __init__(self, **kwargs):
        """Initialize mock provider."""
        super().__init__(api_key="mock", **kwargs)
    
    def generate(
        self,
        prompt: str,
        model: str,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """Generate mock response.
        
        Args:
            prompt: Input prompt
            model: Model name to use
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional parameters
            
        Returns:
            Mock LLM response
        """
        # Generate a simple mock response
        response_text = json.dumps({
            "model": model,
            "response": "This is a mock response for testing purposes.",
            "prompt_preview": prompt[:100] if len(prompt) > 100 else prompt,
            "status": "success"
        }, indent=2)
        
        # Estimate token usage
        prompt_tokens = len(prompt.split()) * 2
        completion_tokens = len(response_text.split()) * 2
        
        return LLMResponse(
            content=response_text,
            model=model,
            usage={
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens
            },
            finish_reason="stop"
        )
    
    def generate_chat(
        self,
        messages: List[LLMMessage],
        model: str,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """Generate mock chat response.
        
        Args:
            messages: List of conversation messages
            model: Model name to use
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional parameters
            
        Returns:
            Mock LLM response
        """
        # Convert messages to a single prompt for mock generation
        prompt_parts = []
        for msg in messages:
            prompt_parts.append(f"{msg.role}: {msg.content}")
        
        combined_prompt = "\n".join(prompt_parts)
        return self.generate(combined_prompt, model, max_tokens, temperature, **kwargs)
    
    def count_tokens(self, text: str, model: str) -> int:
        """Count tokens in text (approximate).
        
        Args:
            text: Text to count tokens for
            model: Model name (ignored for mock)
            
        Returns:
            Approximate number of tokens
        """
        # Simple approximation: ~2 tokens per word
        return len(text.split()) * 2
    
    def get_available_models(self) -> List[str]:
        """Get list of mock models.
        
        Returns:
            List of mock model names
        """
        return [
            "gpt-4o-mini",
            "gpt-4o",
            "gpt-4-turbo",
            "claude-3-5-haiku-latest",
            "claude-3-5-sonnet-latest",
            "claude-3-opus-latest"
        ]
