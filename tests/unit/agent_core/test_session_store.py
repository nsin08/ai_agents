"""Tests for short-term session memory."""

from __future__ import annotations

import asyncio

import pytest

from agent_core.memory import InMemorySessionStore, estimate_tokens


@pytest.mark.asyncio
async def test_add_message_and_get_context() -> None:
    store = InMemorySessionStore()
    await store.add_message("user", "hi")
    await store.add_message("assistant", "hello")

    context = await store.get_context()

    assert context == [
        {"role": "user", "content": "hi"},
        {"role": "assistant", "content": "hello"},
    ]


@pytest.mark.asyncio
async def test_tool_message_fields_in_context() -> None:
    store = InMemorySessionStore()
    await store.add_message(
        "tool",
        "result",
        name="calculator",
        tool_call_id="call-1",
    )

    context = await store.get_context()

    assert context[-1]["role"] == "tool"
    assert context[-1]["name"] == "calculator"
    assert context[-1]["tool_call_id"] == "call-1"


@pytest.mark.asyncio
async def test_truncation_drops_oldest_messages() -> None:
    store = InMemorySessionStore(max_tokens=2)
    await store.add_message("user", "1111")  # ~1 token
    await store.add_message("assistant", "2222")  # ~1 token
    await store.add_message("user", "3333")  # ~1 token

    context = await store.get_context()

    assert [msg["content"] for msg in context] == ["2222", "3333"]


@pytest.mark.asyncio
async def test_get_context_override_max_tokens() -> None:
    store = InMemorySessionStore(max_tokens=10)
    await store.add_message("user", "1111")
    await store.add_message("assistant", "2222")

    context = await store.get_context(max_tokens=1)

    assert [msg["content"] for msg in context] == ["2222"]


@pytest.mark.asyncio
async def test_clear_resets_state() -> None:
    store = InMemorySessionStore()
    await store.add_message("user", "hi")
    await store.clear()

    context = await store.get_context()

    assert context == []


@pytest.mark.asyncio
async def test_concurrent_add_message() -> None:
    store = InMemorySessionStore()
    await asyncio.gather(
        *[store.add_message("user", f"msg-{i}") for i in range(50)]
    )

    context = await store.get_context()

    assert len(context) == 50
    contents = {msg["content"] for msg in context}
    assert contents == {f"msg-{i}" for i in range(50)}


def test_estimate_tokens_is_deterministic() -> None:
    assert estimate_tokens("abcd") == estimate_tokens("abcd")
