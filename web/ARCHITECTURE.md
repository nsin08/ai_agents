# Web Agent Chat Interface - Architecture

## Overview

The **Web Agent Chat Interface** is a multi-provider, full-stack AI agent chat application built with FastAPI (backend) and React 18 (frontend). It demonstrates seamless integration between multiple LLM providers and the agent orchestration core from `agent_labs`.

**Key Design Philosophy:** Backend abstraction via `ServiceInterface` Protocol enables zero-API-change swapping between `agent_labs` (Phase 1-3) and future `agent_core` (Phase B).

---

## Architecture Layers

### 1. Frontend (React 18 + TypeScript)

**Location:** `web/frontend/src/`

**Technology Stack:**
- React 18 with Hooks
- TypeScript (strict mode)
- React Testing Library
- CSS3 (Flexbox, Grid, Animations)

**Key Components:**

| Component | Purpose | Tests |
|-----------|---------|-------|
| `Chat.tsx` | Main chat interface, message display, input handling | `Chat.test.tsx` (8 cases) |
| `ProviderSelector.tsx` | Dropdown UI for provider/model selection | `ProviderSelector.test.tsx` (10 cases) |
| `APIKeyInput.tsx` | Secure API key input with validation | `APIKeyInput.test.tsx` (10 cases) |
| `SettingsDrawer.tsx` | Side panel for advanced configuration | (integrated in Chat) |

**Service Layer:**

```
services/
├── chatService.ts         # REST client for /api/chat endpoints
├── providerService.ts     # REST client for /api/providers endpoints
```

**Type System:**

```
types/
└── providers.ts           # All request/response interfaces
    ├── ProviderType enum (6 providers)
    ├── ChatRequest / ChatResponse
    ├── ProviderInfo / ProviderConfig
    └── ValidateKeyRequest / ValidateKeyResponse
```

---

### 2. Backend (FastAPI + Python 3.11+)

**Location:** `web/backend/`

**Technology Stack:**
- FastAPI (async-first)
- Python 3.11+
- Pydantic v2 (strict mode)
- agent_labs core (orchestration)

**API Routes:**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/chat/send` | POST | Send message, get agent response |
| `/api/chat/sessions` | POST | Create new session |
| `/api/chat/sessions/{id}` | GET | Get session history |
| `/api/providers` | GET | List available providers |
| `/api/providers/validate-key` | POST | Validate API key for provider |

**Key Modules:**

#### `models.py` - Pydantic Data Models

Defines strict request/response schemas with validation:

```python
class ChatRequest(BaseModel):
    message: str           # Required, non-empty
    provider: str          # Provider identifier
    model: str             # Model name
    api_key: Optional[str] # Override env var
    config: Dict[str, Any] # Agent config (max_turns, temp, etc.)

class ChatResponse(BaseModel):
    success: bool          # True if agent succeeded
    response: str          # Agent's reply text
    metadata: Dict[str, Any] # Latency, provider, error info
```

#### `services/interfaces.py` - Backend Abstraction

**Core Design Pattern:**

```python
class AgentServiceInterface(Protocol):
    """Abstraction layer for swappable backends"""
    async def process_message(
        message: str,
        provider: str,
        model: str,
        config: Dict[str, Any],
        api_key: Optional[str] = None
    ) -> ChatResponse: ...
```

**Why This Matters:**

- **Phase 1-3:** Implement with `AgentLabsService` using `agent_labs` core
- **Phase B:** Swap to `AgentCoreService` using `agent_core` (planned)
- **Zero Frontend Changes:** React UI never knows which backend is running
- **Environment Control:** Set `AGENT_CORE_BACKEND` env var to switch

**Benefits:**

1. **Production Safety:** Deploy with `agent_labs` while developing `agent_core`
2. **Testing Flexibility:** Mock service for unit tests, real service for integration
3. **Backward Compatibility:** New backend can be dropped in without API changes

#### `services/agent_labs_impl.py` - Phase 1-3 Implementation

Implements `AgentServiceInterface` using `agent_labs` orchestrator:

```python
class AgentLabsService(AgentServiceInterface):
    async def process_message(...) -> ChatResponse:
        # 1. Validate provider and convert to enum
        # 2. Create LLM provider using ProviderFactory
        # 3. Initialize Agent orchestrator
        # 4. Run full Observe → Plan → Act → Verify loop
        # 5. Return response with metadata (latency, tokens, etc.)
```

**Agent Orchestration Flow:**

```
User Message
    ↓
[Observe] Perceive input and context
    ↓
[Plan] Reason through goal and strategy
    ↓
[Act] Execute tools or generate response
    ↓
[Verify] Check if goal achieved
    ↓
Return Response
```

#### `services/provider_factory.py` - Provider Instantiation

Creates LLM provider instances from `agent_labs.llm_providers`:

```python
class ProviderFactory:
    @staticmethod
    def create_provider(
        provider_type: ProviderEnum,
        model: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None
    ) -> Provider:
        # Map ProviderEnum to agent_labs provider class
        # Pass API key override or read from env
        # Return configured provider instance
```

**Supported Providers (from agent_labs):**

| Provider | Requires Key | Type | Status |
|----------|-------------|------|--------|
| Mock | No | Deterministic | ✅ Available |
| Ollama | No | Local LLM | ✅ Available |
| OpenAI | Yes | Cloud LLM | ✅ Available |
| Anthropic | Yes | Cloud LLM | ✅ Available |
| Google | Yes | Cloud LLM | ⏳ Coming Soon |
| Azure OpenAI | Yes | Cloud LLM | ⏳ Coming Soon |

#### `api/chat.py` - Chat Endpoints

REST routes for chat operations with standardized error handling:

```python
@router.post("/send")
async def send_message(
    request: ChatRequest,
    service: AgentServiceInterface = Depends(agent_service)
) -> ChatResponse:
    """
    Process message through agent service.
    
    Error Handling:
    - 400 Bad Request: Validation errors (empty message, invalid config)
    - 401 Unauthorized: API key invalid or auth failed
    - 500 Internal Server Error: Unexpected errors
    - 504 Gateway Timeout: Agent took too long (timeout exceeded)
    """
```

**Error Response Format:**

All errors follow consistent structure:

```python
class ErrorResponse(BaseModel):
    success: bool = False      # Always False
    error: str                 # Error type (e.g., "Invalid provider")
    detail: Optional[str]      # Human-readable message
```

---

## Communication Protocol

### Request/Response Lifecycle

```
Frontend                          Backend
   │
   ├─ POST /api/chat/send ──────→ ChatRequest
   │                              (message, provider, model, config)
   │                              │
   │                              ├─ Validate input
   │                              ├─ Create LLM provider
   │                              ├─ Run agent orchestrator
   │                              │  (Observe → Plan → Act → Verify)
   │                              ├─ Format response
   │                              │
   ←─────────── ChatResponse ──────┤
      (success, response,
       metadata with latency)
   │
   └─ Display in UI
```

### Metadata Included in Response

```json
{
  "success": true,
  "response": "Agent's answer...",
  "metadata": {
    "provider": "ollama",
    "model": "mistral",
    "latency_ms": 2500,
    "max_turns": 3,
    "backend": "agent_labs"
  }
}
```

---

## Data Flow Patterns

### 1. Provider Selection

```
User selects provider
    ↓
[Frontend] Load available models for provider
    ↓
[Backend] GET /api/providers?include_models=true
    ↓
[Response] List of ProviderInfo with models
    ↓
User selects model
```

### 2. API Key Validation

```
User enters API key
    ↓
[Frontend] POST /api/providers/validate-key
    ├─ provider: ProviderType
    ├─ api_key: string
    └─ model: string (optional)
    ↓
[Backend] Try creating provider + query available models
    ↓
[Response] ValidateKeyResponse (valid, message, models_available)
```

### 3. Message Processing

```
User sends message
    ↓
[Frontend] POST /api/chat/send
    ├─ message: string
    ├─ provider: string
    ├─ model: string
    ├─ api_key: optional override
    └─ config: agent config
    ↓
[Backend] AgentLabsService.process_message()
    ├─ Create LLM provider
    ├─ Initialize Agent
    ├─ Run orchestrator (max_turns iterations)
    ├─ Catch errors → ChatResponse(success=false)
    └─ Return ChatResponse with metadata
    ↓
[Frontend] Display response + metadata
```

---

## Phase Roadmap

### Phase 1: MVP Foundation ✅
- **Status:** 70% complete (in cleanup phase)
- **Scope:** Basic chat UI, single provider, static model list
- **Phase 1 Cleanup (Current):**
  - ✅ ServiceInterface documentation
  - ✅ Error response standardization
  - ✅ CSS loading animations
  - ✅ Backend type hints verification
  - ✅ Frontend component tests (Chat, ProviderSelector, APIKeyInput)
  - ✅ Documentation (ARCHITECTURE.md, QUICK_START.md)

### Phase 2: Multi-Provider Support ✅
- **Status:** 100% merged
- **Scope:** 6 providers, API key validation, dynamic model selection
- **Features:** ProviderSelector component, API key input, provider info

### Phase 3: Debug Mode, Export & Polish (Not Started)
- **Status:** 0% - Planned
- **Scope:** Debug panel, reasoning chain export, dark mode, accessibility
- **Key Features:**
  - Debug panel showing Observe/Plan/Act/Verify states
  - Export conversation as JSON/Markdown
  - Dark mode toggle
  - a11y improvements (ARIA labels, keyboard nav)
  - Richer error messages with suggestions
  - Session persistence (localStorage)
  - Settings persistence

### Phase B: Agent Core Backend (Planned)
- **Status:** 0% - Future
- **Scope:** Swap `agent_labs` for `agent_core`
- **Change:** Only backend implementation changes; API stays identical

---

## Testing Strategy

### Backend Tests (19 tests, all passing)

**Unit Tests** (`tests/test_models.py` - 7 tests)
```python
test_chat_request_valid
test_chat_request_empty_message
test_chat_response_success
test_error_response
```

**API Tests** (`tests/test_api.py` - 8 tests)
```python
test_root                          # Health check
test_health                        # Server up
test_send_message_success          # Happy path
test_send_message_unsupported_provider  # Error case
test_send_message_empty             # Validation
test_create_session                 # Session mgmt
test_get_session                    # Session retrieval
```

**Service Tests** (`tests/test_services.py` - 4 tests)
```python
test_agent_labs_service_mock_provider
test_agent_labs_service_unsupported_provider
test_agent_labs_service_with_config
test_agent_labs_service_metadata
```

### Frontend Tests (28 tests, new in Phase 1 cleanup)

**Chat Component** (`src/components/Chat.test.tsx` - 8 tests)
```
✓ Renders chat component
✓ Loads providers on mount
✓ Sends message and displays response
✓ Shows loading state while sending
✓ Displays error message on failed response
✓ Prevents sending empty messages
✓ Scrolls to bottom on new messages
✓ Handles service errors gracefully
```

**ProviderSelector** (`src/components/ProviderSelector.test.tsx` - 10 tests)
```
✓ Renders provider selector
✓ Loads and displays providers
✓ Handles provider change
✓ Displays available models
✓ Handles model change
✓ Disables when disabled prop is true
✓ Shows coming soon providers as disabled
✓ Displays API key warning
✓ Handles loading state
✓ Handles error and allows retry
```

**APIKeyInput** (`src/components/APIKeyInput.test.tsx` - 10 tests)
```
✓ Renders nothing when not required
✓ Renders input when required
✓ Handles API key input
✓ Toggles visibility
✓ Validates API key
✓ Shows error for invalid key
✓ Shows error on validation failure
✓ Prevents validation with empty key
✓ Disables when disabled prop is true
✓ Clears validation when key changes
```

---

## Dependency Injection Pattern

### Backend (FastAPI)

**Config Module** (`config.py`):

```python
# Singleton agent service instance
agent_service = AgentLabsService()

# Dependency function for route injection
def get_agent_service() -> AgentServiceInterface:
    return agent_service

# In routes:
@router.post("/api/chat/send")
async def send_message(
    request: ChatRequest,
    service: AgentServiceInterface = Depends(get_agent_service)
) -> ChatResponse:
    ...
```

**Benefits:**

1. **Testability:** Inject mock service in tests
2. **Flexibility:** Swap provider factory without changing routes
3. **Type Safety:** Protocol ensures contract compliance

---

## Environment Configuration

### Backend Environment Variables

```bash
# LLM Provider Selection
LLM_PROVIDER=ollama                    # mock, ollama, openai, anthropic, google, azure-openai
LLM_MODEL=mistral                      # Model name

# API Keys (per provider)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
AZURE_OPENAI_API_KEY=...

# Local Ollama
OLLAMA_BASE_URL=http://localhost:11434

# Agent Configuration
AGENT_MAX_TURNS=3                      # Max iterations in Observe→Plan→Act→Verify
AGENT_TIMEOUT=30                       # Seconds before timeout

# Backend Selection (Phase B)
AGENT_CORE_BACKEND=agent_labs          # agent_labs or agent_core
```

### Frontend Environment Variables

```bash
# API Endpoint
REACT_APP_API_BASE_URL=http://localhost:8000

# Optional: Analytics, monitoring, etc.
REACT_APP_ENVIRONMENT=development
```

---

## Running Locally

### Backend

```bash
# Install dependencies
cd web/backend
pip install -r requirements.txt

# Run server
python main.py
# Starts on http://localhost:8000
# Docs: http://localhost:8000/docs
```

### Frontend

```bash
# Install dependencies
cd web/frontend
npm install

# Start development server
npm start
# Opens http://localhost:3000

# Run tests
npm test

# Build for production
npm run build
```

---

## Future Enhancements (Phase 3 & Beyond)

### Phase 3 Features
- [ ] Debug panel (state visualization)
- [ ] Export conversation (JSON/Markdown)
- [ ] Dark mode toggle
- [ ] Accessibility improvements (ARIA, keyboard nav)
- [ ] Rich error messages with suggestions
- [ ] Session persistence (localStorage)
- [ ] Settings persistence

### Phase B Features
- [ ] Swap backend from `agent_labs` → `agent_core` (zero API changes)
- [ ] Database persistence (PostgreSQL)
- [ ] User authentication
- [ ] Multi-session UI
- [ ] Conversation search and filtering
- [ ] Usage analytics and cost tracking
- [ ] Streaming responses (SSE/WebSocket)

---

## Key Design Decisions

### 1. ServiceInterface Protocol for Backend Abstraction

**Decision:** Use Python Protocol for backend swapping  
**Alternative:** Inheritance-based ABC  
**Reason:** Protocols are "structural typing" - more flexible, no circular deps  
**Benefit:** Enables zero-API-change backend replacement (Phase B)

### 2. REST API vs GraphQL

**Decision:** REST API  
**Reason:** Simplicity, cached responses, standard HTTP semantics  
**Future:** Consider GraphQL for Phase 3 (filtering, pagination)

### 3. In-Memory Session Storage (Phase 1)

**Decision:** Dict-based in `_sessions` (web/backend/api/chat.py)  
**Limitation:** Sessions lost on server restart  
**Phase 2:** Migrate to database (PostgreSQL)

### 4. Type-First Frontend

**Decision:** TypeScript strict mode, full interface definitions  
**Benefit:** Catches errors at compile time, better IDE support  
**Testing:** React Testing Library (user behavior, not implementation)

---

## References

- **Agent Labs Core:** [src/agent_labs/](../../src/agent_labs/)
- **Orchestrator:** [src/agent_labs/orchestrator.py](../../src/agent_labs/orchestrator.py)
- **LLM Providers:** [src/agent_labs/llm_providers/](../../src/agent_labs/llm_providers/)
- **Framework:** [GitHub: space_framework](https://github.com/nsin08/space_framework)

---

**Last Updated:** Phase 1 Cleanup  
**Maintainer:** AI Agents Team  
**License:** [See project LICENSE]
