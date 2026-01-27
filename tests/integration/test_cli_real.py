"""Integration tests for CLI commands."""

from __future__ import annotations

import json
from pathlib import Path

from agent_core.cli import EXIT_SUCCESS, EXIT_USER_ERROR, main


def _write_config(path: Path, *, deterministic: bool = False, include_fixture: bool = True) -> None:
    payload = {
        "engine": {"key": "local", "config": {}},
        "models": {"roles": {"actor": {"provider": "mock", "model": "deterministic"}}},
        "tools": {"providers": {"fixture": {"path": "tests/fixtures/tool_fixtures.json"}}},
    }
    if not include_fixture:
        payload["tools"] = {"providers": {}}
    if deterministic:
        payload["mode"] = "deterministic"
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_cli_validate_config(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    _write_config(config_path, deterministic=True)

    exit_code = main(["validate-config", str(config_path)])

    assert exit_code == EXIT_SUCCESS


def test_cli_run_creates_artifacts(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    _write_config(config_path)
    artifact_dir = tmp_path / "artifacts"

    exit_code = main(
        ["run", "hello", "--config", str(config_path), "--artifact-dir", str(artifact_dir)]
    )

    assert exit_code == EXIT_SUCCESS
    run_dirs = [path for path in artifact_dir.iterdir() if path.is_dir()]
    assert run_dirs
    assert (run_dirs[0] / "run.json").exists()


def test_cli_validate_config_failure(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    _write_config(config_path, deterministic=False, include_fixture=False)

    exit_code = main(["validate-config", str(config_path), "--mode", "deterministic"])

    assert exit_code == EXIT_USER_ERROR
