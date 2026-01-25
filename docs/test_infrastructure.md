# Test Infrastructure Documentation

## Overview

This document describes the test infrastructure for the AI Agents project, including fixture factories, mock providers, and testing patterns.

## Quick Start

```python
# tests/unit/test_example.py
import pytest

@pytest.mark.asyncio
async def test_with_mock_provider(mock_provider):
    """Use shared mock_provider fixture."""
    response = await mock_provider.generate("test")
    assert response.text is not None
```

## Table of Contents

1. [Test Organization](#test-organization)
2. [Fixture Factories](#fixture-factories)
3. [MockProvider Usage](#mockprovider-usage)
4. [Test Markers](#test-markers)
5. [Best Practices](#best-practices)
6. [Running Tests](#running-tests)

---

## Test Organization

Tests are organized into three categories:

```
tests/
├── unit/          # Fast, isolated tests (no external dependencies)
├── integration/   # Tests with real services (Ollama, OpenAI, etc.)
└── conftest.py    # Shared fixtures and configuration
```

**Auto-marking:**
- Tests in `tests/unit/` automatically get `@pytest.mark.unit`
- Tests in `tests/integration/` automatically get `@pytest.mark.integration`

---

## Fixture Factories

Shared fixtures are defined in `tests/conftest.py` to avoid duplication.

### Provider Fixtures

#### `mock_provider`
Basic MockProvider for deterministic testing.

```python
async def test_basic(mock_provider):
    response = await mock_provider.generate("Hello")
    assert "Mock response" in response.text
```

#### `custom_mock_provider`
Factory for creating MockProvider with custom responses.

```python
async def test_custom(custom_mock_provider):
    provider = custom_mock_provider({
        "calculate": "The answer is 42",
        "greet": "Hello, user!"
    })
    
    response = await provider.generate("calculate")
    assert response.text == "The answer is 42"
```

#### `ollama_provider`
OllamaProvider for integration testing (requires Ollama running).

```python
@pytest.mark.ollama
async def test_ollama(ollama_provider):
    response = await ollama_provider.generate("test")
    assert response.text is not None
```

### Agent Fixtures

#### `mock_agent`
Pre-configured Agent with MockProvider.

```python
async def test_agent(mock_agent):
    result = await mock_agent.run("Complete task")
    assert result is not None
```

#### `agent_context_factory`
Factory for creating AgentContext instances.

```python
def test_context(agent_context_factory):
    context = agent_context_factory(
        goal="test goal",
        inputs={"key": "value"}
    )
    assert context.goal == "test goal"
```

### Tool Fixtures

#### `tool_registry`
Empty ToolRegistry for tool testing.

```python
async def test_tools(tool_registry):
    tool_registry.register(MyTool(), "my_tool")
    result = await tool_registry.execute("my_tool", arg="value")
```

### Test Data Fixtures

#### `sample_prompts`
Common test prompts for consistent testing.

```python
async def test_prompts(sample_prompts, mock_provider):
    for prompt in sample_prompts:
        response = await mock_provider.generate(prompt)
        assert response.text is not None
```

#### `sample_llm_response`
Sample LLMResponse for testing response handling.

```python
def test_response(sample_llm_response):
    assert sample_llm_response.tokens_used > 0
    assert sample_llm_response.model == "mock"
```

#### `test_config`
Common test configuration parameters.

```python
async def test_with_config(test_config, mock_provider):
    response = await mock_provider.generate(
        "test",
        max_tokens=test_config["max_tokens"]
    )
    assert response.tokens_used <= test_config["max_tokens"]
```

---

## MockProvider Usage

The MockProvider supports three modes for deterministic testing:

### Mode 1: Default Responses

```python
provider = MockProvider()
response = await provider.generate("Hello, world!")
# Returns: "Hello! I'm a mock LLM responding to your greeting."

response = await provider.generate("unknown prompt")
# Returns: "Mock response to: unknown prompt"
```

### Mode 2: Custom Response Map

```python
provider = MockProvider(responses={
    "test": "custom response",
    "calculate": "42"
})

response = await provider.generate("test")
# Returns: "custom response"
```

### Mode 3: Response Sequence (Multi-turn)

```python
provider = MockProvider(response_sequence=[
    "First response",
    "Second response",
    "Third response"
])

r1 = await provider.generate("any prompt 1")  # "First response"
r2 = await provider.generate("any prompt 2")  # "Second response"
r3 = await provider.generate("any prompt 3")  # "Third response"
```

### Mode 4: Custom Default Response

```python
provider = MockProvider(
    default_response="Always return this"
)

response = await provider.generate("anything")
# Returns: "Always return this"
```

---

## Test Markers

Configure which tests to run using pytest markers.

### Available Markers

| Marker | Purpose | Auto-applied |
|--------|---------|--------------|
| `@pytest.mark.unit` | Fast, isolated tests | Tests in `tests/unit/` |
| `@pytest.mark.integration` | Tests with external services | Tests in `tests/integration/` |
| `@pytest.mark.ollama` | Requires Ollama running | Manual |
| `@pytest.mark.openai` | Requires OpenAI API access | Manual |
| `@pytest.mark.asyncio` | Async test (auto-detected) | Auto by pytest-asyncio |

### Using Markers

```python
# Mark test that requires Ollama
@pytest.mark.ollama
@pytest.mark.integration
async def test_ollama_integration(ollama_provider):
    response = await ollama_provider.generate("test")
    assert response.text is not None

# Mark slow integration test
@pytest.mark.integration
async def test_full_workflow(mock_agent):
    result = await mock_agent.run("complex task")
    assert result is not None
```

### Marker Usage in CI

```bash
# Skip Ollama tests (for CI without Ollama)
pytest -m "not ollama"

# Skip all integration tests
pytest -m "not integration"

# Run only unit tests
pytest -m unit

# Skip both Ollama and OpenAI tests
pytest -m "not ollama and not openai"
```

---

## Best Practices

### 1. Use Shared Fixtures

**Don't:**
```python
def test_something():
    provider = MockProvider()  # Duplication
    response = await provider.generate("test")
```

**Do:**
```python
async def test_something(mock_provider):
    response = await mock_provider.generate("test")
```

### 2. Use Factory Fixtures for Customization

**Don't:**
```python
def test_custom():
    provider = MockProvider()
    provider._responses = {"test": "custom"}  # Brittle
```

**Do:**
```python
async def test_custom(custom_mock_provider):
    provider = custom_mock_provider({"test": "custom"})
    response = await provider.generate("test")
```

### 3. Write Deterministic Tests

**Don't:**
```python
async def test_nondeterministic():
    provider = OllamaProvider()  # Random outputs
    response = await provider.generate("test")
    assert "hello" in response.text  # Might fail
```

**Do:**
```python
async def test_deterministic(mock_provider):
    # Use MockProvider for predictable outputs
    response = await mock_provider.generate("Hello, world!")
    assert "mock" in response.text.lower()
```

### 4. Mark Slow/External Tests

**Always mark integration tests:**
```python
@pytest.mark.integration
@pytest.mark.ollama
async def test_ollama_integration(ollama_provider):
    # Test with real Ollama
    pass
```

### 5. One Concept Per Test

**Don't:**
```python
async def test_everything(mock_provider, mock_agent):
    # Tests multiple unrelated things
    r1 = await mock_provider.generate("test")
    r2 = await mock_agent.run("task")
    assert r1.text and r2
```

**Do:**
```python
async def test_provider_generates_response(mock_provider):
    response = await mock_provider.generate("test")
    assert response.text is not None

async def test_agent_completes_task(mock_agent):
    result = await mock_agent.run("task")
    assert result is not None
```

### 6. Use Descriptive Test Names

**Test names should describe what is being tested:**

```python
# Good names
test_mock_provider_returns_deterministic_response()
test_agent_handles_max_turns_exceeded_error()
test_custom_response_sequence_for_multi_turn_conversation()

# Bad names
test_1()
test_provider()
test_it_works()
```

### 7. Use Parametrize for Multiple Cases

**Don't:**
```python
async def test_tokens_10(mock_provider):
    response = await mock_provider.generate("test", max_tokens=10)
    assert response.tokens_used <= 10

async def test_tokens_50(mock_provider):
    response = await mock_provider.generate("test", max_tokens=50)
    assert response.tokens_used <= 50
```

**Do:**
```python
@pytest.mark.parametrize("max_tokens", [10, 50, 100, 500])
async def test_respects_max_tokens(mock_provider, max_tokens):
    response = await mock_provider.generate("test", max_tokens=max_tokens)
    assert response.tokens_used <= max_tokens
```

---

## Running Tests

### Basic Commands

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_fixture_patterns.py

# Run specific test
pytest tests/unit/test_fixture_patterns.py::TestBasicFixtureUsage::test_mock_provider_fixture

# Run with coverage
pytest --cov=src --cov-report=term-missing
```

### Filter by Markers

```bash
# Run only unit tests (fast)
pytest -m unit

# Skip integration tests
pytest -m "not integration"

# Skip Ollama tests (for CI)
pytest -m "not ollama"

# Run only integration tests
pytest -m integration

# Complex filter: unit tests but not ollama
pytest -m "unit and not ollama"
```

### Filter by Test Name

```bash
# Run tests matching pattern
pytest -k "mock_provider"

# Run tests NOT matching pattern
pytest -k "not ollama"

# Multiple patterns
pytest -k "mock or agent"
```

### Debugging Tests

```bash
# Show print statements
pytest -s

# Show locals in tracebacks
pytest -l

# Drop into debugger on failure
pytest --pdb

# Stop at first failure
pytest -x

# Show full diff for assertions
pytest -vv
```

### Parallel Execution

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel (4 workers)
pytest -n 4

# Auto-detect CPU count
pytest -n auto
```

---

## Examples

See `tests/unit/test_fixture_patterns.py` for comprehensive examples of all patterns.

### Example: Basic Test

```python
import pytest

@pytest.mark.asyncio
async def test_provider_returns_response(mock_provider):
    """Test that provider returns valid response."""
    response = await mock_provider.generate("test prompt")
    
    assert isinstance(response.text, str)
    assert len(response.text) > 0
    assert response.tokens_used > 0
```

### Example: Custom Mock Response

```python
@pytest.mark.asyncio
async def test_agent_handles_error(custom_mock_provider, mock_agent):
    """Test agent handles error responses."""
    provider = custom_mock_provider({
        "task": "ERROR: Cannot complete task"
    })
    
    # Replace agent's provider
    mock_agent.provider = provider
    
    result = await mock_agent.run("task")
    assert "ERROR" in result
```

### Example: Response Sequence

```python
@pytest.mark.asyncio
async def test_multi_turn_conversation():
    """Test multi-turn conversation with sequence."""
    provider = MockProvider(response_sequence=[
        "Hello! How can I help?",
        "Sure, I can help with that.",
        "Task completed successfully."
    ])
    
    r1 = await provider.generate("Hi")
    r2 = await provider.generate("Can you help?")
    r3 = await provider.generate("Do task")
    
    assert "Hello" in r1.text
    assert "Sure" in r2.text
    assert "completed" in r3.text
```

---

## Contributing

When adding new tests:

1. Use shared fixtures from `conftest.py`
2. Add new fixtures to `conftest.py` if they'll be reused
3. Mark integration tests appropriately
4. Write deterministic tests using MockProvider
5. Follow naming conventions
6. Add examples to `test_fixture_patterns.py` for new patterns

---

## Summary

**Key Points:**
- ✅ Use shared fixtures from `conftest.py`
- ✅ MockProvider ensures deterministic tests
- ✅ Mark integration tests with appropriate markers
- ✅ Use factory fixtures for customization
- ✅ One logical concept per test
- ✅ Descriptive test names
- ✅ Parametrize for multiple cases

**Running Tests:**
```bash
pytest                          # All tests
pytest -m unit                  # Fast unit tests only
pytest -m "not ollama"          # Skip Ollama tests
pytest --cov=src                # With coverage
```

For examples, see: `tests/unit/test_fixture_patterns.py`
