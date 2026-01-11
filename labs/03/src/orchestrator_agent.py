"""
Orchestrator agent demonstrating Observe → Plan → Act → Verify → Refine loop.
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class StateLog:
    """A single state transition log entry."""

    state: str
    turn: int
    timestamp: str
    duration_ms: float
    data: Dict[str, Any]


class OrchestratorAgent:
    """
    Simple orchestrator illustrating a state machine for reasoning.
    Supports configurable max_turns and confidence-based early stopping.
    """

    def __init__(
        self,
        max_turns: int = 5,
        confidence_threshold: float = 0.95,
        clock: Optional[callable] = None,
    ) -> None:
        self.max_turns = max_turns
        self.confidence_threshold = confidence_threshold
        self.state_history: List[StateLog] = []
        self._clock = clock or time.perf_counter
        self.turn_count = 0
        self._last_time = self._clock()

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat(timespec="milliseconds")

    def _log_state(self, state: str, turn: int, data: Dict[str, Any]) -> None:
        now = self._clock()
        duration_ms = (now - self._last_time) * 1000.0
        self.state_history.append(
            StateLog(
                state=state,
                turn=turn,
                timestamp=self._now_iso(),
                duration_ms=duration_ms,
                data=data,
            )
        )
        self._last_time = now

    def observe(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        observation = {"query": query, "context": context}
        return observation

    def plan(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        query = observation["query"].lower()
        if "weather" in query:
            return {"action": "weather_lookup", "city": "Seattle", "expect": "weather"}
        if "%" in query or "shipping" in query or "plus" in query:
            return {"action": "multi_step_math", "steps": ["percentage", "addition"]}
        if any(op in query for op in ["+", "-", "*", "add"]):
            return {"action": "math", "expression": query}
        return {"action": "respond", "message": "I cannot find a suitable tool."}

    def _compute_math(self, expression: str) -> float:
        # Very small parser for demo purposes.
        if "15%" in expression and "234.50" in expression:
            return round(0.15 * 234.50 + 12.0, 2)
        if "2 + 2" in expression or "2+2" in expression:
            return 4
        if "impossible" in expression:
            raise ValueError("No valid math operation")
        # Fallback simple eval with safeties removed for brevity (demo only).
        cleaned = expression.replace("what is", "").replace("?", "").strip()
        try:
            return eval(cleaned)  # noqa: S307 (demo scope only)
        except Exception as exc:  # pragma: no cover - defensive
            raise ValueError(str(exc))

    def act(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        action = plan["action"]
        if action == "weather_lookup":
            return {
                "status": "success",
                "response": "Weather in Seattle: 20C and clear.",
                "confidence": 0.7,
            }
        if action == "math":
            result = self._compute_math(plan["expression"])
            return {
                "status": "success",
                "response": f"Computed result: {result}",
                "confidence": 0.7,
                "value": result,
            }
        if action == "multi_step_math":
            subtotal = round(0.15 * 234.50, 2)
            total = round(subtotal + 12.0, 2)
            return {
                "status": "success",
                "response": f"Subtotal {subtotal}, total with shipping {total}",
                "confidence": 0.8,
                "value": total,
            }
        return {
            "status": "failure",
            "response": plan.get("message", "Action not supported"),
            "confidence": 0.2,
        }

    def verify(self, action_result: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        if action_result["status"] != "success":
            return False, {"reason": "action_failed", "error": action_result["response"]}

        confidence = action_result.get("confidence", 0.0)
        if confidence >= self.confidence_threshold:
            return True, {"reason": "confidence_met", "confidence": confidence}

        # For math, if result present we can conclude success.
        if "value" in action_result:
            return True, {"reason": "value_available", "confidence": confidence}

        return False, {"reason": "continue", "confidence": confidence}

    def refine(self, verify_context: Dict[str, Any], previous_query: str) -> str:
        if verify_context.get("reason") == "action_failed":
            return "Provide a helpful message; unable to use the requested tool."
        return previous_query + " (please refine)"

    def run(self, query: str) -> str:
        context: Dict[str, Any] = {"confidence": 0.0}
        self._last_time = self._clock()
        for turn in range(1, self.max_turns + 1):
            self.turn_count = turn

            obs = self.observe(query, context)
            self._log_state("Observe", turn, obs)

            plan = self.plan(obs)
            self._log_state("Plan", turn, plan)

            action_result = self.act(plan)
            self._log_state("Act", turn, action_result)

            is_complete, verify_ctx = self.verify(action_result)
            self._log_state("Verify", turn, verify_ctx)

            if is_complete:
                return action_result["response"]

            query = self.refine(verify_ctx, query)
            self._log_state("Refine", turn, {"query": query, **verify_ctx})

        return "Max turns reached without completion."

    def get_state_history(self) -> List[StateLog]:
        return self.state_history


async def demo() -> None:
    agent = OrchestratorAgent(max_turns=5)
    for task in [
        "What's the weather in Seattle?",
        "What's 15% of $234.50 plus $12 shipping?",
        "Send email to user@example.com",
    ]:
        print(f"\n=== Task: {task}")
        result = agent.run(task)
        print(f"Result: {result}")
        print("Trace:")
        for entry in agent.get_state_history():
            print(
                f"  Turn {entry.turn} {entry.state} "
                f"@ {entry.timestamp} (+{entry.duration_ms:.1f}ms) "
                f"{entry.data}"
            )
        agent.state_history.clear()


if __name__ == "__main__":
    asyncio.run(demo())
