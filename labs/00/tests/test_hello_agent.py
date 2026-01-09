"""
Tests for Lab 0 hello agent.
"""

import pytest

from src.agent_labs.llm_providers import MockProvider
from src.agent_labs.orchestrator import Agent


@pytest.mark.asyncio
async def test_hello_agent_runs():
    provider = MockProvider()
    agent = Agent(provider=provider)
    result = await agent.run("Say hello in one sentence.", max_turns=1)

    assert isinstance(result, str)
    assert len(result) > 0
