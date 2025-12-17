"""OpenAI LLM provider."""
import os
import time
import logging
from typing import List, Optional
from .base import BaseLLMProvider, LLMResponse, LLMMessage

logger = logging.getLogger(__name__)

# Try to import OpenAI SDK, but don't fail if not available
try:
    from openai import OpenAI, RateLimitError, APIError, APITimeoutError
    import tiktoken
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI SDK not available. Install with: pip install openai tiktoken")


class OpenAIProvider(BaseLLMProvider):
    """OpenAI LLM provider."""
    
    SUPPORTED_MODELS = [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4-turbo",
        "gpt-3.5-turbo"
    ]
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        max_retries: int = 3,
        timeout: int = 60,
    ):
        """Initialize OpenAI provider.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            max_retries: Maximum number of retries on failure
            timeout: Request timeout in seconds
        """
        if not OPENAI_AVAILABLE:
            raise ImportError(
                "OpenAI SDK not available. Install with: pip install openai tiktoken"
            )
        
        api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OpenAI API key not provided. Set OPENAI_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        super().__init__(api_key=api_key, max_retries=max_retries, timeout=timeout)
        self.client = OpenAI(api_key=api_key, timeout=timeout)
    
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
        """Generate text from prompt using OpenAI.
        
        Args:
            prompt: Input prompt
            model: Model name to use
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional OpenAI parameters
            
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
        """Generate response from chat messages using OpenAI.
        
        Args:
            messages: List of conversation messages
            model: Model name to use
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional OpenAI parameters
            
        Returns:
            LLM response
        """
        # Convert to OpenAI message format
        openai_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        # Make API call with retry logic
        def _make_request():
            return self.client.chat.completions.create(
                model=model,
                messages=openai_messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
        
        response = self._retry_with_backoff(_make_request)
        
        # Extract response data
        choice = response.choices[0]
        content = choice.message.content
        
        return LLMResponse(
            content=content,
            model=response.model,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            },
            finish_reason=choice.finish_reason,
            raw_response=response
        )
    
    def count_tokens(self, text: str, model: str) -> int:
        """Count tokens in text using tiktoken.
        
        Args:
            text: Text to count tokens for
            model: Model name (for model-specific tokenization)
            
        Returns:
            Number of tokens
        """
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            # Fall back to cl100k_base for unknown models
            encoding = tiktoken.get_encoding("cl100k_base")
        
        return len(encoding.encode(text))
    
    def get_available_models(self) -> List[str]:
        """Get list of supported OpenAI models.
        
        Returns:
            List of model names
        """
        return self.SUPPORTED_MODELS
