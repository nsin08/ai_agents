"""AgentCore example showing a multi-turn conversation using a shared session store."""

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
)
from agent_core.engine import RunRequest
from agent_core.memory import InMemorySessionStore
from agent_core.model import ModelResponse


@dataclass
class MemoryAwareModel:
    async def generate(self, messages, role):
        # Very small demo: if user says "My name is X", later answer "X".
        if any("Plan the next step." == msg.get("content") for msg in messages):
            return ModelResponse(text="plan", role=role)

        name = None
        for msg in messages:
            if msg.get("role") == "user" and "My name is" in str(msg.get("content")):
                tail = str(msg.get("content")).split("My name is", 1)[1].strip()
                if tail:
                    name = tail.strip(". ")

        last_user = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                last_user = str(msg.get("content"))
                break

        if "What is my name" in last_user and name:
            return ModelResponse(text=name, role=role)
        return ModelResponse(text=f"echo:{last_user}", role=role)


def main() -> int:
    parser = argparse.ArgumentParser(description="AgentCore example: multi-turn")
    parser.add_argument(
        "--config",
        default="",
        help="Optional AgentCore config path. If provided, the example uses AgentCore.from_file() "
        "and a shared session store (outputs depend on the configured provider/model).",
    )
    parser.add_argument("--first", default="", help="First user message (overrides positional if set).")
    parser.add_argument("--second", default="", help="Second user message (overrides positional if set).")
    parser.add_argument("first_prompt", nargs="?", default="My name is Alice.")
    parser.add_argument("second_prompt", nargs="?", default="What is my name?")
    args = parser.parse_args()

    first = args.first or args.first_prompt
    second = args.second or args.second_prompt

    shared_memory = InMemorySessionStore()

    if args.config:
        core = AgentCore.from_file(args.config, emit_event=None)
        # Force shared memory for multi-turn behavior across calls.
        core._memory_factory = lambda: shared_memory  # type: ignore[attr-defined]
    else:
        config = AgentCoreConfig(
            engine=EngineConfig(key="local"),
            models=ModelsConfig(roles={"actor": ModelSpec(provider="mock", model="deterministic")}),
            observability=ObservabilityConfig(exporter="disabled"),
        )
        model = MemoryAwareModel()
        core = AgentCore(
            config,
            models={"planner": model, "actor": model},
            memory_factory=lambda: shared_memory,
        )

    first_result = core.run_sync(RunRequest(input=first))
    second_result = core.run_sync(RunRequest(input=second))

    print("turn1:", first_result.output_text)
    print("turn2:", second_result.output_text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
