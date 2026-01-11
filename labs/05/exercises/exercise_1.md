# Exercise 1: Template Rendering and Basic Usage

## Objective
Understand how prompt templates work, how to render them with variables, and observe how template choice affects agent output quality.

## Background
Prompt templates are like function prototypes for agent behavior. They define the structure, tone, and expectations for agent responses. Different templates work better for different tasks:

- **Q&A Template**: Best for direct questions with context
- **Reasoning Template**: Best for problems requiring step-by-step logic
- **Tool-Use Template**: Best for structured task selection
- **Sentiment Analysis**: Best for classification with examples

## Tasks

### Task 1.1: Register and Render Templates

Create a Python script `exercise_1_solution.py`:

```python
from context_agent import ContextAgent
from prompt_templates import get_template

# Initialize agent
agent = ContextAgent()

# Register three templates from the library
agent.register_template("qa", get_template("qa"))
agent.register_template("reasoning", get_template("reasoning"))
agent.register_template("sentiment", get_template("sentiment_analysis"))

# Test Q&A template
print("=== Q&A Template ===")
qa_prompt = agent.render_template(
    "qa",
    question="What is machine learning?",
    context="ML enables systems to learn from data without explicit programming."
)
print(qa_prompt)

# Test Reasoning template
print("\n=== Reasoning Template ===")
reasoning_prompt = agent.render_template(
    "reasoning",
    problem="A train travels 120 miles in 2 hours. What's its speed?"
)
print(reasoning_prompt)

# Test Sentiment template
print("\n=== Sentiment Template ===")
sentiment_prompt = agent.render_template(
    "sentiment",
    text="This product exceeded my expectations!"
)
print(sentiment_prompt)
```

**Expected Output**:
- Three rendered prompts displayed
- Each with variables properly substituted
- No errors during rendering

**Deliverable**: `exercise_1_solution.py` with all three renders

---

### Task 1.2: Compare Template Quality

Create `exercise_1_comparison.md` that analyzes the three templates:

For each template, document:

1. **Structure**: What parts does it have? (intro, examples, task, format)
2. **Specificity**: How clear are the instructions?
3. **Best For**: What task type works best?
4. **Quality Score**: Rate 1-5 (1=vague, 5=crystal clear)

**Example**:
```markdown
## Q&A Template
- Structure: Question + Context + Answer
- Specificity: Very clear (4/5)
- Best For: Direct questions with background info
- Quality: 4/5 - Clear but lacks reasoning steps
```

**Deliverable**: Comparison table with all three templates analyzed

---

### Task 1.3: Test Template Flexibility

Modify `exercise_1_solution.py` to test each template with 3 different inputs:

**Q&A Template**:
1. "What is Python?" with context about programming languages
2. "How do photosynthesis work?" with biology context
3. "Why is climate change happening?" with environmental context

**Reasoning Template**:
1. Speed problem (already shown)
2. Budget problem: "You have $500. Item A costs $150, Item B costs $180. Can you buy both?"
3. Logic problem: "Alice is older than Bob. Charlie is older than Alice. Who is oldest?"

**Sentiment Template**:
1. Positive text: "This is amazing!"
2. Negative text: "Terrible service"
3. Neutral text: "The package arrived today"

Track:
- Whether each renders without error
- Whether instructions are clear for each task
- Which template produces best results for which task type

**Deliverable**: Results logged in `exercise_1_testing_log.txt`

---

### Task 1.4: Identify Template Patterns

Write `exercise_1_patterns.md` with observations:

1. **What do all good templates have in common?**
   - Look at structure (role, task, format, constraints)
   - Identify common elements

2. **How does template specificity affect output?**
   - Compare vague vs specific instructions
   - Example: "Answer the question" vs "Answer step-by-step with examples"

3. **Which template would you choose for:**
   - Customer support chatbot? Why?
   - Code review assistant? Why?
   - Document summarization? Why?
   - Problem-solving tutor? Why?

**Deliverable**: Markdown file with analysis (3-5 sentences per question)

---

## Success Criteria

- [ ] All three templates render without errors
- [ ] At least 3 different inputs tested per template
- [ ] Comparison table created with quality scores
- [ ] Pattern observations documented
- [ ] Script runs without exceptions

## Testing Your Solution

Run the tests:
```bash
pytest tests/test_context_agent.py::TestPromptTemplates -v
pytest tests/test_context_agent.py::TestTemplateRegistration -v
```

## Key Learning Points

1. Templates provide structure, consistency, and predictability
2. Different templates suit different tasks
3. Specificity in instructions improves output quality
4. Good templates include: role definition, clear task, format specification, constraints

## Next Steps

- Exercise 2: Design a custom template for a new task
- Exercise 3: Manage context for large documents
