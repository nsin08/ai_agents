# Configuration System

## Overview

The AI Agents configuration system provides flexible, secure, and validated configuration management through multiple sources with clear precedence rules.

**Features:**
- **Multiple sources**: Explicit params, environment variables, YAML files, and defaults
- **Precedence-based**: Explicit > Env > File > Default
- **Pydantic v2 validation**: Type-safe with clear error messages
- **JSON Schema export**: Automatic schema generation for documentation/validation
- **Security-first**: API keys from environment only, never in files
- **Config sections**: app, models, tools, memory, engine, observability

**Configuration modules:**
- `src/agent_labs/config_v2.py` - Enhanced config system (recommended for new code)
- `src/agent_labs/config.py` - Legacy config (backward compatible)

## Quick Start

### Method 1: Using YAML Configuration Files (Recommended)

1. **Choose a configuration file:**
   ```bash
   # For local development with Ollama
   export CONFIG_FILE=config/local.yaml
   
   # For staging with OpenAI GPT-3.5
   export CONFIG_FILE=config/staging.yaml
   
   # For production with OpenAI GPT-4
   export CONFIG_FILE=config/production.yaml
   ```

2. **Set required secrets (for cloud providers):**
   ```bash
   # Only for OpenAI configurations
   export OPENAI_API_KEY=sk-proj-xxxxx
   ```

3. **Load and use configuration:**
   ```python
   from agent_labs.config_v2 import load_config
   
   config = load_config("config/local.yaml")
   print(f"Provider: {config.models.provider}")
   print(f"Model: {config.models.model}")
   ```

### Method 2: Using Environment Variables

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

### Method 3: Explicit Configuration (Testing)

```python
from agent_labs.config_v2 import AgentConfig

config = AgentConfig(
    models={"provider": "mock", "model": "test-model"},
    engine={"max_turns": 5}
)
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

## Configuration Precedence

The configuration system uses a clear precedence order when loading settings from multiple sources:

**Precedence Order: Explicit > Environment > YAML File > Defaults**

### Example: Understanding Precedence

```python
# config/staging.yaml contains:
# models:
#   provider: openai
#   model: gpt-3.5-turbo
#   timeout: 30

# Environment has:
# LLM_MODEL=gpt-4
# AGENT_MAX_TURNS=20

# Explicit override:
config = load_config(
    "config/staging.yaml",
    models={"timeout": 60}
)

# Result:
# - models.provider: "openai" (from YAML)
# - models.model: "gpt-4" (from ENV, overrides YAML)
# - models.timeout: 60 (from Explicit, overrides YAML)
# - engine.max_turns: 20 (from ENV, overrides YAML defaults)
```

### Why Precedence Matters

1. **Explicit parameters** - Unit tests and specific use cases
2. **Environment variables** - Deployment-specific secrets and overrides
3. **YAML files** - Environment profiles (local, staging, production)
4. **Defaults** - Sensible defaults for all settings

## Configuration Sections

Configuration is organized into six logical sections:

### 1. App Section (`app`)

Application-level settings.

**Fields:**
- `name` (str): Application name (default: "ai_agent")
- `mode` (enum): Execution mode - development, staging, production, test
- `debug` (bool): Enable debug logging
- `log_level` (str): Logging level (DEBUG, INFO, WARNING, ERROR)

**Example:**
```python
config = AgentConfig(app={
    "name": "my_agent",
    "mode": "production",
    "debug": False,
    "log_level": "WARNING"
})
```

**Environment Variables:**
```bash
APP_NAME=my_agent
APP_MODE=production
APP_DEBUG=false
LOG_LEVEL=WARNING
```

### 2. Models Section (`models`)

LLM provider and model configuration.

**Fields:**
- `provider` (enum): LLM provider (mock, ollama, openai, anthropic, google, azure-openai)
- `model` (str): Model name/identifier (required for non-mock providers)
- `base_url` (str): API base URL (auto-set for standard providers)
- `timeout` (int): Request timeout in seconds (1-600, default: 60)
- `temperature` (float): Generation temperature (0.0-2.0, default: 0.7)
- `max_tokens` (int): Maximum tokens to generate (optional)

**Example:**
```python
config = AgentConfig(models={
    "provider": "openai",
    "model": "gpt-4",
    "timeout": 30,
    "temperature": 0.7,
    "max_tokens": 4096
})
```

**Environment Variables:**
```bash
LLM_PROVIDER=openai  # or MODEL_PROVIDER
LLM_MODEL=gpt-4
LLM_BASE_URL=https://api.openai.com/v1
LLM_TIMEOUT=30
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=4096

# Provider-specific (overrides LLM_MODEL):
OPENAI_MODEL=gpt-4
ANTHROPIC_MODEL=claude-3-opus
OLLAMA_MODEL=llama2
```

### 3. Tools Section (`tools`)

Tool execution configuration.

**Fields:**
- `timeout` (int): Tool execution timeout in seconds (1-300, default: 30)
- `temperature` (float): Temperature for tool-related LLM calls (0.0-2.0, default: 0.3)
- `max_length` (int): Maximum tool output length in characters (default: 500)
- `allowlist` (list): Optional list of allowed tool names

**Example:**
```python
config = AgentConfig(tools={
    "timeout": 45,
    "temperature": 0.2,
    "max_length": 1000,
    "allowlist": ["calculator", "web_search"]
})
```

**Environment Variables:**
```bash
TOOL_TIMEOUT=45
TOOL_TEMPERATURE=0.2
TOOL_MAX_LENGTH=1000
TOOL_ALLOWLIST=calculator,web_search,file_read
```

### 4. Memory Section (`memory`)

Memory and context management configuration.

**Fields:**
- `short_term_size` (int): Number of conversation turns to keep (default: 10)
- `long_term_enabled` (bool): Enable long-term/RAG memory (default: false)
- `context_window` (int): Context window size in tokens (default: 4096)

**Example:**
```python
config = AgentConfig(memory={
    "short_term_size": 20,
    "long_term_enabled": True,
    "context_window": 8192
})
```

**Environment Variables:**
```bash
MEMORY_SHORT_TERM_SIZE=20
MEMORY_LONG_TERM_ENABLED=true
MEMORY_CONTEXT_WINDOW=8192
```

### 5. Engine Section (`engine`)

Agent orchestration engine configuration.

**Fields:**
- `max_turns` (int): Maximum reasoning turns before stopping (1-100, default: 10)
- `timeout` (int): Agent execution timeout in seconds (1-3600, default: 300)
- `enable_reflection` (bool): Enable reflection step (default: true)

**Example:**
```python
config = AgentConfig(engine={
    "max_turns": 20,
    "timeout": 600,
    "enable_reflection": True
})
```

**Environment Variables:**
```bash
AGENT_MAX_TURNS=20
AGENT_TIMEOUT=600
AGENT_ENABLE_REFLECTION=true
```

### 6. Observability Section (`observability`)

Monitoring, tracing, and logging configuration.

**Fields:**
- `enable_tracing` (bool): Enable distributed tracing (default: false)
- `enable_metrics` (bool): Enable metrics collection (default: false)
- `log_prompts` (bool): Log LLM prompts (default: false)
- `log_responses` (bool): Log LLM responses (default: false)

**Example:**
```python
config = AgentConfig(observability={
    "enable_tracing": True,
    "enable_metrics": True,
    "log_prompts": False,
    "log_responses": False
})
```

**Environment Variables:**
```bash
OBSERVABILITY_ENABLE_TRACING=true
OBSERVABILITY_ENABLE_METRICS=true
OBSERVABILITY_LOG_PROMPTS=false
OBSERVABILITY_LOG_RESPONSES=false
```

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

## YAML Configuration Files

YAML files provide environment-specific profiles for easy deployment.

### Local Development (config/local.yaml)

```yaml
# Optimized for local development with Ollama
app:
  name: ai_agent_local
  mode: development
  debug: true
  log_level: DEBUG

models:
  provider: ollama
  model: llama2
  base_url: http://localhost:11434
  timeout: 60
  temperature: 0.7

tools:
  timeout: 30
  temperature: 0.3
  max_length: 500

memory:
  short_term_size: 10
  long_term_enabled: false
  context_window: 4096

engine:
  max_turns: 10
  timeout: 300
  enable_reflection: true

observability:
  enable_tracing: true
  enable_metrics: false
  log_prompts: true
  log_responses: true
```

### Staging Environment (config/staging.yaml)

```yaml
# Uses OpenAI GPT-3.5-turbo for cost-effective testing
app:
  name: ai_agent_staging
  mode: staging
  debug: false
  log_level: INFO

models:
  provider: openai
  model: gpt-3.5-turbo
  timeout: 30
  temperature: 0.7
  max_tokens: 2048

tools:
  timeout: 30

memory:
  short_term_size: 15
  long_term_enabled: true

engine:
  max_turns: 15

observability:
  enable_tracing: true
  enable_metrics: true

# Note: Set OPENAI_API_KEY environment variable
# Never store API keys in configuration files!
```

### Production Environment (config/production.yaml)

```yaml
# Uses OpenAI GPT-4 for maximum capability
app:
  name: ai_agent_production
  mode: production
  debug: false
  log_level: WARNING

models:
  provider: openai
  model: gpt-4
  timeout: 60
  temperature: 0.7
  max_tokens: 4096

tools:
  timeout: 60
  temperature: 0.2
  max_length: 1000

memory:
  short_term_size: 20
  long_term_enabled: true
  context_window: 8192

engine:
  max_turns: 20
  timeout: 600

observability:
  enable_tracing: true
  enable_metrics: true
```

### Loading YAML Configurations

```python
from agent_labs.config_v2 import load_config

# Load specific environment config
config = load_config("config/local.yaml")

# Load with environment variable overrides
# (OPENAI_API_KEY from env overrides anything in file)
config = load_config("config/staging.yaml")

# Load with explicit overrides for testing
config = load_config(
    "config/production.yaml",
    models={"model": "gpt-4-turbo"},  # Override model
    engine={"max_turns": 30}          # Override max_turns
)
```

## JSON Schema Export

Generate JSON Schema for validation, documentation, or IDE autocomplete.

```python
from agent_labs.config_v2 import AgentConfig

# Export complete schema
schema = AgentConfig().to_json_schema()

# Save to file for documentation
import json
with open("config-schema.json", "w") as f:
    json.dump(schema, f, indent=2)

# Use in validation tools
# - IDE autocomplete
# - Pre-commit hooks
# - API documentation
# - Config file validation
```

### Example Schema Output

```json
{
  "type": "object",
  "properties": {
    "app": {
      "type": "object",
      "properties": {
        "name": {"type": "string", "default": "ai_agent"},
        "mode": {"enum": ["development", "staging", "production", "test"]},
        "debug": {"type": "boolean"},
        "log_level": {"type": "string"}
      }
    },
    "models": {
      "type": "object",
      "properties": {
        "provider": {"enum": ["mock", "ollama", "openai", "anthropic", "google", "azure-openai"]},
        "model": {"type": "string"},
        "timeout": {"type": "integer", "minimum": 1, "maximum": 600}
      },
      "required": ["provider"]
    }
  }
}
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
