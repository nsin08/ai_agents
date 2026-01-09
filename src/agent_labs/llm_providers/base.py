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


class MockProvider(Provider):
    """
    Deterministic mock provider for testing.

    Returns fixed responses for testing without external API calls.
    Perfect for unit tests (deterministic output).
    """

    # Simple mock responses for determinism
    _MOCK_RESPONSES = {
        "Hello, world!": "Hello! I'm a mock LLM responding to your greeting.",
        "Test prompt": "This is a deterministic test response.",
        "What is 2+2?": "The answer to 2+2 is 4.",
    }

    async def generate(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """Return fixed mock response."""
        # Get response from mock dictionary, or generate a default
        text = self._MOCK_RESPONSES.get(
            prompt,
            f"Mock response to: {prompt}"
        )

        # Simulate token counting (roughly 1 token per word)
        tokens = len(text.split())
        tokens = min(tokens, max_tokens)  # Respect max_tokens

        return LLMResponse(
            text=text[:max_tokens * 4],  # Rough estimate: 4 chars per token
            tokens_used=tokens,
            model="mock"
        )

    async def stream(
        self,
        prompt: str,
        max_tokens: int = 1000,
    ) -> AsyncIterator[str]:
        """Stream mock response tokens."""
        response = await self.generate(prompt, max_tokens)

        # Yield text in small chunks to simulate streaming
        words = response.text.split()
        for word in words:
            yield word + " "

    async def count_tokens(self, text: str) -> int:
        """Count tokens (mock: ~1 token per word)."""
        if not text:
            return 0
        return len(text.split())
