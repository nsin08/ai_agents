"""Configuration service for managing agent settings."""
from typing import Dict, Optional
from models import AgentConfig, PresetConfig


class ConfigService:
    """Service for managing agent configuration."""

    # Preset configurations
    PRESETS = {
        "creative": PresetConfig(
            name="Creative",
            description="High creativity, more variation in responses",
            config=AgentConfig(
                max_turns=5,
                temperature=1.2,
                timeout_seconds=45,
                system_prompt="You are a creative AI assistant. Generate diverse and imaginative responses.",
                enable_debug=False
            )
        ),
        "precise": PresetConfig(
            name="Precise",
            description="Low temperature, more deterministic responses",
            config=AgentConfig(
                max_turns=3,
                temperature=0.3,
                timeout_seconds=30,
                system_prompt="You are a precise AI assistant. Provide accurate, focused responses.",
                enable_debug=False
            )
        ),
        "balanced": PresetConfig(
            name="Balanced",
            description="Default balanced configuration",
            config=AgentConfig(
                max_turns=3,
                temperature=0.7,
                timeout_seconds=30,
                system_prompt=None,
                enable_debug=False
            )
        ),
    }

    def __init__(self):
        """Initialize configuration service."""
        self._user_configs: Dict[str, AgentConfig] = {}
        self._default_config = AgentConfig()

    def get_default_config(self) -> AgentConfig:
        """Get default configuration."""
        return self._default_config

    def get_preset(self, preset_name: str) -> Optional[PresetConfig]:
        """Get preset configuration by name."""
        return self.PRESETS.get(preset_name.lower())

    def list_presets(self) -> list[PresetConfig]:
        """List all available presets."""
        return list(self.PRESETS.values())

    def save_config(self, session_id: str, config: AgentConfig) -> AgentConfig:
        """Save configuration for a session."""
        # Validate configuration
        if config.max_turns < 1 or config.max_turns > 10:
            raise ValueError("max_turns must be between 1 and 10")
        if config.temperature < 0.0 or config.temperature > 2.0:
            raise ValueError("temperature must be between 0.0 and 2.0")
        if config.timeout_seconds < 5 or config.timeout_seconds > 300:
            raise ValueError("timeout_seconds must be between 5 and 300")

        self._user_configs[session_id] = config
        return config

    def get_config(self, session_id: str) -> AgentConfig:
        """Get configuration for a session, or default if not set."""
        return self._user_configs.get(session_id, self._default_config)

    def apply_preset(self, session_id: str, preset_name: str) -> AgentConfig:
        """Apply a preset configuration to a session."""
        preset = self.get_preset(preset_name)
        if not preset:
            raise ValueError(f"Unknown preset: {preset_name}")

        config = preset.config
        self._user_configs[session_id] = config
        return config

    def reset_config(self, session_id: str) -> AgentConfig:
        """Reset configuration to default."""
        if session_id in self._user_configs:
            del self._user_configs[session_id]
        return self._default_config
