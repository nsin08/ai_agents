"""Deterministic mock model provider for agent_core."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence


@dataclass(frozen=True)
class ModelResponse:
    """Simple response container for mock model provider."""

    text: str
    role: str
    prompt_hash: str


class MockProvider:
    """Deterministic mock provider based on prompt hash + seed."""

    def __init__(
        self,
        responses: Mapping[str, str] | Sequence[str] | None = None,
        seed: int = 42,
        role_responses: Mapping[str, Mapping[str, str] | Sequence[str]] | None = None,
    ) -> None:
        self._responses = list(responses.values()) if isinstance(responses, Mapping) else list(responses or [])
        self._seed = seed
        self._role_responses = role_responses or {}

    async def query(self, messages: Iterable[Mapping[str, Any]] | Iterable[str], role: str) -> ModelResponse:
        prompt_hash = self._hash_prompt(messages, role)
        text = self._select_response(prompt_hash, role)
        return ModelResponse(text=text, role=role, prompt_hash=prompt_hash)

    def _hash_prompt(self, messages: Iterable[Mapping[str, Any]] | Iterable[str], role: str) -> str:
        payload = {
            "role": role,
            "messages": list(messages),
            "seed": self._seed,
        }
        encoded = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def _select_response(self, prompt_hash: str, role: str) -> str:
        role_pool = self._role_responses.get(role)
        if role_pool:
            responses = list(role_pool.values()) if isinstance(role_pool, Mapping) else list(role_pool)
        else:
            responses = self._responses

        if responses:
            index = int(prompt_hash, 16) % len(responses)
            return responses[index]

        return f"mock::{role}::{prompt_hash[:8]}"


__all__ = ["MockProvider", "ModelResponse"]
