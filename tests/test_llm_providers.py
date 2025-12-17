"""Tests for LLM providers."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from paper2repo.utils.llm_utils import (
    LLMClient,
    LLMConfig,
    LLMProvider,
    ModelTier,
    TokenBudget,
    HybridRouter,
    create_llm_config_from_dict,
)
from paper2repo.utils.llm_providers.base import BaseLLMProvider, LLMResponse, LLMMessage
from paper2repo.utils.llm_providers.mock_provider import MockLLMProvider


class TestMockProvider:
    """Test mock LLM provider."""
    
    def test_initialization(self):
        """Test mock provider initialization."""
        provider = MockLLMProvider()
        assert provider.api_key == "mock"
        assert provider.max_retries == 3
    
    def test_generate(self):
        """Test mock text generation."""
        provider = MockLLMProvider()
        response = provider.generate(
            prompt="Test prompt",
            model="gpt-4o",
            max_tokens=100,
            temperature=0.7
        )
        
        assert isinstance(response, LLMResponse)
        assert response.model == "gpt-4o"
        assert response.content is not None
        assert "mock" in response.content.lower() or "response" in response.content.lower()
        assert response.usage["total_tokens"] > 0
        assert response.finish_reason == "stop"
    
    def test_generate_chat(self):
        """Test mock chat generation."""
        provider = MockLLMProvider()
        messages = [
            LLMMessage(role="system", content="You are a helpful assistant"),
            LLMMessage(role="user", content="Hello!")
        ]
        
        response = provider.generate_chat(
            messages=messages,
            model="gpt-4o",
            max_tokens=100,
            temperature=0.7
        )
        
        assert isinstance(response, LLMResponse)
        assert response.content is not None
        assert response.usage["total_tokens"] > 0
    
    def test_count_tokens(self):
        """Test token counting."""
        provider = MockLLMProvider()
        text = "This is a test with five words"
        tokens = provider.count_tokens(text, "gpt-4o")
        
        # Mock provider uses ~2 tokens per word
        assert tokens > 0
        assert tokens == len(text.split()) * 2
    
    def test_get_available_models(self):
        """Test getting available models."""
        provider = MockLLMProvider()
        models = provider.get_available_models()
        
        assert isinstance(models, list)
        assert len(models) > 0
        assert "gpt-4o" in models
        assert "claude-3-5-sonnet-latest" in models


class TestOpenAIProvider:
    """Test OpenAI LLM provider."""
    
    def test_import_availability(self):
        """Test that OpenAI provider handles missing SDK gracefully."""
        try:
            from paper2repo.utils.llm_providers.openai_provider import OPENAI_AVAILABLE
            # If SDK is not available, OPENAI_AVAILABLE should be False
            if not OPENAI_AVAILABLE:
                pytest.skip("OpenAI SDK not installed - this is expected")
            else:
                # SDK is available, verify we can import the provider
                from paper2repo.utils.llm_providers.openai_provider import OpenAIProvider
                assert OpenAIProvider is not None
        except ImportError:
            pytest.skip("OpenAI SDK not installed - this is expected")


class TestAnthropicProvider:
    """Test Anthropic LLM provider."""
    
    def test_import_availability(self):
        """Test that Anthropic provider handles missing SDK gracefully."""
        try:
            from paper2repo.utils.llm_providers.anthropic_provider import ANTHROPIC_AVAILABLE
            # If SDK is not available, ANTHROPIC_AVAILABLE should be False
            if not ANTHROPIC_AVAILABLE:
                pytest.skip("Anthropic SDK not installed - this is expected")
            else:
                # SDK is available, verify we can import the provider
                from paper2repo.utils.llm_providers.anthropic_provider import AnthropicProvider
                assert AnthropicProvider is not None
        except ImportError:
            pytest.skip("Anthropic SDK not installed - this is expected")


class TestTokenBudget:
    """Test token budget management."""
    
    def test_initialization(self):
        """Test token budget initialization."""
        budget = TokenBudget(total_budget=1000)
        assert budget.total_budget == 1000
        assert budget.used_tokens == 0
        assert budget.get_remaining() == 1000
    
    def test_allocate(self):
        """Test token allocation."""
        budget = TokenBudget(total_budget=1000)
        
        # Successful allocation
        result = budget.allocate("agent1", 300)
        assert result is True
        assert budget.used_tokens == 300
        assert budget.get_remaining() == 700
        
        # Another allocation
        result = budget.allocate("agent2", 400)
        assert result is True
        assert budget.used_tokens == 700
        
        # Over budget
        result = budget.allocate("agent3", 500)
        assert result is False
        assert budget.used_tokens == 700  # Should not change
    
    def test_agent_usage_tracking(self):
        """Test per-agent usage tracking."""
        budget = TokenBudget(total_budget=1000)
        
        budget.allocate("agent1", 300)
        budget.allocate("agent1", 100)
        budget.allocate("agent2", 200)
        
        assert budget.agent_usage["agent1"] == 400
        assert budget.agent_usage["agent2"] == 200
    
    def test_usage_report(self):
        """Test usage report generation."""
        budget = TokenBudget(total_budget=1000)
        budget.allocate("agent1", 600)
        
        report = budget.get_usage_report()
        
        assert report["total_budget"] == 1000
        assert report["used_tokens"] == 600
        assert report["remaining"] == 400
        assert report["utilization"] == 0.6
        assert "agent1" in report["agent_usage"]


class TestHybridRouter:
    """Test hybrid model routing."""
    
    def test_model_selection(self):
        """Test model selection based on tier."""
        config = LLMConfig(
            fast_model="gpt-4o-mini",
            balanced_model="gpt-4o",
            powerful_model="gpt-4-turbo"
        )
        router = HybridRouter(config)
        
        assert router.select_model(ModelTier.FAST) == "gpt-4o-mini"
        assert router.select_model(ModelTier.BALANCED) == "gpt-4o"
        assert router.select_model(ModelTier.POWERFUL) == "gpt-4-turbo"


class TestLLMClient:
    """Test unified LLM client."""
    
    def test_initialization(self):
        """Test LLM client initialization."""
        config = LLMConfig(provider=LLMProvider.MOCK)
        client = LLMClient(config)
        
        assert client.config.provider == LLMProvider.MOCK
        assert isinstance(client.provider, MockLLMProvider)
        assert isinstance(client.token_budget, TokenBudget)
    
    def test_generate_with_mock_provider(self):
        """Test text generation with mock provider."""
        config = LLMConfig(provider=LLMProvider.MOCK)
        client = LLMClient(config)
        
        response = client.generate(
            prompt="Test prompt",
            agent_name="test_agent",
            model_tier=ModelTier.BALANCED
        )
        
        assert isinstance(response, str)
        assert len(response) > 0
    
    def test_budget_tracking(self):
        """Test budget tracking during generation."""
        config = LLMConfig(provider=LLMProvider.MOCK)
        budget = TokenBudget(total_budget=10000)
        client = LLMClient(config, token_budget=budget)
        
        initial_remaining = budget.get_remaining()
        
        client.generate(
            prompt="Test prompt",
            agent_name="test_agent",
            model_tier=ModelTier.FAST
        )
        
        # Should have used some tokens
        assert budget.get_remaining() < initial_remaining
        assert budget.agent_usage.get("test_agent", 0) > 0
    
    def test_budget_exceeded(self):
        """Test behavior when budget is exceeded."""
        config = LLMConfig(provider=LLMProvider.MOCK)
        budget = TokenBudget(total_budget=10)  # Very small budget
        client = LLMClient(config, token_budget=budget)
        
        with pytest.raises(RuntimeError, match="Token budget exceeded"):
            client.generate(
                prompt="Test prompt " * 100,  # Large prompt
                agent_name="test_agent",
                model_tier=ModelTier.BALANCED
            )
    
    @patch.dict('os.environ', {}, clear=True)
    def test_fallback_to_mock_without_api_key(self):
        """Test fallback to mock provider when no API key is set."""
        config = LLMConfig(provider=LLMProvider.OPENAI)
        client = LLMClient(config)
        
        # Should fall back to mock provider
        assert isinstance(client.provider, MockLLMProvider)
    
    def test_model_tier_routing(self):
        """Test that model tier routing works correctly."""
        config = LLMConfig(
            provider=LLMProvider.MOCK,
            fast_model="gpt-4o-mini",
            balanced_model="gpt-4o",
            powerful_model="gpt-4-turbo"
        )
        client = LLMClient(config)
        
        # The router should select the correct model for each tier
        assert client.router.select_model(ModelTier.FAST) == "gpt-4o-mini"
        assert client.router.select_model(ModelTier.BALANCED) == "gpt-4o"
        assert client.router.select_model(ModelTier.POWERFUL) == "gpt-4-turbo"


class TestConfigLoading:
    """Test configuration loading."""
    
    def test_create_llm_config_from_dict(self):
        """Test creating LLMConfig from dictionary."""
        config_dict = {
            'llm': {
                'provider': 'openai',
                'models': {
                    'fast': 'gpt-4o-mini',
                    'balanced': 'gpt-4o',
                    'powerful': 'gpt-4-turbo'
                },
                'max_tokens': 2048,
                'temperature': 0.5,
                'api_timeout': 30,
                'max_retries': 5
            }
        }
        
        config = create_llm_config_from_dict(config_dict)
        
        assert config.provider == LLMProvider.OPENAI
        assert config.fast_model == 'gpt-4o-mini'
        assert config.balanced_model == 'gpt-4o'
        assert config.powerful_model == 'gpt-4-turbo'
        assert config.max_tokens == 2048
        assert config.temperature == 0.5
        assert config.api_timeout == 30
        assert config.max_retries == 5
    
    def test_create_llm_config_defaults(self):
        """Test creating LLMConfig with defaults."""
        config_dict = {'llm': {}}
        config = create_llm_config_from_dict(config_dict)
        
        assert config.provider == LLMProvider.MOCK
        assert config.max_tokens == 4096
        assert config.temperature == 0.7
    
    def test_create_llm_config_invalid_provider(self):
        """Test handling of invalid provider."""
        config_dict = {
            'llm': {
                'provider': 'invalid_provider'
            }
        }
        
        config = create_llm_config_from_dict(config_dict)
        
        # Should default to MOCK for invalid provider
        assert config.provider == LLMProvider.MOCK
