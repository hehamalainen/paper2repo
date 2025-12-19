"""LLM utilities for provider selection, token management, and hybrid routing."""
from typing import Any, Dict, List, Optional, Callable
from enum import Enum
import json
import logging
import re

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
    ):
        self.provider = provider
        self.fast_model = fast_model
        self.balanced_model = balanced_model
        self.powerful_model = powerful_model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.api_key = api_key


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
    
    # Default system message for OpenAI
    DEFAULT_SYSTEM_MESSAGE = (
        "You are a helpful AI assistant specialized in understanding and "
        "generating code from research papers."
    )
    
    def __init__(self, config: LLMConfig, token_budget: Optional[TokenBudget] = None):
        self.config = config
        self.token_budget = token_budget or TokenBudget()
        self.router = HybridRouter(config)
        self._openai_client = None
        
        # Initialize OpenAI client if using OpenAI provider
        if self.config.provider == LLMProvider.OPENAI and self.config.api_key:
            try:
                import openai
                self._openai_client = openai.OpenAI(api_key=self.config.api_key)
            except ImportError:
                logger.warning("OpenAI library not installed. Install with: pip install openai")
                self._openai_client = None
    
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
        
        # For mock mode, return a simple response
        if self.config.provider == LLMProvider.MOCK:
            return self._mock_generate(prompt, agent_name)
        
        # Implement OpenAI provider
        if self.config.provider == LLMProvider.OPENAI:
            return self._openai_generate(
                prompt=prompt,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
        
        # Fallback to mock if provider not implemented
        logger.warning(f"Provider {self.config.provider} not implemented, using mock")
        return self._mock_generate(prompt, agent_name)
    
    def _openai_generate(
        self,
        prompt: str,
        model: str,
        max_tokens: int,
        temperature: float,
        **kwargs
    ) -> str:
        """Generate text using OpenAI API.
        
        Args:
            prompt: Input prompt
            model: Model name
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional OpenAI-specific arguments
            
        Returns:
            Generated text
        """
        if not self._openai_client:
            raise RuntimeError(
                "OpenAI client not initialized. Ensure API key is provided and openai library is installed."
            )
        
        try:
            response = self._openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": self.DEFAULT_SYSTEM_MESSAGE},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            
            # Extract the generated text
            if not response.choices or not response.choices[0].message.content:
                raise RuntimeError("OpenAI API returned empty response")
            
            generated_text = response.choices[0].message.content
            
            # Log actual token usage
            if hasattr(response, 'usage') and response.usage:
                actual_tokens = response.usage.total_tokens
                logger.info(f"OpenAI API call completed. Tokens used: {actual_tokens}")
            
            return generated_text
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise RuntimeError(f"OpenAI API call failed: {e}")
    
    def _mock_generate(self, prompt: str, agent_name: str) -> str:
        """Generate mock response for testing."""
        return json.dumps({
            "agent": agent_name,
            "response": f"Mock response for {agent_name}",
            "status": "success"
        }, indent=2)
    
    def get_budget_report(self) -> Dict[str, Any]:
        """Get token budget usage report."""
        return self.token_budget.get_usage_report()
