"""Tests for agent_core model providers."""

from __future__ import annotations

import pytest

from agent_core.providers import OllamaProvider, OpenAIProvider


def test_openai_provider_requires_model() -> None:
    with pytest.raises(ValueError, match="model cannot be empty"):
        OpenAIProvider(model="")


@pytest.mark.asyncio
async def test_openai_provider_requires_api_key() -> None:
    provider = OpenAIProvider(model="gpt-4", api_key="")

    with pytest.raises(ValueError, match="Missing API key"):
        await provider.generate([{"role": "user", "content": "hi"}], role="actor")


def test_ollama_provider_requires_model() -> None:
    with pytest.raises(ValueError, match="model cannot be empty"):
        OllamaProvider(model="")


def test_ollama_provider_requires_base_url() -> None:
    with pytest.raises(ValueError, match="base_url cannot be empty"):
        OllamaProvider(model="llama2", base_url="")
