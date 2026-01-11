# Lab 5: Context Engineering

## Overview

Learn sophisticated prompt and context management techniques that enable agents to handle complex tasks with large documents. Understand how to design effective prompts, manage token budgets, and prevent context overflow.

**Time Required**: 6-8 hours  
**Difficulty**: Intermediate  
**Prerequisites**: Labs 1-4 (agent basics, tools, orchestration)

## Learning Outcomes

After completing this lab, you will be able to:

1. **Design Effective Prompts**: Write clear, structured prompts that elicit desired agent behavior
2. **Use Template Patterns**: Apply Q&A, reasoning, and tool-use templates appropriately
3. **Manage Context Windows**: Calculate token usage and prevent context overflow
4. **Implement Few-Shot Learning**: Use in-context examples to guide agent behavior
5. **Optimize Prompt Performance**: Measure how prompt variations affect output quality and latency

## Lab Structure

### Module 1: Prompt Templates (1-2 hours)

Learn how templates provide structure and consistency:

**Key Concepts**:
- **Q&A Templates**: Direct question answering with context
- **Reasoning Templates**: Chain-of-thought problem solving
- **Tool-Use Templates**: Structured task selection
- **Few-Shot Templates**: In-context learning examples
- **Classification Templates**: Category prediction
- **Analysis Templates**: Document examination

**Core API**:

```python
from src.context_agent import ContextAgent
from src.prompt_templates import get_template, list_templates

# Initialize agent
agent = ContextAgent(model="gpt-3.5-turbo", max_tokens=8000)

# Register template
agent.register_template("qa", get_template("qa"))

# Render with variables
prompt = agent.render_template("qa", 
    question="What is AI?",
    context="Artificial intelligence enables machine learning..."
)

# List available templates
templates = list_templates()
```

### Module 2: Token Management (2-3 hours)

Prevent context overflow with smart token budgeting:

**Key Concepts**:
- **Token Counting**: Estimate text size in tokens
- **Token Budget**: Reserve tokens for system prompt, context, and response
- **Overflow Prevention**: Detect when prompt exceeds limits
- **Truncation**: Cut text to fit limit
- **Chunking**: Split document into smaller pieces

**Core API**:

```python
from src.context_agent import ContextAgent

agent = ContextAgent(max_tokens=8000)

# Count tokens
tokens = agent.count_tokens("This is a test.")

# Check budget
summary = agent.get_budget_summary(
    prompt_text,
    system_prompt_tokens=200,
    response_tokens=500
)

# Prevent overflow
prompt = agent.render_with_context_check("template_name", **kwargs)

# Manage large documents
managed = agent.manage_context(
    document,
    max_tokens=4000,
    strategy="truncate"  # or "chunk"
)
```

### Module 3: Few-Shot Learning (1-2 hours)

Guide agent behavior with in-context examples:

**Key Concepts**:
- **Example Registration**: Store examples by category
- **Example Formatting**: Prepare examples for prompt inclusion
- **Few-Shot Templates**: Use examples to improve accuracy
- **Example Impact**: Measure quality improvement from examples

**Core API**:

```python
from src.context_agent import ContextAgent

agent = ContextAgent()

# Register examples
examples = [
    {"text": "Great!", "label": "POSITIVE"},
    {"text": "Bad", "label": "NEGATIVE"},
]
agent.register_examples("sentiment", examples)

# Format for prompt inclusion
formatted = agent.format_examples("sentiment",
    'Text: {text}, Sentiment: {label}'
)

# Get categories
categories = agent.get_example_categories()
```

## Quick Start

### 1. Explore Templates

```python
from src.context_agent import ContextAgent
from src.prompt_templates import list_templates, get_template

# See all templates
templates = list_templates()
for name, description in templates.items():
    print(f"{name}: {description}")

# Use a template
agent = ContextAgent()
agent.register_template("qa", get_template("qa"))

prompt = agent.render_template("qa",
    question="What is prompt engineering?",
    context="The art of crafting effective instructions for AI systems."
)
print(prompt)
```

### 2. Manage Token Budget

```python
agent = ContextAgent(max_tokens=8000)

# Check if your prompt fits
large_doc = "Your document here..."
summary = agent.get_budget_summary(large_doc)
print(f"Fits: {summary['fits']}")
print(f"Available: {summary['available']} tokens")

# If overflow, manage with truncation or chunking
if not summary['fits']:
    truncated = agent.truncate_to_fit(large_doc, max_tokens=4000)
    # or
    chunks = agent.chunk_text(large_doc, chunk_size=500)
```

### 3. Use Few-Shot Examples

```python
agent = ContextAgent()

# Register examples
agent.register_examples("sentiment", [
    {"text": "Great!", "label": "POSITIVE"},
    {"text": "Bad", "label": "NEGATIVE"},
    {"text": "OK", "label": "NEUTRAL"}
])

# Include in prompt
examples_text = agent.format_examples("sentiment",
    "Text: {text}, Sentiment: {label}"
)

# Build prompt with examples
prompt = f"""
Classify sentiment as POSITIVE, NEGATIVE, or NEUTRAL.

Examples:
{examples_text}

Now classify: "This is awesome!"
"""
```

## Key Components

### ContextAgent

Main class for context and template management.

**Methods**:

| Method | Purpose | Example |
|--------|---------|---------|
| `register_template(name, template)` | Store template for reuse | `agent.register_template("qa", template)` |
| `render_template(name, **kwargs)` | Fill template with variables | `agent.render_template("qa", question="...", context="...")` |
| `count_tokens(text)` | Estimate token count | `tokens = agent.count_tokens(doc)` |
| `truncate_to_fit(text, max_tokens)` | Cut text to fit limit | `short = agent.truncate_to_fit(doc, 4000)` |
| `chunk_text(text, chunk_size)` | Split into chunks | `chunks = agent.chunk_text(doc, 400)` |
| `render_with_context_check(name, **kwargs)` | Render and verify budget | `prompt = agent.render_with_context_check("qa", ...)` |
| `manage_context(doc, max_tokens, strategy)` | Auto-manage overflow | `managed = agent.manage_context(doc, strategy="chunk")` |
| `get_budget_summary(text, ...)` | Get token budget breakdown | `summary = agent.get_budget_summary(text)` |
| `get_template_names()` | List registered templates | `names = agent.get_template_names()` |
| `register_examples(category, examples)` | Store few-shot examples | `agent.register_examples("sentiment", [...])` |
| `format_examples(category, format_str)` | Format examples for prompt | `text = agent.format_examples("sentiment", ...)` |

### PromptTemplates

Library of pre-built templates for common tasks.

**Available Templates**:

| Template | Use Case | Example Input |
|----------|----------|---------------|
| `qa` | Question answering with context | question, context |
| `reasoning` | Step-by-step problem solving | problem |
| `tool_use` | Select and use tools | task, tools |
| `sentiment_analysis` | Classify text sentiment | text |
| `code_review` | Analyze code quality | code |
| `summarization` | Condense documents | document, max_length |
| `classification` | Multi-class categorization | text, categories |
| `entity_extraction` | Extract named entities | text, entity_types |
| `comparison` | Compare items | items, dimensions |
| `role_play` | Character interaction | user_message, role, context |
| `analysis` | Detailed examination | subject |
| `planning` | Create action plans | goal, constraints, timeline |

## Best Practices

### 1. Prompt Design

**✅ GOOD**: Clear, specific, structured
```python
good_prompt = """\
Role: You are a Python expert code reviewer.

Task: Review the following code for bugs and style issues.

Format your response as:
1. Bugs: [list critical issues]
2. Style: [list style improvements]
3. Rating: [1-5 scale]

Code:
{code}

Review:"""
```

**❌ BAD**: Vague, unstructured
```python
bad_prompt = "Review this code: {code}"
```

**Impact**: Good → Structured output; Bad → Unpredictable format

### 2. Token Budget Management

```python
# Always calculate budget
agent = ContextAgent(max_tokens=8000)

budget = agent.get_budget_summary(
    prompt,
    system_prompt_tokens=200,  # Instructions
    response_tokens=500         # Space for answer
)

# Ensure fit BEFORE making API call
if not budget['fits']:
    # Truncate or chunk
    prompt = agent.truncate_to_fit(prompt, budget['available'])
```

### 3. Few-Shot Learning

```python
# Use examples to guide behavior
agent.register_examples("sentiment", [
    {"text": "Love it!", "label": "POSITIVE"},      # Clear positive
    {"text": "Hate it", "label": "NEGATIVE"},       # Clear negative
    {"text": "It works", "label": "NEUTRAL"}        # Clear neutral
])

# Include in prompt
examples = agent.format_examples("sentiment", 
    "Text: {text}, Label: {label}")
```

### 4. Strategy Selection

| Situation | Strategy | Reason |
|-----------|----------|--------|
| Real-time chat | Truncate | Speed critical |
| Document analysis | Chunk | Quality critical |
| Log processing | Truncate | Info at start |
| Research paper | Chunk | Preserve all |
| User message | Truncate | Single response |

## Testing Your Code

Run the test suite:

```bash
# All tests
pytest tests/test_context_agent.py -v

# Specific categories
pytest tests/test_context_agent.py::TestTemplateRegistration -v
pytest tests/test_context_agent.py::TestTokenCounting -v
pytest tests/test_context_agent.py::TestContextOverflowPrevention -v

# Integration tests
pytest tests/test_context_agent.py::TestIntegration -v
```

## Project Files

```
labs/05/
├── src/
│   ├── context_agent.py          # Core ContextAgent class
│   └── prompt_templates.py        # Template library
├── tests/
│   └── test_context_agent.py      # Test suite (55+ tests)
├── exercises/
│   ├── exercise_1.md              # Template rendering basics
│   ├── exercise_2.md              # Custom template design
│   └── exercise_3.md              # Context management
├── data/
│   └── examples.json              # Few-shot examples
└── README.md                       # This file
```

## Exercises

### Exercise 1: Template Rendering (1-2 hours)

Learn how templates work and why they matter.

- Register and render 3 different templates
- Test each with multiple inputs
- Compare template quality and effectiveness
- Document patterns of good templates

**Skills**: Template usage, variable substitution, comparing approaches

### Exercise 2: Custom Template Design (2-3 hours)

Design a template for your own use case.

- Create custom code review template
- Test on 5 diverse code samples
- Validate output quality and structure
- Compare with built-in template

**Skills**: Prompt engineering, template design, validation, comparison

### Exercise 3: Context Management (2-3 hours)

Handle large documents with context overflow prevention.

- Implement token counting for different document sizes
- Compare truncation vs chunking strategies
- Develop decision guidelines for strategy selection
- Analyze quality trade-offs

**Skills**: Token budgeting, truncation/chunking, strategy selection, analysis

## Challenge Projects

### 1. Template Library Builder

Create a comprehensive template library for your domain:
- Design 5-10 templates for your use case
- Document each with examples
- Measure effectiveness on test cases
- Build template version control

### 2. Context-Aware Document Analyzer

Build a system that:
- Analyzes documents using multiple strategies
- Compares truncation vs chunking quality
- Automatically selects best strategy
- Measures and reports quality metrics

### 3. Few-Shot Example Optimizer

Create a system that:
- Evaluates different example sets
- Measures impact on output quality
- Automatically selects best examples
- Adapts examples based on feedback

## Advanced Topics

### 1. Adaptive Token Budgeting

Automatically adjust budget based on:
- Document importance
- Available context window
- Quality requirements
- Latency constraints

### 2. Hierarchical Chunking

Chunk documents while preserving context:
- Maintain chunk boundaries at meaningful points
- Use overlapping windows to preserve continuity
- Rank chunks by importance
- Process in priority order

### 3. Template Optimization

Measure and improve template effectiveness:
- A/B test template variations
- Analyze output quality metrics
- Track latency for each template
- Build optimization pipeline

### 4. Multi-Model Strategy

Adapt to different model capabilities:
- Adjust budget for 4K vs 128K models
- Use different strategies per model
- Optimize for cost vs quality
- Handle model fallback scenarios

## Common Patterns

### Pattern 1: Q&A with Large Context

```python
# Problem: Long document + question

# Solution:
doc_tokens = agent.count_tokens(document)
if doc_tokens > 4000:
    doc = agent.truncate_to_fit(document, 3500)

prompt = agent.render_template("qa",
    question="...",
    context=doc
)
```

### Pattern 2: Multi-Document Analysis

```python
# Problem: Multiple documents, each might be large

# Solution: Chunk and process separately
documents = [doc1, doc2, doc3]
for doc in documents:
    chunks = agent.chunk_text(doc, chunk_size=400)
    for chunk in chunks:
        # Process each chunk
        prompt = agent.render_template("qa", context=chunk)
```

### Pattern 3: Guided Few-Shot Classification

```python
# Problem: Classify consistently with examples

# Solution: Use few-shot learning
agent.register_examples("sentiment", positive_examples)
examples_text = agent.format_examples("sentiment")

prompt = f"""
{examples_text}

Now classify: "{user_text}"
"""
```

## Key Metrics

### Token Efficiency

```
Efficiency = Useful Tokens / Total Tokens
Good: > 80%
Acceptable: 50-80%
Poor: < 50%
```

### Quality Preservation

```
Quality Retention = (Output Quality after management) / (Original Quality)
Truncation: 60-80%
Chunking: 85-95%
Summarization: 75-90%
```

### Cost-Quality Trade-off

```
Cost per token = Model cost per 1K tokens
Quality = User satisfaction or metric score
Choose strategy that maximizes: Quality / Cost
```

## Troubleshooting

### Problem: "Token limit exceeded"

**Cause**: Prompt too large for context window

**Solutions**:
1. Truncate: Remove less important text
2. Chunk: Split into smaller pieces
3. Summarize: Compress while preserving meaning
4. Select: Use only most relevant sections

### Problem: "Missing variable in template"

**Cause**: Forgot to provide required template variable

**Solution**:
```python
# Check template requirements
template = agent.templates["my_template"]
# Render with all required variables
prompt = agent.render_template("my_template", 
    var1="value",
    var2="value"
)
```

### Problem: "Output not well-structured"

**Cause**: Template too vague or missing format specification

**Solution**:
- Add explicit output format section
- Include examples of desired format
- Use clear separators and headers
- Specify constraints (length, style, tone)

### Problem: "Few-shot examples not helping"

**Cause**: Examples not representative or correctly formatted

**Solution**:
- Choose diverse, representative examples
- Ensure examples match actual use cases
- Verify format matches what agent should produce
- Test with 3-5 examples first

## Resources

### Documentation
- [OpenAI Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering)
- [Claude Prompt Engineering](https://docs.anthropic.com/en/docs/build-a-chatbot)
- [Token Counting with Tiktoken](https://github.com/openai/tiktoken)

### Libraries
- `tiktoken`: Token counting for OpenAI models
- `langchain`: Template and prompt management
- `guidance`: Structured prompt engineering

### Papers & Articles
- "Prompt Engineering for Developers" (DeepLearning.AI)
- "Language Models as Few-Shot Learner" (Brown et al., 2020)
- "Chain-of-Thought Prompting" (Wei et al., 2022)

## Next Steps

1. **Complete Exercises 1-3** to master core concepts
2. **Build Challenge Projects** to apply learning
3. **Explore Advanced Topics** for production use
4. **Integrate with Real LLMs** (GPT, Claude, etc.)

## Frequently Asked Questions

**Q: How do I choose between truncation and chunking?**  
A: Truncate for speed/simplicity (real-time); chunk for quality/completeness (batch/analysis)

**Q: Can I use actual token counting (tiktoken)?**  
A: Yes! Replace `count_tokens()` implementation with tiktoken for production

**Q: How many few-shot examples do I need?**  
A: Start with 3-5, measure quality, add more if needed (diminishing returns ~10-15)

**Q: What's the best strategy for very large documents (100K+ tokens)?**  
A: Use ranking/importance scoring to select key sections, then chunk those

**Q: How do I measure template effectiveness?**  
A: A/B test variations, track quality metrics, measure latency, analyze output consistency

## Contributing

Have improvements? Found a bug? 

- Open an issue on GitHub
- Submit a pull request
- Share your template library
- Report test failures

## License

This lab is part of the AI Agents course. See LICENSE for details.

---

**Ready to master prompt engineering?** Start with [Exercise 1](exercises/exercise_1.md)!
