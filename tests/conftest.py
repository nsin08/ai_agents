"""
Shared pytest fixtures and configuration for all tests.

This conftest.py provides:
- Fixture factories to avoid duplication
- Common test providers (MockProvider, OllamaProvider, etc.)
- Reusable test data and helpers
- Consistent test configuration

Usage:
    # In any test file:
    def test_something(mock_provider):
        # Use the mock_provider fixture
        response = await mock_provider.generate("test")
        assert response.text is not None
"""

import pytest
from typing import List, Dict, Any
from src.agent_labs.llm_providers import (
    MockProvider,
    OllamaProvider,
    LLMResponse,
)
from src.agent_labs.orchestrator import Agent, AgentContext
from src.agent_labs.tools import ToolRegistry


# ============================================================================
# Provider Fixtures (Fixture Factory Pattern)
# ============================================================================


@pytest.fixture
def mock_provider():
    """
    Create a MockProvider for deterministic testing.
    
    Returns MockProvider with default responses.
    
    Example:
        def test_agent(mock_provider):
            response = await mock_provider.generate("Hello")
            assert "Mock response" in response.text
    """
    return MockProvider(name="mock")


@pytest.fixture
def custom_mock_provider():
    """
    Factory fixture for creating MockProvider with custom responses.
    
    Returns a function that creates MockProvider with custom response map.
    
    Example:
        def test_custom(custom_mock_provider):
            provider = custom_mock_provider({
                "test": "custom response"
            })
            response = await provider.generate("test")
            assert response.text == "custom response"
    """
    def _create_provider(responses: Dict[str, str] = None, name: str = "mock"):
        # Create provider with custom responses
        return MockProvider(name=name, responses=responses)
    return _create_provider


@pytest.fixture
def ollama_provider():
    """
    Create an OllamaProvider for integration testing.
    
    Requires Ollama running at http://localhost:11434.
    Tests using this fixture should be marked with @pytest.mark.ollama.
    
    Example:
        @pytest.mark.ollama
        async def test_ollama(ollama_provider):
            response = await ollama_provider.generate("test")
            assert response.text is not None
    """
    provider = OllamaProvider(
        base_url="http://localhost:11434",
        model="mistral:7b",
        timeout=120,
    )
    yield provider
    # Cleanup after test
    # Note: OllamaProvider might need close() method


# ============================================================================
# Agent Fixtures
# ============================================================================


@pytest.fixture
def mock_agent(mock_provider):
    """
    Create an Agent with MockProvider for testing.
    
    Example:
        async def test_agent_run(mock_agent):
            result = await mock_agent.run("test prompt")
            assert result is not None
    """
    return Agent(mock_provider)


@pytest.fixture
def agent_context_factory():
    """
    Factory fixture for creating AgentContext instances.
    
    Example:
        def test_context(agent_context_factory):
            context = agent_context_factory(
                goal="test goal",
                inputs={"key": "value"}
            )
            assert context.goal == "test goal"
    """
    def _create_context(
        goal: str = "test goal",
        inputs: Dict[str, Any] = None,
        metadata: dict = None
    ) -> AgentContext:
        return AgentContext(
            goal=goal,
            inputs=inputs or {},
            metadata=metadata or {}
        )
    return _create_context


# ============================================================================
# Tool Fixtures
# ============================================================================


@pytest.fixture
def tool_registry():
    """
    Create an empty ToolRegistry for testing.
    
    Example:
        def test_tool(tool_registry):
            tool_registry.register(MyTool(), "my_tool")
            result = await tool_registry.execute("my_tool", arg="value")
    """
    return ToolRegistry()


# ============================================================================
# Test Data Fixtures
# ============================================================================


@pytest.fixture
def sample_prompts() -> List[str]:
    """
    Provide common test prompts for consistent testing.
    
    Example:
        def test_prompts(sample_prompts, mock_provider):
            for prompt in sample_prompts:
                response = await mock_provider.generate(prompt)
                assert response.text is not None
    """
    return [
        "Hello, world!",
        "What is 2+2?",
        "Test prompt",
        "Simple task",
        "Calculate 10 + 5",
    ]


@pytest.fixture
def sample_llm_response() -> LLMResponse:
    """
    Provide a sample LLMResponse for testing.
    
    Example:
        def test_response_handling(sample_llm_response):
            assert sample_llm_response.tokens_used > 0
    """
    return LLMResponse(
        text="This is a test response",
        tokens_used=5,
        model="mock"
    )


# ============================================================================
# Configuration Fixtures
# ============================================================================


@pytest.fixture
def test_config() -> Dict[str, any]:
    """
    Provide common test configuration.
    
    Example:
        def test_with_config(test_config):
            assert test_config["max_tokens"] == 100
    """
    return {
        "max_tokens": 100,
        "temperature": 0.0,  # Deterministic for tests
        "timeout": 30,
        "max_turns": 5,
    }


# ============================================================================
# Pytest Configuration Hooks
# ============================================================================


def pytest_configure(config):
    """
    Configure pytest with custom markers and settings.
    """
    # Custom markers are already defined in pytest.ini
    # This hook can be used for additional configuration
    pass


def pytest_collection_modifyitems(config, items):
    """
    Modify test collection to add markers based on test location.
    
    Automatically marks tests based on their location:
    - tests/unit/* -> @pytest.mark.unit
    - tests/integration/* -> @pytest.mark.integration
    """
    for item in items:
        # Get the test file path
        test_path = str(item.fspath)
        
        # Auto-mark unit tests
        if "/unit/" in test_path:
            item.add_marker(pytest.mark.unit)
        
        # Auto-mark integration tests
        if "/integration/" in test_path:
            item.add_marker(pytest.mark.integration)
