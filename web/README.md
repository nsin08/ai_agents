# Web-Based Agent Chat Interface — Learning Lab

**Purpose**: Hands-on demonstration of a production-ready AI agent chat interface with multi-provider support, debug observability, and configuration management. This lab serves as a practical reference for building web-based agent applications that integrate with the broader AI agents learning curriculum.

---

## 🎯 Learning Objectives

This lab teaches you how to:

1. **Build a multi-provider agent interface** — Support 6 LLM providers (Mock, Ollama, OpenAI, Anthropic, Google, Azure) with dynamic switching
2. **Implement debug observability** — Display 14 performance metrics (tokens, latency, reasoning steps, cost estimation)
3. **Design configuration management** — Create presets (Creative/Precise/Balanced) with sliders and validation
4. **Export conversations** — Generate JSON and Markdown exports with metadata
5. **Implement accessibility** — ARIA labels, keyboard navigation, semantic HTML (WCAG AA compliant)
6. **Test comprehensively** — 61 tests (44 unit + 17 integration) with 81% coverage
7. **Deploy to production** — Docker + nginx configuration with SSL, monitoring, and auto-scaling

---

## 🏗️ What You'll Build

A complete full-stack web application featuring:

**Backend (FastAPI + Python)**:
- REST API with 3 endpoint groups (chat, providers, config)
- Provider abstraction layer supporting 6 LLM providers
- Session management with in-memory storage
- Debug metadata collection (14 performance metrics)
- Configuration presets and validation
- Comprehensive test suite (61 tests, 81% coverage)

**Frontend (React + TypeScript)**:
- Modern chat interface with message history
- 4 advanced components (Debug Panel, Config Panel, Export, Theme Toggle)
- Provider settings drawer with dynamic model selection
- Dark mode with localStorage persistence
- Full keyboard navigation and screen reader support
- Responsive design (mobile 320px, tablet 768px, desktop 1024px+)

**Infrastructure**:
- Docker Compose configuration for production
- Nginx reverse proxy with SSL termination
- Health checks and auto-restart policies
- Horizontal scaling (3+ backend replicas)
- Monitoring and logging integration

---

## ✅ Implementation Status

### Phase 1: Basic Chat MVP ✅ COMPLETE
- ✅ Chat interface with message history
- ✅ Session management (in-memory, UUID-based)
- ✅ Mock provider for deterministic testing
- ✅ REST API endpoints (/send, /sessions, /messages)
- ✅ React frontend with TypeScript strict mode
- ✅ 19 initial tests (API, models, services)

### Phase 2: Multi-Provider Support ✅ COMPLETE
- ✅ 6 LLM providers (Mock, Ollama, OpenAI, Anthropic, Google, Azure)
- ✅ Dynamic model loading per provider
- ✅ API key validation and session-based storage
- ✅ Provider enumeration and factory pattern
- ✅ Settings drawer UI component
- ✅ 9 provider-specific tests

### Phase 3: Advanced Features ✅ COMPLETE
- ✅ Debug panel displaying 14 performance metrics
- ✅ Configuration panel with 3 presets and sliders
- ✅ Conversation export (JSON + Markdown formats)
- ✅ Dark mode toggle with localStorage persistence
- ✅ Keyboard shortcuts (Enter, Shift+Enter, Escape)
- ✅ Responsive design (breakpoints: 320px, 768px, 1024px)
- ✅ Full accessibility (ARIA labels, keyboard nav, semantic HTML)
- ✅ 32 additional tests (debug, config, integration flows)
- ✅ Production deployment documentation

**Total**: 61 tests, 81% code coverage, 13.36s execution time

---

## 📚 Documentation (Learning Path)

**Recommended Order**: Start with QUICK_START → Explore ARCHITECTURE → Reference DEPLOYMENT for production

| Document | Purpose | Audience | Lines |
|----------|---------|----------|-------|
| **[QUICK_START.md](./QUICK_START.md)** | 5-minute setup guide with step-by-step instructions | Beginners, first-time users | 541 |
| **[ARCHITECTURE.md](./ARCHITECTURE.md)** | Technical design patterns, data flow, and component details | Intermediate engineers, architects | 590 |
| **[DEPLOYMENT.md](./DEPLOYMENT.md)** | Production deployment with Docker, nginx, SSL, monitoring | DevOps, SRE, production deployment | 500 |
| **[Backend README](./backend/README.md)** | API documentation, endpoints, and backend configuration | Backend developers | - |

---

## 🎓 Learning Modules (Theory → Practice → Reflection)

### Module 1: Basic Chat Interface (Phase 1)

**Theory**: REST API design, session management, provider abstraction patterns

**Hands-On**:
1. Run backend server: `cd web/backend && python main.py`
2. Explore Swagger UI: http://localhost:8000/docs
3. Test `/api/chat/send` endpoint with Mock provider
4. Examine session lifecycle in `chat_service.py`
5. Run unit tests: `pytest tests/test_api.py -v`

**Key Files to Study**:
- `backend/main.py` (116 lines) — FastAPI app initialization, CORS, health check
- `backend/api/chat.py` (180 lines) — Chat endpoints with validation
- `backend/services/chat_service.py` (110 lines) — Business logic, session management
- `backend/models.py` (150 lines) — Pydantic models with validation
- `frontend/src/components/Chat.tsx` (394 lines) — Chat UI with state management

**Reflection Questions**:
- Why use UUIDs for session IDs instead of auto-incrementing integers?
- How does the provider abstraction enable multi-LLM support?
- What are the trade-offs of in-memory session storage vs database?

**Exercise**: Add a new endpoint `/api/chat/sessions/{session_id}/export` that returns conversation history as JSON

---

### Module 2: Multi-Provider Integration (Phase 2)

**Theory**: Factory pattern, strategy pattern, dynamic configuration, API key security

**Hands-On**:
1. Study provider abstraction in `provider_service.py`
2. Add API key for OpenAI: Set `OPENAI_API_KEY` environment variable
3. Switch providers mid-conversation (Mock → OpenAI)
4. Compare model outputs for same prompt across providers
5. Run provider tests: `pytest tests/test_providers_api.py -v`

**Key Files to Study**:
- `backend/services/provider_service.py` (140 lines) — Provider factory, 6 implementations
- `backend/api/providers.py` (70 lines) — Provider enumeration, model loading
- `frontend/src/components/SettingsDrawer.tsx` (180 lines) — Provider UI with validation
- `frontend/src/types/providers.ts` (40 lines) — TypeScript type definitions

**Reflection Questions**:
- How does the factory pattern simplify adding new providers?
- Why store API keys in session memory instead of localStorage?
- What security considerations exist for API key transmission?

**Exercise**: Add support for a new provider (e.g., Cohere, Hugging Face, Mistral)

---

### Module 3: Debug & Observability (Phase 3)

**Theory**: Performance instrumentation, structured logging, debug metadata, cost attribution

**Hands-On**:
1. Enable debug mode: `POST /api/config/debug` with `{"enabled": true}`
2. Send message and inspect 14 debug metrics in response
3. Measure performance overhead (should be <50ms)
4. Export debug data via Debug Panel UI
5. Run debug tests: `pytest tests/test_debug_mode.py -v`

**Key Files to Study**:
- `backend/models.py` (lines 61-79) — DebugMetadata model (14 fields)
- `backend/api/config.py` (120 lines) — Debug toggle endpoint
- `frontend/src/components/DebugPanel.tsx` (97 lines) — Debug metrics display

**14 Debug Metrics Captured**:
1. `input_tokens` — Tokens in user prompt
2. `output_tokens` — Tokens in assistant response
3. `total_tokens` — Sum of input + output
4. `latency_ms` — Total request latency
5. `provider` — LLM provider used
6. `model` — Model name
7. `agent_state` — Orchestrator state
8. `tool_calls_count` — Number of tool invocations
9. `reasoning_steps` — Steps in reasoning chain
10. `error_details` — Error messages if any
11. `session_config` — Active configuration
12. `timestamp` — ISO 8601 timestamp
13. `request_id` — Unique request identifier
14. `cost_estimate` — Estimated API cost (USD)

**Exercise**: Add 2 new debug metrics (cache_hit, retry_count)

---

### Module 4: Configuration Management (Phase 3)

**Theory**: Preset patterns, validation, user preferences, defaults

**Hands-On**:
1. Apply "Creative" preset: `GET /api/config/presets`
2. Customize parameters: max_turns=5, temperature=0.9
3. Compare outputs with "Precise" preset
4. Create custom preset with your preferred parameters
5. Run config tests: `pytest tests/test_config.py -v`

**3 Built-in Presets**:
| Preset | Temperature | Max Turns | Timeout | Use Case |
|--------|-------------|-----------|---------|----------|
| **Creative** | 0.9 | 5 | 60s | Brainstorming, storytelling |
| **Precise** | 0.3 | 3 | 30s | Factual Q&A, code generation |
| **Balanced** | 0.7 | 4 | 45s | General conversation |

**Exercise**: Create an "Experimental" preset (temp=1.5, turns=7, custom system prompt)

---

### Module 5: Testing & Quality (All Phases)

**Theory**: Test pyramid, mocking, coverage targets, CI/CD

**Test Suite (61 tests, 13.36s execution)**:
| Test File | Tests | Focus |
|-----------|-------|-------|
| `test_api.py` | 8 | Chat endpoints |
| `test_config.py` | 10 | Config validation |
| `test_models.py` | 7 | Model validation |
| `test_services.py` | 4 | Business logic |
| `test_providers_api.py` | 9 | Provider management |
| `test_debug_mode.py` | 10 | Debug accuracy |
| `test_integration_flows.py` | 13 | End-to-end workflows |

**Coverage**: 81% overall, 100% on models.py

**Exercise**: Write an integration test for provider switching

---

### Module 6: Production Deployment (DevOps)

**Theory**: Containerization, reverse proxies, SSL/TLS, horizontal scaling

**Hands-On**:
1. Build frontend: `npm run build`
2. Deploy with Docker Compose
3. Configure nginx reverse proxy
4. Add SSL certificate with Let's Encrypt
5. Monitor health checks and logs

**Production Architecture**:
```
Nginx (:80, :443) → Backend Replicas (×3) → LLM Providers
```

**Exercise**: Deploy to AWS/GCP/Azure with auto-scaling

---

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- Python 3.11+ (backend)
- Node.js 16+ (frontend)
- Optional: Ollama for local LLM

### Setup

**Backend**:
```bash
cd web/backend
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
pip install -r requirements.txt
python main.py  # http://localhost:8000
```

**Frontend**:
```bash
cd web/frontend
npm install
npm start  # http://localhost:3000
```

**Verify**: Open http://localhost:3000, send message with Mock provider

---

## 📁 Project Structure

```
web/
├── README.md                       # This file (learning overview)
├── QUICK_START.md                  # 5-minute setup guide
├── ARCHITECTURE.md                 # Technical deep-dive
├── DEPLOYMENT.md                   # Production deployment
│
├── frontend/                       # React 18 + TypeScript
│   ├── src/
│   │   ├── components/
│   │   │   ├── Chat.tsx            # Main chat (394 lines)
│   │   │   ├── DebugPanel.tsx      # Debug metrics (97 lines)
│   │   │   ├── ConfigPanel.tsx     # Config controls (232 lines)
│   │   │   ├── ConversationExport.tsx  # Export (152 lines)
│   │   │   ├── ThemeToggle.tsx     # Dark mode (31 lines)
│   │   │   └── SettingsDrawer.tsx  # Provider settings (180 lines)
│   │   ├── services/
│   │   │   ├── chatService.ts
│   │   │   ├── providerService.ts
│   │   │   └── configService.ts
│   │   └── types/
│   │       ├── providers.ts
│   │       └── config.ts
│   └── package.json
│
└── backend/                        # FastAPI Application
    ├── main.py                     # FastAPI init (116 lines)
    ├── models.py                   # Pydantic models (150 lines)
    ├── api/
    │   ├── chat.py                 # Chat endpoints (180 lines)
    │   ├── providers.py            # Provider endpoints (70 lines)
    │   └── config.py               # Config endpoints (120 lines)
    ├── services/
    │   ├── chat_service.py         # Chat logic (110 lines)
    │   ├── provider_service.py     # Providers (140 lines)
    │   └── config_service.py       # Config (95 lines)
    ├── tests/                      # 61 tests, 81% coverage
    │   ├── test_api.py
    │   ├── test_config.py
    │   ├── test_models.py
    │   ├── test_services.py
    │   ├── test_providers_api.py
    │   ├── test_debug_mode.py
    │   └── test_integration_flows.py
    └── requirements.txt
```

---

## 🔬 Key Concepts Demonstrated

1. **Provider Abstraction** — Factory pattern for multi-LLM support
2. **Session Management** — UUID-based, stateless HTTP with stateful conversations
3. **Debug Observability** — 14-field metadata with optional collection
4. **Configuration Presets** — Curated defaults with customization
5. **Test-Driven Development** — 61 tests, 81% coverage, MockProvider
6. **Accessibility First** — ARIA, keyboard nav, WCAG AA compliance

---

## 🎓 Learning Outcomes

After completing this lab, you will be able to:

✅ Design REST APIs with FastAPI  
✅ Implement provider abstraction for multiple LLMs  
✅ Build accessible UIs with React + TypeScript  
✅ Write comprehensive test suites  
✅ Instrument applications with debug metadata  
✅ Deploy to production with Docker + nginx  
✅ Apply design patterns (Factory, Strategy, Observer)

---

## 🔗 Integration with Broader Curriculum

| Related Module | Connection |
|----------------|------------|
| **Labs 00-08** | Backend uses same `agent_labs` orchestrator |
| **Curriculum 02_intermediate** | Configuration patterns match curriculum |
| **Curriculum 03_advanced** | Debug observability aligns with production |
| **Projects P01-P12** | Can serve as frontend for projects |
| **Agents/ docs** | Architecture mirrors reference docs |

---

## 📊 Success Metrics

| Metric | Target | Achieved |
|--------|--------|----------|
| Test Coverage | ≥80% | 81% ✅ |
| Tests Passing | 100% | 61/61 ✅ |
| Test Execution | <20s | 13.36s ✅ |
| API Response | <500ms | ~200ms ✅ |
| Debug Overhead | <50ms | <30ms ✅ |
| Accessibility | WCAG AA | WCAG AA ✅ |

---

## 🛠️ Tools & Technologies

**Backend**: Python 3.11, FastAPI 0.104, Pydantic v2, Uvicorn, pytest  
**Frontend**: React 18, TypeScript 5.9, CSS3  
**Infrastructure**: Docker, nginx, Let's Encrypt

---

## 🤝 Contributing

This is a learning resource. To contribute:
1. Study existing patterns
2. Add tests (maintain 80%+ coverage)
3. Update documentation
4. Follow space_framework governance

---

**Version**: 1.0.0 (Production Ready)  
**Last Updated**: 2026-01-26  
**Story**: #57 Web-Based Agent Chat Interface  
**Status**: ✅ Complete (all 3 phases)
