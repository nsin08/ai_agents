"""Ollama model provider for agent_core."""

from __future__ import annotations

import json
import time
from typing import Any, Mapping, Sequence

import httpx

from ..model import ModelMessage, ModelResponse, ModelUsage, ToolCall, normalize_messages


class OllamaProvider:
    """Ollama chat provider (local-first)."""

    def __init__(
        self,
        model: str,
        base_url: str = "http://localhost:11434",
        timeout_s: float = 30.0,
    ) -> None:
        if not model:
            raise ValueError("model cannot be empty")
        if not base_url:
            raise ValueError("base_url cannot be empty")
        if timeout_s <= 0:
            raise ValueError("timeout_s must be positive")
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout_s = timeout_s

    async def generate(
        self,
        messages: Sequence[ModelMessage] | Sequence[Mapping[str, Any]],
        role: str,
    ) -> ModelResponse:
        payload = {
            "model": self.model,
            "messages": normalize_messages(messages),
            "stream": False,
        }

        start = time.perf_counter()
        async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout_s) as client:
            response = await client.post("/api/chat", json=payload)

        if response.status_code >= 400:
            raise RuntimeError(f"Ollama request failed ({response.status_code}): {response.text}")

        data = response.json()
        message = data.get("message") or {}
        tool_calls_data = message.get("tool_calls") or data.get("tool_calls") or []
        prompt_tokens = data.get("prompt_eval_count")
        completion_tokens = data.get("eval_count")
        total_tokens = None
        if isinstance(prompt_tokens, int) and isinstance(completion_tokens, int):
            total_tokens = prompt_tokens + completion_tokens

        usage = ModelUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            latency_s=time.perf_counter() - start,
        )

        tool_calls: list[ToolCall] = []
        for call in tool_calls_data:
            function = call.get("function") or {}
            arguments = function.get("arguments")
            parsed_args: Any = {}
            if isinstance(arguments, str) and arguments.strip():
                try:
                    parsed_args = json.loads(arguments)
                except json.JSONDecodeError:
                    parsed_args = {"raw": arguments}
            elif isinstance(arguments, Mapping):
                parsed_args = dict(arguments)
            tool_calls.append(
                ToolCall(
                    name=function.get("name") or "",
                    arguments=parsed_args if isinstance(parsed_args, Mapping) else {"value": parsed_args},
                    call_id=call.get("id"),
                )
            )

        return ModelResponse(
            text=message.get("content") or "",
            role=message.get("role") or "assistant",
            tool_calls=tool_calls or None,
            usage=usage,
        )


__all__ = ["OllamaProvider"]
