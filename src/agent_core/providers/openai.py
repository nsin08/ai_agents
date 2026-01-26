"""OpenAI model provider for agent_core."""

from __future__ import annotations

import json
import os
import time
from typing import Any, Mapping, Sequence

import httpx

from ..model import ModelMessage, ModelResponse, ModelUsage, ToolCall, normalize_messages


class OpenAIProvider:
    """OpenAI chat-completions provider using httpx (no SDK)."""

    def __init__(
        self,
        model: str,
        base_url: str = "https://api.openai.com/v1",
        api_key: str | None = None,
        api_key_env: str = "OPENAI_API_KEY",
        timeout_s: float = 30.0,
        temperature: float = 0.0,
    ) -> None:
        if not model:
            raise ValueError("model cannot be empty")
        if not base_url:
            raise ValueError("base_url cannot be empty")
        if timeout_s <= 0:
            raise ValueError("timeout_s must be positive")
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.api_key_env = api_key_env
        self.timeout_s = timeout_s
        self.temperature = temperature

    async def generate(
        self,
        messages: Sequence[ModelMessage] | Sequence[Mapping[str, Any]],
        role: str,
    ) -> ModelResponse:
        api_key = self.api_key if self.api_key is not None else os.getenv(self.api_key_env, "")
        if not api_key:
            raise ValueError(f"Missing API key. Set {self.api_key_env}.")

        payload = {
            "model": self.model,
            "messages": normalize_messages(messages),
            "temperature": self.temperature,
        }

        headers = {"Authorization": f"Bearer {api_key}"}
        start = time.perf_counter()
        async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout_s) as client:
            response = await client.post("/chat/completions", json=payload, headers=headers)

        if response.status_code >= 400:
            raise RuntimeError(f"OpenAI request failed ({response.status_code}): {response.text}")

        data = response.json()
        choice = (data.get("choices") or [{}])[0]
        message = choice.get("message") or {}
        usage_data = data.get("usage") or {}

        usage = ModelUsage(
            prompt_tokens=usage_data.get("prompt_tokens"),
            completion_tokens=usage_data.get("completion_tokens"),
            total_tokens=usage_data.get("total_tokens"),
            latency_s=time.perf_counter() - start,
        )

        tool_calls_data = message.get("tool_calls") or []
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


__all__ = ["OpenAIProvider"]
