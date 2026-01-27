"""AgentCore example showing tool calls via a custom model client.

This example uses the built-in calculator tool (native provider).
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from agent_core.api import AgentCore
from agent_core.config.models import (
    AgentCoreConfig,
    EngineConfig,
    ModelSpec,
    ModelsConfig,
    ObservabilityConfig,
    ToolsConfig,
)
from agent_core.engine import RunRequest
from agent_core.model import ModelResponse, ToolCall


@dataclass
class CalculatorFirstModel:
    used_tools: bool = False

    async def generate(self, messages, role):
        last = messages[-1]["content"] if messages else ""
        if last == "Plan the next step.":
            return ModelResponse(text="plan", role=role)
        if last == "Provide final answer.":
            return ModelResponse(text="The answer is 4.", role=role)

        if not self.used_tools:
            self.used_tools = True
            return ModelResponse(
                text="",
                role=role,
                tool_calls=[
                    ToolCall(name="calculator", arguments={"operation": "add", "a": 2, "b": 2})
                ],
            )
        return ModelResponse(text="done", role=role)


def main() -> int:
    parser = argparse.ArgumentParser(description="AgentCore example: tool use")
    parser.add_argument("prompt", nargs="?", default="What is 2+2?", help="Prompt text")
    args = parser.parse_args()

    config = AgentCoreConfig(
        engine=EngineConfig(key="local"),
        models=ModelsConfig(roles={"actor": ModelSpec(provider="mock", model="deterministic")}),
        tools=ToolsConfig(allowlist=["calculator"], providers={}),
        observability=ObservabilityConfig(exporter="disabled"),
    )

    model = CalculatorFirstModel()
    core = AgentCore(
        config,
        models={"planner": model, "actor": model},
    )

    # For artifact output, prefer CLI (agent-core run ...) or run_with_artifacts in async contexts.
    result = core.run_sync(RunRequest(input=args.prompt))
    print(result.output_text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
