"""
Serialization utilities for context data.
"""

from __future__ import annotations

import json
from typing import Any, Dict


def to_json(data: Dict[str, Any], indent: int = 2) -> str:
    """Serialize data to JSON."""
    return json.dumps(data, indent=indent, sort_keys=True)


def from_json(payload: str) -> Dict[str, Any]:
    """Deserialize JSON payload."""
    return json.loads(payload)


def to_yaml(data: Dict[str, Any]) -> str:
    """Serialize data to YAML (requires PyYAML)."""
    try:
        import yaml
    except ImportError as exc:
        raise RuntimeError("PyYAML is required for YAML serialization") from exc
    return yaml.safe_dump(data, sort_keys=True)


def from_yaml(payload: str) -> Dict[str, Any]:
    """Deserialize YAML payload (requires PyYAML)."""
    try:
        import yaml
    except ImportError as exc:
        raise RuntimeError("PyYAML is required for YAML deserialization") from exc
    return yaml.safe_load(payload)
