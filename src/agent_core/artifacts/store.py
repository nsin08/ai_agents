"""Artifact stores for run bundles."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol

from .models import ArtifactPayloads, RunArtifact


class ArtifactStore(Protocol):
    def save_artifact(self, artifact: RunArtifact, payloads: ArtifactPayloads) -> RunArtifact:
        ...


class LocalFilesystemStore:
    def __init__(self, base_dir: str = "artifacts") -> None:
        self._base_dir = Path(base_dir)

    def save_artifact(self, artifact: RunArtifact, payloads: ArtifactPayloads) -> RunArtifact:
        run_dir = self._base_dir / artifact.run_id
        run_dir.mkdir(parents=True, exist_ok=True)

        self._write_json(run_dir / artifact.paths.config_snapshot, payloads.config_snapshot)
        self._write_json_lines(run_dir / artifact.paths.events, payloads.events)
        self._write_json(run_dir / artifact.paths.tool_calls, payloads.tool_calls)
        self._write_json(run_dir / artifact.paths.run_index, artifact.to_dict())

        return artifact

    @staticmethod
    def _write_json(path: Path, payload: object) -> None:
        path.write_text(
            json.dumps(payload, sort_keys=True, indent=2, default=str),
            encoding="utf-8",
        )

    @staticmethod
    def _write_json_lines(path: Path, events: list[dict[str, object]]) -> None:
        with path.open("w", encoding="utf-8") as handle:
            for event in events:
                handle.write(json.dumps(event, sort_keys=True, default=str) + "\n")


__all__ = ["ArtifactStore", "LocalFilesystemStore"]
