"""Minimal AgentCore run example (single prompt)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from agent_core.api import AgentCore
from agent_core.engine import RunRequest


def main() -> int:
    parser = argparse.ArgumentParser(description="AgentCore example: simple Q&A")
    parser.add_argument(
        "--config",
        default="examples/configs/mock.json",
        help="Path to agent_core config (JSON/YAML).",
    )
    parser.add_argument("prompt", nargs="?", default="hello", help="Prompt text")
    args = parser.parse_args()

    core = AgentCore.from_file(args.config)
    result = core.run_sync(RunRequest(input=args.prompt))

    print(result.output_text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
