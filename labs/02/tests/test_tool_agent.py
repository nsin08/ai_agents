"""
Tests for Lab 2 tool-enabled agent.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))
from tool_agent import build_registry, run_tool_sequence  # noqa: E402


@pytest.mark.asyncio
async def test_tool_agent_sequence():
    registry = build_registry()
    results = await run_tool_sequence(registry)

    assert results["calculator"] == 5
    assert results["weather"]["city"] == "Berlin"
    assert "files" in results["files"]
