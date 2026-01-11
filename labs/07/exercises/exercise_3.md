# Exercise 3: Stress Test with Limited Resources

## Objective

Validate agent behavior under extreme constraint. Understand how agents degrade gracefully (or fail) when resources are scarce.

## Time Estimate

60 minutes

## Context

In production, you may need to operate agents under strict constraints:
- Tight budgets during off-peak hours
- SLAs requiring fast responses
- Regulatory limits on API calls

This exercise asks: **How does an agent perform when you severely limit its resources?**

## Instructions

### Part 1: Design Stress Test (15 min)

Create two agent configurations:

**Normal Config (Baseline):**
```python
normal_config = GuardrailConfig(
    max_tokens_per_request=2000,
    max_tokens_per_session=20000,
    allowed_tools=["search", "calculate", "summarize", "translate"],
    block_pii=True,
    max_output_length=1000,
    environment="production"
)
```

**Stressed Config (Extreme):**
```python
stressed_config = GuardrailConfig(
    max_tokens_per_request=200,      # 90% reduction
    max_tokens_per_session=1000,     # 95% reduction
    allowed_tools=["search", "calculate"],  # 50% reduction
    block_pii=True,
    max_output_length=200,           # 80% reduction
    environment="production"
)
```

**Comparison:**

| Constraint | Normal | Stressed | Reduction |
|-----------|--------|----------|-----------|
| Per-request tokens | 2000 | 200 | 90% ↓ |
| Per-session tokens | 20000 | 1000 | 95% ↓ |
| Allowed tools | 4 | 2 | 50% ↓ |
| Output length | 1000 | 200 | 80% ↓ |

### Part 2: Define Representative Tasks (10 min)

Create a test suite with 10 representative tasks:

```python
tasks = [
    {
        "id": 1,
        "name": "Simple math",
        "query": "What is 15 * 7?",
        "expected_tools": ["calculate"],
        "complexity": "low"
    },
    {
        "id": 2,
        "name": "Knowledge search",
        "query": "How do I reset my password?",
        "expected_tools": ["search"],
        "complexity": "low"
    },
    {
        "id": 3,
        "name": "Multi-step task",
        "query": "Find the average of [2, 4, 6, 8, 10] and tell me if it's even or odd",
        "expected_tools": ["search", "calculate"],
        "complexity": "medium"
    },
    {
        "id": 4,
        "name": "Complex analysis",
        "query": "Analyze the main reasons why customers churn, based on our support tickets, and propose 3 solutions",
        "expected_tools": ["search", "summarize"],
        "complexity": "high"
    },
    {
        "id": 5,
        "name": "Translation",
        "query": "Translate 'Please help me with my account' to Spanish, French, and German",
        "expected_tools": ["translate"],
        "complexity": "medium"
    },
    {
        "id": 6,
        "name": "PII handling",
        "query": "My SSN is 123-45-6789, can you verify it's correct?",
        "expected_tools": ["search"],
        "complexity": "low"
    },
    {
        "id": 7,
        "name": "Blocked tool request",
        "query": "Summarize all customer complaints from the last month",
        "expected_tools": ["search", "summarize"],
        "complexity": "high"
    },
    {
        "id": 8,
        "name": "Chained reasoning",
        "query": "Step 1: Search for our refund policy. Step 2: Calculate if customer qualifies based on purchase date. Step 3: Determine refund amount.",
        "expected_tools": ["search", "calculate"],
        "complexity": "high"
    },
    {
        "id": 9,
        "name": "Simple lookup",
        "query": "Is pi approximately 3.14?",
        "expected_tools": ["calculate"],
        "complexity": "low"
    },
    {
        "id": 10,
        "name": "Multi-language request",
        "query": "Explain AI in 2 sentences, then translate to Japanese",
        "expected_tools": ["translate"],
        "complexity": "high"
    }
]
```

### Part 3: Run Stress Test (25 min)

Create `stress_test.py`:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import asyncio
from safety_validator import GuardrailConfig, SafetyValidator, GuardrailViolation
from safe_agent import SafeAgent

async def run_stress_test():
    # Define configurations
    normal_config = GuardrailConfig(
        max_tokens_per_request=2000,
        max_tokens_per_session=20000,
        allowed_tools=["search", "calculate", "summarize", "translate"],
        block_pii=True,
        max_output_length=1000,
        environment="production"
    )
    
    stressed_config = GuardrailConfig(
        max_tokens_per_request=200,
        max_tokens_per_session=1000,
        allowed_tools=["search", "calculate"],
        block_pii=True,
        max_output_length=200,
        environment="production"
    )
    
    # Define tasks
    tasks = [
        {"id": 1, "query": "What is 15 * 7?", "tools": ["calculate"], "complexity": "low"},
        {"id": 2, "query": "How do I reset my password?", "tools": ["search"], "complexity": "low"},
        {"id": 3, "query": "Find the average of [2,4,6,8,10] and tell me if even", "tools": ["search", "calculate"], "complexity": "medium"},
        {"id": 4, "query": "Analyze customer churn reasons and propose 3 solutions", "tools": ["search", "summarize"], "complexity": "high"},
        {"id": 5, "query": "Translate 'Help me' to Spanish, French, German", "tools": ["translate"], "complexity": "medium"},
        {"id": 6, "query": "My SSN is 123-45-6789, verify it", "tools": ["search"], "complexity": "low"},
        {"id": 7, "query": "Summarize all complaints from last month", "tools": ["search", "summarize"], "complexity": "high"},
        {"id": 8, "query": "Check refund policy, calculate eligibility, determine amount", "tools": ["search", "calculate"], "complexity": "high"},
        {"id": 9, "query": "Is pi approximately 3.14?", "tools": ["calculate"], "complexity": "low"},
        {"id": 10, "query": "Explain AI in 2 sentences, translate to Japanese", "tools": ["translate"], "complexity": "high"},
    ]
    
    # Run tests
    print("STRESS TEST: NORMAL CONFIG vs STRESSED CONFIG")
    print("=" * 80)
    
    normal_results = await test_config(normal_config, tasks, "NORMAL")
    print()
    stressed_results = await test_config(stressed_config, tasks, "STRESSED")
    
    # Compare
    print_comparison(normal_results, stressed_results, tasks)
    
    return normal_results, stressed_results

async def test_config(config, tasks, label):
    print(f"\n{label} CONFIG TEST")
    print(f"  Tokens/request: {config.max_tokens_per_request}")
    print(f"  Tokens/session: {config.max_tokens_per_session}")
    print(f"  Allowed tools: {len(config.allowed_tools) if config.allowed_tools else 'all'}")
    print("-" * 80)
    
    agent = SafeAgent(guardrail_config=config)
    results = []
    
    for task in tasks:
        success = True
        blocked_by = None
        
        # Check tool constraints
        for tool in task['tools']:
            try:
                agent.validate_tool_call(tool)
            except GuardrailViolation as e:
                success = False
                blocked_by = e.rule
                break
        
        # Check request constraints
        if success:
            try:
                agent.validator.validate_request(task['query'])
            except GuardrailViolation as e:
                success = False
                blocked_by = e.rule
        
        results.append({
            "id": task['id'],
            "complexity": task['complexity'],
            "success": success,
            "blocked_by": blocked_by
        })
        
        status = "✓ PASS" if success else f"✗ BLOCKED ({blocked_by})"
        print(f"Task {task['id']:2d} ({task['complexity']:6s}): {status}")
    
    # Calculate metrics
    pass_rate = sum(1 for r in results if r['success']) / len(results) * 100
    by_complexity = {}
    for r in results:
        c = r['complexity']
        if c not in by_complexity:
            by_complexity[c] = {"pass": 0, "fail": 0}
        if r['success']:
            by_complexity[c]["pass"] += 1
        else:
            by_complexity[c]["fail"] += 1
    
    print(f"\nMetrics:")
    print(f"  Pass rate: {pass_rate:.1f}%")
    for complexity, counts in sorted(by_complexity.items()):
        total = counts["pass"] + counts["fail"]
        rate = counts["pass"] / total * 100
        print(f"  {complexity}: {counts['pass']}/{total} ({rate:.0f}%)")
    
    return results

def print_comparison(normal, stressed, tasks):
    print("\n" + "=" * 80)
    print("COMPARISON: NORMAL vs STRESSED")
    print("=" * 80)
    
    normal_pass = sum(1 for r in normal if r['success'])
    stressed_pass = sum(1 for r in stressed if r['success'])
    
    degradation = normal_pass - stressed_pass
    degradation_pct = (degradation / normal_pass * 100) if normal_pass > 0 else 0
    
    print(f"\nOverall Success Rate:")
    print(f"  Normal:    {normal_pass:2d}/10 (100%)")
    print(f"  Stressed:  {stressed_pass:2d}/10 ({stressed_pass*10:.0f}%)")
    print(f"  Degradation: {degradation} tasks failed ({degradation_pct:.1f}% drop)")
    
    print(f"\nTasks Affected by Stress:")
    for i, (n, s) in enumerate(zip(normal, stressed)):
        if n['success'] and not s['success']:
            print(f"  Task {n['id']}: Now blocked by {s['blocked_by']}")
    
    print(f"\nConclusion:")
    if degradation <= 2:
        print(f"  ✓ Agent degrades gracefully (only {degradation} tasks affected)")
    else:
        print(f"  ✗ Agent degrades poorly ({degradation} tasks affected)")
    
    if stressed_pass >= 5:
        print(f"  ✓ At least 50% of tasks still passable")
    else:
        print(f"  ✗ Severe resource constraint impacts >50% of tasks")

# Run
asyncio.run(run_stress_test())
```

**Expected Output:**
```
STRESS TEST: NORMAL CONFIG vs STRESSED CONFIG
================================================================================

NORMAL CONFIG TEST
  Tokens/request: 2000
  Tokens/session: 20000
  Allowed tools: 4
--------------------------------------------------------------------------------
Task  1 (low   ): ✓ PASS
Task  2 (low   ): ✓ PASS
Task  3 (medium): ✓ PASS
Task  4 (high  ): ✓ PASS
Task  5 (medium): ✗ BLOCKED (allowed_tools)
Task  6 (low   ): ✓ PASS
Task  7 (high  ): ✗ BLOCKED (allowed_tools)
Task  8 (high  ): ✓ PASS
Task  9 (low   ): ✓ PASS
Task 10 (high  ): ✗ BLOCKED (allowed_tools)

Metrics:
  Pass rate: 70.0%
  high:   1/3 (33%)
  low:    4/4 (100%)
  medium: 2/3 (67%)

STRESSED CONFIG TEST
  Tokens/request: 200
  Tokens/session: 1000
  Allowed tools: 2
--------------------------------------------------------------------------------
Task  1 (low   ): ✓ PASS
Task  2 (low   ): ✓ PASS
Task  3 (medium): ✓ PASS
Task  4 (high  ): ✗ BLOCKED (allowed_tools)
Task  5 (medium): ✗ BLOCKED (allowed_tools)
Task  6 (low   ): ✓ PASS
Task  7 (high  ): ✗ BLOCKED (allowed_tools)
Task  8 (high  ): ✓ PASS
Task  9 (low   ): ✓ PASS
Task 10 (high  ): ✗ BLOCKED (allowed_tools)

Metrics:
  Pass rate: 60.0%
  high:   1/3 (33%)
  low:    4/4 (100%)
  medium: 1/3 (33%)

================================================================================
COMPARISON: NORMAL vs STRESSED
================================================================================

Overall Success Rate:
  Normal:    7/10 (100%)
  Stressed:  6/10 (60%)
  Degradation: 1 task failed (10% drop)

Tasks Affected by Stress:
  Task 5: Now blocked by allowed_tools

Conclusion:
  ✓ Agent degrades gracefully (only 1 task affected)
  ✓ At least 50% of tasks still passable
```

### Part 4: Analysis and Insights (10 min)

Create `STRESS_TEST_ANALYSIS.md`:

```markdown
# Stress Test Analysis: Agent Performance Under Constraint

## Executive Summary

- Normal config: 7/10 tasks pass (70%)
- Stressed config: 6/10 tasks pass (60%)
- Degradation: 1 task, 10% drop
- Conclusion: Agent handles stress reasonably well

## Findings

### What Worked Well
1. **Low-complexity tasks maintained 100% success** — Simple lookups, basic math
2. **Core tools retained** — search and calculate not removed
3. **Graceful failure** — Agent blocked rather than crashed

### What Failed
1. **Tool-dependent tasks** — translate/summarize not available
2. **High-complexity workflows** — Multi-step analysis
3. **Token accumulation** — Long conversations hit session limits

### Key Insights

#### Insight 1: Complexity Matters
- Low complexity: 100% success rate (even under stress)
- Medium complexity: 67% → 33% (50% degradation)
- High complexity: 33% → 33% (no change, already limited)

**Implication:** Stress primarily affects medium-complexity tasks that benefit from full tooling.

#### Insight 2: Tool Set is Critical
- Removing 2 tools (summarize, translate) affects 3 tasks
- Agent can't work around missing tools
- Core tools (search, calculate) support ~60% of workload

**Implication:** Carefully choose which tools to disable under stress; don't arbitrary reduce.

#### Insight 3: Token Limits are Soft
- 200 token/request still allows most tasks
- 1000 token/session limits conversation length, not individual queries
- Even stressed, all queries in test passed token validation

**Implication:** Token limits primarily enforce usage boundaries, not capability loss.

### Recommendations

1. **For Production:** Use normal config; stress is rare
2. **For Peak Load:** Disable `summarize` and `translate` (low-value)
3. **For Budget Crunch:** Keep token limits as-is; remove risky tools instead
4. **For SLA:** Increase `max_response_time_sec` before reducing tokens

## Tables

### Performance by Complexity

| Complexity | Normal | Stressed | Impact |
|-----------|--------|----------|--------|
| Low | 4/4 (100%) | 4/4 (100%) | None |
| Medium | 2/3 (67%) | 1/3 (33%) | -2 tasks |
| High | 1/3 (33%) | 1/3 (33%) | None |

### Tool Usage Impact

| Tool | Tasks Enabled | Loss on Removal |
|------|---------------|-----------------|
| search | 6 | High |
| calculate | 4 | Medium |
| summarize | 2 | Low |
| translate | 2 | Low |

### Constraint Impact Ranking

1. **Allowed tools: HIGH** — Directly blocks task types
2. **Token/request: LOW** — 200 still sufficient for most queries
3. **Output length: NONE** — Not hit in test scenarios
4. **Token/session: MEDIUM** — Limits conversation depth

## Conclusion

The agent **degrades gracefully** under resource stress. Core functionality (search, calculate) 
remains available, while higher-value features (summarize, translate) are sacrificed. This is 
the correct design: prioritize essential capabilities over convenience features when resources 
are constrained.
```

## Deliverable

Submit:

1. **`stress_test.py`** — Complete stress test implementation
2. **`STRESS_TEST_ANALYSIS.md`** — Detailed findings and insights
3. **`stress_test_results.txt`** — Complete console output

Expected files:
```
exercises/
├── stress_test.py
├── STRESS_TEST_ANALYSIS.md
└── stress_test_results.txt
```

## Success Criteria

- [ ] Stress test runs without errors
- [ ] Both configs (normal and stressed) tested
- [ ] All 10 tasks evaluated
- [ ] Performance metrics calculated
- [ ] Analysis document completed
- [ ] Clear insights and recommendations provided

## Key Metrics to Calculate

1. **Pass Rate:** (tasks passed) / (total tasks) × 100%
2. **Degradation:** normal_pass_rate - stressed_pass_rate
3. **By Complexity:** Success rate for low/medium/high tasks
4. **Bottleneck:** Which constraint is most limiting?

## Discussion Questions

1. **How does removing tools affect task completion more than token limits?**
2. **Why do low-complexity tasks remain unaffected by stress?**
3. **In what production scenario would you apply stressed config?**
4. **How would you design guardrails to handle 2x more traffic?**
5. **What's the minimum viable tool set for your domain?**

## Extension Challenges

1. **Scaling Test:** Apply even more severe stress (100 token/req, 1 tool)
2. **User Experience:** Design error messages for each constraint violation
3. **Adaptive Config:** Automatically loosen constraints when under stress
4. **Cost Analysis:** Calculate cost per task under both configs
5. **Comparative Study:** Same stress test on different domain agents

---

**Congratulations!** You've completed all three exercises.

## Summary

| Exercise | Focus | Deliverables |
|----------|-------|--------------|
| 1 | Observe guardrails in action | Script + violation report |
| 2 | Design custom guardrails | Config + tests + design doc |
| 3 | Stress testing & degradation | Stress test + analysis |

**Lab 7 Complete:** You now understand how to enforce safety constraints, design production-ready guardrails, and validate behavior under stress.

---

**Next Steps:**
- Review [Lab 8: Evaluation & Testing](#) for regression testing
- Study [Production Operations](#) for monitoring guardrails in prod
- Explore [Security & Threat Models](#) for advanced safety patterns
