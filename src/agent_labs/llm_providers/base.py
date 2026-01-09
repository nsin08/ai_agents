"""
LLM Provider abstraction layer.

Provides async interface for multiple LLM backends (OpenAI, Ollama, Anthropic, etc.)
All implementations must support:
- Async operations (async/await)
- Token counting
- Streaming responses
- Error handling (rate limits, timeouts)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import AsyncIterator, Optional


@dataclass
class LLMResponse:
    """Response from LLM provider."""

    text: str
    """Generated text response."""

    tokens_used: int
    """Number of tokens used."""

    model: str
    """Model used for generation."""


class Provider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """
        Generate text response from prompt.

        Args:
            prompt: Input text to send to LLM
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0 = deterministic, 1.0 = random)

        Returns:
            LLMResponse with generated text + metadata

        Example:
            >>> provider = MockProvider()
            >>> response = await provider.generate("Hello, world!")
            >>> print(response.text)
        """
        pass

    @abstractmethod
    async def stream(
        self,
        prompt: str,
        max_tokens: int = 1000,
    ) -> AsyncIterator[str]:
        """
        Stream text response tokens as they arrive.

        Args:
            prompt: Input text
            max_tokens: Maximum tokens to generate

        Yields:
            Chunks of generated text

        Example:
            >>> provider = MockProvider()
            >>> async for chunk in provider.stream("Hello"):
            ...     print(chunk, end="", flush=True)
        """
        pass

    @abstractmethod
    async def count_tokens(self, text: str) -> int:
        """
        Count tokens in text without making API call.

        Args:
            text: Text to count

        Returns:
            Number of tokens

        Example:
            >>> provider = MockProvider()
            >>> tokens = await provider.count_tokens("Hello, world!")
            >>> print(tokens)  # Output: 4
        """
        pass
