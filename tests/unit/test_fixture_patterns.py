"""
Example tests demonstrating fixture factory patterns.

This module shows best practices for using the shared fixtures
and testing patterns in the ai_agents project.

Test Patterns Demonstrated:
1. Basic fixture usage (mock_provider, agent_context_factory)
2. Custom mock responses for deterministic testing
3. Response sequences for multi-turn conversations
4. Tool registry testing
5. Test data fixtures usage
6. Parametrized tests with fixtures
7. Integration test patterns with markers
"""

import pytest
from src.agent_labs.llm_providers import MockProvider, LLMResponse
from src.agent_labs.orchestrator import Agent


# ============================================================================
# Pattern 1: Basic Fixture Usage
# ============================================================================


@pytest.mark.asyncio
class TestBasicFixtureUsage:
    """Examples of using basic fixtures from conftest.py."""

    async def test_mock_provider_fixture(self, mock_provider):
        """Demonstrate using the mock_provider fixture."""
        # The mock_provider fixture is automatically injected
        response = await mock_provider.generate("Hello, world!")
        
        assert isinstance(response, LLMResponse)
        assert response.model == "mock"
        assert len(response.text) > 0

    async def test_mock_agent_fixture(self, mock_agent):
        """Demonstrate using the mock_agent fixture."""
        # Agent is pre-configured with MockProvider
        result = await mock_agent.run("Test prompt")
        
        assert result is not None
        assert isinstance(result, str)

    def test_sample_prompts_fixture(self, sample_prompts):
        """Demonstrate using test data fixtures."""
        # sample_prompts provides common test data
        assert isinstance(sample_prompts, list)
        assert len(sample_prompts) > 0
        assert "Hello, world!" in sample_prompts


# ============================================================================
# Pattern 2: Custom Mock Responses
# ============================================================================


@pytest.mark.asyncio
class TestCustomMockResponses:
    """Examples of creating custom mock responses."""

    async def test_custom_response_map(self, custom_mock_provider):
        """Create MockProvider with custom responses."""
        # Use the factory to create provider with custom responses
        provider = custom_mock_provider({
            "calculate": "The result is 42",
            "greet": "Hello, user!",
            "error": "This is an error message"
        })
        
        # Test each custom response
        calc_response = await provider.generate("calculate")
        assert calc_response.text == "The result is 42"
        
        greet_response = await provider.generate("greet")
        assert greet_response.text == "Hello, user!"

    async def test_response_sequence_pattern(self):
        """Demonstrate response sequences for multi-turn conversations."""
        # Create provider with sequence of responses
        provider = MockProvider(response_sequence=[
            "First response",
            "Second response",
            "Third response"
        ])
        
        # Each call returns next response in sequence
        r1 = await provider.generate("any prompt 1")
        r2 = await provider.generate("any prompt 2")
        r3 = await provider.generate("any prompt 3")
        
        assert r1.text == "First response"
        assert r2.text == "Second response"
        assert r3.text == "Third response"

    async def test_default_response_pattern(self):
        """Demonstrate custom default response."""
        # Create provider with custom default
        provider = MockProvider(
            default_response="This is the default response for any unknown prompt"
        )
        
        # Any prompt returns the default
        r1 = await provider.generate("unknown prompt 1")
        r2 = await provider.generate("unknown prompt 2")
        
        assert r1.text == "This is the default response for any unknown prompt"
        assert r2.text == "This is the default response for any unknown prompt"


# ============================================================================
# Pattern 3: Agent Context Factory
# ============================================================================


class TestAgentContextFactory:
    """Examples of using the agent_context_factory."""

    def test_create_basic_context(self, agent_context_factory):
        """Create agent context with default values."""
        context = agent_context_factory()
        
        assert context.goal == "test goal"
        assert context.inputs == {}
        assert context.turn_count == 0

    def test_create_custom_context(self, agent_context_factory):
        """Create agent context with custom values."""
        context = agent_context_factory(
            goal="Custom goal",
            inputs={"param": "value"},
            metadata={"test": "value"}
        )
        
        assert context.goal == "Custom goal"
        assert context.inputs == {"param": "value"}
        assert context.metadata == {"test": "value"}


# ============================================================================
# Pattern 4: Tool Registry Testing
# ============================================================================


@pytest.mark.asyncio
class TestToolRegistryPattern:
    """Examples of testing with tool registry."""

    async def test_tool_registry_fixture(self, tool_registry):
        """Demonstrate basic tool registry usage."""
        # tool_registry fixture provides empty registry
        assert isinstance(tool_registry, type(tool_registry))
        
        # Can register and test tools
        # (This is a skeleton - actual tool registration would go here)

    async def test_with_test_config(self, test_config, mock_provider):
        """Combine configuration and provider fixtures."""
        # Use test_config for consistent test parameters
        response = await mock_provider.generate(
            "test prompt",
            max_tokens=test_config["max_tokens"],
            temperature=test_config["temperature"]
        )
        
        assert response.tokens_used <= test_config["max_tokens"]


# ============================================================================
# Pattern 5: Parametrized Tests with Fixtures
# ============================================================================


@pytest.mark.asyncio
class TestParametrizedPatterns:
    """Examples of parametrized tests with fixtures."""

    @pytest.mark.parametrize("prompt,expected_keywords", [
        ("Hello, world!", ["Hello", "mock", "greeting"]),
        ("Test prompt", ["deterministic", "test"]),
        ("What is 2+2?", ["2+2", "4"]),
    ])
    async def test_parametrized_with_fixture(
        self,
        mock_provider,
        prompt,
        expected_keywords
    ):
        """Combine parametrize with fixtures."""
        response = await mock_provider.generate(prompt)
        
        # Check that at least one expected keyword is in response
        response_lower = response.text.lower()
        assert any(keyword.lower() in response_lower for keyword in expected_keywords)

    @pytest.mark.parametrize("max_tokens", [10, 50, 100, 500])
    async def test_parametrized_max_tokens(self, mock_provider, max_tokens):
        """Test different configurations with same fixture."""
        response = await mock_provider.generate(
            "Test prompt",
            max_tokens=max_tokens
        )
        
        # Response should respect max_tokens
        assert response.tokens_used <= max_tokens


# ============================================================================
# Pattern 6: Integration Test Patterns (with markers)
# ============================================================================


@pytest.mark.integration
@pytest.mark.asyncio
class TestIntegrationPatterns:
    """Examples of integration test patterns."""

    async def test_end_to_end_with_mock(self, mock_agent):
        """Integration test using mock provider (fast)."""
        # Full end-to-end flow with deterministic mock
        result = await mock_agent.run("Complex multi-step task")
        
        assert result is not None
        # Integration test verifies full flow, not just components


@pytest.mark.ollama
@pytest.mark.integration
@pytest.mark.asyncio
class TestOllamaIntegrationPatterns:
    """Examples of Ollama integration tests (requires Ollama running)."""

    @pytest.mark.skip(reason="Requires Ollama running - example pattern only")
    async def test_ollama_provider_fixture(self, ollama_provider):
        """Demonstrate Ollama integration test."""
        # This test requires Ollama running (marked with @pytest.mark.ollama)
        # Skip in CI with: pytest -m "not ollama"
        
        response = await ollama_provider.generate(
            "Say 'hello'",
            max_tokens=10,
            temperature=0.0
        )
        
        assert response.text is not None
        assert len(response.text) > 0


# ============================================================================
# Pattern 7: Test Organization Best Practices
# ============================================================================


class TestOrganizationPatterns:
    """Examples of test organization best practices."""

    def test_descriptive_names_show_intent(self, mock_provider):
        """
        Test names should clearly describe what is being tested.
        
        Good: test_mock_provider_returns_deterministic_response
        Bad: test_1, test_provider
        """
        pass

    def test_one_assertion_per_logical_concept(self, sample_llm_response):
        """
        Each test should verify one logical concept.
        
        Multiple assertions are OK if they test the same concept.
        """
        # Testing response structure (one concept)
        assert sample_llm_response.text is not None
        assert isinstance(sample_llm_response.text, str)
        assert len(sample_llm_response.text) > 0

    def test_use_fixtures_to_avoid_duplication(self, mock_provider, test_config):
        """
        Use fixtures to avoid duplicating setup code.
        
        Fixtures make tests more maintainable and consistent.
        """
        # No setup needed - fixtures handle it
        assert mock_provider is not None
        assert test_config is not None


# ============================================================================
# Pattern 8: Testing Error Conditions
# ============================================================================


@pytest.mark.asyncio
class TestErrorPatterns:
    """Examples of testing error conditions."""

    async def test_empty_prompt_handling(self, mock_provider):
        """Test provider handles empty prompts gracefully."""
        response = await mock_provider.generate("")
        
        # Should not crash, should return something
        assert isinstance(response, LLMResponse)

    async def test_extremely_long_prompt(self, mock_provider):
        """Test provider handles very long prompts."""
        long_prompt = "test " * 10000
        response = await mock_provider.generate(long_prompt, max_tokens=100)
        
        # Should handle gracefully and respect max_tokens
        assert response.tokens_used <= 100


# ============================================================================
# Summary Documentation
# ============================================================================


"""
Key Takeaways for Test Infrastructure:

1. **Use Shared Fixtures**: Import from conftest.py, don't recreate
2. **Factory Pattern**: Use fixture factories for customization
3. **Deterministic Tests**: MockProvider ensures reproducible results
4. **Mark Slow Tests**: Use @pytest.mark.ollama/@pytest.mark.integration
5. **Parametrize**: Test multiple cases efficiently
6. **Clear Names**: Test names document intent
7. **One Concept**: Each test verifies one logical concept
8. **Test Config**: Use test_config for consistent parameters

Running Tests:
--------------
# All tests
pytest

# Unit tests only (fast)
pytest -m unit

# Skip integration tests
pytest -m "not integration"

# Skip Ollama tests (for CI)
pytest -m "not ollama"

# Run specific pattern examples
pytest tests/unit/test_fixture_patterns.py -v

# With coverage
pytest --cov=src --cov-report=term-missing
"""
