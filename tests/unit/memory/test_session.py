"""
Unit tests for session-based memory (SessionStore and InMemorySessionStore).
"""

from __future__ import annotations

import threading
import time
from datetime import datetime

import pytest

from src.agent_labs.memory import InMemorySessionStore, Message, SessionStore


def test_message_creation():
    """Test Message dataclass creation and serialization."""
    msg = Message(role="user", content="Hello", metadata={"source": "test"})

    assert msg.role == "user"
    assert msg.content == "Hello"
    assert msg.metadata["source"] == "test"
    assert isinstance(msg.timestamp, datetime)

    data = msg.to_dict()
    assert data["role"] == "user"
    assert data["content"] == "Hello"
    assert "timestamp" in data
    assert data["metadata"]["source"] == "test"


def test_in_memory_session_store_initialization():
    """Test InMemorySessionStore initialization."""
    store = InMemorySessionStore(max_turns=10)
    assert store._max_turns == 10
    assert len(store._messages) == 0


def test_in_memory_session_store_invalid_max_turns():
    """Test InMemorySessionStore rejects invalid max_turns."""
    with pytest.raises(ValueError, match="max_turns must be positive"):
        InMemorySessionStore(max_turns=0)

    with pytest.raises(ValueError, match="max_turns must be positive"):
        InMemorySessionStore(max_turns=-5)


def test_add_message():
    """Test adding messages to session store."""
    store = InMemorySessionStore(max_turns=10)

    store.add_message("user", "Hello")
    store.add_message("assistant", "Hi there!")
    store.add_message("system", "System prompt")

    messages = store._messages
    assert len(messages) == 3
    assert messages[0].role == "user"
    assert messages[0].content == "Hello"
    assert messages[1].role == "assistant"
    assert messages[1].content == "Hi there!"
    assert messages[2].role == "system"
    assert messages[2].content == "System prompt"


def test_add_message_with_metadata():
    """Test adding messages with metadata."""
    store = InMemorySessionStore()

    store.add_message("user", "Test", metadata={"key": "value"})
    messages = store._messages

    assert len(messages) == 1
    assert messages[0].metadata["key"] == "value"


def test_add_message_invalid_role():
    """Test that invalid roles are rejected."""
    store = InMemorySessionStore()

    with pytest.raises(ValueError, match="Invalid role"):
        store.add_message("invalid", "content")


def test_get_context_list_format():
    """Test getting context in list format."""
    store = InMemorySessionStore()

    store.add_message("user", "Question 1")
    store.add_message("assistant", "Answer 1")
    store.add_message("user", "Question 2")

    context = store.get_context(format="list")

    assert len(context) == 3
    assert context[0]["role"] == "user"
    assert context[0]["content"] == "Question 1"
    assert context[1]["role"] == "assistant"
    assert context[1]["content"] == "Answer 1"
    assert context[2]["role"] == "user"
    assert context[2]["content"] == "Question 2"


def test_get_context_string_format():
    """Test getting context in string format."""
    store = InMemorySessionStore()

    store.add_message("user", "Hello")
    store.add_message("assistant", "Hi!")

    context = store.get_context(format="string")

    assert "USER: Hello" in context
    assert "ASSISTANT: Hi!" in context
    assert context == "USER: Hello\nASSISTANT: Hi!"


def test_get_context_invalid_format():
    """Test that invalid formats are rejected."""
    store = InMemorySessionStore()

    with pytest.raises(ValueError, match="Invalid format"):
        store.get_context(format="invalid")


def test_clear():
    """Test clearing session store."""
    store = InMemorySessionStore()

    store.add_message("user", "Message 1")
    store.add_message("assistant", "Message 2")
    assert len(store._messages) == 2

    store.clear()
    assert len(store._messages) == 0

    context = store.get_context()
    assert len(context) == 0


def test_max_turns_enforcement():
    """Test that max_turns limit is enforced."""
    store = InMemorySessionStore(max_turns=2)  # 2 turns = 4 messages (2 user + 2 assistant)

    # Add 3 turns (6 messages)
    store.add_message("user", "Turn 1 user")
    store.add_message("assistant", "Turn 1 assistant")
    store.add_message("user", "Turn 2 user")
    store.add_message("assistant", "Turn 2 assistant")
    store.add_message("user", "Turn 3 user")
    store.add_message("assistant", "Turn 3 assistant")

    messages = store._messages
    # Should only keep last 2 turns (4 messages)
    assert len(messages) == 4

    # Should have kept only turns 2 and 3
    assert messages[0].content == "Turn 2 user"
    assert messages[1].content == "Turn 2 assistant"
    assert messages[2].content == "Turn 3 user"
    assert messages[3].content == "Turn 3 assistant"


def test_max_turns_preserves_system_messages():
    """Test that system messages are preserved when enforcing max_turns."""
    store = InMemorySessionStore(max_turns=1)  # 1 turn = 2 messages

    store.add_message("system", "System prompt")
    store.add_message("user", "Turn 1 user")
    store.add_message("assistant", "Turn 1 assistant")
    store.add_message("user", "Turn 2 user")
    store.add_message("assistant", "Turn 2 assistant")

    messages = store._messages

    # Should have system message + last turn (3 total)
    assert len(messages) == 3
    assert messages[0].role == "system"
    assert messages[0].content == "System prompt"
    assert messages[1].content == "Turn 2 user"
    assert messages[2].content == "Turn 2 assistant"


def test_get_token_count():
    """Test token counting (approximate)."""
    store = InMemorySessionStore()

    # Empty store
    assert store.get_token_count() == 0

    # Add messages
    store.add_message("user", "This is a test message")  # ~23 chars = ~5 tokens
    store.add_message("assistant", "This is a response")  # ~18 chars = ~4 tokens

    token_count = store.get_token_count()
    # Total: ~41 chars = ~10 tokens (41 // 4 = 10)
    assert token_count == 10


def test_thread_safety_concurrent_adds():
    """Test thread-safe concurrent message additions."""
    store = InMemorySessionStore(max_turns=100)
    num_threads = 10
    messages_per_thread = 20

    def add_messages(thread_id: int):
        for i in range(messages_per_thread):
            store.add_message("user", f"Thread {thread_id} message {i}")

    threads = []
    for i in range(num_threads):
        thread = threading.Thread(target=add_messages, args=(i,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    # Should have all messages
    assert len(store._messages) == num_threads * messages_per_thread


def test_thread_safety_concurrent_reads():
    """Test thread-safe concurrent reads."""
    store = InMemorySessionStore()
    store.add_message("user", "Test message")

    results = []

    def read_context():
        context = store.get_context()
        results.append(len(context))

    threads = []
    for _ in range(20):
        thread = threading.Thread(target=read_context)
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    # All reads should return same count
    assert all(count == 1 for count in results)


def test_thread_safety_mixed_operations():
    """Test thread-safe mixed read/write operations."""
    store = InMemorySessionStore(max_turns=50)

    def writer(thread_id: int):
        for i in range(10):
            store.add_message("user", f"Writer {thread_id} msg {i}")
            time.sleep(0.001)

    def reader():
        for _ in range(10):
            store.get_context()
            time.sleep(0.001)

    def clearer():
        time.sleep(0.01)
        store.clear()

    threads = []

    # Start writers
    for i in range(5):
        thread = threading.Thread(target=writer, args=(i,))
        threads.append(thread)
        thread.start()

    # Start readers
    for _ in range(3):
        thread = threading.Thread(target=reader)
        threads.append(thread)
        thread.start()

    # Start clearer
    thread = threading.Thread(target=clearer)
    threads.append(thread)
    thread.start()

    for thread in threads:
        thread.join()

    # Store should be in valid state (either has messages or was cleared)
    context = store.get_context()
    assert isinstance(context, list)


def test_session_store_is_abstract():
    """Test that SessionStore cannot be instantiated directly."""
    # SessionStore is an ABC, so it should not be instantiable
    with pytest.raises(TypeError):
        SessionStore()


def test_default_max_turns():
    """Test default max_turns value."""
    store = InMemorySessionStore()
    assert store._max_turns == 20  # Default value
