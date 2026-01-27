"""Models for run artifacts."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ArtifactPaths:
    run_index: str = "run.json"
    config_snapshot: str = "config.snapshot.json"
    events: str = "events.jsonl"
    tool_calls: str = "tool_calls.json"
    evidence: str | None = None
    eval_scorecard: str | None = None
    eval_gate: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "config_snapshot": self.config_snapshot,
            "events": self.events,
            "tool_calls": self.tool_calls,
        }
        if self.evidence:
            payload["evidence"] = self.evidence
        if self.eval_scorecard:
            payload["eval_scorecard"] = self.eval_scorecard
        if self.eval_gate:
            payload["eval_gate"] = self.eval_gate
        return payload


@dataclass(frozen=True)
class RunArtifact:
    run_id: str
    status: str
    started_at: str
    finished_at: str | None
    config_hash: str
    paths: ArtifactPaths
    versions: dict[str, Any] = field(default_factory=dict)
    result: dict[str, Any] = field(default_factory=dict)
    error: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "run_id": self.run_id,
            "status": self.status,
            "started_at": self.started_at,
            "config_hash": self.config_hash,
            "paths": self.paths.to_dict(),
            "versions": dict(self.versions),
            "result": dict(self.result),
        }
        if self.finished_at:
            payload["finished_at"] = self.finished_at
        if self.error:
            payload["error"] = dict(self.error)
        return payload


@dataclass(frozen=True)
class ArtifactPayloads:
    config_snapshot: dict[str, Any]
    events: list[dict[str, Any]]
    tool_calls: list[dict[str, Any]]


__all__ = ["ArtifactPaths", "RunArtifact", "ArtifactPayloads"]
