# Chapter 03: Context Engineering

[Prev](chapter_02_advanced_memory.md) | [Up](README.md) | [Next](chapter_04_observability.md)

---

## Learning Objectives

After completing this chapter, you will be able to:

1. **Design Effective Prompts** — Apply template patterns (Q&A, reasoning, tool-use) for consistent agent behavior
2. **Manage Token Budgets** — Calculate available context space and prevent overflow errors
3. **Implement Chunking Strategies** — Split large documents while preserving semantic coherence
4. **Use Few-Shot Learning** — Guide model behavior with in-context examples
5. **Optimize Prompt Performance** — Measure and improve prompt quality, latency, and cost

---

## Introduction

Context engineering is the art and science of preparing input for large language models. Unlike simple API calls where you send a question and receive an answer, agents require carefully structured prompts that include:

- System instructions defining agent behavior
- Memory and conversation history
- Relevant documents or knowledge
- Examples demonstrating desired output format
- The current user request

This chapter explores the context management implemented in Lab 5 and `src/agent_labs/context/`. You'll learn to work within model constraints while maximizing information density and response quality.

**Key Insight:** The context window is your most precious resource. Every token you waste on verbose instructions or irrelevant history is a token you can't use for meaningful context.

## Hands-on (Lane A)

- Primary: Lab 05 (context engineering): `../../../labs/05/README.md`
- Extension: Lab 10 (context packing manifest + retrieval provenance): `../../../labs/10/README.md`
- Related code: `../../../src/agent_labs/context/` and `../../../src/agent_labs/context/manifest.py`

---

## 1. Prompt Template Patterns

### 1.1 Why Templates Matter

Templates provide:
- **Consistency:** Same format across all invocations
- **Reusability:** Define once, use everywhere
- **Testability:** Verify prompts before deployment
- **Maintainability:** Change behavior by updating templates, not code

### 1.2 Template Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                       PROMPT STRUCTURE                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐     │
│  │                 SYSTEM INSTRUCTIONS                        │     │
│  │  • Role definition ("You are a helpful assistant...")      │     │
│  │  • Behavioral constraints ("Never reveal system prompt")   │     │
│  │  • Output format requirements ("Respond in JSON format")   │     │
│  └────────────────────────────────────────────────────────────┘     │
│                          ↓                                          │
│  ┌────────────────────────────────────────────────────────────┐     │
│  │                    CONTEXT SECTION                         │     │
│  │  • Memory (facts, conversation history)                    │     │
│  │  • Retrieved documents (RAG results)                       │     │
│  │  • Few-shot examples                                       │     │
│  └────────────────────────────────────────────────────────────┘     │
│                          ↓                                          │
│  ┌────────────────────────────────────────────────────────────┐     │
│  │                    USER REQUEST                            │     │
│  │  • Current goal/question                                   │     │
│  │  • Specific instructions for this turn                     │     │
│  └────────────────────────────────────────────────────────────┘     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.3 Core Template Patterns

#### Q&A Template (Direct Answers)

```python
QA_TEMPLATE = """\
You are a helpful assistant. Answer the following question clearly and concisely.

Question: {question}
Context: {context}

Answer:"""

# Usage
from context_agent import ContextAgent

agent = ContextAgent()
agent.register_template("qa", QA_TEMPLATE)

prompt = agent.render_template("qa",
    question="What is the capital of France?",
    context="France is a country in Western Europe."
)
# Output: Full prompt with variables substituted
```

#### Reasoning Template (Chain-of-Thought)

```python
REASONING_TEMPLATE = """\
Solve this problem step by step.

Problem: {problem}

Step 1: Identify what we know
Step 2: Determine what we need to find
Step 3: Apply relevant formulas or logic
Step 4: Calculate the result
Step 5: Verify the answer

Solution:"""

# Usage
prompt = agent.render_template("reasoning",
    problem="If a train travels 60 mph for 2.5 hours, how far does it go?"
)
```

#### Tool-Use Template (Action Selection)

```python
TOOL_USE_TEMPLATE = """\
You are an agent that can use tools to solve problems.

Available Tools:
{tools}

Task: {task}

Select the most appropriate tool and provide:
1. Tool Name: [which tool to use]
2. Reasoning: [why this tool is best]
3. Parameters: [required parameters]
4. Expected Outcome: [what the tool will return]

Response:"""

# Usage
tools_list = """
- calculator: Perform mathematical calculations
- weather: Get current weather for a location
- search: Search the web for information
"""

prompt = agent.render_template("tool_use",
    tools=tools_list,
    task="What is 15% of $234.50?"
)
```

### 1.4 Template Registration and Management

```python
class ContextAgent:
    def __init__(self, model: str = "gpt-3.5-turbo", max_tokens: int = 8000):
        self.model = model
        self.max_tokens = max_tokens
        self.templates = {}  # Template storage
    
    def register_template(self, name: str, template: str) -> None:
        """Register a prompt template for later use."""
        if name in self.templates:
            raise ValueError(f"Template '{name}' already registered")
        self.templates[name] = template
    
    def render_template(self, name: str, **kwargs) -> str:
        """Fill template with provided variables."""
        if name not in self.templates:
            raise ValueError(f"Template '{name}' not found")
        
        template = self.templates[name]
        
        try:
            return template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing required variable: {e}")
    
    def get_template_names(self) -> list[str]:
        """List all registered template names."""
        return list(self.templates.keys())
```

---

## 2. Token Management

### 2.1 Why Token Budgeting Matters

Every model has a maximum context window:

| Model | Context Window | Approximate Characters |
|-------|---------------|----------------------|
| GPT-3.5-turbo | 4,096 tokens | ~16,000 chars |
| GPT-4 | 8,192 tokens | ~32,000 chars |
| GPT-4-turbo | 128,000 tokens | ~512,000 chars |
| Claude 3 | 200,000 tokens | ~800,000 chars |

Exceeding the context window causes:
- API errors (request rejected)
- Truncated inputs (lost context)
- Degraded performance (model confusion)

### 2.2 Token Counting

```python
class ContextAgent:
    def __init__(self, model: str = "gpt-3.5-turbo", max_tokens: int = 8000):
        self.model = model
        self.max_tokens = max_tokens
        # Simple approximation: ~4 characters per token
        self._chars_per_token = 4
    
    def count_tokens(self, text: str) -> int:
        """Estimate token count in text."""
        if not text:
            return 0
        return max(1, len(text) // self._chars_per_token)
```

**Production Tip:** For production systems, use the `tiktoken` library for accurate counts:

```python
# Production token counting with tiktoken
import tiktoken

def count_tokens_accurate(text: str, model: str = "gpt-3.5-turbo") -> int:
    """Count tokens using tiktoken (production)."""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))
```

### 2.3 Token Budget Tracking

```python
from dataclasses import dataclass

@dataclass
class TokenBudget:
    """Tracks token usage across prompt components."""
    system_prompt: int
    context: int
    response: int
    
    @property
    def total(self) -> int:
        """Total tokens reserved."""
        return self.system_prompt + self.context + self.response
    
    def available_for_context(self, max_tokens: int) -> int:
        """Calculate available tokens for context after reservations."""
        # Reserve 500 tokens as safety buffer
        return max(0, max_tokens - self.system_prompt - self.response - 500)

# Usage
budget = TokenBudget(system_prompt=200, context=0, response=500)
available = budget.available_for_context(max_tokens=8000)
print(f"Available for context: {available} tokens")  # 7300 tokens
```

### 2.4 Budget Summary Method

```python
def get_budget_summary(
    self, 
    prompt_text: str,
    system_prompt_tokens: int = 200,
    response_tokens: int = 500
) -> dict:
    """Get detailed token budget breakdown."""
    prompt_tokens = self.count_tokens(prompt_text)
    total_reserved = system_prompt_tokens + prompt_tokens + response_tokens
    
    return {
        "prompt_tokens": prompt_tokens,
        "system_tokens": system_prompt_tokens,
        "response_tokens": response_tokens,
        "total_reserved": total_reserved,
        "max_tokens": self.max_tokens,
        "available": max(0, self.max_tokens - total_reserved),
        "fits": total_reserved <= self.max_tokens,
        "overflow": max(0, total_reserved - self.max_tokens),
    }

# Usage
large_doc = "..." * 10000  # Large document
summary = agent.get_budget_summary(large_doc)

if summary["fits"]:
    print("Document fits in context window")
else:
    print(f"Overflow by {summary['overflow']} tokens")
```

---

## 3. Overflow Prevention

### 3.1 Truncation Strategy

When content exceeds budget, truncate to fit:

```python
def truncate_to_fit(self, text: str, max_tokens: int) -> str:
    """Truncate text to fit within token budget."""
    tokens = self.count_tokens(text)
    
    if tokens <= max_tokens:
        return text
    
    # Calculate approximate character limit
    max_chars = max_tokens * self._chars_per_token
    
    # Find word boundary near limit
    truncated = text[:max_chars]
    last_space = truncated.rfind(' ')
    
    if last_space > max_chars * 0.8:  # Don't truncate too early
        truncated = truncated[:last_space]
    
    return truncated + "..."

# Usage
long_text = "Very long document..." * 1000
short_text = agent.truncate_to_fit(long_text, max_tokens=500)
```

### 3.2 Chunking Strategy

For large documents, split into processable chunks:

```python
def chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Split text into overlapping chunks."""
    tokens = self.count_tokens(text)
    
    if tokens <= chunk_size:
        return [text]
    
    chunks = []
    chars_per_chunk = chunk_size * self._chars_per_token
    chars_overlap = overlap * self._chars_per_token
    
    start = 0
    while start < len(text):
        end = start + chars_per_chunk
        
        # Find word boundary
        if end < len(text):
            space_pos = text.rfind(' ', start, end)
            if space_pos > start + chars_per_chunk * 0.5:
                end = space_pos
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        # Move start with overlap
        start = end - chars_overlap
    
    return chunks

# Usage
document = "..." * 10000
chunks = agent.chunk_text(document, chunk_size=1000, overlap=100)
print(f"Split into {len(chunks)} chunks")
```

### 3.3 Context Management Strategy Pattern

```python
def manage_context(
    self, 
    document: str, 
    max_tokens: int,
    strategy: str = "truncate"
) -> Union[str, list[str]]:
    """Auto-manage context overflow."""
    
    tokens = self.count_tokens(document)
    
    if tokens <= max_tokens:
        return document
    
    if strategy == "truncate":
        return self.truncate_to_fit(document, max_tokens)
    
    elif strategy == "chunk":
        return self.chunk_text(document, chunk_size=max_tokens)
    
    elif strategy == "summarize":
        # Placeholder for LLM-based summarization
        return self._summarize_to_fit(document, max_tokens)
    
    else:
        raise ValueError(f"Unknown strategy: {strategy}")
```

### 3.4 Render with Context Check

```python
def render_with_context_check(self, name: str, **kwargs) -> str:
    """Render template and verify it fits in context window."""
    
    prompt = self.render_template(name, **kwargs)
    summary = self.get_budget_summary(prompt)
    
    if not summary["fits"]:
        raise ValueError(
            f"Rendered prompt exceeds context window by {summary['overflow']} tokens. "
            f"Total: {summary['total_reserved']}, Max: {self.max_tokens}"
        )
    
    return prompt

# Usage
try:
    prompt = agent.render_with_context_check("qa",
        question="What is this about?",
        context=very_long_document
    )
except ValueError as e:
    print(f"Context overflow: {e}")
    # Handle by truncating context
    short_context = agent.truncate_to_fit(very_long_document, max_tokens=3000)
    prompt = agent.render_template("qa",
        question="What is this about?",
        context=short_context
    )
```

---

## 4. Few-Shot Learning

### 4.1 What is Few-Shot Learning?

Few-shot learning uses examples in the prompt to guide model behavior. Instead of fine-tuning, you show the model what you want via demonstration.

```
┌─────────────────────────────────────────────────────────────────────┐
│                      FEW-SHOT LEARNING                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   Zero-shot:   "Classify the sentiment of: 'Great product!'"        │
│                                                                     │
│   One-shot:    "Example: 'Amazing!' → POSITIVE                      │
│                 Classify: 'Great product!'"                         │
│                                                                     │
│   Few-shot:    "Examples:                                           │
│                 'Amazing!' → POSITIVE                               │
│                 'Terrible' → NEGATIVE                               │
│                 'It's okay' → NEUTRAL                               │
│                 Classify: 'Great product!'"                         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 4.2 Example Registration

```python
class ContextAgent:
    def __init__(self, ...):
        self.examples = {}  # Category -> list of examples
    
    def register_examples(self, category: str, examples: list[dict]) -> None:
        """Register few-shot learning examples for a task category."""
        self.examples[category] = examples
    
    def format_examples(self, category: str, format_str: str) -> str:
        """Format examples for prompt inclusion."""
        if category not in self.examples:
            raise ValueError(f"No examples registered for '{category}'")
        
        formatted = []
        for example in self.examples[category]:
            formatted.append(format_str.format(**example))
        
        return "\n".join(formatted)
    
    def get_example_categories(self) -> list[str]:
        """List all example categories."""
        return list(self.examples.keys())

# Usage
agent = ContextAgent()

# Register sentiment examples
agent.register_examples("sentiment", [
    {"text": "This is amazing!", "label": "POSITIVE"},
    {"text": "Terrible experience.", "label": "NEGATIVE"},
    {"text": "It arrived on time.", "label": "NEUTRAL"},
])

# Format for inclusion in prompt
examples_text = agent.format_examples("sentiment",
    "Text: \"{text}\" → Sentiment: {label}"
)

print(examples_text)
# Text: "This is amazing!" → Sentiment: POSITIVE
# Text: "Terrible experience." → Sentiment: NEGATIVE
# Text: "It arrived on time." → Sentiment: NEUTRAL
```

### 4.3 Few-Shot Template Pattern

```python
FEW_SHOT_TEMPLATE = """\
{task_description}

Examples:
{examples}

Now perform the same task:
{input}

Output:"""

# Usage
agent.register_template("few_shot", FEW_SHOT_TEMPLATE)

# Register task-specific examples
agent.register_examples("entity_extraction", [
    {"text": "John lives in New York", "entities": "PERSON: John, LOCATION: New York"},
    {"text": "Apple released iOS 17", "entities": "ORG: Apple, PRODUCT: iOS 17"},
])

# Build prompt
examples_text = agent.format_examples("entity_extraction",
    "Input: \"{text}\"\nEntities: {entities}"
)

prompt = agent.render_template("few_shot",
    task_description="Extract named entities from text.",
    examples=examples_text,
    input="Microsoft announced Windows 12 in Seattle."
)
```

### 4.4 When to Use Few-Shot

| Scenario | Zero-shot | One-shot | Few-shot (3-5) |
|----------|-----------|----------|----------------|
| Common task (summarize) | ✓ | - | - |
| Specific format needed | - | ✓ | ✓ |
| Domain-specific jargon | - | - | ✓ |
| Unusual classification | - | ✓ | ✓ |
| Complex reasoning | - | - | ✓ |

**Trade-off:** Each example consumes tokens. Balance example quality against context space.

---

## 5. Context Optimization

### 5.1 Prompt Compression Techniques

1. **Remove filler words:** "Please kindly" → ""
2. **Use abbreviations:** "approximately" → "~"
3. **Structured formats:** Prose → bullet points or tables
4. **Key facts only:** Remove redundant information

```python
# Verbose prompt (wasteful)
verbose_prompt = """
Please kindly analyze the following document and provide a comprehensive
summary that captures all the main points and key takeaways. Make sure
to include any important details that might be relevant to understanding
the document's purpose and conclusions.
"""

# Compressed prompt (efficient)
compressed_prompt = """
Summarize this document. Include:
- Main points
- Key takeaways
- Important details
"""

# Token savings: ~40 tokens → ~15 tokens
```

### 5.2 Dynamic Context Selection

Only include relevant context, not everything:

```python
def build_context(
    self,
    query: str,
    memory: MemoryAgent,
    max_context_tokens: int = 2000
) -> str:
    """Build context by selecting relevant memories."""
    
    # Retrieve memories relevant to query
    relevant_memories = memory.retrieve(query, include_trace=True)
    
    context_parts = []
    tokens_used = 0
    
    for item in relevant_memories:
        item_tokens = self.count_tokens(item.content)
        
        if tokens_used + item_tokens > max_context_tokens:
            break  # Stop before overflow
        
        context_parts.append(item.content)
        tokens_used += item_tokens
    
    return "\n".join(context_parts)
```

### 5.3 Priority-Based Context Packing

```python
def pack_context(
    self,
    items: list[dict],  # [{content, priority, tokens}]
    max_tokens: int
) -> str:
    """Pack highest-priority items into available space."""
    
    # Sort by priority (higher = more important)
    sorted_items = sorted(items, key=lambda x: x["priority"], reverse=True)
    
    packed = []
    tokens_used = 0
    
    for item in sorted_items:
        if tokens_used + item["tokens"] <= max_tokens:
            packed.append(item["content"])
            tokens_used += item["tokens"]
    
    return "\n---\n".join(packed)

# Usage
items = [
    {"content": "User lives in Seattle", "priority": 10, "tokens": 5},
    {"content": "Recent conversation...", "priority": 5, "tokens": 100},
    {"content": "User preferences...", "priority": 8, "tokens": 50},
]

context = agent.pack_context(items, max_tokens=60)
# Includes: location (10) + preferences (8), skips conversation
```

---

## 6. Template Library Reference

### 6.1 Available Templates

| Template | Purpose | Variables |
|----------|---------|-----------|
| `qa` | Direct Q&A | question, context |
| `reasoning` | Chain-of-thought | problem |
| `tool_use` | Action selection | tools, task |
| `sentiment_analysis` | Classification | text |
| `code_review` | Code analysis | code |
| `summarization` | Document condensing | document, max_length |
| `classification` | Multi-class | text, categories |
| `entity_extraction` | NER | text, entity_types |
| `comparison` | Item comparison | items, dimensions |
| `role_play` | Character interaction | user_message, role, context |
| `analysis` | Detailed examination | subject |
| `planning` | Action planning | goal, constraints, timeline |

### 6.2 Sentiment Analysis Template

```python
SENTIMENT_ANALYSIS_TEMPLATE = """\
Classify the sentiment of the text as POSITIVE, NEGATIVE, or NEUTRAL.

Examples:
Text: "This product is amazing! Best purchase ever."
Sentiment: POSITIVE

Text: "Terrible experience. Would not recommend."
Sentiment: NEGATIVE

Text: "The item arrived on time."
Sentiment: NEUTRAL

Now classify:
Text: "{text}"
Sentiment:"""
```

### 6.3 Code Review Template

```python
CODE_REVIEW_TEMPLATE = """\
Role: You are a Python expert code reviewer.

Task: Review the following code for bugs and style issues.

Guidelines:
1. Identify critical bugs that could cause failures
2. Flag style issues that violate PEP 8
3. Suggest performance improvements
4. Check for security vulnerabilities

Format your response as:
1. Bugs: [list critical issues, or "None found"]
2. Style: [list style improvements, or "Meets PEP 8"]
3. Performance: [optimization opportunities, or "Good"]
4. Security: [security concerns, or "No issues found"]
5. Rating: [1-5 scale]

Code:
{code}

Review:"""
```

---

## 7. Best Practices

### 7.1 Template Design Principles

1. **Be explicit about format:** Specify exactly how you want the output structured
2. **Use delimiters:** Clearly separate sections with `---`, `###`, or XML tags
3. **Include examples:** When format matters, show don't tell
4. **Test with edge cases:** Empty inputs, very long inputs, special characters

### 7.2 Token Budget Rules

1. **Reserve response space:** Always leave at least 500-1000 tokens for response
2. **Buffer for variance:** Add 10% safety margin to estimates
3. **Monitor in production:** Track actual vs. estimated token usage
4. **Fail gracefully:** If budget exceeded, truncate or summarize, don't crash

### 7.3 Context Quality Checklist

- [ ] Most relevant information appears first
- [ ] No redundant or duplicate content
- [ ] Format is consistent throughout
- [ ] Examples are representative and diverse
- [ ] Instructions are clear and unambiguous
- [ ] Total tokens within budget

---

## 3.4 Token Budgets: Make Them Explicit

Token budgets are not optional in production. They are the only reliable way to control cost and latency.

Define two limits:

- **Hard limit**: never exceed this, even if you must drop context.
- **Soft limit**: a warning threshold where you start compressing or summarizing.

Practical approach:

1. Estimate tokens for the prompt and history.
2. Reserve a fixed budget for the model response.
3. If you exceed soft limit, summarize or truncate the lowest-priority context.

This turns "LLM length surprises" into predictable behavior.

---

## 3.5 Overflow Strategies (What to Drop First)

When the context window is full, you must decide what to keep. Common strategies:

- **Prioritized trimming**: drop low-priority items first (older chat, low-confidence memory).
- **Summarization**: compress old turns into a short summary.
- **Retrieval-on-demand**: store documents externally and retrieve only when needed.

The key is determinism: the agent should make the same decision every time given the same inputs.

---

### 3.5.1 Context Packing Policy + Evidence Manifest

In production, you want a *repeatable* answer to: "What did we put into the prompt, and why?"

Start with a deterministic packing order (example):

1. System instructions
2. Current user request (goal + constraints)
3. Tool contracts (names + schemas for tools available this run)
4. Retrieved evidence (RAG results), **with provenance**
5. Long-term memory (facts), **with confidence + provenance**
6. Conversation history (recent turns)
7. Summaries (only if needed to fit budget)

Then produce a lightweight **evidence manifest** alongside the prompt. This is not sent to the user by default, but it is logged for debugging and evaluation.

Example manifest shape:

```json
{
  "request_id": "req-123",
  "budget": {"max_tokens": 8000, "reserved_response_tokens": 1000},
  "items": [
    {"kind": "tool_schema", "name": "ticket_read", "tokens": 120, "reason": "tool available"},
    {"kind": "evidence", "doc_id": "runbook-7", "chunk_id": "c12", "tokens": 260, "reason": "retrieval_top_k"},
    {"kind": "memory_fact", "key": "user_pref", "tokens": 40, "reason": "high_confidence"}
  ]
}
```

This makes it easier to:

- debug wrong answers ("what evidence did we include?")
- evaluate changes ("did new chunking change evidence coverage?")
- audit sensitive decisions ("did we include the right documents for this tenant?")

## Implementation Guide (using core modules)

Use these repo assets to make the chapter actionable:

- Templates: `src/agent_labs/context/templates.py`
- Token counting: `src/agent_labs/context/tokens.py`
- Chunking: `src/agent_labs/context/chunking.py`
- Context windows: `src/agent_labs/context/window.py`
- Lab: `labs/05/README.md`
- Runnable snippet: `curriculum/presentable/02_intermediate/snippets/ch03_prompt_template_token_count.py`

Suggested sequence:

1. Build a template with variables and validate it (see `PromptTemplate`).
2. Use token estimation to create a budgeted prompt.
3. Run Lab 05 and experiment with chunk sizes + overlaps.

**Deliverable:** a context packing plan with explicit budgets and overflow rules.

---

## Common Pitfalls and How to Avoid Them

1. **Unbounded context growth:** Always enforce a budget, even in demos.
2. **Over-summarizing:** Summaries can erase critical details; keep citations or IDs.
3. **No template validation:** If variables are missing, the prompt will break silently.
4. **Assuming chunking is free:** Chunking too small increases retrieval noise.

---

## 3.6 Prompt Contracts (Treat Prompts Like APIs)

Prompts should be treated as interfaces, not free-form text. When a prompt becomes a contract, it is easier to test and maintain.

A basic contract has:

- **Inputs**: defined variables and types (e.g., `user_question: str`, `context_items: List[str]`).
- **Outputs**: required structure (e.g., JSON with `answer`, `citations`, `confidence`).
- **Failure modes**: what the model should do when input is missing or uncertain.

When you version prompts, you reduce accidental regressions. When you add output schemas, you can validate responses and fail fast.

**Practical tip:** Store prompt versions with clear names (e.g., `rag_answer_v2`) and log the version in every response. This makes A/B testing and incident debugging much easier.

---

## Summary

### Key Takeaways

1. **Templates ensure consistency** across all agent interactions. Register once, use everywhere.

2. **Token budgeting prevents overflow** errors. Always reserve space for system prompt and response.

3. **Chunking and truncation** handle large documents. Choose strategy based on use case.

4. **Few-shot learning guides behavior** without fine-tuning. Quality examples > quantity.

5. **Context optimization maximizes value** from limited token budget. Prioritize relevance over completeness.

### What's Next

In Chapter 04, you'll learn about **Observability & Monitoring**—how to trace agent execution, collect metrics, and debug production issues.

---

## References

- **Lab 5:** [labs/05/README.md](../../../labs/05/README.md) — Context Engineering hands-on exercises
- **Source Code:** [labs/05/src/context_agent.py](../../../labs/05/src/context_agent.py)
- **Templates:** [labs/05/src/prompt_templates.py](../../../labs/05/src/prompt_templates.py)
- **OpenAI Tokenizer:** [platform.openai.com/tokenizer](https://platform.openai.com/tokenizer)
- **Tiktoken:** [github.com/openai/tiktoken](https://github.com/openai/tiktoken)

---

## Exercises

Complete these exercises in the workbook to reinforce your learning:

1. **Template Design:** Create a custom template for a domain-specific task (e.g., legal document analysis, medical diagnosis assistance).

2. **Token Budget Calculator:** Build a utility that calculates exact token counts using tiktoken and compares against the simple estimation method.

3. **Chunking Comparison:** Implement and compare different chunking strategies (fixed-size, sentence-aware, paragraph-aware) on a sample document.

4. **Few-Shot Optimization:** Measure classification accuracy with 0, 1, 3, and 5 examples. Find the optimal number for your use case.

5. **Context Prioritization:** Implement a priority-based context packer that dynamically selects the most relevant information from multiple sources.

---

[Prev](chapter_02_advanced_memory.md) | [Up](README.md) | [Next](chapter_04_observability.md)
