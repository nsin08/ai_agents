"""Integration test for tool failure recovery behavior."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from agent_core.engine import EngineComponents, LocalEngine, RunRequest, RunStatus
from agent_core.memory import InMemorySessionStore
from agent_core.model import ModelResponse, ToolCall
from agent_core.tools import ToolExecutor
from agent_core.tools.native import NativeToolProvider


@dataclass
class ToolFailureModel:
    tool_calls_used: bool = False

    async def generate(self, messages, role):
        last_content = messages[-1]["content"] if messages else ""
        if last_content == "Plan the next step.":
            return ModelResponse(text="plan", role=role)
        if last_content == "Provide final answer.":
            return ModelResponse(text="recovered", role=role)
        if not self.tool_calls_used:
            self.tool_calls_used = True
            return ModelResponse(
                text="",
                role=role,
                tool_calls=[
                    ToolCall(
                        name="calculator",
                        arguments={"operation": "divide", "a": 1, "b": 0},
                    )
                ],
            )
        return ModelResponse(text="done", role=role)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_tool_failure_recovery() -> None:
    model = ToolFailureModel()
    events: list[dict] = []
    tool_executor = ToolExecutor(
        providers=[NativeToolProvider()],
        allowlist=["calculator"],
        emit_event=events.append,
    )

    engine = LocalEngine()
    components = EngineComponents(
        models={"planner": model, "actor": model},
        tool_executor=tool_executor,
        memory=InMemorySessionStore(),
        emit_event=events.append,
    )

    result = await engine.execute(RunRequest(input="fail tool", max_turns=2), components)

    assert result.status == RunStatus.SUCCESS
    assert result.output_text == "recovered"
    tool_events = [event for event in events if event.get("event_type") == "tool.call.finished"]
    assert tool_events
    assert tool_events[0]["attrs"]["status"] == "failure"
