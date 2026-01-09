# Ollama-Based Tools Implementation

## Overview

Added two powerful Ollama-based tools to the tools framework:
1. **TextSummarizer** - Summarize text using Ollama LLM
2. **CodeAnalyzer** - Analyze code for quality, security, performance, or documentation

## New Tools

### TextSummarizer

Summarize text using Ollama LLM with configurable parameters.

**Features:**
- Configurable max summary length (10-1000 words)
- Configurable temperature for creativity (0-1)
- Returns word count in summary
- Performance tracking (latency_ms)
- Rich metadata (model, temperature, input length)

**Usage:**
```python
from agent_labs.tools import TextSummarizer, ToolRegistry

summarizer = TextSummarizer(
    ollama_url="http://localhost:11434",
    model="mistral:7b",
    max_tokens=200,
    temperature=0.3
)

registry = ToolRegistry()
registry.register(summarizer)

# Execute
result = await registry.execute(
    "text_summarizer",
    text="Long text to summarize..." * 10,
    max_length=50
)

if result.success:
    print(result.output["summary"])
    print(f"Summary: {result.output['word_count']} words")
```

**Input Schema:**
```python
{
    "text": str,              # 50+ characters required
    "max_length": int         # 10-1000 words, default 100
}
```

**Output Schema:**
```python
{
    "summary": str,           # The summarized text
    "word_count": int         # Words in summary
}
```

### CodeAnalyzer

Analyze code for various aspects using Ollama LLM.

**Features:**
- 4 analysis types: quality, security, performance, documentation
- Multi-language support (Python, JavaScript, Java, etc.)
- Extracts issue count from analysis
- Suggests improvements
- Tracks execution metadata (model, language, analysis type)

**Usage:**
```python
from agent_labs.tools import CodeAnalyzer, ToolRegistry

analyzer = CodeAnalyzer(
    ollama_url="http://localhost:11434",
    model="mistral:7b",
    timeout=60
)

registry = ToolRegistry()
registry.register(analyzer)

# Security analysis
result = await registry.execute(
    "code_analyzer",
    code="def process(data): exec(data)",
    analysis_type="security",
    language="python"
)

if result.success:
    print(result.output["analysis"])
    print(f"Issues found: {result.output['issues_found']}")
    for suggestion in result.output["suggestions"]:
        print(f"  - {suggestion}")
```

**Input Schema:**
```python
{
    "code": str,              # 10+ characters required
    "analysis_type": str,     # "quality" | "security" | "performance" | "documentation"
    "language": str           # "python", "javascript", etc. (default: python)
}
```

**Output Schema:**
```python
{
    "analysis": str,          # Full analysis text
    "issues_found": int,      # Count of issues detected
    "suggestions": list[str]  # List of suggestions (max 5)
}
```

## Implementation Details

### File Structure
```
src/agent_labs/tools/
└── ollama_tools.py              # New module with TextSummarizer and CodeAnalyzer

tests/
├── unit/tools/
│   └── test_ollama_tools_unit.py   # Unit tests (no Ollama required)
└── integration/
    └── test_ollama_tools.py        # Integration tests (requires Ollama)
```

### Key Features

1. **Robust Input Validation**
   - Minimum length requirements
   - Parameter range validation
   - Clear error messages for invalid inputs

2. **Error Handling**
   - Connection errors (ExecutionStatus.FAILURE)
   - Timeout handling (ExecutionStatus.TIMEOUT)
   - Invalid input validation (ExecutionStatus.INVALID_INPUT)
   - Exception handling with metadata

3. **Performance Tracking**
   - Latency tracking in milliseconds
   - Metadata for debugging
   - Timestamp recording
   - Structured result format

4. **Async/Await Support**
   - Fully async implementation
   - Compatible with asyncio event loop
   - Non-blocking I/O with httpx

5. **Tool Contract**
   - Full ToolContract implementation
   - Input/output schemas defined
   - Constraints documented
   - Version tracking

## Testing

### Unit Tests (20 tests)
- **TextSummarizer** (9 tests)
  - Input validation (short text, empty, max_length bounds)
  - Schema structure validation
  - Configuration parameter handling
  - URL normalization

- **CodeAnalyzer** (9 tests)
  - Input validation (short code, empty, invalid type)
  - Schema structure validation
  - All analysis types validation
  - Configuration parameter handling
  - Analysis type enum verification

- **Integration** (3 tests)
  - Consistent interface between tools
  - Schema completeness
  - Ollama requirement marking

### Integration Tests (9 tests)
- TextSummarizer full execution (when Ollama available)
- CodeAnalyzer analysis types (quality, security, performance, documentation)
- Registry integration
- Error handling (connection, timeout)
- Performance tracking

### Test Results
```bash
$ pytest tests/unit/tools/test_ollama_tools_unit.py -v
20 passed, 1 skipped in 14.19s

$ pytest tests/ -v  # All tests
98 passed, 1 skipped in 12.34s
```

## Configuration

### Ollama Setup Required

Ensure Ollama is running with a model installed:
```bash
ollama pull mistral:7b  # or another model
ollama serve            # runs on http://localhost:11434 by default
```

### Custom Configuration

Both tools support custom Ollama URLs and models:
```python
summarizer = TextSummarizer(
    ollama_url="http://custom-host:8080",
    model="llama2:7b",
    timeout=60
)

analyzer = CodeAnalyzer(
    ollama_url="http://custom-host:8080",
    model="neural-chat",
    timeout=60
)
```

## Integration with ToolRegistry

Both tools are fully integrated with ToolRegistry:

```python
from agent_labs.tools import ToolRegistry, TextSummarizer, CodeAnalyzer

# Create registry
registry = ToolRegistry()

# Register tools
registry.register(TextSummarizer())
registry.register(CodeAnalyzer())

# List available tools
print(registry.list_tools())
# Output: ["text_summarizer", "code_analyzer"]

# Get tool schema
schema = registry.get("text_summarizer").get_schema()

# Execute with validation
result = await registry.execute(
    "text_summarizer",
    text="Long text...",
    validate_input=True  # Default: True
)

# Batch execution
operations = [
    ("text_summarizer", {"text": "Text 1..." * 5}),
    ("code_analyzer", {"code": "def test(): pass" * 2})
]
results = await registry.execute_batch(operations)
```

## Error Handling

### Connection Error
```python
result = await summarizer.execute(text="Text..." * 5)

if result.status == ExecutionStatus.FAILURE:
    if "Cannot connect" in result.error:
        print(f"Ollama not available: {result.error}")
```

### Timeout Error
```python
summarizer = TextSummarizer(timeout=5)
result = await summarizer.execute(text="Text..." * 5)

if result.status == ExecutionStatus.TIMEOUT:
    print("Request timed out")
```

### Validation Error
```python
result = await summarizer.execute(text="Short")  # < 50 chars

if result.status == ExecutionStatus.INVALID_INPUT:
    print(f"Invalid input: {result.error}")
```

## Performance Characteristics

- **TextSummarizer**: Typically 1-10 seconds per summarization
- **CodeAnalyzer**: Typically 2-15 seconds per analysis
- **Latency**: Tracked in `result.latency_ms`
- **Network**: Uses httpx for efficient async HTTP

## Metadata Example

TextSummarizer result metadata:
```python
{
    "tool_name": "text_summarizer",
    "model": "mistral:7b",
    "input_length": 500,           # words in input
    "temperature": 0.3
}
```

CodeAnalyzer result metadata:
```python
{
    "tool_name": "code_analyzer",
    "model": "mistral:7b",
    "analysis_type": "security",
    "language": "python"
}
```

## Limitations & Considerations

1. **Ollama Required**: These tools require a running Ollama instance
2. **Model Dependent**: Results quality depends on the LLM model used
3. **Latency**: LLM inference adds several seconds per request
4. **Network**: Requires connectivity to Ollama (local or remote)
5. **GPU Memory**: Running large models requires significant GPU memory

## Future Enhancements

- [ ] Caching layer for repeated summaries
- [ ] Streaming responses for large summaries
- [ ] Custom prompt templates
- [ ] Multiple model support (fallback models)
- [ ] Request queuing for high concurrency
- [ ] Batch processing optimization
- [ ] Cost tracking per request

## Commit Information

- **Commit**: 8211cef
- **Files Changed**: 5
- **Insertions**: +1,199
- **Branch**: feature/story-1-3/tools-framework

## Quick Reference

**TextSummarizer**
- Tool name: `text_summarizer`
- Ollama model: `mistral:7b` (configurable)
- Min text length: 50 characters
- Max summary length: 1000 words

**CodeAnalyzer**
- Tool name: `code_analyzer`
- Ollama model: `mistral:7b` (configurable)
- Min code length: 10 characters
- Analysis types: quality, security, performance, documentation

**Testing**
- Unit tests: Run without Ollama
- Integration tests: Require Ollama running
- Skip integration: `pytest -m "not ollama"`
- Run all: `pytest tests/unit/tools/test_ollama_tools_unit.py -v`
