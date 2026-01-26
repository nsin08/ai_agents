"""Config loader for agent_core."""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional

from dotenv import load_dotenv

from .models import AgentCoreConfig


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    result = dict(base)
    for key, value in override.items():
        if (
            key in result
            and isinstance(result[key], dict)
            and isinstance(value, dict)
        ):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def _parse_env_value(value: str) -> Any:
    lowered = value.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    if lowered == "none":
        return None
    try:
        if "." in value:
            return float(value)
        return int(value)
    except ValueError:
        return value


def _set_nested(target: Dict[str, Any], keys: list[str], value: Any) -> None:
    current = target
    for key in keys[:-1]:
        current = current.setdefault(key, {})
    current[keys[-1]] = value


def _env_to_dict(prefix: str, environ: Dict[str, str]) -> Dict[str, Any]:
    data: Dict[str, Any] = {}
    for key, value in environ.items():
        if not key.startswith(prefix):
            continue
        path = key[len(prefix) :].strip("_")
        if not path:
            continue
        parts = path.split("__")
        parts = [p.lower() for p in parts if p]
        _set_nested(data, parts, _parse_env_value(value))
    return data


def _load_file(path: str) -> Dict[str, Any]:
    if path.lower().endswith(".json"):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    if path.lower().endswith((".yaml", ".yml")):
        try:
            import yaml
        except ImportError as exc:
            raise RuntimeError("PyYAML is required for YAML config files.") from exc
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    raise ValueError(f"Unsupported config file type: {path}")


def load_config(
    path: Optional[str] = None,
    overrides: Optional[Dict[str, Any]] = None,
    env_prefix: str = "AGENT_CORE_",
    load_dotenv_file: bool = True,
) -> AgentCoreConfig:
    if load_dotenv_file:
        load_dotenv()

    base = AgentCoreConfig().model_dump()

    data: Dict[str, Any] = {}
    if path is None:
        path = os.getenv(f"{env_prefix}CONFIG_PATH")
    if path:
        data = _load_file(path)

    env_data = _env_to_dict(env_prefix, os.environ)
    merged = _deep_merge(base, data)
    merged = _deep_merge(merged, env_data)
    if overrides:
        merged = _deep_merge(merged, overrides)

    config = AgentCoreConfig(**merged)
    config.validate_deterministic()
    return config
