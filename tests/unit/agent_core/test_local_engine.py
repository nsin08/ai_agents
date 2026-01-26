"""Unit tests for LocalEngine state machine."""

from __future__ import annotations

import asyncio

import pytest

from agent_core.engine import EngineComponents, LocalEngine, RunRequest, RunStatus
from agent_core.memory import InMemorySessionStore
from agent_core.model import ModelResponse, ToolCall as ModelToolCall
from agent_core.tools import ExecutionStatus, RiskLevel, ToolContract, ToolExecutor, ToolResult
from agent_core.tools.provider import ToolProvider
from agent_core.config.models import PoliciesConfig, BudgetsConfig


class StaticModel:
    def __init__(self, text: str, tool_calls=None, delay: float = 0.0) -> None:
        self._text = text
        self._tool_calls = tool_calls
        self._delay = delay

    async def generate(self, messages, role: str) -> ModelResponse:  # type: ignore[override]
        if self._delay:
            await asyncio.sleep(self._delay)
        return ModelResponse(text=self._text, role=role, tool_calls=self._tool_calls)


class RecordingProvider(ToolProvider):
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict]] = []

    async def list_tools(self):
        return [
            ToolContract(
                name="tool",
                description="test tool",
                risk=RiskLevel.READ,
                input_schema={"type": "object"},
                output_schema={"type": "object"},
            )
        ]

    async def execute(self, tool_name: str, args: dict):
        self.calls.append((tool_name, dict(args)))
        return ToolResult(status=ExecutionStatus.SUCCESS, output={"ok": True})


@pytest.mark.asyncio
async def test_max_turns_stops_loop() -> None:
    engine = LocalEngine()
    models = {
        "planner": StaticModel("plan"),
        "actor": StaticModel("answer"),
        "critic": StaticModel("NO | retry"),
    }
    components = EngineComponents(models=models, memory=InMemorySessionStore())
    result = await engine.execute(RunRequest(input="hi", max_turns=2), components)

    assert result.status == RunStatus.FAILED
    assert result.reason == "max_turns"
    assert result.turns == 2


@pytest.mark.asyncio
async def test_timeout_returns_timeout() -> None:
    engine = LocalEngine()
    models = {
        "planner": StaticModel("plan", delay=0.05),
        "actor": StaticModel("answer", delay=0.05),
    }
    components = EngineComponents(models=models, memory=InMemorySessionStore())
    result = await engine.execute(RunRequest(input="hi", timeout_s=0.01), components)

    assert result.status == RunStatus.TIMEOUT


@pytest.mark.asyncio
async def test_budget_exceeded() -> None:
    engine = LocalEngine()
    models = {
        "planner": StaticModel("plan"),
        "actor": StaticModel("long-answer" * 50),
    }
    policies = PoliciesConfig(budgets=BudgetsConfig(max_total_tokens=5))
    components = EngineComponents(models=models, memory=InMemorySessionStore(), policies=policies)
    result = await engine.execute(RunRequest(input="hi"), components)

    assert result.status == RunStatus.BUDGET_EXCEEDED


@pytest.mark.asyncio
async def test_cancelled_before_start() -> None:
    engine = LocalEngine()
    cancel_event = asyncio.Event()
    cancel_event.set()
    models = {"planner": StaticModel("plan"), "actor": StaticModel("answer")}
    components = EngineComponents(models=models, memory=InMemorySessionStore())
    result = await engine.execute(RunRequest(input="hi", cancel_event=cancel_event), components)

    assert result.status == RunStatus.CANCELLED


@pytest.mark.asyncio
async def test_tool_calls_flow_through_executor() -> None:
    engine = LocalEngine()
    tool_call = ModelToolCall(name="tool", arguments={"a": 1})
    models = {
        "planner": StaticModel("plan"),
        "actor": StaticModel("use tool", tool_calls=[tool_call]),
        "critic": StaticModel("YES | done"),
    }
    provider = RecordingProvider()
    executor = ToolExecutor([provider], allowlist=["tool"])
    components = EngineComponents(
        models=models,
        tool_executor=executor,
        memory=InMemorySessionStore(),
    )

    result = await engine.execute(RunRequest(input="hi"), components)

    assert result.status == RunStatus.SUCCESS
    assert provider.calls == [("tool", {"a": 1})]
