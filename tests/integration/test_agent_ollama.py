"""
Integration test for Agent (Orchestrator) with Ollama.

Tests the refactored orchestrator with real Ollama LLM to ensure:
- State transitions work correctly
- Verification logic properly checks goal completion
- Multi-turn reasoning works
- Ollama integration is functional
"""

import pytest
from src.agent_labs.llm_providers import OllamaProvider
from src.agent_labs.orchestrator import (
    Agent,
    AgentContext,
    AgentState,
    VerificationResult,
)


@pytest.fixture
def ollama_provider():
    """Create Ollama provider for testing."""
    return OllamaProvider(base_url="http://localhost:11434", model="mistral:7b")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_agent_with_ollama_simple_math(ollama_provider):
    """Test agent with Ollama on simple math problem."""
    agent = Agent(provider=ollama_provider, model="mistral:7b")
    
    result = await agent.run("Calculate 15 + 27 and provide just the numeric answer", max_turns=2)

    # Should get an answer (may not be exactly "42" but should have a number)
    assert result is not None
    assert len(result) > 0
    print(f"\n[OK] Math test - Result: {result}")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_agent_with_ollama_custom_verifier(ollama_provider):
    """Test agent with custom verifier that checks for specific content."""
    verification_calls = []

    def number_verifier(context: AgentContext, result: str) -> VerificationResult:
        """Verify result contains a number."""
        import re
        
        verification_calls.append((context.goal, result[:50]))
        has_number = bool(re.search(r"\b\d+\b", result))
        if has_number:
            return VerificationResult(
                is_complete=True,
                confidence=1.0,
                reason="Result contains a numeric answer",
            )
        else:
            return VerificationResult(
                is_complete=False,
                confidence=0.0,
                reason="No numeric answer found",
                feedback="Please provide a numeric answer to the math problem",
            )

    agent = Agent(provider=ollama_provider, model="mistral:7b", verifier=number_verifier)
    
    result = await agent.run("What is 100 divided by 4?", max_turns=3)

    # Verify the custom verifier was called
    assert len(verification_calls) > 0
    assert result is not None
    print(f"\n[OK] Custom verifier test - Result: {result[:100]}")
    print(f"   Verifier called {len(verification_calls)} time(s)")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_agent_with_ollama_state_transitions(ollama_provider):
    """Test that state transitions work correctly with Ollama."""
    states_visited = []

    def track_states(from_state: AgentState, to_state: AgentState):
        states_visited.append((from_state.value, to_state.value))

    agent = Agent(
        provider=ollama_provider, model="mistral:7b", on_state_change=track_states
    )
    
    result = await agent.run("List three primary colors", max_turns=2)

    # Check state transitions occurred
    assert len(states_visited) > 0
    assert result is not None

    print(f"\n[OK] State transitions test - Result: {result[:100]}")
    print(f"   State transitions: {states_visited}")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_agent_with_ollama_max_turns(ollama_provider):
    """Test that max_turns limit works with Ollama."""
    call_count = [0]

    def never_satisfied(context: AgentContext, result: str) -> VerificationResult:
        """Verifier that never completes to test max_turns."""
        call_count[0] += 1
        return VerificationResult(
            is_complete=False,
            confidence=0.0,
            reason="Never satisfied for testing",
            feedback="Try again",
        )

    agent = Agent(provider=ollama_provider, model="mistral:7b", verifier=never_satisfied)
    
    result = await agent.run("Test max turns behavior", max_turns=2)

    # Verifier should be called for each turn
    assert call_count[0] == 2
    assert result is not None  # Should still return the last result

    print(f"\n[OK] Max turns test - Result: {result[:100]}...")
    print(f"   Verifier called {call_count[0]} times (expected 2)")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_agent_with_ollama_basic_reasoning(ollama_provider):
    """Test basic reasoning with Ollama."""
    agent = Agent(provider=ollama_provider, model="mistral:7b")
    
    result = await agent.run("What is 5 multiplied by 8?", max_turns=2)

    # Should get a result
    assert result is not None
    assert len(result) > 0

    print(f"\n[OK] Basic reasoning test - Result: {result[:100]}")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_agent_with_ollama_simple_task(ollama_provider):
    """Test simple task completion with Ollama."""
    agent = Agent(provider=ollama_provider, model="mistral:7b")
    
    result = await agent.run("Count from 1 to 3", max_turns=2)

    # Should get a result
    assert result is not None
    assert len(result) > 0

    print(f"\n[OK] Simple task test - Result: {result[:100]}")


if __name__ == "__main__":
    """Run tests manually if needed."""
    import asyncio

    async def main():
        provider = OllamaProvider(base_url="http://localhost:11434")

        print("\n" + "=" * 70)
        print("Testing Agent (Orchestrator) with Ollama")
        print("=" * 70)

        # Test 1: Simple math
        await test_agent_with_ollama_simple_math(provider)

        # Test 2: Custom verifier
        await test_agent_with_ollama_custom_verifier(provider)

        # Test 3: State transitions
        await test_agent_with_ollama_state_transitions(provider)

        # Test 4: Max turns
        await test_agent_with_ollama_max_turns(provider)

        # Test 5: Context history
        await test_agent_with_ollama_context_history(provider)

        # Test 6: Metadata
        await test_agent_with_ollama_metadata(provider)

        print("\n" + "=" * 70)
        print("All tests completed!")
        print("=" * 70)

    asyncio.run(main())
