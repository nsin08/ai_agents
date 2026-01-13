from __future__ import annotations

from _bootstrap import add_repo_src_to_path

add_repo_src_to_path()

from agent_labs.orchestrator import AgentContext


def main() -> None:
    context = AgentContext(goal="demo")
    for i in range(1, 8):
        context.add_history("user", f"message {i}")

    last_three = context.format_history(n=3)
    print("OK: history_last_3=")
    print(last_three)


if __name__ == "__main__":
    main()

