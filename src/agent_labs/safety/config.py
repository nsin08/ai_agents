"""
Configuration loading for safety guardrails.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from .guardrails import (
    TokenLimitGuardrail,
    ToolAllowlistGuardrail,
    InputValidationGuardrail,
    OutputFilterGuardrail,
)
from .base import Guardrail


def load_config(path: str) -> Dict[str, object]:
    """Load guardrail configuration from JSON or YAML."""
    file_path = Path(path)
    data = file_path.read_text(encoding="utf-8")
    if file_path.suffix.lower() in {".yaml", ".yml"}:
        try:
            import yaml
        except ImportError as exc:
            raise RuntimeError("PyYAML is required for YAML config") from exc
        return yaml.safe_load(data)
    return json.loads(data)


def build_guardrails(config: Dict[str, object]) -> List[Guardrail]:
    """Build guardrails from config data."""
    guardrails: List[Guardrail] = []
    guardrail_config = config.get("guardrails", {}) if isinstance(config, dict) else {}

    token_cfg = guardrail_config.get("token_limit", {})
    if token_cfg.get("enabled", False):
        guardrails.append(TokenLimitGuardrail(max_tokens=token_cfg.get("max_tokens", 4096)))

    tool_cfg = guardrail_config.get("tool_allowlist", {})
    if tool_cfg.get("enabled", False):
        guardrails.append(
            ToolAllowlistGuardrail(allowed_tools=tool_cfg.get("allowed_tools", []))
        )

    input_cfg = guardrail_config.get("input_validation", {})
    if input_cfg.get("enabled", False):
        guardrails.append(
            InputValidationGuardrail(
                max_input_length=input_cfg.get("max_input_length", 1000),
                patterns_to_block=input_cfg.get("patterns_to_block", []),
            )
        )

    output_cfg = guardrail_config.get("output_filter", {})
    if output_cfg.get("enabled", False):
        guardrails.append(
            OutputFilterGuardrail(
                patterns_to_block=output_cfg.get("patterns_to_block", []),
            )
        )

    return guardrails
