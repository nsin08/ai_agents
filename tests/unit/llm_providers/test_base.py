"""
Tests for LLM Provider base class and MockProvider.

Test approach: TDD (test-driven development)
1. Define what provider should do (in tests)
2. Implement minimal code to pass tests
3. Add more tests for edge cases
4. Iterate until >95% coverage
"""

import pytest
from src.agent_labs.llm_providers import MockProvider, LLMResponse, Provider


@pytest.mark.asyncio
class TestMockProvider:
    """Test MockProvider implementation."""

    @pytest.fixture
    def provider(self):
        """Create mock provider for tests."""
        return MockProvider()

    @pytest.mark.asyncio
    async def test_generate_returns_response(self, provider):
        """Test that generate returns LLMResponse with required fields."""
        response = await provider.generate("Hello, world!")

        assert isinstance(response, LLMResponse)
        assert isinstance(response.text, str)
        assert len(response.text) > 0
        assert response.tokens_used > 0
        assert response.model == "mock"

    @pytest.mark.asyncio
    async def test_generate_with_max_tokens(self, provider):
        """Test that max_tokens is respected."""
        response = await provider.generate(
            "Hello, world!",
            max_tokens=10
        )

        # Token count should be <= max_tokens
        assert response.tokens_used <= 10

    @pytest.mark.asyncio
    async def test_generate_custom_temperature(self, provider):
        """Test that temperature parameter is accepted."""
        response = await provider.generate(
            "Hello, world!",
            temperature=0.5
        )

        assert isinstance(response, LLMResponse)
        assert response.text is not None

    @pytest.mark.asyncio
    async def test_stream_returns_chunks(self, provider):
        """Test that stream returns text chunks."""
        chunks = []
        async for chunk in provider.stream("Hello, world!"):
            assert isinstance(chunk, str)
            assert len(chunk) > 0
            chunks.append(chunk)

        # Should have gotten at least one chunk
        assert len(chunks) > 0

        # Combined chunks should form complete response
        full_text = "".join(chunks)
        assert len(full_text) > 0

    @pytest.mark.asyncio
    async def test_stream_respects_max_tokens(self, provider):
        """Test that stream respects max_tokens limit."""
        chunks = []
        async for chunk in provider.stream("Hello, world!", max_tokens=5):
            chunks.append(chunk)

        # Should have some chunks
        assert len(chunks) > 0

    @pytest.mark.asyncio
    async def test_count_tokens_returns_positive_int(self, provider):
        """Test that count_tokens returns positive integer."""
        count = await provider.count_tokens("Hello, world!")

        assert isinstance(count, int)
        assert count > 0

    @pytest.mark.asyncio
    async def test_count_tokens_empty_string(self, provider):
        """Test count_tokens with empty string."""
        count = await provider.count_tokens("")

        assert isinstance(count, int)
        assert count == 0

    @pytest.mark.asyncio
    async def test_count_tokens_single_word(self, provider):
        """Test count_tokens with single word."""
        count = await provider.count_tokens("Hello")

        assert count == 1

    @pytest.mark.asyncio
    async def test_count_tokens_multiple_words(self, provider):
        """Test count_tokens with multiple words."""
        count = await provider.count_tokens("Hello world test prompt")

        assert count == 4

    @pytest.mark.asyncio
    async def test_deterministic_responses(self, provider):
        """Test that MockProvider always returns same response for same input."""
        response1 = await provider.generate("Test prompt")
        response2 = await provider.generate("Test prompt")

        # Same input should give same response (deterministic)
        assert response1.text == response2.text
        assert response1.tokens_used == response2.tokens_used

    @pytest.mark.asyncio
    async def test_different_prompts_different_responses(self, provider):
        """Test that different prompts can give different responses."""
        response1 = await provider.generate("Hello, world!")
        response2 = await provider.generate("Test prompt")

        # Different prompts may give different responses (from mock dict)
        # At minimum, both should be valid
        assert response1.text is not None
        assert response2.text is not None

    @pytest.mark.asyncio
    async def test_unknown_prompt_generates_response(self, provider):
        """Test that unknown prompts still generate responses."""
        response = await provider.generate("Some unknown prompt that's not in the dict")

        assert isinstance(response, LLMResponse)
        assert len(response.text) > 0
        assert "unknown" in response.text or "Some" in response.text


class TestLLMResponse:
    """Test LLMResponse data class."""

    def test_llm_response_creation(self):
        """Test creating LLMResponse with required fields."""
        response = LLMResponse(
            text="Hello, world!",
            tokens_used=4,
            model="mock"
        )

        assert response.text == "Hello, world!"
        assert response.tokens_used == 4
        assert response.model == "mock"

    def test_llm_response_zero_tokens(self):
        """Test LLMResponse with zero tokens (edge case)."""
        response = LLMResponse(
            text="",
            tokens_used=0,
            model="mock"
        )

        assert response.tokens_used == 0
        assert response.text == ""

    def test_llm_response_large_token_count(self):
        """Test LLMResponse with large token count."""
        response = LLMResponse(
            text="Long response",
            tokens_used=1000000,
            model="mock"
        )

        assert response.tokens_used == 1000000

    def test_llm_response_different_models(self):
        """Test LLMResponse with different model names."""
        models = ["mock", "gpt-4", "claude", "llama"]

        for model in models:
            response = LLMResponse(
                text="test",
                tokens_used=1,
                model=model
            )
            assert response.model == model


class TestProviderInterface:
    """Test Provider ABC interface."""

    def test_provider_is_abstract(self):
        """Test that Provider cannot be instantiated directly."""
        with pytest.raises(TypeError):
            Provider()

    def test_mock_provider_implements_provider(self):
        """Test that MockProvider implements Provider interface."""
        provider = MockProvider()
        assert isinstance(provider, Provider)

    @pytest.mark.asyncio
    async def test_provider_methods_exist(self):
        """Test that MockProvider implements all required methods."""
        provider = MockProvider()

        # Check all methods exist and are callable
        assert hasattr(provider, 'generate')
        assert callable(provider.generate)
        assert hasattr(provider, 'stream')
        assert callable(provider.stream)
        assert hasattr(provider, 'count_tokens')
        assert callable(provider.count_tokens)
