"""Short-term session memory for agent_core."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Mapping, Protocol, Sequence


def estimate_tokens(text: str) -> int:
    """Deterministic token estimate based on character count."""
    if not text:
        return 0
    return max(1, len(text) // 4)


@dataclass(frozen=True)
class SessionMessage:
    role: str
    content: str
    name: str | None = None
    tool_call_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_prompt_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"role": self.role, "content": self.content}
        if self.name:
            payload["name"] = self.name
        if self.tool_call_id:
            payload["tool_call_id"] = self.tool_call_id
        return payload


class SessionStore(Protocol):
    async def add_message(
        self,
        role: str,
        content: str,
        *,
        name: str | None = None,
        tool_call_id: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> None:
        ...

    async def get_context(self, max_tokens: int | None = None) -> list[dict[str, Any]]:
        ...

    async def clear(self) -> None:
        ...


class InMemorySessionStore:
    """In-memory session store with deterministic truncation."""

    def __init__(
        self,
        *,
        max_tokens: int | None = None,
        token_estimator: Callable[[str], int] | None = None,
    ) -> None:
        self._messages: list[SessionMessage] = []
        self._lock = asyncio.Lock()
        self._max_tokens = max_tokens
        self._token_estimator = token_estimator or estimate_tokens

    async def add_message(
        self,
        role: str,
        content: str,
        *,
        name: str | None = None,
        tool_call_id: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> None:
        if not role:
            raise ValueError("role must be provided")
        message = SessionMessage(
            role=role,
            content=content,
            name=name,
            tool_call_id=tool_call_id,
            metadata=dict(metadata or {}),
        )
        async with self._lock:
            self._messages.append(message)

    async def get_context(self, max_tokens: int | None = None) -> list[dict[str, Any]]:
        async with self._lock:
            messages = list(self._messages)
        limit = max_tokens if max_tokens is not None else self._max_tokens
        truncated = self._truncate(messages, limit)
        return [message.to_prompt_dict() for message in truncated]

    async def clear(self) -> None:
        async with self._lock:
            self._messages.clear()

    def _truncate(
        self,
        messages: Sequence[SessionMessage],
        max_tokens: int | None,
    ) -> list[SessionMessage]:
        if max_tokens is None or max_tokens <= 0:
            return list(messages)
        selected: list[SessionMessage] = []
        total_tokens = 0
        for message in reversed(messages):
            tokens = int(self._token_estimator(message.content))
            if not selected and tokens > max_tokens:
                selected.append(message)
                break
            if selected and total_tokens + tokens > max_tokens:
                continue
            selected.append(message)
            total_tokens += tokens
            if total_tokens >= max_tokens:
                break
        return list(reversed(selected))


__all__ = ["SessionMessage", "SessionStore", "InMemorySessionStore", "estimate_tokens"]
