"""Integration tests for complex multi-tool workflows."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest

from agent_core.engine import EngineComponents, LocalEngine, RunRequest, RunStatus
from agent_core.memory import InMemorySessionStore
from agent_core.model import ModelResponse, ToolCall
from agent_core.tools import ToolExecutor
from agent_core.tools.native import NativeToolProvider


@dataclass
class MultiToolModel:
    tool_calls: list[ToolCall]
    tool_calls_used: bool = False

    async def generate(self, messages, role):
        last_content = messages[-1]["content"] if messages else ""
        if last_content == "Plan the next step.":
            return ModelResponse(text="plan", role=role)
        if last_content == "Provide final answer.":
            return ModelResponse(text="final", role=role)
        if not self.tool_calls_used:
            self.tool_calls_used = True
            return ModelResponse(text="", role=role, tool_calls=self.tool_calls)
        return ModelResponse(text="done", role=role)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_multi_tool_workflow(tmp_path: Path) -> None:
    test_file = tmp_path / "note.txt"
    test_file.write_text("hello", encoding="utf-8")

    tool_calls = [
        ToolCall(name="calculator", arguments={"operation": "add", "a": 1, "b": 3}),
        ToolCall(name="web_search", arguments={"query": "agent core", "top_k": 2}),
        ToolCall(name="file_read", arguments={"path": str(test_file), "start_line": 1, "end_line": 1}),
    ]

    model = MultiToolModel(tool_calls=tool_calls)
    events: list[dict] = []
    tool_executor = ToolExecutor(
        providers=[NativeToolProvider()],
        allowlist=["calculator", "web_search", "file_read"],
        emit_event=events.append,
    )

    engine = LocalEngine()
    components = EngineComponents(
        models={"planner": model, "actor": model},
        tool_executor=tool_executor,
        memory=InMemorySessionStore(),
        emit_event=events.append,
    )

    result = await engine.execute(RunRequest(input="hello", max_turns=2), components)

    assert result.status == RunStatus.SUCCESS
    tool_events = [event for event in events if event.get("event_type") == "tool.call.finished"]
    assert len(tool_events) >= 3
    tool_names = {event["attrs"]["tool_name"] for event in tool_events}
    assert tool_names == {"calculator", "web_search", "file_read"}
