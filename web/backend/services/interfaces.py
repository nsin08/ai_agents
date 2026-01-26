"""Service interface definitions (abstraction layer)."""
import sys
from pathlib import Path
from typing import Protocol, Dict, Any, Optional

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models import ChatResponse


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
