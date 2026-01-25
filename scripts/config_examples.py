#!/usr/bin/env python
"""
Example script demonstrating the enhanced configuration system.

Shows configuration loading from:
1. Defaults
2. Environment variables
3. YAML files
4. Explicit overrides
"""

import os
from pathlib import Path
from agent_labs.config_v2 import (
    AgentConfig,
    load_config,
    get_config,
    ConfigError,
)


def example_1_defaults():
    """Example 1: Load with defaults only."""
    print("\n=== Example 1: Default Configuration ===")

    config = AgentConfig()

    print(f"App name: {config.app.name}")
    print(f"App mode: {config.app.mode}")
    print(f"Provider: {config.models.provider}")
    print(f"Model: {config.models.model}")
    print(f"Max turns: {config.engine.max_turns}")
    print(f"Timeout: {config.engine.timeout}s")


def example_2_env_vars():
    """Example 2: Load from environment variables."""
    print("\n=== Example 2: Environment Variables ===")

    # Set some env vars
    os.environ["APP_NAME"] = "demo_agent"
    os.environ["LLM_PROVIDER"] = "ollama"
    os.environ["LLM_MODEL"] = "mistral:7b"
    os.environ["AGENT_MAX_TURNS"] = "15"

    config = AgentConfig.from_env()

    print(f"App name: {config.app.name}")
    print(f"Provider: {config.models.provider}")
    print(f"Model: {config.models.model}")
    print(f"Max turns: {config.engine.max_turns}")


def example_3_yaml_file():
    """Example 3: Load from YAML file."""
    print("\n=== Example 3: YAML Configuration ===")

    yaml_path = Path(__file__).parent.parent / "config" / "local.yaml"

    if not yaml_path.exists():
        print(f"YAML file not found: {yaml_path}")
        return

    config = load_config(str(yaml_path))

    print(f"App name: {config.app.name}")
    print(f"App mode: {config.app.mode}")
    print(f"Provider: {config.models.provider}")
    print(f"Model: {config.models.model}")
    print(f"Debug: {config.app.debug}")
    print(f"Log prompts: {config.observability.log_prompts}")


def example_4_precedence():
    """Example 4: Configuration precedence."""
    print("\n=== Example 4: Configuration Precedence ===")

    yaml_path = Path(__file__).parent.parent / "config" / "local.yaml"

    if not yaml_path.exists():
        print(f"YAML file not found: {yaml_path}")
        return

    # YAML has: model=llama2, max_turns=10
    # Set env var to override
    os.environ["AGENT_MAX_TURNS"] = "20"

    # Load with explicit override
    config = load_config(str(yaml_path), models={"temperature": 0.9})  # Explicit override

    print("Configuration sources:")
    print(f"  - Model: {config.models.model} (from YAML)")
    print(f"  - Max turns: {config.engine.max_turns} (from ENV, overrides YAML)")
    print(f"  - Temperature: {config.models.temperature} (from Explicit, overrides YAML)")
    print(f"  - Timeout: {config.models.timeout}s (from YAML)")


def example_5_validation():
    """Example 5: Configuration validation."""
    print("\n=== Example 5: Configuration Validation ===")

    # Valid config
    try:
        config = AgentConfig(models={"provider": "ollama", "model": "llama2"})
        print("✓ Valid Ollama configuration")
    except ConfigError as e:
        print(f"✗ Error: {e}")

    # Invalid config - missing model for OpenAI
    try:
        config = AgentConfig(models={"provider": "openai"})
        print("✓ Valid OpenAI configuration")
    except ConfigError as e:
        print(f"✗ Expected error: {e}")

    # Invalid config - timeout out of range
    try:
        config = AgentConfig(models={"timeout": 700})
        print("✓ Valid timeout")
    except Exception as e:
        print(f"✗ Expected validation error: timeout out of range")


def example_6_export():
    """Example 6: Export configuration."""
    print("\n=== Example 6: Export Configuration ===")

    config = AgentConfig(
        app={"name": "export_demo", "mode": "development"},
        models={"provider": "mock"},
        engine={"max_turns": 5},
    )

    # Export as dictionary
    config_dict = config.to_dict()
    print("\nConfiguration as dictionary:")
    print(f"  App: {config_dict['app']}")
    print(f"  Models: {config_dict['models']}")

    # Export schema
    schema = config.to_json_schema()
    print(f"\nJSON Schema has {len(schema['properties'])} top-level properties")
    print(f"Properties: {list(schema['properties'].keys())}")


def example_7_security():
    """Example 7: Security validation."""
    print("\n=== Example 7: Security Validation ===")

    # OpenAI without API key
    os.environ.pop("OPENAI_API_KEY", None)

    config = AgentConfig(models={"provider": "openai", "model": "gpt-4"})

    try:
        config.validate_secrets()
        print("✓ API key validated")
    except ConfigError as e:
        print(f"✗ Expected error: {e}")

    # Ollama (no API key needed)
    config = AgentConfig(models={"provider": "ollama", "model": "llama2"})

    try:
        config.validate_secrets()
        print("✓ Ollama config valid (no API key required)")
    except ConfigError as e:
        print(f"✗ Error: {e}")


def main():
    """Run all examples."""
    print("=" * 60)
    print("Enhanced Configuration System - Examples")
    print("=" * 60)

    example_1_defaults()
    example_2_env_vars()
    example_3_yaml_file()
    example_4_precedence()
    example_5_validation()
    example_6_export()
    example_7_security()

    print("\n" + "=" * 60)
    print("Examples complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
