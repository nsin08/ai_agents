# Chapter 05: Multi-Turn Conversations

[Prev](chapter_04_observability.md) | [Up](README.md) | [Next](chapter_06_integration_patterns.md)

---

## Learning Objectives

After completing this chapter, you will be able to:

1. **Design Conversation Flows** — Structure multi-turn interactions with clear state transitions
2. **Manage Conversation State** — Track context, goals, and progress across turns
3. **Implement Context Preservation** — Maintain relevant history without exceeding token limits
4. **Handle Conversation Repair** — Recover from misunderstandings and clarify ambiguous requests
5. **Build Session Persistence** — Save and restore conversations across sessions

---

## Introduction

Single-turn interactions are simple: user asks, agent answers. But real-world agents operate in *multi-turn* conversations where context accumulates, goals evolve, and the agent must track what was said three exchanges ago.

This chapter teaches you to design agents that feel like they're having a coherent conversation, not a series of disconnected Q&A exchanges.

**Key Insight:** Multi-turn conversations require explicit state management. The LLM has no memory between calls—your agent must provide the context that creates the illusion of continuity.

---

## 1. Anatomy of Multi-Turn Conversations

### 1.1 Turn Structure

```
┌─────────────────────────────────────────────────────────────────────┐
│                   MULTI-TURN CONVERSATION FLOW                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Turn 1: User initiates                                              │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  User: "I want to book a flight to Seattle"                  │   │
│  │  Agent: "Sure! When would you like to travel?"               │   │
│  │  → State: {goal: flight_booking, destination: Seattle}       │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                              ↓                                       │
│  Turn 2: User provides detail                                        │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  User: "Next Friday"                                         │   │
│  │  Agent: "One-way or round trip?"                             │   │
│  │  → State: {..., date: next_friday, awaiting: trip_type}      │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                              ↓                                       │
│  Turn 3: User provides more detail                                   │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  User: "Round trip, returning Sunday"                        │   │
│  │  Agent: "Found 5 options. Here are the top 3..."             │   │
│  │  → State: {..., trip_type: round_trip, return: sunday}       │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                              ↓                                       │
│  Turn 4: Goal achieved                                               │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  User: "Book the second option"                              │   │
│  │  Agent: "Booked! Confirmation #ABC123"                       │   │
│  │  → State: {status: completed, confirmation: ABC123}          │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.2 What Changes Between Turns

| Component | Turn 1 | Turn 2 | Turn 3 |
|-----------|--------|--------|--------|
| **History** | Empty | 2 messages | 4 messages |
| **State** | Initialized | Partial | Complete |
| **Context tokens** | ~50 | ~150 | ~300 |
| **Available actions** | Ask clarifying questions | Search, ask more | Execute, confirm |

---

## 2. Conversation State Management

### 2.1 Conversation State Model

```python
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum

class ConversationStatus(str, Enum):
    ACTIVE = "active"
    WAITING_USER = "waiting_user"
    COMPLETED = "completed"
    ABANDONED = "abandoned"

@dataclass
class Message:
    """A single message in the conversation."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
        }

@dataclass
class ConversationState:
    """Tracks state across a multi-turn conversation."""
    
    session_id: str
    messages: List[Message] = field(default_factory=list)
    goal: Optional[str] = None
    slots: Dict[str, Any] = field(default_factory=dict)  # Collected info
    status: ConversationStatus = ConversationStatus.ACTIVE
    turn_count: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)

    def add_message(self, role: str, content: str, **metadata) -> None:
        """Add a message to conversation history."""
        self.messages.append(Message(
            role=role,
            content=content,
            metadata=metadata
        ))
        self.last_activity = datetime.utcnow()
        if role == "user":
            self.turn_count += 1

    def get_history_for_llm(self, max_messages: int = 10) -> List[Dict[str, str]]:
        """Get recent history formatted for LLM input."""
        recent = self.messages[-max_messages:]
        return [{"role": m.role, "content": m.content} for m in recent]

    def set_slot(self, name: str, value: Any) -> None:
        """Set a slot value (collected information)."""
        self.slots[name] = value

    def get_slot(self, name: str, default: Any = None) -> Any:
        """Get a slot value."""
        return self.slots.get(name, default)

    def is_slot_filled(self, name: str) -> bool:
        """Check if a slot has been filled."""
        return name in self.slots and self.slots[name] is not None
```

### 2.2 Slot Filling Pattern

Many conversations follow a slot-filling pattern where the agent collects required information:

```python
@dataclass
class SlotDefinition:
    """Definition of a slot to fill."""
    name: str
    required: bool = True
    prompt: str = ""  # Question to ask if missing
    validator: Optional[callable] = None

class SlotFillingAgent:
    """Agent that fills slots through conversation."""

    def __init__(self, slots: List[SlotDefinition]):
        self.slot_definitions = {s.name: s for s in slots}
        self.state = ConversationState(session_id="demo")

    def get_missing_slots(self) -> List[SlotDefinition]:
        """Get list of unfilled required slots."""
        missing = []
        for name, defn in self.slot_definitions.items():
            if defn.required and not self.state.is_slot_filled(name):
                missing.append(defn)
        return missing

    def extract_slots_from_message(self, message: str) -> Dict[str, Any]:
        """Extract slot values from user message (simplified)."""
        extracted = {}
        
        # Example: Extract date
        if "friday" in message.lower():
            extracted["date"] = "next_friday"
        if "sunday" in message.lower():
            extracted["return_date"] = "next_sunday"
        
        # Example: Extract trip type
        if "round trip" in message.lower():
            extracted["trip_type"] = "round_trip"
        elif "one way" in message.lower():
            extracted["trip_type"] = "one_way"
        
        return extracted

    def process_turn(self, user_message: str) -> str:
        """Process a user turn and return agent response."""
        self.state.add_message("user", user_message)
        
        # Extract any slot values from message
        extracted = self.extract_slots_from_message(user_message)
        for name, value in extracted.items():
            if name in self.slot_definitions:
                self.state.set_slot(name, value)
        
        # Check for missing required slots
        missing = self.get_missing_slots()
        
        if missing:
            # Ask for next missing slot
            next_slot = missing[0]
            response = next_slot.prompt
        else:
            # All slots filled - execute action
            response = self._execute_with_slots()
        
        self.state.add_message("assistant", response)
        return response

    def _execute_with_slots(self) -> str:
        """Execute action when all slots are filled."""
        return f"Booking flight with: {self.state.slots}"
```

### 2.3 Usage Example

```python
# Define slots for flight booking
flight_slots = [
    SlotDefinition("destination", required=True, 
                   prompt="Where would you like to fly to?"),
    SlotDefinition("date", required=True,
                   prompt="When would you like to travel?"),
    SlotDefinition("trip_type", required=True,
                   prompt="One-way or round trip?"),
    SlotDefinition("return_date", required=False,
                   prompt="When would you like to return?"),
]

agent = SlotFillingAgent(flight_slots)

# Turn 1
print(agent.process_turn("I want to book a flight to Seattle"))
# "When would you like to travel?"

# Turn 2
print(agent.process_turn("Next Friday, round trip"))
# "When would you like to return?"

# Turn 3
print(agent.process_turn("Sunday"))
# "Booking flight with: {destination: Seattle, date: next_friday, ...}"
```

---

## 3. History Management

### 3.1 History Strategies

```
┌─────────────────────────────────────────────────────────────────────┐
│                   HISTORY MANAGEMENT STRATEGIES                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Strategy 1: SLIDING WINDOW                                          │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  Keep last N messages (e.g., last 10)                        │   │
│  │  ✓ Simple, predictable token count                           │   │
│  │  ✗ May lose important early context                          │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  Strategy 2: SUMMARIZATION                                           │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  Summarize older messages, keep recent verbatim              │   │
│  │  ✓ Preserves context, controls tokens                        │   │
│  │  ✗ Summary may lose detail                                   │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  Strategy 3: IMPORTANCE-BASED                                        │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  Keep messages with high relevance scores                    │   │
│  │  ✓ Retains important info regardless of age                  │   │
│  │  ✗ Complex to implement, may miss continuity                 │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
│  Strategy 4: HYBRID (Recommended)                                    │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  Summary + Recent messages + Key facts                       │   │
│  │  ✓ Best of all approaches                                    │   │
│  │  ✗ More complex to implement                                 │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 Sliding Window Implementation

```python
class HistoryManager:
    """Manages conversation history with token limits."""

    def __init__(self, max_tokens: int = 2000, max_messages: int = 20):
        self.max_tokens = max_tokens
        self.max_messages = max_messages

    def estimate_tokens(self, text: str) -> int:
        """Rough token estimate (4 chars per token)."""
        return len(text) // 4

    def trim_history(self, messages: List[Message]) -> List[Message]:
        """Trim history to fit within limits."""
        # First: apply message limit
        if len(messages) > self.max_messages:
            messages = messages[-self.max_messages:]
        
        # Second: check token limit
        total_tokens = sum(self.estimate_tokens(m.content) for m in messages)
        
        while total_tokens > self.max_tokens and len(messages) > 2:
            # Remove oldest message (but keep system/first user message)
            removed = messages.pop(1)  # Index 1, preserve index 0
            total_tokens -= self.estimate_tokens(removed.content)
        
        return messages

    def get_context_window(
        self,
        messages: List[Message],
        current_query: str,
    ) -> List[Dict[str, str]]:
        """Build context window for LLM call."""
        trimmed = self.trim_history(messages.copy())
        
        result = [{"role": m.role, "content": m.content} for m in trimmed]
        result.append({"role": "user", "content": current_query})
        
        return result
```

### 3.3 Summarization Strategy

```python
from typing import List, Dict

class SummarizingHistoryManager:
    """History manager that summarizes older messages."""

    def __init__(
        self,
        max_tokens: int = 2000,
        recent_count: int = 4,
        summary_trigger: int = 10,
    ):
        self.max_tokens = max_tokens
        self.recent_count = recent_count
        self.summary_trigger = summary_trigger
        self._conversation_summary: str = ""

    async def update_summary(
        self,
        messages: List[Message],
        summarizer: callable,  # Async function to summarize
    ) -> None:
        """Update conversation summary if needed."""
        if len(messages) < self.summary_trigger:
            return
        
        # Summarize older messages
        older = messages[:-self.recent_count]
        older_text = "\n".join(f"{m.role}: {m.content}" for m in older)
        
        self._conversation_summary = await summarizer(older_text)

    def build_context(self, messages: List[Message]) -> List[Dict[str, str]]:
        """Build context with summary + recent messages."""
        context = []
        
        # Add summary if exists
        if self._conversation_summary:
            context.append({
                "role": "system",
                "content": f"Previous conversation summary: {self._conversation_summary}"
            })
        
        # Add recent messages
        recent = messages[-self.recent_count:]
        for msg in recent:
            context.append({"role": msg.role, "content": msg.content})
        
        return context
```

---

## 4. Conversation Flow Control

### 4.1 Flow State Machine

```python
from enum import Enum, auto
from typing import Optional, Dict, Any

class FlowState(Enum):
    """States in a conversation flow."""
    GREETING = auto()
    GATHERING_INFO = auto()
    CONFIRMING = auto()
    EXECUTING = auto()
    COMPLETED = auto()
    ERROR = auto()

class ConversationFlow:
    """State machine for conversation flow control."""

    TRANSITIONS = {
        FlowState.GREETING: [FlowState.GATHERING_INFO],
        FlowState.GATHERING_INFO: [FlowState.CONFIRMING, FlowState.GATHERING_INFO],
        FlowState.CONFIRMING: [FlowState.EXECUTING, FlowState.GATHERING_INFO],
        FlowState.EXECUTING: [FlowState.COMPLETED, FlowState.ERROR],
        FlowState.COMPLETED: [],  # Terminal
        FlowState.ERROR: [FlowState.GATHERING_INFO, FlowState.COMPLETED],
    }

    def __init__(self):
        self.state = FlowState.GREETING
        self.state_data: Dict[str, Any] = {}

    def can_transition(self, to_state: FlowState) -> bool:
        """Check if transition is valid."""
        return to_state in self.TRANSITIONS.get(self.state, [])

    def transition(self, to_state: FlowState) -> bool:
        """Attempt state transition."""
        if not self.can_transition(to_state):
            return False
        self.state = to_state
        return True

    def get_available_actions(self) -> List[str]:
        """Get actions available in current state."""
        actions = {
            FlowState.GREETING: ["greet", "identify_intent"],
            FlowState.GATHERING_INFO: ["ask_question", "validate_input"],
            FlowState.CONFIRMING: ["show_summary", "request_confirmation"],
            FlowState.EXECUTING: ["call_api", "process_request"],
            FlowState.COMPLETED: ["show_result", "offer_followup"],
            FlowState.ERROR: ["apologize", "offer_retry", "escalate"],
        }
        return actions.get(self.state, [])
```

### 4.2 Intent Detection and Routing

```python
class IntentRouter:
    """Routes conversation based on detected intent."""

    INTENT_PATTERNS = {
        "book_flight": ["book", "flight", "fly", "travel"],
        "check_status": ["status", "where", "tracking", "check"],
        "cancel": ["cancel", "refund", "stop"],
        "help": ["help", "how", "what can"],
    }

    def detect_intent(self, message: str) -> Optional[str]:
        """Detect intent from message (simplified)."""
        message_lower = message.lower()
        
        scores = {}
        for intent, keywords in self.INTENT_PATTERNS.items():
            score = sum(1 for kw in keywords if kw in message_lower)
            if score > 0:
                scores[intent] = score
        
        if not scores:
            return None
        
        return max(scores, key=scores.get)

    def get_handler(self, intent: str) -> callable:
        """Get handler for intent."""
        handlers = {
            "book_flight": self._handle_booking,
            "check_status": self._handle_status,
            "cancel": self._handle_cancel,
            "help": self._handle_help,
        }
        return handlers.get(intent, self._handle_unknown)

    def _handle_booking(self, state: ConversationState) -> str:
        state.goal = "book_flight"
        return "I can help you book a flight. Where would you like to go?"

    def _handle_status(self, state: ConversationState) -> str:
        return "I can check your booking status. What's your confirmation number?"

    def _handle_cancel(self, state: ConversationState) -> str:
        return "I can help with cancellation. What's your booking reference?"

    def _handle_help(self, state: ConversationState) -> str:
        return "I can help with: booking flights, checking status, and cancellations."

    def _handle_unknown(self, state: ConversationState) -> str:
        return "I'm not sure what you need. Could you rephrase that?"
```

---

## 5. Context Preservation Patterns

### 5.1 Reference Resolution

Conversations contain references like "it", "that", "the first one":

```python
class ReferenceResolver:
    """Resolves pronouns and references to concrete entities."""

    def __init__(self):
        self.entities: Dict[str, Any] = {}
        self.last_mentioned: List[str] = []

    def track_entity(self, entity_type: str, value: Any) -> None:
        """Track an entity mentioned in conversation."""
        key = f"{entity_type}:{value}"
        self.entities[key] = value
        self.last_mentioned.insert(0, key)
        self.last_mentioned = self.last_mentioned[:10]  # Keep last 10

    def resolve(self, reference: str) -> Optional[Any]:
        """Resolve a reference like 'it' or 'that one'."""
        reference_lower = reference.lower()
        
        # Handle "it", "that", "this"
        if reference_lower in ["it", "that", "this"]:
            if self.last_mentioned:
                key = self.last_mentioned[0]
                return self.entities.get(key)
        
        # Handle "the first/second one"
        if "first" in reference_lower and len(self.last_mentioned) >= 1:
            return self.entities.get(self.last_mentioned[0])
        if "second" in reference_lower and len(self.last_mentioned) >= 2:
            return self.entities.get(self.last_mentioned[1])
        
        return None

    def enrich_message(self, message: str) -> str:
        """Replace references with resolved values."""
        # Simplified - production would use NLP
        for ref in ["it", "that", "this"]:
            if ref in message.lower():
                resolved = self.resolve(ref)
                if resolved:
                    message = message.replace(ref, str(resolved))
        return message
```

### 5.2 Entity Persistence with Memory

Using Lab 4's memory agent for entity persistence:

```python
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class ConversationMemoryAgent:
    """Agent with memory for multi-turn conversations."""

    def __init__(self, max_short_term: int = 10):
        self.short_term: List[Dict[str, Any]] = []
        self.facts: Dict[str, Any] = {}
        self.max_short_term = max_short_term

    def add_turn(self, role: str, content: str) -> None:
        """Add conversation turn to short-term memory."""
        self.short_term.append({
            "role": role,
            "content": content,
        })
        
        # FIFO: Remove oldest if exceeding limit
        if len(self.short_term) > self.max_short_term:
            self.short_term.pop(0)

    def store_fact(self, key: str, value: Any, confidence: float = 1.0) -> None:
        """Store a fact in long-term memory."""
        self.facts[key] = {
            "value": value,
            "confidence": confidence,
        }

    def retrieve_relevant(self, query: str) -> Dict[str, Any]:
        """Retrieve relevant context for query."""
        # Get conversation history
        history = self.short_term[-5:]  # Last 5 turns
        
        # Get relevant facts
        query_terms = set(query.lower().split())
        relevant_facts = {}
        for key, fact in self.facts.items():
            if any(term in key.lower() for term in query_terms):
                relevant_facts[key] = fact
        
        return {
            "history": history,
            "facts": relevant_facts,
        }

    def build_context_prompt(self, query: str) -> str:
        """Build context prompt for LLM."""
        context = self.retrieve_relevant(query)
        
        parts = ["Previous conversation:"]
        for turn in context["history"]:
            parts.append(f"{turn['role']}: {turn['content']}")
        
        if context["facts"]:
            parts.append("\nKnown facts:")
            for key, fact in context["facts"].items():
                parts.append(f"- {key}: {fact['value']}")
        
        parts.append(f"\nCurrent query: {query}")
        
        return "\n".join(parts)
```

---

## 6. Conversation Repair

### 6.1 Handling Misunderstandings

```python
class ConversationRepair:
    """Handle and repair conversation breakdowns."""

    def detect_misunderstanding(self, user_message: str) -> bool:
        """Detect if user is expressing confusion."""
        indicators = [
            "no, i meant",
            "that's not what",
            "i said",
            "not that",
            "wrong",
            "mistake",
            "misunderstood",
            "let me clarify",
        ]
        message_lower = user_message.lower()
        return any(ind in message_lower for ind in indicators)

    def detect_frustration(self, user_message: str) -> bool:
        """Detect user frustration."""
        indicators = ["!!!", "???", "frustrated", "again", "already told"]
        message_lower = user_message.lower()
        return any(ind in message_lower for ind in indicators)

    def generate_clarification(self, context: ConversationState) -> str:
        """Generate clarification request."""
        last_user = None
        for msg in reversed(context.messages):
            if msg.role == "user":
                last_user = msg.content
                break
        
        return (f"I want to make sure I understand correctly. "
                f"You mentioned: '{last_user[:50]}...' "
                f"Could you tell me more about what you need?")

    def generate_apology(self, context: ConversationState) -> str:
        """Generate apology when repair needed."""
        return ("I apologize for the confusion. Let me start fresh. "
                "Could you tell me what you're trying to accomplish?")

    def handle_repair(
        self,
        user_message: str,
        context: ConversationState,
    ) -> str:
        """Handle conversation repair."""
        if self.detect_frustration(user_message):
            return self.generate_apology(context)
        elif self.detect_misunderstanding(user_message):
            return self.generate_clarification(context)
        else:
            return None  # No repair needed
```

### 6.2 Confirmation Patterns

```python
class ConfirmationHandler:
    """Handle confirmations before executing actions."""

    def request_confirmation(
        self,
        action: str,
        details: Dict[str, Any],
    ) -> str:
        """Generate confirmation request."""
        detail_lines = [f"  - {k}: {v}" for k, v in details.items()]
        return (
            f"I'm about to {action}:\n"
            + "\n".join(detail_lines)
            + "\n\nIs this correct? (yes/no)"
        )

    def parse_confirmation(self, message: str) -> Optional[bool]:
        """Parse user's confirmation response."""
        message_lower = message.lower().strip()
        
        positive = ["yes", "yeah", "yep", "correct", "right", "confirm", "ok", "sure"]
        negative = ["no", "nope", "wrong", "incorrect", "cancel", "stop"]
        
        if any(p in message_lower for p in positive):
            return True
        if any(n in message_lower for n in negative):
            return False
        
        return None  # Ambiguous
```

---

## 7. Session Persistence

### 7.1 Saving and Restoring Conversations

```python
import json
from pathlib import Path
from datetime import datetime

class SessionPersistence:
    """Persist conversation sessions to disk."""

    def __init__(self, storage_dir: str = "./sessions"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def save_session(self, state: ConversationState) -> str:
        """Save conversation state to file."""
        filepath = self.storage_dir / f"{state.session_id}.json"
        
        data = {
            "session_id": state.session_id,
            "goal": state.goal,
            "slots": state.slots,
            "status": state.status.value,
            "turn_count": state.turn_count,
            "created_at": state.created_at.isoformat(),
            "last_activity": state.last_activity.isoformat(),
            "messages": [m.to_dict() for m in state.messages],
        }
        
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        
        return str(filepath)

    def load_session(self, session_id: str) -> Optional[ConversationState]:
        """Load conversation state from file."""
        filepath = self.storage_dir / f"{session_id}.json"
        
        if not filepath.exists():
            return None
        
        with open(filepath) as f:
            data = json.load(f)
        
        state = ConversationState(session_id=data["session_id"])
        state.goal = data.get("goal")
        state.slots = data.get("slots", {})
        state.status = ConversationStatus(data.get("status", "active"))
        state.turn_count = data.get("turn_count", 0)
        state.created_at = datetime.fromisoformat(data["created_at"])
        state.last_activity = datetime.fromisoformat(data["last_activity"])
        
        for msg_data in data.get("messages", []):
            state.messages.append(Message(
                role=msg_data["role"],
                content=msg_data["content"],
                timestamp=datetime.fromisoformat(msg_data["timestamp"]),
            ))
        
        return state

    def resume_or_create(self, session_id: str) -> ConversationState:
        """Resume existing session or create new one."""
        state = self.load_session(session_id)
        if state:
            return state
        return ConversationState(session_id=session_id)
```

### 7.2 Session Timeout and Cleanup

```python
from datetime import timedelta

class SessionManager:
    """Manage session lifecycle."""

    def __init__(
        self,
        persistence: SessionPersistence,
        timeout: timedelta = timedelta(hours=24),
    ):
        self.persistence = persistence
        self.timeout = timeout
        self.active_sessions: Dict[str, ConversationState] = {}

    def get_session(self, session_id: str) -> ConversationState:
        """Get or create session."""
        if session_id in self.active_sessions:
            return self.active_sessions[session_id]
        
        state = self.persistence.resume_or_create(session_id)
        self.active_sessions[session_id] = state
        return state

    def is_expired(self, state: ConversationState) -> bool:
        """Check if session has expired."""
        return datetime.utcnow() - state.last_activity > self.timeout

    def cleanup_expired(self) -> int:
        """Remove expired sessions."""
        expired = [
            sid for sid, state in self.active_sessions.items()
            if self.is_expired(state)
        ]
        for sid in expired:
            del self.active_sessions[sid]
        return len(expired)

    def end_session(self, session_id: str) -> None:
        """End and persist session."""
        if session_id in self.active_sessions:
            state = self.active_sessions[session_id]
            state.status = ConversationStatus.COMPLETED
            self.persistence.save_session(state)
            del self.active_sessions[session_id]
```

---

## 8. Putting It Together

### 8.1 Complete Multi-Turn Agent

```python
class MultiTurnAgent:
    """Complete multi-turn conversation agent."""

    def __init__(self, session_id: str):
        self.state = ConversationState(session_id=session_id)
        self.flow = ConversationFlow()
        self.intent_router = IntentRouter()
        self.repair = ConversationRepair()
        self.history_manager = HistoryManager()
        self.reference_resolver = ReferenceResolver()

    async def process_message(self, user_message: str) -> str:
        """Process user message and generate response."""
        
        # 1. Check for conversation repair
        repair_response = self.repair.handle_repair(user_message, self.state)
        if repair_response:
            self.state.add_message("user", user_message)
            self.state.add_message("assistant", repair_response)
            return repair_response
        
        # 2. Resolve references
        enriched_message = self.reference_resolver.enrich_message(user_message)
        
        # 3. Add to history
        self.state.add_message("user", enriched_message)
        
        # 4. Detect intent (if not already established)
        if not self.state.goal:
            intent = self.intent_router.detect_intent(enriched_message)
            if intent:
                handler = self.intent_router.get_handler(intent)
                response = handler(self.state)
                self.flow.transition(FlowState.GATHERING_INFO)
            else:
                response = "How can I help you today?"
        else:
            # 5. Continue existing flow
            response = await self._continue_flow(enriched_message)
        
        # 6. Track entities and add response
        self.state.add_message("assistant", response)
        
        return response

    async def _continue_flow(self, message: str) -> str:
        """Continue existing conversation flow."""
        # Implementation depends on specific flow
        # This would call LLM with context
        context = self.history_manager.get_context_window(
            self.state.messages,
            message
        )
        
        # Call LLM (simplified)
        return f"Processing: {message} (slots: {self.state.slots})"
```

---

## Summary

### Key Takeaways

1. **Explicit state management** is required—LLMs have no inherent memory between calls.

2. **Slot filling** is a common pattern for collecting information across turns.

3. **History management** strategies (sliding window, summarization, hybrid) control token usage while preserving context.

4. **Flow state machines** ensure conversations progress through valid states.

5. **Conversation repair** handles misunderstandings and maintains user trust.

6. **Session persistence** enables conversations to span multiple interactions.

### What's Next

In Chapter 06, you'll learn about **Integration Patterns**—how to connect agents to external APIs, handle webhooks, and build event-driven agent architectures.

---

## References

- **Lab 4:** [labs/04/README.md](../../../labs/04/README.md) — Memory hands-on exercises
- **Memory Agent:** [labs/04/src/memory_agent.py](../../../labs/04/src/memory_agent.py)
- **Memory Manager:** [src/agent_labs/memory/manager.py](../../../src/agent_labs/memory/manager.py)
- **Context Templates:** [src/agent_labs/context/templates.py](../../../src/agent_labs/context/templates.py)

---

## Exercises

Complete these exercises in the workbook to reinforce your learning:

1. **Slot Filling Agent:** Implement a restaurant reservation agent that collects: party size, date, time, and dietary restrictions.

2. **History Summarization:** Implement the summarizing history manager and test with a 20-turn conversation. Compare context size.

3. **Conversation Repair:** Detect three types of misunderstandings (wrong entity, wrong intent, wrong action) and generate appropriate repair responses.

4. **Session Persistence:** Implement save/load for your slot-filling agent. Verify slots persist across restarts.

5. **Reference Resolution:** Extend the reference resolver to handle "the previous one", "both of them", and "neither".

---

[Prev](chapter_04_observability.md) | [Up](README.md) | [Next](chapter_06_integration_patterns.md)
