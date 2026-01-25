# Configuration System - Usage Guide

## Quick Start

### 1. Choose Your Configuration Method

#### Option A: Environment Variables (Simple)
```bash
export LLM_PROVIDER=ollama
export LLM_MODEL=llama2
export AGENT_MAX_TURNS=10
```

```python
from agent_labs.config_v2 import get_config

config = get_config()
print(f"Using {config.models.provider} with {config.models.model}")
```

#### Option B: YAML Files (Recommended)
```bash
# Create or use existing config file
cp config/local.yaml my_config.yaml

# Edit my_config.yaml
# Set environment secrets
export OPENAI_API_KEY=sk-proj-xxxxx
```

```python
from agent_labs.config_v2 import load_config

config = load_config("my_config.yaml")
config.validate_secrets()  # Verify API keys
```

#### Option C: Explicit Parameters (Testing)
```python
from agent_labs.config_v2 import AgentConfig

config = AgentConfig(
    models={"provider": "mock"},
    engine={"max_turns": 5}
)
```

## Common Patterns

### Pattern 1: Local Development
```python
# config/local.yaml
config = load_config("config/local.yaml")

# Use with your agent
agent = MyAgent(
    model=config.models.model,
    provider=config.models.provider,
    max_turns=config.engine.max_turns
)
```

### Pattern 2: Environment-Specific
```python
import os
from agent_labs.config_v2 import load_config

# Load config based on environment
env = os.getenv("ENVIRONMENT", "local")
config = load_config(f"config/{env}.yaml")

# Validate for production
if config.app.mode == "production":
    config.validate_secrets()
```

### Pattern 3: Runtime Overrides
```python
from agent_labs.config_v2 import load_config

# Load base config
config = load_config("config/staging.yaml")

# Override for specific test
test_config = load_config(
    "config/staging.yaml",
    engine={"max_turns": 3},  # Faster for testing
    observability={"log_prompts": True}  # Debug this test
)
```

### Pattern 4: Multi-Environment Support
```python
from agent_labs.config_v2 import load_config

# Development: local Ollama
if ENV == "development":
    config = load_config("config/local.yaml")

# Staging: cloud LLM with moderate settings
elif ENV == "staging":
    config = load_config("config/staging.yaml")
    config.validate_secrets()

# Production: best model with full observability
elif ENV == "production":
    config = load_config("config/production.yaml")
    config.validate_secrets()
    assert config.observability.enable_metrics
```

## Migration Guide

### From Legacy Config (config.py)

#### Before:
```python
from agent_labs.config import Config

base_url = Config.OLLAMA_BASE_URL
model = Config.OLLAMA_MODEL
max_turns = Config.AGENT_MAX_TURNS
```

#### After:
```python
from agent_labs.config_v2 import get_config

config = get_config()
base_url = config.models.base_url
model = config.models.model
max_turns = config.engine.max_turns
```

### From Hardcoded Values

#### Before:
```python
def __init__(self):
    self.provider = "openai"
    self.model = "gpt-4"
    self.max_turns = 20
```

#### After:
```python
from agent_labs.config_v2 import load_config

def __init__(self, config_file="config/production.yaml"):
    config = load_config(config_file)
    self.provider = config.models.provider
    self.model = config.models.model
    self.max_turns = config.engine.max_turns
```

### From Environment Variables Only

#### Before:
```python
import os

provider = os.getenv("LLM_PROVIDER", "ollama")
model = os.getenv("LLM_MODEL", "llama2")
max_turns = int(os.getenv("AGENT_MAX_TURNS", "10"))
```

#### After:
```python
from agent_labs.config_v2 import AgentConfig

config = AgentConfig.from_env()
provider = config.models.provider
model = config.models.model
max_turns = config.engine.max_turns
```

## Configuration Precedence Examples

### Example 1: All Sources
```yaml
# config/base.yaml
models:
  provider: ollama
  model: llama2
  timeout: 60

engine:
  max_turns: 10
```

```bash
# Environment
export LLM_MODEL=mistral:7b
export AGENT_MAX_TURNS=15
```

```python
# Code
config = load_config(
    "config/base.yaml",
    models={"timeout": 90}
)

# Result:
# - provider: "ollama" (from YAML)
# - model: "mistral:7b" (from ENV, overrides YAML)
# - timeout: 90 (from Explicit, overrides YAML)
# - max_turns: 15 (from ENV, overrides YAML)
```

### Example 2: Partial Override
```python
# Start with staging config
config = load_config("config/staging.yaml")

# Override just one field for testing
test_config = load_config(
    "config/staging.yaml",
    models={"temperature": 0.0}  # Deterministic for tests
)
```

## Validation Patterns

### Pattern 1: Early Validation
```python
from agent_labs.config_v2 import load_config, ConfigError

try:
    config = load_config("config/production.yaml")
    config.validate_secrets()
    print("✓ Configuration valid")
except ConfigError as e:
    print(f"✗ Configuration error: {e}")
    sys.exit(1)
```

### Pattern 2: Validation with Fallback
```python
from agent_labs.config_v2 import load_config, ConfigError

try:
    config = load_config("config/cloud.yaml")
    config.validate_secrets()
except ConfigError:
    print("⚠ Cloud config invalid, falling back to local")
    config = load_config("config/local.yaml")
```

### Pattern 3: Conditional Validation
```python
config = load_config("config/app.yaml")

# Only validate secrets for cloud providers
if config.models.provider in ["openai", "anthropic", "google"]:
    config.validate_secrets()
```

## Export Patterns

### Pattern 1: Export for Logging
```python
config = load_config("config/production.yaml")

# Export sanitized config for logs
config_dict = config.to_dict()
# Note: API keys are never included in export
logging.info(f"Loaded config: {config_dict}")
```

### Pattern 2: Export Schema for Docs
```python
from agent_labs.config_v2 import AgentConfig
import json

# Generate schema
schema = AgentConfig().to_json_schema()

# Save to file
with open("docs/config-schema.json", "w") as f:
    json.dump(schema, f, indent=2)
```

### Pattern 3: Export for Validation Tool
```python
# Use schema in pre-commit hook
schema = AgentConfig().to_json_schema()

# Validate user's config file
import yaml
import jsonschema

with open("user_config.yaml") as f:
    user_config = yaml.safe_load(f)

jsonschema.validate(user_config, schema)
```

## Testing Patterns

### Pattern 1: Unit Tests with Mock Config
```python
import pytest
from agent_labs.config_v2 import AgentConfig

def test_my_agent():
    config = AgentConfig(
        models={"provider": "mock"},
        engine={"max_turns": 3}
    )
    agent = MyAgent(config)
    assert agent.run() == expected_result
```

### Pattern 2: Integration Tests with Real Config
```python
@pytest.mark.integration
def test_with_ollama(tmp_path):
    config_file = tmp_path / "test.yaml"
    config_file.write_text("""
models:
  provider: ollama
  model: llama2
    """)
    
    config = load_config(str(config_file))
    agent = MyAgent(config)
    # Test with real Ollama
```

### Pattern 3: Parametric Tests
```python
@pytest.mark.parametrize("config_file", [
    "config/local.yaml",
    "config/staging.yaml",
    "config/production.yaml"
])
def test_all_configs(config_file):
    config = load_config(config_file)
    assert config.models.provider in ["ollama", "openai"]
```

## Security Best Practices

### ✅ DO:
```python
# 1. Store API keys in environment
export OPENAI_API_KEY=sk-proj-xxxxx

# 2. Validate secrets at startup
config.validate_secrets()

# 3. Use separate keys per environment
# .env.dev:  OPENAI_API_KEY=sk-proj-dev-xxxxx
# .env.prod: OPENAI_API_KEY=sk-proj-prod-xxxxx

# 4. Never log API keys
config_dict = config.to_dict()  # API keys excluded automatically
```

### ❌ DON'T:
```yaml
# NEVER store API keys in YAML files
models:
  provider: openai
  api_key: sk-proj-xxxxx  # ❌ WRONG! Use env var instead
```

## Troubleshooting

### Issue: "Model name required for provider 'openai'"
**Solution:**
```python
# Option 1: Set in environment
export OPENAI_MODEL=gpt-4

# Option 2: Set in YAML
models:
  provider: openai
  model: gpt-4

# Option 3: Set explicitly
config = AgentConfig(models={"provider": "openai", "model": "gpt-4"})
```

### Issue: "API key required for openai"
**Solution:**
```bash
# Set via environment
export OPENAI_API_KEY=sk-proj-xxxxx

# Verify
python -c "from agent_labs.config_v2 import load_config; c=load_config('config/staging.yaml'); c.validate_secrets()"
```

### Issue: Configuration not updating
**Solution:**
```python
# get_config() is cached - reload if needed
from agent_labs.config_v2 import AgentConfig

# Don't use cached version
config = AgentConfig.from_env()  # Fresh load

# Or for YAML
config = AgentConfig.from_yaml("config/local.yaml")  # Fresh load
```

## Reference

- **Full Documentation**: `docs/configuration.md`
- **Config Examples**: `config/README.md`
- **Test Examples**: `tests/unit/test_config_v2.py`
- **Working Examples**: `scripts/config_examples.py`
- **Quick Test**: `labs/00/src/quick_config_test.py`
