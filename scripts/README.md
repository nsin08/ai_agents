# Interactive Agent Scripts

Four interactive scripts for experimenting with AI agents from `src/agent_labs`.

Note: These are test scripts for agent behavior and learning workflows.

## Quick Start (30 seconds)

```bash
# Option 1: Single prompt (fastest)
python scripts/quick_test.py "What is Python?"

# Option 2: Interactive REPL (best for exploration)
python scripts/interactive_agent.py

# Option 3: Production-grade with observability, context & safety
python scripts/advanced_interactive_agent.py

# Option 4: Learning scenarios
python scripts/explore.py quickstart
```

---

## Scripts Overview

| Script | Purpose | Best For |
|--------|---------|----------|
| **quick_test.py** | Single-prompt testing | Fast verification, CI/CD, one-liners |
| **interactive_agent.py** | Full REPL interface with tools | Deep exploration, conversations, debugging |
| **advanced_interactive_agent.py** | REPL with observability, context & safety | Production patterns, monitoring, safety guardrails |
| **explore.py** | Predefined scenarios | Structured learning, teaching, demos |

---

## 1. quick_test.py - One-Liner Testing

**Usage:**
```bash
python scripts/quick_test.py "Your prompt here"
```

**Options:**
```bash
python scripts/quick_test.py "Prompt" --ollama           # Use Ollama (requires ollama serve)
python scripts/quick_test.py "Prompt" --model mistral    # Change model
python scripts/quick_test.py "Prompt" --turns 5          # More reasoning iterations
```

**Examples:**
```bash
python scripts/quick_test.py "What is machine learning?"
python scripts/quick_test.py "2+2=?" --ollama --model mistral
python scripts/quick_test.py "I'm thinking of a number between 1-100. It's even, divisible by 3, and less than 50. What could it be?" --turns 5
```

**Pros:** Instant (MockProvider default), single command, perfect for automation/scripts  
**Cons:** Limited interaction, must restart for each prompt

---

## 2. interactive_agent.py - REPL Interface

**Start REPL:**
```bash
python scripts/interactive_agent.py
```

**Interactive Commands:**

| Command | Example | Effect |
|---------|---------|--------|
| Ask question | `> What is AI?` | Run agent with prompt |
| `/help` | `> /help` | Show help menu |
| `/config` | `> /config` | Display configuration |
| `/reset` | `> /reset` | Clear history, restart |
| `/provider TYPE` | `> /provider ollama` | Switch to mock or ollama |
| `/model NAME` | `> /model mistral` | Set model (for ollama) |
| `/max_turns N` | `> /max_turns 5` | Set reasoning iterations (1-10) |
| `/tools` | `> /tools` | List available tools and usage |
| `/summarize TEXT` | `> /summarize Long text here...` | Summarize text (min 50 chars) |
| `/analyze CODE` | `> /analyze def foo(): pass` | Analyze code quality/security/performance |
| `/history` | `> /history` | Show conversation history |
| `/exit` | `> /exit` | Quit |

**Example Session:**
```
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
```

**Features:** Conversation memory (context injection), provider switching, full history tracking, real-time feedback, integrated tool support  
**Pros:** Full conversation history, command-driven interface, memory across turns, real tools for text and code analysis  
**Cons:** Requires interactive terminal, OllamaProvider needs Ollama running

---

### Tool Integration

The interactive agent now includes real tools for practical tasks:

#### 1. Text Summarizer Tool

Summarize long text passages (minimum 50 characters):

```bash
python scripts/interactive_agent.py
> /tools
[Shows available tools and usage]

> /summarize The quick brown fox jumps over the lazy dog. This is a longer sentence to make it over 50 characters minimum.
Tool executing: TextSummarizer...
Summary: Fast fox leaps over lazy dog.
```

**Use Cases:**
- Compress long documents
- Extract key points from articles
- Summarize meeting notes
- Condense long descriptions

#### 2. Code Analyzer Tool

Analyze Python code for quality, security, or performance issues:

```bash
> /analyze def slow_function(items):
>     for i in range(len(items)):
>         for j in range(len(items)):
>             if items[i] == items[j]:
>                 pass
> /analyze CODE quality

Tool executing: CodeAnalyzer...
Analysis Results:
- Nested loop complexity: O(n²) - inefficient for large lists
- Suggestion: Use set for O(n) lookup
- Performance: 🔴 Poor - optimize loops
```

**Analysis Types:**
- `quality` - Code style, readability, best practices
- `security` - Potential vulnerabilities, safe practices
- `performance` - Algorithmic complexity, optimization opportunities

**Use Cases:**
- Review code before commit
- Identify performance bottlenecks
- Security audit of user input handling
- Learn optimization patterns

#### Example Tool Session

```bash
> /provider ollama
Switched to ollama provider

> /model mistral
Changed model to: mistral

> /tools
Available Tools:
  - text_summarizer: Summarize long text passages
  - code_analyzer: Analyze code for quality/security/performance

> /summarize Artificial intelligence is transforming industries. Machine learning enables computers to learn from data. Deep learning uses neural networks with multiple layers. NLP processes human language. AI applications span healthcare, finance, and robotics.
Tool executing: TextSummarizer...
Summary: AI transforms industries through ML and DL, enabling language processing across healthcare, finance, and robotics.

> /analyze def process_data(data, threshold=10):
>     result = []
>     for item in data:
>         if item > threshold:
>             result.append(item * 2)
>     return result
Tool executing: CodeAnalyzer...
Code Analysis (quality):
- Readability: ✅ Good - clear logic
- Style: ✅ Follows conventions
- Performance: ✅ O(n) - efficient

> /exit
Goodbye!
```

---

**Pros:** Full conversation history, command-driven interface, memory across turns, integrated tools  
**Cons:** Requires interactive terminal, OllamaProvider needs Ollama running

---

## 3. advanced_interactive_agent.py - Production-Grade REPL

**Start REPL with Observability:**
```bash
python scripts/advanced_interactive_agent.py
```

A comprehensive interactive agent playground featuring production-grade monitoring and safety constraints. Demonstrates how to add observability, context management, and safety guardrails to AI agent applications.

### Observability Features

**Metrics Tracking:**
```bash
> /metrics
[Shows: Total tokens used, average latency, error count, tool calls]

Session Metrics:
  Requests:              5
  Total Tokens:          1,250
  Total Latency:         3,245.3ms
  Avg Latency/Request:   649.1ms
```

**Execution Tracing:**
```bash
> /trace
[Shows detailed trace of last execution with timestamps and status]

Last Execution Trace:
  Timestamp: 2026-01-10T14:32:45.123456
  Input Length: 42 chars
  Latency: 523.4ms
  Response Length: 287 chars
  Status: ✓ Success
```

### Context Management Features

**Adaptive Context Window:**
```bash
> /context 5
✓ Context window set to 5 messages

> /context_info
[Shows context saturation and recommendations]

SATURATION: 45% ✓ Healthy
  [██████░░░░░░░░░░░░░░░░░░░░░]

Context usage is healthy
```

**Features:**
- Configurable message window size (1-100 messages)
- Saturation monitoring with visual indicator
- Token estimation for context window
- Auto-recommendation to summarize when context gets full (>80%)

### Safety & Guardrails

**Safety Status:**
```bash
> /safety
[Shows all safety settings and current usage]

INPUT VALIDATION:
  Max Length: 2000 chars (Injection Detection: Enabled)

TOKEN BUDGETING:
  Budget:     4000 tokens
  Used:       1250
  Remaining:  2750
  Usage:      31.3%
```

**Safety Features:**
- Input validation: Length checking, prompt injection detection, encoding validation
- Tool rate limiting: Max 5 tool calls per minute
- Token budgeting: Session token limit with warnings at 80%
- Pre-execution safety checks with clear feedback

**Configure Safety Limits:**
```bash
> /limits SET max_input_length 1000
✓ Max input length set to 1000

> /limits SET tool_rate_limit 10
✓ Tool rate limit set to 10/minute

> /cost_budget 8000
✓ Token budget set to 8000
```

### Complete Command Reference

| Command | Example | Effect |
|---------|---------|--------|
| Chat | `> What is AI?` | Run agent with prompt |
| `/help` | `> /help` | Show help menu |
| `/config` | `> /config` | Display full configuration |
| `/metrics` | `> /metrics` | Show session statistics |
| `/trace` | `> /trace` | Show last execution trace |
| `/context SIZE` | `> /context 10` | Set context window |
| `/context_info` | `> /context_info` | Show context usage |
| `/safety` | `> /safety` | Display safety settings |
| `/limits SET K V` | `> /limits SET max_input_length 1500` | Configure limits |
| `/cost_budget N` | `> /cost_budget 5000` | Set token budget |
| `/provider TYPE` | `> /provider ollama` | Switch provider |
| `/model NAME` | `> /model mistral` | Set model |
| `/max_turns N` | `> /max_turns 5` | Set reasoning turns |
| `/history` | `> /history` | View conversation history |
| `/reset` | `> /reset` | Clear all history |
| `/exit` | `> /exit` | Quit |

### Example Session: Full Features

```bash
$ python scripts/advanced_interactive_agent.py

╔════════════════════════════════════════════════════════════════╗
║    Advanced Interactive Agent - Observability & Safety         ║
╚════════════════════════════════════════════════════════════════╝

> /config
[Shows: Provider=mock, Model=mistral:7b, Context=10msg, Safety=enabled]

> /context 15
✓ Context window set to 15 messages

> What is machine learning?
⏳ Agent thinking...
✓ Complete (324ms)

[Agent provides detailed response about ML]

> /metrics
Session Metrics:
  Requests:              1
  Total Tokens:          425
  Avg Latency:           324.1ms
  
Last Execution:
  Tokens: 425 | Latency: 324.0ms | Tools: 0 | Errors: 0

> /context_info
SATURATION: 13% ✓ Healthy
  [████░░░░░░░░░░░░░░░░░░░░░░░░]

Total Messages: 2
Active (in window): 2
Window Size: 15

> /safety
INPUT VALIDATION:
  Max Length: 2000 chars
  Injection Detection: Enabled
  
TOKEN BUDGETING:
  Budget: 4000 | Used: 425 | Remaining: 3575 | Usage: 10.6%

> /exit
Goodbye!
```

**Features:**
- Full observability into agent behavior
- Smart context management with saturation monitoring
- Comprehensive safety guardrails
- Token budgeting and cost tracking
- Rate limiting and injection detection

**Pros:**
- Production-grade monitoring and debugging
- Clear visibility into resource usage
- Safety constraints prevent runaway execution
- Excellent for understanding agent internals

**Cons:**
- More overhead than basic agent
- Requires understanding of all safety settings
- Better suited for advanced users/educational settings

---

## 4. explore.py - Predefined Scenarios with Dynamic Provider Control

**Basic Usage:**
```bash
python scripts/explore.py SCENARIO_NAME
```

**Available Scenarios:**
```bash
python scripts/explore.py quickstart     # Simple 2-3 question intro
python scripts/explore.py reasoning      # Logic puzzles and riddles
python scripts/explore.py storytelling   # Creative writing prompts
python scripts/explore.py teaching       # Topic explanations
python scripts/explore.py advanced       # Complex multi-turn reasoning
python scripts/explore.py openai         # OpenAI GPT-4 powered responses
```

**CLI Arguments for Provider/Model Override:**
```bash
# Switch provider
python scripts/explore.py reasoning --openai                    # Use OpenAI
python scripts/explore.py teaching --ollama                     # Use Ollama
python scripts/explore.py quickstart --mock                     # Use Mock (instant)

# Override model
python scripts/explore.py openai --model gpt-3.5-turbo
python scripts/explore.py reasoning --ollama --model phi

# List or help
python scripts/explore.py --list                                # List scenarios
python scripts/explore.py --help                                # Show help
```

**Features:** Structured learning paths, dynamic provider control, batch prompts  
**Pros:** No configuration needed, flexible provider switching, reproducible  
**Cons:** Limited to predefined scenarios (customize by editing script)

---

## Examples: Agent Multi-Stage Reasoning

These examples showcase agent thinking through multiple stages:

### 1. Logic Puzzle - Constraint-Based Reasoning
```bash
python scripts/quick_test.py "I'm thinking of a number between 1-100. It's even, divisible by 3, and less than 50. What could it be?"
```
**Agent Stages:** Parse constraints  Filter by even  Filter by divisible by 3  Filter by < 50  List candidates  Verify answers

### 2. Planning & Execution - Structured Study Plan
```bash
python scripts/interactive_agent.py
> /provider ollama
> I want to learn Python in 30 days. Create a structured study plan with daily goals and milestones.
> /max_turns 5
```
**Agent Stages:** Analyze requirements  Break into weeks  Design daily topics  Set milestones  Create deliverables

### 3. Technical Deep Dive - Mathematical Explanation
```bash
python scripts/quick_test.py "Explain how neural networks learn using backpropagation. Include the forward pass, loss calculation, and gradient descent." --turns 5
```
**Agent Stages:** Explain architecture  Show forward pass  Explain loss function  Describe gradient descent  Detail backpropagation  Provide example

### 4. Creative Task with Constraints - Poetry
```bash
python scripts/quick_test.py "Write a haiku about AI that must include these words: 'learning', 'wonder', 'code'. Verify it follows 5-7-5 syllable structure."
```
**Agent Stages:** Understand haiku structure  Identify word constraints  Generate lines  Count syllables  Verify word inclusion  Refine

### 5. Conversational Memory - Multi-Turn Story
```bash
python scripts/interactive_agent.py
> /provider ollama
> My favorite color is blue, favorite animal is penguin, and lucky number is 7.
> Tell me a creative story combining all three elements.
> Now recommend a perfect gift based on what you know about me.
> /history
```
**Agent Stages:** Extract preferences from first message  Remember context  Generate coherent story  Apply memory to recommendation  Show full history

### 6. Analytical Comparison - Multi-Factor Analysis
```bash
python scripts/quick_test.py "Create a detailed comparison matrix for remote work vs office work. Include: productivity, collaboration, cost, work-life balance, career growth, and flexibility. Use a 1-10 scoring system." --turns 5
```
**Agent Stages:** Identify all factors  Analyze each factor  Establish scoring criteria  Apply weights  Generate comparison matrix  Draw conclusions

### 7. Problem Diagnosis - Root Cause Analysis
```bash
python scripts/quick_test.py "My Python script is slow with 1M row CSV files. It: 1) loads entire CSV, 2) filters by date range, 3) groups by category, 4) sorts by value. Find bottlenecks and suggest optimizations with code." --turns 5
```
**Agent Stages:** Map data flow  Identify operations  Analyze complexity  Find bottlenecks  Propose optimizations  Rank by impact  Provide code

### 8. Code Review & Refactoring - Complex Code Analysis
```bash
python scripts/interactive_agent.py
> /provider ollama
> Review this code for issues:
> def process(data):
>     result = []
>     for i in range(len(data)):
>         for j in range(len(data)):
>             if data[i] == data[j] and i != j:
>                 result.append((i,j))
>     return result
> What's wrong and how to fix it?
> /max_turns 5
```
**Agent Stages:** Understand algorithm  Identify inefficiencies  Detect bugs  Propose fixes  Suggest improvements  Provide refactored code

### 9. Ethical Reasoning - Multi-Perspective Analysis
```bash
python scripts/quick_test.py "Should companies collect user data for AI training? Present arguments from: user privacy advocates, AI researchers, business leaders, and regulators. Then provide a balanced recommendation." --turns 5
```
**Agent Stages:** Identify stakeholders  Present each perspective  Analyze trade-offs  Weigh pros/cons  Draw balanced conclusion

### 10. Systems Design - Architecture Planning
```bash
python scripts/interactive_agent.py
> /provider ollama
> Design a recommendation system for an e-commerce platform handling 10M daily users. Consider: scalability, latency, accuracy, cost, maintenance.
> /max_turns 5
```
**Agent Stages:** Understand requirements  Identify constraints  Propose architecture  Analyze trade-offs  Optimize for each dimension  Provide implementation roadmap

---

## Setup & Configuration

### Using Ollama (Optional for Real LLM)

> **Recommended Model:** `mistral:7b` - Fast, high-quality reasoning, optimized for Labs 1+

1. **Install Ollama**: https://ollama.ai
2. **Start Ollama server**: 
   ```bash
   ollama serve
   ```
3. **Pull a model** (one-time, ~4GB each):
   ```bash
   ollama pull mistral      # Recommended (fast, high quality)
   ollama pull llama2       # Alternative (larger, slower)
   ```
4. **Use in scripts**:
   ```bash
   python scripts/interactive_agent.py
   > /provider ollama
   > /model mistral         # Use recommended model
   > Your prompt here
   ```

**Model Comparison:**

| Model | Speed | Quality | Size | Best For |
|-------|-------|---------|------|----------|
| MockProvider (default) | Instant | N/A | None | Rapid testing, CI/CD |
| **mistral:7b** | ⚡ Fast | ⭐⭐⭐⭐ | 4GB | **Lab 1+ (Recommended)** |
| llama2:7b | Moderate | ⭐⭐⭐ | 4GB | Learning, comparison |
| llama2:13b | Slow | ⭐⭐⭐⭐ | 7GB | Complex reasoning |

### Environment Variables

```bash
# Set Ollama server URL (if not localhost:11434)
$env:OLLAMA_BASE_URL="http://localhost:11434"
```

---

## Common Scenarios

| Scenario | Command | Purpose |
|----------|---------|---------|
| Quick test (instant) | `python scripts/quick_test.py "test prompt"` | Fast feedback with MockProvider |
| Real LLM testing | `python scripts/quick_test.py "prompt" --ollama` | Use actual LLM via Ollama |
| Interactive conversation | `python scripts/interactive_agent.py` | Full REPL with memory |
| With provider switching | `python scripts/interactive_agent.py` then `/provider ollama` | Switch between mock/ollama |
| Complex reasoning | `python scripts/quick_test.py "prompt" --turns 5` | More reasoning iterations |
| Structured learning | `python scripts/explore.py storytelling` | Predefined scenarios |

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: No module named agent_labs` | Run from workspace root: `cd d:\wsl_shared\src\ai_agents` |
| `OllamaProvider connection error` | Start Ollama: `ollama serve` in another terminal |
| `Model not found` | Pull model: `ollama pull llama2` |
| Script hangs with Ollama | Check Ollama is running: `ollama list` or `curl http://localhost:11434` |
| Slow response | MockProvider is instant; Ollama depends on model and hardware |

---

## Files in This Directory

- `quick_test.py` - Single-prompt testing script
- `interactive_agent.py` - Full REPL with commands and memory
- `explore.py` - Predefined learning scenarios
- `memory_test.py` - Memory/context injection verification
- `README.md` - This file

---

## Next Steps

1. Try `quick_test.py` with simple prompts first
2. Switch to `interactive_agent.py` for exploration
3. Experiment with multi-stage examples above
4. Use `/provider ollama` for real LLM responses
5. Check `/history` to see how agent uses memory
6. Explore the agent source in `src/agent_labs/`
