# Interactive Agent Scripts

Three interactive scripts for experimenting with AI agents from src/agent_labs.

## Quick Start (30 seconds)

\\\ash
# Option 1: Single prompt (fastest)
python scripts/quick_test.py "What is Python?"

# Option 2: Interactive REPL (best for exploration)
python scripts/interactive_agent.py

# Option 3: Learning scenarios
python scripts/explore.py quickstart
\\\

---

## Scripts Overview

| Script | Purpose | Best For |
|--------|---------|----------|
| **quick_test.py** | Single-prompt testing | Fast verification, CI/CD, one-liners |
| **interactive_agent.py** | Full REPL interface | Deep exploration, conversations, debugging |
| **explore.py** | Predefined scenarios | Structured learning, teaching, demos |

---

## 1. quick_test.py - One-Liner Testing

**Usage:**
\\\ash
python scripts/quick_test.py "Your prompt here"
\\\

**Options:**
\\\ash
python scripts/quick_test.py "Prompt" --ollama           # Use Ollama (requires ollama serve)
python scripts/quick_test.py "Prompt" --model mistral    # Change model
python scripts/quick_test.py "Prompt" --turns 5          # More reasoning iterations
\\\

**Examples:**
\\\ash
python scripts/quick_test.py "What is machine learning?"
python scripts/quick_test.py "2+2=?" --ollama --model mistral
\\\

**Pros:** Instant (MockProvider default), single command, perfect for automation/scripts  
**Cons:** Limited interaction, must restart for each prompt

---

## 2. interactive_agent.py - REPL Interface

**Start REPL:**
\\\ash
python scripts/interactive_agent.py
\\\

**Interactive Commands:**

| Command | Example | Effect |
|---------|---------|--------|
| Ask question | \> What is AI?\ | Run agent with prompt |
| \/help\ | \> /help\ | Show help menu |
| \/config\ | \> /config\ | Display configuration |
| \/reset\ | \> /reset\ | Clear history, restart |
| \/provider TYPE\ | \> /provider ollama\ | Switch to mock or ollama |
| \/model NAME\ | \> /model mistral\ | Set model (for ollama) |
| \/max_turns N\ | \> /max_turns 5\ | Set reasoning iterations (1-10) |
| \/history\ | \> /history\ | Show conversation history |
| \/exit\ | \> /exit\ | Quit |

**Example Session:**
\\\
> /provider ollama
 Switched to ollama provider

> Hi, my name is Neeraj
 Agent thinking...
[Agent responds and remembers your name]

> What is 2+2?
 Agent thinking...
The answer is 4.

> Do you remember my name?
 Agent thinking...
Yes, your name is Neeraj.

> /history
[Shows full conversation]

> /exit
 Goodbye!
\\\

**Features:** Conversation memory (context injection), provider switching, full history tracking, real-time feedback  
**Pros:** Full conversation history, command-driven interface, memory across turns  
**Cons:** Requires interactive terminal, OllamaProvider needs Ollama running

---

## 3. explore.py - Predefined Scenarios

**Usage:**
\\\ash
python scripts/explore.py SCENARIO_NAME
\\\

**Available Scenarios:**
\\\ash
python scripts/explore.py quickstart     # Simple 2-3 question intro
python scripts/explore.py reasoning      # Logic puzzles and riddles
python scripts/explore.py storytelling   # Creative writing prompts
python scripts/explore.py teaching       # Topic explanations
python scripts/explore.py advanced       # Complex multi-turn reasoning
\\\

**Features:** Structured learning paths, batch prompts, great for demos/teaching  
**Pros:** No configuration needed, good for learning, reproducible  
**Cons:** Limited to predefined scenarios

---

## Setup & Configuration

### Using Ollama (Optional)

1. **Install Ollama**: https://ollama.ai
2. **Start Ollama server**: \ollama serve\
3. **Pull a model** (one-time):
   \\\ash
   ollama pull llama2      # ~4GB
   ollama pull mistral     # ~4GB
   \\\
4. **Use in scripts**:
   \\\ash
   python scripts/interactive_agent.py
   > /provider ollama
   > /model mistral
   > Your prompt here
   \\\

### Environment Variables

\\\ash
# Set Ollama server URL (if not localhost:11434)
\http://localhost:11434="http://localhost:11434"
\\\

---

## Common Scenarios

| Scenario | Command |
|----------|---------|
| Quick test with MockProvider | \python scripts/quick_test.py "Explain quantum computing"\ |
| Test with real LLM (Ollama) | \python scripts/quick_test.py "..." --ollama --model mistral\ |
| Conversation with memory | \python scripts/interactive_agent.py\ then use prompts |
| Structured learning | \python scripts/explore.py storytelling\ |

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| ModuleNotFoundError | Ensure you're in workspace root: \cd d:\wsl_shared\src\ai_agents\ |
| OllamaProvider connection error | Start Ollama: \ollama serve\ |
| Model not found | Pull model: \ollama pull llama2\ |
| Script hangs | Check Ollama is running: \ollama list\ |

---

## Files in This Directory

- \quick_test.py\ - Single-prompt testing script
- \interactive_agent.py\ - Full REPL with commands
- \explore.py\ - Predefined learning scenarios
- \memory_test.py\ - Memory/context injection verification
- \README.md\ - This file
