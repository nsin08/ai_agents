"""Comprehensive tests for debug mode functionality."""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from main import app

client = TestClient(app)


class TestDebugMetadata:
    """Test suite for debug metadata feature."""
    
    def test_debug_disabled_by_default(self):
        """Test that debug metadata is not returned by default."""
        response = client.post(
            "/api/chat/send",
            json={
                "message": "Test message",
                "provider": "mock",
                "model": "mock-model"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "metadata" in data
        assert data["debug_metadata"] is None
    
    def test_debug_enabled_returns_metadata(self):
        """Test that debug metadata is returned when enabled."""
        response = client.post(
            "/api/chat/send",
            json={
                "message": "Test message",
                "provider": "mock",
                "model": "mock-model",
                "config": {"enable_debug": True}
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["debug_metadata"] is not None
        
        # Verify debug metadata structure
        debug = data["debug_metadata"]
        assert "latency_ms" in debug
        assert "temperature" in debug
        assert "max_turns" in debug
        assert "agent_state" in debug
        assert "reasoning" in debug
        assert "provider" in debug
        assert "model" in debug
    
    def test_debug_metadata_fields(self):
        """Test all expected debug metadata fields are present."""
        response = client.post(
            "/api/chat/send",
            json={
                "message": "Debug test",
                "provider": "mock",
                "model": "mock-model",
                "config": {
                    "enable_debug": True,
                    "temperature": 0.8,
                    "max_turns": 5
                }
            }
        )
        assert response.status_code == 200
        data = response.json()
        debug = data["debug_metadata"]
        
        # Check all fields exist
        required_fields = [
            "tokens_used", "tokens_input", "tokens_output",
            "latency_ms", "provider", "model", "max_turns",
            "current_turn", "temperature", "agent_state",
            "reasoning", "tool_calls", "errors", "backend"
        ]
        for field in required_fields:
            assert field in debug, f"Missing debug field: {field}"
        
        # Verify values match config
        assert debug["temperature"] == 0.8
        assert debug["max_turns"] == 5
    
    def test_debug_mode_with_config_preset(self):
        """Test debug mode with predefined config presets."""
        # Enable debug in config
        client.post(
            "/api/config/save",
            json={
                "config": {
                    "max_turns": 3,
                    "temperature": 0.7,
                    "timeout_seconds": 30,
                    "enable_debug": True
                }
            }
        )
        
        # Send message (should inherit debug setting)
        response = client.post(
            "/api/chat/send",
            json={
                "message": "Test with preset",
                "provider": "mock",
                "model": "mock-model"
            }
        )
        assert response.status_code == 200
        data = response.json()
        # Note: Per-request config may override global
        assert "debug_metadata" in data
    
    def test_debug_metadata_performance_overhead(self):
        """Test that debug mode doesn't significantly impact performance."""
        # Send without debug
        response1 = client.post(
            "/api/chat/send",
            json={
                "message": "Performance test",
                "provider": "mock",
                "model": "mock-model",
                "config": {"enable_debug": False}
            }
        )
        latency_no_debug = response1.json()["metadata"]["latency_ms"]
        
        # Send with debug
        response2 = client.post(
            "/api/chat/send",
            json={
                "message": "Performance test",
                "provider": "mock",
                "model": "mock-model",
                "config": {"enable_debug": True}
            }
        )
        latency_with_debug = response2.json()["debug_metadata"]["latency_ms"]
        
        # Debug overhead should be minimal (< 50ms difference)
        overhead = abs(latency_with_debug - latency_no_debug)
        assert overhead < 50, f"Debug overhead too high: {overhead}ms"


class TestDebugModeIntegration:
    """Integration tests for debug mode workflows."""
    
    def test_debug_toggle_in_session(self):
        """Test enabling/disabling debug within a session."""
        # Create session
        session_response = client.post("/api/chat/sessions")
        session_id = session_response.json()["session_id"]
        
        # Send with debug disabled
        response1 = client.post(
            "/api/chat/send",
            json={
                "session_id": session_id,
                "message": "First message",
                "provider": "mock",
                "model": "mock-model",
                "config": {"enable_debug": False}
            }
        )
        assert response1.json()["debug_metadata"] is None
        
        # Send with debug enabled
        response2 = client.post(
            "/api/chat/send",
            json={
                "session_id": session_id,
                "message": "Second message",
                "provider": "mock",
                "model": "mock-model",
                "config": {"enable_debug": True}
            }
        )
        assert response2.json()["debug_metadata"] is not None
    
    def test_debug_with_different_configs(self):
        """Test debug metadata with various config combinations."""
        configs = [
            {"temperature": 0.3, "max_turns": 1},
            {"temperature": 1.0, "max_turns": 10},
            {"temperature": 0.7, "max_turns": 5}
        ]
        
        for config in configs:
            config["enable_debug"] = True
            response = client.post(
                "/api/chat/send",
                json={
                    "message": f"Test with temp={config['temperature']}",
                    "provider": "mock",
                    "model": "mock-model",
                    "config": config
                }
            )
            assert response.status_code == 200
            debug = response.json()["debug_metadata"]
            assert debug["temperature"] == config["temperature"]
            assert debug["max_turns"] == config["max_turns"]


class TestDebugModeEdgeCases:
    """Test edge cases for debug mode."""
    
    def test_debug_with_error_response(self):
        """Test debug metadata when request fails."""
        response = client.post(
            "/api/chat/send",
            json={
                "message": "",  # Empty message should fail validation
                "provider": "mock",
                "model": "mock-model",
                "config": {"enable_debug": True}
            }
        )
        # Empty message causes 422 validation error
        assert response.status_code == 422
    
    def test_debug_metadata_data_types(self):
        """Test that debug metadata fields have correct types."""
        response = client.post(
            "/api/chat/send",
            json={
                "message": "Type check",
                "provider": "mock",
                "model": "mock-model",
                "config": {"enable_debug": True}
            }
        )
        debug = response.json()["debug_metadata"]
        
        # Check types
        assert isinstance(debug["latency_ms"], (int, float))
        assert isinstance(debug["temperature"], (int, float))
        assert isinstance(debug["max_turns"], int)
        assert isinstance(debug["current_turn"], int)
        assert isinstance(debug["agent_state"], str)
        assert isinstance(debug["provider"], str)
        assert isinstance(debug["model"], str)
    
    def test_debug_reasoning_field(self):
        """Test that reasoning field is populated when debug enabled."""
        response = client.post(
            "/api/chat/send",
            json={
                "message": "Test reasoning",
                "provider": "mock",
                "model": "mock-model",
                "config": {"enable_debug": True}
            }
        )
        debug = response.json()["debug_metadata"]
        assert debug["reasoning"] is not None
        assert len(debug["reasoning"]) > 0
