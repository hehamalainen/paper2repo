"""Abstract base class for LLM providers."""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class LLMResponse:
    """Response from LLM provider."""
    content: str
    model: str
    usage: Dict[str, int]  # prompt_tokens, completion_tokens, total_tokens
    finish_reason: str = "stop"
    raw_response: Optional[Any] = None


@dataclass
class LLMMessage:
    """Message for LLM conversation."""
    role: str  # system, user, assistant
    content: str


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        max_retries: int = 3,
        timeout: int = 60,
    ):
        """Initialize LLM provider.
        
        Args:
            api_key: API key for the provider
            max_retries: Maximum number of retries on failure
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.max_retries = max_retries
        self.timeout = timeout
    
    @abstractmethod
    def generate(
        self,
        prompt: str,
        model: str,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """Generate text from prompt.
        
        Args:
            prompt: Input prompt
            model: Model name to use
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional provider-specific parameters
            
        Returns:
            LLM response
        """
        pass
    
    @abstractmethod
    def generate_chat(
        self,
        messages: List[LLMMessage],
        model: str,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """Generate response from chat messages.
        
        Args:
            messages: List of conversation messages
            model: Model name to use
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional provider-specific parameters
            
        Returns:
            LLM response
        """
        pass
    
    @abstractmethod
    def count_tokens(self, text: str, model: str) -> int:
        """Count tokens in text.
        
        Args:
            text: Text to count tokens for
            model: Model name (for model-specific tokenization)
            
        Returns:
            Number of tokens
        """
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Get list of available models.
        
        Returns:
            List of model names
        """
        pass
