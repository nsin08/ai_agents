"""Regression test for deterministic stability across multiple runs."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agent_core import AgentCoreConfig
from agent_core.api import AgentCore
from agent_core.config.models import ArtifactsConfig, BackendConfig, EngineConfig, ModelSpec, ModelsConfig, ToolsConfig
from agent_core.engine import RunRequest


def _load_json_lines(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _normalize_run_id(events: list[dict], run_id: str) -> list[dict]:
    normalized: list[dict] = []
    for event in events:
        item = dict(event)
        if item.get("run_id") == run_id:
            item["run_id"] = "deterministic"
        normalized.append(item)
    return normalized


@pytest.mark.asyncio
@pytest.mark.integration
async def test_deterministic_stability_multiple_runs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo_root = Path(__file__).resolve().parents[3]
    fixtures_root = repo_root / "tests" / "fixtures"

    local_fixture_dir = tmp_path / "tests" / "fixtures"
    local_fixture_dir.mkdir(parents=True, exist_ok=True)
    (local_fixture_dir / "tool_fixtures.json").write_text(
        (fixtures_root / "tool_fixtures.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    monkeypatch.chdir(tmp_path)

    config = AgentCoreConfig(
        mode="deterministic",
        engine=EngineConfig(key="local"),
        models=ModelsConfig(roles={"actor": ModelSpec(provider="mock", model="deterministic")}),
        tools=ToolsConfig(
            providers={"fixture": {"path": "tests/fixtures/tool_fixtures.json"}},
            allowlist=[],
        ),
        artifacts=ArtifactsConfig(
            store=BackendConfig(backend="filesystem", config={"base_dir": "artifacts"})
        ),
    )

    core = AgentCore.from_config(config)

    baseline_events = None
    baseline_result = None

    for index in range(10):
        run_id = f"run-{index}"
        await core.run_with_artifacts(RunRequest(input="hello", run_id=run_id))
        run_dir = tmp_path / "artifacts" / run_id
        events = _normalize_run_id(_load_json_lines(run_dir / "events.jsonl"), run_id)
        run_json = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))

        if baseline_events is None:
            baseline_events = events
            baseline_result = run_json["result"]
        else:
            assert events == baseline_events
            assert run_json["result"] == baseline_result

    assert baseline_events is not None
