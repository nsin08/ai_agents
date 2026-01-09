"""
Unit tests for context engineering utilities.
"""

import pytest

from src.agent_labs.context import (
    PromptTemplate,
    TemplateEngine,
    ContextSummarizer,
    chunk_fixed,
    chunk_sliding,
    chunk_semantic_mock,
    estimate_tokens,
    TokenCounter,
    ContextWindow,
    TokenLimitExceededError,
    to_json,
    from_json,
)
from src.agent_labs.llm_providers import MockProvider
from src.agent_labs.context.templates import summarize_with_provider


def test_prompt_template_format():
    template = PromptTemplate(
        template="Hello {name}",
        variables=["name"],
        engine=TemplateEngine.SIMPLE,
    )
    result = template.format(name="World")
    assert result == "Hello World"


def test_prompt_template_missing_variable():
    template = PromptTemplate(
        template="Hello {name}",
        variables=["name"],
        engine=TemplateEngine.SIMPLE,
    )
    with pytest.raises(ValueError):
        template.format()


def test_prompt_template_jinja_missing_dependency():
    template = PromptTemplate(
        template="Hello {{ name }}",
        variables=["name"],
        engine=TemplateEngine.JINJA2,
    )
    try:
        import jinja2  # noqa: F401
        rendered = template.format(name="World")
        assert rendered == "Hello World"
    except ImportError:
        with pytest.raises(ImportError):
            template.format(name="World")


def test_chunk_fixed():
    chunks = chunk_fixed("abcdefgh", size=3)
    assert chunks == ["abc", "def", "gh"]


def test_chunk_sliding():
    chunks = chunk_sliding("abcdefgh", size=4, overlap=2)
    assert chunks == ["abcd", "cdef", "efgh"]


def test_chunk_sliding_invalid_overlap():
    with pytest.raises(ValueError):
        chunk_sliding("text", size=4, overlap=4)


def test_chunk_semantic_mock():
    text = "First sentence. Second sentence. Third sentence."
    chunks = chunk_semantic_mock(text, max_chars=25)
    assert len(chunks) >= 2
    assert all(chunk.endswith(".") for chunk in chunks)


def test_estimate_tokens():
    count = estimate_tokens("one two three", tokens_per_word=1.0)
    assert count == 3


def test_token_counter_special_chars():
    count = TokenCounter.count("Hello, world!")
    assert count >= 2


@pytest.mark.asyncio
async def test_context_window_error_strategy():
    window = ContextWindow(max_tokens=3, overflow_strategy="error")
    await window.add("one")
    with pytest.raises(TokenLimitExceededError):
        await window.add("one two three four")


@pytest.mark.asyncio
async def test_context_window_drop_strategy():
    window = ContextWindow(max_tokens=4, overflow_strategy="drop")
    await window.add("one two")
    await window.add("three four")
    assert len(window.items) == 2
    await window.add("five six")
    assert len(window.items) == 2


@pytest.mark.asyncio
async def test_context_window_summarize_strategy():
    summarizer = ContextSummarizer(provider=MockProvider())
    window = ContextWindow(
        max_tokens=6,
        overflow_strategy="summarize",
        summarizer=summarizer,
    )
    await window.add("one two three four")
    await window.add("five six seven eight")
    assert len(window.items) >= 1


def test_json_serialization_round_trip():
    payload = {"a": 1, "b": "two"}
    encoded = to_json(payload)
    decoded = from_json(encoded)
    assert decoded == payload


@pytest.mark.asyncio
async def test_summarize_with_provider_mock():
    provider = MockProvider()
    summary = await summarize_with_provider(provider, "Example text")
    assert isinstance(summary, str)
    assert len(summary) > 0


@pytest.mark.asyncio
async def test_context_summarizer_truncates_input():
    summarizer = ContextSummarizer(provider=MockProvider(), max_input_chars=10)
    text = "Sentence one. Sentence two. Sentence three."
    summary = await summarizer.summarize(text, max_length=10)
    assert isinstance(summary, str)
