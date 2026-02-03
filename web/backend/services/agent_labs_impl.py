"""AgentLabsService implementation using agent_labs core."""
import time
import asyncio
import logging
from typing import Dict, Any, Optional

# Centralized path setup
import core.path_setup  # noqa: F401

from models import ChatResponse, ProviderEnum, DebugMetadata
from services.interfaces import AgentServiceInterface
from services.provider_factory import ProviderFactory
from agent_labs.llm_providers import ProviderConfigError
from agent_labs.orchestrator import Agent

logger = logging.getLogger(__name__)


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
        config: Dict[str, Any],
        api_key: Optional[str] = None
    ) -> ChatResponse:
        """
        Process message using agent_labs orchestrator.
        
        Args:
            message: User message
            provider: Provider name (mock, ollama, openai, etc.)
            model: Model name
            config: Agent config (max_turns, temperature, etc.)
            api_key: Optional API key override
            
        Returns:
            ChatResponse with agent reply and metadata
        """
        start_time = time.time()
        
        try:
            # Convert provider string to enum
            try:
                provider_enum = ProviderEnum(provider)
            except ValueError:
                return ChatResponse(
                    success=False,
                    response=f"Unknown provider '{provider}'. Supported: {[p.value for p in ProviderEnum]}",
                    metadata={
                        "provider": provider,
                        "model": model,
                        "latency_ms": round((time.time() - start_time) * 1000, 2),
                        "error": "Invalid provider",
                        "backend": "agent_labs"
                    }
                )
            
            # Create provider using factory
            try:
                llm_provider = ProviderFactory.create_provider(
                    provider_type=provider_enum,
                    model=model,
                    api_key=api_key,
                    base_url=config.get("base_url"),
                )
            except ProviderConfigError as e:
                return ChatResponse(
                    success=False,
                    response=f"Provider configuration error: {str(e)}",
                    metadata={
                        "provider": provider,
                        "model": model,
                        "latency_ms": round((time.time() - start_time) * 1000, 2),
                        "error": str(e),
                        "backend": "agent_labs"
                    }
                )
            
            # Create and run agent with full orchestrator (Observe → Plan → Act → Verify)
            agent = Agent(provider=llm_provider, model=model)
            
            # Run agent with timeout enforcement
            # Apply timeout if specified (defaults to 30 seconds)
            timeout_seconds = config.get("timeout", config.get("timeout_seconds", 30))
            try:
                result = await asyncio.wait_for(
                    agent.run(
                        goal=message,
                        max_turns=config.get("max_turns", 3)
                    ),
                    timeout=timeout_seconds
                )
            except asyncio.TimeoutError:
                logger.warning(f"Agent execution timed out after {timeout_seconds}s")
                raise TimeoutError(f"Agent execution exceeded timeout of {timeout_seconds} seconds")
            
            # Calculate metrics
            latency_ms = (time.time() - start_time) * 1000
            
            # Build comprehensive debug metadata
            temperature = config.get("temperature", 0.7)
            max_turns = config.get("max_turns", 3)
            enable_debug = config.get("enable_debug", False)
            
            debug_metadata = DebugMetadata(
                tokens_used=None,  # Will be available when provider supports it
                tokens_input=None,
                tokens_output=None,
                latency_ms=round(latency_ms, 2),
                provider=provider,
                model=model,
                max_turns=max_turns,
                current_turn=1,  # Single turn for now
                temperature=temperature,
                agent_state="Complete",  # Would be "Observe/Plan/Act/Verify" in full impl
                reasoning=None if not enable_debug else "Agent processed request through orchestrator",
                tool_calls=None,
                errors=None,
                backend="agent_labs"
            )
            
            # Build response with debug metadata
            metadata_dict = debug_metadata.model_dump()
            
            # Only include full debug info if debug mode is enabled
            if not enable_debug:
                # Minimal metadata in production mode
                metadata_dict = {
                    "provider": provider,
                    "model": model,
                    "latency_ms": round(latency_ms, 2),
                    "max_turns": max_turns,
                    "backend": "agent_labs"
                }
            
            return ChatResponse(
                success=True,
                response=result,
                metadata={
                    "provider": provider,
                    "model": model,
                    "latency_ms": round(latency_ms, 2),
                    "max_turns": max_turns,  # Include for backward compatibility
                    "backend": "agent_labs"
                },
                debug_metadata=metadata_dict if enable_debug else None
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
                },
                debug_metadata=None
            )
