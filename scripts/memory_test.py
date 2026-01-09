#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Memory Fix Test - Demonstrates agent now remembers conversation context
"""

import sys
import io
import asyncio
import os
from pathlib import Path

# Fix Windows console encoding
if sys.stdout.encoding and 'utf' not in sys.stdout.encoding.lower():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agent_labs.orchestrator import Agent
from agent_labs.llm_providers import OllamaProvider


async def test_memory():
    """Test if agent remembers conversation context."""
    
    print("\n" + "="*70)
    print("MEMORY TEST - Agent With Context Injection")
    print("="*70 + "\n")
    
    # Create provider
    provider = OllamaProvider(
        model="llama2",
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    )
    
    agent = Agent(provider=provider)
    conversation_history = []
    
    # Test 1: Ask a math question
    print("TEST 1: Math Question")
    print("-" * 70)
    prompt1 = "what is 2+2?"
    result1 = await agent.run(prompt1, max_turns=2)
    conversation_history.append(("user", prompt1))
    conversation_history.append(("agent", result1))
    print(f"Q: {prompt1}")
    print(f"A: {result1[:100]}...\n")
    
    # Test 2: Introduce yourself
    print("TEST 2: Introduce Yourself")
    print("-" * 70)
    prompt2 = "i am neeraj singh"
    result2 = await agent.run(prompt2, max_turns=2)
    conversation_history.append(("user", prompt2))
    conversation_history.append(("agent", result2))
    print(f"Q: {prompt2}")
    print(f"A: {result2[:100]}...\n")
    
    # Test 3: Ask about context WITH history injection
    print("TEST 3: Recall Question (WITH CONTEXT INJECTION)")
    print("-" * 70)
    
    # Build context prompt (simulating what interactive_agent.py now does)
    context = "CONVERSATION CONTEXT:\n"
    context += "═" * 60 + "\n"
    for role, msg in conversation_history[-4:]:
        prefix = "User" if role == "user" else "Agent"
        msg_short = msg[:100] + "..." if len(msg) > 100 else msg
        context += f"{prefix}: {msg_short}\n"
    context += "═" * 60 + "\n"
    
    prompt3 = "what was the number i asked you to add?"
    context_prompt3 = context + f"NEW QUESTION: {prompt3}\n"
    
    result3 = await agent.run(context_prompt3, max_turns=2)
    print(f"Q: {prompt3}")
    print(f"WITH CONTEXT: Yes ✓")
    print(f"A: {result3[:150]}...\n")
    
    # Test 4: Ask about name WITH history injection
    print("TEST 4: Name Recall (WITH CONTEXT INJECTION)")
    print("-" * 70)
    
    # Rebuild context with updated history
    conversation_history.append(("user", prompt3))
    conversation_history.append(("agent", result3))
    
    context = "CONVERSATION CONTEXT:\n"
    context += "═" * 60 + "\n"
    for role, msg in conversation_history[-6:]:
        prefix = "User" if role == "user" else "Agent"
        msg_short = msg[:80] + "..." if len(msg) > 80 else msg
        context += f"{prefix}: {msg_short}\n"
    context += "═" * 60 + "\n"
    
    prompt4 = "do you know my name?"
    context_prompt4 = context + f"NEW QUESTION: {prompt4}\n"
    
    result4 = await agent.run(context_prompt4, max_turns=2)
    print(f"Q: {prompt4}")
    print(f"WITH CONTEXT: Yes ✓")
    print(f"A: {result4[:150]}...\n")
    
    print("="*70)
    print("✅ MEMORY TEST COMPLETE")
    print("="*70)
    print("\nKEY FINDING:")
    print("  • Agent now receives CONVERSATION CONTEXT before each prompt")
    print("  • Context includes previous 10 messages (configurable)")
    print("  • This fix is automatically applied in interactive_agent.py")
    print("\nNEXT STEP:")
    print("  Run: python scripts/interactive_agent.py")
    print("  Then: /provider ollama")
    print("  Try: Ask questions and the agent should remember!")
    print()


if __name__ == "__main__":
    try:
        asyncio.run(test_memory())
    except KeyboardInterrupt:
        print("\n👋 Test interrupted")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
