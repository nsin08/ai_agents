"""AgentLabsService implementation using agent_labs core."""
import time
import sys
from pathlib import Path
from typing import Dict, Any

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from models import ChatResponse
from services.interfaces import AgentServiceInterface
from agent_labs.llm_providers import MockProvider
from agent_labs.orchestrator import Agent


class AgentLabsService(AgentServiceInterface):
    """Service implementation using agent_labs core."""
    
    def __init__(self):
        """Initialize service with agent_labs components."""
        # Service is stateless, so no initialization needed
        pass
    
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
            # For Phase 1, only Mock provider supported
            if provider != "mock":
                return ChatResponse(
                    success=False,
                    response=f"Provider '{provider}' not yet supported in Phase 1. Use 'mock' provider.",
                    metadata={
                        "provider": provider,
                        "model": model,
                        "latency_ms": round((time.time() - start_time) * 1000, 2),
                        "error": "Unsupported provider",
                        "backend": "agent_labs"
                    }
                )
            
            # Create Mock provider (deterministic for testing)
            llm_provider = MockProvider(name=model)
            
            # Create and run agent
            agent = Agent(provider=llm_provider, model=model)
            
            # Run agent with the message as goal
            result = await agent.run(
                goal=message,
                max_turns=config.get("max_turns", 3),
                inputs=config
            )
            
            # Calculate metrics
            latency_ms = (time.time() - start_time) * 1000
            
            # Build response
            return ChatResponse(
                success=True,
                response=result,
                metadata={
                    "provider": provider,
                    "model": model,
                    "latency_ms": round(latency_ms, 2),
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
