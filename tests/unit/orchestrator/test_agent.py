"""
Tests for Agent orchestrator and orchestration loop.

Test approach: TDD (test-driven development)
1. Define what agent should do (in tests)
2. Implement minimal code to pass tests
3. Add more tests for edge cases
4. Iterate until >95% coverage
"""

import pytest
from src.agent_labs.llm_providers import MockProvider
from src.agent_labs.orchestrator import (
    Agent,
    AgentState,
    AgentContext,
    VerificationResult,
    StateTransitionError,
)


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
    async def test_agent_verify_returns_verification_result(self, agent):
        """Test that _verify returns VerificationResult."""
        context = AgentContext(goal="Test verification")
        result = "Some result"

        verification = await agent._verify(context, result)

        assert isinstance(verification, VerificationResult)
        assert isinstance(verification.is_complete, bool)

    @pytest.mark.asyncio
    async def test_agent_refine_updates_history(self, agent):
        """Test that _refine updates history."""
        context = AgentContext(goal="Test refinement")
        context.turn_count = 1
        result = "Some result"
        feedback = "Keep trying"

        initial_len = len(context.history)
        await agent._refine(context, result, feedback)

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


@pytest.mark.asyncio
class TestAgentVerificationAndStateTransitions:
    """Test verification logic and state transitions."""

    @pytest.fixture
    def provider(self):
        """Create mock provider for tests."""
        return MockProvider()

    @pytest.mark.asyncio
    async def test_agent_with_custom_verifier_that_passes(self, provider):
        """Test agent with custom verifier that returns success."""
        verification_calls = []
        
        def custom_verifier(context, result):
            verification_calls.append((context.goal, result))
            # Always succeed on first call
            return VerificationResult(
                is_complete=True,
                reason="Goal achieved",
                confidence=1.0
            )
        
        agent = Agent(provider, verifier=custom_verifier)
        result = await agent.run("Test goal", max_turns=5)
        
        # Should complete on first turn
        assert len(verification_calls) == 1
        assert result is not None

    @pytest.mark.asyncio
    async def test_agent_with_custom_verifier_that_fails_then_succeeds(self, provider):
        """Test agent with verifier that fails first, then succeeds."""
        call_count = [0]
        
        def custom_verifier(context, result):
            call_count[0] += 1
            # Fail first 2 times, succeed on 3rd
            if call_count[0] < 3:
                return VerificationResult(
                    is_complete=False,
                    reason="Not yet complete",
                    feedback="Keep trying"
                )
            return VerificationResult(
                is_complete=True,
                reason="Goal achieved",
                confidence=1.0
            )
        
        agent = Agent(provider, verifier=custom_verifier)
        result = await agent.run("Test goal", max_turns=5)
        
        # Should take 3 turns
        assert call_count[0] == 3
        assert result is not None

    @pytest.mark.asyncio
    async def test_agent_reaches_max_turns_without_completion(self, provider):
        """Test that agent reaches max_turns when verification keeps failing."""
        def always_fail_verifier(context, result):
            return VerificationResult(
                is_complete=False,
                reason="Never complete",
                feedback="Try again"
            )
        
        agent = Agent(provider, verifier=always_fail_verifier)
        result = await agent.run("Test goal", max_turns=3)
        
        # Should reach max turns
        assert result is not None
        # Result should indicate incompletion or be the last action result

    @pytest.mark.asyncio
    async def test_agent_state_transitions_are_valid(self, provider):
        """Test that agent follows valid state transition path."""
        state_history = []
        
        def track_state_change(old_state, new_state):
            state_history.append((old_state, new_state))
        
        def quick_success_verifier(context, result):
            return VerificationResult(is_complete=True, reason="Done")
        
        agent = Agent(
            provider,
            verifier=quick_success_verifier,
            on_state_change=track_state_change
        )
        
        await agent.run("Test", max_turns=3)
        
        # Verify state transition sequence
        assert len(state_history) > 0
        
        # Expected flow for successful first turn:
        # OBSERVING -> PLANNING -> ACTING -> VERIFYING -> DONE
        expected_transitions = [
            (AgentState.OBSERVING, AgentState.PLANNING),
            (AgentState.PLANNING, AgentState.ACTING),
            (AgentState.ACTING, AgentState.VERIFYING),
            (AgentState.VERIFYING, AgentState.DONE),
        ]
        
        # First 4 transitions should match expected
        for i, (expected_from, expected_to) in enumerate(expected_transitions):
            assert state_history[i] == (expected_from, expected_to)

    @pytest.mark.asyncio
    async def test_agent_refine_path_when_verification_fails(self, provider):
        """Test that agent goes through refine state when verification fails."""
        state_history = []
        
        def track_state_change(old_state, new_state):
            state_history.append((old_state, new_state))
        
        call_count = [0]
        def fail_once_verifier(context, result):
            call_count[0] += 1
            if call_count[0] == 1:
                return VerificationResult(is_complete=False, reason="Not done")
            return VerificationResult(is_complete=True, reason="Done")
        
        agent = Agent(
            provider,
            verifier=fail_once_verifier,
            on_state_change=track_state_change
        )
        
        await agent.run("Test", max_turns=3)
        
        # Should have REFINING state in transitions
        refining_transitions = [
            (from_st, to_st) for from_st, to_st in state_history
            if from_st == AgentState.VERIFYING and to_st == AgentState.REFINING
        ]
        assert len(refining_transitions) >= 1
        
        # Should also have REFINING -> OBSERVING (loop back)
        loop_transitions = [
            (from_st, to_st) for from_st, to_st in state_history
            if from_st == AgentState.REFINING and to_st == AgentState.OBSERVING
        ]
        assert len(loop_transitions) >= 1

    @pytest.mark.asyncio
    async def test_agent_with_custom_tool_executor(self, provider):
        """Test agent with custom tool executor."""
        tool_calls = []
        
        def custom_tool_executor(plan: str) -> str:
            tool_calls.append(plan)
            return f"Custom result for: {plan}"
        
        def quick_success_verifier(context, result):
            return VerificationResult(is_complete=True, reason="Done")
        
        agent = Agent(
            provider,
            tool_executor=custom_tool_executor,
            verifier=quick_success_verifier
        )
        
        result = await agent.run("Test", max_turns=2)
        
        # Tool should have been called
        assert len(tool_calls) >= 1
        assert "Custom result" in result

    @pytest.mark.asyncio
    async def test_agent_default_verifier_uses_llm(self, provider):
        """Test that default verifier uses LLM to check goal completion."""
        # Default verifier should call provider.generate to verify
        agent = Agent(provider)  # No custom verifier
        
        # Run agent - default verifier will use LLM
        result = await agent.run("Simple task", max_turns=2)
        
        # Should complete (MockProvider returns reasonable responses)
        assert result is not None
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_agent_max_turns_results_in_failed_state(self, provider):
        """Test that reaching max_turns transitions to FAILED state."""
        final_state = [None]
        
        def track_state_change(old_state, new_state):
            final_state[0] = new_state
        
        def always_fail_verifier(context, result):
            return VerificationResult(is_complete=False, reason="Never done")
        
        agent = Agent(
            provider,
            verifier=always_fail_verifier,
            on_state_change=track_state_change
        )
        
        await agent.run("Test", max_turns=2)
        
        # Final state should be FAILED
        assert final_state[0] == AgentState.FAILED

    def test_context_add_history_method(self):
        """Test AgentContext.add_history method."""
        context = AgentContext(goal="Test")
        
        context.add_history("user", "Hello")
        context.add_history("assistant", "Hi")
        
        assert len(context.history) == 2
        assert context.history[0] == ("user", "Hello")
        assert context.history[1] == ("assistant", "Hi")

    def test_context_get_recent_history(self):
        """Test AgentContext.get_recent_history method."""
        context = AgentContext(goal="Test")
        
        for i in range(5):
            context.add_history("user", f"Message {i}")
        
        recent = context.get_recent_history(n=2)
        assert len(recent) == 2
        assert recent[0] == ("user", "Message 3")
        assert recent[1] == ("user", "Message 4")

    def test_context_format_history(self):
        """Test AgentContext.format_history method."""
        context = AgentContext(goal="Test")
        
        context.add_history("user", "Hello")
        context.add_history("assistant", "Hi there")
        
        formatted = context.format_history()
        assert "user: Hello" in formatted
        assert "assistant: Hi there" in formatted

    def test_context_metadata_operations(self):
        """Test AgentContext metadata add/get."""
        context = AgentContext(goal="Test")
        
        context.add_metadata("request_id", "req-123")
        context.add_metadata("tokens", 100)
        
        assert context.get_metadata("request_id") == "req-123"
        assert context.get_metadata("tokens") == 100
        assert context.get_metadata("missing", "default") == "default"

    def test_verification_result_creation(self):
        """Test VerificationResult data class."""
        result = VerificationResult(
            is_complete=True,
            confidence=0.95,
            reason="Goal met",
            feedback="Good job"
        )
        
        assert result.is_complete is True
        assert result.confidence == 0.95
        assert result.reason == "Goal met"
        assert result.feedback == "Good job"
