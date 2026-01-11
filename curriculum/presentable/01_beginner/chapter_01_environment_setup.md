# Chapter 1: Environment Setup

**Level**: Beginner  
**Duration**: 30-45 minutes  
**Prerequisites**: None (complete beginners welcome!)  
**Lab**: [Lab 0 - Environment Setup](../../../../labs/00/README.md)

---

## Learning Objectives

By the end of this chapter, you will:

1. **Understand** what tools are needed to build AI agents
2. **Install** Python 3.11+ and the `uv` package manager
3. **Set up** your first agent development environment
4. **Run** your first "Hello Agent" program
5. **Verify** your setup with automated tests

---

## 1. Introduction: Why Environment Setup Matters

Before you build anything, you need the right tools. Think of it like a carpenter's workshop—you need:
- A workbench (Python environment)
- Tools (libraries and packages)
- Safety equipment (testing tools)
- A way to organize everything (project structure)

**The Good News**: Modern Python tools make this easy. We'll use `uv`, a fast package manager that handles everything automatically.

**What You'll Build**: By the end of this chapter, you'll have a fully working agent development environment that runs a simple "Hello Agent" program.

---

## 2. What You Need (The Toolbox)

### Python 3.11+
**What it is**: Python is the programming language we'll use. Version 3.11 or higher is required because it has performance improvements and features agents need.

**Why this version**: Newer Python versions have better async support (agents often do multiple things at once) and improved error messages (helpful when debugging).

**How to check if you have it**:
```bash
python --version
# Should show: Python 3.11.x or higher
```

**Where to get it**: https://www.python.org/downloads/

### uv (Package Manager)
**What it is**: `uv` is a super-fast tool that installs Python packages (libraries) for you. It's like an app store for Python code.

**Why uv (not pip)**: 
- 10-100x faster than traditional `pip`
- Handles dependencies automatically
- Creates isolated environments (no conflicts)

**How to install**:
```bash
# Option 1: Using pip (if you already have Python)
pip install uv

# Option 2: Using curl (on Linux/Mac)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Option 3: On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Git (Version Control)
**What it is**: Git tracks changes to your code. Think of it like "undo" for your entire project, but much more powerful.

**Why you need it**: You'll download lab materials from GitHub, and later you'll save your own work.

**Where to get it**: https://git-scm.com/downloads

### A Code Editor
**What it is**: Where you write code. We recommend VS Code (free and powerful).

**Why VS Code**: 
- Free
- Great Python support
- Built-in terminal
- Extensions for testing and debugging

**Where to get it**: https://code.visualstudio.com/

---

## 3. Step-by-Step Setup (15 minutes)

### Step 1: Clone the Repository
First, download all the lab materials:

```bash
# Navigate to where you want the project
cd ~/Documents  # or any folder you prefer

# Clone the repository
git clone https://github.com/nsin08/ai_agents.git

# Enter the project folder
cd ai_agents
```

**What just happened**: You downloaded all the code, labs, and examples to your computer.

### Step 2: Create a Virtual Environment
A virtual environment is like a clean room for your project—it keeps your dependencies separate from other Python projects.

```bash
# Create the environment
uv venv

# Activate it (Linux/Mac)
source .venv/bin/activate

# Activate it (Windows)
.venv\Scripts\activate
```

**You'll see**: Your command prompt now shows `(.venv)` at the beginning—this means you're "inside" the environment.

### Step 3: Install Dependencies
Now install all the packages agents need:

```bash
# Install from Lab 0's requirements file
uv pip install -r labs/00/requirements.txt
```

**What gets installed**:
- `pytest` - for testing
- `agent_labs` - the core agent library
- Helper tools for debugging and observability

This takes about 30 seconds.

### Step 4: Verify Your Setup
Let's make sure everything works:

```bash
# Run the hello agent
python labs/00/src/hello_agent.py
```

**Expected output**:
```
Hello from AI Agent! 🤖
Agent initialized successfully.
Environment: Python 3.11.5
Provider: MockProvider (echo mode)
Response: I am a simple agent. You said: Hello!
```

If you see this, **congratulations!** Your environment is ready.

### Step 5: Run the Tests
Agents need tests to verify they work correctly. Run Lab 0's test suite:

```bash
pytest labs/00/tests/test_hello_agent.py -v
```

**Expected output**:
```
test_hello_agent_initialization PASSED
test_hello_agent_responds PASSED
test_hello_agent_mock_provider PASSED
==================== 3 passed in 0.15s ====================
```

**All green?** Perfect! You're ready to build agents.

---

## 4. Understanding What You Built

### Project Structure
Let's explore what you just set up:

```
ai_agents/
├── labs/
│   ├── 00/               ← You're here (Lab 0)
│   │   ├── src/
│   │   │   └── hello_agent.py    ← Your first agent
│   │   ├── tests/
│   │   │   └── test_hello_agent.py
│   │   └── requirements.txt
│   ├── 01/               ← Next lab (RAG)
│   ├── 02/               ← Lab 2 (Tools)
│   └── ...
├── src/
│   └── agent_labs/       ← Core agent library
└── .venv/                ← Your virtual environment
```

### The Hello Agent Code
Open `labs/00/src/hello_agent.py` in your editor. Let's break it down:

```python
from agent_labs.orchestrator import AgentOrchestrator
from agent_labs.llm_providers import MockProvider

# Create a provider (MockProvider echoes back messages)
provider = MockProvider()

# Create the agent with the provider
agent = AgentOrchestrator(llm_provider=provider)

# Send a message
response = agent.run("Hello!")
print(response)
```

**Key concepts**:
1. **Import**: Load code from the `agent_labs` library
2. **Provider**: Where responses come from (mock, OpenAI, Ollama, etc.)
3. **Orchestrator**: The "brain" that coordinates everything
4. **run()**: Send a message and get a response

Don't worry if this doesn't all make sense yet—we'll build on this in every chapter.

---

## 5. Hands-On Exercise

**Exercise 1: Modify the Hello Agent**

1. Open `labs/00/src/hello_agent.py`
2. Change the message from `"Hello!"` to your own message
3. Run it: `python labs/00/src/hello_agent.py`
4. Observe: MockProvider echoes back your message

**Exercise 2: Break It (Then Fix It)**

1. Comment out the import line: `# from agent_labs.orchestrator import AgentOrchestrator`
2. Run it again—what error do you get?
3. Uncomment the line and verify it works again

**Why this matters**: Learning to read error messages is a superpower. Most bugs are just missing imports or typos.

**Exercise 3: Add Logging**

Add this line after creating the agent:
```python
print(f"Agent initialized: {agent}")
```

Run it and see what information the agent object contains.

---

## 6. Common Troubleshooting

### Problem: `uv: command not found`
**Solution**: 
1. Make sure uv is installed: `pip install uv`
2. Restart your terminal
3. Verify: `uv --version`

### Problem: `ModuleNotFoundError: No module named 'agent_labs'`
**Solution**: 
1. Make sure you're in the project root: `cd ai_agents`
2. Activate your virtual environment
3. Reinstall: `uv pip install -r labs/00/requirements.txt`
4. Run from the root directory, not inside `labs/00/`

### Problem: Tests fail with import errors
**Solution**: 
Always run pytest from the project root:
```bash
# Wrong: cd labs/00 && pytest tests/
# Right: pytest labs/00/tests/ -v
```

### Problem: Python version is too old
**Solution**: 
1. Install Python 3.11+ from python.org
2. Create a new venv: `python3.11 -m venv .venv`
3. Activate and continue

---

## 7. Key Concepts Summary

| Concept | What It Is | Why It Matters |
|---------|------------|----------------|
| **Virtual Environment** | Isolated Python installation | Prevents package conflicts |
| **uv** | Fast package manager | Installs dependencies quickly |
| **MockProvider** | Fake LLM for testing | No API costs while learning |
| **AgentOrchestrator** | Core agent controller | Manages the agent lifecycle |
| **pytest** | Testing framework | Verifies your code works |

---

## 8. Glossary

- **Dependencies**: Other code libraries your project needs
- **Virtual Environment**: Isolated Python installation per project
- **Package Manager**: Tool that installs libraries (like uv or pip)
- **Repository**: Collection of code files (usually on GitHub)
- **Provider**: Where LLM responses come from (OpenAI, Ollama, mock)
- **Orchestrator**: The central coordinator for an agent
- **Test Suite**: Collection of automated tests

---

## 9. What's Next?

✅ **You've completed**: Environment setup and your first agent  
🎯 **Next chapter**: [Chapter 2 - Your First Agent](./chapter_02_your_first_agent.md)  
🔬 **Next lab**: [Lab 1 - RAG Fundamentals](../../../../labs/01/README.md)

### Skills Unlocked
- ✅ Set up Python development environment
- ✅ Use uv for package management
- ✅ Run agents from the command line
- ✅ Execute tests to verify code works
- ✅ Read and understand basic agent code

### Preview: Chapter 2
In the next chapter, you'll:
- Build a conversational agent from scratch
- Understand the orchestrator loop (observe → plan → act)
- Add basic memory so agents remember context
- Learn about different LLM providers (mock vs. real)

---

## 10. Self-Assessment Quiz

Test your understanding (answers at the end):

1. **What is a virtual environment?**
   - A) A cloud server
   - B) An isolated Python installation for one project
   - C) A type of LLM provider
   - D) A testing framework

2. **Why do we use `uv` instead of `pip`?**
   - A) It's the only way to install packages
   - B) It's much faster and handles dependencies better
   - C) pip is deprecated
   - D) uv comes with Python by default

3. **What does `MockProvider` do?**
   - A) Calls OpenAI's API
   - B) Echoes back messages for testing
   - C) Runs local LLMs
   - D) Provides memory storage

4. **Where should you run pytest from?**
   - A) Inside the `labs/00/` directory
   - B) Inside the `tests/` directory
   - C) The project root directory
   - D) Anywhere—it doesn't matter

5. **What does the `AgentOrchestrator` do?**
   - A) Stores conversation history
   - B) Manages the agent's core loop and lifecycle
   - C) Runs local LLMs
   - D) Handles database connections

6. **If you see `(.venv)` in your terminal prompt, what does it mean?**
   - A) You're connected to a server
   - B) Your virtual environment is activated
   - C) Python is running
   - D) There's an error

7. **What command verifies your Python version?**
   - A) `python --check`
   - B) `python --version`
   - C) `uv version`
   - D) `which python`

8. **Why do we need tests?**
   - A) To make the code slower
   - B) To verify code works correctly
   - C) They're optional and not important
   - D) Only for large projects

9. **What does `git clone` do?**
   - A) Creates a new project
   - B) Downloads a repository to your computer
   - C) Uploads your code to GitHub
   - D) Deletes a repository

10. **What happens if you don't activate your virtual environment?**
    - A) Python won't run
    - B) Packages might install to the wrong location
    - C) Tests will always fail
    - D) Nothing—it's not necessary

### Answers
1. B, 2. B, 3. B, 4. C, 5. B, 6. B, 7. B, 8. B, 9. B, 10. B

**Scoring**:
- 9-10: Excellent! You're ready for Chapter 2.
- 7-8: Good! Review the sections you missed.
- 5-6: Re-read the chapter and try the exercises again.
- <5: No worries! This is new. Re-read carefully and ask for help.

---

## Further Reading

- [uv Documentation](https://github.com/astral-sh/uv)
- [Python Virtual Environments Explained](https://docs.python.org/3/tutorial/venv.html)
- [Lab 0 - Full Lab Materials](../../../../labs/00/README.md)
- [pytest Tutorial](https://docs.pytest.org/en/stable/)

---

**Chapter Complete!** 🎉  
You've set up your development environment and run your first agent. Time to build something more sophisticated!

**Next**: [Chapter 2 - Your First Agent →](./chapter_02_your_first_agent.md)

---

*Estimated reading time: 25 minutes*  
*Hands-on exercises: 15-20 minutes*  
*Total chapter time: 40-45 minutes*
