# LLM Provider Integration Guide

This document explains how to configure and use real LLM APIs (OpenAI, Anthropic) with Paper2Repo.

## Overview

Paper2Repo supports multiple LLM providers with automatic fallback to a mock provider for testing. The system uses:

- **OpenAI** for GPT-4o, GPT-4o-mini, GPT-4-turbo models
- **Anthropic** for Claude 3.5 Sonnet, Claude 3.5 Haiku, Claude 3 Opus models
- **Mock** for testing without API costs

## Installation

### Basic Installation

The core dependencies are installed by default:

```bash
pip install paper2repo
```

### With LLM API Support

Install with LLM provider dependencies:

```bash
pip install openai>=1.0.0 anthropic>=0.18.0 tiktoken>=0.5.0
```

Or install from requirements.txt:

```bash
pip install -r requirements.txt
```

## Configuration

### Environment Variables

Create a `.env` file in your project root (use `.env.template` as a starting point):

```bash
# Choose your provider: openai, anthropic, or mock (default: mock)
LLM_PROVIDER=openai

# OpenAI API Key (required for OpenAI provider)
OPENAI_API_KEY=your-openai-api-key-here

# Anthropic API Key (required for Anthropic provider)
ANTHROPIC_API_KEY=your-anthropic-api-key-here
```

**Getting API Keys:**

- **OpenAI**: Get your API key from [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- **Anthropic**: Get your API key from [https://console.anthropic.com/](https://console.anthropic.com/)

### YAML Configuration

Edit `paper2repo/config/mcp_agent.config.yaml` to customize model selection and parameters:

```yaml
llm:
  provider: ${LLM_PROVIDER:-mock}  # openai, anthropic, or mock
  default_model: gpt-4o
  models:
    fast: gpt-4o-mini              # Fast, cheap models for simple tasks
    balanced: gpt-4o               # Balanced models for most tasks
    powerful: gpt-4-turbo          # Most capable models for complex tasks
  max_tokens: 4096
  temperature: 0.7
  api_timeout: 60                  # Request timeout in seconds
  max_retries: 3                   # Number of retry attempts on failure

budget:
  total_tokens: 1000000            # Total token budget
  per_agent_limit: 100000          # Per-agent token limit
```

## Usage

### Programmatic Usage

```python
from paper2repo.utils.llm_utils import (
    LLMClient,
    LLMConfig,
    LLMProvider,
    ModelTier,
    TokenBudget,
    create_llm_config_from_dict
)

# Method 1: Using config file
from paper2repo.utils.config_loader import get_config

config_loader = get_config()
llm_config = create_llm_config_from_dict(config_loader.config)
client = LLMClient(llm_config)

# Method 2: Manual configuration
config = LLMConfig(
    provider=LLMProvider.OPENAI,
    fast_model="gpt-4o-mini",
    balanced_model="gpt-4o",
    powerful_model="gpt-4-turbo",
    max_tokens=4096,
    temperature=0.7,
    api_timeout=60,
    max_retries=3
)

# Optional: Set custom token budget
budget = TokenBudget(total_budget=500000)
client = LLMClient(config, token_budget=budget)

# Generate text with automatic model tier selection
response = client.generate(
    prompt="Explain the transformer architecture",
    agent_name="my_agent",
    model_tier=ModelTier.BALANCED  # FAST, BALANCED, or POWERFUL
)

print(response)

# Check token usage
report = client.get_budget_report()
print(f"Tokens used: {report['used_tokens']:,}/{report['total_budget']:,}")
print(f"Remaining: {report['remaining']:,}")
```

### Model Tier Selection

The system provides three model tiers for different task complexities:

| Tier | OpenAI Models | Anthropic Models | Use Case |
|------|---------------|------------------|----------|
| **FAST** | gpt-4o-mini | claude-3-5-haiku-latest | Simple tasks, quick responses, low cost |
| **BALANCED** | gpt-4o | claude-3-5-sonnet-latest | Most general tasks, good balance |
| **POWERFUL** | gpt-4-turbo | claude-3-opus-latest | Complex reasoning, deep analysis |

### Token Budget Management

The system automatically tracks token usage and prevents over-spending:

```python
# Initialize with budget
budget = TokenBudget(total_budget=100000)
client = LLMClient(config, token_budget=budget)

# Budget is automatically tracked per request
try:
    response = client.generate(
        prompt="Your prompt here",
        agent_name="my_agent",
        model_tier=ModelTier.FAST
    )
except RuntimeError as e:
    print(f"Budget exceeded: {e}")

# Get detailed usage report
report = client.get_budget_report()
print("Token Usage Report:")
print(f"  Total Budget: {report['total_budget']:,}")
print(f"  Used: {report['used_tokens']:,}")
print(f"  Remaining: {report['remaining']:,}")
print(f"  Utilization: {report['utilization']:.1%}")
print("\nPer-Agent Usage:")
for agent, tokens in report['agent_usage'].items():
    print(f"  {agent}: {tokens:,} tokens")
```

## Provider-Specific Features

### OpenAI Provider

- **Accurate token counting** using tiktoken library
- **Streaming support** (optional, set `stream=True` in kwargs)
- **Supported models**: gpt-4o, gpt-4o-mini, gpt-4-turbo, gpt-3.5-turbo

```python
from paper2repo.utils.llm_providers.openai_provider import OpenAIProvider

provider = OpenAIProvider(api_key="your-key", max_retries=3, timeout=60)
response = provider.generate(
    prompt="Hello, GPT!",
    model="gpt-4o",
    max_tokens=100,
    temperature=0.7
)
print(response.content)
print(f"Tokens used: {response.usage['total_tokens']}")
```

### Anthropic Provider

- **Approximate token counting** (~4 chars per token)
- **Supported models**: claude-3-5-sonnet-latest, claude-3-5-haiku-latest, claude-3-opus-latest

```python
from paper2repo.utils.llm_providers.anthropic_provider import AnthropicProvider

provider = AnthropicProvider(api_key="your-key", max_retries=3, timeout=60)
response = provider.generate(
    prompt="Hello, Claude!",
    model="claude-3-5-sonnet-latest",
    max_tokens=100,
    temperature=0.7
)
print(response.content)
print(f"Tokens used: {response.usage['total_tokens']}")
```

### Mock Provider (Default)

The mock provider is used automatically when:
- No provider is specified (default)
- API keys are not set
- SDK dependencies are not installed

It's perfect for:
- Testing without API costs
- Development without API keys
- CI/CD pipelines

```python
from paper2repo.utils.llm_providers.mock_provider import MockLLMProvider

provider = MockLLMProvider()
response = provider.generate(
    prompt="Test prompt",
    model="gpt-4o",
    max_tokens=100
)
# Returns mock response without making API calls
```

## Error Handling

The system includes robust error handling:

### Automatic Retries with Exponential Backoff

API errors and rate limits trigger automatic retries with exponential backoff (1s, 2s, 4s).

### Graceful Fallback

When API keys are missing or SDKs are not installed, the system automatically falls back to the mock provider:

```python
# Set provider to OpenAI, but no API key is set
config = LLMConfig(provider=LLMProvider.OPENAI)
client = LLMClient(config)

# Automatically falls back to mock provider with a warning
response = client.generate(
    prompt="Test",
    agent_name="test_agent",
    model_tier=ModelTier.BALANCED
)
# Still works, using mock provider!
```

### Budget Protection

The system prevents over-spending by tracking token usage:

```python
budget = TokenBudget(total_budget=1000)  # Small budget
client = LLMClient(config, token_budget=budget)

try:
    # This will succeed
    response1 = client.generate(
        prompt="Short prompt",
        agent_name="agent1",
        model_tier=ModelTier.FAST
    )
    
    # This will fail if budget exceeded
    response2 = client.generate(
        prompt="Very long prompt..." * 100,
        agent_name="agent2",
        model_tier=ModelTier.POWERFUL
    )
except RuntimeError as e:
    print(f"Budget exceeded: {e}")
```

## Best Practices

1. **Use appropriate model tiers**: Don't use POWERFUL tier for simple tasks
2. **Set realistic budgets**: Monitor usage and adjust budgets accordingly
3. **Handle errors gracefully**: Wrap API calls in try-except blocks
4. **Secure API keys**: Never commit API keys to source control; use environment variables
5. **Monitor token usage**: Check budget reports regularly
6. **Test with mock provider first**: Validate your code without API costs

## Troubleshooting

### Provider Falls Back to Mock

**Problem**: System uses mock provider even though you set OpenAI/Anthropic

**Solutions**:
1. Check that API key is set in environment: `echo $OPENAI_API_KEY`
2. Verify SDK is installed: `pip list | grep openai`
3. Check for import errors in logs

### Budget Exceeded Errors

**Problem**: RuntimeError: Token budget exceeded

**Solutions**:
1. Increase total budget in config
2. Use FAST tier for simple tasks
3. Optimize prompts to be more concise
4. Check per-agent usage in budget report

### Rate Limit Errors

**Problem**: API returns rate limit errors even after retries

**Solutions**:
1. Increase `max_retries` in config
2. Add delays between requests
3. Upgrade your API plan
4. Use FAST tier models (lower rate limits)

### Timeout Errors

**Problem**: Requests timeout

**Solutions**:
1. Increase `api_timeout` in config
2. Reduce `max_tokens` parameter
3. Check network connectivity
4. Use faster model tiers

## Support

For issues or questions:
- GitHub Issues: [https://github.com/hehamalainen/paper2repo/issues](https://github.com/hehamalainen/paper2repo/issues)
- Documentation: [https://github.com/hehamalainen/paper2repo#readme](https://github.com/hehamalainen/paper2repo#readme)
