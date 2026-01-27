"""Unit tests for CLI argument parsing."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from agent_core.artifacts import ArtifactPaths, RunArtifact
from agent_core.cli import EXIT_RUNTIME_ERROR, EXIT_SUCCESS, EXIT_USER_ERROR, _run_command, build_parser, main
from agent_core.engine import RunResult, RunStatus


def test_parse_run_with_prompt() -> None:
    parser = build_parser()
    args = parser.parse_args(["run", "hello"])

    assert args.command == "run"
    assert args.prompt == "hello"


def test_parse_run_with_flags() -> None:
    parser = build_parser()
    args = parser.parse_args(
        [
            "run",
            "hello",
            "--config",
            "config.json",
            "--mode",
            "deterministic",
            "--artifact-dir",
            "out",
            "--json",
        ]
    )

    assert args.config_path == "config.json"
    assert args.mode == "deterministic"
    assert args.artifact_dir == "out"
    assert args.json_summary is True


def test_parse_validate_config() -> None:
    parser = build_parser()
    args = parser.parse_args(["validate-config", "config.json"])

    assert args.command == "validate-config"
    assert args.config_path == "config.json"


def test_main_without_command_returns_error(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main([])

    assert exit_code == EXIT_USER_ERROR
    assert capsys.readouterr().out


def test_run_command_requires_prompt(capsys: pytest.CaptureFixture[str]) -> None:
    args = build_parser().parse_args(["run"])

    exit_code = _run_command(args)

    assert exit_code == EXIT_USER_ERROR
    assert "prompt text is required" in capsys.readouterr().err


def test_run_command_config_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def _raise(*_args, **_kwargs):
        raise ValueError("bad config")

    monkeypatch.setattr("agent_core.cli.load_config", _raise)
    args = build_parser().parse_args(["run", "hello"])

    exit_code = _run_command(args)

    assert exit_code == EXIT_USER_ERROR


def test_run_command_runtime_error(monkeypatch: pytest.MonkeyPatch) -> None:
    class DummyCore:
        async def run_with_artifacts(self, request):
            raise RuntimeError("boom")

    monkeypatch.setattr("agent_core.cli.load_config", lambda *args, **kwargs: object())
    monkeypatch.setattr("agent_core.cli.AgentCore.from_config", lambda config: DummyCore())

    args = build_parser().parse_args(["run", "hello"])
    exit_code = _run_command(args)

    assert exit_code == EXIT_RUNTIME_ERROR


def test_run_command_json_summary(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    @dataclass
    class DummyCore:
        async def run_with_artifacts(self, request):
            result = RunResult(status=RunStatus.SUCCESS, output_text="ok")
            artifact = RunArtifact(
                run_id="run-1",
                status="finished",
                started_at="2026-01-27T00:00:00+00:00",
                finished_at="2026-01-27T00:00:01+00:00",
                config_hash="hash",
                paths=ArtifactPaths(),
                result={"status": "success", "output_text": "ok"},
            )
            return result, artifact

    monkeypatch.setattr("agent_core.cli.load_config", lambda *args, **kwargs: object())
    monkeypatch.setattr("agent_core.cli.AgentCore.from_config", lambda config: DummyCore())

    args = build_parser().parse_args(["run", "hello", "--json", "--artifact-dir", "out"])
    exit_code = _run_command(args)

    assert exit_code == EXIT_SUCCESS
    stderr = capsys.readouterr().err
    assert "\"run_id\": \"run-1\"" in stderr


def test_validate_command_with_mode_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def _raise(*_args, **_kwargs):
        raise ValueError("bad config")

    monkeypatch.setattr("agent_core.cli.load_config", _raise)

    exit_code = main(["validate-config", "config.json", "--mode", "deterministic"])

    assert exit_code == EXIT_USER_ERROR
