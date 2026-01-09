"""
Safety checker that coordinates multiple guardrails.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

from .base import Guardrail, GuardrailResult, SafetyViolation


@dataclass
class SafetyChecker:
    """Coordinator for safety guardrails."""

    guardrails: List[Guardrail]

    def check_input(self, text: str) -> None:
        for guardrail in self._enabled_guardrails():
            result = guardrail.check_input(text)
            self._raise_if_violation(result, guardrail.name, "input")

    def check_tool(self, tool_name: str) -> None:
        for guardrail in self._enabled_guardrails():
            result = guardrail.check_tool(tool_name)
            self._raise_if_violation(result, guardrail.name, "tool")

    def check_output(self, text: str) -> str:
        sanitized = text
        for guardrail in self._enabled_guardrails():
            result = guardrail.check_output(sanitized)
            self._raise_if_violation(result, guardrail.name, "output")
            if result.sanitized_output is not None:
                sanitized = result.sanitized_output
        return sanitized

    def _enabled_guardrails(self) -> Iterable[Guardrail]:
        return [guardrail for guardrail in self.guardrails if guardrail.enabled]

    @staticmethod
    def _raise_if_violation(result: GuardrailResult, name: str, stage: str) -> None:
        if not result.allowed:
            raise SafetyViolation(
                f"Guardrail '{name}' blocked {stage}: {result.reason}"
            )
