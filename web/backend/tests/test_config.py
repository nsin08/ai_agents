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
