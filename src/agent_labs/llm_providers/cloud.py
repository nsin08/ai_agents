"""
Cloud provider adapter template.

This is a stub that defines the interface shape for future cloud providers
(OpenAI, Anthropic, etc.) without locking in a vendor.
"""

from typing import AsyncIterator

from .base import Provider, LLMResponse
from .exceptions import ProviderConfigError


class CloudProvider(Provider):
    """Template for cloud LLM providers (Phase 2)."""

    def __init__(self, *args, **kwargs):
        raise ProviderConfigError(
            "CloudProvider is a template only. Implement a provider-specific adapter."
        )

    async def generate(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> LLMResponse:
        raise ProviderConfigError("CloudProvider is not implemented.")

    async def stream(
        self,
        prompt: str,
        max_tokens: int = 1000,
    ) -> AsyncIterator[str]:
        raise ProviderConfigError("CloudProvider is not implemented.")

    async def count_tokens(self, text: str) -> int:
        raise ProviderConfigError("CloudProvider is not implemented.")
