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

### 1.2 Solution Architecture

**Three-Layer Design**:

```
┌─────────────────────────────────────────────────────────────────┐
│                    CHANNEL LAYER (Adapters)                     │
│    WhatsApp (Twilio) │ Telegram │ Slack │ Future Channels      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                    [Webhook Router]
                    (POST /webhook/{channel})
                         │
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│               CORE AGENT LAYER (LLM-Agnostic)                   │
│  - Message normalization (ChannelMessage)                       │
│  - Conversation history retrieval & context engineering        │
│  - LLM orchestration (Ollama bridge)                           │
│  - Safety guardrails & idempotency                            │
│  - Error handling & backpressure                              │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                 CHANNEL LAYER (Senders)                         │
│    WhatsApp (Twilio) │ Telegram │ Slack │ Future Channels      │
└─────────────────────────────────────────────────────────────────┘
```

**Key Insight**: Agent core is **completely channel-agnostic**. Adding a new channel requires only adapters + senders, zero changes to core logic.

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

## 6. PHASE-BY-PHASE DELIVERY

### **Phase 1: Local Dev Foundation (14 stories, ~20 days, 4 weeks)**

**Delivers**: Working WhatsApp agent on your laptop, POC quality

**Stories**:
1. Architecture & Decisions Lock
2. Twilio WhatsApp Sandbox Setup
3. Cloudflare Tunnel Infrastructure
4. FastAPI Webhook Router + Signature Validation
5. ChannelMessage Data Model
6. WhatsApp Adapter (Twilio) + Golden Payloads
7. SQLite Conversation Schema
8. Conversation Storage Interface
9. Agent Core Orchestrator
10. Ollama Bridge Contract
11. Context Engineering (History + Prompt)
12. WhatsApp Sender (Twilio API)
13. E2E Test: WhatsApp Local Loop
14. Environment Configuration + Logging

**Acceptance**: Send WhatsApp message → agent responds with Ollama answer → message stored in SQLite → correlation IDs in logs

---

### **Phase 1.5: Prove Abstraction (3 stories, ~8 days, 1.5 weeks)**

**Delivers**: Multi-channel support, proves abstraction pattern works

**Stories**:
15. Telegram Adapter + Sender (no core changes, pure plugin)
16. Multi-Channel History Isolation Tests
17. Telegram E2E Test

**Acceptance**: Send Telegram message → agent responds → separate history from WhatsApp → correlation IDs trace flow

---

### **Phase 2: Hardening + Scaling (10 stories, ~20 days, 4-5 weeks)**

**Delivers**: Production-ready, handles errors, scales to multi-instance

**Stories**:
18. Message Idempotency + Ordering
19. Concurrency Control (Row-Level Lock)
20. Outbound Queue + Exponential Backoff
21. Ollama Fallback + Circuit Breaker
22. Context Summarization (Long Conversations)
23. System Prompt Versioning
24. Safety Guardrails + Fallback Responses
25. Postgres Migration + Connection Pooling
26. Failure Scenario Tests
27. Metrics + Monitoring Dashboard

**Acceptance**: Ollama down → user gets fallback within 2s → message retried → metrics show incident → no data loss

---

### **Phase 3: Compliance + Future-Proof (4 stories, ~8 days, 2 weeks)**

**Delivers**: Deployable to cloud, compliant, future-proof

**Stories**:
28. Secret Rotation + Vault Plan
29. GDPR + Data Retention Policies
30. Public Deployment Plan (Docker Compose + Cloud)
31. Account Linking Preparation (Schema Extension)

**Acceptance**: Deploy to AWS EC2 free tier → messages work → GDPR deletion API works → secrets rotate without downtime

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

## 9. IMPLEMENTATION TIMELINE

| Phase | Stories | Duration | Team | Deliverable |
|-------|---------|----------|------|-------------|
| **Phase 1** | 14 | 4 weeks | 1 dev | ✅ Working WhatsApp agent (local) |
| **Phase 1.5** | 3 | 1.5 weeks | 1 dev | ✅ Multi-channel (Telegram added, abstraction proven) |
| **Phase 2** | 10 | 4-5 weeks | 1-2 devs | ✅ Production-ready (errors, scaling, monitoring) |
| **Phase 3** | 4 | 2 weeks | 1 dev | ✅ Deployed, compliant, future-proof |
| **TOTAL** | **31** | **12 weeks** | 1 full-time | ✅ Fully operational, ready for users |

**Alternative Staffing**:
- 2 devs: ~8-10 weeks (parallel work on adapters)
- 1 part-time dev (20h/week): ~30 weeks (careful scoping)

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
4. ✅ **31 stories realistic?** (12 weeks for 1 full-time dev)
5. ✅ **Risk mitigations acceptable?** (Idempotency, concurrency, observability, fallbacks)
6. ✅ **POC cost understood?** ($0 guaranteed for Phases 1-2, $0-50/month for Phase 3)
7. ✅ **Ready to create GitHub issues?** (EPIC-1 + 31 stories)

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
