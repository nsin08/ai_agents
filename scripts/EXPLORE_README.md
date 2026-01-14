# Exploration Notebook Guide

## Overview

`explore.py` is a script-based notebook for testing AI agents with real LLM providers. It runs predefined scenarios to demonstrate agent capabilities with flexible provider and model selection via CLI arguments.

## Quick Start

### 1. Run with Default Provider (No Setup Required)

```bash
# Run default quickstart scenario with MockProvider (instant)
python scripts/explore.py

# Run specific scenario
python scripts/explore.py reasoning
python scripts/explore.py teaching

# List scenarios
python scripts/explore.py --list
python scripts/explore.py --help
```

### 2. Switch to Ollama (For Real LLM)

```bash
# Install Ollama from https://ollama.ai/download
# Start Ollama server: ollama serve
# Pull model: ollama pull llama2

# Run with Ollama
python scripts/explore.py reasoning --ollama
python scripts/explore.py teaching --ollama --model phi
```

### 3. Use Cloud Providers (OpenAI, etc.)

```bash
# Set API key
export OPENAI_API_KEY="sk-..."

# Run with OpenAI
python scripts/explore.py reasoning --openai --model gpt-4
python scripts/explore.py teaching --openai
```

## Available Scenarios

| Scenario | Default Provider | Description | Prompts | Override |
|----------|----------|-------------|---------|----------|
| `quickstart` | Ollama | Simple introductory prompts | 3 | ✅ |
| `reasoning` | Ollama | Test logical reasoning | 3 | ✅ |
| `storytelling` | Ollama | Creative story generation | 3 | ✅ |
| `teaching` | Ollama | Complex topic explanations | 3 | ✅ |
| `advanced` | Ollama | Advanced reasoning tasks | 3 | ✅ |
| `openai` | OpenAI | OpenAI GPT-4 responses | 3 | ✅ |
| `mock` | Mock | Fast testing without LLM | 3 | ✅ |

## Provider Configuration

### CLI Arguments for Provider Selection

```bash
# Provider flags
python scripts/explore.py SCENARIO --openai              # Use OpenAI
python scripts/explore.py SCENARIO --ollama              # Use Ollama
python scripts/explore.py SCENARIO --mock                # Use Mock

# Model override
python scripts/explore.py SCENARIO --model MODEL_NAME

# Examples
python scripts/explore.py reasoning --openai --model gpt-4
python scripts/explore.py teaching --ollama --model phi
python scripts/explore.py quickstart --mock
```

### Ollama Setup

```bash
# Use specific model
python scripts/explore.py teaching --ollama --model phi
python scripts/explore.py advanced --ollama --model llama3.2:3b

# Custom endpoint
export OLLAMA_BASE_URL="http://custom-server:11434"
python scripts/explore.py reasoning --ollama
```

### OpenAI Setup

```bash
# Set API key
export OPENAI_API_KEY="sk-..."

# Run scenarios
python scripts/explore.py reasoning --openai              # Uses default model
python scripts/explore.py teaching --openai --model gpt-3.5-turbo
python scripts/explore.py openai --model gpt-4           # OpenAI scenario
```

## Adding Custom Scenarios

Edit `explore.py` to add your own scenarios:

```python
SCENARIOS = {
    "my_scenario": Scenario(
        name="My Custom Scenario",
        description="Description of what this tests",
        provider="ollama",  # Default: "ollama", "openai", "mock"
        model="llama2",
        max_turns=5,
        prompts=["First prompt", "Second prompt", "Third prompt"],
    ),
}
```

**Override at runtime:**
```bash
python scripts/explore.py my_scenario --openai --model gpt-4
```

## Troubleshooting

### Ollama Connection Error

```bash
# Error: Connection refused to localhost:11434
# Solution 1: Start Ollama server
ollama serve

# Solution 2: Use different provider
python scripts/explore.py reasoning --openai    # Use OpenAI
python scripts/explore.py reasoning --mock      # Use Mock
```

### Model Not Found (Ollama)

```bash
# Error: Model not found
# Solution: Download model
ollama pull phi
ollama pull llama3.2:3b

# Use pre-pulled model
python scripts/explore.py reasoning --ollama --model phi
```

### Missing OpenAI API Key

```bash
# Error: OPENAI_API_KEY not set
# Solution 1: Set env var
export OPENAI_API_KEY="sk-..."
python scripts/explore.py reasoning --openai

# Solution 2: Use different provider
python scripts/explore.py reasoning --ollama
python scripts/explore.py reasoning --mock
```

### Slow Responses

```bash
# Use faster model
python scripts/explore.py reasoning --ollama --model phi

# Or use Mock for instant testing
python scripts/explore.py reasoning --mock
```

## Example Output

```
╔════════════════════════════════════════════════════════════════╗
║  Reasoning & Logic                                             ║
╚════════════════════════════════════════════════════════════════╝

Description: Test agent's reasoning capabilities

Configuration:
  Provider:  ollama
  Model:     phi
  Max Turns: 5

────────────────────────────────────────────────────────────────
Prompt 1/3
────────────────────────────────────────────────────────────────

📝 Solve this riddle: I have cities but no houses. What am I?

⏳ Agent processing...

✓ Response:
[Agent's response with reasoning...]

════════════════════════════════════════════════════════════════
✓ Scenario 'reasoning' completed successfully!
════════════════════════════════════════════════════════════════
```

## Command Reference

```bash
# List scenarios
python scripts/explore.py --list

# Run scenario (uses default provider/model)
python scripts/explore.py reasoning

# Override provider
python scripts/explore.py reasoning --openai
python scripts/explore.py reasoning --ollama
python scripts/explore.py reasoning --mock

# Override model
python scripts/explore.py teaching --ollama --model phi
python scripts/explore.py reasoning --openai --model gpt-3.5-turbo

# Show help
python scripts/explore.py --help
```

## Next Steps

1. **Quick Test**: `python scripts/explore.py --mock` (instant, no setup)
2. **Try Ollama**: `python scripts/explore.py reasoning --ollama`
3. **Use OpenAI**: `python scripts/explore.py reasoning --openai --model gpt-4`
4. **Customize**: Add your own scenarios with specific prompts

## Next Steps

1. **Experiment**: Try different scenarios and observe agent behavior
2. **Customize**: Add your own scenarios with specific prompts
3. **Cloud Integration**: Implement cloud providers for production use
4. **Monitor**: Use observability features to track agent performance
