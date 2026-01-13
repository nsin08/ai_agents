from __future__ import annotations

import asyncio

from _bootstrap import add_repo_src_to_path

add_repo_src_to_path()

from agent_labs.llm_providers import MockProvider
from agent_labs.orchestrator import (
    Agent,
    AgentContext,
    AgentState,
    VerificationResult,
    get_valid_transitions,
)


def always_complete(_context: AgentContext, _result: str) -> VerificationResult:
    return VerificationResult(is_complete=True, reason="demo", feedback="")


async def main() -> None:
    context = AgentContext(goal="demo")
    transitions = [s.value for s in get_valid_transitions(context.current_state)]
    print(f"OK: start_state={context.current_state.value}")
    print(f"OK: valid_transitions={transitions}")

    agent = Agent(provider=MockProvider(), verifier=always_complete)
    result = await agent.run(goal="Say hello in one sentence", max_turns=1)
    print(f"OK: agent_result_prefix={result.split(':', 1)[0]}")


if __name__ == "__main__":
    asyncio.run(main())

