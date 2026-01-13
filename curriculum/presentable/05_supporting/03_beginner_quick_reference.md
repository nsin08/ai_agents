# Beginner Quick Reference Guide (1-Page Cheat Sheet)

**Level**: Beginner  
**Use**: Quick lookup while coding  
**Print**: Yes, fits on 1-2 pages

---

## Essential Commands

```bash
# Virtual Environment
uv venv                           # Create virtual environment
source .venv/bin/activate        # Activate (Linux/Mac)
.venv\Scripts\activate           # Activate (Windows)
uv pip install package-name      # Install packages

# Git
git clone <url>                  # Download repository
git status                       # See changes
git add file.py                  # Stage file
git commit -m "message"          # Commit changes
git push                         # Push to remote

# Testing
pytest tests/                    # Run all tests
pytest tests/test_file.py -v     # Run with output
pytest --cov=src                 # Coverage report

# Run Code
python script.py                 # Execute Python file
python -m pytest                 # Run tests via module
python -i script.py              # Interactive mode
```

---

## Python Patterns

```python
import asyncio
from agent_labs.orchestrator import Agent
from agent_labs.llm_providers import MockProvider, OllamaProvider
from agent_labs.memory import ShortTermMemory, MemoryItem

provider = MockProvider()  # or OllamaProvider(model="llama2")
agent = Agent(provider=provider)
memory = ShortTermMemory(max_items=10)

def run_agent(agent, goal, max_turns=1):
    return asyncio.run(agent.run(goal, max_turns=max_turns))

# Use memory by injecting history into the prompt
memory.store(MemoryItem(role="user", content="Hello"))
history = "\n".join(item.content for item in memory.retrieve())
response = run_agent(agent, f"History:\n{history}\nUser: say hello")
print(response)
```

---

## Common Patterns by Chapter

### Ch 1: Setup
```bash
python --version  # Should be 3.11+
uv --version
pytest --version
```

### Ch 2: Agent Loop
```python
user_input = "What is an AI agent?"
response = run_agent(agent, user_input, max_turns=2)
print(response)
```

### Ch 3: RAG
```python
from agent_labs.memory import RAGMemory, MemoryItem

rag = RAGMemory()
rag.store(MemoryItem(role="doc", content="Paris is the capital of France."))
results = rag.retrieve(query="capital of France", top_k=1)
print(results[0].content)
```

### Ch 4: Tools
```python
from agent_labs.tools import ToolRegistry, Calculator

registry = ToolRegistry()
registry.register(Calculator())
result = registry.execute("calculator", {"operation": "add", "a": 2, "b": 3})
print(result.output)
```

### Ch 5: Memory Persistence
```python
import json
from pathlib import Path

def save_preferences(data, file="prefs.json"):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)

def load_preferences(file="prefs.json"):
    return json.load(open(file)) if Path(file).exists() else {}
```

### Ch 6: Testing
```python
import pytest

def test_my_feature():
    result = 2 + 2
    assert result == 4
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: No module named 'agent_labs'` | Install: `uv pip install -r requirements.txt` |
| `NameError: name 'XYZ' is not defined` | Add import: `from module import XYZ` |
| `pytest: command not found` | Install: `uv pip install pytest` |
| `virtual environment not activated` | Run: `source .venv/bin/activate` (Linux/Mac) or `.venv\Scripts\activate` (Windows) |
| `git: command not found` | Install Git from https://git-scm.com/downloads |
| `Python version too old` | Download 3.11+ from https://python.org |
| Agent doesn't remember | Use `ShortTermMemory` and include history in the prompt |
| Test fails randomly | Switch to `MockProvider` instead of real LLM |

---

## File Locations

```
ai_agents/
|-- labs/
|   |-- 00/                    # Environment (Chapter 1)
|   |-- 01/                    # RAG (Chapter 3)
|   |-- 02/                    # Tools (Chapter 4)
|   |-- 04/                    # Memory (Chapter 5)
|-- curriculum/presentable/01_beginner/
|   |-- chapter_01_*.md        # Chapters
|   |-- ...
|-- src/agent_labs/
|   |-- orchestrator/          # Agent core
|   |-- llm_providers/         # Providers (OpenAI, Mock, Ollama)
|   |-- memory/                # Memory systems
|   |-- tools/                 # Tool implementations
|   |-- ...
|-- tests/                     # Test files
```

---

## Key Classes & Methods

| Class | Method | Purpose |
|-------|--------|---------|
| `Agent` | `run(goal, max_turns)` | Run the agent loop |
| `MockProvider` | `generate(prompt)` | Returns mock response (echoes) |
| `OllamaProvider` | `generate(prompt)` | Calls local LLM |
| `ShortTermMemory` | `store(item)` | Add memory item |
| `ShortTermMemory` | `retrieve(query)` | Get memory items |
| `RAGMemory` | `retrieve(query, top_k)` | Retrieve relevant items |
| `ToolRegistry` | `register(tool)` | Register tool |
| `ToolRegistry` | `execute(name, input)` | Execute tool |

---

## Decision Trees

### Which Provider to Use?
- Do you want to test locally?
  - YES -> Use `MockProvider` (instant, free)
  - NO -> Do you have a local LLM?
    - YES -> Use `OllamaProvider`
    - NO -> Use a cloud provider adapter (not yet implemented here)

### How to Store Data?
- Does data need to survive restart?
  - NO -> Use `ShortTermMemory` (RAM-based)
  - YES -> Use JSON file or `LongTermMemory`
    - Simple -> JSON with `open()` + `json.dump()`
    - Complex -> Database (later curriculum)

### Should I Test It?
- Is it part of core functionality?
  - YES -> Write unit test
  - Tools? -> Test tool behavior
  - Memory? -> Test persistence
  - User-facing? -> Write integration test

---

## Common Mistakes & Fixes

| Wrong | Right |
|-------|-------|
| No imports | Add `from module import Class` |
| Unactivated venv | Always activate before running |
| No memory in agent | Use `ShortTermMemory` and inject history |
| Tool execution fails silently | Wrap calls in try/except |
| Memory grows forever | Set `max_items` limit |
| Test uses real LLM | Switch to `MockProvider` |
| No error handling | Add `assert` statements in tests |
| Ignoring error messages | Read the error, it tells you what's wrong |

---

## Learning Resources

| Topic | Resource |
|-------|----------|
| Python Basics | https://python.org/doc |
| pytest | https://pytest.org/doc |
| Git | https://git-scm.com/doc |
| LangChain | https://langchain.readthedocs.io |
| OpenAI API | https://platform.openai.com/docs |
| Ollama | https://ollama.ai |

---

## Quick Checklist Before Moving to Intermediate

- [ ] Completed all 7 chapters
- [ ] Solved all 21 exercises
- [ ] Wrote and ran tests
- [ ] Built a small project
- [ ] Understand agent loop (observe -> plan -> act)
- [ ] Know the difference: tools vs memory vs RAG
- [ ] Can explain: embeddings, tokens, hallucination
- [ ] Feel confident running Python + pytest + git

**Ready?** -> Move to Intermediate curriculum!

---

## Emergency Debugging Script

```python
# Copy this when stuck (debug_helper.py)
import sys
from pathlib import Path

print(f"Python: {sys.version}")
print(f"Working Dir: {Path.cwd()}")
print(f"Virtual Env: {sys.prefix}")

# Check imports
try:
    from agent_labs.orchestrator import Agent
    print("[OK] agent_labs installed")
except ImportError:
    print("[FAIL] agent_labs NOT installed")

try:
    import pytest
    print("[OK] pytest installed")
except ImportError:
    print("[FAIL] pytest NOT installed")

# List installed packages
import subprocess
print("\nInstalled packages:")
subprocess.run(["pip", "list"])
```

Run with: `python debug_helper.py`

---

## Final Tips

1. **Read error messages** - They're your friend
2. **Google the error** - Odds are someone had it before
3. **Print debugging** - `print(variable)` to see what's happening
4. **Test incrementally** - Change one thing at a time
5. **Ask for help** - Show your error message + code
6. **Break problems down** - Don't build everything at once
7. **Read the docs** - Library docs have examples
8. **Version control always** - Use git from day 1
9. **Test early** - Write tests while coding, not after
10. **Have fun** - You're building AI agents!

---

**Bookmark this page!** Return here whenever you need a quick lookup.

Last Updated: January 2026 | For Beginner Curriculum

---

## Document Checklist

- [ ] Accessibility review (WCAG AA)
- [ ] Scannable sections with short bullets
- [ ] Commands and tips included
- [ ] ASCII only
