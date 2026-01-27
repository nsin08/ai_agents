"""Integration test for concurrent runs isolation."""

from __future__ import annotations

import asyncio

import pytest

from agent_core.api import AgentCore
from agent_core.config.models import AgentCoreConfig, EngineConfig, ModelSpec, ModelsConfig, ObservabilityConfig
from agent_core.engine import RunRequest, RunStatus
from agent_core.model import ModelResponse


class EchoModel:
    async def generate(self, messages, role):
        for message in reversed(messages or []):
            if message.get("role") == "user" and message.get("content") not in {
                "Plan the next step.",
                "Provide final answer.",
            }:
                return ModelResponse(text=f"echo:{message.get('content', '')}", role=role)
        return ModelResponse(text="echo:", role=role)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_concurrent_runs_isolated() -> None:
    config = AgentCoreConfig(
        engine=EngineConfig(key="local"),
        models=ModelsConfig(roles={"actor": ModelSpec(provider="mock", model="deterministic")}),
        observability=ObservabilityConfig(exporter="disabled"),
    )
    core = AgentCore(config, models={"actor": EchoModel(), "planner": EchoModel()})

    async def run_one(index: int):
        request = RunRequest(input=f"msg-{index}", run_id=f"run-{index}")
        return await core.run(request)

    results = await asyncio.gather(*[run_one(i) for i in range(10)])

    assert all(result.status == RunStatus.SUCCESS for result in results)
    outputs = {result.output_text for result in results}
    assert outputs == {f"echo:msg-{i}" for i in range(10)}
