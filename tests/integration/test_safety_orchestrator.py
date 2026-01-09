"""
Integration tests for safety guardrails with orchestrator usage.
"""

import pytest

from src.agent_labs.safety import (
    SafetyChecker,
    TokenLimitGuardrail,
    OutputFilterGuardrail,
    SafetyViolation,
)
from src.agent_labs.orchestrator import Agent
from src.agent_labs.llm_providers import MockProvider


@pytest.mark.asyncio
async def test_safety_checker_blocks_input_before_agent():
    checker = SafetyChecker([TokenLimitGuardrail(max_tokens=2)])
    agent = Agent(provider=MockProvider())

    with pytest.raises(SafetyViolation):
        checker.check_input("one two three")

    result = await agent.run("ok", max_turns=1)
    assert result is not None


@pytest.mark.asyncio
async def test_safety_checker_sanitizes_agent_output():
    checker = SafetyChecker([OutputFilterGuardrail(patterns_to_block=["mock"])])
    agent = Agent(provider=MockProvider())

    result = await agent.run("Hello, world!", max_turns=1)
    sanitized = checker.check_output(result)
    assert "[REDACTED]" in sanitized
