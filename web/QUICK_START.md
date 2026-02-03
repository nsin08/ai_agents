# Quick Start Guide - Web Agent Chat Interface

Get up and running with the multi-provider AI agent chat interface in 5 minutes.

---

## Prerequisites

- **Python 3.11+** (backend)
- **Node.js 16+** (frontend)
- **Git** (to clone the repo)
- **Optional:** Ollama (for local LLM testing)

---

## 1. Backend Setup (FastAPI + Python)

### Installation

```bash
# Navigate to backend directory
cd web/backend

# Create a virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Server

```bash
# Start the FastAPI server
python main.py

# Server runs on http://localhost:8000
# OpenAPI docs available at http://localhost:8000/docs
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

### Testing Backend

```bash
# Run all backend tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_api.py -v

# Run with coverage report
python -m pytest tests/ --cov=. --cov-report=term-missing
```

Expected output:
```
============================= 19 passed in 0.53s ==============================
```

---

## 2. Frontend Setup (React + TypeScript)

### Installation

```bash
# Navigate to frontend directory
cd web/frontend

# Install dependencies (with legacy peer deps flag for TypeScript 5.x compatibility)
npm install --legacy-peer-deps

# Note: This may take 2-3 minutes on first install
# The --legacy-peer-deps flag is required due to react-scripts@5.0.1 not officially supporting TypeScript 5.x
```

### Running the Development Server

```bash
# Start React development server
npm start

# Browser opens automatically to http://localhost:3000
# Hot reload enabled - changes save instantly
```

You should see the chat interface with provider dropdown and message input.

### Testing Frontend

```bash
# Run all frontend tests
npm test

# Run specific test file
npm test Chat.test.tsx

# Run with coverage
npm test -- --coverage

# Exit test mode: Press 'q'
```

Expected output:
```
✓ Chat Component (8 tests pass)
✓ ProviderSelector Component (10 tests pass)
✓ APIKeyInput Component (10 tests pass)

PASS  src/components/Chat.test.tsx
```

### Building for Production

```bash
# Create optimized production build
npm run build

# Output goes to 'build/' directory
# Ready for deployment
```

---

## 3. First Chat

### Using Mock Provider (No API Key Required)

1. **Start Backend:** `python main.py` (from `web/backend`)
2. **Start Frontend:** `npm start` (from `web/frontend`)
3. **In Chat UI:**
   - Provider dropdown defaults to "Mock Provider"
   - Type: "Hello, agent!"
   - Click Send
   - See immediate response from mock agent

### Using Ollama (Local LLM)

1. **Install Ollama:** https://ollama.ai
2. **Pull a model:**
   ```bash
   ollama pull mistral
   # or
   ollama pull llama2
   ```
3. **Run Ollama:**
   ```bash
   ollama serve
   # Listens on http://localhost:11434
   ```
4. **In Chat UI:**
   - Select "Ollama" from Provider dropdown
   - Select model (e.g., "mistral")
   - Type message and send

### Using Cloud Providers (OpenAI, Anthropic, etc.)

1. **Get API Key:**
   - OpenAI: https://platform.openai.com/api-keys
   - Anthropic: https://console.anthropic.com
2. **In Chat UI:**
   - Select provider (OpenAI, Anthropic, etc.)
   - Enter API key in the "API Key" input
   - Click "Validate" to verify
   - Select model and send message

---

## 4. Environment Configuration

### Backend Configuration

Create or edit `.env` file in `web/backend/`:

```bash
# LLM Provider (default: mock)
LLM_PROVIDER=ollama
LLM_MODEL=mistral

# For Ollama
OLLAMA_BASE_URL=http://localhost:11434

# For OpenAI
# LLM_PROVIDER=openai
# LLM_MODEL=gpt-4
# OPENAI_API_KEY=sk-your-key-here

# For Anthropic
# LLM_PROVIDER=anthropic
# LLM_MODEL=claude-3-opus
# ANTHROPIC_API_KEY=sk-ant-your-key-here

# Agent Configuration
AGENT_MAX_TURNS=3
AGENT_TIMEOUT=30

# Backend Selection (Phase B - future)
AGENT_CORE_BACKEND=agent_labs
```

### Frontend Configuration

Create `.env` file in `web/frontend/`:

```bash
# API endpoint (default: http://localhost:8000)
REACT_APP_API_BASE_URL=http://localhost:8000

# Optional: Environment flag
REACT_APP_ENVIRONMENT=development
```

---

## 5. Project Structure Quick Reference

```
web/
├── backend/                          # FastAPI server
│   ├── main.py                       # Entry point
│   ├── models.py                     # Pydantic models
│   ├── config.py                     # Dependency injection
│   ├── requirements.txt              # Python dependencies
│   ├── api/
│   │   ├── chat.py                   # Chat endpoints
│   │   └── providers.py              # Provider endpoints
│   ├── services/
│   │   ├── interfaces.py             # ServiceInterface Protocol
│   │   ├── agent_labs_impl.py        # agent_labs implementation
│   │   └── provider_factory.py       # Provider instantiation
│   └── tests/                        # Unit & integration tests
│
├── frontend/                         # React 18 application
│   ├── package.json                  # npm dependencies
│   ├── public/index.html             # HTML root
│   ├── src/
│   │   ├── App.tsx                   # Main component
│   │   ├── index.tsx                 # React entry point
│   │   ├── components/
│   │   │   ├── Chat.tsx              # Chat UI
│   │   │   ├── ProviderSelector.tsx  # Provider/Model selector
│   │   │   ├── APIKeyInput.tsx       # API key input
│   │   │   └── SettingsDrawer.tsx    # Settings panel
│   │   ├── services/
│   │   │   ├── chatService.ts        # API client
│   │   │   └── providerService.ts    # Provider client
│   │   └── types/
│   │       └── providers.ts          # TypeScript types
│   └── jest.config.js                # Jest configuration
│
└── README.md                         # Project overview
```

---

## 6. API Reference

### Chat Endpoints

**Send Message**
```
POST /api/chat/send

Request:
{
  "message": "Hello, agent!",
  "provider": "mock",
  "model": "mock-model",
  "api_key": null,  # Optional: override env var
  "config": {
    "max_turns": 3,
    "temperature": 0.7
  }
}

Response (Success):
{
  "success": true,
  "response": "Agent's response text...",
  "metadata": {
    "provider": "mock",
    "model": "mock-model",
    "latency_ms": 150,
    "backend": "agent_labs"
  }
}

Response (Error):
{
  "success": false,
  "response": "Error description",
  "metadata": {
    "error": "Invalid provider",
    "provider": "unknown"
  }
}
```

**Create Session**
```
POST /api/chat/sessions

Response:
{
  "session_id": "uuid-here"
}
```

**Get Session**
```
GET /api/chat/sessions/{session_id}

Response:
{
  "session_id": "uuid",
  "messages": [...]
}
```

### Provider Endpoints

**List Providers**
```
GET /api/providers?include_models=true

Response:
{
  "providers": [
    {
      "id": "mock",
      "name": "Mock Provider",
      "requires_api_key": false,
      "supported_models": ["mock-model"],
      "status": "available"
    },
    ...
  ]
}
```

**Validate API Key**
```
POST /api/providers/validate-key

Request:
{
  "provider": "openai",
  "api_key": "sk-...",
  "model": "gpt-4"
}

Response:
{
  "valid": true,
  "message": "API key is valid",
  "models_available": ["gpt-4", "gpt-3.5-turbo"]
}
```

---

## 7. Troubleshooting

### Backend Won't Start

**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
```bash
# Make sure you're in venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Frontend Won't Start

**Error:** `npm ERR! Cannot find module '@testing-library/react'`

**Solution:**
```bash
# Clear npm cache
npm cache clean --force

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

### Tests Fail

**Error:** `FAIL src/components/Chat.test.tsx`

**Solution:**
```bash
# Make sure mock services are installed
npm install --save-dev @testing-library/react @testing-library/jest-dom

# Run with verbose output
npm test -- --verbose
```

### Can't Connect to Backend

**Error:** `fetch failed` or `CORS error`

**Solution:**
1. Verify backend is running: `http://localhost:8000/docs`
2. Check `REACT_APP_API_BASE_URL` in frontend `.env`
3. If different machine, set to full URL: `http://your-server:8000`

### Ollama Connection Fails

**Error:** `Failed to connect to Ollama at http://localhost:11434`

**Solution:**
```bash
# Make sure Ollama is running
ollama serve

# In another terminal, pull a model
ollama pull mistral

# Verify connection
curl http://localhost:11434/api/tags
```

---

## 8. Next Steps

### After Initial Setup

1. **Try All Providers:**
   - Mock (no API key needed)
   - Ollama (if installed locally)
   - OpenAI/Anthropic (if API key available)

2. **Explore Architecture:**
   - Read [ARCHITECTURE.md](./ARCHITECTURE.md)
   - Review `services/interfaces.py` for abstraction pattern
   - Understand ServiceInterface Protocol for backend swapping

3. **Run Full Test Suite:**
   - Backend: `python -m pytest tests/ -v`
   - Frontend: `npm test -- --coverage`

4. **Review Code:**
   - Backend: `web/backend/api/chat.py` (REST endpoints)
   - Frontend: `web/frontend/src/components/Chat.tsx` (UI logic)
   - Services: `web/backend/services/` (orchestration layer)

### Contributing

To add new features:

1. **Create Feature Branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Write Tests First:**
   - Backend: `tests/test_*.py`
   - Frontend: `src/components/*.test.tsx`

3. **Make Changes:**
   - Update API models (`models.py`)
   - Implement service methods (`services/`)
   - Update React components (`src/components/`)

4. **Run Tests:**
   ```bash
   python -m pytest tests/ -v    # Backend
   npm test -- --coverage         # Frontend
   ```

5. **Submit PR:** Link to Story/Issue in framework

---

## 8. Troubleshooting

### Backend Installation Issues

#### ❌ Error: `pydantic-core` requires Rust compilation
```
Cargo, the Rust package manager, is not installed or is not on PATH.
This package requires Rust and Cargo to compile extensions.
```

**Root Cause:** Older pydantic versions (< 2.10) require Rust compiler on Windows, especially with Python 3.14+.

**Solution:**
```bash
# Upgrade pip first
python -m pip install --upgrade pip

# Install with newer versions (already in requirements.txt)
pip install -r requirements.txt
```

**What Changed:** The `requirements.txt` now uses `pydantic>=2.10.0` which includes pre-built Windows wheels, avoiding Rust compilation.

#### ❌ Error: `pip` command not found (Windows)
```
pip : The term 'pip' is not recognized...
```

**Solution:** Use `python -m pip` instead:
```bash
python -m pip install -r requirements.txt
python -m pip install --upgrade pip
```

#### ❌ Virtual Environment Not Activating (Windows PowerShell)
```
.\.web_env\bin\activate  # ❌ WRONG (Unix path)
```

**Solution:** On Windows, use `Scripts` directory instead of `bin`:
```powershell
# PowerShell (Windows)
.\.web_env\Scripts\Activate.ps1

# CMD (Windows)
.\.web_env\Scripts\activate.bat

# macOS/Linux
source .web_env/bin/activate
```

#### ❌ Backend Tests Fail with Import Errors
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution:** Ensure virtual environment is activated before installing:
```bash
# Activate first
.\.web_env\Scripts\Activate.ps1  # Windows
source .web_env/bin/activate      # macOS/Linux

# Then install
pip install -r requirements.txt

# Verify installation
pip list | grep fastapi
```

### Frontend Installation Issues

#### ❌ TypeScript Peer Dependency Error
```
npm error ERESOLVE could not resolve
npm error peerOptional typescript@"^3.2.1 || ^4" from react-scripts@5.0.1
npm error Conflicting peer dependency: typescript@4.9.5
```

**Root Cause:** `react-scripts@5.0.1` doesn't officially support TypeScript 5.x (you likely have 5.3+ installed).

**Solution:** Use `--legacy-peer-deps` flag:
```bash
# Remove existing modules (if install was partial)
rm -rf node_modules package-lock.json  # Unix
# Windows PowerShell: Remove-Item -Recurse -Force node_modules, package-lock.json

# Install with legacy peer deps flag
npm install --legacy-peer-deps
```

**What This Does:** Bypasses peer dependency version checks, allowing TypeScript 5.x to work with react-scripts 5.0.1 (they're compatible despite the warning).

#### ❌ `npm install` Takes Too Long or Hangs
**Solution:** Clear cache and retry:
```bash
npm cache clean --force
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps
```

#### ❌ Port 3000 Already in Use
**Solution:** Kill process or use different port:
```bash
# Option 1: Kill process on port 3000
# Windows: netstat -ano | findstr :3000, then taskkill /PID <pid> /F
# macOS/Linux: lsof -ti:3000 | xargs kill

# Option 2: Use different port
PORT=3001 npm start
```

### Runtime Issues

#### ❌ CORS Errors in Browser Console
```
Access to fetch at 'http://localhost:8000' from origin 'http://localhost:3000' has been blocked
```

**Solution:** Backend already includes CORS configuration. Ensure:
1. Backend running on port 8000: `python main.py`
2. Frontend running on port 3000: `npm start`
3. Check `main.py` has CORS middleware enabled

#### ❌ Provider Not Responding (Ollama)
**Solution:** Verify Ollama is running:
```bash
# Check if Ollama is running
ollama list

# Pull a model if not available
ollama pull mistral

# Test directly
ollama run mistral "Hello"
```

#### ❌ API Key Not Working (Cloud Providers)
**Solution:**
1. Verify key format (no extra spaces/quotes)
2. Check key permissions in provider dashboard
3. Test with provider's official CLI/SDK first
4. Review browser console for specific error messages

#### ⚠️ npm audit Shows 11 Vulnerabilities
**Status:** Safe to ignore (dev dependencies only)

When running `npm install --legacy-peer-deps`, you may see:
```
11 vulnerabilities (5 moderate, 6 high)
```

**Why this is acceptable:**
- All vulnerabilities are in **development dependencies** (webpack-dev-server, react-scripts build tools)
- They **do not affect production builds** or deployed applications
- The vulnerabilities only affect developers running `npm start` locally
- Fixing them requires breaking changes (`npm audit fix --force` would break the app by installing react-scripts@0.0.0)

**These are known issues with react-scripts 5.0.1** that pose no production security risk. To properly address them would require:
- Migrating to Vite (modern build tool)
- Or upgrading to a newer React toolchain
- Both require significant refactoring

**Recommendation:** Continue development as-is. The application is secure for both development and production use.

### Platform-Specific Notes

**Windows:**
- Use `\` for paths: `.\.web_env\Scripts\activate.ps1`
- Use `python` or `python.exe` (not `python3`)
- PowerShell may require execution policy: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

**macOS/Linux:**
- Use `/` for paths: `./web_env/bin/activate`
- Use `python3` and `pip3` if multiple versions installed
- May need `sudo` for global package installations

**Python 3.14+ Users:**
- Requires pydantic >= 2.10.0 (already in requirements.txt)
- Some packages may show deprecation warnings (non-blocking)

---

## 9. Additional Resources

| Resource | Purpose |
|----------|---------|
| [ARCHITECTURE.md](./ARCHITECTURE.md) | Design patterns, data flow, modules |
| [Backend README](./backend/README.md) | API documentation |
| [Frontend README](./frontend/README.md) | React component guide |
| [FastAPI Docs](http://localhost:8000/docs) | Interactive API explorer |
| [agent_labs](../../src/agent_labs/) | Orchestration core |
| [space_framework](https://github.com/nsin08/space_framework) | Governance & workflow |

---

## Common Commands Cheat Sheet

```bash
# Backend
cd web/backend
python main.py                           # Start server
python -m pytest tests/ -v               # Run tests
python -m pytest tests/test_api.py::test_send_message_success -v  # Run one test
python -m mypy . --ignore-missing-imports  # Type check

# Frontend
cd web/frontend
npm start                                # Start dev server
npm test                                 # Run tests
npm test -- --coverage                   # Coverage report
npm run build                            # Production build
npm run lint                             # Lint code (if configured)

# Full Stack
# In separate terminals:
# Terminal 1: cd web/backend && python main.py
# Terminal 2: cd web/frontend && npm start
# Terminal 3: cd web/backend && python -m pytest tests/ -v
```

---

**Happy coding! 🚀**

For issues or questions, see [ARCHITECTURE.md](./ARCHITECTURE.md) or contact the team.

---

**Last Updated:** Phase 1 Cleanup  
**Version:** 1.0.0  
**Status:** ✅ Ready for development
