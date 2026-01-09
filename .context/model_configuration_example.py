"""
Example: Configuring Ollama model for tools and agents.

Shows how to:
1. Set model globally via environment or Config
2. Override per-tool
3. Switch models at runtime
"""

from agent_labs.config import Config, set_ollama_model, get_ollama_model
from agent_labs.tools.ollama_tools import TextSummarizer, CodeAnalyzer


def example_global_config():
    """Example 1: Set model globally."""
    print("=== Example 1: Global Model Configuration ===\n")
    
    # Option A: Set at module load
    set_ollama_model("llama2")
    print(f"Active model: {get_ollama_model()}")
    
    # Tools will use the global model
    summarizer = TextSummarizer()
    print(f"TextSummarizer model: {summarizer.model}")
    
    analyzer = CodeAnalyzer()
    print(f"CodeAnalyzer model: {analyzer.model}\n")


def example_per_tool_override():
    """Example 2: Override model per tool."""
    print("=== Example 2: Per-Tool Model Override ===\n")
    
    # Global default
    set_ollama_model("llama2")
    print(f"Global model: {get_ollama_model()}")
    
    # Override for specific tool
    summarizer = TextSummarizer(model="mistral:7b")
    print(f"TextSummarizer model: {summarizer.model} (overridden)")
    
    analyzer = CodeAnalyzer()
    print(f"CodeAnalyzer model: {analyzer.model} (using global)\n")


def example_runtime_switch():
    """Example 3: Switch models at runtime."""
    print("=== Example 3: Runtime Model Switching ===\n")
    
    # Start with llama2
    set_ollama_model("llama2")
    summarizer1 = TextSummarizer()
    print(f"Summarizer (created with llama2): {summarizer1.model}")
    
    # Switch to mistral
    set_ollama_model("mistral:7b")
    summarizer2 = TextSummarizer()
    print(f"Summarizer (created with mistral:7b): {summarizer2.model}\n")


def example_config_inspection():
    """Example 4: Inspect all configuration."""
    print("=== Example 4: Configuration Inspection ===\n")
    
    config = Config.to_dict()
    
    print("Ollama Configuration:")
    for key, value in config["ollama"].items():
        print(f"  {key}: {value}")
    
    print("\nAgent Configuration:")
    for key, value in config["agent"].items():
        print(f"  {key}: {value}\n")


if __name__ == "__main__":
    example_global_config()
    example_per_tool_override()
    example_runtime_switch()
    example_config_inspection()
