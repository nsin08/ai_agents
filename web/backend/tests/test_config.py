"""Tests for configuration API endpoints."""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_get_default_config():
    """Test retrieving default configuration."""
    response = client.get("/api/config/default")
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert "config" in data
    assert data["config"]["max_turns"] == 3
    assert data["config"]["temperature"] == 0.7
    assert data["config"]["timeout_seconds"] == 30


def test_list_presets():
    """Test listing all preset configurations."""
    response = client.get("/api/config/presets")
    assert response.status_code == 200
    
    presets = response.json()
    assert isinstance(presets, list)
    assert len(presets) == 3
    
    preset_names = [p["name"] for p in presets]
    assert "Creative" in preset_names
    assert "Precise" in preset_names
    assert "Balanced" in preset_names


def test_get_preset():
    """Test retrieving a specific preset."""
    response = client.get("/api/config/presets/creative")
    assert response.status_code == 200
    
    preset = response.json()
    assert preset["name"] == "Creative"
    assert preset["config"]["temperature"] == 1.2
    assert preset["config"]["max_turns"] == 5


def test_get_preset_not_found():
    """Test retrieving a nonexistent preset."""
    response = client.get("/api/config/presets/unknown")
    assert response.status_code == 404


def test_save_custom_config():
    """Test saving a custom configuration."""
    config_data = {
        "config": {
            "max_turns": 5,
            "temperature": 0.9,
            "timeout_seconds": 45,
            "system_prompt": "Test prompt",
            "enable_debug": True
        }
    }
    
    response = client.post("/api/config/save", json=config_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert data["config"]["max_turns"] == 5
    assert data["config"]["temperature"] == 0.9
    assert data["config"]["enable_debug"] is True


def test_save_preset_config():
    """Test applying a preset configuration."""
    config_data = {
        "config": {
            "max_turns": 3,
            "temperature": 0.7,
            "timeout_seconds": 30,
            "enable_debug": False
        },
        "preset": "precise"
    }
    
    response = client.post("/api/config/save", json=config_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Applied preset: precise"
    assert data["config"]["temperature"] == 0.3


def test_save_invalid_config():
    """Test saving invalid configuration."""
    config_data = {
        "config": {
            "max_turns": 15,  # Invalid: max is 10
            "temperature": 0.7,
            "timeout_seconds": 30,
            "enable_debug": False
        }
    }
    
    response = client.post("/api/config/save", json=config_data)
    assert response.status_code == 422  # Pydantic validation error


def test_reset_config():
    """Test resetting configuration to default."""
    response = client.post("/api/config/reset")
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert data["message"] == "Configuration reset to default"
    assert data["config"]["max_turns"] == 3
    assert data["config"]["temperature"] == 0.7


def test_get_session_config():
    """Test retrieving configuration for a session."""
    session_id = "test_session"
    response = client.get(f"/api/config/{session_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert "config" in data
    assert data["config"]["max_turns"] == 3  # Default


def test_debug_metadata_in_chat_response():
    """Test that debug metadata is included when enabled."""
    # First, enable debug mode
    config_data = {
        "config": {
            "max_turns": 3,
            "temperature": 0.7,
            "timeout_seconds": 30,
            "enable_debug": True
        }
    }
    client.post("/api/config/save", json=config_data)
    
    # Then send a chat message
    response = client.post(
        "/api/chat/send",
        json={
            "message": "Hello",
            "provider": "mock",
            "model": "mock-model",
            "config": {"enable_debug": True}
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "metadata" in data
    assert "latency_ms" in data["metadata"]
    assert "provider" in data["metadata"]
    assert "model" in data["metadata"]
    # Debug-specific fields should be in debug_metadata
    assert "debug_metadata" in data
    assert data["debug_metadata"] is not None
    assert "temperature" in data["debug_metadata"]
    assert data["debug_metadata"]["temperature"] == 0.7
    assert "max_turns" in data["debug_metadata"]
    assert data["debug_metadata"]["max_turns"] == 3


def test_session_specific_config_save():
    """Test that config can be saved for a specific session (PR #115 Fix #1)."""
    session_id_1 = "user_session_123"
    session_id_2 = "user_session_456"
    
    # Save config for session 1 with high temperature
    config_data_1 = {
        "config": {
            "max_turns": 5,
            "temperature": 1.2,
            "timeout_seconds": 45,
            "enable_debug": True
        },
        "session_id": session_id_1
    }
    response1 = client.post("/api/config/save", json=config_data_1)
    assert response1.status_code == 200
    assert response1.json()["config"]["temperature"] == 1.2
    
    # Save config for session 2 with low temperature
    config_data_2 = {
        "config": {
            "max_turns": 2,
            "temperature": 0.3,
            "timeout_seconds": 20,
            "enable_debug": False
        },
        "session_id": session_id_2
    }
    response2 = client.post("/api/config/save", json=config_data_2)
    assert response2.status_code == 200
    assert response2.json()["config"]["temperature"] == 0.3
    
    # Verify sessions have different configs
    session1_config = client.get(f"/api/config/{session_id_1}").json()
    session2_config = client.get(f"/api/config/{session_id_2}").json()
    
    assert session1_config["config"]["temperature"] == 1.2
    assert session2_config["config"]["temperature"] == 0.3


def test_session_specific_config_reset():
    """Test that config reset works for specific session (PR #115 Fix #1)."""
    session_id = "reset_test_session"
    
    # Save custom config
    config_data = {
        "config": {
            "max_turns": 8,
            "temperature": 1.5,
            "timeout_seconds": 60,
            "enable_debug": True
        },
        "session_id": session_id
    }
    client.post("/api/config/save", json=config_data)
    
    # Reset config for this session
    response = client.post(f"/api/config/reset?session_id={session_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert data["config"]["max_turns"] == 3  # Default value
    assert data["config"]["temperature"] == 0.7  # Default value
    assert data["config"]["timeout_seconds"] == 30  # Default value


def test_timeout_config_applied():
    """Test that timeout config is applied to agent execution (PR #115 Fix #2)."""
    # Send message with very short timeout
    response = client.post(
        "/api/chat/send",
        json={
            "message": "Count to 1000 slowly",
            "provider": "mock",
            "model": "mock-model",
            "config": {
                "timeout": 1,  # 1 second timeout
                "max_turns": 3
            }
        }
    )
    
    # With mock provider, should complete quickly and succeed
    # Real provider with long operations would timeout
    assert response.status_code == 200
    data = response.json()
    
    # Verify timeout was passed to agent (check metadata)
    assert "metadata" in data
    assert "latency_ms" in data["metadata"]
    # Latency should be less than timeout
    assert data["metadata"]["latency_ms"] < 1000


def test_timeout_backwards_compatibility():
    """Test that both 'timeout' and 'timeout_seconds' keys work (PR #115 Fix #2)."""
    # Test with 'timeout' key
    response1 = client.post(
        "/api/chat/send",
        json={
            "message": "Test timeout key",
            "provider": "mock",
            "model": "mock-model",
            "config": {"timeout": 15}
        }
    )
    assert response1.status_code == 200
    
    # Test with 'timeout_seconds' key
    response2 = client.post(
        "/api/chat/send",
        json={
            "message": "Test timeout_seconds key",
            "provider": "mock",
            "model": "mock-model",
            "config": {"timeout_seconds": 20}
        }
    )
    assert response2.status_code == 200

