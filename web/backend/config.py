"""Backend configuration and dependency injection."""
import os
from typing import Generator

# Centralized path setup
import core.path_setup  # noqa: F401

from services.interfaces import AgentServiceInterface
from services.agent_labs_impl import AgentLabsService


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
