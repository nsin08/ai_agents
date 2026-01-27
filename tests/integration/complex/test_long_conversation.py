"""Integration test for long conversations."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from agent_core.engine import EngineComponents, LocalEngine, RunRequest, RunStatus
from agent_core.memory import InMemorySessionStore
from agent_core.model import ModelResponse


class SimpleModel:
    async def generate(self, messages, role):
        last_content = messages[-1]["content"] if messages else ""
        if last_content == "Plan the next step.":
            return ModelResponse(text="plan", role=role)
        return ModelResponse(text="ok", role=role)


@dataclass
class CountingCritic:
    target_turns: int
    calls: int = 0

    async def generate(self, messages, role):
        self.calls += 1
        verdict = "YES" if self.calls >= self.target_turns else "NO"
        return ModelResponse(text=verdict, role=role)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_long_conversation_20_turns() -> None:
    actor = SimpleModel()
    critic = CountingCritic(target_turns=20)

    engine = LocalEngine()
    components = EngineComponents(
        models={"planner": actor, "actor": actor, "critic": critic},
        memory=InMemorySessionStore(),
    )

    result = await engine.execute(RunRequest(input="hello", max_turns=25), components)

    assert result.status == RunStatus.SUCCESS
    assert result.turns == 20
