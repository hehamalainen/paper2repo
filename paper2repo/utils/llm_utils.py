"""LLM utilities for provider selection, token management, and hybrid routing."""
from typing import Any, Dict, List, Optional, Callable
from enum import Enum
import json
import os
import logging

from .llm_providers.base import BaseLLMProvider, LLMMessage
from .llm_providers.mock_provider import MockLLMProvider

logger = logging.getLogger(__name__)


def create_llm_config_from_dict(config_dict: Dict[str, Any]) -> 'LLMConfig':
    """Create LLMConfig from dictionary (e.g., loaded from YAML).
    
    Args:
        config_dict: Configuration dictionary with 'llm' key
        
    Returns:
        LLMConfig instance
    """
    llm_config = config_dict.get('llm', {})
    
    # Parse provider
    provider_str = llm_config.get('provider', 'mock').lower()
    try:
        provider = LLMProvider(provider_str)
    except ValueError:
        logger.warning(f"Unknown provider '{provider_str}', defaulting to mock")
        provider = LLMProvider.MOCK
    
    # Get model configuration
    models = llm_config.get('models', {})
    
    return LLMConfig(
        provider=provider,
        fast_model=models.get('fast', 'gpt-4o-mini'),
        balanced_model=models.get('balanced', 'gpt-4o'),
        powerful_model=models.get('powerful', 'gpt-4-turbo'),
        max_tokens=llm_config.get('max_tokens', 4096),
        temperature=llm_config.get('temperature', 0.7),
        api_timeout=llm_config.get('api_timeout', 60),
        max_retries=llm_config.get('max_retries', 3),
    )


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
        balanced_model: str = "gpt-4o",
        powerful_model: str = "gpt-4-turbo",
        max_tokens: int = 4096,
        temperature: float = 0.7,
        api_timeout: int = 60,
        max_retries: int = 3,
    ):
        self.provider = provider
        self.fast_model = fast_model
        self.balanced_model = balanced_model
        self.powerful_model = powerful_model
        self.max_tokens = max_tokens
        self.temperature = temperature
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
    
    def warn_if_approaching_limit(self, threshold: float = 0.8) -> None:
        """Warn if approaching budget limit.
        
        Args:
            threshold: Warning threshold as fraction of total budget (default 0.8 = 80%)
        """
        utilization = self.used_tokens / self.total_budget if self.total_budget > 0 else 0
        if utilization >= threshold:
            logger.warning(
                f"Token budget at {utilization:.1%} capacity "
                f"({self.used_tokens:,}/{self.total_budget:,} tokens used)"
            )


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
        self.provider = self._create_provider()
    
    def _create_provider(self) -> BaseLLMProvider:
        """Create the appropriate LLM provider based on configuration.
        
        Returns:
            LLM provider instance
        """
        provider_type = self.config.provider
        
        # Always try to use mock provider if no API keys are set
        if provider_type == LLMProvider.OPENAI:
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                logger.warning(
                    "OPENAI_API_KEY not set, falling back to mock provider. "
                    "Set the environment variable to use OpenAI."
                )
                return MockLLMProvider()
            
            try:
                from .llm_providers.openai_provider import OpenAIProvider
                return OpenAIProvider(
                    api_key=api_key,
                    max_retries=self.config.max_retries,
                    timeout=self.config.api_timeout
                )
            except ImportError as e:
                logger.warning(f"Failed to import OpenAI provider: {e}. Falling back to mock.")
                return MockLLMProvider()
        
        elif provider_type == LLMProvider.ANTHROPIC:
            api_key = os.environ.get("ANTHROPIC_API_KEY")
            if not api_key:
                logger.warning(
                    "ANTHROPIC_API_KEY not set, falling back to mock provider. "
                    "Set the environment variable to use Anthropic."
                )
                return MockLLMProvider()
            
            try:
                from .llm_providers.anthropic_provider import AnthropicProvider
                return AnthropicProvider(
                    api_key=api_key,
                    max_retries=self.config.max_retries,
                    timeout=self.config.api_timeout
                )
            except ImportError as e:
                logger.warning(f"Failed to import Anthropic provider: {e}. Falling back to mock.")
                return MockLLMProvider()
        
        else:
            # Default to mock provider
            return MockLLMProvider()
    
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
        
        # Count actual tokens in prompt
        prompt_tokens = self.provider.count_tokens(prompt, model)
        estimated_tokens = prompt_tokens + max_tokens
        
        # Check budget before making request
        if not self.token_budget.allocate(agent_name, estimated_tokens):
            raise RuntimeError(
                f"Token budget exceeded. Remaining: {self.token_budget.get_remaining():,} tokens"
            )
        
        # Warn if approaching budget limit
        self.token_budget.warn_if_approaching_limit()
        
        try:
            # Make LLM request through provider
            response = self.provider.generate(
                prompt=prompt,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            
            # Update token usage with actual usage
            actual_tokens = response.usage.get("total_tokens", estimated_tokens)
            token_diff = actual_tokens - estimated_tokens
            
            if token_diff != 0:
                # Adjust the budget with the difference
                self.token_budget.used_tokens += token_diff
                self.token_budget.agent_usage[agent_name] += token_diff
            
            logger.info(
                f"LLM request completed for {agent_name}: "
                f"{response.usage.get('prompt_tokens', 0)} prompt + "
                f"{response.usage.get('completion_tokens', 0)} completion = "
                f"{response.usage.get('total_tokens', 0)} total tokens"
            )
            
            return response.content
            
        except Exception as e:
            logger.error(f"LLM generation failed for {agent_name}: {e}")
            # Refund the estimated tokens since the request failed
            self.token_budget.used_tokens -= estimated_tokens
            if agent_name in self.token_budget.agent_usage:
                self.token_budget.agent_usage[agent_name] -= estimated_tokens
            raise
    
    def get_budget_report(self) -> Dict[str, Any]:
        """Get token budget usage report."""
        return self.token_budget.get_usage_report()
