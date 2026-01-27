"""Command-line interface for agent_core."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from typing import Any, Mapping

from .api import AgentCore
from .config import load_config
from .engine import RunRequest, RunStatus


EXIT_SUCCESS = 0
EXIT_USER_ERROR = 2
EXIT_RUNTIME_ERROR = 3
EXIT_EVAL_FAILED = 4


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agent-core", description="AgentCore CLI")
    subparsers = parser.add_subparsers(dest="command")

    run_parser = subparsers.add_parser("run", help="Run a single prompt.")
    run_parser.add_argument("prompt", nargs="?", help="Prompt text.")
    run_parser.add_argument("--input", dest="input_text", help="Prompt text (alternative).")
    run_parser.add_argument("--config", dest="config_path", help="Config file path (YAML/JSON).")
    run_parser.add_argument("--mode", choices=["deterministic", "real"], help="Override mode.")
    run_parser.add_argument(
        "--artifact-dir",
        dest="artifact_dir",
        help="Base directory for artifacts (default: ./artifacts).",
    )
    run_parser.add_argument("--json", dest="json_summary", action="store_true", help="Print JSON summary.")

    validate_parser = subparsers.add_parser("validate-config", help="Validate a config file.")
    validate_parser.add_argument("config_path", help="Config file path (YAML/JSON).")
    validate_parser.add_argument("--mode", choices=["deterministic", "real"], help="Override mode.")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "run":
        return _run_command(args)
    if args.command == "validate-config":
        return _validate_command(args)

    parser.print_help()
    return EXIT_USER_ERROR


def _run_command(args: argparse.Namespace) -> int:
    prompt = args.input_text or args.prompt
    if not prompt:
        print("Error: prompt text is required.", file=sys.stderr)
        return EXIT_USER_ERROR

    overrides: dict[str, Any] = {
        "observability": {"exporter": "stdout"},
    }
    if args.mode:
        overrides["mode"] = args.mode
    if args.artifact_dir:
        overrides["artifacts"] = {
            "store": {"backend": "filesystem", "config": {"base_dir": args.artifact_dir}}
        }

    try:
        config = load_config(path=args.config_path, overrides=overrides)
    except Exception as exc:
        print(f"Config error: {exc}", file=sys.stderr)
        return EXIT_USER_ERROR

    core = AgentCore.from_config(config)
    request = RunRequest(input=prompt)

    try:
        result, artifact = asyncio.run(core.run_with_artifacts(request))
    except Exception as exc:
        print(f"Runtime error: {exc}", file=sys.stderr)
        return EXIT_RUNTIME_ERROR

    summary = {
        "run_id": artifact.run_id,
        "status": result.status.value,
        "artifact_dir": getattr(args, "artifact_dir", None) or "artifacts",
        "output_text": result.output_text,
    }
    if args.json_summary:
        print(json.dumps(summary), file=sys.stderr)
    else:
        print(
            f"run_id={summary['run_id']} status={summary['status']} artifact_dir={summary['artifact_dir']}",
            file=sys.stderr,
        )

    if result.status == RunStatus.SUCCESS:
        return EXIT_SUCCESS
    if result.status == RunStatus.CANCELLED:
        return EXIT_RUNTIME_ERROR
    return EXIT_RUNTIME_ERROR


def _validate_command(args: argparse.Namespace) -> int:
    try:
        overrides: dict[str, Any] = {}
        if args.mode:
            overrides["mode"] = args.mode
        load_config(path=args.config_path, overrides=overrides)
    except Exception as exc:
        print(f"Config error: {exc}", file=sys.stderr)
        return EXIT_USER_ERROR
    print("Config valid.")
    return EXIT_SUCCESS


__all__ = [
    "EXIT_EVAL_FAILED",
    "EXIT_RUNTIME_ERROR",
    "EXIT_SUCCESS",
    "EXIT_USER_ERROR",
    "build_parser",
    "main",
]
