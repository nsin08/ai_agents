"""Tests for chat service."""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from services.agent_labs_impl import AgentLabsService
from models import ChatResponse


@pytest.mark.asyncio
async def test_agent_labs_service_mock_provider():
    """Test agent labs service with mock provider."""
    service = AgentLabsService()
    response = await service.process_message(
        message="Test message",
        provider="mock",
        model="mock-model",
        config={},
    )
    assert isinstance(response, ChatResponse)
    assert response.success is True
    assert len(response.response) > 0


@pytest.mark.asyncio
async def test_agent_labs_service_unsupported_provider():
    """Test service rejects unsupported providers in Phase 1."""
    service = AgentLabsService()
    response = await service.process_message(
        message="Test",
        provider="ollama",
        model="llama2",
        config={},
    )
    assert response.success is False
    assert "not yet supported" in response.response


@pytest.mark.asyncio
async def test_agent_labs_service_with_config():
    """Test service respects agent config."""
    service = AgentLabsService()
    response = await service.process_message(
        message="Test",
        provider="mock",
        model="mock-model",
        config={"max_turns": 1, "timeout": 60},
    )
    assert response.success is True
    assert response.metadata["max_turns"] == 1


@pytest.mark.asyncio
async def test_agent_labs_service_metadata():
    """Test service includes metadata in response."""
    service = AgentLabsService()
    response = await service.process_message(
        message="Test",
        provider="mock",
        model="test-model",
        config={},
    )
    assert "provider" in response.metadata
    assert "model" in response.metadata
    assert "latency_ms" in response.metadata
    assert "backend" in response.metadata
    assert response.metadata["backend"] == "agent_labs"
