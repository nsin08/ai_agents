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
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agent_labs.orchestrator import Agent
from agent_labs.llm_providers import MockProvider, OllamaProvider, OpenAIProvider


async def main():
    if len(sys.argv) < 2:
        print("""
╔════════════════════════════════════════════════════════════════╗
║              Quick Test - Interactive Agent                   ║
╚════════════════════════════════════════════════════════════════╝

USAGE:
  python scripts/quick_test.py "Your prompt here"
  python scripts/quick_test.py "What is 2+2?" --ollama
  python scripts/quick_test.py "Tell me about AI" --openai
  python scripts/quick_test.py "Explain ML" --model gpt-4 --openai

OPTIONS:
  --ollama              Use OllamaProvider (local LLM)
  --openai              Use OpenAIProvider (requires OPENAI_API_KEY)
  --model NAME          Set model name (default: llama2 for ollama, gpt-4 for openai)
  --turns N             Set max turns (default: 3)

EXAMPLES:
  python scripts/quick_test.py "What is Python?"
  python scripts/quick_test.py "Explain quantum computing" --ollama
  python scripts/quick_test.py "Define machine learning" --openai
  python scripts/quick_test.py "Write a haiku about AI" --openai --model gpt-3.5-turbo
  python scripts/quick_test.py "Test prompt" --turns 5
        """)
        sys.exit(1)

    # Parse arguments
    prompt = sys.argv[1]
    use_ollama = "--ollama" in sys.argv
    use_openai = "--openai" in sys.argv
    model_name = None
    max_turns = 3

    for i, arg in enumerate(sys.argv):
        if arg == "--model" and i + 1 < len(sys.argv):
            model_name = sys.argv[i + 1]
        elif arg == "--turns" and i + 1 < len(sys.argv):
            max_turns = int(sys.argv[i + 1])

    # Determine provider and model
    if use_openai:
        # OpenAI provider
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("✗ Error: OPENAI_API_KEY not set")
            print("  Set OPENAI_API_KEY in .env file or environment")
            sys.exit(1)
        
        if not model_name:
            model_name = os.getenv("OPENAI_MODEL", "gpt-4")
        
        provider = OpenAIProvider(
            api_key=api_key,
            model=model_name,
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
            timeout=int(os.getenv("OPENAI_TIMEOUT", "30")),
            temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.7")),
        )
        print(f"🤖 Using OpenAIProvider ({model_name})\n")
    elif use_ollama:
        # Ollama provider
        if not model_name:
            model_name = os.getenv("OLLAMA_MODEL", "llama2")
        
        provider = OllamaProvider(
            model=model_name,
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        )
        print(f"🤖 Using OllamaProvider ({model_name})\n")
    else:
        # Mock provider (default)
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
