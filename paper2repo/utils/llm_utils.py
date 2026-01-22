"""LLM utilities for provider selection, token management, and hybrid routing."""
from typing import Any, Dict, List, Optional, Callable
from enum import Enum
import json
import logging
import re
import os

from .llm_providers.base import BaseLLMProvider, LLMMessage
from .llm_providers.mock_provider import MockLLMProvider

logger = logging.getLogger(__name__)


def extract_json_from_response(response: str) -> Dict[str, Any]:
    """Extract JSON from LLM response, handling markdown code blocks.
    
    Args:
        response: Raw LLM response text
        
    Returns:
        Parsed JSON dictionary
        
    Raises:
        ValueError: If JSON cannot be extracted
    """
    # Try direct JSON parsing first
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        pass
    
    # Try to extract JSON from markdown code blocks
    # Look for ```json ... ``` or ``` ... ```
    json_pattern = r'```(?:json)?\s*\n?(.*?)\n?```'
    matches = re.findall(json_pattern, response, re.DOTALL)
    
    if matches:
        for match in matches:
            try:
                return json.loads(match.strip())
            except json.JSONDecodeError:
                continue
    
    # Try to find JSON-like content between first { and last } or [ and ]
    # This is a simple heuristic that works for most cases
    stripped = response.strip()
    
    # Try to extract object
    if '{' in stripped and '}' in stripped:
        start = stripped.find('{')
        end = stripped.rfind('}')
        if start < end:
            try:
                return json.loads(stripped[start:end+1])
            except json.JSONDecodeError:
                pass
    
    # Try to extract array
    if '[' in stripped and ']' in stripped:
        start = stripped.find('[')
        end = stripped.rfind(']')
        if start < end:
            try:
                return json.loads(stripped[start:end+1])
            except json.JSONDecodeError:
                pass
    
    # If all else fails, raise an error
    raise ValueError("Could not extract valid JSON from response")


class LLMProvider(Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"
    MOCK = "mock"


class ModelTier(Enum):
    """Model capability tiers."""
    FAST = "fast"  # Fast, cheap models for simple tasks
    BALANCED = "balanced"  # Balanced models for most tasks
    POWERFUL = "powerful"  # Most capable models for complex tasks


class LLMConfig:
    """Configuration for LLM provider and models."""
    
    def __init__(
        self,
        provider: LLMProvider = LLMProvider.MOCK,
        fast_model: str = "gpt-4o-mini",
        balanced_model: str = "gpt-4o-mini",
        powerful_model: str = "gpt-4o",
        max_tokens: int = 4096,
        temperature: float = 0.7,
        api_key: Optional[str] = None,
        api_timeout: int = 60,
        max_retries: int = 3,
    ):
        self.provider = provider
        self.fast_model = fast_model
        self.balanced_model = balanced_model
        self.powerful_model = powerful_model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.api_key = api_key
        self.api_timeout = api_timeout
        self.max_retries = max_retries


class TokenBudget:
    """Track and manage token usage across agents."""
    
    def __init__(self, total_budget: int = 1_000_000):
        """Initialize token budget.
        
        Args:
            total_budget: Total token budget for the pipeline
        """
        self.total_budget = total_budget
        self.used_tokens = 0
        self.agent_usage: Dict[str, int] = {}
    
    def allocate(self, agent_name: str, tokens: int) -> bool:
        """Allocate tokens to an agent.
        
        Args:
            agent_name: Name of the agent
            tokens: Number of tokens to allocate
            
        Returns:
            True if allocation successful, False if over budget
        """
        if self.used_tokens + tokens > self.total_budget:
            return False
        
        self.used_tokens += tokens
        self.agent_usage[agent_name] = self.agent_usage.get(agent_name, 0) + tokens
        return True
    
    def get_remaining(self) -> int:
        """Get remaining token budget."""
        return self.total_budget - self.used_tokens
    
    def get_usage_report(self) -> Dict[str, Any]:
        """Get usage report."""
        return {
            "total_budget": self.total_budget,
            "used_tokens": self.used_tokens,
            "remaining": self.get_remaining(),
            "agent_usage": self.agent_usage,
            "utilization": self.used_tokens / self.total_budget if self.total_budget > 0 else 0
        }


class HybridRouter:
    """Route requests to appropriate model tier based on complexity."""
    
    def __init__(self, config: LLMConfig):
        self.config = config
    
    def select_model(self, task_complexity: ModelTier) -> str:
        """Select appropriate model based on task complexity.
        
        Args:
            task_complexity: Complexity tier of the task
            
        Returns:
            Model name to use
        """
        if task_complexity == ModelTier.FAST:
            return self.config.fast_model
        elif task_complexity == ModelTier.BALANCED:
            return self.config.balanced_model
        else:
            return self.config.powerful_model


class LLMClient:
    """Unified LLM client with provider abstraction."""
    
    def __init__(self, config: LLMConfig, token_budget: Optional[TokenBudget] = None):
        self.config = config
        self.token_budget = token_budget or TokenBudget()
        self.router = HybridRouter(config)
        self.provider = self._initialize_provider()
    
    def _initialize_provider(self) -> BaseLLMProvider:
        """Initialize the appropriate LLM provider based on configuration.
        
        Returns:
            Initialized provider instance
        """
        try:
            # Mock provider - no API key needed
            if self.config.provider == LLMProvider.MOCK:
                return MockLLMProvider(
                    max_retries=self.config.max_retries,
                    timeout=self.config.api_timeout
                )
            
            # OpenAI provider
            if self.config.provider == LLMProvider.OPENAI:
                api_key = self.config.api_key or os.environ.get("OPENAI_API_KEY")
                if not api_key:
                    logger.warning("OpenAI provider selected but no API key found. Falling back to mock provider.")
                    return MockLLMProvider(
                        max_retries=self.config.max_retries,
                        timeout=self.config.api_timeout
                    )
                
                try:
                    from .llm_providers.openai_provider import OpenAIProvider
                    return OpenAIProvider(
                        api_key=api_key,
                        max_retries=self.config.max_retries,
                        timeout=self.config.api_timeout
                    )
                except ImportError:
                    logger.warning("OpenAI SDK not available. Falling back to mock provider.")
                    return MockLLMProvider(
                        max_retries=self.config.max_retries,
                        timeout=self.config.api_timeout
                    )
            
            # Anthropic provider
            if self.config.provider == LLMProvider.ANTHROPIC:
                api_key = self.config.api_key or os.environ.get("ANTHROPIC_API_KEY")
                if not api_key:
                    logger.warning("Anthropic provider selected but no API key found. Falling back to mock provider.")
                    return MockLLMProvider(
                        max_retries=self.config.max_retries,
                        timeout=self.config.api_timeout
                    )
                
                try:
                    from .llm_providers.anthropic_provider import AnthropicProvider
                    return AnthropicProvider(
                        api_key=api_key,
                        max_retries=self.config.max_retries,
                        timeout=self.config.api_timeout
                    )
                except ImportError:
                    logger.warning("Anthropic SDK not available. Falling back to mock provider.")
                    return MockLLMProvider(
                        max_retries=self.config.max_retries,
                        timeout=self.config.api_timeout
                    )
            
            # Default to mock provider for unknown providers
            logger.warning(f"Unknown provider {self.config.provider}. Falling back to mock provider.")
            return MockLLMProvider(
                max_retries=self.config.max_retries,
                timeout=self.config.api_timeout
            )
        except Exception as e:
            # Catch any unexpected errors during provider initialization
            logger.error(f"Error initializing provider: {e}. Falling back to mock provider.")
            return MockLLMProvider(
                max_retries=self.config.max_retries,
                timeout=self.config.api_timeout
            )
    
    def generate(
        self,
        prompt: str,
        agent_name: str,
        model_tier: ModelTier = ModelTier.BALANCED,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> str:
        """Generate text from LLM.
        
        Args:
            prompt: Input prompt
            agent_name: Name of calling agent
            model_tier: Model complexity tier
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional provider-specific arguments
            
        Returns:
            Generated text
        """
        model = self.router.select_model(model_tier)
        max_tokens = max_tokens or self.config.max_tokens
        temperature = temperature or self.config.temperature
        
        # Estimate token usage (rough approximation)
        estimated_tokens = len(prompt.split()) * 2 + max_tokens
        
        if not self.token_budget.allocate(agent_name, estimated_tokens):
            raise RuntimeError(
                f"Token budget exceeded. Remaining: {self.token_budget.get_remaining()}"
            )
        
        # Use the provider to generate response
        response = self.provider.generate(
            prompt=prompt,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs
        )
        
        # Log actual token usage if available
        if response.usage:
            try:
                # Handle both dict and object-like usage data
                if isinstance(response.usage, dict):
                    actual_tokens = response.usage.get('total_tokens', 0)
                else:
                    actual_tokens = getattr(response.usage, 'total_tokens', 0)
                logger.info(f"LLM API call completed. Tokens used: {actual_tokens}")
            except (AttributeError, TypeError):
                logger.debug("Could not extract token usage from response")
        
        content = response.content
        
        # For backward compatibility with mock provider, add agent key to response
        if isinstance(self.provider, MockLLMProvider):
            try:
                parsed = json.loads(content)
                if 'agent' not in parsed:
                    parsed['agent'] = agent_name
                    content = json.dumps(parsed, indent=2)
            except (json.JSONDecodeError, ValueError):
                # If not JSON, return as-is
                pass
                pass
        
        return content
    
    def get_budget_report(self) -> Dict[str, Any]:
        """Get token budget usage report."""
        return self.token_budget.get_usage_report()


def create_llm_config_from_dict(config_dict: Dict[str, Any]) -> LLMConfig:
    """Create LLMConfig from configuration dictionary.
    
    Args:
        config_dict: Configuration dictionary with 'llm' section
        
    Returns:
        LLMConfig instance
    """
    llm_config = config_dict.get('llm', {})
    
    # Parse provider
    provider_str = llm_config.get('provider', 'mock')
    try:
        provider = LLMProvider(provider_str.lower())
    except ValueError:
        logger.warning(f"Invalid provider '{provider_str}', defaulting to MOCK")
        provider = LLMProvider.MOCK
    
    # Parse models
    models = llm_config.get('models', {})
    fast_model = models.get('fast', 'gpt-4o-mini')
    balanced_model = models.get('balanced', 'gpt-4o')
    powerful_model = models.get('powerful', 'gpt-4-turbo')
    
    # Parse other settings
    max_tokens = llm_config.get('max_tokens', 4096)
    temperature = llm_config.get('temperature', 0.7)
    api_timeout = llm_config.get('api_timeout', 60)
    max_retries = llm_config.get('max_retries', 3)
    
    # API key from environment or config
    api_key = llm_config.get('api_key')
    if not api_key:
        if provider == LLMProvider.OPENAI:
            api_key = os.environ.get('OPENAI_API_KEY')
        elif provider == LLMProvider.ANTHROPIC:
            api_key = os.environ.get('ANTHROPIC_API_KEY')
    
    return LLMConfig(
        provider=provider,
        fast_model=fast_model,
        balanced_model=balanced_model,
        powerful_model=powerful_model,
        max_tokens=max_tokens,
        temperature=temperature,
        api_key=api_key,
        api_timeout=api_timeout,
        max_retries=max_retries
    )
