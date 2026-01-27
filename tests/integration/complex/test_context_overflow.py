"""Integration test for context overflow behavior."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from agent_core.engine import EngineComponents, LocalEngine, RunRequest, RunStatus
from agent_core.memory import InMemorySessionStore, estimate_tokens
from agent_core.model import ModelResponse


@dataclass
class OverflowModel:
    critic_limit: int = 3
    critic_calls: int = 0

    async def generate(self, messages, role):
        last_content = messages[-1]["content"] if messages else ""
        if last_content == "Plan the next step.":
            return ModelResponse(text="plan", role=role)
        if role == "critic":
            self.critic_calls += 1
            verdict = "YES" if self.critic_calls >= self.critic_limit else "NO"
            return ModelResponse(text=verdict, role=role)
        return ModelResponse(text="x" * 120, role=role)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_context_overflow_truncates() -> None:
    memory = InMemorySessionStore(max_tokens=1)
    model = OverflowModel(critic_limit=3)

    engine = LocalEngine()
    components = EngineComponents(
        models={"planner": model, "actor": model, "critic": model},
        memory=memory,
    )

    result = await engine.execute(RunRequest(input="hello", max_turns=5), components)

    assert result.status == RunStatus.SUCCESS
    context = await memory.get_context()
    total_tokens = sum(estimate_tokens(message["content"]) for message in context)
    assert total_tokens <= 1
    assert len(context) == 1
    assert context[0]["content"] != "hello"
