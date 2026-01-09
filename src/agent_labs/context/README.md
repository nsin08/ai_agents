# Context Engineering Utilities

Utilities for prompt templates, chunking strategies, token estimation, and context windows.

## Components

- `PromptTemplate`: variable substitution with explicit engine selection.
- Chunking: fixed size, sliding window, semantic (mock).
- Token counting: model-agnostic estimates with overflow checks.
- `ContextWindow`: token budgeting helper with overflow strategies.
- Serialization: JSON and YAML helpers.
- Examples: common prompt patterns (Q&A, reasoning, tool use).

## Prompt Templates

```python
from agent_labs.context import PromptTemplate, TemplateEngine

template = PromptTemplate(
    template="Context: {context}\nQuestion: {question}\nAnswer:",
    variables=["context", "question"],
    engine=TemplateEngine.SIMPLE,
)
prompt = template.format(context="...", question="What is AI?")
```

## Chunking Strategies

```python
from agent_labs.context import chunk_fixed, chunk_sliding, chunk_semantic_mock

chunks = chunk_fixed(text, size=500)
chunks = chunk_sliding(text, size=500, overlap=50)
chunks = chunk_semantic_mock(text, max_chars=600)
```

## Context Window

```python
from agent_labs.context import ContextWindow, ContextSummarizer

window = ContextWindow(max_tokens=4000, overflow_strategy="drop")
await window.add("system prompt")
if window.fits("user input"):
    await window.add("user input")
```

## Summarization

```python
from agent_labs.context import ContextSummarizer, summarize_with_provider
from agent_labs.llm_providers import MockProvider

summary = await summarize_with_provider(MockProvider(), "Long text...")

summarizer = ContextSummarizer(provider=MockProvider(), max_input_chars=10000)
summary = await summarizer.summarize("Long text...", max_length=500)
```

## Notes

- Token estimation uses: 1.3 tokens/word + 0.5 per special char.
- ContextWindow overflow strategies: error, drop, summarize.
- YAML serialization requires PyYAML.
