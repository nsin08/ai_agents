# Implementation Guide: Web-Based Agent Chat Interface

**Story**: #57 - Web-Based Agent Chat Interface with Debug Mode  
**Sub-Issues**: #63 (57.1), #64 (57.2), #65 (57.3)  
**Branch**: `feature/57-web-agent-chat-interface`  
**Duration**: 3-5 days  
**Last Updated**: Jan 20, 2026

---

## Table of Contents

1. [Branching Strategy](#branching-strategy)
2. [Overview](#overview)
3. [Architecture](#architecture)
4. [Phase 1: MVP Foundation (Issue #63)](#phase-1-mvp-foundation-issue-63)
5. [Phase 2: Multi-Provider Support (Issue #64)](#phase-2-multi-provider-support-issue-64)
6. [Phase 3: Debug & Polish (Issue #65)](#phase-3-debug-polish-issue-65)
7. [Testing Strategy](#testing-strategy)
8. [Deployment](#deployment)
9. [Future: Agent Core Integration](#future-agent-core-integration)

---

## Branching Strategy (Option C: Framework-Aligned)

### Overview

This project follows **Option C** - Sub-issues merge to parent story branch first, then story branch merges to develop.

**Why Option C?**
- ✅ Framework-aligned (space_framework best practices)
- ✅ Maintains parent-child story relationship
- ✅ Single final PR for Story #57
- ✅ Clean commit history grouped by story
- ✅ Sub-issues visible in feature/57 branch commits

### Branch Structure

```
develop (main integration)
    ↑
    └─ feature/57-web-agent-chat-interface (Story branch)
            ↑ ↑ ↑
            │ │ └─ feature/65-debug-polish → (merge to 57)
            │ └─── feature/64-multi-provider → (merge to 57)
            └───── feature/63-mvp-foundation → (merge to 57)
```

### Workflow Per Phase

#### Phase 1: MVP Foundation

```bash
# Create sub-issue branch from feature/57
git checkout feature/57-web-agent-chat-interface
git checkout -b feature/63-mvp-foundation

# Work on Phase 1
# ... implement code ...
git add .
git commit -m "feat(63): MVP foundation - FastAPI + React scaffold"
git push origin feature/63-mvp-foundation

# Create PR: feature/63-mvp-foundation → feature/57-web-agent-chat-interface
# (NOT to develop)

# After review + tests pass:
# MERGE PR to feature/57-web-agent-chat-interface
```

#### Phase 2: Multi-Provider Support

```bash
# Create sub-issue branch from feature/57
git checkout feature/57-web-agent-chat-interface
git pull origin feature/57-web-agent-chat-interface  # Get Phase 1 code
git checkout -b feature/64-multi-provider

# Work on Phase 2 (Phase 1 code already in branch)
# ... implement code ...
git add .
git commit -m "feat(64): Multi-provider support - 6 providers"
git push origin feature/64-multi-provider

# Create PR: feature/64-multi-provider → feature/57-web-agent-chat-interface
# (NOT to develop)

# After review + tests pass:
# MERGE PR to feature/57-web-agent-chat-interface
```

#### Phase 3: Debug & Polish

```bash
# Create sub-issue branch from feature/57
git checkout feature/57-web-agent-chat-interface
git pull origin feature/57-web-agent-chat-interface  # Get Phase 1 + 2 code
git checkout -b feature/65-debug-polish

# Work on Phase 3 (Phase 1 + 2 code already in branch)
# ... implement code ...
git add .
git commit -m "feat(65): Debug mode, export & polish"
git push origin feature/65-debug-polish

# Create PR: feature/65-debug-polish → feature/57-web-agent-chat-interface
# (NOT to develop)

# After review + tests pass:
# MERGE PR to feature/57-web-agent-chat-interface
```

#### Final: Story Complete

```bash
# After all 3 phases merged to feature/57
git checkout feature/57-web-agent-chat-interface
git pull origin feature/57-web-agent-chat-interface

# Create final PR: feature/57-web-agent-chat-interface → develop
# Title: "feat(#57): Web-Based Agent Chat Interface with Debug Mode - Complete"
# This PR contains all 3 phases

# After final review + all tests pass:
# CODEOWNER merges to develop
```

### PR Titles & Linking

**Phase 1 PR Title**: `feat(#63): MVP Foundation - Basic Chat with Mock Provider`  
**PR Description**: Link to #63 (will be squashed)

**Phase 2 PR Title**: `feat(#64): Multi-Provider Support (6 Providers)`  
**PR Description**: Link to #64

**Phase 3 PR Title**: `feat(#65): Debug Mode, Export & Polish - Production Ready`  
**PR Description**: Link to #65

**Final PR Title**: `feat(#57): Web-Based Agent Chat Interface with Debug Mode - Complete`  
**PR Description**: Closes #57 (links all sub-issues)

### Key Points

✅ **Each phase**:
- Branches from feature/57 (not develop)
- PRs back to feature/57
- Only merged to feature/57 after review

✅ **Final PR**:
- feature/57 → develop
- Only CODEOWNER can merge
- Contains all Phase 1 + 2 + 3 commits

✅ **Never**:
- Branch from previous phase branch
- Push directly to feature/57 (use PRs)
- Merge sub-issues directly to develop

---

## Overview

### Objective
Build a production-ready web-based chat interface for AI agent interaction with multi-provider support, debug mode, and conversation management.

### Phased Approach

| Phase | Sub-Issue | Duration | Key Deliverables |
|---|---|---|---|
| **1** | #63 (57.1) | 1-2 days | FastAPI + React scaffold, ServiceInterface abstraction, Mock provider |
| **2** | #64 (57.2) | 1-2 days | 6 provider support, API key management, provider selection UI |
| **3** | #65 (57.3) | 1 day | Debug panel, export, mobile responsive, accessibility |

### Technology Stack

**Frontend**: React 18+, Vite, CSS3  
**Backend**: FastAPI (Python 3.11+), Pydantic, uvicorn  
**Core**: agent_labs (orchestrator, providers, tools, memory)  
**Future**: agent_core (swappable via env var)

---

## Architecture

### Three-Layer Design

```
┌─────────────────────────────────────────────────────────┐
│  Layer 1: FRONTEND (React)                              │
│  ├─ ChatInterface (message display, input)              │
│  ├─ ProviderSelector (provider/model selection)         │
│  ├─ DebugPanel (metrics display)                        │
│  ├─ ConfigPanel (agent settings)                        │
│  └─ ConversationHistory (export, download)              │
└──────────────────────┬──────────────────────────────────┘
                       │ HTTP POST /api/chat/send
                       ↓
┌─────────────────────────────────────────────────────────┐
│  Layer 2: FASTAPI BACKEND                               │
│  ├─ Routes: /api/chat/send, /api/providers, /api/config│
│  ├─ Dependency Injection: Depends(agent_service)        │
│  ├─ Request Validation: Pydantic models                 │
│  └─ Session Management: In-memory                       │
└──────────────────────┬──────────────────────────────────┘
                       │ Depends() injects service
                       ↓
┌─────────────────────────────────────────────────────────┐
│  Layer 3: SERVICE ABSTRACTION (Backend Switching)       │
│  ├─ AgentServiceInterface (Protocol)                    │
│  ├─ AgentLabsService (uses agent_labs)     ← Phase 1-3 │
│  └─ AgentCoreService (uses agent_core)     ← Future    │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────┐
│  Layer 4: AGENT CORE                                    │
│  ├─ agent_labs (current)                                │
│  │   ├─ Orchestrator                                    │
│  │   ├─ Provider Factory                                │
│  │   ├─ LLM Providers (Mock, Ollama, OpenAI, etc.)     │
│  │   └─ Memory, Tools, Observability                   │
│  └─ agent_core (future - swappable)                     │
└─────────────────────────────────────────────────────────┘
```

### Key Architectural Principles

1. **ServiceInterface Abstraction**: Protocol-based interface enables backend swapping without UI changes
2. **Environment Variable Control**: `AGENT_CORE_BACKEND` determines which service is injected
3. **Backward Compatible Responses**: Both backends return identical response structure
4. **No API Versioning Needed**: Backend switch is server-side only
5. **Stateless Backend**: Easy horizontal scaling

---

## Phase 1: MVP Foundation (Issue #63)

**Duration**: 1-2 days (8-16 hours)  
**Branch**: `feature/57-mvp-foundation`  
**Goal**: Basic chat with Mock provider, FastAPI + React scaffold, ServiceInterface abstraction

### File Structure to Create

```
web/
├── README.md                          # User guide
├── requirements.txt                   # Python dependencies
├── package.json                       # Node dependencies (frontend)
├── .env.example                       # Environment variables template
├── docker-compose.yml                 # Local dev environment (optional)
├── backend/
│   ├── main.py                       # FastAPI app entry point
│   ├── config.py                     # Config + dependency injection
│   ├── models.py                     # Pydantic request/response models
│   ├── api/
│   │   ├── __init__.py
│   │   └── chat.py                   # Chat endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── interfaces.py             # ServiceInterface Protocol
│   │   └── agent_labs_impl.py        # AgentLabsService implementation
│   └── tests/
│       ├── test_agent_service.py
│       ├── test_api_endpoints.py
│       └── test_service_interface.py
└── frontend/
    ├── public/
    │   ├── index.html
    │   └── favicon.ico
    ├── src/
    │   ├── main.jsx                  # Vite entry point
    │   ├── App.jsx                   # Root component
    │   ├── App.css                   # Global styles
    │   ├── components/
    │   │   ├── ChatInterface.jsx
    │   │   ├── Message.jsx
    │   │   └── LoadingIndicator.jsx
    │   ├── services/
    │   │   └── api.js                # API client
    │   └── __tests__/
    │       ├── ChatInterface.test.jsx
    │       └── Message.test.jsx
    ├── vite.config.js
    └── package.json
```

### Step 1.1: Backend Scaffold

#### `web/backend/requirements.txt`
```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
pydantic-settings==2.1.0
python-dotenv==1.0.0
pytest==7.4.4
pytest-asyncio==0.23.3
httpx==0.26.0
```

#### `web/backend/models.py`
```python
"""Request/Response models for API."""
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str = Field(..., min_length=1, description="User message")
    provider: str = Field(default="mock", description="LLM provider to use")
    model: str = Field(default="mock-model", description="Model name")
    config: Dict[str, Any] = Field(default_factory=dict, description="Agent config")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    success: bool = Field(..., description="Whether request succeeded")
    response: str = Field(..., description="Agent response text")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Debug metadata")


class ErrorResponse(BaseModel):
    """Error response model."""
    success: bool = Field(default=False)
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Error details")
```

#### `web/backend/services/interfaces.py`
```python
"""Service interface definitions (abstraction layer)."""
from typing import Protocol, Dict, Any
from backend.models import ChatResponse


class AgentServiceInterface(Protocol):
    """
    Protocol defining the contract for agent services.
    
    This abstraction allows swapping between agent_labs and agent_core
    without changing API routes or frontend code.
    """
    
    async def process_message(
        self,
        message: str,
        provider: str,
        model: str,
        config: Dict[str, Any]
    ) -> ChatResponse:
        """
        Process a user message and return agent response.
        
        Args:
            message: User's input message
            provider: LLM provider name
            model: Model name
            config: Agent configuration
            
        Returns:
            ChatResponse with response text and metadata
        """
        ...
```

#### `web/backend/services/agent_labs_impl.py`
```python
"""AgentLabsService implementation using agent_labs core."""
import time
from typing import Dict, Any
from backend.models import ChatResponse
from backend.services.interfaces import AgentServiceInterface

# Import agent_labs components
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from agent_labs.llm_providers import MockProvider, OllamaProvider
from agent_labs.orchestrator import Agent, AgentContext
from agent_labs.tools import ToolRegistry


class AgentLabsService(AgentServiceInterface):
    """Service implementation using agent_labs core."""
    
    def __init__(self):
        """Initialize service with agent_labs components."""
        self.tool_registry = ToolRegistry()
        # Register any default tools here if needed
    
    async def process_message(
        self,
        message: str,
        provider: str,
        model: str,
        config: Dict[str, Any]
    ) -> ChatResponse:
        """
        Process message using agent_labs orchestrator.
        
        Args:
            message: User message
            provider: Provider name (mock, ollama, etc.)
            model: Model name
            config: Agent config (max_turns, temperature, etc.)
            
        Returns:
            ChatResponse with agent reply and metadata
        """
        start_time = time.time()
        
        try:
            # Create provider
            if provider == "mock":
                llm_provider = MockProvider(responses=["This is a mock response from agent_labs."])
            elif provider == "ollama":
                llm_provider = OllamaProvider(
                    model=model,
                    base_url=config.get("base_url", "http://localhost:11434")
                )
            else:
                # For Phase 1, only Mock provider supported
                llm_provider = MockProvider(responses=[f"Provider '{provider}' not yet supported in Phase 1."])
            
            # Create agent context
            context = AgentContext(
                user_message=message,
                max_turns=config.get("max_turns", 3),
                timeout_seconds=config.get("timeout", 30)
            )
            
            # Create and run agent
            agent = Agent(
                llm_provider=llm_provider,
                tool_registry=self.tool_registry
            )
            
            result = await agent.run(context)
            
            # Calculate metrics
            latency_ms = (time.time() - start_time) * 1000
            
            # Build response
            return ChatResponse(
                success=True,
                response=result.get("response", "No response generated"),
                metadata={
                    "provider": provider,
                    "model": model,
                    "latency_ms": round(latency_ms, 2),
                    "tokens_used": result.get("tokens_used", 0),
                    "max_turns": config.get("max_turns", 3),
                    "backend": "agent_labs"
                }
            )
            
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            return ChatResponse(
                success=False,
                response=f"Error: {str(e)}",
                metadata={
                    "provider": provider,
                    "model": model,
                    "latency_ms": round(latency_ms, 2),
                    "error": str(e),
                    "backend": "agent_labs"
                }
            )
```

#### `web/backend/config.py`
```python
"""Application configuration and dependency injection."""
import os
from typing import Generator
from backend.services.interfaces import AgentServiceInterface
from backend.services.agent_labs_impl import AgentLabsService


# Environment variables
AGENT_CORE_BACKEND = os.getenv("AGENT_CORE_BACKEND", "agent_labs")


def agent_service() -> Generator[AgentServiceInterface, None, None]:
    """
    Dependency injection for agent service.
    
    This function is called by FastAPI's Depends() mechanism.
    It returns the appropriate service based on AGENT_CORE_BACKEND env var.
    
    Yields:
        AgentServiceInterface implementation
    """
    if AGENT_CORE_BACKEND == "agent_labs":
        service = AgentLabsService()
    elif AGENT_CORE_BACKEND == "agent_core":
        # Future: import AgentCoreService
        # service = AgentCoreService()
        raise NotImplementedError("agent_core backend not yet implemented")
    else:
        raise ValueError(f"Unknown backend: {AGENT_CORE_BACKEND}")
    
    yield service
```

#### `web/backend/api/chat.py`
```python
"""Chat API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from backend.models import ChatRequest, ChatResponse, ErrorResponse
from backend.services.interfaces import AgentServiceInterface
from backend.config import agent_service

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/send", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    service: AgentServiceInterface = Depends(agent_service)
) -> ChatResponse:
    """
    Send a message to the agent.
    
    Args:
        request: Chat request with message and config
        service: Injected agent service (agent_labs or agent_core)
        
    Returns:
        ChatResponse with agent reply and metadata
    """
    try:
        response = await service.process_message(
            message=request.message,
            provider=request.provider,
            model=request.model,
            config=request.config
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

#### `web/backend/main.py`
```python
"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api import chat

app = FastAPI(
    title="Agent Chat API",
    description="Web-based agent chat interface API",
    version="0.1.0"
)

# CORS middleware (allow frontend access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite + CRA
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Agent Chat API",
        "version": "0.1.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
```

### Step 1.2: Frontend Scaffold

#### `web/frontend/package.json`
```json
{
  "name": "agent-chat-frontend",
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "test": "vitest"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.2.1",
    "vite": "^5.0.11",
    "vitest": "^1.2.0",
    "@testing-library/react": "^14.1.2",
    "@testing-library/jest-dom": "^6.2.0"
  }
}
```

#### `web/frontend/vite.config.js`
```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
```

#### `web/frontend/src/services/api.js`
```javascript
/**
 * API client for backend communication.
 */

const API_BASE = '/api';

/**
 * Send a message to the agent.
 * @param {string} message - User message
 * @param {Object} config - Agent configuration
 * @returns {Promise<Object>} Response from agent
 */
export async function sendMessage(message, config = {}) {
  const response = await fetch(`${API_BASE}/chat/send`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message,
      provider: config.provider || 'mock',
      model: config.model || 'mock-model',
      config: {
        max_turns: config.maxTurns || 3,
        temperature: config.temperature || 0.7,
        timeout: config.timeout || 30
      }
    })
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Request failed');
  }

  return await response.json();
}
```

#### `web/frontend/src/components/Message.jsx`
```jsx
/**
 * Message component - Displays a single chat message.
 */
import React from 'react';

export default function Message({ role, content, timestamp }) {
  const isUser = role === 'user';
  
  return (
    <div className={`message ${isUser ? 'user-message' : 'assistant-message'}`}>
      <div className="message-header">
        <span className="message-role">{isUser ? 'You' : 'Agent'}</span>
        <span className="message-time">
          {new Date(timestamp).toLocaleTimeString()}
        </span>
      </div>
      <div className="message-content">
        {content}
      </div>
    </div>
  );
}
```

#### `web/frontend/src/components/ChatInterface.jsx`
```jsx
/**
 * ChatInterface - Main chat component.
 */
import React, { useState, useRef, useEffect } from 'react';
import Message from './Message';
import { sendMessage } from '../services/api';

export default function ChatInterface() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage = {
      role: 'user',
      content: input,
      timestamp: Date.now()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);
    setError(null);

    try {
      const response = await sendMessage(input, {
        provider: 'mock',
        model: 'mock-model'
      });

      const assistantMessage = {
        role: 'assistant',
        content: response.response,
        timestamp: Date.now(),
        metadata: response.metadata
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      setError(err.message);
      const errorMessage = {
        role: 'assistant',
        content: `Error: ${err.message}`,
        timestamp: Date.now(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <h1>Agent Chat</h1>
        <span className="provider-badge">Mock Provider</span>
      </div>

      <div className="messages-container">
        {messages.length === 0 && (
          <div className="empty-state">
            <p>Send a message to start chatting with the agent.</p>
          </div>
        )}
        {messages.map((msg, idx) => (
          <Message
            key={idx}
            role={msg.role}
            content={msg.content}
            timestamp={msg.timestamp}
          />
        ))}
        {loading && (
          <div className="loading-indicator">
            <span>Agent thinking...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="input-container">
        {error && (
          <div className="error-banner">
            {error}
          </div>
        )}
        <div className="input-wrapper">
          <textarea
            className="message-input"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message... (Enter to send, Shift+Enter for new line)"
            rows={3}
            disabled={loading}
          />
          <button
            className="send-button"
            onClick={handleSend}
            disabled={!input.trim() || loading}
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
```

#### `web/frontend/src/App.jsx`
```jsx
import React from 'react';
import ChatInterface from './components/ChatInterface';
import './App.css';

function App() {
  return (
    <div className="app">
      <ChatInterface />
    </div>
  );
}

export default App;
```

#### `web/frontend/src/App.css`
```css
/* Basic styling for Phase 1 MVP */
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  background: #f5f5f5;
}

.app {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
}

.chat-interface {
  width: 100%;
  max-width: 800px;
  height: 90vh;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-header {
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chat-header h1 {
  font-size: 24px;
  font-weight: 600;
}

.provider-badge {
  background: #e3f2fd;
  color: #1976d2;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.empty-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  font-style: italic;
}

.message {
  padding: 12px 16px;
  border-radius: 8px;
  max-width: 80%;
}

.user-message {
  background: #1976d2;
  color: white;
  align-self: flex-end;
}

.assistant-message {
  background: #f5f5f5;
  color: #333;
  align-self: flex-start;
}

.message-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
  font-size: 12px;
  opacity: 0.8;
}

.message-content {
  font-size: 14px;
  line-height: 1.5;
  white-space: pre-wrap;
}

.loading-indicator {
  padding: 12px;
  text-align: center;
  color: #666;
  font-style: italic;
}

.input-container {
  border-top: 1px solid #e0e0e0;
  padding: 20px;
}

.error-banner {
  background: #ffebee;
  color: #c62828;
  padding: 10px;
  border-radius: 6px;
  margin-bottom: 10px;
  font-size: 14px;
}

.input-wrapper {
  display: flex;
  gap: 12px;
}

.message-input {
  flex: 1;
  padding: 12px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  resize: none;
  font-family: inherit;
}

.message-input:focus {
  outline: none;
  border-color: #1976d2;
}

.send-button {
  padding: 12px 24px;
  background: #1976d2;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.send-button:hover:not(:disabled) {
  background: #1565c0;
}

.send-button:disabled {
  background: #ccc;
  cursor: not-allowed;
}
```

### Step 1.3: Testing

#### `web/backend/tests/test_api_endpoints.py`
```python
"""Test API endpoints."""
import pytest
from httpx import AsyncClient
from backend.main import app


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test root endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data


@pytest.mark.asyncio
async def test_health_endpoint():
    """Test health check endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_chat_send_endpoint():
    """Test chat send endpoint with mock provider."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/chat/send",
            json={
                "message": "Hello",
                "provider": "mock",
                "model": "mock-model",
                "config": {}
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "response" in data
        assert "metadata" in data
        assert data["metadata"]["provider"] == "mock"
        assert data["metadata"]["backend"] == "agent_labs"


@pytest.mark.asyncio
async def test_chat_send_validation():
    """Test request validation."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/chat/send",
            json={"message": ""}  # Empty message should fail
        )
        assert response.status_code == 422  # Validation error
```

### Step 1.4: Running Phase 1

#### Setup Backend
```bash
cd web/backend
python -m pip install -r requirements.txt
export AGENT_CORE_BACKEND=agent_labs
export LLM_PROVIDER=mock
uvicorn main:app --reload
```

#### Setup Frontend
```bash
cd web/frontend
npm install
npm run dev
```

#### Run Tests
```bash
# Backend tests
cd web/backend
pytest tests/ -v

# Frontend tests (after Phase 1.2 complete)
cd web/frontend
npm test
```

### Phase 1 Acceptance Criteria

- [ ] Backend server starts without errors
- [ ] Frontend dev server starts without errors
- [ ] User can send message and receive mock response
- [ ] Response displays in chat interface with timestamp
- [ ] Loading indicator shows while processing
- [ ] Error messages display properly
- [ ] FastAPI auto-docs accessible at http://localhost:8000/docs
- [ ] All backend tests pass
- [ ] ServiceInterface abstraction layer implemented
- [ ] Environment variable `AGENT_CORE_BACKEND` controls backend selection

---

## Phase 2: Multi-Provider Support (Issue #64)

**Duration**: 1-2 days (8-16 hours)  
**Branch**: `feature/57-multi-provider`  
**Dependencies**: Phase 1 complete and merged  
**Goal**: Support 6 LLM providers with provider selection UI and API key management

### Providers to Implement

1. ✅ Mock (from Phase 1)
2. Ollama (local)
3. OpenAI (GPT-3.5, GPT-4)
4. Anthropic (Claude)
5. Google (Gemini)
6. Azure OpenAI

### Step 2.1: Backend Provider Management

#### Update `web/backend/models.py` (add provider endpoints)
```python
# Add to existing file

class ProviderInfo(BaseModel):
    """Provider information."""
    name: str
    display_name: str
    requires_api_key: bool
    default_model: str
    available_models: List[str]


class ValidateKeyRequest(BaseModel):
    """Request to validate API key."""
    provider: str
    api_key: str


class ValidateKeyResponse(BaseModel):
    """Response from key validation."""
    valid: bool
    message: str
```

#### Create `web/backend/api/providers.py`
```python
"""Provider management endpoints."""
from typing import List
from fastapi import APIRouter, HTTPException
from backend.models import ProviderInfo, ValidateKeyRequest, ValidateKeyResponse

router = APIRouter(prefix="/api/providers", tags=["providers"])


PROVIDERS = {
    "mock": ProviderInfo(
        name="mock",
        display_name="Mock Provider",
        requires_api_key=False,
        default_model="mock-model",
        available_models=["mock-model"]
    ),
    "ollama": ProviderInfo(
        name="ollama",
        display_name="Ollama (Local)",
        requires_api_key=False,
        default_model="llama3.2",
        available_models=["llama3.2", "mistral", "codellama", "phi3"]
    ),
    "openai": ProviderInfo(
        name="openai",
        display_name="OpenAI",
        requires_api_key=True,
        default_model="gpt-3.5-turbo",
        available_models=["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]
    ),
    "anthropic": ProviderInfo(
        name="anthropic",
        display_name="Anthropic (Claude)",
        requires_api_key=True,
        default_model="claude-3-sonnet",
        available_models=["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"]
    ),
    "google": ProviderInfo(
        name="google",
        display_name="Google (Gemini)",
        requires_api_key=True,
        default_model="gemini-pro",
        available_models=["gemini-pro", "gemini-ultra"]
    ),
    "azure": ProviderInfo(
        name="azure",
        display_name="Azure OpenAI",
        requires_api_key=True,
        default_model="gpt-35-turbo",
        available_models=["gpt-35-turbo", "gpt-4"]
    )
}


@router.get("/", response_model=List[ProviderInfo])
async def list_providers():
    """List all available providers."""
    return list(PROVIDERS.values())


@router.get("/{provider}/models")
async def get_provider_models(provider: str):
    """Get available models for a provider."""
    if provider not in PROVIDERS:
        raise HTTPException(status_code=404, detail=f"Provider '{provider}' not found")
    
    return {
        "provider": provider,
        "models": PROVIDERS[provider].available_models
    }


@router.post("/validate-key", response_model=ValidateKeyResponse)
async def validate_api_key(request: ValidateKeyRequest):
    """
    Validate API key for a provider.
    
    Note: For Phase 2, we do basic validation.
    In production, you'd make actual API calls to verify.
    """
    if request.provider not in PROVIDERS:
        return ValidateKeyResponse(
            valid=False,
            message=f"Provider '{request.provider}' not found"
        )
    
    provider_info = PROVIDERS[request.provider]
    
    if not provider_info.requires_api_key:
        return ValidateKeyResponse(
            valid=True,
            message="Provider does not require API key"
        )
    
    # Basic validation (key format)
    if not request.api_key or len(request.api_key) < 10:
        return ValidateKeyResponse(
            valid=False,
            message="API key appears invalid (too short)"
        )
    
    # Provider-specific validation
    if request.provider == "openai" and not request.api_key.startswith("sk-"):
        return ValidateKeyResponse(
            valid=False,
            message="OpenAI API keys should start with 'sk-'"
        )
    
    if request.provider == "anthropic" and not request.api_key.startswith("sk-ant-"):
        return ValidateKeyResponse(
            valid=False,
            message="Anthropic API keys should start with 'sk-ant-'"
        )
    
    # If basic checks pass, assume valid
    # In production, you'd make a test API call
    return ValidateKeyResponse(
        valid=True,
        message="API key format appears valid"
    )
```

#### Update `web/backend/services/agent_labs_impl.py`
```python
"""Updated AgentLabsService with multi-provider support."""
import time
import os
from typing import Dict, Any
from backend.models import ChatResponse
from backend.services.interfaces import AgentServiceInterface

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from agent_labs.llm_providers import (
    MockProvider,
    OllamaProvider,
    OpenAIProvider,
    AnthropicProvider,
    GoogleProvider,
    AzureOpenAIProvider
)
from agent_labs.orchestrator import Agent, AgentContext
from agent_labs.tools import ToolRegistry


class AgentLabsService(AgentServiceInterface):
    """Service implementation using agent_labs core with multi-provider support."""
    
    def __init__(self):
        """Initialize service with agent_labs components."""
        self.tool_registry = ToolRegistry()
    
    def _create_provider(self, provider: str, model: str, api_key: str = None, config: Dict = None):
        """
        Create LLM provider based on provider name.
        
        Args:
            provider: Provider name
            model: Model name
            api_key: API key (for cloud providers)
            config: Additional config
            
        Returns:
            Provider instance
        """
        config = config or {}
        
        if provider == "mock":
            return MockProvider(responses=["This is a mock response."])
        
        elif provider == "ollama":
            return OllamaProvider(
                model=model,
                base_url=config.get("base_url", "http://localhost:11434")
            )
        
        elif provider == "openai":
            if not api_key:
                api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OpenAI API key required")
            return OpenAIProvider(model=model, api_key=api_key)
        
        elif provider == "anthropic":
            if not api_key:
                api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("Anthropic API key required")
            return AnthropicProvider(model=model, api_key=api_key)
        
        elif provider == "google":
            if not api_key:
                api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("Google API key required")
            return GoogleProvider(model=model, api_key=api_key)
        
        elif provider == "azure":
            if not api_key:
                api_key = os.getenv("AZURE_OPENAI_API_KEY")
            endpoint = config.get("endpoint") or os.getenv("AZURE_OPENAI_ENDPOINT")
            if not api_key or not endpoint:
                raise ValueError("Azure OpenAI requires API key and endpoint")
            return AzureOpenAIProvider(
                model=model,
                api_key=api_key,
                endpoint=endpoint
            )
        
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    async def process_message(
        self,
        message: str,
        provider: str,
        model: str,
        config: Dict[str, Any]
    ) -> ChatResponse:
        """Process message with selected provider."""
        start_time = time.time()
        api_key = config.get("api_key")
        
        try:
            # Create provider
            llm_provider = self._create_provider(provider, model, api_key, config)
            
            # Create agent context
            context = AgentContext(
                user_message=message,
                max_turns=config.get("max_turns", 3),
                timeout_seconds=config.get("timeout", 30)
            )
            
            # Create and run agent
            agent = Agent(
                llm_provider=llm_provider,
                tool_registry=self.tool_registry
            )
            
            result = await agent.run(context)
            
            # Calculate metrics
            latency_ms = (time.time() - start_time) * 1000
            
            # Build response
            return ChatResponse(
                success=True,
                response=result.get("response", "No response generated"),
                metadata={
                    "provider": provider,
                    "model": model,
                    "latency_ms": round(latency_ms, 2),
                    "tokens_used": result.get("tokens_used", 0),
                    "max_turns": config.get("max_turns", 3),
                    "backend": "agent_labs"
                }
            )
            
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            return ChatResponse(
                success=False,
                response=f"Error: {str(e)}",
                metadata={
                    "provider": provider,
                    "model": model,
                    "latency_ms": round(latency_ms, 2),
                    "error": str(e),
                    "backend": "agent_labs"
                }
            )
```

#### Update `web/backend/main.py`
```python
# Add provider router
from backend.api import chat, providers

# ... existing code ...

app.include_router(chat.router)
app.include_router(providers.router)  # NEW
```

### Step 2.2: Frontend Provider Selection UI

#### Create `web/frontend/src/components/ProviderSelector.jsx`
```jsx
/**
 * ProviderSelector - Provider and model selection UI.
 */
import React, { useState, useEffect } from 'react';

export default function ProviderSelector({ 
  selectedProvider, 
  selectedModel, 
  apiKey,
  onProviderChange, 
  onModelChange,
  onApiKeyChange 
}) {
  const [providers, setProviders] = useState([]);
  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showApiKey, setShowApiKey] = useState(false);

  // Load providers on mount
  useEffect(() => {
    loadProviders();
  }, []);

  // Load models when provider changes
  useEffect(() => {
    if (selectedProvider) {
      loadModels(selectedProvider);
    }
  }, [selectedProvider]);

  const loadProviders = async () => {
    try {
      const response = await fetch('/api/providers/');
      const data = await response.json();
      setProviders(data);
      
      if (data.length > 0 && !selectedProvider) {
        onProviderChange(data[0].name);
      }
    } catch (error) {
      console.error('Failed to load providers:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadModels = async (provider) => {
    try {
      const response = await fetch(`/api/providers/${provider}/models`);
      const data = await response.json();
      setModels(data.models);
      
      if (data.models.length > 0 && !selectedModel) {
        onModelChange(data.models[0]);
      }
    } catch (error) {
      console.error('Failed to load models:', error);
    }
  };

  const currentProvider = providers.find(p => p.name === selectedProvider);
  const requiresApiKey = currentProvider?.requires_api_key;

  const maskApiKey = (key) => {
    if (!key || key.length < 8) return key;
    return key.substring(0, 4) + '*'.repeat(key.length - 4);
  };

  if (loading) return <div>Loading providers...</div>;

  return (
    <div className="provider-selector">
      <div className="selector-group">
        <label>Provider</label>
        <select 
          value={selectedProvider} 
          onChange={(e) => onProviderChange(e.target.value)}
          className="select-input"
        >
          {providers.map(provider => (
            <option key={provider.name} value={provider.name}>
              {provider.display_name}
            </option>
          ))}
        </select>
      </div>

      <div className="selector-group">
        <label>Model</label>
        <select 
          value={selectedModel} 
          onChange={(e) => onModelChange(e.target.value)}
          className="select-input"
        >
          {models.map(model => (
            <option key={model} value={model}>
              {model}
            </option>
          ))}
        </select>
      </div>

      {requiresApiKey && (
        <div className="selector-group">
          <label>
            API Key
            <button 
              type="button"
              onClick={() => setShowApiKey(!showApiKey)}
              className="toggle-visibility"
            >
              {showApiKey ? '🙈 Hide' : '👁️ Show'}
            </button>
          </label>
          <input
            type={showApiKey ? 'text' : 'password'}
            value={apiKey || ''}
            onChange={(e) => onApiKeyChange(e.target.value)}
            placeholder={`Enter ${currentProvider.display_name} API key`}
            className="text-input"
          />
          {apiKey && !showApiKey && (
            <div className="masked-key">
              {maskApiKey(apiKey)}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
```

#### Update `web/frontend/src/components/ChatInterface.jsx`
```jsx
// Add ProviderSelector import and state
import ProviderSelector from './ProviderSelector';

export default function ChatInterface() {
  // ... existing state ...
  const [provider, setProvider] = useState('mock');
  const [model, setModel] = useState('mock-model');
  const [apiKey, setApiKey] = useState('');

  const handleSend = async () => {
    // ... existing code ...
    
    try {
      const response = await sendMessage(input, {
        provider,  // NEW
        model,     // NEW
        apiKey     // NEW (if required)
      });
      
      // ... rest of existing code ...
    }
  };

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <h1>Agent Chat</h1>
        <ProviderSelector
          selectedProvider={provider}
          selectedModel={model}
          apiKey={apiKey}
          onProviderChange={setProvider}
          onModelChange={setModel}
          onApiKeyChange={setApiKey}
        />
      </div>
      {/* ... rest of existing JSX ... */}
    </div>
  );
}
```

#### Update `web/frontend/src/services/api.js`
```javascript
// Update sendMessage to include apiKey
export async function sendMessage(message, config = {}) {
  const requestBody = {
    message,
    provider: config.provider || 'mock',
    model: config.model || 'mock-model',
    config: {
      max_turns: config.maxTurns || 3,
      temperature: config.temperature || 0.7,
      timeout: config.timeout || 30
    }
  };

  // Add API key if provided
  if (config.apiKey) {
    requestBody.config.api_key = config.apiKey;
  }

  const response = await fetch(`${API_BASE}/chat/send`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(requestBody)
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Request failed');
  }

  return await response.json();
}
```

### Phase 2 Acceptance Criteria

- [ ] User can select from 6 providers in dropdown
- [ ] Model list updates dynamically based on provider
- [ ] User can enter API keys for cloud providers
- [ ] API key is masked in UI (show first 4 chars + asterisks)
- [ ] Chat works with all 6 providers
- [ ] `/api/providers/` returns all providers
- [ ] `/api/providers/{provider}/models` returns correct models
- [ ] Error messages helpful for missing API keys
- [ ] All integration tests pass
- [ ] Response format consistent across providers

---

## Phase 3: Debug & Polish (Issue #65)

**Duration**: 1 day (6-10 hours)  
**Branch**: `feature/57-debug-polish`  
**Dependencies**: Phase 2 complete and merged  
**Goal**: Debug panel, export, mobile responsive, accessibility

### Step 3.1: Debug Panel

#### Create `web/frontend/src/components/DebugPanel.jsx`
```jsx
/**
 * DebugPanel - Display agent debug information.
 */
import React, { useState } from 'react';

export default function DebugPanel({ metadata, visible }) {
  const [copied, setCopied] = useState(false);

  if (!visible || !metadata) return null;

  const copyToClipboard = () => {
    const text = JSON.stringify(metadata, null, 2);
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="debug-panel">
      <div className="debug-header">
        <h3>Debug Information</h3>
        <button onClick={copyToClipboard} className="copy-button">
          {copied ? '✓ Copied' : '📋 Copy'}
        </button>
      </div>
      
      <div className="debug-content">
        <div className="debug-row">
          <span className="debug-label">Provider:</span>
          <span className="debug-value">{metadata.provider}</span>
        </div>
        
        <div className="debug-row">
          <span className="debug-label">Model:</span>
          <span className="debug-value">{metadata.model}</span>
        </div>
        
        <div className="debug-row">
          <span className="debug-label">Latency:</span>
          <span className="debug-value">{metadata.latency_ms}ms</span>
        </div>
        
        <div className="debug-row">
          <span className="debug-label">Tokens:</span>
          <span className="debug-value">{metadata.tokens_used || 'N/A'}</span>
        </div>
        
        <div className="debug-row">
          <span className="debug-label">Backend:</span>
          <span className="debug-value">{metadata.backend}</span>
        </div>
        
        {metadata.error && (
          <div className="debug-row error">
            <span className="debug-label">Error:</span>
            <span className="debug-value">{metadata.error}</span>
          </div>
        )}
        
        <details className="debug-json">
          <summary>Full Metadata (JSON)</summary>
          <pre>{JSON.stringify(metadata, null, 2)}</pre>
        </details>
      </div>
    </div>
  );
}
```

#### Create `web/frontend/src/components/ConfigPanel.jsx`
```jsx
/**
 * ConfigPanel - Agent configuration settings.
 */
import React from 'react';

export default function ConfigPanel({ config, onChange }) {
  return (
    <div className="config-panel">
      <h3>Agent Configuration</h3>
      
      <div className="config-group">
        <label>
          Max Turns: {config.maxTurns}
          <input
            type="range"
            min="1"
            max="10"
            value={config.maxTurns}
            onChange={(e) => onChange({ ...config, maxTurns: parseInt(e.target.value) })}
          />
        </label>
      </div>
      
      <div className="config-group">
        <label>
          Temperature: {config.temperature}
          <input
            type="range"
            min="0"
            max="2"
            step="0.1"
            value={config.temperature}
            onChange={(e) => onChange({ ...config, temperature: parseFloat(e.target.value) })}
          />
        </label>
      </div>
      
      <div className="config-group">
        <label>
          Timeout (seconds): {config.timeout}
          <input
            type="number"
            min="5"
            max="120"
            value={config.timeout}
            onChange={(e) => onChange({ ...config, timeout: parseInt(e.target.value) })}
          />
        </label>
      </div>
      
      <button 
        onClick={() => onChange({ maxTurns: 3, temperature: 0.7, timeout: 30 })}
        className="reset-button"
      >
        Reset to Defaults
      </button>
    </div>
  );
}
```

### Step 3.2: Export & Conversation Management

#### Add export functions to `web/frontend/src/services/api.js`
```javascript
/**
 * Export conversation as JSON.
 */
export function exportAsJSON(messages) {
  const data = {
    exported_at: new Date().toISOString(),
    message_count: messages.length,
    messages: messages
  };
  
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `conversation-${Date.now()}.json`;
  a.click();
  URL.revokeObjectURL(url);
}

/**
 * Export conversation as Markdown.
 */
export function exportAsMarkdown(messages) {
  let markdown = '# Agent Conversation\n\n';
  markdown += `Exported: ${new Date().toLocaleString()}\n\n`;
  markdown += '---\n\n';
  
  messages.forEach((msg, idx) => {
    const timestamp = new Date(msg.timestamp).toLocaleString();
    markdown += `## ${msg.role === 'user' ? 'User' : 'Agent'} (${timestamp})\n\n`;
    markdown += `${msg.content}\n\n`;
    
    if (msg.metadata) {
      markdown += `**Metadata**: ${JSON.stringify(msg.metadata, null, 2)}\n\n`;
    }
    
    markdown += '---\n\n';
  });
  
  const blob = new Blob([markdown], { type: 'text/markdown' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `conversation-${Date.now()}.md`;
  a.click();
  URL.revokeObjectURL(url);
}
```

### Step 3.3: Mobile Responsive & Dark Mode

#### Update `web/frontend/src/App.css` (add responsive + dark mode)
```css
/* ... existing styles ... */

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  body {
    background: #1a1a1a;
    color: #e0e0e0;
  }

  .chat-interface {
    background: #2a2a2a;
  }

  .chat-header {
    border-bottom-color: #404040;
  }

  .assistant-message {
    background: #3a3a3a;
    color: #e0e0e0;
  }

  .message-input {
    background: #3a3a3a;
    color: #e0e0e0;
    border-color: #505050;
  }
}

/* Mobile responsive */
@media (max-width: 768px) {
  .app {
    padding: 0;
  }

  .chat-interface {
    height: 100vh;
    border-radius: 0;
    max-width: 100%;
  }

  .chat-header {
    flex-direction: column;
    gap: 12px;
  }

  .provider-selector {
    width: 100%;
  }

  .message {
    max-width: 90%;
  }

  .input-wrapper {
    flex-direction: column;
  }

  .send-button {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .chat-header h1 {
    font-size: 20px;
  }

  .message-input {
    font-size: 16px; /* Prevents zoom on iOS */
  }
}

/* Accessibility - Focus indicators */
button:focus-visible,
input:focus-visible,
select:focus-visible,
textarea:focus-visible {
  outline: 2px solid #1976d2;
  outline-offset: 2px;
}

/* High contrast mode support */
@media (prefers-contrast: high) {
  .message {
    border: 2px solid currentColor;
  }

  .send-button {
    border: 2px solid currentColor;
  }
}
```

### Phase 3 Acceptance Criteria

- [ ] Debug panel shows all metrics (tokens, latency, provider, model, backend)
- [ ] Export to JSON works
- [ ] Export to Markdown works
- [ ] Config panel allows tuning agent parameters
- [ ] Reset to defaults button works
- [ ] Mobile responsive on 480px, 768px, 1024px
- [ ] Dark mode works (respects system preference)
- [ ] Keyboard navigation works (Tab, Enter, Escape)
- [ ] WCAG 2.1 AA accessibility verified (axe DevTools)
- [ ] All tests passing
- [ ] Zero console errors

---

## Testing Strategy

### Backend Tests

```bash
# Run all backend tests
cd web/backend
pytest tests/ -v

# Run specific test file
pytest tests/test_api_endpoints.py -v

# Run with coverage
pytest tests/ --cov=backend --cov-report=term-missing
```

### Frontend Tests

```bash
# Run all frontend tests
cd web/frontend
npm test

# Run specific test
npm test -- ChatInterface.test.jsx

# Run with coverage
npm test -- --coverage
```

### Integration Tests (Manual)

**Phase 1 Checklist**:
- [ ] Backend starts without errors
- [ ] Frontend starts without errors
- [ ] Can send message with Mock provider
- [ ] Response displays correctly
- [ ] Loading indicator shows
- [ ] Error handling works

**Phase 2 Checklist**:
- [ ] Can switch between 6 providers
- [ ] Models update dynamically
- [ ] API key input works
- [ ] Chat works with each provider (if keys available)
- [ ] Error messages helpful

**Phase 3 Checklist**:
- [ ] Debug panel displays all metrics
- [ ] Export to JSON/Markdown works
- [ ] Config panel updates settings
- [ ] Mobile layout works (test on phone)
- [ ] Dark mode toggles correctly
- [ ] Keyboard navigation complete

---

## Deployment

### Local Development

```bash
# Terminal 1: Backend
cd web/backend
export AGENT_CORE_BACKEND=agent_labs
export LLM_PROVIDER=mock
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd web/frontend
npm run dev
```

Access at: http://localhost:5173

### Docker Deployment

#### `web/Dockerfile`
```dockerfile
# Multi-stage build for production

# Stage 1: Build frontend
FROM node:20-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Backend + frontend static files
FROM python:3.11-slim
WORKDIR /app

# Install backend dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend/

# Copy frontend build
COPY --from=frontend-build /app/frontend/dist ./static

# Expose port
EXPOSE 8000

# Environment variables
ENV AGENT_CORE_BACKEND=agent_labs
ENV LLM_PROVIDER=mock

# Run
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### `web/docker-compose.yml`
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - AGENT_CORE_BACKEND=agent_labs
      - LLM_PROVIDER=ollama
      - LLM_BASE_URL=http://ollama:11434
    depends_on:
      - ollama
  
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama

volumes:
  ollama_data:
```

### Production Deployment

```bash
# Build and run
docker-compose up --build

# Access at http://localhost:8000
```

---

## Future: Agent Core Integration

### When agent_core is Production-Ready

**Step 1**: Implement `AgentCoreService`

```python
# web/backend/services/agent_core_impl.py
from backend.services.interfaces import AgentServiceInterface
# from agent_core import ... (imports when agent_core exists)

class AgentCoreService(AgentServiceInterface):
    """Service implementation using agent_core."""
    
    async def process_message(self, message, provider, model, config):
        # Use agent_core orchestrator
        # Return ChatResponse (same format as AgentLabsService)
        pass
```

**Step 2**: Update config.py

```python
# web/backend/config.py
def agent_service():
    if AGENT_CORE_BACKEND == "agent_labs":
        service = AgentLabsService()
    elif AGENT_CORE_BACKEND == "agent_core":
        service = AgentCoreService()  # NEW
    else:
        raise ValueError(f"Unknown backend: {AGENT_CORE_BACKEND}")
    
    yield service
```

**Step 3**: Deploy with env var

```bash
# Switch backend
export AGENT_CORE_BACKEND=agent_core
uvicorn backend.main:app --reload
```

**Result**: Zero UI changes, zero API changes, seamless backend swap.

---

## Summary

### Timeline

| Phase | Duration | Key Deliverables |
|---|---|---|
| **Phase 1** | 1-2 days | FastAPI + React + ServiceInterface + Mock |
| **Phase 2** | 1-2 days | 6 providers + API key management |
| **Phase 3** | 1 day | Debug panel + export + polish |
| **Total** | 3-5 days | Production-ready web interface |

### Success Metrics

- ✅ Users can chat with agent from browser
- ✅ Support 6 LLM providers seamlessly
- ✅ Debug mode shows comprehensive metrics
- ✅ Export conversations (JSON/Markdown)
- ✅ Mobile responsive
- ✅ WCAG 2.1 AA accessible
- ✅ Backend swappable via env var (future-proof for agent_core)
- ✅ All tests passing
- ✅ Production deployment ready

### Next Steps

1. **Start Phase 1**: Create `feature/57-mvp-foundation` branch and begin FastAPI + React scaffold
2. **Complete Phase 1**: Merge MVP to develop
3. **Start Phase 2**: Create `feature/57-multi-provider` branch
4. **Complete Phase 2**: Merge multi-provider to develop
5. **Start Phase 3**: Create `feature/57-debug-polish` branch
6. **Complete Phase 3**: Merge final polish to develop
7. **Release**: Web interface production-ready on `develop` branch

---

**Documentation Source**: `.context/tasks-57-web-agent-chat-interface__gh/IMPLEMENTATION_GUIDE.md`  
**Last Updated**: Jan 20, 2026  
**Status**: Ready for implementation
