#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick Test Script - Interactive Agent One-Liner

Use this for fast testing without the full interactive loop.

Usage:
    python scripts/quick_test.py "Your prompt here"
    python scripts/quick_test.py "What is 2+2?"
"""

import sys
import io

# Fix Windows console encoding
if sys.stdout.encoding and 'utf' not in sys.stdout.encoding.lower():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import asyncio
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agent_labs.orchestrator import Agent
from agent_labs.llm_providers import MockProvider, OllamaProvider


async def main():
    if len(sys.argv) < 2:
        print("""
╔════════════════════════════════════════════════════════════════╗
║              Quick Test - Interactive Agent                   ║
╚════════════════════════════════════════════════════════════════╝

USAGE:
  python scripts/quick_test.py "Your prompt here"
  python scripts/quick_test.py "What is 2+2?" --ollama
  python scripts/quick_test.py "Tell me about AI" --model mistral

OPTIONS:
  --ollama              Use OllamaProvider instead of MockProvider
  --model NAME          Set model name (default: llama2)
  --turns N             Set max turns (default: 3)

EXAMPLES:
  python scripts/quick_test.py "What is Python?"
  python scripts/quick_test.py "Explain quantum computing" --ollama
  python scripts/quick_test.py "Define machine learning" --turns 5
        """)
        sys.exit(1)

    # Parse arguments
    prompt = sys.argv[1]
    use_ollama = "--ollama" in sys.argv
    model_name = "llama2"
    max_turns = 3

    for i, arg in enumerate(sys.argv):
        if arg == "--model" and i + 1 < len(sys.argv):
            model_name = sys.argv[i + 1]
        elif arg == "--turns" and i + 1 < len(sys.argv):
            max_turns = int(sys.argv[i + 1])

    # Create provider
    if use_ollama:
        provider = OllamaProvider(
            model=model_name,
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        )
        print(f"🤖 Using OllamaProvider ({model_name})\n")
    else:
        provider = MockProvider()
        print(f"🤖 Using MockProvider\n")

    # Create and run agent
    agent = Agent(provider=provider)

    print(f"📝 Prompt: {prompt}\n")
    print("⏳ Thinking...\n")

    try:
        result = await agent.run(prompt, max_turns=max_turns)
        print("╔════════════════════════════════════════════════════════════════╗")
        print("║                      Agent Response                            ║")
        print("╚════════════════════════════════════════════════════════════════╝\n")
        print(result)
        print()
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Interrupted")
