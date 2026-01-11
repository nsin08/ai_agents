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
    print(f"Discovered tools: {registry.list_tools()}")

    calc = await registry.execute("calculator", operation="add", a=2, b=3)
    print("Tool call: calculator(operation=add, a=2, b=3)")
    print(f"Tool result: {calc.output if calc.success else calc.error}")
    results["calculator"] = calc.output if calc.success else {"error": calc.error}

    weather = await registry.execute("weather_lookup", city="Berlin")
    print("Tool call: weather_lookup(city=Berlin)")
    print(f"Tool result: {weather.output if weather.success else weather.error}")
    results["weather"] = weather.output if weather.success else {"error": weather.error}

    files = await registry.execute("file_ops", path="labs/02")
    print("Tool call: file_ops(path=labs/02)")
    print(f"Tool result: {files.output if files.success else files.error}")
    results["files"] = files.output if files.success else {"error": files.error}
    return results


async def main() -> None:
    registry = build_registry()
    results = await run_tool_sequence(registry)
    print(f"Final response: {results}")


if __name__ == "__main__":
    asyncio.run(main())
