# LLM Provider Adapters

Pluggable LLM provider interface for flexible backend switching without code changes.

## Overview

The `llm_providers` module provides a unified async interface for multiple LLM backends:

- **MockProvider**: Deterministic testing (no external calls)
- **OllamaProvider**: Local model inference (privacy-first)
- **CloudProvider**: Template for OpenAI, Anthropic, etc. (Phase 2)

All providers implement the same interface:

```python
async def generate(prompt, max_tokens=1000, temperature=0.7) -> LLMResponse
async def stream(prompt, max_tokens=1000) -> AsyncIterator[str]
async def count_tokens(text) -> int
```

## Installation

```bash
# Core (mock provider only)
pip install pytest pytest-asyncio

# With Ollama support
pip install httpx

# With cloud providers (Phase 2)
pip install openai anthropic
```

## Usage

### MockProvider (Testing)

Deterministic provider - always returns the same response for the same prompt.

```python
from src.agent_labs.llm_providers import MockProvider

provider = MockProvider()

# Generate response
response = await provider.generate("What is Python?")
print(response.text)        # "Mock response to: What is Python?"
print(response.tokens_used) # 5
print(response.model)       # "mock"

# Stream response
async for chunk in provider.stream("Hello"):
    print(chunk, end="")

# Count tokens
tokens = await provider.count_tokens("Hello, world!")
print(tokens)  # 2
```

### OllamaProvider (Local Models)

Run large language models locally on your machine.

```python
from src.agent_labs.llm_providers import OllamaProvider

# 1. Install Ollama: https://ollama.ai
# 2. Pull a model: ollama pull llama2
# 3. Start server: ollama serve

provider = OllamaProvider(
    base_url="http://localhost:11434",
    model="llama2",
    timeout=60
)

# Generate response
response = await provider.generate(
    "Explain machine learning in one sentence",
    max_tokens=100,
    temperature=0.7
)
print(response.text)
print(f"Used {response.tokens_used} tokens")

# Stream response for real-time output
async for chunk in provider.stream("Write a poem about Python"):
    print(chunk, end="", flush=True)

# With context manager for cleanup
async with OllamaProvider(model="mistral") as provider:
    response = await provider.generate("Hello!")
    print(response.text)
```

### Provider Interface

All providers implement the `Provider` abstract base class:

```python
from abc import ABC, abstractmethod
from typing import AsyncIterator
from dataclasses import dataclass

@dataclass
class LLMResponse:
    text: str          # Generated text
    tokens_used: int   # Tokens consumed
    model: str         # Model name

class Provider(ABC):
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """Generate text response."""
        pass

    @abstractmethod
    async def stream(
        self,
        prompt: str,
        max_tokens: int = 1000,
    ) -> AsyncIterator[str]:
        """Stream text tokens."""
        pass

    @abstractmethod
    async def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        pass
```

## Error Handling

Providers raise specific exceptions for different failure modes:

```python
from src.agent_labs.llm_providers import (
    OllamaProvider,
    ModelNotFoundError,
    ProviderConnectionError,
    ProviderTimeoutError,
)

provider = OllamaProvider(model="unknown")

try:
    response = await provider.generate("Hello")
except ModelNotFoundError as e:
    print(f"Model not found: {e}")
except ProviderConnectionError as e:
    print(f"Cannot connect to Ollama: {e}")
except ProviderTimeoutError as e:
    print(f"Request timed out: {e}")
```

## Testing

Unit tests (mock provider):

```bash
pytest tests/unit/llm_providers/test_base.py -v
```

Integration tests (Ollama):

```bash
pytest tests/integration/test_ollama_integration.py -v
```

## File Organization

```
src/agent_labs/llm_providers/
  __init__.py          # Package exports
  base.py              # Provider ABC + LLMResponse
  mock.py              # MockProvider implementation
  ollama.py            # OllamaProvider implementation
  cloud.py             # CloudProvider template
  exceptions.py        # Custom exceptions
  README.md            # This file

tests/unit/llm_providers/
  test_base.py         # Unit tests

tests/integration/
  test_ollama_integration.py
```

## Supported Providers

### Available Now
- **MockProvider**: Deterministic testing (zero external calls)
- **OllamaProvider**: Local model inference (privacy-first)

### Coming in Phase 2
- **OpenAIProvider**: GPT-3.5, GPT-4
- **AnthropicProvider**: Claude
- **GoogleProvider**: Gemini
- **AzureProvider**: Azure OpenAI

## Performance Tips

1. **Token counting**: Use `count_tokens()` before generation to stay under limits.
2. **Streaming**: Use `stream()` for interactive applications.
3. **Temperature**:
   - 0.0 = Deterministic
   - 0.7 = Balanced
   - 1.0 = Maximum creativity
4. **Ollama caching**: First model load is slow; subsequent runs are faster.

## Examples

### Agent with Provider Switching

```python
from src.agent_labs.llm_providers import MockProvider, OllamaProvider

async def run_agent(use_mock: bool = True):
    if use_mock:
        provider = MockProvider()
    else:
        provider = OllamaProvider(model="llama2")
    
    response = await provider.generate("Solve x + 2 = 5")
    print(response.text)

await run_agent(use_mock=True)
await run_agent(use_mock=False)
```

### Integration with Agent Orchestrator

```python
from src.agent_labs.orchestrator import Agent
from src.agent_labs.llm_providers import OllamaProvider

provider = OllamaProvider(model="llama2")
agent = Agent(provider=provider)
result = await agent.run("Find the capital of France")
print(result)
```

## References

- [Ollama Documentation](https://ollama.ai)
- [Ollama Model Library](https://ollama.ai/library)
- [LLM Tokens Explained](https://help.openai.com/en/articles/4936856-what-are-tokens-and-how-to-count-them)
- [Sampling Parameters](https://huggingface.co/blog/how-to-generate)

## Contributing

To add a new provider:

1. Create `src/agent_labs/llm_providers/your_provider.py`
2. Implement the `Provider` interface
3. Add tests in `tests/unit/llm_providers/test_your_provider.py`
4. Update this README with usage examples
5. Export in `__init__.py`
```
class MyProvider(Provider):
    async def generate(self, prompt, max_tokens=1000, temperature=0.7):
        pass
    
    async def stream(self, prompt, max_tokens=1000):
        yield "response chunks"
    
    async def count_tokens(self, text):
        return len(text.split())
```

## License

Part of AI Agents reference project. See `LICENSE` for details.
