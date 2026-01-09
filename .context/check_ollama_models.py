#!/usr/bin/env python
"""Check available models in Ollama."""

import asyncio
import httpx


async def check_models():
    """Check available models."""
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get("http://localhost:11434/api/tags")
            models = [m["name"] for m in response.json().get("models", [])]
            
            print("=" * 60)
            print("AVAILABLE OLLAMA MODELS")
            print("=" * 60)
            
            if models:
                for model in models:
                    print(f"  • {model}")
            else:
                print("  No models found")
            
            print("\n" + "=" * 60)
            
            # Suggest config
            if models:
                print("\nTo use a model, set it in your code:")
                print(f"\n  from agent_labs.config import set_ollama_model")
                print(f'  set_ollama_model("{models[0]}")')
                print("\nOr via environment:")
                print(f'  OLLAMA_MODEL={models[0]} python script.py')
    
    except Exception as e:
        print(f"Error: Could not connect to Ollama at http://localhost:11434")
        print(f"Details: {e}")
        print("\nMake sure Ollama is running:")
        print("  ollama serve")


if __name__ == "__main__":
    asyncio.run(check_models())
