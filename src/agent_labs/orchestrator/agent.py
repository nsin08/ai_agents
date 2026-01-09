"""
Agent orchestrator - implements the agent loop.

Agent Loop: Observe → Plan → Act → Verify → Refine (or Stop)

The orchestrator manages the main execution loop where the agent:
1. Observes the current state/goal
2. Plans the next action using the LLM
3. Acts on the plan (would call tools in real implementation)
4. Verifies the result achieves the goal
5. Either stops (goal met) or refines and loops
"""

from typing import Optional, Callable, Any
import logging

from ..llm_providers import Provider
from .context import AgentContext, VerificationResult
from .states import AgentState, can_transition
from .exceptions import (
    MaxTurnsExceededError,
    StateTransitionError,
    VerificationError,
)

logger = logging.getLogger(__name__)


class Agent:
    """
    Agent that uses LLM to reason and act.

    Implements observe → plan → act → verify → refine loop.
    The agent takes a goal and iteratively works towards it by:
    - Planning actions using the LLM
    - Executing actions (mocked in this version)
    - Verifying results
    - Refining approach based on feedback
    """

    def __init__(
        self,
        provider: Provider,
        model: str = "mock",
        verifier: Optional[Callable[[AgentContext, str], VerificationResult]] = None,
        tool_executor: Optional[Callable[[str], str]] = None,
        on_state_change: Optional[Callable[[AgentState, AgentState], None]] = None,
    ):
        """
        Initialize agent with LLM provider and optional hooks.

        Args:
            provider: LLM provider to use for reasoning
            model: Model name for logging/identification
            verifier: Optional custom verification function that takes (context, result) 
                     and returns VerificationResult. If None, uses default heuristic.
            tool_executor: Optional function to execute actions. If None, uses mock executor.
            on_state_change: Optional callback when state transitions occur

        Example:
            >>> from agent_labs.llm_providers import MockProvider
            >>> provider = MockProvider()
            >>> 
            >>> # With custom verifier
            >>> def my_verifier(ctx, result):
            >>>     return VerificationResult(
            >>>         is_complete="answer" in result.lower(),
            >>>         reason="Found answer in result"
            >>>     )
            >>> agent = Agent(provider, verifier=my_verifier)
        """
        self.provider = provider
        self.model = model
        self.verifier = verifier
        self.tool_executor = tool_executor
        self.on_state_change = on_state_change

    def _transition_state(self, context: AgentContext, new_state: AgentState) -> None:
        """
        Transition to a new state with validation and logging.
        
        Args:
            context: Agent context
            new_state: Target state
            
        Raises:
            StateTransitionError: If transition is invalid
        """
        old_state = context.current_state
        
        if not can_transition(old_state, new_state):
            raise StateTransitionError(old_state.value, new_state.value)
        
        logger.info(f"State transition: {old_state.value} -> {new_state.value}")
        context.current_state = new_state
        
        # Call callback if provided
        if self.on_state_change:
            self.on_state_change(old_state, new_state)

    async def run(
        self,
        goal: str,
        max_turns: int = 5,
        inputs: Optional[dict] = None,
    ) -> str:
        """
        Run agent to completion.

        The agent loops through observe → plan → act → verify → refine
        until either the goal is achieved or max_turns is reached.

        Args:
            goal: What the agent should accomplish
            max_turns: Maximum iterations before stopping
            inputs: Optional additional inputs for the agent

        Returns:
            Final result/answer achieved by the agent

        Raises:
            MaxTurnsExceededError: If max turns reached without completing goal

        Example:
            >>> result = await agent.run("What is 2+2?", max_turns=3)
            >>> print(result)  # "The answer is 4"
        """
        context = AgentContext(goal=goal, inputs=inputs or {})
        last_result = ""

        for turn in range(max_turns):
            context.turn_count = turn + 1
            logger.info(f"Starting turn {context.turn_count}/{max_turns}")

            # Step 1: Observe current state
            # Only transition if not already in OBSERVING state (first turn is already OBSERVING)
            if context.current_state != AgentState.OBSERVING:
                self._transition_state(context, AgentState.OBSERVING)
            await self._observe(context)

            # Step 2: Plan next action using LLM
            self._transition_state(context, AgentState.PLANNING)
            plan = await self._plan(context)

            # Step 3: Execute the plan (would call tools here)
            self._transition_state(context, AgentState.ACTING)
            result = await self._act(context, plan)
            last_result = result

            # Step 4: Verify result achieves goal
            self._transition_state(context, AgentState.VERIFYING)
            verification = await self._verify(context, result)

            if verification.is_complete:
                self._transition_state(context, AgentState.DONE)
                logger.info(f"Goal achieved in {context.turn_count} turns: {verification.reason}")
                return result

            # Step 5: Refine approach for next iteration
            self._transition_state(context, AgentState.REFINING)
            await self._refine(context, result, verification.feedback)

        # If max turns reached without completion
        self._transition_state(context, AgentState.FAILED)
        logger.warning(f"Max turns ({max_turns}) reached without completing goal")
        return last_result or "Max turns reached without completing goal"

    async def _observe(self, context: AgentContext) -> None:
        """
        Observe current state.

        In a real implementation, would read from sensors, APIs, databases, etc.
        Currently just records goal in history.

        Args:
            context: Agent execution context
        """
        context.add_history("system", f"Goal: {context.goal} (Turn {context.turn_count})")
        logger.debug(f"Observed goal: {context.goal}")

    async def _plan(self, context: AgentContext) -> str:
        """
        Plan next action using the LLM.

        Asks the LLM: "Given the goal and history, what should I do next?"

        Args:
            context: Agent execution context

        Returns:
            Plan/action described by LLM
        """
        history_str = context.format_history(n=3)
        prompt = f"""Goal: {context.goal}

Recent history:
{history_str}

What should I do next to achieve this goal?"""

        response = await self.provider.generate(prompt)
        plan = response.text

        # Record in history
        context.add_history("assistant", plan)
        logger.debug(f"Generated plan: {plan}")

        return plan

    async def _act(self, context: AgentContext, plan: str) -> str:
        """
        Execute the plan.

        In a real implementation, would call actual tools/APIs here.
        For now, returns a mock result that says what was done.

        Args:
            context: Agent execution context
            plan: The planned action from LLM

        Returns:
            Result of executing the plan
        """
        # Use custom tool executor if provided
        if self.tool_executor:
            result = self.tool_executor(plan)
        else:
            # Default mock implementation
            result = f"Executed: {plan}"
        
        context.add_history("system", result)
        logger.debug(f"Action result: {result}")
        return result

    async def _verify(self, context: AgentContext, result: str) -> VerificationResult:
        """
        Verify if the result achieves the goal.

        Uses custom verifier if provided, otherwise uses default heuristic.
        The default heuristic uses the LLM to check if the goal is met.

        Args:
            context: Agent execution context
            result: Result from executing the plan

        Returns:
            VerificationResult with completion status and feedback
        """
        # Use custom verifier if provided
        if self.verifier:
            verification = self.verifier(context, result)
        else:
            # Default: Use LLM to verify if goal is met
            prompt = f"""Goal: {context.goal}

Result: {result}

Does this result achieve the goal? Answer with:
- "YES" if the goal is fully achieved
- "NO" if more work is needed
- Include a brief reason

Format: YES/NO | reason"""

            response = await self.provider.generate(prompt, max_tokens=100)
            answer = response.text.strip().upper()
            
            # Parse response
            is_complete = answer.startswith("YES")
            reason = answer if "|" not in answer else answer.split("|", 1)[1].strip()
            
            verification = VerificationResult(
                is_complete=is_complete,
                reason=reason,
                feedback="" if is_complete else "Continue working towards goal"
            )

        # Log result
        status = "COMPLETE" if verification.is_complete else "INCOMPLETE"
        context.add_history("system", f"Verification: {status} - {verification.reason}")
        logger.info(f"Verification: {status} (confidence: {verification.confidence})")

        return verification

    async def _refine(self, context: AgentContext, result: str, feedback: str) -> None:
        """
        Learn and refine approach for next iteration.

        In a real implementation, would analyze failures and adjust strategy.
        Currently just records that we're continuing.

        Args:
            context: Agent execution context
            result: Result from previous attempt
            feedback: Feedback from verification step
        """
        message = f"Turn {context.turn_count} incomplete. {feedback or 'Refining for next turn...'}"
        context.add_history("system", message)
        logger.debug(f"Refining: {message}")
