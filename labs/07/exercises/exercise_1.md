# Exercise 1: Run Agent with Default Guardrails

## Objective

Observe guardrail enforcement in action. Understand how constraints are applied to user requests and how violations are logged.

## Time Estimate

20 minutes

## Instructions

### Part 1: Set Up Agent with Production Guardrails (5 min)

Create a Python script `run_exercise_1.py`:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import asyncio
from safety_validator import GuardrailConfig, SafetyValidator
from safe_agent import SafeAgent

async def main():
    # Create production guardrails (strict)
    config = GuardrailConfig(
        max_tokens_per_request=1000,
        max_tokens_per_session=10000,
        cost_limit_usd=1.0,
        allowed_tools=["get_weather", "calculate"],
        block_pii=True,
        block_profanity=True,
        max_output_length=500,
        environment="production"
    )
    
    # Create safe agent
    agent = SafeAgent(guardrail_config=config)
    
    return agent, config

# Run
agent, config = asyncio.run(main())
print(f"Agent created with {config.environment} guardrails")
print(f"Token limit: {config.max_tokens_per_request}/request")
print(f"Allowed tools: {config.allowed_tools}")
```

**Expected Output:**
```
Agent created with production guardrails
Token limit: 1000/request
Allowed tools: ['get_weather', 'calculate']
```

### Part 2: Define Test Queries (5 min)

Define 5 test queries:

| Query # | Type | Query | Expected Result |
|---------|------|-------|-----------------|
| 1 | ✓ Compliant | "What's the weather?" | Pass (short, within limits) |
| 2 | ✓ Compliant | "Calculate 2+2" | Pass (allowed tool) |
| 3 | ✗ Token Limit | "Explain quantum computing in 1000+ words..." (very long) | **Blocked** (exceeds token limit) |
| 4 | ✗ Tool Blocked | "Send an email to user@example.com" | **Blocked** (send_email not allowed) |
| 5 | ✗ PII Output | "My SSN is 123-45-6789" | **Redacted** (PII filtered) |

### Part 3: Run Queries and Log Results (10 min)

Add to script:

```python
async def test_queries(agent):
    test_cases = [
        {
            "id": 1,
            "query": "What's the weather in New York?",
            "expected": "pass",
            "reason": "Short query, within token limit"
        },
        {
            "id": 2,
            "query": "Calculate: 2+2, 5*3, 10/2",
            "expected": "pass",
            "reason": "Uses allowed 'calculate' tool"
        },
        {
            "id": 3,
            "query": "x" * 5000,  # Very long query
            "expected": "block",
            "reason": "Exceeds token limit (5000 chars >> 1000 token limit)"
        },
        {
            "id": 4,
            "query": "Send an urgent email to john@example.com about the meeting",
            "expected": "block",
            "reason": "Attempts 'send_email' which is not in allowlist"
        },
        {
            "id": 5,
            "query": "My social security number is 123-45-6789",
            "expected": "redact",
            "reason": "Output contains SSN (PII) which should be redacted"
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        print(f"\n{'='*60}")
        print(f"Test Case {test_case['id']}: {test_case['reason']}")
        print(f"Query: {test_case['query'][:50]}...")
        print(f"Expected: {test_case['expected']}")
        
        response = await agent.run(test_case['query'])
        
        result = {
            "test_id": test_case['id'],
            "expected": test_case['expected'],
            "success": response.success,
            "content": response.content[:100],
            "violations": len(response.violations),
            "blocked_by": response.metadata.get('blocked_by')
        }
        results.append(result)
        
        print(f"Result: {'✓ PASS' if response.success else '✗ BLOCKED'}")
        if response.violations:
            print(f"Violations: {response.violations[0]['rule']}")
        print(f"Output: {response.content[:100]}...")
    
    return results

# Run tests
results = asyncio.run(test_queries(agent))
```

**Expected Output:**
```
============================================================
Test Case 1: Short query, within token limit
Query: What's the weather in New York?...
Expected: pass
Result: ✓ PASS
Output: Mock response to: What's the weather in New York...

============================================================
Test Case 3: Exceeds token limit
Query: xxxxx...
Expected: block
Result: ✗ BLOCKED
Violations: max_tokens_per_request
Output: Request blocked by guardrail 'max_tokens_per_request'...
```

### Part 4: Generate Violation Report (5 min)

Add to script:

```python
def print_violation_report(results):
    print(f"\n{'='*60}")
    print("VIOLATION REPORT")
    print(f"{'='*60}\n")
    
    passed = sum(1 for r in results if r['success'])
    blocked = sum(1 for r in results if not r['success'])
    
    print(f"Total Tests: {len(results)}")
    print(f"Passed:      {passed}")
    print(f"Blocked:     {blocked}")
    
    print(f"\nViolation Details:")
    for r in results:
        if not r['success']:
            print(f"  Test {r['test_id']}: {r['blocked_by']} — {r['violations']} violation(s)")
    
    print(f"\nConclusion:")
    print(f"  ✓ Guardrails working correctly")
    print(f"  ✓ {blocked} constraint violations prevented")
    print(f"  ✓ {passed} legitimate requests allowed")

print_violation_report(results)
```

**Expected Output:**
```
============================================================
VIOLATION REPORT
============================================================

Total Tests: 5
Passed:      3
Blocked:     2

Violation Details:
  Test 3: max_tokens_per_request — 1 violation(s)
  Test 4: allowed_tools — 1 violation(s)

Conclusion:
  ✓ Guardrails working correctly
  ✓ 2 constraint violations prevented
  ✓ 3 legitimate requests allowed
```

## Deliverable

Submit:

1. **`run_exercise_1.py`** — Complete script with all 4 parts
2. **`exercise_1_results.txt`** — Console output showing:
   - Agent initialization
   - Test case results
   - Violation report

Example structure:

```
EXERCISE 1 - RUN AGENT WITH DEFAULT GUARDRAILS
================================================

Setup:
  - Agent initialized with production guardrails ✓
  - Token limit: 1000/request ✓
  - Allowed tools: ['get_weather', 'calculate'] ✓

Test Results:
  Test 1 (Short query): PASSED ✓
  Test 2 (Calculate): PASSED ✓
  Test 3 (Long query): BLOCKED ✓ (max_tokens_per_request)
  Test 4 (Send email): BLOCKED ✓ (allowed_tools)
  Test 5 (PII output): REDACTED ✓ (block_pii)

Summary:
  Total: 5 tests
  Passed: 3
  Blocked: 2
  Success Rate: 100%
```

## Success Criteria

- [ ] Script runs without errors
- [ ] 5 test queries execute
- [ ] 3 queries pass, 2 are blocked
- [ ] Violations are logged correctly
- [ ] Report generated and submitted

## Hints

1. **Token Counting:** Approx 4 chars = 1 token. Long query needs ~5000+ chars to exceed 1000 token limit.

2. **Tool Validation:** Agent should attempt to validate tool before calling (or mock agent should do this).

3. **Violation Logging:** Each GuardrailViolation is automatically logged in `agent.validator.violations`.

4. **PII Redaction:** Validator automatically redacts SSN pattern in output.

## Questions to Answer

1. **Which guardrail rule prevented Test #3 from running?**
2. **Why was Test #4 blocked instead of the agent attempting to send email?**
3. **What would change if we used the development config instead of production?**
4. **How would you modify guardrails to allow the 'send_email' tool in production?**

---

**Next Exercise:** [Exercise 2: Create Custom Guardrail Configuration](exercise_2.md)
