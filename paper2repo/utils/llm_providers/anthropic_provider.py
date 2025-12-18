"""Anthropic LLM provider."""
import os
import time
import logging
from typing import List, Optional
from .base import BaseLLMProvider, LLMResponse, LLMMessage

logger = logging.getLogger(__name__)

# Try to import Anthropic SDK, but don't fail if not available
try:
    from anthropic import Anthropic, RateLimitError, APIError, APITimeoutError
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logger.warning("Anthropic SDK not available. Install with: pip install anthropic")


class AnthropicProvider(BaseLLMProvider):
    """Anthropic LLM provider."""
    
    SUPPORTED_MODELS = [
        "claude-3-5-sonnet-latest",
        "claude-3-5-haiku-latest",
        "claude-3-opus-latest"
    ]
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        max_retries: int = 3,
        timeout: int = 60,
    ):
        """Initialize Anthropic provider.
        
        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            max_retries: Maximum number of retries on failure
            timeout: Request timeout in seconds
        """
        if not ANTHROPIC_AVAILABLE:
            raise ImportError(
                "Anthropic SDK not available. Install with: pip install anthropic"
            )
        
        api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "Anthropic API key not provided. Set ANTHROPIC_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        super().__init__(api_key=api_key, max_retries=max_retries, timeout=timeout)
        self.client = Anthropic(api_key=api_key, timeout=timeout)
    
    def _retry_with_backoff(self, func, *args, **kwargs):
        """Execute function with exponential backoff retry logic.
        
        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Function result
            
        Raises:
            Exception after max retries exceeded
        """
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except RateLimitError as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff: 1, 2, 4 seconds
                    logger.warning(f"Rate limit hit, retrying in {wait_time}s... (attempt {attempt + 1}/{self.max_retries})")
                    time.sleep(wait_time)
                else:
                    logger.error("Max retries exceeded for rate limit")
            except (APIError, APITimeoutError) as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.warning(f"API error, retrying in {wait_time}s... (attempt {attempt + 1}/{self.max_retries})")
                    time.sleep(wait_time)
                else:
                    logger.error("Max retries exceeded for API error")
            except Exception as e:
                # Don't retry for other types of exceptions
                raise e
        
        raise last_exception
    
    def generate(
        self,
        prompt: str,
        model: str,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """Generate text from prompt using Anthropic.
        
        Args:
            prompt: Input prompt
            model: Model name to use
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional Anthropic parameters
            
        Returns:
            LLM response
        """
        messages = [LLMMessage(role="user", content=prompt)]
        return self.generate_chat(messages, model, max_tokens, temperature, **kwargs)
    
    def generate_chat(
        self,
        messages: List[LLMMessage],
        model: str,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs
    ) -> LLMResponse:
        """Generate response from chat messages using Anthropic.
        
        Args:
            messages: List of conversation messages
            model: Model name to use
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional Anthropic parameters
            
        Returns:
            LLM response
        """
        # Anthropic requires separate system message
        system_message = None
        anthropic_messages = []
        
        for msg in messages:
            if msg.role == "system":
                system_message = msg.content
            else:
                anthropic_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        # Make API call with retry logic
        def _make_request():
            params = {
                "model": model,
                "messages": anthropic_messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                **kwargs
            }
            if system_message:
                params["system"] = system_message
            
            return self.client.messages.create(**params)
        
        response = self._retry_with_backoff(_make_request)
        
        # Extract response data
        content = response.content[0].text if response.content else ""
        
        return LLMResponse(
            content=content,
            model=response.model,
            usage={
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens
            },
            finish_reason=response.stop_reason,
            raw_response=response
        )
    
    def count_tokens(self, text: str, model: str) -> int:
        """Count tokens in text (approximate for Anthropic).
        
        Args:
            text: Text to count tokens for
            model: Model name (for model-specific tokenization)
            
        Returns:
            Approximate number of tokens
        """
        # Anthropic doesn't provide a public tokenizer
        # Use approximation: ~4 characters per token
        return len(text) // 4
    
    def get_available_models(self) -> List[str]:
        """Get list of supported Anthropic models.
        
        Returns:
            List of model names
        """
        return self.SUPPORTED_MODELS
