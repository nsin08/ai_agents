# Web-Based Agent Chat Interface - MVP Foundation (#63)

> **Issue**: #63 - MVP Foundation - Basic Chat with Mock Provider  
> **Status**: 🟢 **COMPLETE** - All deliverables implemented  
> **Duration**: 1-2 days  

## Overview

This is the foundation of the web-based agent chat interface. It establishes the architecture (FastAPI backend + React frontend + ServiceInterface abstraction) with basic chat functionality using the Mock provider.

### Key Features ✅

- **Chat Interface**: Send messages to Mock provider and receive responses
- **Message Display**: Conversation history with timestamps and metadata
- **Loading States**: Visual feedback while agent processes
- **Error Handling**: User-friendly error messages
- **Architecture**: Abstraction layer allows future provider swapping
- **API Documentation**: Auto-generated FastAPI docs at `/docs`
- **Type Safety**: Full TypeScript + Python type hints
- **Testing**: Unit tests for backend (pytest) and frontend (Jest/RTL)

---

## Quick Start

### Prerequisites
- Python 3.11+ (Python 3.14+ requires pydantic >= 2.10.0)
- Node.js 18+ and npm 9+
- Git

**Windows Users:**
- PowerShell or Windows Terminal (recommended)
- Execution policy may need adjustment: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### 1. Clone Repository
```bash
cd ai_agents
git checkout develop
git pull origin develop
```

### 2. Backend Setup (< 2 minutes)
```bash
cd web/backend

# Create virtual environment (recommended)
python -m venv .web_env

# Activate virtual environment
# Windows PowerShell:
.\.web_env\Scripts\Activate.ps1
# Windows CMD:
.web_env\Scripts\activate.bat
# macOS/Linux:
source .web_env/bin/activate

# Upgrade pip (important for Python 3.14+)
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Set environment (optional)
# Windows PowerShell:
$env:AGENT_CORE_BACKEND="agent_labs"
$env:LLM_PROVIDER="mock"
# macOS/Linux:
export AGENT_CORE_BACKEND=agent_labs
export LLM_PROVIDER=mock

# Run server
python -m uvicorn main:app --reload --port 8000
```

**Expected Output:**
```
INFO: Uvicorn running on http://127.0.0.1:8000
INFO: Started reloader process
INFO: Started server process
INFO: Application startup complete
```

### 3. Frontend Setup (< 2 minutes)
```bash
cd web/frontend

# Install dependencies (use --legacy-peer-deps for TypeScript 5.x compatibility)
npm install --legacy-peer-deps

# Start development server
npm start
```

**Expected Output:**
```
Compiled successfully!
You can now view agent-chat in the browser.
  http://localhost:3000
```

### 4. Access Application
Open browser: **http://localhost:3000**

---

## Architecture

### Project Structure
```
web/
├── backend/
│   ├── main.py                 # FastAPI entry point
│   ├── config.py               # Dependency injection
│   ├── models.py               # Pydantic request/response models
│   ├── api/
│   │   └── chat.py             # Chat endpoints
│   ├── services/
│   │   ├── interfaces.py       # ServiceInterface Protocol (abstraction)
│   │   └── agent_labs_impl.py  # AgentLabsService implementation
│   ├── tests/
│   │   ├── test_api.py         # Endpoint tests (8 tests)
│   │   ├── test_models.py      # Model validation tests (7 tests)
│   │   └── test_services.py    # Service logic tests (4 tests)
│   └── requirements.txt        # Dependencies
│
└── frontend/
    ├── public/
    │   └── index.html          # HTML entry point
    ├── src/
    │   ├── index.tsx           # React root
    │   ├── App.tsx             # Main component
    │   ├── components/
    │   │   ├── Chat.tsx        # Chat UI component
    │   │   └── Chat.test.tsx   # Component tests (13 tests)
    │   ├── services/
    │   │   └── chatService.js  # Backend API client
    │   ├── App.test.tsx        # App tests (2 tests)
    │   └── index.css           # Styles
    ├── package.json            # Dependencies & scripts
    └── tsconfig.json           # TypeScript configuration
```

### Architecture Pattern: ServiceInterface

The backend uses a **Protocol-based abstraction** to decouple the API from specific implementations:

```python
# services/interfaces.py - Defines the contract
class AgentServiceInterface(Protocol):
    async def process_message(...) -> ChatResponse: ...

# services/agent_labs_impl.py - Implements for agent_labs
class AgentLabsService(AgentServiceInterface):
    async def process_message(...) -> ChatResponse: ...

# config.py - Dependency injection
def agent_service() -> AgentServiceInterface:
    if AGENT_CORE_BACKEND == "agent_labs":
        return AgentLabsService()  # Current
    elif AGENT_CORE_BACKEND == "agent_core":
        return AgentCoreService()  # Future
```

This allows **swapping backends** by changing `AGENT_CORE_BACKEND` env var without modifying API code.

---

## API Endpoints

### POST `/api/chat/send`
Send a message to the agent.

**Request:**
```json
{
  "message": "What is Python?",
  "provider": "mock",
  "model": "mock-model",
  "config": {
    "max_turns": 3,
    "temperature": 0.7
  }
}
```

**Response (Success):**
```json
{
  "success": true,
  "response": "Python is a high-level programming language...",
  "metadata": {
    "provider": "mock",
    "model": "mock-model",
    "latency_ms": 45.23,
    "max_turns": 3,
    "backend": "agent_labs"
  }
}
```

**Response (Error):**
```json
{
  "success": false,
  "response": "Error: Provider 'ollama' not yet supported",
  "metadata": {
    "provider": "ollama",
    "error": "Unsupported provider",
    "latency_ms": 5.12
  }
}
```

### POST `/api/chat/sessions`
Create a new chat session.

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### GET `/api/chat/sessions/{session_id}`
Get session history.

**Response:**
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "messages": [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi there!"}
  ]
}
```

### GET `/health`
Health check.

**Response:**
```json
{"status": "healthy"}
```

---

## Testing

### Backend Tests (pytest)
```bash
cd web/backend

# Run all tests (19 tests)
pytest tests/ -v

# Run specific test file
pytest tests/test_api.py -v

# Run specific test
pytest tests/test_api.py::test_send_message_success -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

**Test Coverage:**
- ✅ API endpoints (8 tests in `test_api.py`)
- ✅ Data models (7 tests in `test_models.py`)
- ✅ Service logic (4 tests in `test_services.py`)
- ✅ Request validation
- ✅ Error handling
- ✅ Response formatting

### Frontend Tests (Jest + React Testing Library)
```bash
cd web/frontend

# Run all tests
npm test

# Run specific test file
npm test -- Chat.test.tsx

# Run with coverage
npm test -- --coverage

# Run in watch mode
npm test -- --watch
```

**Test Coverage:**
- ✅ Chat component rendering (13 tests in `Chat.test.tsx`)
- ✅ Message sending and receiving
- ✅ Loading states
- ✅ Error display
- ✅ Session initialization
- ✅ App integration (2 tests in `App.test.tsx`)

---

## Environment Configuration

### Backend Environment Variables
```bash
# Provider selection (default: agent_labs)
export AGENT_CORE_BACKEND=agent_labs

# LLM configuration
export LLM_PROVIDER=mock           # or: ollama, openai, anthropic
export LLM_MODEL=mock-model        # or: llama3.2, gpt-4, etc.
export LLM_BASE_URL=http://localhost:11434  # For Ollama

# Frontend URL (for backend)
export FRONTEND_URL=http://localhost:3000
```

### Frontend Environment Variables
```bash
# Backend API URL (default: http://localhost:8000)
export REACT_APP_API_URL=http://localhost:8000
```

---

## API Documentation

**Interactive API Docs** (Swagger UI):
- **URL**: http://localhost:8000/docs
- **Features**:
  - Try out endpoints directly
  - View request/response schemas
  - See example payloads

**ReDoc Documentation**:
- **URL**: http://localhost:8000/redoc

---

## Development Workflow

### File Organization

**Backend Code:**
```
web/backend/
├── main.py                 # FastAPI app setup + CORS
├── config.py               # Dependency injection, env vars
├── models.py               # Pydantic request/response models
├── api/chat.py             # Route handlers
├── services/
│   ├── interfaces.py       # ServiceInterface Protocol
│   └── agent_labs_impl.py  # Implementation
└── tests/                  # Unit tests
```

**Frontend Code:**
```
web/frontend/src/
├── index.tsx               # React root mount
├── App.tsx                 # Main component
├── components/
│   ├── Chat.tsx            # Chat UI component
│   └── Chat.test.tsx       # Component tests
├── services/
│   └── chatService.js      # API client
└── App.test.tsx            # Integration tests
```

### Adding a New Endpoint

1. **Define Request/Response Models** (models.py)
   ```python
   class NewRequest(BaseModel):
       field: str

   class NewResponse(BaseModel):
       result: str
   ```

2. **Create Handler** (api/chat.py)
   ```python
   @router.post("/new-endpoint")
   async def new_endpoint(request: NewRequest, service = Depends(agent_service)):
       # Implementation
   ```

3. **Write Tests** (tests/test_api.py)
   ```python
   def test_new_endpoint():
       response = client.post("/api/chat/new-endpoint", json={"field": "value"})
       assert response.status_code == 200
   ```

### Switching Backends

To switch from `agent_labs` to `agent_core` (when available):

```bash
# Option 1: Environment variable
export AGENT_CORE_BACKEND=agent_core

# Option 2: Implement AgentCoreService in services/
# Then update config.py agent_service() function
```

No API changes needed - abstraction handles it!

---

## Acceptance Criteria

- [x] User can send message to Mock provider and receive response
- [x] Response displays in chat interface with timestamp
- [x] Loading indicator shows while agent processes
- [x] Error messages display user-friendly format
- [x] FastAPI auto-docs available at `/docs`
- [x] All backend tests pass (19/19 passing)
- [x] All frontend tests pass (15/15 passing)
- [x] Can switch backend via `AGENT_CORE_BACKEND` env var
- [x] ServiceInterface abstraction layer allows future agent_core swap

---

## Troubleshooting

### Backend Port Already in Use
```bash
# Check what's using port 8000
lsof -i :8000  # macOS/Linux
Get-NetTCPConnection -LocalPort 8000  # Windows

# Use different port
python -m uvicorn main:app --reload --port 8001
```

### Frontend Port Already in Use
```bash
# Check what's using port 3000
lsof -i :3000  # macOS/Linux

# Use different port
PORT=3001 npm start
```

### CORS Error
Ensure backend CORS middleware includes frontend URL:
```python
# In main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
)
```

### ❌ `pydantic-core` Compilation Error (Windows + Python 3.14)
**Error:**
```
Cargo, the Rust package manager, is not installed or is not on PATH.
This package requires Rust and Cargo to compile extensions.
```

**Root Cause:** Older pydantic versions require Rust compiler on Windows.

**Solution:**
```bash
# 1. Upgrade pip first
python -m pip install --upgrade pip

# 2. Install with updated requirements (includes pydantic >= 2.10.0 with pre-built wheels)
pip install -r requirements.txt

# 3. Verify installation
pip list | findstr pydantic
# Should show: pydantic 2.10+ and pydantic-core 2.41+
```

**Why This Works:** The updated `requirements.txt` uses `pydantic>=2.10.0`, which includes pre-compiled Windows wheels (no Rust compilation needed).

### ❌ `pip` Command Not Found (Windows)
**Solution:** Use `python -m pip` instead:
```bash
python -m pip install -r requirements.txt
python -m pip install --upgrade pip
```

### ❌ Virtual Environment Activation Fails (Windows)
**Wrong:**
```bash
source .web_env/bin/activate  # ❌ Unix path on Windows
```

**Correct:**
```powershell
# PowerShell (Windows)
.\.web_env\Scripts\Activate.ps1

# CMD (Windows)
.\.web_env\Scripts\activate.bat

# If PowerShell blocks script execution:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Tests Failing
```bash
# Backend tests
cd web/backend
python -m pip install -r requirements.txt
pytest tests/ -v

# Frontend tests
cd web/frontend
npm install
npm test
```

---

## Platform-Specific Notes

**Windows:**
- Use `\` for paths: `.\.web_env\Scripts\activate`
- Use `python` or `python.exe` (not `python3`)
- PowerShell recommended over CMD
- May need execution policy adjustment (see troubleshooting above)

**macOS/Linux:**
- Use `/` for paths: `./web_env/bin/activate`
- Use `python3` if multiple Python versions installed
- May need `sudo` for global package installations

---

## Known Limitations (MVP)

- ❌ No provider selection UI (Mock only)
- ❌ No multi-turn persistence
- ❌ No debug panel
- ❌ No export/download
- ❌ No mobile responsiveness
- ❌ No keyboard shortcuts

These will be addressed in #57.2 and #57.3.

---

## Next Steps

- **#57.2**: Multi-Provider Support (Ollama, OpenAI, etc.)
- **#57.3**: Advanced Features (persistence, debug panel, etc.)
- **#58**: Vector-based Retrieval
- **#59**: Multi-Agent Orchestration

---

## Reference

- **Issue**: https://github.com/nsin08/ai_agents/issues/63
- **Parent Story**: https://github.com/nsin08/ai_agents/issues/57
- **Framework**: https://github.com/nsin08/space_framework

---

**Status**: ✅ **COMPLETE**  
**Test Coverage**: 34/34 tests passing  
**Ready for Review**: Yes  
**Ready for Production**: Yes (MVP phase)
