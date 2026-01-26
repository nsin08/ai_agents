"""Fixture-based tool provider for deterministic tests."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping


@dataclass(frozen=True)
class ToolFixture:
    tool_name: str
    tool_version: str
    args_hash: str
    result: Mapping[str, Any]


class FixtureNotFoundError(KeyError):
    """Raised when a fixture entry cannot be found."""


class FixtureToolProvider:
    """Replay tool results from fixture files."""

    def __init__(self, fixtures_path: str | Path) -> None:
        self._fixtures_path = Path(fixtures_path)
        self._fixtures = self._load_fixtures(self._fixtures_path)

    async def execute(
        self,
        tool_name: str,
        args: Mapping[str, Any],
        tool_version: str = "",
    ) -> Mapping[str, Any]:
        args_hash = hash_args(args)
        key = (tool_name, tool_version, args_hash)
        fixture = self._fixtures.get(key)
        if fixture is None:
            raise FixtureNotFoundError(
                f"No fixture for tool '{tool_name}' version '{tool_version}' with args hash '{args_hash}'."
            )
        return fixture.result

    def _load_fixtures(self, path: Path) -> dict[tuple[str, str, str], ToolFixture]:
        fixtures: dict[tuple[str, str, str], ToolFixture] = {}
        if path.is_dir():
            files = sorted(path.glob("*.json"))
        else:
            files = [path]

        for file_path in files:
            if not file_path.exists():
                continue
            data = json.loads(file_path.read_text(encoding="utf-8-sig"))
            entries = data if isinstance(data, list) else data.get("fixtures", [])
            for entry in entries:
                fixture = ToolFixture(
                    tool_name=entry["tool_name"],
                    tool_version=entry.get("tool_version", ""),
                    args_hash=entry["args_hash"],
                    result=entry["result"],
                )
                fixtures[(fixture.tool_name, fixture.tool_version, fixture.args_hash)] = fixture
        return fixtures


def hash_args(args: Mapping[str, Any]) -> str:
    payload = json.dumps(args, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


__all__ = ["FixtureToolProvider", "FixtureNotFoundError", "ToolFixture", "hash_args"]
