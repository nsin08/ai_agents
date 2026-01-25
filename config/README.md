# Configuration Files

This directory contains environment-specific YAML configuration files for the AI Agents system.

## Available Configurations

### local.yaml - Local Development

**Purpose:** Development with local Ollama LLM  
**Provider:** Ollama (no API key required)  
**Model:** llama2  
**Features:**
- Debug logging enabled
- Prompt and response logging
- Fast iteration with local LLM
- Reflection enabled for learning

**Usage:**
```bash
# Start Ollama
ollama serve
ollama pull llama2

# Load configuration
python -c "
from agent_labs.config_v2 import load_config
config = load_config('config/local.yaml')
print(config.models.provider, config.models.model)
"
```

### staging.yaml - Staging Environment

**Purpose:** Pre-production testing with cloud LLM  
**Provider:** OpenAI  
**Model:** gpt-3.5-turbo (cost-effective)  
**Features:**
- Production-like settings
- Metrics and tracing enabled
- Moderate context window
- Balanced performance/cost

**Setup:**
```bash
# Set API key (required)
export OPENAI_API_KEY=sk-proj-xxxxx

# Load configuration
python -c "
from agent_labs.config_v2 import load_config
config = load_config('config/staging.yaml')
config.validate_secrets()  # Validates API key is set
"
```

### production.yaml - Production Environment

**Purpose:** Production deployment with maximum capability  
**Provider:** OpenAI  
**Model:** gpt-4 (highest quality)  
**Features:**
- Maximum quality and capability
- Extended timeouts
- Large context window
- Full observability
- Conservative tool temperature

**Setup:**
```bash
# Set API key via secret manager (required)
export OPENAI_API_KEY=sk-proj-xxxxx

# In Kubernetes/Docker:
# Mount secret as environment variable
# Never include API keys in config files or images

# Load configuration
python -c "
from agent_labs.config_v2 import load_config
config = load_config('config/production.yaml')
config.validate_secrets()
"
```

## Configuration Precedence

When using YAML files, settings are loaded with this precedence:

**Explicit Params > Environment Variables > YAML File > Defaults**

### Example

```python
from agent_labs.config_v2 import load_config

# staging.yaml has: model: gpt-3.5-turbo, timeout: 30
# Environment has: LLM_MODEL=gpt-4

config = load_config(
    "config/staging.yaml",
    models={"timeout": 60}  # Explicit override
)

# Result:
# - model: "gpt-4" (from environment, overrides YAML)
# - timeout: 60 (from explicit, overrides YAML)
# - temperature: 0.7 (from YAML)
```

## Security Best Practices

### ✅ DO:
- Store API keys in environment variables
- Use secret management systems (AWS Secrets Manager, Azure Key Vault, etc.)
- Use separate API keys for staging and production
- Rotate API keys regularly
- Set up billing alerts for cloud providers
- Use `.env` files locally (never commit them)
- Use different API keys per environment

### ❌ DON'T:
- Store API keys in YAML files
- Commit `.env` files to version control
- Share API keys between environments
- Include secrets in Docker images
- Log API keys or full prompts in production

## Creating Custom Configurations

1. **Copy an example:**
   ```bash
   cp config/local.yaml config/my_env.yaml
   ```

2. **Edit settings:**
   ```yaml
   app:
     name: my_custom_agent
     mode: development
   
   models:
     provider: ollama
     model: mistral:7b
   ```

3. **Load your config:**
   ```python
   config = load_config("config/my_env.yaml")
   ```

## Validation

All configurations are validated on load:

```python
from agent_labs.config_v2 import load_config, ConfigError

try:
    config = load_config("config/production.yaml")
    config.validate_secrets()  # Check API keys
    print("Configuration valid!")
except ConfigError as e:
    print(f"Configuration error: {e}")
```

**Common validation errors:**
- Model name missing for cloud providers
- API key not set (for OpenAI, Anthropic, etc.)
- Invalid timeout/temperature ranges
- Unknown provider or mode
- Extra/unknown fields

## Configuration Sections

Each YAML file can configure six sections:

1. **app** - Application name, mode, logging
2. **models** - LLM provider, model, API settings
3. **tools** - Tool execution settings
4. **memory** - Context and memory management
5. **engine** - Agent orchestration settings
6. **observability** - Tracing, metrics, logging

All fields are optional (defaults are used if not specified).

## Environment-Specific Settings

### Development (local.yaml)
- Debug logging: `log_level: DEBUG`
- Log prompts/responses: `log_prompts: true`
- Short timeouts: `timeout: 60`
- Local provider: `provider: ollama`

### Staging (staging.yaml)
- Info logging: `log_level: INFO`
- No prompt logging: `log_prompts: false`
- Medium timeouts: `timeout: 30`
- Cost-effective model: `model: gpt-3.5-turbo`
- Metrics enabled: `enable_metrics: true`

### Production (production.yaml)
- Warning logging: `log_level: WARNING`
- No debug logging: `debug: false`
- Extended timeouts: `timeout: 60`
- Best model: `model: gpt-4`
- Full observability: `enable_tracing/metrics: true`

## Testing Configurations

```bash
# Test local config
python -m pytest tests/unit/test_config_v2.py::TestYAMLLoading::test_load_example_configs -v

# Validate all configs
for config in config/*.yaml; do
    python -c "
from agent_labs.config_v2 import load_config
try:
    cfg = load_config('$config')
    print('✓ $config valid')
except Exception as e:
    print('✗ $config error:', e)
"
done
```

## Migration from Environment Variables

If you're currently using environment variables, you can migrate to YAML:

**Before (env vars only):**
```bash
export LLM_PROVIDER=openai
export OPENAI_MODEL=gpt-4
export AGENT_MAX_TURNS=20
export TOOL_TIMEOUT=45
```

**After (YAML config):**
```yaml
# config/my_env.yaml
models:
  provider: openai
  model: gpt-4

engine:
  max_turns: 20

tools:
  timeout: 45
```

```python
# Load from YAML instead
config = load_config("config/my_env.yaml")
```

## Reference

- **Full documentation:** `docs/configuration.md`
- **Configuration module:** `src/agent_labs/config_v2.py`
- **Tests:** `tests/unit/test_config_v2.py`
- **Example .env:** `.env.example`
