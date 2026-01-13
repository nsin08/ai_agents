from __future__ import annotations

import asyncio

from _bootstrap import add_repo_src_to_path

add_repo_src_to_path()

from agent_labs.tools import Calculator, ToolRegistry, WebSearch


async def main() -> None:
    registry = ToolRegistry()
    registry.register(Calculator())
    registry.register(WebSearch())

    print("OK: discovered_tools=", sorted(registry.list_tools()))

    results = await registry.execute_batch(
        [
            {"tool": "calculator", "params": {"operation": "add", "a": 2, "b": 3}},
            {"tool": "web_search", "params": {"query": "ai agents orchestration", "max_results": 2}},
        ]
    )

    print("OK: batch_statuses=", [r.status.value for r in results])
    print("OK: calc_output=", results[0].output)
    print("OK: web_total_results=", results[1].output.get("total_results"))


if __name__ == "__main__":
    asyncio.run(main())

