"""Integration tests for LocalEngine execution flow."""

from __future__ import annotations

import pytest

from agent_core import AgentCoreConfig
from agent_core.config.models import EngineConfig, ModelSpec, ModelsConfig, ToolsConfig
from agent_core.engine import EngineComponents, LocalEngine, RunRequest, RunStatus
from agent_core.factories import ModelFactory
from agent_core.memory import InMemorySessionStore
from agent_core.model import ModelResponse, ToolCall as ModelToolCall
from agent_core.registry import get_global_registry
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
    def __init__(self) -> None:
        self.calls: list[dict] = []

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
        self.calls.append({"tool": tool_name, "args": dict(args)})
        return ToolResult(status=ExecutionStatus.SUCCESS, output={"echo": dict(args)})


@pytest.mark.asyncio
@pytest.mark.integration
async def test_local_engine_e2e_mock_answer() -> None:
    registry = get_global_registry()
    config = AgentCoreConfig(
        engine=EngineConfig(key="local"),
        models=ModelsConfig(
            roles={
                "planner": ModelSpec(provider="mock", model="deterministic"),
                "actor": ModelSpec(provider="mock", model="deterministic"),
            }
        ),
        tools=ToolsConfig(),
    )

    model_factory = ModelFactory(registry.model_providers)
    models = model_factory.build_role_map(config.models.roles)
    engine = LocalEngine()

    components = EngineComponents(models=models, memory=InMemorySessionStore())
    result = await engine.execute(RunRequest(input="hello"), components)

    assert result.status == RunStatus.SUCCESS
    assert result.output_text.startswith("mock::actor::")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_local_engine_e2e_tool_flow() -> None:
    tool_call = ModelToolCall(name="echo", arguments={"text": "hi"}, call_id="call-1")
    actor = SequenceModel(
        [
            ModelResponse(text="calling tool", role="assistant", tool_calls=[tool_call]),
            ModelResponse(text="final answer", role="assistant"),
        ]
    )
    planner = SequenceModel([ModelResponse(text="plan", role="assistant")])
    critic = SequenceModel([ModelResponse(text="YES | done", role="assistant")])

    provider = EchoProvider()
    executor = ToolExecutor([provider], allowlist=["echo"])
    components = EngineComponents(
        models={"planner": planner, "actor": actor, "critic": critic},
        tool_executor=executor,
        memory=InMemorySessionStore(),
    )

    engine = LocalEngine()
    result = await engine.execute(RunRequest(input="hello"), components)

    assert result.status == RunStatus.SUCCESS
    assert result.output_text == "final answer"
    assert provider.calls == [{"tool": "echo", "args": {"text": "hi"}}]
