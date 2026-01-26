# Short-Term Memory (Session Store)

This document describes the short-term session memory interface and the in-memory implementation.

## SessionStore interface

Session stores manage the current conversation context for a run. The interface is async-first:

```python
from typing import Protocol

class SessionStore(Protocol):
    async def add_message(self, role: str, content: str, **meta) -> None: ...
    async def get_context(self, max_tokens: int | None = None) -> list[dict[str, object]]: ...
    async def clear(self) -> None: ...
```

## InMemorySessionStore

The default backend stores messages in memory and truncates context deterministically using
an approximate token estimator (len/4).

```python
import asyncio

from agent_core.memory import InMemorySessionStore


async def main() -> None:
    store = InMemorySessionStore(max_tokens=200)
    await store.add_message("user", "Hello")
    await store.add_message("assistant", "Hi there!")
    context = await store.get_context()
    print(context)


asyncio.run(main())
```

## Notes

- Truncation drops the oldest messages first to stay within `max_tokens`.
- Messages include role, content, and optional tool metadata.
- The interface is designed to allow swapping in Redis or other backends later.
- Concurrent writes can interleave; ordering follows insertion sequence.
