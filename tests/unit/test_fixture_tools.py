"""Tests for FixtureToolProvider."""

from __future__ import annotations

import pytest

from agent_core.providers import FixtureNotFoundError, FixtureToolProvider, hash_args


@pytest.mark.asyncio
async def test_fixture_tool_provider_replays_result(fixture_tool_provider: FixtureToolProvider) -> None:
    result = await fixture_tool_provider.execute(
        "calculator",
        {"a": 2, "b": 2},
        tool_version="1.0",
    )

    assert result == {"value": 4}


@pytest.mark.asyncio
async def test_fixture_tool_provider_missing_fixture_raises() -> None:
    provider = FixtureToolProvider("tests/fixtures/tool_fixtures.json")

    with pytest.raises(FixtureNotFoundError):
        await provider.execute("calculator", {"a": 3, "b": 3}, tool_version="1.0")


def test_hash_args_is_stable() -> None:
    args = {"b": 2, "a": 2}
    first = hash_args(args)
    second = hash_args({"a": 2, "b": 2})

    assert first == second
