#!/usr/bin/env python
"""Verification test for configurable Ollama model system."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agent_labs.config import Config, set_ollama_model, get_ollama_model
from agent_labs.tools.ollama_tools import TextSummarizer, CodeAnalyzer


def test_default_configuration():
    """Test 1: Default configuration."""
    print("\n1. DEFAULT CONFIGURATION")
    print(f"   Default model: {get_ollama_model()}")
    print(f"   Expected: llama2")
    assert get_ollama_model() == "llama2", "Default should be llama2"
    print("   ✅ PASS")


def test_tool_initialization():
    """Test 2: Tool initialization with defaults."""
    print("\n2. TOOL INITIALIZATION WITH DEFAULTS")
    summarizer = TextSummarizer()
    analyzer = CodeAnalyzer()
    print(f"   TextSummarizer model: {summarizer.model}")
    print(f"   CodeAnalyzer model: {analyzer.model}")
    assert summarizer.model == "llama2", "Summarizer should use default"
    assert analyzer.model == "llama2", "Analyzer should use default"
    print("   ✅ PASS")


def test_runtime_switching():
    """Test 3: Runtime model switching."""
    print("\n3. RUNTIME MODEL SWITCHING")
    set_ollama_model("mistral:7b")
    print(f"   Changed to: {get_ollama_model()}")
    assert get_ollama_model() == "mistral:7b", "Should be mistral:7b"
    new_summarizer = TextSummarizer()
    print(f"   New TextSummarizer model: {new_summarizer.model}")
    assert new_summarizer.model == "mistral:7b", "New tool should use updated model"
    print("   ✅ PASS")


def test_per_tool_override():
    """Test 4: Per-tool override."""
    print("\n4. PER-TOOL OVERRIDE")
    set_ollama_model("llama2")
    summarizer_global = TextSummarizer()
    summarizer_override = TextSummarizer(model="mistral:7b")
    print(f"   Global default: {summarizer_global.model}")
    print(f"   Overridden: {summarizer_override.model}")
    assert summarizer_global.model == "llama2", "Should use global"
    assert summarizer_override.model == "mistral:7b", "Should use override"
    print("   ✅ PASS")


def test_configuration_dict():
    """Test 5: Configuration dictionary."""
    print("\n5. CONFIGURATION DICTIONARY")
    config = Config.to_dict()
    print(f"   Ollama URL: {config['ollama']['base_url']}")
    print(f"   Model: {config['ollama']['model']}")
    print(f"   Timeout: {config['ollama']['timeout']}s")
    print(f"   Temperature: {config['ollama']['temperature']}")
    assert "ollama" in config, "Config should have ollama section"
    assert "agent" in config, "Config should have agent section"
    print("   ✅ PASS")


def test_environment_support():
    """Test 6: Environment variable support."""
    print("\n6. ENVIRONMENT VARIABLE SUPPORT")
    print(f"   OLLAMA_BASE_URL: {Config.OLLAMA_BASE_URL}")
    print(f"   OLLAMA_TIMEOUT: {Config.OLLAMA_TIMEOUT}s")
    print(f"   OLLAMA_TOOLS_TEMPERATURE: {Config.OLLAMA_TOOLS_TEMPERATURE}")
    assert Config.OLLAMA_BASE_URL == "http://localhost:11434"
    assert Config.OLLAMA_TIMEOUT == 60
    print("   ✅ PASS")


def main():
    """Run all tests."""
    print("=" * 60)
    print("CONFIGURABLE OLLAMA MODEL - VERIFICATION TEST")
    print("=" * 60)

    test_default_configuration()
    test_tool_initialization()
    test_runtime_switching()
    test_per_tool_override()
    test_configuration_dict()
    test_environment_support()

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED ✅")
    print("=" * 60)
    print("\nSummary:")
    print("• Ollama model is now configurable")
    print("• Default model: llama2 (supports your new pull)")
    print("• Runtime switching works")
    print("• Per-tool overrides supported")
    print("• Environment variables supported")
    print("• All tools automatically use configured model")


if __name__ == "__main__":
    main()
