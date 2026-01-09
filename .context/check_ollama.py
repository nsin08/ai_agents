"""Quick script to check Ollama connectivity and list models."""
import httpx
import asyncio
import json


async def check_ollama():
    """Check Ollama API connectivity and list available models."""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            # Check health
            health_resp = await client.get("http://localhost:11434/api/tags")
            
            if health_resp.status_code == 200:
                data = health_resp.json()
                models = data.get("models", [])
                
                print("✅ Ollama is running!")
                print(f"\nAvailable models ({len(models)}):")
                for model in models:
                    name = model.get("name", "unknown")
                    size = model.get("size", 0)
                    size_gb = size / (1024**3)
                    print(f"  - {name} ({size_gb:.1f} GB)")
                
                if models:
                    print(f"\n✅ Ready to use: {models[0]['name']}")
                    return models[0]['name']
                else:
                    print("\n⚠️  No models available. Run: ollama pull <model>")
                    return None
            else:
                print(f"❌ Error: {health_resp.status_code}")
                return None
    except Exception as e:
        print(f"❌ Cannot connect to Ollama: {e}")
        print("Make sure Ollama is running: ollama serve")
        return None


if __name__ == "__main__":
    model = asyncio.run(check_ollama())
