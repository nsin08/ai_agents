"""
Mock LLM provider for deterministic testing.

MockProvider returns fixed responses without making any external API calls.
Perfect for:
- Unit testing agent logic (deterministic output)
- CI/CD pipelines (zero external dependencies)
- Development without API costs
- Reproducible test runs
"""

from typing import AsyncIterator

from .base import Provider, LLMResponse


class MockProvider(Provider):
    """
    Deterministic mock provider for testing.

    Returns fixed responses for testing without external API calls.
    Perfect for unit tests (deterministic output).
    
    Example:
        >>> provider = MockProvider()
        >>> response = await provider.generate("Hello")
        >>> print(response.text)
        Mock response to: Hello
        >>> print(response.model)
        mock
    """

    # Simple mock responses for determinism
    _MOCK_RESPONSES = {
        "Hello, world!": "Hello! I'm a mock LLM responding to your greeting.",
        "Test prompt": "This is a deterministic test response.",
        "What is 2+2?": "The answer to 2+2 is 4.",
    }

    def __init__(self, name: str = "mock"):
        """
        Initialize MockProvider.
        
        Args:
            name: Model name to use in responses (default: "mock")
        """
        self.name = name

    async def generate(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """
        Return fixed mock response.
        
        Args:
            prompt: Input prompt (used to look up mock response)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (ignored for mock)
            
        Returns:
            LLMResponse with mock text + metadata
        """
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
            model=self.name
        )

    async def stream(
        self,
        prompt: str,
        max_tokens: int = 1000,
    ) -> AsyncIterator[str]:
        """
        Stream mock response tokens.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            
        Yields:
            Chunks of generated text (words with spaces)
        """
        response = await self.generate(prompt, max_tokens)

        # Yield text in small chunks to simulate streaming
        words = response.text.split()
        for word in words:
            yield word + " "

    async def count_tokens(self, text: str) -> int:
        """
        Count tokens (mock: ~1 token per word).
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Estimated token count
        """
        if not text:
            return 0
        return len(text.split())
