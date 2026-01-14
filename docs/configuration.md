# Configuration Quick Reference

## Overview

All LLM provider configuration is centralized in `src/agent_labs/config.py`. Configuration is loaded from environment variables following 12-factor app principles.

## Quick Start

1. **Copy the example file:**
   ```bash
   cp .env.example .env
   ```

2. **Set your provider:**
   ```bash
   # For local development (no API key needed)
   LLM_PROVIDER=ollama
   OLLAMA_MODEL=llama2

   # For production with OpenAI
   LLM_PROVIDER=openai
   OPENAI_MODEL=gpt-4
   OPENAI_API_KEY=sk-proj-xxxxx
   ```

3. **Run your code:**
   ```bash
   python scripts/interactive_agent.py
   ```

## Supported Providers

| Provider | Value | Requires API Key | Base URL |
|----------|-------|------------------|----------|
| Mock (Testing) | `mock` | No | - |
| Ollama (Local) | `ollama` | No | http://localhost:11434 |
| OpenAI | `openai` | Yes | https://api.openai.com/v1 |
| Anthropic (Claude) | `anthropic` | Yes | https://api.anthropic.com/v1 |
| Google (Gemini) | `google` | Yes | https://generativelanguage.googleapis.com/v1 |
| Azure OpenAI | `azure-openai` | Yes | Custom |

## Environment Variables

### Required

```bash
# Choose your provider
LLM_PROVIDER=ollama  # or: mock, openai, anthropic, google, azure-openai

# Specify model (provider-specific or generic)
OLLAMA_MODEL=llama2              # For Ollama
OPENAI_MODEL=gpt-4               # For OpenAI
ANTHROPIC_MODEL=claude-3-sonnet  # For Anthropic
# OR use generic:
LLM_MODEL=llama2                 # Works for any provider
```

### Authentication (Cloud Providers Only)

```bash
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx
GOOGLE_API_KEY=AIzaSyxxxxxxxxxxxxx
AZURE_OPENAI_API_KEY=xxxxxxxxxxxxx
```

### Optional Overrides

```bash
# Timeouts (seconds)
LLM_TIMEOUT=60
AGENT_TIMEOUT=300
TOOL_TIMEOUT=30

# Generation parameters
LLM_TEMPERATURE=0.7
TOOL_TEMPERATURE=0.3

# Agent behavior
AGENT_MAX_TURNS=10

# Provider-specific base URLs (for custom endpoints)
OLLAMA_BASE_URL=http://localhost:11434
OPENAI_BASE_URL=https://api.openai.com/v1
```

## Usage in Code

### New Code (Recommended)

```python
from agent_labs.config import get_config

# Get configuration (singleton, loads once)
config = get_config()

# Access provider details
print(f"Provider: {config.provider.value}")
print(f"Model: {config.provider_config.model}")
print(f"Base URL: {config.provider_config.base_url}")

# Validate configuration
valid, error = config.validate()
if not valid:
    print(f"Configuration error: {error}")

# Export as dictionary
config_dict = config.to_dict()
```

### Legacy Code (Backwards Compatible)

```python
from agent_labs.config import Config

# Direct access to Ollama settings
model = Config.OLLAMA_MODEL
base_url = Config.OLLAMA_BASE_URL
timeout = Config.OLLAMA_TIMEOUT
```

### Lab Code

```python
# Lab 05: Context Agent
from labs.context_agent import ContextAgent

# Model is now optional - reads from LLM_MODEL env var
agent = ContextAgent()  # Uses env var
# OR explicitly specify:
agent = ContextAgent(model="gpt-4")

# Lab 00: Hello Agent
from labs.hello_agent import main

# Automatically uses LLM_PROVIDER and provider-specific settings
asyncio.run(main())
```

## Common Scenarios

### Scenario 1: Local Development with Ollama

```bash
# .env
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama2
OLLAMA_BASE_URL=http://localhost:11434
```

**Setup:**
```bash
# Install Ollama from https://ollama.ai/
ollama serve
ollama pull llama2
python scripts/interactive_agent.py
```

### Scenario 2: CI/CD Testing (No LLM Required)

```bash
# .env or GitHub Actions
LLM_PROVIDER=mock
MOCK_MODEL=mock-gpt-4
```

**Usage:**
```bash
pytest tests/  # All tests use mock provider
```

### Scenario 3: Production with OpenAI

```bash
# .env.production
LLM_PROVIDER=openai
OPENAI_MODEL=gpt-4-turbo
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
AGENT_MAX_TURNS=20
AGENT_TIMEOUT=600
```

**Deployment:**
```bash
# Set via environment (not .env file in production)
export OPENAI_API_KEY="sk-proj-xxxxx"
python scripts/advanced_interactive_agent.py
```

### Scenario 4: Multi-Provider Testing

```bash
# Test with different providers
LLM_PROVIDER=ollama OLLAMA_MODEL=llama2 python scripts/interactive_agent.py
LLM_PROVIDER=mock python scripts/interactive_agent.py
LLM_PROVIDER=openai OPENAI_MODEL=gpt-4 python scripts/interactive_agent.py
```

## Configuration Validation

The system validates configuration on startup:

```python
from agent_labs.config import get_config

try:
    config = get_config()
    # Configuration is valid
except ValueError as e:
    # Configuration error with helpful message
    print(f"Error: {e}")
    # Example: "Model not specified for openai (set OPENAI_MODEL or LLM_MODEL)"
    # Example: "API key required for openai (set OPENAI_API_KEY)"
```

## Migration from Old Code

### Before (Hardcoded)

```python
# scripts/interactive_agent.py
self.model_name = "mistral:7b"  # Hardcoded!
provider = OllamaProvider(model="mistral:7b", base_url="http://localhost:11434")

# labs/05/context_agent.py
def __init__(self, model: str = "gpt-3.5-turbo"):  # Hardcoded!
```

### After (Configurable)

```python
# scripts/interactive_agent.py
config = get_config()
self.model_name = config.provider_config.model  # From env
provider = OllamaProvider(
    model=config.provider_config.model,
    base_url=config.provider_config.base_url
)

# labs/05/context_agent.py
import os
def __init__(self, model: Optional[str] = None):
    self.model = model or os.getenv("LLM_MODEL")  # Configurable!
```

## Troubleshooting

### Error: "Model not specified for openai"

**Solution:** Set the model in environment:
```bash
export OPENAI_MODEL=gpt-4
# OR
export LLM_MODEL=gpt-4
```

### Error: "API key required for openai"

**Solution:** Set your API key:
```bash
export OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
```

### Error: "Unknown LLM_PROVIDER: 'chatgpt'"

**Solution:** Use correct provider name:
```bash
# Wrong:
LLM_PROVIDER=chatgpt

# Right:
LLM_PROVIDER=openai
OPENAI_MODEL=gpt-4
```

### Configuration Not Updating

**Solution:** Reload configuration:
```python
from agent_labs.config import reload_config

# Change environment
os.environ["LLM_PROVIDER"] = "ollama"
os.environ["OLLAMA_MODEL"] = "mistral:7b"

# Reload to pick up changes
config = reload_config()
```

## Security Best Practices

1. **Never commit .env files** - Already in .gitignore
2. **Use .env.example for documentation** - No secrets in this file
3. **Production secrets** - Use environment variables or secret management
4. **Rotate API keys** - Regularly update cloud provider keys
5. **Separate environments** - Different keys for dev/staging/production

## Testing

### Unit Tests

```python
def test_with_mock_provider():
    os.environ["LLM_PROVIDER"] = "mock"
    config = reload_config()
    assert config.provider == LLMProvider.MOCK
```

### Integration Tests

```python
@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="No API key")
def test_with_openai():
    os.environ["LLM_PROVIDER"] = "openai"
    os.environ["OPENAI_MODEL"] = "gpt-3.5-turbo"
    config = reload_config()
    # Test with real OpenAI API
```

## Reference

- **Full documentation**: `.env.example`
- **Architecture review**: `.context/architecture-review-config-hardcoding.md`
- **Configuration module**: `src/agent_labs/config.py`
