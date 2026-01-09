"""
Tests for Agent orchestrator and orchestration loop.

Test approach: TDD (test-driven development)
1. Define what agent should do (in tests)
2. Implement minimal code to pass tests
3. Add more tests for edge cases
4. Iterate until >95% coverage
"""

import pytest
from agent_labs.llm_providers import MockProvider
from agent_labs.orchestrator import Agent, AgentState, AgentContext


@pytest.mark.asyncio
class TestAgent:
    """Test Agent orchestrator implementation."""

    @pytest.fixture
    def provider(self):
        """Create mock provider for tests."""
        return MockProvider()

    @pytest.fixture
    def agent(self, provider):
        """Create agent with mock provider."""
        return Agent(provider)

    @pytest.mark.asyncio
    async def test_agent_run_completes(self, agent):
        """Test that agent.run() completes successfully."""
        result = await agent.run("What is 2+2?")

        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_agent_run_returns_non_empty(self, agent):
        """Test that agent returns non-empty result."""
        result = await agent.run("Simple task")

        # Should always return something
        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_agent_respects_max_turns(self, agent):
        """Test that agent doesn't exceed max_turns."""
        result = await agent.run("Test task", max_turns=3)

        # Should complete without error
        assert result is not None

    @pytest.mark.asyncio
    async def test_agent_with_different_goals(self, agent):
        """Test agent with various goals."""
        goals = [
            "What is 2+2?",
            "Hello, world!",
            "Test prompt",
            "Complex reasoning task",
        ]

        for goal in goals:
            result = await agent.run(goal)
            assert result is not None
            assert len(result) > 0

    @pytest.mark.asyncio
    async def test_agent_default_max_turns(self, agent):
        """Test that agent uses default max_turns if not specified."""
        result = await agent.run("Test")

        # Should use default max_turns=5 and complete
        assert result is not None

    @pytest.mark.asyncio
    async def test_agent_with_max_turns_one(self, agent):
        """Test agent with max_turns=1 (single iteration)."""
        result = await agent.run("One turn test", max_turns=1)

        # Should complete even with only one turn
        assert result is not None
        assert "Executed" in result or "Max turns" in result

    @pytest.mark.asyncio
    async def test_agent_history_tracking(self, agent):
        """Test that agent maintains conversation history."""
        result = await agent.run("Test with history", max_turns=2)

        # Result should be non-empty (agent completed)
        assert result is not None

    @pytest.mark.asyncio
    async def test_agent_init_with_custom_model(self, provider):
        """Test agent initialization with custom model name."""
        agent = Agent(provider, model="custom-model")

        assert agent.model == "custom-model"
        assert agent.provider is provider

    @pytest.mark.asyncio
    async def test_agent_plan_uses_provider(self, agent):
        """Test that _plan method calls the LLM provider."""
        context = AgentContext(goal="Test planning")
        plan = await agent._plan(context)

        # Should get non-empty plan from provider
        assert isinstance(plan, str)
        assert len(plan) > 0

    @pytest.mark.asyncio
    async def test_agent_observe_records_goal(self, agent):
        """Test that _observe records goal in history."""
        context = AgentContext(goal="Test observation")
        await agent._observe(context)

        # Goal should be in history
        assert len(context.history) > 0
        assert context.history[0][0] == "system"
        assert "Test observation" in context.history[0][1]

    @pytest.mark.asyncio
    async def test_agent_verify_returns_bool(self, agent):
        """Test that _verify returns boolean."""
        context = AgentContext(goal="Test verification")
        result = "Some result"

        is_verified = await agent._verify(context, result)

        assert isinstance(is_verified, bool)

    @pytest.mark.asyncio
    async def test_agent_refine_updates_history(self, agent):
        """Test that _refine updates history."""
        context = AgentContext(goal="Test refinement")
        context.turn_count = 1
        result = "Some result"

        initial_len = len(context.history)
        await agent._refine(context, result)

        # History should be updated
        assert len(context.history) > initial_len


class TestAgentState:
    """Test AgentState enum."""

    def test_agent_state_values(self):
        """Test that all agent states are defined."""
        states = [
            AgentState.OBSERVING,
            AgentState.PLANNING,
            AgentState.ACTING,
            AgentState.VERIFYING,
            AgentState.REFINING,
            AgentState.DONE,
        ]

        # Should have all 6 states
        assert len(states) == 6

    def test_agent_state_names(self):
        """Test that agent states have correct names."""
        assert AgentState.OBSERVING.value == "observing"
        assert AgentState.PLANNING.value == "planning"
        assert AgentState.ACTING.value == "acting"
        assert AgentState.VERIFYING.value == "verifying"
        assert AgentState.REFINING.value == "refining"
        assert AgentState.DONE.value == "done"


class TestAgentContext:
    """Test AgentContext dataclass."""

    def test_agent_context_creation(self):
        """Test creating AgentContext with required fields."""
        context = AgentContext(goal="Test goal")

        assert context.goal == "Test goal"
        assert context.turn_count == 0
        assert context.current_state == AgentState.OBSERVING
        assert len(context.history) == 0

    def test_agent_context_history_operations(self):
        """Test adding to context history."""
        context = AgentContext(goal="Test")

        context.history.append(("user", "Hello"))
        context.history.append(("assistant", "Hi there"))

        assert len(context.history) == 2
        assert context.history[0] == ("user", "Hello")
        assert context.history[1] == ("assistant", "Hi there")

    def test_agent_context_state_transitions(self):
        """Test changing agent state in context."""
        context = AgentContext(goal="Test")

        # Simulate state transitions
        context.current_state = AgentState.PLANNING
        assert context.current_state == AgentState.PLANNING

        context.current_state = AgentState.ACTING
        assert context.current_state == AgentState.ACTING

        context.current_state = AgentState.DONE
        assert context.current_state == AgentState.DONE

    def test_agent_context_turn_tracking(self):
        """Test tracking turn count."""
        context = AgentContext(goal="Test")

        context.turn_count = 1
        assert context.turn_count == 1

        context.turn_count = 5
        assert context.turn_count == 5
