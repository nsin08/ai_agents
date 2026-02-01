# Multi-Channel Conversational Agent Platform — Architecture & Design Analysis

**Document ID**: ARCH-001  
**Status**: LOCKED (Ready for Implementation)  
**Last Updated**: 2026-02-01  
**Phase**: Planning (Before GitHub Issues)  
**Branch**: `feature/conversational-agent-bridge` (develop)

---

## Executive Summary

This document captures the **complete architecture design** for a **channel-agnostic, multi-tenant conversational agent platform** powered by local Ollama LLMs. The system supports WhatsApp (via Twilio), Telegram, Slack, and future channels with **zero cost for POC** and **~12 weeks to production-ready deployment** (31 stories).

**Key Principles**:
- ✅ Channel-agnostic core (adapters are pluggable)
- ✅ Framework-agnostic agent (can swap LangChain/LangGraph later)
- ✅ Production-grade safety (idempotency, concurrency, observability, fallbacks)
- ✅ 100% open-source, free software stack
- ✅ Incremental delivery (4-week MVP, then scale)

---

## 1. ARCHITECTURAL VISION

### 1.1 Problem Statement

Building a conversational AI agent that:
- Works across **multiple communication channels** (WhatsApp, Telegram, Slack, SMS, etc.)
- Avoids channel-specific coupling in the agent logic
- Runs **locally** with free open-source tools
- Handles **production concerns** (idempotency, concurrency, errors, observability)
- Scales from **single developer POC** → **multi-tenant SaaS**

### 1.2 High-Level Solution Architecture

**Three-Layer Design**:

```
┌─────────────────────────────────────────────────────────────────┐
│                    CHANNEL LAYER (Input)                         │
│    WhatsApp (Twilio) │ Telegram │ Slack │ Future Channels      │
└────────────────────────┬────────────────────────────────────────┘
                         │
         ┌───────────────┴───────────────┐
         ↓                               ↓
  [Message Adapters]         [Signature Validators]
  (Normalize format)          (Per-channel auth)
  - WhatsAppAdapter           - HMAC-SHA1 validation
  - TelegramAdapter           - Timestamp checks
  - SlackAdapter              - Replay protection
         │                               │
         └───────────────┬───────────────┘
                         ↓
              [ChannelMessage]
              (Canonical format)
                         ↓
       ┌─────────────────┴──────────────────┐
       ↓                                    ↓
[Webhook Router]                  [Observability & Correlation]
(HTTP /webhook/{ch})              (Logging, metrics, tracing)
       │                                    │
       └─────────────────┬──────────────────┘
                         ↓
    ┌────────────────────────────────────────────┐
    │   CORE AGENT LAYER (LLM-Agnostic)          │
    ├────────────────────────────────────────────┤
    │ 1. Agent Core Orchestrator                │
    │    - Receives ChannelMessage              │
    │    - Checks idempotency                   │
    │    - Acquires concurrency lock            │
    │                                           │
    │ 2. Conversation Storage ←──────────────┐  │
    │    - Query history by (channel, user)   │  │
    │    - Add message (with dedup)            │  │
    │    - Store (SQLite→Postgres)             │  │
    │                                           │
    │ 3. Context Engineering                   │  │
    │    - Build system prompt                 │  │
    │    - Truncate history to token limit     │  │
    │    - Summarize long conversations        │  │
    │                                           │
    │ 4. Agent Bridge (Ollama)                 │  │
    │    - Call LLM with context               │  │
    │    - Timeout handling (10s)              │  │
    │    - Circuit breaker on failures         │  │
    │                                           │
    │ 5. Safety Guardrails                     │  │
    │    - Keyword filtering                   │  │
    │    - Content validation                  │  │
    │    - Fallback responses                  │  │
    └────────────────────────────────────────────┘
                         ↓
       ┌─────────────────┴──────────────────┐
       ↓                                    ↓
[Message Senders]                  [Observability & Correlation]
(Format & send response)            (Logging, metrics, tracing)
- WhatsAppSender                    (Correlation IDs throughout)
- TelegramSender
- SlackSender
       │                                    │
       └─────────────────┬──────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                    CHANNEL LAYER (Output)                        │
│    WhatsApp (Twilio) │ Telegram │ Slack │ Future Channels      │
└─────────────────────────────────────────────────────────────────┘
```

**Key Insight**: Agent core is **completely channel-agnostic**. Adding a new channel requires only adapters + senders, zero changes to core logic.

### 1.3 Component Connection Map

| Component | Section | Diagram Layer | Connects To |
|-----------|---------|---------------|------------|
| **Webhook Router** | 2.1 | Input → Core | Adapters, Observability, Senders |
| **Message Adapters** | 2.2 | Input Layer | Webhook Router, ChannelMessage |
| **ChannelMessage** | 2.3 | Normalization | Adapters, Agent Core, Senders |
| **Conversation Storage** | 2.4 | Core → Persistence | Agent Core, Context Engineering |
| **Agent Core Orchestrator** | 2.5 | Core Heart | All other core components |
| **Agent Bridge (Ollama)** | 2.6 | Core → LLM | Agent Core, Context Engineering |
| **Context Engineering** | 2.7 | Core → History | Agent Core, Storage, Bridge |
| **Message Senders** | 2.8 | Core → Output | Webhook Router, Agent Core |
| **Observability** | 2.9 | Cross-cutting | Entire flow (logging + correlation) |
| **Safety Guardrails** | 2.10 | Core → Validation | Agent Core, before Bridge call |

---

## 2. CORE COMPONENTS & RESPONSIBILITIES

### 2.1 Webhook Router

**Purpose**: Entry point for all inbound messages

**Responsibilities**:
- Receives POST at `/webhook/{channel}`
- Routes to appropriate adapter by channel name
- Handles channel registration/availability checks
- Returns 200 OK or error responses with proper HTTP status

**Implementation**: FastAPI `APIRouter` with dependency injection

---

### 2.2 Message Adapter Interface (Abstract)

**Purpose**: Normalize all channel formats to canonical `ChannelMessage`

**Implementations**:
- `WhatsAppAdapter` (Twilio)
- `TelegramAdapter` (Bot API)
- `SlackAdapter` (Web API)
- Future: SMSAdapter, DiscordAdapter, etc.

**Responsibilities**:
1. Parse inbound webhook payload (JSON, form-data, etc.)
2. Validate signature/authentication:
   - Twilio: HMAC-SHA1 signature validation
   - Telegram: secret_token validation
   - Slack: signing_secret + timestamp validation
3. Replay protection:
   - Timestamp within 5 minutes of server time
   - Nonce/message_id tracking (last 1000 per channel)
4. Input validation:
   - Payload size limits (10MB WhatsApp, 256KB Telegram)
   - Content-Type validation
   - Schema sanity checks (required fields present)
   - Text length limits (4096 chars WhatsApp, vary per channel)
5. Extract and normalize:
   - sender_id (phone, user_id, composite)
   - text (user's message)
   - timestamp (provider's time, or server arrival)
   - external_msg_id (for deduplication)
   - metadata (channel-specific extras)

**Returns**: `ChannelMessage` (Pydantic model)

**Testing**: Golden payloads (real provider examples, edge cases like emoji, long text, special chars)

---

### 2.3 ChannelMessage (Canonical Format)

```python
class ChannelMessage(BaseModel):
    channel: str                          # whatsapp, telegram, slack, sms
    sender_id: str                        # phone, user_id, composite
    text: str                             # user's message
    timestamp: datetime                   # provider's timestamp (canonical)
    created_at: datetime                  # when created
    received_at: datetime                 # when server received
    processed_at: Optional[datetime]      # when agent processed (null until processed)
    external_msg_id: str                  # provider's ID (MessageSid, message_id, ts, etc.)
    metadata: Dict[str, Any] = {}         # channel-specific extras (group_id, thread_ts, etc.)
    correlation_id: Optional[str]         # trace ID for logging (set by webhook router)
```

**Key Insight**: All messages, regardless of origin, are normalized to this single format. Agent core never sees channel-specific fields.

---

### 2.4 Conversation Storage Interface (Abstract)

**Purpose**: Persist & retrieve conversation history with idempotency & concurrency guarantees

**Schema** (SQLite Phase 1, Postgres Phase 2+):

```sql
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY,
    channel VARCHAR(50),                    -- whatsapp, telegram, slack
    sender_id VARCHAR(255),                 -- phone, user_id, composite
    timestamp DATETIME,                     -- canonical timestamp (from provider)
    created_at DATETIME DEFAULT CURRENT,
    received_at DATETIME,
    processed_at DATETIME,
    role VARCHAR(20),                       -- user | assistant
    message_text TEXT,
    external_msg_id VARCHAR(255) UNIQUE,   -- provider's ID, prevents dupes
    system_prompt_version INT,              -- for regression debugging
    
    -- Concurrency control
    version INT DEFAULT 1,                  -- for optimistic locking (future)
    
    UNIQUE(channel, external_msg_id),       -- idempotency guarantee
    INDEX(channel, sender_id, timestamp),   -- for history retrieval
    FOREIGN KEY...                          -- (future) user account linking
);
```

**Responsibilities**:
1. `get_history(channel: str, sender_id: str, limit: int) → List[dict]`
   - Retrieve conversation history ordered by timestamp
   - Respects idempotency (no duplicates by external_msg_id)
2. `add_message(msg: ChannelMessage, role: str, text: str) → id`
   - Store message atomically
   - Prevent duplicate processing (external_msg_id uniqueness)
   - Return message ID for tracking
3. `get_context(channel: str, sender_id: str) → str`
   - Return formatted history for agent (system prompt + recent messages)
   - Respects token limits (see Context Engineering)

**Concurrency Safety**:
- Phase 1: Pessimistic row-level lock (simpler for POC)
- Phase 2: Optionally migrate to optimistic versioning
- Tests: 5 concurrent messages for same user → serialize correctly

**Idempotency**:
- `external_msg_id` UNIQUE constraint prevents duplicate inserts
- Query by `external_msg_id` before storing (if exists, skip)
- Guarantees: each message processed exactly once, in order

---

### 2.5 Agent Core Orchestrator

**Purpose**: Channel-agnostic reasoning loop

**Responsibilities**:
1. Receive `ChannelMessage` from webhook
2. Idempotency check: Query history for `external_msg_id`
   - If exists: already processed, skip (return cached response)
   - If new: proceed
3. Concurrency lock: Acquire row lock for (channel, sender_id)
4. Query conversation history:
   ```
   history = storage.get_context(channel, sender_id)
   ```
5. Build context for LLM:
   - System prompt (with version stored in DB)
   - Recent conversation history
   - Respects token limit (4K for Mistral 7B)
6. Call Ollama Bridge (async):
   ```python
   response = await ollama_bridge.generate(
       context=history,
       user_message=msg.text,
       timeout=10.0,
       correlation_id=msg.correlation_id
   )
   ```
7. Parse LLM response
8. Store conversation pair:
   - User message: role="user", text=msg.text
   - Assistant response: role="assistant", text=response.text
9. Release lock
10. Return response text to webhook for sending

**Key Properties**:
- **Zero channel coupling**: Never checks `msg.channel` (except for history query)
- **Async-first**: All I/O (DB, Ollama, logging) is async/await
- **Observable**: Emits correlation_id, logs all transitions
- **Resilient**: Handles Ollama timeouts, DB failures with fallbacks

---

### 2.6 Agent Bridge (Ollama Interface)

**Purpose**: Async, testable contract to local LLM

**Request**:
```python
class AgentBridgeRequest(BaseModel):
    context: str                    # system prompt + history
    user_message: str               # latest message from user
    model: str = "mistral:7b"
    timeout: float = 10.0           # seconds (max 30s)
    correlation_id: str             # for tracing
```

**Response**:
```python
class AgentBridgeResponse(BaseModel):
    response_text: str              # LLM's answer
    tokens_used: int                # prompt + completion tokens
    latency_ms: float               # roundtrip time
    status: Literal["success", "timeout", "error"]
    error_msg: Optional[str]        # if status != "success"
```

**Responsibilities**:
1. Format request for Ollama API (POST /api/generate)
2. Call Ollama with timeout handling
3. Parse response, extract text
4. Measure latency
5. Handle errors:
   - Timeout (10s) → return fallback response
   - Connection error → retry up to 3 times (exponential backoff: 1s, 2s, 4s)
   - Circuit breaker: if 3 consecutive failures, return fallback for 5 min

**Circuit Breaker**:
- Tracks failure count per model
- When failures ≥ 3: return fallback immediately for 5 min
- After 5 min: attempt recovery (reset counter)
- Logged & metricated (alerts if open)

**Fallback Response**:
```
"I'm processing your message, please give me a moment..."
```

**Testing**: Mock Ollama responses (deterministic for CI)

---

### 2.7 Context Engineering

**Purpose**: Build conversation context respecting token limits

**Responsibilities**:

1. **System Prompt**:
   - Define base personality ("You are a helpful assistant...")
   - Version control (stored in DB for regression debugging)
   - Can be updated without breaking old conversations

2. **History Retrieval**:
   - Query recent N messages: `storage.get_history(channel, sender_id, limit=50)`
   - Format as: `role: text` pairs
   - Ordered by timestamp (oldest first)

3. **Token Counting**:
   - Count tokens in system_prompt + history
   - Model: Mistral 7B → 4K token context window
   - Formula: roughly 4 chars = 1 token (conservative)
   - Enforce: total_tokens < 4000

4. **Truncation Policy**:
   - If history exceeds token limit: remove oldest messages first
   - Preserve most recent context (freshest conversation)
   - Fallback: if very old message critical, summarize (see Summarization)

5. **Summarization** (Long Conversations):
   - When message_count > 50 AND tokens > 80% of window
   - Call Ollama to summarize oldest 30 messages: "Summary: user discussed X, Y, Z. Key context: [summary]"
   - Replace oldest messages with summary in history
   - Cache summary (don't re-summarize)
   - Enables unlimited conversation history (user sees all, agent sees summary + recent)

**Example Context**:
```
System: You are a helpful WhatsApp assistant. Keep responses concise (max 3 sentences).

History:
User: What's the weather?
Assistant: I don't have real-time weather data. Try checking weather.com.
User: Thanks, how about tomorrow?
Assistant: I'd recommend checking a weather app for forecasts.
User: OK, tell me a joke instead.
Assistant: [response]

[Next user message will be appended here for LLM]
```

---

### 2.8 Message Sender Interface (Abstract)

**Purpose**: Send responses back via channel APIs

**Implementations**:
- `WhatsAppSender` (Twilio)
- `TelegramSender` (Bot API)
- `SlackSender` (Web API)
- Future: SMSSender, DiscordSender, etc.

**Response Contract**:
```python
class SenderResponse(BaseModel):
    external_msg_id: Optional[str]              # provider's ID (or null if failed)
    status: Literal["success", "queued", "failed", "invalid_recipient"]
    provider_error_code: Optional[str]          # e.g., "21202" (invalid phone)
    provider_error_msg: Optional[str]           # human-readable error
    retry_policy: Literal["immediate", "exponential", "do_not_retry"]
    raw_metadata: Dict[str, Any]                # full provider response for audit
```

**Responsibilities**:
1. Format response for channel API:
   - WhatsApp: `{To: phone, From: twilio_number, Body: text}`
   - Telegram: `{chat_id: user_id, text: response_text}`
   - Slack: `{channel: channel_id, text: response_text}`
2. Validate recipient:
   - Twilio: validate phone number format
   - Telegram: validate user_id exists
   - Slack: validate channel ID exists
3. Call channel API with auth
4. Handle rate limits:
   - If rate-limited (429): queue for retry
   - Backoff: 1s, 2s, 4s, 8s, max 5 retries
5. Parse provider response:
   - Extract external_msg_id (proof of delivery)
   - Capture error codes (for auditing & alerts)
6. Return `SenderResponse` with full details

**Outbound Queue** (Phase 2):
- If send fails: queue message for retry
- Retry schedule: 1s, 2s, 4s, 8s (exponential backoff)
- Max queue depth: 1000 messages per channel
- Persistent queue: written to DB or Redis (for Phase 3)

**Testing**: Mock channel APIs (deterministic responses)

---

### 2.9 Observability & Correlation

**Purpose**: Trace entire message flow for debugging

**Correlation ID**:
- Generated at webhook entry (UUID)
- Propagated through async context (Python contextvars)
- Included in every log, metric, DB record

**Logging**:
- Structured JSON format: `{timestamp, level, correlation_id, component, message, context}`
- Secret masking: any value matching credential pattern is masked
- Example:
  ```json
  {
    "timestamp": "2026-02-01T10:30:45.123Z",
    "correlation_id": "abc-123-def",
    "component": "WhatsAppAdapter",
    "level": "INFO",
    "message": "Webhook received",
    "channel": "whatsapp",
    "sender_id": "+1234567890",
    "event": "adapter_parse_start"
  }
  ```

**Metrics**:
- Inbound message rate (msgs/min per channel)
- Response latency: p50, p95, p99 (milliseconds)
- Ollama success rate (%)
- Error rate by type (adapter error, bridge timeout, sender failure, etc.)
- Queue depth (outbound messages pending retry)

**Tracing**:
- Tail logs: `grep "correlation_id=abc-123" logs.json` shows entire message flow
- Dashboard: message volume, latency heatmap, error rate chart
- Alerts: if error rate > 5% for 5 min → page on-call

---

### 2.10 Safety Guardrails

**Purpose**: Prevent unsafe/off-topic LLM responses

**Guardrail Rules**:
- Reject requests for passwords, credentials, secrets
- Reject requests for illegal activity
- Reject requests for malware, hacking, etc.
- Block attempts to manipulate agent (e.g., "ignore previous instructions")

**Implementation**:
1. Keyword filtering: simple regex patterns for known bad words
2. (Optional, Phase 2+) Content moderation API (e.g., OpenAI moderation endpoint, optional paid)

**On Violation**:
- Log violation (message, rule triggered, sender)
- Return fallback: "I'm not able to help with that. Can I assist with something else?"
- DO NOT send to Ollama
- Alert: if violation rate > 10/hour → investigate

---

## 3. DATA FLOW EXAMPLE (WhatsApp)

```
User sends WhatsApp message "Hello, how are you?"
    ↓
Twilio webhook → POST /webhook/whatsapp with form-data
    (From=+1234567890, Body="Hello, how are you?", MessageSid=SMxxxxxx)
    ↓
Webhook Router:
  - Extracts channel="whatsapp"
  - Generates correlation_id="abc-123-def"
  - Routes to WhatsAppAdapter
    ↓
WhatsAppAdapter:
  - Validates HMAC-SHA1 signature ✓
  - Validates timestamp (within 5 min) ✓
  - Checks replay (MessageSid not in last 1000) ✓
  - Extracts: sender_id="+1234567890", text="Hello, how are you?"
  - Creates ChannelMessage(channel="whatsapp", sender_id="+1234567890", ...)
    ↓
Webhook Router:
  - Calls Agent Core with ChannelMessage
    ↓
Agent Core:
  1. Check idempotency: SELECT * FROM conversations WHERE external_msg_id="SMxxxxxx"
     → Not found, proceed
  2. Acquire row lock: LOCK TABLE conversations WHERE channel="whatsapp" AND sender_id="+1234567890"
  3. Query history: storage.get_context("whatsapp", "+1234567890")
     → Returns: system_prompt + last 10 messages (~2000 tokens)
  4. Call Ollama Bridge:
     context = "You are a helpful WhatsApp assistant...\nUser: Hello...\nAssistant:..."
     response = await ollama_bridge.generate(context, "Hello, how are you?", timeout=10s)
     → response_text="Hi there! How can I help you today?"
  5. Store messages:
     INSERT conversations (channel, sender_id, role, text, external_msg_id, ...)
     VALUES ("whatsapp", "+1234567890", "user", "Hello, how are you?", "SMxxxxxx", ...)
     INSERT conversations (channel, sender_id, role, text, external_msg_id, ...)
     VALUES ("whatsapp", "+1234567890", "assistant", "Hi there! How can I help you today?", "auto-generated", ...)
  6. Release lock
  7. Return: "Hi there! How can I help you today?"
    ↓
Webhook Router:
  - Passes response to WhatsAppSender
    ↓
WhatsAppSender:
  - Formats: {To: "+1234567890", From: TWILIO_NUMBER, Body: "Hi there! How can I help you today?"}
  - Calls Twilio API: POST /Messages
  - Returns: SenderResponse(external_msg_id="SMyyyyy", status="success", ...)
    ↓
Webhook Router:
  - Returns HTTP 200 OK to Twilio
    ↓
User receives WhatsApp message: "Hi there! How can I help you today?"
```

**Correlation ID Trail**:
```
Webhook: correlation_id=abc-123-def, event="webhook_start"
Adapter: correlation_id=abc-123-def, event="adapter_parse_start"
Adapter: correlation_id=abc-123-def, event="adapter_signature_valid"
Agent: correlation_id=abc-123-def, event="agent_history_query"
Agent: correlation_id=abc-123-def, event="agent_bridge_call_start"
Bridge: correlation_id=abc-123-def, event="ollama_request_sent"
Bridge: correlation_id=abc-123-def, event="ollama_response_received", latency_ms=2500
Agent: correlation_id=abc-123-def, event="agent_message_stored"
Sender: correlation_id=abc-123-def, event="sender_api_call"
Sender: correlation_id=abc-123-def, event="sender_success", external_msg_id="SMyyyyy"
Webhook: correlation_id=abc-123-def, event="webhook_end", total_latency_ms=3200
```

**Single grep finds entire flow**: `grep "correlation_id=abc-123-def" logs.json`

---

## 4. KEY ARCHITECTURAL DECISIONS (LOCKED)

| # | Decision | Choice | Rationale | Alternatives Rejected |
|---|----------|--------|-----------|----------------------|
| **1** | **Web Framework** | FastAPI | Async-native, Pydantic built-in, auto-docs | Flask (sync-first), Django (overkill) |
| **2** | **Tunnel Tool (Phase 1)** | Cloudflare Tunnel | Free tier unlimited, stable, simple | ngrok (free tier limited, noisy) |
| **3** | **LLM Provider & Model** | Ollama + Mistral 7B | CPU-friendly, free, good reasoning | Cloud APIs (paid), GPT (cost), local LLaMA (slower) |
| **4** | **Context Window Size** | 4K tokens (4,096) | Mistral 7B efficient, covers ~1000 msg chars history | 8K (slower on CPU), 2K (truncates too much) |
| **5** | **Phase 1→2 DB Scale Path** | SQLite → PostgreSQL | SQLite free for dev, Postgres free for scale, self-hostable | MongoDB (overkill), DynamoDB (pay), Firebase (vendor lock) |

**All decisions locked. Ready for implementation.**

---

## 5. RISK MITIGATION SUMMARY

| Risk | Mitigation Stories | Status |
|------|-------------------|--------|
| **Idempotency + Ordering** | Stories #18 (idempotency), #26 (ordering tests) | ✅ Addressed |
| **Concurrency Race Conditions** | Story #19 (row-level locks), tests with 5 concurrent msgs | ✅ Addressed |
| **Backpressure & Message Loss** | Story #20 (outbound queue), #21 (fallback response) | ✅ Addressed |
| **Observability for Debugging** | Story #14 (correlation IDs), structured JSON logging | ✅ Addressed |
| **Adapter Input Validation** | Story #6 (payload size, content-type, schema checks) | ✅ Addressed |
| **Replay Attacks** | Story #6 (timestamp + nonce validation) | ✅ Addressed |
| **Context Token Overflow** | Story #11 (token limit enforcement), #22 (summarization) | ✅ Addressed |
| **Guardrails & Safety** | Story #24 (keyword filtering, fallback responses) | ✅ Addressed |
| **Multi-Channel Identity** | Story #31 (schema for future account linking) | ✅ Addressed |
| **Data Retention & GDPR** | Story #29 (TTL, deletion, export APIs) | ✅ Addressed |
| **Secret Leakage** | Story #14 (secret masking), #28 (rotation plan) | ✅ Addressed |
| **Ollama Unavailability** | Story #21 (circuit breaker, fallback response) | ✅ Addressed |
| **Horizontal Scaling** | Story #25 (Postgres connection pooling) | ✅ Addressed |
| **Golden Payload Testing** | Story #6, #17 (adapter golden payloads) | ✅ Addressed |
| **Failure Scenarios** | Story #26 (simulate Ollama down, DB error, API failures) | ✅ Addressed |

**All identified risks have mitigation stories assigned.**

---

## 6. PHASE-BY-PHASE DELIVERY (CONSOLIDATED: 12 Stories, 6 Weeks)

### **Phase 1: MVP — WhatsApp Agent (5 stories, ~12 days, 2.5 weeks)**

**Delivers**: Fully functional WhatsApp conversational agent on your laptop

| Story # | Title | Scope | Est. Days | Acceptance Criteria |
|---------|-------|-------|-----------|-------------------|
| **1** | **Architecture & Setup** | Twilio sandbox, Cloudflare tunnel, FastAPI scaffold, .env config, decisions locked | 2 | ✅ Tunnel active, Twilio sandbox ready, FastAPI runs on localhost, all 5 decisions documented |
| **2** | **WhatsApp Adapter + Storage** | Twilio webhook parsing (signature validation, schema checks, golden payloads), SQLite schema with idempotency & ordering, CRUD ops (add_message, get_history, dedup) | 3 | ✅ Parse Twilio payloads (normal, emoji, long text), store in SQLite, idempotency by external_msg_id works, correlation IDs in logs |
| **3** | **Agent Core Orchestrator** | Receive ChannelMessage, query history, call Ollama (mocked), store messages, return response text (zero channel coupling) | 3 | ✅ End-to-end flow works: webhook → adapter → agent → storage → sender; channel-agnostic verified |
| **4** | **Context Engineering + Logging** | System prompt definition, 4K token limit enforcement, history truncation, structured JSON logging with correlation IDs throughout | 2 | ✅ Token limits respected, logs show correlation_id at every step (adapter→agent→storage→sender), old messages excluded from context |
| **5** | **E2E Test: WhatsApp Loop** | Send 3 test messages, verify responses appear in chat, verify history stored correctly, verify correlation IDs trace entire flow | 2 | ✅ Send message via Twilio Sandbox → get response within 3s → history queryable → logs show end-to-end trace |

**Phase 1 Total: 5 stories, ~12 days** ✅ **Working WhatsApp agent (local dev)**

---

### **Phase 1.5: Prove Multi-Channel Abstraction (1 story, ~2 days, 0.5 weeks)**

**Delivers**: Multi-channel support proven, adapters are truly pluggable

| Story # | Title | Scope | Est. Days | Acceptance Criteria |
|---------|-------|-------|-----------|-------------------|
| **6** | **Telegram Adapter + E2E** | TelegramAdapter (parse JSON, validate secret_token, extract user_id), TelegramSender (call Bot API), multi-turn test, verify history isolation from WhatsApp | 2 | ✅ Send Telegram message → get response; separate history from WhatsApp; same agent core used (zero changes to Story 3); correlation IDs trace flow |

**Phase 1.5 Total: 1 story, ~2 days** ✅ **Multi-channel works, agent core untouched**

---

### **Phase 2: Hardening + Scaling (4 stories, ~11 days, 2.5 weeks)**

**Delivers**: Production-ready, handles errors gracefully, scales horizontally

| Story # | Title | Scope | Est. Days | Acceptance Criteria |
|---------|-------|-------|-----------|-------------------|
| **7** | **Idempotency + Concurrency** | Enforce external_msg_id uniqueness (prevents duplicate processing), row-level pessimistic lock (prevents message interleaving), ordering by timestamp (not arrival order), simulate 5 concurrent messages for same user | 3 | ✅ Send same message 2x → stored once, response sent both times; 5 concurrent messages → processed in correct timestamp order; no history corruption |
| **8** | **Resilience + Backpressure** | Outbound message queue (in-memory for Phase 2), exponential backoff retries (1s, 2s, 4s, 8s, max 5), Ollama timeout handling with fallback response, circuit breaker (3 failures → return fallback 5 min), simulate Ollama down + DB error | 3 | ✅ Ollama timeout → user gets fallback within 2s; Twilio API error → message queued & retried; circuit breaker activates & recovery logs shown; no message loss |
| **9** | **Safety + Context Management** | Guardrail rules (reject passwords, illegal activity), keyword filtering, summarization for long conversations (>50 msgs), system prompt versioning (for regression), prompt version stored in DB | 2 | ✅ Guardrail test triggers & returns fallback (not sent to Ollama); 100-message convo fits 4K token window via summarization; old conversations reload with original prompt version |
| **10** | **Postgres + Monitoring** | Provision Postgres (local or AWS free tier), schema migration script (SQLite → Postgres), connection pooling (pgbouncer), metrics emission (inbound rate, latency p50/p95, error rate), dashboard/alerts setup (basic: print to stdout or file) | 3 | ✅ Webhook server scaled to 3 instances, all connect to Postgres; metrics show message rate, latency heatmap, error rate; alerts if error rate >5%; migration reversible |

**Phase 2 Total: 4 stories, ~11 days** ✅ **Production-ready, error handling, scaling proof**

---

### **Phase 3: Compliance + Deployment (2 stories, ~4 days, 1 week)**

**Delivers**: Deployable to cloud, compliant with regulations, future-proof

| Story # | Title | Scope | Est. Days | Acceptance Criteria |
|---------|-------|-------|-----------|-------------------|
| **11** | **GDPR + Secrets Management** | Data retention policy (TTL: 90 days free users, 1 year paid), scheduled deletion job, GDPR right-to-deletion API (delete all messages for user), data export API (download as JSON), secret masking in logs, secret rotation plan (runbook), account linking schema prep (future Phase 4) | 2 | ✅ Retention job runs daily, old messages deleted; export API returns user data; GDPR deletion API removes all traces; secrets not in logs; rotation runbook documented |
| **12** | **Public Deployment** | Docker Compose (webhook + Ollama + Postgres), deployment guide (AWS EC2 free tier or DigitalOcean), HTTPS via Cloudflare Tunnel, monitoring dashboards (or alerting integration), tested on live cloud instance | 2 | ✅ Docker Compose spins up full stack; deployed to cloud; HTTPS works; messages flow end-to-end; monitoring accessible; documentation for hand-off |

**Phase 3 Total: 2 stories, ~4 days** ✅ **Production deployed, compliant, future-ready**

---

## Summary: 12-Story Breakdown

| Phase | Stories | Duration | Team | Deliverable |
|-------|---------|----------|------|-------------|
| **Phase 1** | 5 | 2.5 weeks | 1 dev | ✅ Working WhatsApp agent (local) |
| **Phase 1.5** | 1 | 0.5 weeks | 1 dev | ✅ Multi-channel (Telegram added, abstraction proven) |
| **Phase 2** | 4 | 2.5 weeks | 1 dev | ✅ Production-ready (errors, scaling, monitoring) |
| **Phase 3** | 2 | 1 week | 1 dev | ✅ Deployed, compliant, future-proof |
| **TOTAL** | **12** | **6 weeks** | 1 full-time | ✅ Fully operational, ready for users |

**Alternative Staffing**:
- 2 devs: ~4-5 weeks (parallel work on adapters, storage, bridge)
- 1 part-time dev (20h/week): ~12 weeks

---

## 7. COST ANALYSIS (POC)

### **Phase 1 + 1.5 (Weeks 1-6): $0**

| Item | Cost | Notes |
|------|------|-------|
| Python, FastAPI, Pydantic | $0 | Open-source |
| Twilio Sandbox | $0 | Free forever, no time limit |
| Telegram Bot API | $0 | Completely free |
| Ollama (CPU-based) | $0 | Runs on your machine |
| SQLite | $0 | Embedded in Python |
| Cloudflare Tunnel | $0 | Free tier unlimited |
| GitHub | $0 | Public repo or free private tier |
| Your laptop/server | Your existing hardware | No additional cost |
| **TOTAL** | **$0** | Completely free POC |

---

### **Phase 2 (Weeks 7-10): $0 (Self-Hosted)**

| Item | Cost | Notes |
|------|------|-------|
| PostgreSQL | $0 | Open-source, self-hosted on your machine |
| Docker | $0 | Docker Desktop free for personal use |
| Monitoring (optional) | $0 | Free tools (CloudWatch free tier if on AWS) |
| **TOTAL** | **$0** | Still free |

---

### **Phase 3 (Weeks 11-12): $0-50/month (If Cloud)**

| Item | Cost | Notes |
|------|------|-------|
| Twilio Sandbox → Production | ~$0.005-0.01 per message | Pay-per-message (small cost once live) |
| Cloud Hosting | $0-30/month | AWS free tier (12 mo), DigitalOcean ($5-10/mo), Heroku (deprecated), self-hosted free |
| Managed Postgres (optional) | $0-20/month | AWS RDS free tier (12 mo), DigitalOcean ($15/mo), self-hosted free |
| Monitoring (optional) | $0-20/month | CloudWatch free tier (AWS), Datadog ($0 startup tier) |
| **TOTAL** | **$0-50/month** | Depends on deployment choices |

**For POC (Phases 1-2): $0 guaranteed.**

---

## 8. STACK SUMMARY (All Open-Source, All Free)

| Category | Component | License | Cost | Notes |
|----------|-----------|---------|------|-------|
| **Language** | Python 3.11+ | PSF | $0 | Free, open-source |
| **Web Framework** | FastAPI | MIT | $0 | Async, Pydantic integration |
| **Validation** | Pydantic | MIT | $0 | Data model validation |
| **Async Runtime** | asyncio (stdlib) | PSF | $0 | Built into Python |
| **Database (Phase 1)** | SQLite | Public Domain | $0 | Embedded in Python |
| **Database (Phase 2)** | PostgreSQL | PostgreSQL License | $0 | Self-hosted or cloud free tier |
| **LLM Engine** | Ollama | MIT | $0 | Local inference |
| **LLM Model** | Mistral 7B | Apache 2.0 | $0 | Open-weights, community supported |
| **WhatsApp API** | Twilio SDK | Apache 2.0 | $0 Sandbox, $$ Prod | Free sandbox, pay-per-message production |
| **Telegram API** | python-telegram-bot | MIT | $0 | Free bot API |
| **Slack API** | Slack Web API | Official | $0 Free tier | Free tier covers POC |
| **Tunnel** | Cloudflare Tunnel | Proprietary | $0 Free tier | Free tier unlimited for POC |
| **Container** | Docker | Moby (OSS) + Docker Desktop | $0 Personal | Free for personal use |
| **Testing** | pytest | MIT | $0 | Standard Python testing |
| **Async Testing** | pytest-asyncio | Apache 2.0 | $0 | Async test support |
| **VCS** | GitHub | Proprietary | $0 Free tier | Free public/private repos |
| **CI/CD** | GitHub Actions | Proprietary | $0 Free tier | 2000 min/mo free |

**Total Cost for POC: $0**

---

## 7. IMPLEMENTATION TIMELINE (CONSOLIDATED)

| Phase | Stories | Duration | Team | Deliverable |
|-------|---------|----------|------|-------------|
| **Phase 1** | 5 | 2.5 weeks | 1 dev | ✅ Working WhatsApp agent (local) |
| **Phase 1.5** | 1 | 0.5 weeks | 1 dev | ✅ Multi-channel (Telegram added, abstraction proven) |
| **Phase 2** | 4 | 2.5 weeks | 1 dev | ✅ Production-ready (errors, scaling, monitoring) |
| **Phase 3** | 2 | 1 week | 1 dev | ✅ Deployed, compliant, future-proof |
| **TOTAL** | **12** | **6 weeks** | 1 full-time | ✅ Fully operational, ready for users |

**Alternative Staffing**:
- 2 devs: ~4-5 weeks (parallel work on adapters, storage, bridge)
- 1 part-time dev (20h/week): ~12 weeks

---

## 10. ADDING NEW CHANNELS (After MVP)

**With this architecture, adding a new channel is simple**:

### **Add Slack (Example)**

```
Story A: SlackAdapter
  - Parse Slack webhook JSON
  - Validate signing_secret
  - Extract user_id, text, ts
  - Return ChannelMessage (same contract as WhatsApp)
  - Est: 2 days

Story B: SlackSender
  - Call Slack Web API (/chat.postMessage)
  - Format message with channel_id
  - Handle rate limits
  - Return SenderResponse (same contract)
  - Est: 2 days

Story C: E2E Test (Slack)
  - Send test message via Slack bot
  - Verify response in chat
  - Verify separate history from WhatsApp/Telegram
  - Est: 1 day
```

**Total: 5 days, 0 changes to agent core**

**Compare to traditional approach:**
- Without abstraction: Each new channel requires changes to agent logic, message routing, storage schema, response formatting
- With abstraction: Plugin in new adapters + senders, done

---

## 11. FUTURE ROADMAP (Beyond Phase 3)

### **Phase 4: Multi-Tenant Account Linking**
- Link same user across channels (WhatsApp + Telegram = 1 user)
- Unified conversation history (if user requests)
- Per-channel conversation preferences (different tone for different channels)

### **Phase 5: Advanced LLM Features**
- Swap LangChain/LangGraph in (architecture allows this, agent is framework-agnostic)
- Add tool calling (calculator, web search, database queries)
- Add memory systems (RAG, long-term memory)
- Multi-turn planning + verification loops

### **Phase 6: Scaling & SaaS**
- Multi-tenant isolation
- Per-tenant LLM models
- Usage-based billing
- Custom guardrails per tenant

---

## 12. QUESTIONS FOR IMPLEMENTATION TEAM

Before starting Phase 1, confirm:

1. ✅ **Architecture makes sense?** (Channel adapters, agent core, senders)
2. ✅ **Tech stack approved?** (FastAPI, Ollama, Postgres, all free & open-source)
3. ✅ **5 decisions locked?** (Mistral 7B, 4K tokens, Cloudflare Tunnel, Twilio Sandbox, Postgres)
4. ✅ **12 stories realistic?** (6 weeks for 1 full-time dev, proportional to Issue #58)
5. ✅ **Risk mitigations acceptable?** (Idempotency, concurrency, observability, fallbacks)
6. ✅ **POC cost understood?** ($0 guaranteed for Phases 1-2, $0-50/month for Phase 3)
7. ✅ **Consolidated scope acceptable?** (5 stories per phase reduces over-engineering)

---

## 13. DOCUMENT REFERENCES

- **Architecture Diagram**: Section 1.2
- **Component Descriptions**: Section 2
- **Data Flow Example**: Section 3
- **Locked Decisions**: Section 4
- **Risk Mitigations**: Section 5
- **Story Breakdown**: Section 6
- **Cost Analysis**: Section 7
- **Implementation Timeline**: Section 9
- **Extending with New Channels**: Section 10

---

## 14. REVISION HISTORY

| Date | Version | Author | Change |
|------|---------|--------|--------|
| 2026-02-01 | 1.0 | Copilot | Initial architecture analysis (31 stories, 3 phases, all risks addressed) |

---

## APPROVAL CHECKLIST

**To proceed with GitHub issue creation**:

- [ ] Architecture approved
- [ ] Tech stack approved
- [ ] 5 decisions locked
- [ ] Risk mitigations acceptable
- [ ] Cost analysis understood ($0 POC)
- [ ] 31-story plan realistic
- [ ] Ready to create EPIC-1 + stories

**Once all approved: Create GitHub issues following space_framework format.**

---

**Document Status**: LOCKED & READY FOR IMPLEMENTATION  
**Next Step**: Create GitHub EPIC-1 + 31 Story issues
