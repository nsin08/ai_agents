"""Integration test for deterministic mode artifacts."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agent_core import AgentCoreConfig
from agent_core.api import AgentCore
from agent_core.config.models import EngineConfig, ModelSpec, ModelsConfig, ToolsConfig, ArtifactsConfig, BackendConfig
from agent_core.engine import RunRequest


def _load_events(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _normalize_run_id(payloads: list[dict], run_id: str) -> list[dict]:
    normalized: list[dict] = []
    for event in payloads:
        item = dict(event)
        if item.get("run_id") == run_id:
            item["run_id"] = "deterministic"
        normalized.append(item)
    return normalized


@pytest.mark.asyncio
@pytest.mark.integration
async def test_deterministic_mode_artifacts_equal(tmp_path: Path) -> None:
    base_dir = tmp_path / "artifacts"
    config = AgentCoreConfig(
        mode="deterministic",
        engine=EngineConfig(key="local"),
        models=ModelsConfig(
            roles={"actor": ModelSpec(provider="mock", model="deterministic")}
        ),
        tools=ToolsConfig(
            providers={"fixture": {"path": "tests/fixtures/tool_fixtures.json"}},
            allowlist=[],
        ),
        artifacts=ArtifactsConfig(
            store=BackendConfig(
                backend="filesystem",
                config={"base_dir": str(base_dir)},
            )
        ),
    )

    core = AgentCore.from_config(config)
    result1, artifact1 = await core.run_with_artifacts(RunRequest(input="hello", run_id="run-1"))
    result2, artifact2 = await core.run_with_artifacts(RunRequest(input="hello", run_id="run-2"))

    run1 = json.loads((base_dir / "run-1" / "run.json").read_text(encoding="utf-8"))
    run2 = json.loads((base_dir / "run-2" / "run.json").read_text(encoding="utf-8"))

    assert result1.output_text == result2.output_text

    events1 = _normalize_run_id(_load_events(base_dir / "run-1" / "events.jsonl"), "run-1")
    events2 = _normalize_run_id(_load_events(base_dir / "run-2" / "events.jsonl"), "run-2")

    assert events1 == events2
    assert run1["result"] == run2["result"]
    assert artifact1.status == artifact2.status
