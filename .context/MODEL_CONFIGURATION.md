# Model Configuration Guide

This guide explains how to configure the Ollama model used by tools and agents in the agent_labs framework.

## Quick Start

### Option 1: Global Configuration (Recommended)

```python
from agent_labs.config import set_ollama_model

# Set the model for all tools/agents
set_ollama_model("llama2")
```

### Option 2: Environment Variable

```bash
# Set default model via environment
export OLLAMA_MODEL=llama2

# Or for Windows PowerShell
$env:OLLAMA_MODEL="llama2"
```

### Option 3: Per-Tool Override

```python
from agent_labs.tools.ollama_tools import TextSummarizer

# Use specific model for this tool instance
summarizer = TextSummarizer(model="mistral:7b")
```

## Configuration Class

The `Config` class centralizes all settings:

```python
from agent_labs.config import Config

# View current settings
print(Config.OLLAMA_MODEL)           # "llama2"
print(Config.OLLAMA_BASE_URL)        # "http://localhost:11434"
print(Config.OLLAMA_TOOLS_TEMPERATURE)  # 0.3

# Change settings at runtime
Config.set_ollama_model("mistral:7b")

# View all configuration
config = Config.to_dict()
print(config)
# {
#     "ollama": {
#         "base_url": "http://localhost:11434",
#         "model": "mistral:7b",
#         "timeout": 60,
#         "temperature": 0.3,
#         "max_length": 500
#     },
#     "agent": {
#         "max_turns": 10,
#         "timeout": 300
#     }
# }
```

## Available Models

### Built-in Models (via OllamaModel enum)

```python
from agent_labs.config import OllamaModel

OllamaModel.LLAMA2          # "llama2"
OllamaModel.LLAMA2_13B      # "llama2:13b"
OllamaModel.MISTRAL         # "mistral:7b"
OllamaModel.NEURAL_CHAT     # "neural-chat"
OllamaModel.QWEN            # "qwen"
OllamaModel.GEMMA           # "gemma"
```

### Custom Models

You can use any model installed in Ollama:

```python
set_ollama_model("phi")
set_ollama_model("neural-chat:latest")
set_ollama_model("my-custom-model")
```

## Environment Variables

All configuration supports environment variable overrides:

```bash
# Ollama Settings
OLLAMA_BASE_URL=http://localhost:11434      # Ollama API endpoint
OLLAMA_MODEL=llama2                          # Default model
OLLAMA_TIMEOUT=60                            # Request timeout (seconds)

# Tool Settings
OLLAMA_TOOLS_TEMPERATURE=0.3                 # Generation temperature
OLLAMA_TOOLS_MAX_LENGTH=500                  # Max output tokens

# Agent Settings
AGENT_MAX_TURNS=10                           # Max reasoning turns
AGENT_TIMEOUT=300                            # Max execution time (seconds)
```

## Usage Examples

### Example 1: Switch Models at Runtime

```python
from agent_labs.config import set_ollama_model
from agent_labs.tools.ollama_tools import TextSummarizer

# Create summarizer with llama2
set_ollama_model("llama2")
summarizer1 = TextSummarizer()
result1 = summarizer1.summarize("Long text...")

# Switch to mistral
set_ollama_model("mistral:7b")
summarizer2 = TextSummarizer()
result2 = summarizer2.summarize("Long text...")
```

### Example 2: Per-Tool Model Override

```python
from agent_labs.tools.ollama_tools import TextSummarizer, CodeAnalyzer

# Global default
set_ollama_model("llama2")

# TextSummarizer uses global model
summarizer = TextSummarizer()

# CodeAnalyzer uses specific model
analyzer = CodeAnalyzer(model="mistral:7b")
```

### Example 3: Testing Multiple Models

```python
from agent_labs.config import OllamaModel
from agent_labs.tools.ollama_tools import TextSummarizer

for model in [OllamaModel.LLAMA2, OllamaModel.MISTRAL]:
    summarizer = TextSummarizer(model=model.value)
    # Run tests...
```

## Default Values

| Setting | Default | Environment Variable |
|---------|---------|----------------------|
| **Ollama URL** | `http://localhost:11434` | `OLLAMA_BASE_URL` |
| **Model** | `llama2` | `OLLAMA_MODEL` |
| **Timeout** | 60s | `OLLAMA_TIMEOUT` |
| **Temperature** | 0.3 | `OLLAMA_TOOLS_TEMPERATURE` |
| **Max Length** | 500 tokens | `OLLAMA_TOOLS_MAX_LENGTH` |
| **Agent Max Turns** | 10 | `AGENT_MAX_TURNS` |
| **Agent Timeout** | 300s | `AGENT_TIMEOUT` |

## Migration from Hardcoded Models

### Before (Hardcoded)
```python
summarizer = TextSummarizer(
    model="mistral:7b"  # Hardcoded
)
```

### After (Configurable)
```python
# Option 1: Use global config
from agent_labs.config import set_ollama_model
set_ollama_model("mistral:7b")
summarizer = TextSummarizer()

# Option 2: Environment variable
# OLLAMA_MODEL=mistral:7b python script.py
summarizer = TextSummarizer()

# Option 3: Still support explicit override
summarizer = TextSummarizer(model="mistral:7b")
```

## Testing with Different Models

### Unit Tests (Mock, no Ollama required)
```bash
python -m pytest tests/unit/test_config.py -v
```

### Integration Tests (Requires Ollama)
```bash
# Use default model (llama2)
python -m pytest tests/integration/test_ollama_tools.py -v

# Use specific model
OLLAMA_MODEL=mistral:7b python -m pytest tests/integration/test_ollama_tools.py -v

# Skip Ollama tests
SKIP_OLLAMA=true python -m pytest tests/ -v
```

## Best Practices

1. **Use Config for Global Settings**: Set model once at application startup
2. **Environment Variables for Deployment**: Use env vars in Docker/CI/CD
3. **Per-Tool Overrides for Exceptions**: Only override when needed
4. **Test Multiple Models**: Verify compatibility before deployment

## API Reference

### `set_ollama_model(model: str)`
Set the global Ollama model for all tools.

### `get_ollama_model() -> str`
Get the current Ollama model.

### `Config.set_ollama_model(model: str)`
Class method to set model.

### `Config.get_ollama_model() -> str`
Class method to get model.

### `Config.to_dict() -> dict`
Get all configuration as dictionary.

## Troubleshooting

### Model Not Found Error
```
ModelNotFoundError: Model 'xyz' not found
```
Solution: Install model with `ollama pull xyz`

### Using Hardcoded Model?
Check your tool initialization:
```python
# ❌ Avoid hardcoding
TextSummarizer(model="mistral:7b")

# ✅ Use Config instead
set_ollama_model("mistral:7b")
TextSummarizer()
```

### Need to Check Current Model?
```python
from agent_labs.config import get_ollama_model
print(f"Using model: {get_ollama_model()}")
```
