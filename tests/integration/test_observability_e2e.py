"""Integration test for observability event emission."""

from __future__ import annotations

import pytest

from agent_core.engine import EngineComponents, LocalEngine, RunRequest, RunStatus
from agent_core.memory import InMemorySessionStore
from agent_core.model import ModelResponse, ToolCall as ModelToolCall
from agent_core.observability import MemoryExporter, ObservabilityEmitter
from agent_core.tools import ExecutionStatus, RiskLevel, ToolContract, ToolExecutor, ToolResult
from agent_core.tools.provider import ToolProvider


class SequenceModel:
    def __init__(self, responses: list[ModelResponse]) -> None:
        self._responses = responses
        self._index = 0

    async def generate(self, messages, role: str) -> ModelResponse:  # type: ignore[override]
        if self._index >= len(self._responses):
            return self._responses[-1]
        response = self._responses[self._index]
        self._index += 1
        return response


class EchoProvider(ToolProvider):
    async def list_tools(self):
        return [
            ToolContract(
                name="echo",
                description="Echo tool",
                risk=RiskLevel.READ,
                input_schema={"type": "object"},
                output_schema={"type": "object"},
            )
        ]

    async def execute(self, tool_name: str, args: dict):
        return ToolResult(status=ExecutionStatus.SUCCESS, output={"echo": dict(args)})


@pytest.mark.asyncio
@pytest.mark.integration
async def test_observability_events_emitted() -> None:
    tool_call = ModelToolCall(name="echo", arguments={"text": "hi"})
    actor = SequenceModel(
        [
            ModelResponse(text="calling tool", role="assistant", tool_calls=[tool_call]),
            ModelResponse(text="final answer", role="assistant"),
        ]
    )
    planner = SequenceModel([ModelResponse(text="plan", role="assistant")])
    critic = SequenceModel([ModelResponse(text="YES | done", role="assistant")])

    exporter = MemoryExporter()
    emitter = ObservabilityEmitter([exporter])
    executor = ToolExecutor([EchoProvider()], allowlist=["echo"], emit_event=emitter.emit)

    components = EngineComponents(
        models={"planner": planner, "actor": actor, "critic": critic},
        tool_executor=executor,
        memory=InMemorySessionStore(),
        emit_event=emitter.emit,
    )

    engine = LocalEngine()
    result = await engine.execute(RunRequest(input="hello"), components)

    assert result.status == RunStatus.SUCCESS
    event_types = {event["event_type"] for event in exporter.events}
    assert "run.started" in event_types
    assert "run.finished" in event_types
    assert "model.call.started" in event_types
    assert "model.call.finished" in event_types
    assert "tool.call.started" in event_types
    assert "tool.call.finished" in event_types

    trace_ids = {
        event.get("trace", {}).get("trace_id")
        for event in exporter.events
        if event.get("trace")
    }
    assert len({trace_id for trace_id in trace_ids if trace_id}) == 1
