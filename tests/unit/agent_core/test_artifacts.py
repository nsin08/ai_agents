"""Unit tests for artifact bundle generation."""

from __future__ import annotations

import json
from pathlib import Path

from agent_core.artifacts import (
    ArtifactPayloads,
    ArtifactPaths,
    LocalFilesystemStore,
    RunArtifact,
    hash_config_snapshot,
    normalize_events_for_determinism,
    normalize_tool_calls_for_determinism,
)


def test_local_filesystem_store_writes_bundle(tmp_path: Path) -> None:
    artifact = RunArtifact(
        run_id="run-1",
        status="finished",
        started_at="2026-01-27T00:00:00+00:00",
        finished_at="2026-01-27T00:00:01+00:00",
        config_hash="hash",
        paths=ArtifactPaths(),
        result={"status": "success", "output_text": "ok"},
    )
    payloads = ArtifactPayloads(
        config_snapshot={"mode": "deterministic"},
        events=[{"run_id": "run-1", "event_type": "run.started"}],
        tool_calls=[{"tool_name": "calculator"}],
    )

    store = LocalFilesystemStore(base_dir=str(tmp_path))
    store.save_artifact(artifact, payloads)

    run_dir = tmp_path / "run-1"
    assert (run_dir / "run.json").exists()
    assert (run_dir / "config.snapshot.json").exists()
    assert (run_dir / "events.jsonl").exists()
    assert (run_dir / "tool_calls.json").exists()

    run_index = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
    assert run_index["run_id"] == "run-1"


def test_hash_config_snapshot_is_stable() -> None:
    snapshot = {"b": 2, "a": 1}
    assert hash_config_snapshot(snapshot) == hash_config_snapshot({"a": 1, "b": 2})


def test_artifact_paths_to_dict_includes_optional_fields() -> None:
    paths = ArtifactPaths(
        evidence="evidence.json",
        eval_scorecard="eval/score.json",
        eval_gate="eval/gate.json",
    )
    payload = paths.to_dict()

    assert payload["evidence"] == "evidence.json"
    assert payload["eval_scorecard"] == "eval/score.json"
    assert payload["eval_gate"] == "eval/gate.json"


def test_run_artifact_to_dict_includes_error_and_finished_at() -> None:
    artifact = RunArtifact(
        run_id="run-2",
        status="failed",
        started_at="2026-01-27T00:00:00+00:00",
        finished_at="2026-01-27T00:00:02+00:00",
        config_hash="hash",
        paths=ArtifactPaths(),
        result={"status": "failed", "output_text": ""},
        error={"type": "failed", "message": "boom"},
    )

    payload = artifact.to_dict()
    assert payload["finished_at"] == "2026-01-27T00:00:02+00:00"
    assert payload["error"]["type"] == "failed"


def test_normalize_events_for_determinism_rewrites_trace_and_time() -> None:
    events = [
        {
            "run_id": "run-1",
            "event_type": "run.started",
            "time": "2026-01-27T01:00:00+00:00",
            "trace": {"trace_id": "t1", "span_id": "s1"},
            "attrs": {"latency_s": 1.2},
        },
        {
            "run_id": "run-1",
            "event_type": "model.call.finished",
            "time": "2026-01-27T01:00:01+00:00",
            "trace": {"trace_id": "t1", "span_id": "s2", "parent_span_id": "s1"},
        },
    ]

    normalized = normalize_events_for_determinism(events)

    assert normalized[0]["time"].startswith("1970-01-01")
    assert normalized[0]["trace"]["trace_id"] == "trace-1"
    assert normalized[1]["trace"]["parent_span_id"] == "span-1"


def test_normalize_tool_calls_for_determinism_sets_time() -> None:
    tool_calls = [{"time": "2026-01-27T00:00:00+00:00", "tool_name": "x"}]
    normalized = normalize_tool_calls_for_determinism(tool_calls)

    assert normalized[0]["time"].startswith("1970-01-01")
