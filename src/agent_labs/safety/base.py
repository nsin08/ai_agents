"""
Safety guardrail base abstractions.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


class SafetyViolation(RuntimeError):
    """Raised when a safety guardrail is violated."""


@dataclass
class GuardrailResult:
    """Result of a guardrail check."""

    allowed: bool
    reason: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    sanitized_output: Optional[str] = None


class Guardrail(ABC):
    """Abstract base class for safety guardrails."""

    name: str

    def __init__(self, enabled: bool = True) -> None:
        self.enabled = enabled

    @abstractmethod
    def check_input(self, text: str) -> GuardrailResult:
        raise NotImplementedError

    @abstractmethod
    def check_output(self, text: str) -> GuardrailResult:
        raise NotImplementedError

    @abstractmethod
    def check_tool(self, tool_name: str) -> GuardrailResult:
        raise NotImplementedError
