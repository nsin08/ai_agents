#!/usr/bin/env python3
"""
Demo script for SessionStore and InMemorySessionStore.

Shows basic usage of the session-based conversation memory.
"""

from agent_labs.memory import InMemorySessionStore


def main():
    print("=== SessionStore Demo ===\n")

    # Create a session store
    print("Creating session store with max_turns=3...")
    session = InMemorySessionStore(max_turns=3)

    # Simulate a conversation
    print("\n--- Adding conversation messages ---")
    session.add_message("system", "You are a helpful assistant.")
    session.add_message("user", "What is Python?")
    session.add_message(
        "assistant",
        "Python is a high-level, interpreted programming language known for its simplicity and readability.",
    )
    session.add_message("user", "How do I install it?")
    session.add_message(
        "assistant",
        "You can download Python from python.org or use a package manager like apt, brew, or chocolatey.",
    )

    # Get context in list format
    print("\n--- Context (list format) ---")
    context_list = session.get_context(format="list")
    for i, msg in enumerate(context_list, 1):
        print(f"{i}. [{msg['role']}] {msg['content'][:60]}...")

    # Get context in string format
    print("\n--- Context (string format) ---")
    context_str = session.get_context(format="string")
    print(context_str)

    # Check token count
    print(f"\n--- Token count: ~{session.get_token_count()} tokens ---")

    # Add more messages to trigger max_turns enforcement
    print("\n--- Adding more messages (will trigger truncation) ---")
    session.add_message("user", "What are some Python frameworks?")
    session.add_message("assistant", "Popular frameworks include Django, Flask, FastAPI, and Pyramid.")
    session.add_message("user", "Tell me about Django.")
    session.add_message("assistant", "Django is a high-level Python web framework that encourages rapid development.")

    print("\n--- Context after truncation (should keep system + last 3 turns) ---")
    context_list = session.get_context(format="list")
    for i, msg in enumerate(context_list, 1):
        print(f"{i}. [{msg['role']}] {msg['content'][:60]}...")

    print(f"\nTotal messages: {len(context_list)}")
    print(f"Token count: ~{session.get_token_count()} tokens")

    # Clear session
    print("\n--- Clearing session ---")
    session.clear()
    print(f"Messages after clear: {len(session.get_context())}")

    print("\n=== Demo complete ===")


if __name__ == "__main__":
    main()
