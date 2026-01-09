# Quick Reference: Configurable Ollama Models

## TL;DR - 30 Seconds

```python
# Set model globally (recommended)
from agent_labs.config import set_ollama_model
set_ollama_model("mistral:7b")

# Or use environment variable
# OLLAMA_MODEL=mistral:7b python script.py

# Tools automatically use the configured model
summarizer = TextSummarizer()  # Uses mistral:7b
```

## Common Tasks

### Switch Between llama2 and mistral:7b

```python
from agent_labs.config import set_ollama_model

# Use llama2
set_ollama_model("llama2")

# Use mistral
set_ollama_model("mistral:7b")
```

### Check Current Model

```python
from agent_labs.config import get_ollama_model
print(get_ollama_model())
```

### View All Settings

```python
from agent_labs.config import Config
import json
print(json.dumps(Config.to_dict(), indent=2))
```

### Override Model for Specific Tool

```python
from agent_labs.tools.ollama_tools import TextSummarizer

summarizer = TextSummarizer(model="mistral:7b")
```

### Set Model via Environment (Before Running Python)

**Bash/Linux/Mac**:
```bash
export OLLAMA_MODEL=mistral:7b
python script.py
```

**PowerShell (Windows)**:
```powershell
$env:OLLAMA_MODEL="mistral:7b"
python script.py
```

**Docker**:
```dockerfile
ENV OLLAMA_MODEL=mistral:7b
```

## Available Models

| Model | Enum Value | Size | Speed | Quality |
|-------|-----------|------|-------|---------|
| llama2 | `OllamaModel.LLAMA2` | 7B | ⚡⚡ | ⭐⭐⭐ |
| llama2:13b | `OllamaModel.LLAMA2_13B` | 13B | ⚡ | ⭐⭐⭐⭐ |
| mistral:7b | `OllamaModel.MISTRAL` | 7B | ⚡⚡ | ⭐⭐⭐⭐ |
| neural-chat | `OllamaModel.NEURAL_CHAT` | 7B | ⚡⚡ | ⭐⭐⭐ |
| Custom model | Use string | Varies | Varies | Varies |

## Testing with Different Models

```bash
# Test with default model (llama2)
pytest tests/integration/test_ollama_tools.py -v

# Test with mistral:7b
OLLAMA_MODEL=mistral:7b pytest tests/integration/test_ollama_tools.py -v

# Test multiple models
for model in llama2 mistral:7b llama2:13b; do
  OLLAMA_MODEL=$model pytest tests/integration/test_ollama_tools.py -q
done
```

## Configuration Hierarchy (What Wins?)

1. **Explicit parameter** ← Most specific
   ```python
   TextSummarizer(model="mistral:7b")
   ```
2. **Config runtime change**
   ```python
   set_ollama_model("mistral:7b")
   ```
3. **Environment variable**
   ```bash
   OLLAMA_MODEL=mistral:7b
   ```
4. **Config default** ← Least specific
   ```python
   # Default: "llama2"
   ```

## Environment Variables

```bash
# Model Selection
OLLAMA_MODEL=llama2

# Connection
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_TIMEOUT=60

# Tool Behavior
OLLAMA_TOOLS_TEMPERATURE=0.3
OLLAMA_TOOLS_MAX_LENGTH=500

# Agent Settings
AGENT_MAX_TURNS=10
AGENT_TIMEOUT=300
```

## Troubleshooting

**Q: How do I know what model is being used?**
```python
from agent_labs.config import get_ollama_model
print(f"Model: {get_ollama_model()}")
```

**Q: My code is still using mistral:7b, how do I switch?**
```python
from agent_labs.config import set_ollama_model
set_ollama_model("llama2")
# Creates new tools AFTER this call
```

**Q: How do I use a custom model?**
```python
set_ollama_model("my-custom-model:latest")
# Must be installed: ollama pull my-custom-model:latest
```

**Q: Can I still use explicit parameters?**
Yes! Both work:
```python
# Way 1: Via Config (recommended)
set_ollama_model("mistral:7b")
tool = TextSummarizer()

# Way 2: Explicit (still supported)
tool = TextSummarizer(model="mistral:7b")
```

## Files to Know About

| File | Purpose |
|------|---------|
| `src/agent_labs/config.py` | Configuration system |
| `src/agent_labs/tools/ollama_tools.py` | Tools using Config |
| `.context/MODEL_CONFIGURATION.md` | Full documentation |
| `.context/model_configuration_example.py` | Runnable examples |
| `tests/unit/test_config.py` | Config tests |

## One-Liner Examples

```python
# Set model
from agent_labs.config import set_ollama_model; set_ollama_model("mistral:7b")

# Get model
from agent_labs.config import get_ollama_model; print(get_ollama_model())

# View config
from agent_labs.config import Config; print(Config.to_dict())

# Use enum
from agent_labs.config import OllamaModel; set_ollama_model(OllamaModel.MISTRAL.value)
```

## See Also

- Full Guide: `.context/MODEL_CONFIGURATION.md`
- Examples: `.context/model_configuration_example.py`
- Implementation: `src/agent_labs/config.py`
- Tests: `tests/unit/test_config.py`
