"""
Tool-enabled agent for Lab 2.
"""

from __future__ import annotations

import asyncio
from typing import Dict

import sys
from pathlib import Path

from src.agent_labs.tools import ToolRegistry

sys.path.insert(0, str(Path(__file__).parent))
from custom_tools import CalculatorTool, WeatherLookupTool, FileOpsTool  # noqa: E402


def build_registry() -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(CalculatorTool())
    registry.register(WeatherLookupTool())
    registry.register(FileOpsTool())
    return registry


async def run_tool_sequence(registry: ToolRegistry) -> Dict[str, object]:
    results = {}
    calc = await registry.execute("calculator", operation="add", a=2, b=3)
    results["calculator"] = calc.output
    weather = await registry.execute("weather_lookup", city="Berlin")
    results["weather"] = weather.output
    files = await registry.execute("file_ops", path="labs/02")
    results["files"] = files.output
    return results


async def main() -> None:
    registry = build_registry()
    results = await run_tool_sequence(registry)
    print(results)


if __name__ == "__main__":
    asyncio.run(main())
