"""Service interface definitions (abstraction layer).

This module defines the ServiceInterface Protocol that enables seamless backend
swapping between agent_labs (current Phase 1-3) and agent_core (future Phase B).

Key Design Pattern:
    - Abstraction Layer: All backend implementations conform to AgentServiceInterface
    - Zero API Changes: Response format is identical across backends
    - Environment Variable Control: Set AGENT_CORE_BACKEND env var to switch
    - Frontend Unaware: React UI doesn't know which backend is running
    
Backend Switching Example:
    Phase 1-3: AGENT_CORE_BACKEND="agent_labs" → Uses AgentLabsService
    Phase B:   AGENT_CORE_BACKEND="agent_core" → Uses AgentCoreService
    API Response Format: Identical - React UI never changes

This pattern enables production deployment with agent_labs while preparing
for seamless upgrade to agent_core when ready.
"""
from typing import Protocol, Dict, Any, Optional
import logging

# Centralized path setup
import core.path_setup  # noqa: F401

from models import ChatResponse

logger = logging.getLogger(__name__)


class AgentServiceInterface(Protocol):
    """
    Protocol defining the contract for agent services.
    
    This abstraction allows swapping between agent_labs and agent_core
    without changing API routes or frontend code.
    
    Implementations:
        - AgentLabsService: Uses agent_labs core (Phase 1-3)
        - AgentCoreService: Uses agent_core (Phase B, placeholder)
    """
    
    async def process_message(
        self,
        message: str,
        provider: str,
        model: str,
        config: Dict[str, Any],
        api_key: Optional[str] = None
    ) -> ChatResponse:
        """
        Process a user message and return agent response.
        
        Args:
            message: User's input message
            provider: LLM provider name
            model: Model name
            config: Agent configuration
            api_key: Optional API key override
            
        Returns:
            ChatResponse with response text and metadata
        """
        ...
