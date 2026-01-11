# Exploration Notebook Guide

## Overview

`explore.py` is a script-based notebook for testing AI agents with real LLM providers. It runs predefined scenarios to demonstrate agent capabilities.

## Quick Start

### 1. Setup Ollama (Default Provider)

```bash
# Install Ollama from https://ollama.ai/download

# Start Ollama server
ollama serve

# Pull the model (in another terminal)
ollama pull llama2
```

### 2. Run Scenarios

```bash
# Run default quickstart scenario
python scripts/explore.py

# Run specific scenario
python scripts/explore.py reasoning
python scripts/explore.py teaching
python scripts/explore.py advanced

# List all available scenarios
python scripts/explore.py --list

# Show help
python scripts/explore.py --help
```

## Available Scenarios

| Scenario | Provider | Description | Prompts |
|----------|----------|-------------|---------|
| `quickstart` | Ollama | Simple introductory prompts | 3 |
| `reasoning` | Ollama | Test logical reasoning | 3 |
| `storytelling` | Ollama | Creative story generation | 3 |
| `teaching` | Ollama | Complex topic explanations | 3 |
| `advanced` | Ollama | Advanced reasoning tasks | 3 |
| `mock` | Mock | Fast testing without LLM | 3 |
| `cloud` | Cloud | [Coming Soon] Cloud providers | 2 |

## Provider Configuration

### Ollama (Default)

```python
# Default configuration
provider = OllamaProvider(
    model="llama2",
    base_url="http://localhost:11434"
)

# Custom Ollama endpoint
export OLLAMA_BASE_URL="http://custom-server:11434"
python scripts/explore.py quickstart
```

### Cloud Providers (Future)

To add cloud provider support (OpenAI, Anthropic, etc.):

1. **Implement CloudProvider** in `src/agent_labs/llm_providers/cloud.py`:

```python
class OpenAIProvider(Provider):
    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.api_key = api_key
        self.model = model
        self.client = OpenAI(api_key=api_key)
    
    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            **kwargs
        )
        return LLMResponse(
            content=response.choices[0].message.content,
            model=self.model,
            tokens=response.usage.total_tokens
        )
```

2. **Update explore.py** to use the cloud provider:

```python
elif scenario.provider == "cloud":
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Missing OPENAI_API_KEY environment variable")
        return
    provider = OpenAIProvider(api_key=api_key, model=scenario.model)
```

3. **Configure API keys**:

```bash
export OPENAI_API_KEY="sk-..."
python scripts/explore.py cloud
```

## Adding Custom Scenarios

Edit `explore.py` to add your own scenarios:

```python
SCENARIOS = {
    "my_scenario": Scenario(
        name="My Custom Scenario",
        description="Description of what this tests",
        provider="ollama",  # or "cloud", "mock"
        model="llama2",
        max_turns=5,
        prompts=[
            "First prompt",
            "Second prompt",
            "Third prompt",
        ],
    ),
}
```

## Troubleshooting

### Ollama Connection Error

```bash
# Error: Connection refused to localhost:11434
# Solution: Start Ollama server
ollama serve
```

### Model Not Found

```bash
# Error: Model 'llama2' not found
# Solution: Download the model
ollama pull llama2

# List available models
ollama list
```

### Slow Responses

```bash
# Use a smaller/faster model
ollama pull llama2:7b
# Update scenario model to "llama2:7b"
```

### API Rate Limits (Cloud Providers)

When cloud providers are implemented, rate limiting may occur. The framework includes automatic retry with exponential backoff.

## Example Output

```
╔════════════════════════════════════════════════════════════════╗
║  Quick Start                                                   ║
╚════════════════════════════════════════════════════════════════╝

Description: Simple introductory prompts with Ollama

Configuration:
  Provider:  ollama
  Model:     llama2
  Max Turns: 3

────────────────────────────────────────────────────────────────
Prompt 1/3
────────────────────────────────────────────────────────────────

📝 What is artificial intelligence?

⏳ Agent processing...

✓ Response:
Artificial intelligence (AI) refers to computer systems that can perform tasks
that typically require human intelligence, such as learning, problem-solving,
and decision-making...

════════════════════════════════════════════════════════════════
✓ Scenario 'quickstart' completed successfully!
════════════════════════════════════════════════════════════════
```

## Next Steps

1. **Experiment**: Try different scenarios and observe agent behavior
2. **Customize**: Add your own scenarios with specific prompts
3. **Cloud Integration**: Implement cloud providers for production use
4. **Monitor**: Use observability features to track agent performance
