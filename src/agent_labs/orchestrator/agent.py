"""
Agent orchestrator - implements the agent loop.

Agent Loop: Observe -> Plan -> Act -> Verify -> Refine (or Stop)
"""

from typing import Optional, Callable
import logging

from ..llm_providers import Provider
from .context import AgentContext, VerificationResult
from .states import AgentState, can_transition
from .exceptions import (
    MaxTurnsExceededError,
    StateTransitionError,
    VerificationError,
    PlanningError,
    ActionExecutionError,
)

logger = logging.getLogger(__name__)


class Agent:
    """Agent that uses an LLM to reason, act, and verify progress."""

    def __init__(
        self,
        provider: Provider,
        model: str = "mock",
        verifier: Optional[Callable[[AgentContext, str], VerificationResult]] = None,
        tool_executor: Optional[Callable[[str], str]] = None,
        on_state_change: Optional[Callable[[AgentState, AgentState], None]] = None,
    ) -> None:
        self.provider = provider
        self.model = model
        self.verifier = verifier
        self.tool_executor = tool_executor
        self.on_state_change = on_state_change

    def _transition_state(self, context: AgentContext, new_state: AgentState) -> None:
        """Transition to a new state with validation and logging."""
        old_state = context.current_state

        if not can_transition(old_state, new_state):
            raise StateTransitionError(old_state.value, new_state.value)

        logger.info("State transition: %s -> %s", old_state.value, new_state.value)
        context.current_state = new_state

        if self.on_state_change:
            self.on_state_change(old_state, new_state)

    async def run(
        self,
        goal: str,
        max_turns: int = 5,
        inputs: Optional[dict] = None,
    ) -> str:
        """Run agent to completion."""
        if max_turns <= 0:
            raise MaxTurnsExceededError("max_turns must be positive")

        context = AgentContext(goal=goal, inputs=inputs or {})
        last_result = ""

        for turn in range(max_turns):
            context.turn_count = turn + 1
            logger.info("Starting turn %s/%s", context.turn_count, max_turns)

            if context.current_state != AgentState.OBSERVING:
                self._transition_state(context, AgentState.OBSERVING)
            await self._observe(context)

            self._transition_state(context, AgentState.PLANNING)
            plan = await self._plan(context)

            self._transition_state(context, AgentState.ACTING)
            result = await self._act(context, plan)
            last_result = result

            self._transition_state(context, AgentState.VERIFYING)
            verification = await self._verify(context, result)

            if verification.is_complete:
                self._transition_state(context, AgentState.DONE)
                logger.info(
                    "Goal achieved in %s turns: %s",
                    context.turn_count,
                    verification.reason,
                )
                return result

            self._transition_state(context, AgentState.REFINING)
            await self._refine(context, result, verification.feedback)

        self._transition_state(context, AgentState.FAILED)
        logger.warning("Max turns (%s) reached without completing goal", max_turns)
        return last_result or "Max turns reached without completing goal"

    async def _observe(self, context: AgentContext) -> None:
        """Observe current state."""
        context.add_history("system", f"Goal: {context.goal} (Turn {context.turn_count})")
        logger.debug("Observed goal: %s", context.goal)

    async def _plan(self, context: AgentContext) -> str:
        """Plan next action using the LLM."""
        try:
            history_str = context.format_history(n=3)
            prompt = (
                f"Goal: {context.goal}\n\n"
                f"Recent history:\n{history_str}\n\n"
                "What should I do next to achieve this goal? Keep answer concise."
            )
            response = await self.provider.generate(prompt, max_tokens=200, temperature=0.7)
            plan = response.text
        except Exception as exc:
            raise PlanningError(str(exc)) from exc

        context.add_history("assistant", plan)
        logger.debug("Generated plan: %s", plan)
        return plan

    async def _act(self, context: AgentContext, plan: str) -> str:
        """Execute the plan."""
        try:
            if self.tool_executor:
                result = self.tool_executor(plan)
            else:
                # Default behavior: return the plan as the execution result
                # For web chat use cases, integrate via tool_executor or custom _act override
                result = f"Executed: {plan}"
        except Exception as exc:
            raise ActionExecutionError(str(exc)) from exc

        context.add_history("system", result)
        logger.debug("Action result: %s", result)
        return result

    async def _verify(self, context: AgentContext, result: str) -> VerificationResult:
        """Verify if the result achieves the goal."""
        try:
            if self.verifier:
                verification = self.verifier(context, result)
            else:
                verification = await self._default_verify(context, result)
        except Exception as exc:
            raise VerificationError(str(exc)) from exc

        status = "COMPLETE" if verification.is_complete else "INCOMPLETE"
        context.add_history("system", f"Verification: {status} - {verification.reason}")
        logger.info("Verification: %s (confidence: %s)", status, verification.confidence)
        return verification

    async def _default_verify(self, context: AgentContext, result: str) -> VerificationResult:
        """Default verifier using LLM to determine completion."""
        prompt = (
            f"Goal: {context.goal}\n\n"
            f"Result: {result}\n\n"
            "Does this result achieve the goal? Answer with:\n"
            "- \"YES\" if the goal is fully achieved\n"
            "- \"NO\" if more work is needed\n"
            "- Include a brief reason\n\n"
            "Format: YES/NO | reason"
        )

        response = await self.provider.generate(prompt, max_tokens=100)
        answer = response.text.strip()
        upper = answer.upper()

        is_complete = upper.startswith("YES")
        reason = answer
        if "|" in answer:
            reason = answer.split("|", 1)[1].strip()

        feedback = "" if is_complete else "Continue working towards goal"

        return VerificationResult(
            is_complete=is_complete,
            reason=reason,
            feedback=feedback,
        )

    async def _refine(self, context: AgentContext, result: str, feedback: str) -> None:
        """Refine approach for next iteration."""
        message = f"Turn {context.turn_count} incomplete. {feedback or 'Refining for next turn...'}"
        context.add_history("system", message)
        logger.debug("Refining: %s", message)
