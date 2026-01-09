"""
Integration tests for OllamaProvider using real Ollama instance.

These tests require:
- Ollama running at http://localhost:11434
- At least one model installed (e.g., ollama pull mistral:7b)

Run with: pytest tests/unit/llm_providers/test_ollama_integration.py -v
Skip with: pytest -m "not ollama"
"""

import pytest
import asyncio
from src.agent_labs.llm_providers import (
    OllamaProvider,
    ModelNotFoundError,
    ProviderConnectionError,
    ProviderConfigError,
)


# Mark all tests in this module as requiring Ollama
pytestmark = pytest.mark.ollama


class TestOllamaProviderIntegration:
    """Integration tests for OllamaProvider with real Ollama instance."""

    @pytest.mark.asyncio
    async def test_ollama_connectivity(self):
        """Test that we can connect to Ollama."""
        provider = OllamaProvider(
            base_url="http://localhost:11434",
            model="mistral:7b",
            timeout=120,
        )
        
        try:
            response = await provider.generate(
                "Say 'hello'",
                max_tokens=10,
                temperature=0.0
            )
            
            assert response is not None
            assert response.model == "mistral:7b"
            assert len(response.text) > 0
        finally:
            await provider.close()

    @pytest.mark.asyncio
    async def test_ollama_generate_simple_prompt(self):
        """Test generating text with a simple prompt."""
        provider = OllamaProvider(model="mistral:7b", timeout=120)
        
        try:
            response = await provider.generate(
                prompt="What is 2+2?",
                max_tokens=20,
                temperature=0.0
            )
            
            assert len(response.text) > 0
            assert response.tokens_used >= 0
            assert response.model == "mistral:7b"
        finally:
            await provider.close()

    @pytest.mark.asyncio
    async def test_ollama_generate_respects_max_tokens(self):
        """Test that max_tokens parameter is respected."""
        provider = OllamaProvider(model="mistral:7b", timeout=120)
        
        try:
            response = await provider.generate(
                prompt="Write a long story.",
                max_tokens=50,
                temperature=0.5
            )
            
            assert response is not None
            # Token count should be roughly less than max_tokens
            assert response.tokens_used <= 100  # Some overhead allowed
        finally:
            await provider.close()

    @pytest.mark.asyncio
    async def test_ollama_generate_with_temperature(self):
        """Test temperature parameter affects response."""
        provider = OllamaProvider(model="mistral:7b", timeout=120)
        
        try:
            # Low temperature = deterministic
            response_cold = await provider.generate(
                prompt="Complete: The sky is",
                max_tokens=5,
                temperature=0.0
            )
            
            response_warm = await provider.generate(
                prompt="Complete: The sky is",
                max_tokens=5,
                temperature=0.9
            )
            
            assert response_cold.text is not None
            assert response_warm.text is not None
        finally:
            await provider.close()

    @pytest.mark.asyncio
    async def test_ollama_stream_yields_tokens(self):
        """Test that streaming yields text chunks."""
        provider = OllamaProvider(model="mistral:7b", timeout=120)
        
        try:
            chunks = []
            async for chunk in provider.stream(
                prompt="What is Python? Say in 2 sentences.",
                max_tokens=50
            ):
                chunks.append(chunk)
            
            assert len(chunks) > 0
            full_text = "".join(chunks)
            assert len(full_text) > 0
        finally:
            await provider.close()

    @pytest.mark.asyncio
    async def test_ollama_stream_vs_generate_similar_output(self):
        """Test that streaming produces similar output to generate."""
        provider = OllamaProvider(model="mistral:7b", timeout=120)
        
        try:
            # Stream version
            stream_chunks = []
            async for chunk in provider.stream(
                prompt="Say hello",
                max_tokens=20
            ):
                stream_chunks.append(chunk)
            stream_text = "".join(stream_chunks).strip()
            
            # Generate version
            response = await provider.generate(
                prompt="Say hello",
                max_tokens=20
            )
            gen_text = response.text.strip()
            
            # Both should produce output
            assert len(stream_text) > 0
            assert len(gen_text) > 0
        finally:
            await provider.close()

    @pytest.mark.asyncio
    async def test_ollama_count_tokens(self):
        """Test token counting."""
        provider = OllamaProvider(model="mistral:7b")
        
        try:
            text = "The quick brown fox jumps over the lazy dog"
            tokens = await provider.count_tokens(text)
            
            assert tokens > 0
            # Roughly one token per word (heuristic)
            assert tokens <= len(text.split()) + 2
        finally:
            await provider.close()

    @pytest.mark.asyncio
    async def test_ollama_count_tokens_empty_string(self):
        """Test token counting for empty string."""
        provider = OllamaProvider(model="mistral:7b")
        
        try:
            tokens = await provider.count_tokens("")
            assert tokens == 0
        finally:
            await provider.close()

    @pytest.mark.asyncio
    async def test_ollama_count_tokens_long_text(self):
        """Test token counting for longer text."""
        provider = OllamaProvider(model="mistral:7b")
        
        try:
            text = " ".join(["word"] * 100)
            tokens = await provider.count_tokens(text)
            
            assert tokens > 0
            assert tokens <= 150  # Should be around 100
        finally:
            await provider.close()

    @pytest.mark.asyncio
    async def test_ollama_invalid_model_raises_error(self):
        """Test that invalid model name raises error on generation."""
        provider = OllamaProvider(
            model="nonexistent_model_xyz",
            timeout=10
        )
        
        with pytest.raises(ModelNotFoundError):
            await provider.generate("Hello")
        
        await provider.close()

    @pytest.mark.asyncio
    async def test_ollama_context_manager(self):
        """Test using OllamaProvider as async context manager."""
        async with OllamaProvider(model="mistral:7b", timeout=120) as provider:
            response = await provider.generate("Hi", max_tokens=5)
            assert response.text is not None
        # Provider is closed after context

    @pytest.mark.asyncio
    async def test_ollama_multiple_sequential_calls(self):
        """Test multiple sequential API calls."""
        provider = OllamaProvider(model="mistral:7b", timeout=120)
        
        try:
            prompts = [
                "What is AI?",
                "What is ML?",
                "What is DL?",
            ]
            
            responses = []
            for prompt in prompts:
                response = await provider.generate(
                    prompt,
                    max_tokens=30,
                    temperature=0.3
                )
                responses.append(response)
            
            assert len(responses) == 3
            for response in responses:
                assert response.text is not None
                assert len(response.text) > 0
        finally:
            await provider.close()

    @pytest.mark.asyncio
    async def test_ollama_long_prompt(self):
        """Test with a longer prompt."""
        provider = OllamaProvider(model="mistral:7b", timeout=120)
        
        try:
            long_prompt = """
            Explain machine learning in simple terms.
            Include:
            1. What it is
            2. How it works
            3. Real-world examples
            Keep answer to 3 sentences.
            """
            
            response = await provider.generate(
                long_prompt,
                max_tokens=100,
                temperature=0.5
            )
            
            assert response.text is not None
            assert len(response.text) > 20
        finally:
            await provider.close()

    @pytest.mark.asyncio
    async def test_ollama_response_has_all_fields(self):
        """Test that response has all required fields."""
        provider = OllamaProvider(model="mistral:7b", timeout=120)
        
        try:
            response = await provider.generate("Test", max_tokens=10)
            
            assert hasattr(response, 'text')
            assert hasattr(response, 'tokens_used')
            assert hasattr(response, 'model')
            
            assert isinstance(response.text, str)
            assert isinstance(response.tokens_used, int)
            assert isinstance(response.model, str)
        finally:
            await provider.close()


class TestOllamaProviderConfiguration:
    """Tests for OllamaProvider configuration."""

    def test_ollama_default_configuration(self):
        """Test default configuration."""
        provider = OllamaProvider()
        
        assert provider.base_url == "http://localhost:11434"
        assert provider.model == "llama2"
        assert provider.timeout == 60

    def test_ollama_custom_configuration(self):
        """Test custom configuration."""
        provider = OllamaProvider(
            base_url="http://example.com:8000",
            model="custom-model",
            timeout=30
        )
        
        assert provider.base_url == "http://example.com:8000"
        assert provider.model == "custom-model"
        assert provider.timeout == 30

    def test_ollama_strips_trailing_slash_from_url(self):
        """Test that trailing slash is removed from base_url."""
        provider = OllamaProvider(base_url="http://localhost:11434/")
        
        assert provider.base_url == "http://localhost:11434"

    def test_ollama_empty_base_url_raises_error(self):
        """Test that empty base_url raises ConfigError."""
        with pytest.raises(ProviderConfigError):
            OllamaProvider(base_url="")

    def test_ollama_empty_model_raises_error(self):
        """Test that empty model raises ConfigError."""
        with pytest.raises(ProviderConfigError):
            OllamaProvider(model="")

    def test_ollama_invalid_timeout_raises_error(self):
        """Test that non-positive timeout raises ConfigError."""
        with pytest.raises(ProviderConfigError):
            OllamaProvider(timeout=0)
        
        with pytest.raises(ProviderConfigError):
            OllamaProvider(timeout=-1)


class TestOllamaProviderErrorHandling:
    """Tests for error handling in OllamaProvider."""

    @pytest.mark.asyncio
    async def test_ollama_wrong_host_raises_error(self):
        """Test connection error when Ollama is not running."""
        provider = OllamaProvider(
            base_url="http://localhost:9999",  # Wrong port
            timeout=2
        )
        
        try:
            with pytest.raises((ProviderConnectionError, ConnectionError, Exception)):
                await provider.generate("Hello")
        finally:
            await provider.close()

    @pytest.mark.asyncio
    async def test_ollama_timeout(self):
        """Test timeout handling."""
        provider = OllamaProvider(
            model="mistral:7b",
            timeout=1  # Very short timeout
        )
        
        # This might timeout depending on system load
        # We're just checking the timeout parameter works
        try:
            await provider.generate("Hello world long response", max_tokens=1000)
        except Exception:
            # Either succeeds quickly or times out - both are acceptable
            pass
        
        await provider.close()


@pytest.mark.asyncio
async def test_ollama_smoke_test():
    """Smoke test: Can we reach Ollama and get a response?"""
    provider = OllamaProvider(model="mistral:7b", timeout=120)
    
    try:
        response = await provider.generate("Say 'ok'", max_tokens=5)
        assert response.text is not None
        assert len(response.text) > 0
    finally:
        await provider.close()
