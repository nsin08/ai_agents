# Exercise 2: Custom Template Design

## Objective
Design, implement, and validate a custom prompt template for a specific use case. Learn how prompt engineering choices directly impact agent behavior.

## Background
While pre-built templates are helpful, real-world applications often need custom templates tailored to specific requirements. A good custom template includes:

1. **Role Definition**: "You are a..."
2. **Task Description**: What to do and why
3. **Input Specification**: What inputs you'll receive
4. **Output Format**: How to structure the response
5. **Constraints**: Rules to follow (length, style, tone)
6. **Examples** (optional): Few-shot learning samples

## Project: Code Review Assistant

You will build a custom template for a Code Review Assistant that:
- Analyzes Python code for bugs and style issues
- Provides structured feedback
- Suggests improvements
- Rates code quality

### Template Components

**Role**: Python expert code reviewer

**Task**: Review code for:
- Critical bugs (failures, crashes, logic errors)
- Style issues (PEP 8 violations)
- Performance problems
- Security vulnerabilities

**Output Format**:
```
1. Bugs: [list or "None found"]
2. Style: [list or "Follows PEP 8" or improvements]
3. Performance: [optimization opportunities or "Good"]
4. Security: [concerns or "No issues found"]
5. Rating: [1-5 scale]
```

**Constraints**:
- Be specific (not "bad code" but "function exceeds 50 lines")
- Focus on important issues
- Suggest concrete fixes

---

## Tasks

### Task 2.1: Create Custom Template

Create `exercise_2_custom_template.py`:

```python
from context_agent import ContextAgent
from prompt_templates import PromptTemplates

# Create custom template
code_review_template = """\
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

# Register template
agent = ContextAgent()
agent.register_template("code_review", code_review_template)

print("Template registered successfully!")
print(f"Available templates: {agent.get_template_names()}")
```

**Deliverable**: Script that registers custom template

---

### Task 2.2: Test on Sample Code

Create `exercise_2_test_samples.py` with 5 code samples:

**Sample 1: Good code** (should get high rating)
```python
def calculate_average(numbers):
    """Calculate average of numbers."""
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)
```

**Sample 2: Style issues** (PEP 8 violations)
```python
def calculate_average(numbers):
    if len(numbers)==0:
        return 0
    total=sum(numbers)
    length=len(numbers)
    result=total/length
    return result
```

**Sample 3: Performance issue** (inefficient algorithm)
```python
def contains_duplicate(numbers):
    for i in range(len(numbers)):
        for j in range(len(numbers)):
            if i != j and numbers[i] == numbers[j]:
                return True
    return False
```

**Sample 4: Security issue** (SQL injection vulnerability)
```python
def get_user(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return db.execute(query)
```

**Sample 5: Bug** (logic error)
```python
def is_valid_password(password):
    if len(password) < 8:
        return True  # BUG: Should be False
    return False
```

Test your template on each sample:

```python
agent = ContextAgent()
agent.register_template("code_review", code_review_template)

samples = [
    ("good", good_code_sample),
    ("style_issues", style_code_sample),
    ("performance", performance_code_sample),
    ("security", security_code_sample),
    ("bug", bug_code_sample)
]

for name, code in samples:
    prompt = agent.render_template("code_review", code=code)
    print(f"\n{'='*50}")
    print(f"Sample: {name}")
    print(f"{'='*50}")
    print(prompt)
```

**Deliverable**: Testing script with 5 code samples

---

### Task 2.3: Template Validation

Create `exercise_2_validation.md` documenting:

1. **Did the template work for each sample?**
   - Good code: Correct rating?
   - Style issues: Found PEP 8 problems?
   - Performance: Identified inefficiency?
   - Security: Spotted vulnerability?
   - Bug: Caught logic error?

2. **Template Effectiveness Score**:
   - Clarity (1-5): Were instructions clear?
   - Usefulness (1-5): Did it produce useful feedback?
   - Completeness (1-5): Did it cover all required checks?
   - Accuracy (1-5): Did it identify real issues?
   
   **Overall Score**: (Clarity + Usefulness + Completeness + Accuracy) / 4

3. **What Worked Well?**
   - Which instructions were most effective?
   - Did format specification help structure output?
   - Did examples improve quality?

4. **What Could Improve?**
   - Were any issues missed?
   - Was output always properly formatted?
   - Any ambiguous instructions?

5. **How Would You Enhance It?**
   - Add more specific constraints?
   - Include few-shot examples?
   - Restructure output format?
   - Add weights (critical vs nice-to-have)?

**Deliverable**: Validation report (markdown format, 1-2 pages)

---

### Task 2.4: Compare with Built-in Template

Compare your custom template with the built-in code review template:

```python
from prompt_templates import get_template

builtin_template = get_template("code_review")
```

Create `exercise_2_comparison.md`:

1. **Differences**:
   - What's different in role/task/format?
   - Which is more specific?

2. **Which is better for code review?** Why?

3. **Could you improve the built-in template?** How?

**Deliverable**: Comparison analysis

---

## Success Criteria

- [ ] Custom template created and registered
- [ ] Template tested on 5 diverse code samples
- [ ] Each sample produces structured feedback
- [ ] Validation report completed with scores
- [ ] Comparison with built-in template documented
- [ ] Overall template score ≥ 3.5/5

## Testing Your Solution

Run the validation tests:
```bash
pytest tests/test_context_agent.py::TestTemplateRegistration -v
pytest tests/test_context_agent.py::TestIntegration::test_workflow_qa_with_context -v
```

## Key Learning Points

1. Good custom templates save time and improve consistency
2. Specificity in format and constraints improves output structure
3. Few-shot examples help guide behavior
4. Role definition sets expectations and tone
5. Template design requires iteration and testing

## Extension Ideas

1. Add few-shot examples to your custom template
2. Create templates for other domains (security audit, documentation, refactoring)
3. Test template variations and measure which works best
4. Implement a template version control system

## Next Steps

- Exercise 3: Manage context for large documents
- Build a template library for your domain
