# AI Agents Web Application

**Multi-Provider LLM Support | Chat Interface | API Key Management | Dynamic Model Selection**

## ✅ Current Features

✅ **Chat Interface** - Real-time conversation with AI agents  
✅ **6 LLM Providers** - Mock, Ollama, OpenAI (working) + Anthropic, Google, Azure (coming soon)  
✅ **Dynamic Provider Selection** - Dropdown UI with status badges  
✅ **API Key Management** - Secure input with validation  
✅ **Model Selection** - Provider-specific model lists  
✅ **Metadata Display** - Shows provider, model, and latency for each response  
✅ **Response History** - Chat messages persist during session  

## Project Structure

```
web/
├── frontend/                       # React 18 + TypeScript Application
│   ├── package.json               # npm dependencies & scripts
│   ├── tsconfig.json              # TypeScript strict configuration
│   ├── public/
│   │   └── index.html             # HTML entry point
│   └── src/
│       ├── index.tsx              # React root
│       ├── App.tsx                # Main App component
│       ├── App.css                # Styles
│       ├── index.css              # Global styles
│       ├── setupTests.ts          # Jest configuration
│       ├── components/
│       │   ├── Chat.tsx                  # Chat UI component
│       │   ├── Chat.css                  # Chat styles
│       │   ├── SettingsDrawer.tsx        # Provider selection UI
│       │   ├── SettingsDrawer.css        # Settings styles
│       ├── services/
│       │   ├── chatService.js            # Backend API client
│       │   ├── chatService.d.ts          # TypeScript types
│       │   └── providerService.ts        # Provider API client
│       └── types/
│           └── providers.ts              # Provider types
│
└── backend/                        # FastAPI Application
    ├── main.py                    # Entry point
    ├── config.py                  # Dependency injection
    ├── models.py                  # Pydantic data models
    ├── requirements.txt           # Python dependencies
    ├── api/
    │   ├── chat.py                # Chat endpoints
    │   └── providers.py           # Provider endpoints
    ├── services/
    │   ├── agent_labs_impl.py     # Business logic
    │   ├── interfaces.py          # Service interfaces
    │   ├── provider_service.py    # Provider service
    │   └── provider_factory.py    # Provider factory
    └── tests/
        ├── test_api.py            # 8 endpoint tests ✅
        ├── test_models.py         # 7 model tests ✅
        ├── test_services.py       # 4 service tests ✅
        └── test_integration.py    # Integration tests ✅
```

## Prerequisites

Before starting, ensure you have:
- **Python 3.11+** ([Download](https://www.python.org/downloads/))
- **Node.js 16+** with npm ([Download](https://nodejs.org/))
- **Git** (for cloning this repo)
- **(Optional) Ollama** for local LLM inference ([Download](https://ollama.ai/)) - only if using Ollama provider

## First-Time Setup (Run Once)

From the **root project directory** (`ai_agents/`):

```bash
# Install backend dependencies
cd web/backend
pip install -r requirements.txt

# Install frontend dependencies
cd web/frontend
npm install --legacy-peer-deps
```

## Quick Start (Run Every Time)

**You need TWO separate terminal windows:**

### Terminal 1: Start Backend
```bash
cd web/backend
python main.py
```
✅ You should see: `✅ Agent Chat API Started Successfully!`  
✅ API Documentation: http://localhost:8000/docs  
✅ Ready when backend is running

### Terminal 2: Start Frontend
```bash
cd web/frontend
npm start
```
✅ You should see: `Compiled successfully!`  
✅ Browser opens automatically at: http://localhost:3000  
✅ If not, open http://localhost:3000 manually

## 🎮 Using the Application

### First Time? Start with Mock Provider ✅

1. **Open the app** at http://localhost:3000 (frontend should open automatically)
2. Type a message: `"Hello, what is Python?"`
3. Click **Send** - you'll get a response instantly
4. Look at the top-right for the **provider badge** (should show "Mock")

### Switching Providers

1. Click **⚙️ Settings** button (top-right corner)
2. Select provider from **"Provider"** dropdown:
   - **Mock** ✅ - No setup, instant responses (start here!)
   - **Ollama** ✅ - Local models, free, private (requires running Ollama)
   - **OpenAI** ✅ - GPT-4, high quality (requires API key)
   - **Anthropic** 🚧 - Coming soon
   - **Google** 🚧 - Coming soon
   - **Azure OpenAI** 🚧 - Coming soon
3. Select **"Model"** from second dropdown
4. If using **OpenAI**: Paste your API key in the text field, click **Validate**
5. Click outside Settings or start chatting

### Using Ollama (Optional)

If you want to use Ollama:

1. **Install Ollama** from https://ollama.ai/
2. **Run Ollama server** (open terminal and run):
   ```bash
   ollama serve
   ```
3. **Download a model** (in another terminal):
   ```bash
   ollama pull mistral
   ```
4. In the app: Select **Ollama** provider → Select **mistral** model → Chat
5. First response takes a few seconds to generate locally

### Using OpenAI (Optional)

If you want to use OpenAI:

1. **Get API key** from https://platform.openai.com/account/api-keys
2. In the app: Select **OpenAI** provider
3. Paste your API key, click **Validate** (optional step)
4. Select model (gpt-4, gpt-3.5-turbo, etc.)
5. Start chatting - responses are faster and higher quality than Mock

## ❓ Troubleshooting

| Problem | Solution |
|---------|----------|
| **Backend won't start** | Make sure port 8000 is free: `lsof -i :8000` (Mac/Linux) or `netstat -ano \| findstr :8000` (Windows) |
| **Frontend shows errors** | Run `npm install --legacy-peer-deps` again in `web/frontend` |
| **"Cannot GET /" at localhost:3000** | Wait 30 seconds for React to compile, then refresh |
| **Ollama model not found** | Run `ollama pull mistral` before selecting Ollama provider |
| **OpenAI API key rejected** | Check key is correct, test at https://platform.openai.com/account/api-keys |
| **Backend returns 500 error** | Check terminal 1 (backend) for error message - copy it here for help |
| **Frontend freezes on send** | Check backend is running (should see output in Terminal 1) |

## Environment Variables (Optional)

Create `web/backend/.env` to set defaults (not needed for Mock provider):

```env
# For OpenAI
OPENAI_API_KEY=sk-your-key-here

# For Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral
```

No `.env` needed to get started with Mock provider!

## API Endpoints

### Chat Endpoints
- `POST /api/chat/sessions` - Create new chat session
- `POST /api/chat/send` - Send message to agent
- `GET /api/chat/sessions/{id}` - Get session history
- `GET /health` - Health check

### Provider Endpoints
- `GET /providers` - List all providers with metadata
- `GET /providers?include_models=true` - List providers with available models
- `POST /providers/validate` - Validate API key format

## Tech Stack

**Frontend:**
- React 18.2.0
- TypeScript 5.9.3
- react-scripts 5.0.1
- Testing Library + Jest

**Backend:**
- Python 3.14.2
- FastAPI 0.109.0
- Pydantic 2.12.5
- Uvicorn (ASGI server)
- pytest 9.0.2

**Agent Framework:**
- agent_labs (local package)
- Providers: MockProvider, OllamaProvider, OpenAIProvider

## Implementation Details

**Architecture:**
- Multi-provider support with factory pattern
- Dynamic provider instantiation
- Type-safe TypeScript frontend and Pydantic backend
- Async/await throughout for responsiveness
- Comprehensive error handling and validation

**What Works:**
- 3/6 providers fully functional (Mock, Ollama, OpenAI)
- Provider selection with beautiful gradient UI
- Dynamic model loading per provider
- API key validation and management
- Real-time chat interface
- Response metadata (provider, model, latency)

**Known Limitations:**
- Anthropic, Google, Azure providers not yet implemented
- API key validation is format-only (not live API test)
- Session persistence is in-memory only
- No frontend component tests yet

**Future Roadmap:**
- [ ] Implement remaining providers (Anthropic, Google, Azure)
- [ ] Live API key validation
- [ ] Frontend component tests
- [ ] Database-backed session persistence
- [ ] Conversation export/import
- [ ] User authentication
- [ ] Usage analytics

## Current Status ✅

| Component | Status |
|-----------|--------|
| **Backend Tests** | ✅ 19/19 PASSING |
| **Integration Tests** | ✅ ALL PASSING |
| **Frontend Build** | ✅ COMPILING (0 errors) |
| **API Endpoints** | ✅ WORKING |
| **TypeScript** | ✅ STRICT MODE |
| **Chat Interface** | ✅ FULLY FUNCTIONAL |
| **Multi-Provider Support** | ✅ FULLY FUNCTIONAL |  
