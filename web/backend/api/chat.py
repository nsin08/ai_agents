"""Chat API endpoints.

Provides REST API for chat interactions with LLM agents.
All responses follow a standardized format (ChatResponse or ErrorResponse).
"""
import uuid
import logging
from fastapi import APIRouter, Depends, HTTPException

# Centralized path setup
import core.path_setup  # noqa: F401

from models import ChatRequest, ChatResponse, ErrorResponse
from services.interfaces import AgentServiceInterface
from config import agent_service

logger = logging.getLogger(__name__)

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
        
    Raises:
        HTTPException: 400 for validation errors, 401 for auth errors, 500 for server errors
    """
    try:
        if not request.message.strip():
            logger.warning("Empty message received")
            raise HTTPException(status_code=400, detail="Message cannot be empty")
            
        logger.info(f"Processing message with provider={request.provider}, model={request.model}")
        response = await service.process_message(
            message=request.message,
            provider=request.provider,
            model=request.model,
            config=request.config,
            api_key=request.api_key
        )
        logger.info(f"Message processed successfully")
        return response
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid request: {str(e)}")
    except PermissionError as e:
        logger.error(f"Auth error: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid API key or authentication failed")
    except TimeoutError as e:
        logger.error(f"Timeout: {str(e)}")
        raise HTTPException(status_code=504, detail="Request timeout - agent took too long to respond")
    except Exception as e:
        logger.exception(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error - please try again later")


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
