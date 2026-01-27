"""Unit tests for AgentCore public API."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest

from agent_core import AgentCoreConfig
from agent_core.api import AgentCore, RunArtifact
from agent_core.config.models import EngineConfig, ModelSpec, ModelsConfig, ToolsConfig
from agent_core.engine import EngineComponents, RunRequest, RunResult, RunStatus


class DummyEngine:
    def __init__(self) -> None:
        self.calls: list[tuple[RunRequest, EngineComponents]] = []

    async def execute(self, request: RunRequest, components: EngineComponents) -> RunResult:
        self.calls.append((request, components))
        return RunResult(status=RunStatus.SUCCESS, output_text="ok")


def _basic_config(base_dir: str | None = None) -> AgentCoreConfig:
    artifacts_config: dict = {}
    if base_dir:
        artifacts_config = {"store": {"backend": "filesystem", "config": {"base_dir": base_dir}}}
    return AgentCoreConfig(
        engine=EngineConfig(key="local"),
        models=ModelsConfig(
            roles={"actor": ModelSpec(provider="mock", model="deterministic")}
        ),
        tools=ToolsConfig(allowlist=[]),
        **({"artifacts": artifacts_config} if artifacts_config else {}),
    )


def test_from_config_builds_instance() -> None:
    core = AgentCore.from_config(_basic_config())
    assert isinstance(core, AgentCore)
    assert core.config.engine.key == "local"


def test_from_file_loads_config(tmp_path: Path) -> None:
    config_path = tmp_path / "agent_core.json"
    config_path.write_text(
        json.dumps(
            {
                "engine": {"key": "local", "config": {}},
                "models": {
                    "roles": {
                        "actor": {"provider": "mock", "model": "deterministic"}
                    }
                },
                "tools": {"allowlist": []},
            }
        ),
        encoding="utf-8",
    )
    core = AgentCore.from_file(str(config_path))
    assert core.config.engine.key == "local"
    assert "actor" in core.config.models.roles


def test_from_env_loads_config(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AGENT_CORE_APP__NAME", "agent-core-test")
    core = AgentCore.from_env()
    assert core.config.app.name == "agent-core-test"


@pytest.mark.asyncio
async def test_run_uses_engine_and_components() -> None:
    engine = DummyEngine()
    sentinel = object()
    core = AgentCore(
        _basic_config(),
        engine=engine,
        models={"actor": sentinel},
    )

    request = RunRequest(input="hi")
    result = await core.run(request)

    assert result.status == RunStatus.SUCCESS
    assert engine.calls
    called_request, called_components = engine.calls[0]
    assert called_request is request
    assert called_components.models == {"actor": sentinel}


@pytest.mark.asyncio
async def test_run_with_artifacts_returns_bundle(tmp_path: Path) -> None:
    engine = DummyEngine()
    sentinel = object()
    core = AgentCore(
        _basic_config(base_dir=str(tmp_path)),
        engine=engine,
        models={"actor": sentinel},
    )

    request = RunRequest(input="hi")
    result, artifact = await core.run_with_artifacts(request)

    assert result.status == RunStatus.SUCCESS
    assert isinstance(artifact, RunArtifact)
    assert artifact.run_id == request.run_id
    assert artifact.result["status"] == result.status.value


def test_run_sync_executes() -> None:
    engine = DummyEngine()
    sentinel = object()
    core = AgentCore(
        _basic_config(),
        engine=engine,
        models={"actor": sentinel},
    )

    result = core.run_sync(RunRequest(input="sync"))
    assert result.status == RunStatus.SUCCESS


def test_run_sync_rejects_running_loop() -> None:
    engine = DummyEngine()
    sentinel = object()
    core = AgentCore(
        _basic_config(),
        engine=engine,
        models={"actor": sentinel},
    )

    async def _runner() -> None:
        with pytest.raises(RuntimeError):
            core.run_sync(RunRequest(input="fail"))

    asyncio.run(_runner())
