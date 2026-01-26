"""Tests for MockProvider."""

from __future__ import annotations

import pytest

from agent_core.model import ModelMessage
from agent_core.providers import MockProvider


@pytest.mark.asyncio
async def test_mock_provider_deterministic(mock_provider: MockProvider) -> None:
    messages = [{"role": "user", "content": "Hello"}]

    first = await mock_provider.generate(messages, role="actor")
    second = await mock_provider.generate(messages, role="actor")

    assert first.text == second.text
    assert first.prompt_hash == second.prompt_hash
    assert first.usage is not None


@pytest.mark.asyncio
async def test_mock_provider_role_specific_responses() -> None:
    provider = MockProvider(
        responses=["default"],
        role_responses={"planner": ["plan-response"]},
        seed=7,
    )

    messages = ["Plan something"]
    response = await provider.generate(messages, role="planner")

    assert response.text == "plan-response"


@pytest.mark.asyncio
async def test_mock_provider_seed_changes_response() -> None:
    messages = ["Same prompt"]

    provider_a = MockProvider(responses=["A", "B"], seed=1)
    provider_b = MockProvider(responses=["A", "B"], seed=2)

    response_a = await provider_a.generate(messages, role="actor")
    response_b = await provider_b.generate(messages, role="actor")

    assert response_a.prompt_hash != response_b.prompt_hash


@pytest.mark.asyncio
async def test_mock_provider_accepts_model_messages() -> None:
    provider = MockProvider(responses=["ok"], seed=1)
    messages = [ModelMessage(role="user", content="Hello")]

    response = await provider.generate(messages, role="actor")

    assert response.text == "ok"
