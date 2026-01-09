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

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Tuple

from agent_labs.llm_providers import Provider, LLMResponse


class AgentState(Enum):
    """Agent execution states in the orchestration loop."""

    OBSERVING = "observing"  # Reading input/goal
    PLANNING = "planning"  # Using LLM to decide next action
    ACTING = "acting"  # Executing the planned action
    VERIFYING = "verifying"  # Checking if result achieves goal
    REFINING = "refining"  # Learning from result for next iteration
    DONE = "done"  # Task complete


@dataclass
class AgentContext:
    """Context and state for an agent execution run."""

    goal: str
    """What the agent is trying to accomplish."""

    turn_count: int = 0
    """How many iterations (turns) the agent has taken."""

    history: List[Tuple[str, str]] = field(default_factory=list)
    """Conversation history: list of (role, message) tuples."""

    current_state: AgentState = AgentState.OBSERVING
    """Current state in the agent loop."""


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

    def __init__(self, provider: Provider, model: str = "mock"):
        """
        Initialize agent with LLM provider.

        Args:
            provider: LLM provider to use for reasoning
            model: Model name for logging/identification

        Example:
            >>> from agent_labs.llm_providers import MockProvider
            >>> provider = MockProvider()
            >>> agent = Agent(provider)
        """
        self.provider = provider
        self.model = model

    async def run(
        self,
        goal: str,
        max_turns: int = 5,
    ) -> str:
        """
        Run agent to completion.

        The agent loops through observe → plan → act → verify → refine
        until either the goal is achieved or max_turns is reached.

        Args:
            goal: What the agent should accomplish
            max_turns: Maximum iterations before stopping

        Returns:
            Final result/answer achieved by the agent

        Example:
            >>> result = await agent.run("What is 2+2?", max_turns=3)
            >>> print(result)  # "The answer is 4"
        """
        context = AgentContext(goal=goal)

        for turn in range(max_turns):
            context.turn_count = turn + 1

            # Step 1: Observe current state
            context.current_state = AgentState.OBSERVING
            await self._observe(context)

            # Step 2: Plan next action using LLM
            context.current_state = AgentState.PLANNING
            plan = await self._plan(context)

            # Step 3: Execute the plan (would call tools here)
            context.current_state = AgentState.ACTING
            result = await self._act(context, plan)

            # Step 4: Verify result achieves goal
            context.current_state = AgentState.VERIFYING
            is_complete = await self._verify(context, result)

            if is_complete:
                context.current_state = AgentState.DONE
                return result

            # Step 5: Refine approach for next iteration
            context.current_state = AgentState.REFINING
            await self._refine(context, result)

        # If max turns reached without completion
        context.current_state = AgentState.DONE
        return "Max turns reached without completing goal"

    async def _observe(self, context: AgentContext) -> None:
        """
        Observe current state.

        In a real implementation, would read from sensors, APIs, databases, etc.
        Currently just records goal in history.

        Args:
            context: Agent execution context
        """
        context.history.append(("system", f"Goal: {context.goal}"))

    async def _plan(self, context: AgentContext) -> str:
        """
        Plan next action using the LLM.

        Asks the LLM: "Given the goal and history, what should I do next?"

        Args:
            context: Agent execution context

        Returns:
            Plan/action described by LLM
        """
        history_str = "\n".join(
            [f"{role}: {msg}" for role, msg in context.history[-3:]]
        )
        prompt = f"""Goal: {context.goal}

Recent history:
{history_str}

What should I do next?"""

        response = await self.provider.generate(prompt)
        plan = response.text

        # Record in history
        context.history.append(("assistant", plan))

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
        result = f"Executed: {plan}"
        context.history.append(("system", result))
        return result

    async def _verify(self, context: AgentContext, result: str) -> bool:
        """
        Verify if the result achieves the goal.

        Simple heuristic: if we got a non-empty result, consider it a success.
        A real implementation would check if result actually solves the goal.

        Args:
            context: Agent execution context
            result: Result from executing the plan

        Returns:
            True if goal is achieved, False otherwise
        """
        # Simple check: did we get a non-empty result?
        is_complete = len(result) > 0

        status = "SUCCESS" if is_complete else "FAILED"
        context.history.append(("system", f"Verification: {status}"))

        return is_complete

    async def _refine(self, context: AgentContext, result: str) -> None:
        """
        Learn and refine approach for next iteration.

        In a real implementation, would analyze failures and adjust strategy.
        Currently just records that we're continuing.

        Args:
            context: Agent execution context
            result: Result from previous attempt
        """
        context.history.append(
            ("system", f"Turn {context.turn_count} complete. Refining for next turn...")
        )
