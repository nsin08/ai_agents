"""
Mock LLM provider for deterministic testing.

MockProvider returns fixed responses without making any external API calls.
Perfect for:
- Unit testing agent logic (deterministic output)
- CI/CD pipelines (zero external dependencies)
- Development without API costs
- Reproducible test runs
"""

from typing import AsyncIterator, List, Optional, Dict

from .base import Provider, LLMResponse


class MockProvider(Provider):
    """
    Deterministic mock provider for testing.

    Returns fixed responses for testing without external API calls.
    Perfect for unit tests (deterministic output).
    
    Supports three modes:
    1. Dictionary mapping (prompt -> response)
    2. Response sequence (returns responses in order)
    3. Default fallback (auto-generates response)
    
    Examples:
        # Default mode
        >>> provider = MockProvider()
        >>> response = await provider.generate("Hello")
        >>> print(response.text)
        Mock response to: Hello
        
        # Custom response map
        >>> provider = MockProvider(responses={"test": "custom"})
        >>> response = await provider.generate("test")
        >>> print(response.text)
        custom
        
        # Response sequence for multi-turn conversations
        >>> provider = MockProvider(response_sequence=["First", "Second", "Third"])
        >>> r1 = await provider.generate("any prompt")
        >>> r2 = await provider.generate("another prompt")
        >>> print(r1.text, r2.text)
        First Second
    """

    # Default mock responses for determinism
    _DEFAULT_RESPONSES = {
        "Hello, world!": "Hello! I'm a mock LLM responding to your greeting.",
        "Test prompt": "This is a deterministic test response.",
        "What is 2+2?": "The answer to 2+2 is 4.",
    }

    def __init__(
        self,
        name: str = "mock",
        responses: Optional[Dict[str, str]] = None,
        response_sequence: Optional[List[str]] = None,
        default_response: Optional[str] = None
    ):
        """
        Initialize MockProvider.
        
        Args:
            name: Model name to use in responses (default: "mock")
            responses: Custom prompt -> response mapping (overrides defaults)
            response_sequence: List of responses to return in sequence (for multi-turn)
            default_response: Default response when no match found (overrides auto-generation)
        
        Note:
            If both responses and response_sequence are provided, response_sequence takes precedence.
        """
        self.name = name
        self._responses = responses if responses is not None else self._DEFAULT_RESPONSES.copy()
        self._response_sequence = response_sequence or []
        self._sequence_index = 0
        self._default_response = default_response

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
        # Priority 1: Use response sequence if available
        if self._response_sequence:
            if self._sequence_index < len(self._response_sequence):
                text = self._response_sequence[self._sequence_index]
                self._sequence_index += 1
            else:
                # Sequence exhausted, use last response
                text = self._response_sequence[-1]
        # Priority 2: Check response map
        elif prompt in self._responses:
            text = self._responses[prompt]
        # Priority 3: Use default response if provided
        elif self._default_response:
            text = self._default_response
        # Priority 4: Generate default response
        else:
            text = f"Mock response to: {prompt}"

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
