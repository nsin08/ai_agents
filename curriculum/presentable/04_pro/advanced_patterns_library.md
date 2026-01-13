# Advanced Patterns Library (Pro Level)

This library is a compact reference of proven patterns for building pro-grade agent systems.

Each pattern includes:
- Problem: what breaks without this
- Solution: the core idea
- Implementation sketch: how to build it (with code snippets)
- Evidence: what to test or measure

## Orchestration patterns

### Pattern: Explicit state machine (graph or loop)

Problem:
- "Prompt-only" agents are hard to test, hard to audit, and easy to regress.

Solution:
- Model the agent as explicit states and transitions (observe -> plan -> act -> verify -> refine).

Implementation sketch (framework-agnostic):

```python
from enum import Enum

class State(Enum):
    OBSERVE = "observe"
    PLAN = "plan"
    ACT = "act"
    VERIFY = "verify"
    DONE = "done"
    FAILED = "failed"
```

Evidence:
- Unit tests for allowed transitions.
- Trace logs contain state transitions for every run.

### Pattern: Interrupts and approvals

Problem:
- High-risk actions require human control, but adding humans can break flow.

Solution:
- Add explicit interrupt states for approvals and missing inputs.

Evidence:
- Tests that risky actions cannot execute without an approval token.
- Audit logs show "who approved what".

## Reasoning patterns

### Pattern: Candidate generation + scoring (ToT-like)

Problem:
- Single-pass reasoning is brittle and non-deterministic.

Solution:
- Generate multiple candidates; score them with constraints; execute the best.

Implementation sketch:

```python
def pick_best(candidates, score_fn):
    scored = [(score_fn(c), c) for c in candidates]
    scored.sort(reverse=True, key=lambda t: t[0])
    return scored[0][1]
```

Evidence:
- Success rate improves on high-risk tasks.
- Cost per success stays acceptable.

### Pattern: Separate reasoning from user-visible answers

Problem:
- Exposing raw reasoning can leak sensitive info and reduce trust.

Solution:
- Keep internal plans separate from final outputs; log plans for debugging only.

Evidence:
- Final outputs have citations or checks, not raw chain-of-thought.

## Tooling patterns

### Pattern: Tool contracts (schemas + validation)

Problem:
- Tool calls fail due to invalid args, missing tools, or unsafe parameters.

Solution:
- Define a tool contract: name, description, input schema, output schema.
- Validate input before execution; validate output when possible.

Evidence:
- Contract tests for every tool.
- Metrics: invalid-arg rate, not-found rate, retry success rate.

### Pattern: Teach with error messages

Problem:
- The model repeats the same invalid calls.

Solution:
- Return actionable errors that guide correct usage (expected fields, examples).

Evidence:
- Decreasing invalid-arg rate over time for the same prompt set.

## Memory and RAG patterns

### Pattern: Retrieval gating (no-retrieve vs light vs deep)

Problem:
- Always retrieving increases cost and increases injection surface area.

Solution:
- Route retrieval based on intent and uncertainty; budget retrieval depth.

Evidence:
- Citation precision improves; cost per grounded answer decreases.

### Pattern: Provenance-first memory

Problem:
- Storing untrusted content as "facts" contaminates future runs.

Solution:
- Store where each memory item came from; tag trust level; keep tenant isolation.

Evidence:
- For any claim: you can trace it to a source (doc id, tool output, timestamp).

## Evaluation patterns

### Pattern: Executable correctness checks first

Problem:
- LLM-as-judge can drift and can be gamed.

Solution:
- Prefer deterministic checks (tests, validators) before any subjective scoring.

Evidence:
- Benchmark suite contains a deterministic core.

### Pattern: Regression gates in CI/CD

Problem:
- Prompt/model changes regress behavior silently.

Solution:
- Run a small, high-signal benchmark suite on every PR and gate merges.

Evidence:
- A failing benchmark blocks the PR.

## Multi-agent patterns

### Pattern: Manager-worker-verifier

Problem:
- Multi-agent systems can amplify hallucinations and coordination failures.

Solution:
- Manager delegates; workers propose; verifier checks against constraints.

Evidence:
- Trace logs show each role output and verifier decisions.

