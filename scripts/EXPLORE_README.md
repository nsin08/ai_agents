# Exploration Notebook Guide

## Overview

`explore.py` is a script-based notebook for testing AI agents with predefined learning scenarios. It runs structured prompts to demonstrate agent capabilities with flexible provider and model selection via CLI arguments.

**No setup required** - runs instantly with MockProvider by default. Optional Ollama integration for real LLM responses.

**Location:** `scripts/explore.py` in workspace  
**Workspace:** `d:\wsl_shared\src\ai_agents`  
**Python:** 3.11+ required

---

## Setup (Optional - Choose One)

### Setup Method 1: From Scripts Directory (Automated)

```bash
cd scripts

# Windows
setup.bat
.venv\Scripts\activate.bat

# Linux/macOS
chmod +x setup.sh
./setup.sh
source .venv/bin/activate
```

### Setup Method 2: Using Make

```bash
cd scripts
make setup      # Creates venv and installs dependencies
```

### Setup Method 3: No Setup - Run Directly

```bash
# From scripts/ or workspace root, run without setup
python scripts/explore.py quickstart
```

---

## Quick Start

### 1. No Setup Required - Run Immediately

```bash
# Run default quickstart scenario (instant, uses MockProvider)
python scripts/explore.py

# Run specific scenario
python scripts/explore.py reasoning
python scripts/explore.py teaching
python scripts/explore.py storytelling

# List all scenarios
python scripts/explore.py --list
python scripts/explore.py --help
```

### 2. With Ollama (For Real LLM - Optional)

```bash
# Prerequisites:
# 1. Install Ollama from https://ollama.ai/download
# 2. Start Ollama: ollama serve (in separate terminal)
# 3. Pull model: ollama pull llama2

# Run with Ollama
python scripts/explore.py reasoning --ollama
python scripts/explore.py teaching --ollama --model mistral
python scripts/explore.py quickstart --ollama
```

### 3. With Cloud Providers (OpenAI, Anthropic, etc.)

```bash
# Set API key
export OPENAI_API_KEY="sk-..."     # Linux/macOS
# OR
set OPENAI_API_KEY=sk-...           # Windows

# Run with OpenAI
python scripts/explore.py reasoning --openai
python scripts/explore.py teaching --openai --model gpt-4
```

---

## Available Scenarios

| Scenario | Description | Example | Prompts | Provider |
|----------|-------------|---------|---------|----------|
| `quickstart` | Simple introductory prompts (2-3 quick questions) | `python explore.py quickstart` | 3 | Mock (instant) |
| `reasoning` | Test logical reasoning and puzzle-solving | `python explore.py reasoning --ollama` | 3 | Ollama/Mock |
| `storytelling` | Creative story generation and narrative | `python explore.py storytelling --openai` | 3 | Ollama/Mock |
| `teaching` | Complex topic explanations and tutorials | `python explore.py teaching --ollama` | 3 | Ollama/Mock |
| `advanced` | Advanced multi-turn reasoning tasks | `python explore.py advanced --ollama --turns 5` | 3 | Ollama/Mock |
| `openai` | OpenAI GPT-4 specific responses | `python explore.py openai` | 3 | OpenAI |
| `mock` | Fast testing without LLM | `python explore.py mock` | 3 | Mock (instant) |

## Provider Configuration

### CLI Arguments for Provider Selection

```bash
# Provider flags
python scripts/explore.py SCENARIO --openai              # Use OpenAI
python scripts/explore.py SCENARIO --ollama              # Use Ollama
python scripts/explore.py SCENARIO --mock                # Use Mock

# Model override
python scripts/explore.py SCENARIO --model MODEL_NAME

# Examples
python scripts/explore.py reasoning --openai --model gpt-4
python scripts/explore.py teaching --ollama --model phi
python scripts/explore.py quickstart --mock
```

### Ollama Setup

```bash
# Use specific model
python scripts/explore.py teaching --ollama --model phi
python scripts/explore.py advanced --ollama --model llama3.2:3b

# Custom endpoint
export OLLAMA_BASE_URL="http://custom-server:11434"
python scripts/explore.py reasoning --ollama
```

### OpenAI Setup

```bash
# Set API key
export OPENAI_API_KEY="sk-..."

# Run scenarios
python scripts/explore.py reasoning --openai              # Uses default model
python scripts/explore.py teaching --openai --model gpt-3.5-turbo
python scripts/explore.py openai --model gpt-4           # OpenAI scenario
```

## Adding Custom Scenarios

Edit `explore.py` to add your own scenarios:

```python
SCENARIOS = {
    "my_scenario": Scenario(
        name="My Custom Scenario",
        description="Description of what this tests",
        provider="ollama",  # Default: "ollama", "openai", "mock"
        model="llama2",
        max_turns=5,
        prompts=["First prompt", "Second prompt", "Third prompt"],
    ),
}
```

**Override at runtime:**
```bash
python scripts/explore.py my_scenario --openai --model gpt-4
```

## Troubleshooting

### Ollama Connection Error

```bash
# Error: Connection refused to localhost:11434
# Solution 1: Start Ollama server
ollama serve

# Solution 2: Use different provider
python scripts/explore.py reasoning --openai    # Use OpenAI
python scripts/explore.py reasoning --mock      # Use Mock
```

### Model Not Found (Ollama)

```bash
# Error: Model not found
# Solution: Download model
ollama pull phi
ollama pull llama3.2:3b

# Use pre-pulled model
python scripts/explore.py reasoning --ollama --model phi
```

### Missing OpenAI API Key

```bash
# Error: OPENAI_API_KEY not set
# Solution 1: Set env var
export OPENAI_API_KEY="sk-..."
python scripts/explore.py reasoning --openai

# Solution 2: Use different provider
python scripts/explore.py reasoning --ollama
python scripts/explore.py reasoning --mock
```

### Slow Responses

```bash
# Use faster model
python scripts/explore.py reasoning --ollama --model phi

# Or use Mock for instant testing
python scripts/explore.py reasoning --mock
```

## Example Output

```
╔════════════════════════════════════════════════════════════════╗
║  Reasoning & Logic                                             ║
╚════════════════════════════════════════════════════════════════╝

Description: Test agent's reasoning capabilities

Configuration:
  Provider:  ollama
  Model:     phi
  Max Turns: 5

────────────────────────────────────────────────────────────────
Prompt 1/3
────────────────────────────────────────────────────────────────

📝 Solve this riddle: I have cities but no houses. What am I?

⏳ Agent processing...

✓ Response:
[Agent's response with reasoning...]

════════════════════════════════════════════════════════════════
✓ Scenario 'reasoning' completed successfully!
════════════════════════════════════════════════════════════════
```

## Command Reference

```bash
# List scenarios
python scripts/explore.py --list

# Run scenario (uses default provider/model)
python scripts/explore.py reasoning

# Override provider
python scripts/explore.py reasoning --openai
python scripts/explore.py reasoning --ollama
python scripts/explore.py reasoning --mock

# Override model
python scripts/explore.py teaching --ollama --model phi
python scripts/explore.py reasoning --openai --model gpt-3.5-turbo

# Show help
python scripts/explore.py --help
```

---

## 🔌 Provider Configuration Details

### MockProvider (Default - Instant)
- **Speed:** Instant
- **Setup:** None required
- **Best for:** Quick testing, CI/CD, learning structure

```bash
python scripts/explore.py quickstart
# OR explicit
python scripts/explore.py quickstart --mock
```

### OllamaProvider (Local LLM - Optional)
- **Speed:** Depends on model and hardware
- **Setup:** ~5 minutes (install Ollama, pull model)
- **Best for:** Real LLM testing without API keys

```bash
# Prerequisites
ollama pull mistral     # ~4GB, recommended
# OR
ollama pull llama2      # ~4GB, alternative

# Run
python scripts/explore.py reasoning --ollama
python scripts/explore.py teaching --ollama --model mistral
```

### OpenAIProvider (Cloud - Optional)
- **Speed:** Fast (API-based)
- **Setup:** API key required
- **Best for:** Production-quality responses, GPT-4

```bash
# Set API key
export OPENAI_API_KEY="sk-..."

# Run
python scripts/explore.py reasoning --openai
python scripts/explore.py teaching --openai --model gpt-4
python scripts/explore.py advanced --openai
```

---

## ✅ Verify Installation

```bash
# Test 1: No-setup test (should be instant)
python scripts/explore.py --mock

# Test 2: List scenarios
python scripts/explore.py --list

# Test 3: Run quickstart
python scripts/explore.py quickstart
```

Expected: Agent processes each prompt and shows response.

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: No module named agent_labs` | Run `python -m pip install -e .` from workspace root |
| `Scenario not found` | Run `python scripts/explore.py --list` to see available scenarios |
| `OllamaProvider connection error` | Start Ollama: `ollama serve` in separate terminal; check running: `ollama list` |
| `Model not found in Ollama` | Pull model: `ollama pull mistral` or `ollama pull llama2` |
| `OPENAI_API_KEY not set` | Set key: `export OPENAI_API_KEY=sk-...` (Linux/macOS) or `set OPENAI_API_KEY=sk-...` (Windows) |
| Slow responses | Use MockProvider (instant) or switch to faster model (mistral < llama2) |

---

## 📖 Related Documentation

- **README.md** - Complete interactive agent guide with all script descriptions
- **QUICK_START.md** - Quick setup reference for all scripts
- **quick_test.py** - Single-prompt testing (see usage: `python quick_test.py`)
- **interactive_agent.py** - Full REPL interface
- **advanced_interactive_agent.py** - REPL with observability

---

## Next Steps
