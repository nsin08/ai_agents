from __future__ import annotations

from _bootstrap import add_repo_src_to_path

add_repo_src_to_path()

from agent_labs.memory import MemoryItem, MemoryManager


def main() -> None:
    manager = MemoryManager()

    manager.store_short(MemoryItem(content="short: last user asked about retries"))
    manager.store_long(MemoryItem(content="long: user prefers concise answers"), key="preference")
    manager.store_rag(MemoryItem(content="rag: docs say use exponential backoff"))

    snapshot = manager.observe(query="retries")

    print("OK: short_term_count=", len(snapshot["short_term"]))
    print("OK: long_term_count=", len(snapshot["long_term"]))
    print("OK: rag_count=", len(snapshot["rag"]))


if __name__ == "__main__":
    main()

