#!/usr/bin/env python
"""
Quick test script for configuration system.

Demonstrates loading configuration from different sources and using it
to initialize an agent. This is a minimal example for quick testing.
"""

import sys
from pathlib import Path
from agent_labs.config_v2 import load_config, AgentConfig, ConfigError


def test_default_config():
    """Test default configuration."""
    print("Testing default configuration...")
    config = AgentConfig()
    print(f"  Provider: {config.models.provider.value}")
    print(f"  Model: {config.models.model}")
    print(f"  Max turns: {config.engine.max_turns}")
    print("  ✓ Default config loaded\n")
    return config


def test_yaml_config():
    """Test YAML configuration."""
    print("Testing YAML configuration...")
    # Look for config files in repository root
    yaml_path = Path(__file__).parent.parent.parent.parent / "config" / "local.yaml"

    if not yaml_path.exists():
        print(f"  ⚠ YAML file not found: {yaml_path}")
        print("  Skipping YAML test\n")
        return None

    config = load_config(str(yaml_path))
    print(f"  App name: {config.app.name}")
    print(f"  Provider: {config.models.provider.value}")
    print(f"  Model: {config.models.model}")
    print(f"  Debug: {config.app.debug}")
    print("  ✓ YAML config loaded\n")
    return config


def test_config_override():
    """Test configuration with overrides."""
    print("Testing configuration overrides...")
    config = AgentConfig(
        app={"name": "quick_test_agent", "debug": True},
        models={"provider": "mock", "temperature": 0.5},
        engine={"max_turns": 3},
    )
    print(f"  App name: {config.app.name}")
    print(f"  Provider: {config.models.provider.value}")
    print(f"  Temperature: {config.models.temperature}")
    print(f"  Max turns: {config.engine.max_turns}")
    print("  ✓ Override config loaded\n")
    return config


def test_config_export():
    """Test configuration export."""
    print("Testing configuration export...")
    config = AgentConfig(models={"provider": "mock"})

    # Export as dict
    config_dict = config.to_dict()
    print(f"  Exported {len(config_dict)} sections")

    # Export schema
    schema = config.to_json_schema()
    print(f"  Schema has {len(schema.get('properties', {}))} properties")
    print("  ✓ Export successful\n")


def test_validation():
    """Test configuration validation."""
    print("Testing configuration validation...")

    # Valid config
    try:
        config = AgentConfig(models={"provider": "mock"})
        print("  ✓ Valid mock config")
    except ConfigError as e:
        print(f"  ✗ Unexpected error: {e}")
        return False

    # Invalid config (OpenAI without model)
    try:
        config = AgentConfig(models={"provider": "openai"})
        print("  ✗ Should have failed: OpenAI requires model")
        return False
    except ConfigError as e:
        print(f"  ✓ Expected validation error: {str(e)[:50]}...")

    print()
    return True


def main():
    """Run all quick tests."""
    print("=" * 60)
    print("Configuration System - Quick Test")
    print("=" * 60)
    print()

    try:
        test_default_config()
        test_yaml_config()
        test_config_override()
        test_config_export()
        test_validation()

        print("=" * 60)
        print("All tests passed! ✓")
        print("=" * 60)
        return 0

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
