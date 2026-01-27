"""Regression test for golden artifacts."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agent_core import AgentCoreConfig
from agent_core.api import AgentCore
from agent_core.config.models import ArtifactsConfig, BackendConfig, EngineConfig, ModelSpec, ModelsConfig, ToolsConfig
from agent_core.engine import RunRequest


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_json_lines(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_golden_artifacts_match(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    repo_root = Path(__file__).resolve().parents[3]
    fixtures_root = repo_root / "tests" / "fixtures"
    regression_root = fixtures_root / "regression"

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
    await core.run_with_artifacts(RunRequest(input="hello", run_id="golden-run"))

    run_dir = tmp_path / "artifacts" / "golden-run"
    run_json = _load_json(run_dir / "run.json")
    events = _load_json_lines(run_dir / "events.jsonl")
    tool_calls = _load_json(run_dir / "tool_calls.json")

    expected_run = _load_json(regression_root / "golden_run.json")
    expected_events = _load_json_lines(regression_root / "golden_events.jsonl")
    expected_tool_calls = _load_json(regression_root / "golden_tool_calls.json")

    assert run_json == expected_run
    assert events == expected_events
    assert tool_calls == expected_tool_calls
