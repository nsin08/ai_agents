"""
Observable agent demonstrating structured logging, tracing, and metrics.
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class LLMResponse:
    text: str
    tokens: int
    requires_tool: bool = False
    tool_name: Optional[str] = None
    tool_args: Optional[Dict[str, Any]] = None


class ObservableAgent:
    """Simple agent instrumented with structured logs and metrics."""

    def __init__(
        self,
        max_turns: int = 5,
        log_level: str = "INFO",
        session_id: str = "demo-session",
    ) -> None:
        self.max_turns = max_turns
        self.session_id = session_id
        self.metrics = {
            "turns": 0,
            "llm_calls": 0,
            "tool_calls": 0,
            "total_time_ms": 0.0,
            "tokens_used": 0,
        }
        self.trace: List[Dict[str, Any]] = []
        self._timers: Dict[str, float] = {}
        self.logger = self._setup_logger(log_level)

    def _setup_logger(self, level: str) -> logging.Logger:
        logger = logging.getLogger(f"observable_agent.{self.session_id}")
        logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        logger.propagate = False

        json_formatter = logging.Formatter(
            '{"timestamp":"%(asctime)s","level":"%(levelname)s",'
            '"component":"%(name)s","message":%(message)s}'
        )
        text_formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
        )

        if not logger.handlers:
            console = logging.StreamHandler()
            console.setFormatter(text_formatter)
            logger.addHandler(console)
        self._json_formatter = json_formatter
        return logger

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat(timespec="milliseconds")

    def _start_timer(self, name: str) -> None:
        self._timers[name] = time.perf_counter()

    def _end_timer(self, name: str) -> float:
        start = self._timers.get(name)
        if start is None:
            return 0.0
        duration_ms = (time.perf_counter() - start) * 1000.0
        return duration_ms

    def log_event(self, event: str, level: str = "INFO", **data: Any) -> None:
        entry = {
            "timestamp": self._now(),
            "level": level.upper(),
            "event": event,
            "session_id": self.session_id,
            "data": data,
        }
        self.trace.append(entry)
        msg = json.dumps(entry)
        self.logger.log(getattr(logging, level.upper(), logging.INFO), msg)

    def _simulate_llm(self, query: str) -> LLMResponse:
        tokens = max(5, len(query.split()) * 3)
        if "tool" in query.lower():
            return LLMResponse(
                text="Calling calculator tool.",
                tokens=tokens,
                requires_tool=True,
                tool_name="calculator",
                tool_args={"operation": "add", "a": 2, "b": 3},
            )
        return LLMResponse(text="Here is the answer.", tokens=tokens)

    def _simulate_tool(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        if name == "calculator":
            op = args.get("operation", "add")
            a = args.get("a", 0)
            b = args.get("b", 0)
            result = a + b if op == "add" else None
            return {"status": "success", "result": result, "tool": name}
        return {"status": "failure", "error": "unknown tool", "tool": name}

    def run(self, query: str) -> str:
        self._start_timer("total")
        self.log_event("agent_started", query=query, max_turns=self.max_turns)

        result_text = ""
        for turn in range(1, self.max_turns + 1):
            self.metrics["turns"] += 1
            self.log_event("turn_started", turn=turn, query=query)

            # LLM step
            self._start_timer("llm")
            self.log_event("llm_request_sent", turn=turn, query=query)
            llm_response = self._simulate_llm(query)
            llm_time = self._end_timer("llm")
            self.metrics["llm_calls"] += 1
            self.metrics["tokens_used"] += llm_response.tokens
            self.log_event(
                "llm_response_received",
                turn=turn,
                duration_ms=llm_time,
                tokens=llm_response.tokens,
                text_preview=llm_response.text[:80],
            )

            # Tool step (optional)
            tool_time = None
            if llm_response.requires_tool and llm_response.tool_name:
                self._start_timer("tool")
                self.log_event(
                    "tool_call_initiated",
                    turn=turn,
                    tool=llm_response.tool_name,
                    args=llm_response.tool_args,
                )
                tool_result = self._simulate_tool(
                    llm_response.tool_name, llm_response.tool_args or {}
                )
                tool_time = self._end_timer("tool")
                self.metrics["tool_calls"] += 1
                self.log_event(
                    "tool_call_completed",
                    turn=turn,
                    tool=llm_response.tool_name,
                    duration_ms=tool_time,
                    success=tool_result.get("status") == "success",
                )
                result_text = json.dumps(tool_result)
            else:
                result_text = llm_response.text

            # Turn complete
            self.log_event(
                "turn_completed",
                turn=turn,
                llm_time_ms=llm_time,
                tool_time_ms=tool_time,
            )

            # For demo, stop after first successful turn.
            break

        total_time = self._end_timer("total")
        self.metrics["total_time_ms"] = total_time
        self.log_event(
            "agent_completed",
            metrics=self.metrics,
            total_time_ms=total_time,
            success=True,
        )
        return result_text

    def get_trace(self) -> List[Dict[str, Any]]:
        return self.trace

    def get_metrics(self) -> Dict[str, Any]:
        return self.metrics

    def export_trace(self, path: str) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"trace": self.trace, "metrics": self.metrics}, f, indent=2)
