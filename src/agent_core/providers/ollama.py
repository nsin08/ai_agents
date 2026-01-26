"""Ollama model provider for agent_core."""

from __future__ import annotations

import time
from typing import Any, Mapping, Sequence

import httpx

from ..model import ModelMessage, ModelResponse, ModelUsage, normalize_messages


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

        return ModelResponse(
            text=message.get("content") or "",
            role=message.get("role") or "assistant",
            usage=usage,
        )


__all__ = ["OllamaProvider"]
