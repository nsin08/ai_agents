"""Model interface definitions for agent_core."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol, Sequence, runtime_checkable


@dataclass(frozen=True)
class ModelMessage:
    role: str
    content: str
    name: str | None = None
    tool_call_id: str | None = None


@dataclass(frozen=True)
class ToolCall:
    name: str
    arguments: Mapping[str, Any]
    call_id: str | None = None


@dataclass(frozen=True)
class ModelUsage:
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None
    latency_s: float | None = None
    cost: float | None = None


@dataclass(frozen=True)
class ModelResponse:
    text: str
    role: str = "assistant"
    tool_calls: Sequence[ToolCall] | None = None
    usage: ModelUsage | None = None
    prompt_hash: str | None = None


@runtime_checkable
class ModelClient(Protocol):
    async def generate(
        self,
        messages: Sequence[ModelMessage] | Sequence[Mapping[str, Any]],
        role: str,
    ) -> ModelResponse:
        ...


def normalize_messages(
    messages: Sequence[ModelMessage] | Sequence[Mapping[str, Any]] | Sequence[str],
) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for message in messages:
        if isinstance(message, ModelMessage):
            payload: dict[str, Any] = {"role": message.role, "content": message.content}
            if message.name:
                payload["name"] = message.name
            if message.tool_call_id:
                payload["tool_call_id"] = message.tool_call_id
            normalized.append(payload)
            continue
        if isinstance(message, Mapping):
            normalized.append(dict(message))
            continue
        normalized.append({"role": "user", "content": str(message)})
    return normalized


__all__ = [
    "ModelClient",
    "ModelMessage",
    "ModelResponse",
    "ModelUsage",
    "ToolCall",
    "normalize_messages",
]
