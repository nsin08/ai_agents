"""Chat API endpoints."""
import sys
from pathlib import Path
import uuid
from fastapi import APIRouter, Depends, HTTPException

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models import ChatRequest, ChatResponse, ErrorResponse
from services.interfaces import AgentServiceInterface
from config import agent_service

router = APIRouter(prefix="/api/chat", tags=["chat"])

# In-memory session storage (will be replaced with database in Phase 2)
_sessions = {}


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


@router.post("/sessions")
async def create_session():
    """Create new session.
    
    Returns:
        New session ID
    """
    session_id = str(uuid.uuid4())
    _sessions[session_id] = {
        "session_id": session_id,
        "messages": []
    }
    return {
        "session_id": session_id
    }


@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """Get session history.
    
    Args:
        session_id: Session identifier
        
    Returns:
        Session data with message history
    """
    if session_id not in _sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return _sessions[session_id]
